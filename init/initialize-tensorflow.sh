#!/bin/bash
docker run -it \
    --network=host \
    --device=/dev/kfd \
    --device=/dev/dri \
    --ipc=host \
    --shm-size 32G \
    --group-add video \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    -v "$(pwd)":/app \
    rocm/tensorflow:latest \
    bash -c "
        ./init/initialize-torch.sh &&
        pip install transformers accelerate &&
        export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 &&
        python main.py $*
    "