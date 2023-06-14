#!/usr/bin/env python
''' Contains the handler function that will be called by the serverless. '''
from modules.call_queue import wrap_gradio_gpu_call, wrap_queued_call, queue_lock  # noqa: F401
import runpod
from fastapi import FastAPI
from modules.api.api import Api
from modules.api.models import StableDiffusionImg2ImgProcessingAPI
import modules
from webui import initialize, setup_middleware
from launch import *
app = FastAPI()
initialize()
modules.script_callbacks.on_list_optimizers(modules.sd_hijack_optimizations.list_optimizers)
modules.sd_hijack.list_optimizers()
modules.script_callbacks.on_list_optimizers(modules.sd_hijack_optimizations.list_optimizers)
modules.sd_hijack.list_optimizers()
api = Api(app, queue_lock)


def handler(request):
    '''
    This is the handler function that will be called by the serverless.
    '''
    kwargs = request['input']
    if not kwargs:
        return None
    img_req = StableDiffusionImg2ImgProcessingAPI(
       **kwargs
    )
    resp = api.img2imgapi(img_req)

    # do the things

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return resp.images[0]


runpod.serverless.start({"handler": handler})
