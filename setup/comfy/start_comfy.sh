#!/bin/bash

apt update
apt install psmisc
fuser -k 3000/tcp

# Add CUDA library paths for cusparseLt and other nvidia libs
export LD_LIBRARY_PATH=/usr/local/lib/python3.12/dist-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/dist-packages/nvidia/nvjitlink/lib:${LD_LIBRARY_PATH}

cd /workspace/ComfyUI/venv
source bin/activate
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --use-sage-attention
