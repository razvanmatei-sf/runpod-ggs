#!/bin/bash

# Sync workflows from private repo
WORKFLOWS_DIR="/workspace/ComfyUI/user/default/workflows"
mkdir -p "$WORKFLOWS_DIR"
if [ -d "$WORKFLOWS_DIR/.git" ]; then
    cd "$WORKFLOWS_DIR"
    git pull
else
    git clone git@github.com:razvanmatei-sf/comfyui-workflows.git "$WORKFLOWS_DIR"
fi

apt update
apt install psmisc
fuser -k 3000/tcp

cd /workspace/ComfyUI/venv
source bin/activate
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --use-sage-attention
