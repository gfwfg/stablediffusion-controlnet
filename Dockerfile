# Base image
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04
ARG MODEL_URL="https://firebasestorage.googleapis.com/v0/b/new-test-project-b425d.appspot.com/o/asserts%2Fmeinamix_meinaV10.safetensors?alt=media"
ARG CONTROL_URL="https://firebasestorage.googleapis.com/v0/b/new-test-project-b425d.appspot.com/o/asserts%2Fcontrol_v11p_sd15_lineart.pth?alt=media"

ENV MODEL_URL=${MODEL_URL}
ENV CONTROL_URL=${CONTROL_URL}
ENV HF_TOKEN=${HF_TOKEN}
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
RUN useradd -ms /bin/bash banana
USER banana
ENV install_dir="$HOME"
ENV python_cmd="python3.10"
ENV K_DIFFUSION_REPO="https://github.com/brkirch/k-diffusion.git"
ENV K_DIFFUSION_COMMIT_HASH="51c9778f269cedb55a4d88c79c0246d35bdadb71"
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

WORKDIR /app
# Stable Diffusioni Webui
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git && \
    cd stable-diffusion-webui && \
    git checkout baf6946e06249c5af9851c60171692c44ef633e0 &&\
    cd models/Stable-diffusion/ && \
    wget -O meinamix_meinaV10.safetensors --no-verbose --show-progress --progress=bar:force:noscroll ${MODEL_URL}

# Controlnet
WORKDIR /app/stable-diffusion-webui/extensions
RUN git clone https://github.com/Mikubill/sd-webui-controlnet.git && \
    cd sd-webui-controlnet && \
    git checkout 99408b9f4e514efdf33b19f3215ab661b989e209 &&\
    cd models && \
    wget -O control_v11p_sd15_lineart.pth --no-verbose --show-progress --progress=bar:force:noscroll ${CONTROL_URL}

WORKDIR /app/stable-diffusion-webui
RUN pip install tqdm requests runpod --no-cache-dir
ADD prepare.py .
RUN python prepare.py --skip-torch-cuda-test --xformers

ADD . .
RUN chmod +x /start.sh
CMD /start.sh