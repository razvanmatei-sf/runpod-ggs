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

download "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors" \
    "ComfyUI/models/clip_vision/clip_vision_h.safetensors"

download "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
    "ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

echo "Done"
