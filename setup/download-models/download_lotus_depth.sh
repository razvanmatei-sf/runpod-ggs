#!/bin/bash
# ABOUTME: Downloads Lotus depth estimation models
# ABOUTME: Includes diffusion model and VAE

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Lotus depth models..."

download "https://huggingface.co/Comfy-Org/lotus/resolve/main/lotus-depth-d-v1-1.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/lotus-depth-d-v1-1.safetensors"

download "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors" \
    "/workspace/ComfyUI/models/vae/vae-ft-mse-840000-ema-pruned.safetensors"

echo "Download finished"
