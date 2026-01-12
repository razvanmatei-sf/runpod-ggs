#!/bin/bash
# ABOUTME: Downloads Wan 2.2 GGUF quantized models
# ABOUTME: Optimized models for lower VRAM usage

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Wan 2.2 GGUF models..."

download "https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF/resolve/main/wan2.2_i2v_high_noise_14B_Q6_K.gguf" \
    "/workspace/ComfyUI/models/unet/wan2.2_i2v_high_noise_14B_Q6_K.gguf"

download "https://huggingface.co/bullerwins/Wan2.2-I2V-A14B-GGUF/resolve/main/wan2.2_i2v_low_noise_14B_Q6_K.gguf" \
    "/workspace/ComfyUI/models/unet/wan2.2_i2v_low_noise_14B_Q6_K.gguf"

echo "Download finished"
