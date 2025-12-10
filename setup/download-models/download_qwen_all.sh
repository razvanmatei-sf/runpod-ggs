#!/bin/bash
# ABOUTME: Downloads Qwen image generation and editing models
# ABOUTME: Includes diffusion models, text encoders, VAE, LoRAs, and ControlNets

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Qwen models..."

# Diffusion models
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors"

# Text encoders
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"

# VAE
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors" \
    "/workspace/ComfyUI/models/vae/qwen_image_vae.safetensors"

# LoRAs
download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-4steps-V2.0.safetensors" \
    "/workspace/ComfyUI/models/loras/Qwen-Image-Lightning-4steps-V2.0.safetensors"

download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V2.0.safetensors" \
    "/workspace/ComfyUI/models/loras/Qwen-Image-Lightning-8steps-V2.0.safetensors"

download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors" \
    "/workspace/ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors"

# ControlNets
download "https://huggingface.co/Comfy-Org/Qwen-Image-InstantX-ControlNets/resolve/main/split_files/controlnet/Qwen-Image-InstantX-ControlNet-Union.safetensors" \
    "/workspace/ComfyUI/models/controlnet/Qwen-Image-InstantX-ControlNet-Union.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-InstantX-ControlNets/resolve/main/split_files/controlnet/Qwen-Image-InstantX-ControlNet-Inpainting.safetensors" \
    "/workspace/ComfyUI/models/controlnet/Qwen-Image-InstantX-ControlNet-Inpainting.safetensors"

# Model patches
download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_canny_diffsynth_controlnet.safetensors" \
    "/workspace/ComfyUI/models/model_patches/qwen_image_canny_diffsynth_controlnet.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_depth_diffsynth_controlnet.safetensors" \
    "/workspace/ComfyUI/models/model_patches/qwen_image_depth_diffsynth_controlnet.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_inpaint_diffsynth_controlnet.safetensors" \
    "/workspace/ComfyUI/models/model_patches/qwen_image_inpaint_diffsynth_controlnet.safetensors"

echo "Download finished"
