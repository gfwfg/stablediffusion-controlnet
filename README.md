
# Simple using stable diffusion webui api to runpod


## 主要逻辑
- stable diffustion webui
- runpod handler 

通过runpod_handler把数据提交进来后，转发到stable diffusion webui api中执行操作; api的文档地址： https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
包装后的参数格式为:
```json

{
  "params": {}, // webui api params; webhook, base_model name.
  "endpoint": "/sdapi/v1/img2img" // url endpoint
}

```

## 打包服务
1. 查看dockerfile
2. `docker build docker build . --platform=linux/amd64 -t <dockerhub-name>:<image-name:<version>`
3. `docker push <image>`
4. runpod 创建或者修改对应的template并重新设置instance数量为0，在修改为1，强制拉最新的image
