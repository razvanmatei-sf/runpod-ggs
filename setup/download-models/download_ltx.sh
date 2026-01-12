#!/bin/bash
# ABOUTME: Downloads LTX-2 video generation models from Lightricks
# ABOUTME: Includes checkpoints, text encoders, loras, vae, diffusion models and upscalers

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading LTX-2 models..."

# Checkpoints
download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors" \
    "/workspace/ComfyUI/models/checkpoints/ltx-2-19b-dev.safetensors"

download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev-fp8.safetensors" \
    "/workspace/ComfyUI/models/checkpoints/ltx-2-19b-dev-fp8.safetensors"

download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled.safetensors" \
    "/workspace/ComfyUI/models/checkpoints/ltx-2-19b-distilled.safetensors"

download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-fp8.safetensors" \
    "/workspace/ComfyUI/models/checkpoints/ltx-2-19b-distilled-fp8.safetensors"

# Text Encoders
download "https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/gemma_3_12B_it.safetensors"

# LoRAs
download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors" \
    "/workspace/ComfyUI/models/loras/ltx-2-19b-distilled-lora-384.safetensors"

download "https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Left/resolve/main/ltx-2-19b-lora-camera-control-dolly-left.safetensors" \
    "/workspace/ComfyUI/models/loras/ltx-2-19b-lora-camera-control-dolly-left.safetensors"

download "https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Canny-Control/resolve/main/ltx-2-19b-ic-lora-canny-control.safetensors" \
    "/workspace/ComfyUI/models/loras/ltx-2-19b-ic-lora-canny-control.safetensors"

download "https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Depth-Control/resolve/main/ltx-2-19b-ic-lora-depth-control.safetensors" \
    "/workspace/ComfyUI/models/loras/ltx-2-19b-ic-lora-depth-control.safetensors"

# Diffusion Models
download "https://huggingface.co/Comfy-Org/lotus/resolve/main/lotus-depth-d-v1-1.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/lotus-depth-d-v1-1.safetensors"

# VAE
download "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors" \
    "/workspace/ComfyUI/models/vae/vae-ft-mse-840000-ema-pruned.safetensors"

# Latent Upscale Models
download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors" \
    "/workspace/ComfyUI/models/latent_upscale_models/ltx-2-spatial-upscaler-x2-1.0.safetensors"

echo "Download finished"
