#!/bin/bash
# ABOUTME: Downloads LTX-2 video generation models from Lightricks
# ABOUTME: Includes checkpoints, text encoders, loras, vae, diffusion models and upscalers

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

download "https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors"

# LoRAs
download "https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors" \
    "/workspace/ComfyUI/models/loras/ltx-2-19b-distilled-lora-384.safetensors"

# VAE
download "https://huggingface.co/Kijai/LTXV2_comfy/resolve/main/VAE/LTX2_video_vae_bf16.safetensors" \
    "/workspace/ComfyUI/models/vae/LTX2_video_vae_bf16.safetensors"

echo "Download finished"
