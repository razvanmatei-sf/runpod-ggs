#!/bin/bash

# Sync workflows from private repo (optional - don't fail if not available)
if [ -d "/workspace/ComfyUI/user/default/workflows/.git" ]; then
    cd /workspace/ComfyUI/user/default/workflows
    git pull 2>/dev/null || echo "Warning: Could not sync workflows (no network or auth)"
fi

apt update
apt install -y psmisc
fuser -k 8188/tcp 2>/dev/null || true

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
