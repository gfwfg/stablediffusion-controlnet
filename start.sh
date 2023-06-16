#!/bin/bash

echo "Worker Initiated"
echo "Starting RunPod Handler"
python -u rpc_handler.py &
echo "Starting WebUI API"
python launch.py --ckpt meinamix_meinaV10 --xformers --disable-safe-unpickle --lowram --port 3000 --api --nowebui --no-hashing --no-download-sd-model
#python launch.py --ckpt meinamix_meinaV10  --skip-torch-cuda-test --upcast-sampling --no-half-vae --use-cpu interrogate --disable-safe-unpickle --port 3000 --api --nowebui --skip-version-check  --no-hashing --no-download-sd-model &

