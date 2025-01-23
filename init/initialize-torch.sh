#!/bin/bash
docker run -it \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --ipc=host \
  --shm-size 32G \
  -v "$(pwd)":/app \
  rocm/pytorch:rocm6.1.3_ubuntu22.04_py3.10_pytorch_release-2.1.2 \
  bash -c "
    cd /app &&
    source ./venv312/bin/activate &&
    pip install transformers accelerate &&
    export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 &&
    python main.py $*
  "
  