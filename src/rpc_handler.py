# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin
import runpod
import requests
from requests.adapters import HTTPAdapter, Retry
from r2_loader import R2Loader
import os
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor as Pool
from logging import getLogger
from copy import deepcopy

logger = getLogger("RPC_HANDLE")
automatic_session = requests.Session()
retries = Retry(total=10, backoff_factor=0.3, status_forcelist=[502, 503, 504, 500])
automatic_session.mount('http://', HTTPAdapter(max_retries=retries))
current_model = None
pool = Pool(max_workers=5)

r2 = R2Loader(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_access_secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    bucket_name=os.environ.get("BUCKET_NAME"),
    endpoint_url=os.environ.get("ENDPOINT"),
    domain=os.environ.get("DOMAIN")
)


def process_parameters(prams: dict):
    init_images = prams.get("init_images")
    images = [
        r2.download(img)
        for img in init_images
        if img.startswith("http")
    ]
    prams['init_images'] = images
    controlnet = prams.get("alwayson_scripts", {}).get("controlnet")
    if controlnet:
        for arg in controlnet.get("args", []):
            input_image = arg.get("input_image", "")
            if input_image.startswith("http"):
                img_base = r2.download(image_url=input_image)
                arg['input_image'] = img_base
    return prams


def process_response(resp_data: dict):
    return [
        r2.upload(img, f"{uuid4()}.jpg")
        for img in resp_data['images']
    ]


def switch_base_model(prams: dict):
    global current_model
    base_model = None
    if "base_model" in prams:
        base_model = prams.pop("base_model")
    if not base_model:
        return
    if base_model != current_model:
        try:
            option_payload = {
                "sd_model_checkpoint": base_model,
                "CLIP_stop_at_last_layers": 2
            }
            resp = automatic_session.post('http://127.0.0.1:3000/sdapi/v1/options', json=option_payload)
            print(f"SWITCH MODEL: {resp.text}")
            current_model = base_model
        except:
            return


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #
def wait_for_service(url):
    '''
    Check if the service is ready to receive requests.
    '''
    while True:
        try:
            requests.post(url)
            return
        except requests.exceptions.RequestException:
            print("Service not ready yet. Retrying...")
        except Exception as err:
            print("Error: ", err)
        time.sleep(1)


def run_inference(inference_request, job_id):
    '''
    Run inference on a request.
    '''
    endpoint = inference_request.get("endpoint", "/sdapi/v1/img2img")
    params = inference_request.get("params")
    web_hook_url = params.pop("webhook")
    logger.info(f"[PARAMS]: {params}")
    params = process_parameters(params)
    switch_base_model(params)
    response = automatic_session.post(
        url=urljoin('http://127.0.0.1:3000', endpoint),
        json=params,
        timeout=600)
    images = process_response(response.json())
    output = {"images": images, "job_id": job_id}
    if web_hook_url:
        pool.submit(r2.send_post, web_hook_url, output)
    return output


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event["input"], job_id=event['id'])

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    wait_for_service(url='http://127.0.0.1:3000/sdapi/v1/img2img')

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
