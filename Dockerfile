# Base image
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Use bash shell with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
USER root
RUN apt update
RUN apt install -y git wget build-essential libgl-dev libglib2.0-0
RUN apt install -y python3.10 python3.10-venv python3-pip

# Cleanup section (Worker Template)
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python

WORKDIR /app
# Stable Diffusioni Webui
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git && \
    cd stable-diffusion-webui && \
    git checkout tags/v1.3.2 -b v132

# Controlnet
WORKDIR /app/stable-diffusion-webui/extensions
RUN git clone https://github.com/Mikubill/sd-webui-controlnet.git && \
    cd sd-webui-controlnet && \
    git checkout 99408b9f4e514efdf33b19f3215ab661b989e209

WORKDIR /app/stable-diffusion-webui
RUN pip install requests runpod --no-cache-dir
RUN pip install pytorch_lightning --no-cache-dir
ENV TORCH_COMMAND="pip install torch==2.0.1 torchvision==0.15.2"
ENV K_DIFFUSION_REPO="https://github.com/brkirch/k-diffusion.git"
ENV K_DIFFUSION_COMMIT_HASH="51c9778f269cedb55a4d88c79c0246d35bdadb71"
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

RUN pip install -r requirements_versions.txt --prefer-binary --no-cache-dir
ADD ./requirements_costom.txt .
RUN pip install -r requirements_costom.txt --no-cache-dir
ADD ./start.sh .
# ADD MODELS
ADD ./models/Stable-diffusion models/Stable-diffusion
ADD ./models/Lora models/Lora
ADD ./extensions/sd-webui-controlnet/models extensions/sd-webui-controlnet/models

ADD ./src/webui.py ./webui.py
ADD ./src/rpc_handler.py ./rpc_handler.py
ADD ./src/r2_loader.py ./r2_loader.py

RUN chmod +x /app/stable-diffusion-webui/start.sh
ENTRYPOINT ["/app/stable-diffusion-webui/start.sh"]
