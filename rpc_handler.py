# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin
import runpod
import requests
from requests.adapters import HTTPAdapter, Retry
from r2_loader import R2Loader
import os
from uuid import uuid4
# os.environ.get("AWS_ACCESS_KEY_ID")
# os.environ.get("AWS_SECRET_ACCESS_KEY")

automatic_session = requests.Session()
retries = Retry(total=10, backoff_factor=0.3, status_forcelist=[502, 503, 504, 500])
automatic_session.mount('http://', HTTPAdapter(max_retries=retries))

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
        r2.download(image_url=img)
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
        for img in resp_data['images']]


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


def run_inference(inference_request):
    '''
    Run inference on a request.
    '''
    endpoint = inference_request.get("endpoint", "/sdapi/v1/img2img")
    params = inference_request.get("params")
    params = process_parameters(params)
    response = automatic_session.post(
        url=urljoin('http://127.0.0.1:3000', endpoint),
        json=params,
        timeout=600)
    images = process_response(response.json())
    return {"images": images}


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event["input"])

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    wait_for_service(url='http://127.0.0.1:3000/sdapi/v1/img2img')

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
