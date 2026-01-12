#!/bin/bash
# ABOUTME: Downloads Z Image Turbo models
# ABOUTME: Includes text encoder, diffusion model, VAE, and ControlNet

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Z Image Turbo models..."

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors" \
    "/workspace/ComfyUI/models/vae/ae.safetensors"

download "https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union/resolve/main/Z-Image-Turbo-Fun-Controlnet-Union.safetensors" \
    "/workspace/ComfyUI/models/controlnet/Z-Image-Turbo-Fun-Controlnet-Union.safetensors"

echo "Download finished"
