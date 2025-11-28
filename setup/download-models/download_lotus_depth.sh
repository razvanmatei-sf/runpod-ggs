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

download "https://huggingface.co/Comfy-Org/lotus/resolve/main/lotus-depth-d-v1-1.safetensors" \
    "ComfyUI/models/diffusion_models/lotus-depth-d-v1-1.safetensors"

download "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors" \
    "ComfyUI/models/vae/vae-ft-mse-840000-ema-pruned.safetensors"

echo "Done"
