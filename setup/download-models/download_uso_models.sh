#!/bin/bash
# ABOUTME: Downloads USO (Unified Style Output) models for Flux
# ABOUTME: Includes checkpoint, LoRA, projector, and CLIP vision

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading USO models..."

download "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
    "/workspace/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors"

download "https://huggingface.co/Comfy-Org/USO_1.0_Repackaged/resolve/main/split_files/loras/uso-flux1-dit-lora-v1.safetensors" \
    "/workspace/ComfyUI/models/loras/uso-flux1-dit-lora-v1.safetensors"

download "https://huggingface.co/Comfy-Org/USO_1.0_Repackaged/resolve/main/split_files/model_patches/uso-flux1-projector-v1.safetensors" \
    "/workspace/ComfyUI/models/model_patches/uso-flux1-projector-v1.safetensors"

download "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors" \
    "/workspace/ComfyUI/models/clip_vision/sigclip_vision_patch14_384.safetensors"

echo "Download finished"
