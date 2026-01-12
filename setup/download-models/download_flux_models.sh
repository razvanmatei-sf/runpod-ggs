#!/bin/bash
# ABOUTME: Downloads Flux models (diffusion, CLIP, VAE, ControlNet)
# ABOUTME: Requires HF_TOKEN for gated model access

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Flux models..."

# Diffusion models
download "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors" \
    "/workspace/models/diffusion_models/flux1-dev.safetensors"

download "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
    "/workspace/models/diffusion_models/flux1-schnell.safetensors"

download "https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev/resolve/main/flux1-fill-dev.safetensors" \
    "/workspace/models/diffusion_models/flux1-fill-dev.safetensors"

download "https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/resolve/main/flux1-kontext-dev.safetensors" \
    "/workspace/models/diffusion_models/flux1-kontext-dev.safetensors"

download "https://huggingface.co/black-forest-labs/FLUX.1-Redux-dev/resolve/main/flux1-redux-dev.safetensors" \
    "/workspace/models/diffusion_models/flux1-redux-dev.safetensors"

# CLIP models
download "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors" \
    "/workspace/models/clip/clip_l.safetensors"

download "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors" \
    "/workspace/models/clip/t5xxl_fp8_e4m3fn.safetensors"

download "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors" \
    "/workspace/models/clip/t5xxl_fp16.safetensors"

# CLIP Vision
download "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors" \
    "/workspace/models/clip_vision/sigclip_vision_patch14_384.safetensors"

# VAE
download "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors" \
    "/workspace/models/vae/ae.safetensors"

# ControlNet
download "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/diffusion_pytorch_model.safetensors" \
    "/workspace/models/controlnet/FLUX.1-dev-ControlNet-Union-Pro.safetensors"

download "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro-2.0/resolve/main/diffusion_pytorch_model.safetensors" \
    "/workspace/models/controlnet/FLUX.1-dev-ControlNet-Union-Pro-2.0.safetensors"

echo "Download finished"
