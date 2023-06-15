#!/bin/bash

echo "Worker Initiated"

echo "Starting WebUI API"
python webui.py --skip-python-version-check --skip-torch-cuda-test --no-tests --skip-install --ckpt meinamix_meinaV10 --lowram --opt-sdp-attention --disable-safe-unpickle --port 3000 --api --nowebui --skip-version-check  --no-hashing --no-download-sd-model &

echo "Starting RunPod Handler"
python -u rpc_handler.py