#!/bin/bash

apt update
apt install psmisc
fuser -k 3000/tcp

cd /workspace/ComfyUI/venv
source bin/activate
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --use-sage-attention
