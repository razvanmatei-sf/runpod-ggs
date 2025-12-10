#!/bin/bash
# ABOUTME: Downloads Wan 2.2 video generation models
# ABOUTME: Includes Animate diffusion model and VAE

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Wan video models..."

download "https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/Wan22Animate/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors"

download "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors" \
    "/workspace/ComfyUI/models/vae/Wan2_1_VAE_bf16.safetensors"

echo "Download finished"
