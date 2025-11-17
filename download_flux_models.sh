#!/bin/bash

# Flux Models Download Script for RunPod
# Downloads all Flux models to workspace models directory

set -e

echo "=========================================="
echo "🚀 Flux Models Download Script"
echo "=========================================="

# HuggingFace optimizations
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240

# Check for HuggingFace token (required for gated models)
if [ -z "$HUGGING_FACE_HUB_TOKEN" ] && [ -z "$HF_TOKEN" ]; then
    echo "⚠️  WARNING: HUGGING_FACE_HUB_TOKEN not set"
    echo "   Some models require authentication. Set with:"
    echo "   export HUGGING_FACE_HUB_TOKEN=hf_your_token"
    echo ""
fi
export HF_TOKEN="${HF_TOKEN:-$HUGGING_FACE_HUB_TOKEN}"

# Base models directory
MODELS_DIR="/workspace/models"

# Create model directories (skip if they exist)
echo "📁 Ensuring model directories exist..."
mkdir -p "$MODELS_DIR/diffusion_models" 2>/dev/null || true
mkdir -p "$MODELS_DIR/clip" 2>/dev/null || true
mkdir -p "$MODELS_DIR/clip_vision" 2>/dev/null || true
mkdir -p "$MODELS_DIR/vae" 2>/dev/null || true
mkdir -p "$MODELS_DIR/controlnet" 2>/dev/null || true

echo "🔐 HuggingFace token set for authenticated downloads"
echo ""

# Diffusion Models
echo "⬇️  Downloading Diffusion Models..."
cd "$MODELS_DIR/diffusion_models"

echo "  • flux1-dev.safetensors"
if [ ! -f "flux1-dev.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O flux1-dev.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • flux1-schnell.safetensors"
if [ ! -f "flux1-schnell.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O flux1-schnell.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • flux1-fill-dev.safetensors"
if [ ! -f "flux1-fill-dev.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O flux1-fill-dev.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev/resolve/main/flux1-fill-dev.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • flux1-kontext-dev.safetensors"
if [ ! -f "flux1-kontext-dev.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O flux1-kontext-dev.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/resolve/main/flux1-kontext-dev.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • flux1-redux-dev.safetensors"
if [ ! -f "flux1-redux-dev.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O flux1-redux-dev.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-Redux-dev/resolve/main/flux1-redux-dev.safetensors"
else
    echo "    ✅ Already exists"
fi

# CLIP Models
echo ""
echo "⬇️  Downloading CLIP Models..."
cd "$MODELS_DIR/clip"

echo "  • clip_l.safetensors"
if [ ! -f "clip_l.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O clip_l.safetensors \
         "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • t5xxl_fp8_e4m3fn.safetensors"
if [ ! -f "t5xxl_fp8_e4m3fn.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O t5xxl_fp8_e4m3fn.safetensors \
         "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • t5xxl_fp16.safetensors"
if [ ! -f "t5xxl_fp16.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O t5xxl_fp16.safetensors \
         "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"
else
    echo "    ✅ Already exists"
fi

# CLIP Vision Models
echo ""
echo "⬇️  Downloading CLIP Vision Models..."
cd "$MODELS_DIR/clip_vision"

echo "  • sigclip_vision_patch14_384.safetensors"
if [ ! -f "sigclip_vision_patch14_384.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O sigclip_vision_patch14_384.safetensors \
         "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors"
else
    echo "    ✅ Already exists"
fi

# VAE Models
echo ""
echo "⬇️  Downloading VAE Models..."
cd "$MODELS_DIR/vae"

echo "  • ae.safetensors"
if [ ! -f "ae.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O ae.safetensors \
         "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors"
else
    echo "    ✅ Already exists"
fi

# ControlNet Models
echo ""
echo "⬇️  Downloading ControlNet Models..."
cd "$MODELS_DIR/controlnet"

echo "  • FLUX.1-dev-ControlNet-Union-Pro.safetensors"
if [ ! -f "FLUX.1-dev-ControlNet-Union-Pro.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O FLUX.1-dev-ControlNet-Union-Pro.safetensors \
         "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/diffusion_pytorch_model.safetensors"
else
    echo "    ✅ Already exists"
fi

echo "  • FLUX.1-dev-ControlNet-Union-Pro-2.0.safetensors"
if [ ! -f "FLUX.1-dev-ControlNet-Union-Pro-2.0.safetensors" ]; then
    wget --header="Authorization: Bearer $HUGGING_FACE_HUB_TOKEN" \
         -O FLUX.1-dev-ControlNet-Union-Pro-2.0.safetensors \
         "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro-2.0/resolve/main/diffusion_pytorch_model.safetensors"
else
    echo "    ✅ Already exists"
fi

echo ""
echo "=========================================="
echo "✅ Flux Models Download Complete!"
echo "=========================================="
echo ""
echo "📊 Downloaded models:"
echo "   • Diffusion Models: flux1-dev, flux1-schnell, flux1-fill-dev, flux1-kontext-dev, flux1-redux-dev"
echo "   • CLIP: clip_l, t5xxl_fp8_e4m3fn, t5xxl_fp16"
echo "   • CLIP Vision: sigclip_vision_patch14_384"
echo "   • VAE: ae"
echo "   • ControlNet: FLUX.1-dev-ControlNet-Union-Pro, FLUX.1-dev-ControlNet-Union-Pro-2.0"
echo ""
echo "💾 Total storage used: ~40-50 GB"
echo "📁 Models location: $MODELS_DIR"
echo ""
echo "🚀 Ready for Flux workflows in ComfyUI!"