#!/bin/bash

cd "$(dirname "$0")"

export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240

download() {
    url="$1"
    dest="$2"
    mkdir -p "$(dirname "$dest")"
    if [ -f "$dest" ]; then
        echo "Skip: $(basename "$dest") exists"
        return
    fi
    echo "Downloading $(basename "$dest")..."
    curl -L -s -o "$dest" "$url"
}

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors" \
    "/workspace/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors" \
    "/workspace/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"

download "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors" \
    "/workspace/ComfyUI/models/vae/ae.safetensors"

download "https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union/resolve/main/Z-Image-Turbo-Fun-Controlnet-Union.safetensors" \
    "/workspace/ComfyUI/models/controlnet/Z-Image-Turbo-Fun-Controlnet-Union.safetensors"

echo "Z Image Turbo download complete"
