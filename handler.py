#!/usr/bin/env python
''' Contains the handler function that will be called by the serverless. '''
from modules.call_queue import wrap_gradio_gpu_call, wrap_queued_call, queue_lock  # noqa: F401
import runpod
from fastapi import FastAPI
from modules.api.api import Api
from modules.api.models import StableDiffusionImg2ImgProcessingAPI

app = FastAPI()
api = Api(app, queue_lock)


def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''
    kwargs = event
    img_req = StableDiffusionImg2ImgProcessingAPI(
       **kwargs
    )
    resp = api.img2imgapi(img_req)

    # do the things

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return resp.images[0]


runpod.serverless.start({"handler": handler})
