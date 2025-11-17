#!/bin/bash

cd "$(dirname "$0")"

# HuggingFace download optimizations
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240

echo "HuggingFace optimizations enabled:"
echo "  HF_HUB_ENABLE_HF_TRANSFER=1"
echo "  HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240 (84.5GB cache)"
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

echo "=== Downloading Qwen Diffusion Models ==="
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors" \
    "ComfyUI/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/non_official/diffusion_models/qwen_image_distill_full_fp8_e4m3fn.safetensors" \
    "ComfyUI/models/diffusion_models/qwen_image_distill_full_fp8_e4m3fn.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors" \
    "ComfyUI/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors"

echo ""
echo "=== Downloading Qwen Text Encoders ==="
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors" \
    "ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"

echo ""
echo "=== Downloading Qwen VAE ==="
download "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors" \
    "ComfyUI/models/vae/qwen_image_vae.safetensors"

echo ""
echo "=== Downloading Qwen Lightning LoRAs ==="
download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-4steps-V1.0.safetensors" \
    "ComfyUI/models/loras/Qwen-Image-Lightning-4steps-V1.0.safetensors"

download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-4steps-V2.0.safetensors" \
    "ComfyUI/models/loras/Qwen-Image-Lightning-4steps-V2.0.safetensors"

download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V2.0.safetensors" \
    "ComfyUI/models/loras/Qwen-Image-Lightning-8steps-V2.0.safetensors"

download "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors" \
    "ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors"

echo ""
echo "=== Downloading Qwen InstantX ControlNets ==="
download "https://huggingface.co/Comfy-Org/Qwen-Image-InstantX-ControlNets/resolve/main/split_files/controlnet/Qwen-Image-InstantX-ControlNet-Union.safetensors" \
    "ComfyUI/models/controlnet/Qwen-Image-InstantX-ControlNet-Union.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-InstantX-ControlNets/resolve/main/split_files/controlnet/Qwen-Image-InstantX-ControlNet-Inpainting.safetensors" \
    "ComfyUI/models/controlnet/Qwen-Image-InstantX-ControlNet-Inpainting.safetensors"

echo ""
echo "=== Downloading Qwen DiffSynth ControlNet Patches ==="
download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_canny_diffsynth_controlnet.safetensors" \
    "ComfyUI/models/model_patches/qwen_image_canny_diffsynth_controlnet.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_depth_diffsynth_controlnet.safetensors" \
    "ComfyUI/models/model_patches/qwen_image_depth_diffsynth_controlnet.safetensors"

download "https://huggingface.co/Comfy-Org/Qwen-Image-DiffSynth-ControlNets/resolve/main/split_files/model_patches/qwen_image_inpaint_diffsynth_controlnet.safetensors" \
    "ComfyUI/models/model_patches/qwen_image_inpaint_diffsynth_controlnet.safetensors"

echo ""
echo "=== All Qwen models downloaded ==="
