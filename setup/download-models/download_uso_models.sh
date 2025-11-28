#!/bin/bash

cd "$(dirname "$0")"

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

download "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
    "ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors"

download "https://huggingface.co/Comfy-Org/USO_1.0_Repackaged/resolve/main/split_files/loras/uso-flux1-dit-lora-v1.safetensors" \
    "ComfyUI/models/loras/uso-flux1-dit-lora-v1.safetensors"

download "https://huggingface.co/Comfy-Org/USO_1.0_Repackaged/resolve/main/split_files/model_patches/uso-flux1-projector-v1.safetensors" \
    "ComfyUI/models/model_patches/uso-flux1-projector-v1.safetensors"

download "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors" \
    "ComfyUI/models/clip_visions/sigclip_vision_patch14_384.safetensors"

echo "Done"
