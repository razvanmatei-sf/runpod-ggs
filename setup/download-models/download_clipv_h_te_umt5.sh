#!/bin/bash
# ABOUTME: Downloads CLIP Vision H and UMT5 text encoder models
# ABOUTME: Required for Wan 2.1 workflows

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading CLIP Vision H & UMT5 models..."

download "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors" \
    "/workspace/ComfyUI/models/clip_vision/clip_vision_h.safetensors"

download "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

echo "Download finished"
