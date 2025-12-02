#!/bin/bash

cd "$(dirname "$0")"

# HuggingFace download optimizations
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240

echo "=========================================="
echo "Z Image Turbo Models Download"
echo "=========================================="
echo ""

download() {
    url="$1"
    dest="$2"

    mkdir -p "$(dirname "$dest")"

    if [ -f "$dest" ]; then
        echo "Skip: $(basename "$dest") exists"
        return
    fi

    echo "Downloading $(basename "$dest")..."
    wget --show-progress -q -O "$dest" "$url" || curl -L --progress-bar -o "$dest" "$url"
}

echo "=== Downloading Text Encoders ==="
download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"

echo ""
echo "=== Downloading Diffusion Models ==="
download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"

echo ""
echo "=== Downloading VAE ==="
download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors" \
    "/workspace/ComfyUI/models/vae/ae.safetensors"

echo ""
echo "=== Downloading ControlNet ==="
download "https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union/resolve/main/Z-Image-Turbo-Fun-Controlnet-Union.safetensors" \
    "/workspace/ComfyUI/models/controlnet/Z-Image-Turbo-Fun-Controlnet-Union.safetensors"

echo ""
echo "=========================================="
echo "Z Image Turbo download complete!"
echo "=========================================="
