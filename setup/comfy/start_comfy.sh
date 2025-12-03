#!/bin/bash

# Sync workflows from private repo
cd /workspace/ComfyUI/user/default/workflows
git pull

apt update
apt install psmisc
fuser -k 8188/tcp

cd /workspace/ComfyUI/venv
source bin/activate
cd /workspace/ComfyUI

# Build command args
ARGS="--listen 0.0.0.0 --use-sage-attention"
if [ -n "$COMFY_OUTPUT_DIR" ]; then
    mkdir -p "$COMFY_OUTPUT_DIR"
    ARGS="$ARGS --output-directory \"$COMFY_OUTPUT_DIR\""
fi

eval python main.py $ARGS
