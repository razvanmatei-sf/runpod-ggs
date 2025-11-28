#!/bin/bash

# Krita AI Diffusion Installer for RunPod
# Installs required custom nodes and downloads essential models

set -e

# Enable HuggingFace high-speed downloads
export HF_HUB_ENABLE_HF_TRANSFER=1

echo "🎨 Krita AI Diffusion Installer"
echo "==============================="

# Base models directory
MODELS_DIR="/workspace/models"
mkdir -p "$MODELS_DIR"/{clip_vision,upscale_models,controlnet,ipadapter,loras,inpaint,style_models,checkpoints}

echo "📁 Created model directories in $MODELS_DIR"

# Install Custom Nodes First
echo ""
echo "🔧 Installing Custom Nodes..."
echo "============================"

CUSTOM_NODES_DIR="/workspace/ComfyUI/custom_nodes"
cd "$CUSTOM_NODES_DIR"

# ControlNet preprocessors
if [ ! -d "comfyui_controlnet_aux" ]; then
    echo "Installing ControlNet preprocessors..."
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
    cd comfyui_controlnet_aux
    if [ -f "requirements.txt" ]; then
        source /workspace/venv/bin/activate
        pip install -r requirements.txt
    fi
    if [ -f "install.py" ]; then
        python install.py
    fi
    cd "$CUSTOM_NODES_DIR"
else
    echo "✅ ControlNet preprocessors already installed"
fi

# IP-Adapter
if [ ! -d "ComfyUI_IPAdapter_plus" ]; then
    echo "Installing IP-Adapter..."
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
    cd ComfyUI_IPAdapter_plus
    if [ -f "requirements.txt" ]; then
        source /workspace/venv/bin/activate
        pip install -r requirements.txt
    fi
    if [ -f "install.py" ]; then
        python install.py
    fi
    cd "$CUSTOM_NODES_DIR"
else
    echo "✅ IP-Adapter already installed"
fi

# Inpaint nodes
if [ ! -d "comfyui-inpaint-nodes" ]; then
    echo "Installing Inpaint nodes..."
    git clone https://github.com/Acly/comfyui-inpaint-nodes.git
    cd comfyui-inpaint-nodes
    if [ -f "requirements.txt" ]; then
        source /workspace/venv/bin/activate
        pip install -r requirements.txt
    fi
    if [ -f "install.py" ]; then
        python install.py
    fi
    cd "$CUSTOM_NODES_DIR"
else
    echo "✅ Inpaint nodes already installed"
fi

# External tooling nodes
if [ ! -d "comfyui-tooling-nodes" ]; then
    echo "Installing External tooling nodes..."
    git clone https://github.com/Acly/comfyui-tooling-nodes.git
    cd comfyui-tooling-nodes
    if [ -f "requirements.txt" ]; then
        source /workspace/venv/bin/activate
        pip install -r requirements.txt
    fi
    if [ -f "install.py" ]; then
        python install.py
    fi
    cd "$CUSTOM_NODES_DIR"
else
    echo "✅ External tooling nodes already installed"
fi

echo ""
echo "✅ Custom nodes installation complete!"
echo ""
echo "⬇️  Now downloading models..."
echo "============================"

# CLIP Vision
echo "⬇️  Downloading CLIP Vision models..."
cd "$MODELS_DIR/clip_vision"
if [ ! -f "clip-vision_vit-h.safetensors" ]; then
    wget -O clip-vision_vit-h.safetensors \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
fi
if [ ! -f "sigclip_vision_patch14_384.safetensors" ]; then
    wget -O sigclip_vision_patch14_384.safetensors \
        "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors"
fi

# Upscale Models
echo "⬇️  Downloading Upscale models..."
cd "$MODELS_DIR/upscale_models"
if [ ! -f "4x_NMKD-Superscale-SP_178000_G.pth" ]; then
    wget -O 4x_NMKD-Superscale-SP_178000_G.pth \
        "https://huggingface.co/gemasai/4x_NMKD-Superscale-SP_178000_G/resolve/main/4x_NMKD-Superscale-SP_178000_G.pth"
fi
if [ ! -f "OmniSR_X2_DIV2K.safetensors" ]; then
    wget -O OmniSR_X2_DIV2K.safetensors \
        "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X2_DIV2K.safetensors"
fi
if [ ! -f "OmniSR_X3_DIV2K.safetensors" ]; then
    wget -O OmniSR_X3_DIV2K.safetensors \
        "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X3_DIV2K.safetensors"
fi
if [ ! -f "OmniSR_X4_DIV2K.safetensors" ]; then
    wget -O OmniSR_X4_DIV2K.safetensors \
        "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X4_DIV2K.safetensors"
fi
if [ ! -f "HAT_SRx4_ImageNet-pretrain.pth" ]; then
    wget -O HAT_SRx4_ImageNet-pretrain.pth \
        "https://huggingface.co/Acly/hat/resolve/main/HAT_SRx4_ImageNet-pretrain.pth"
fi
if [ ! -f "Real_HAT_GAN_sharper.pth" ]; then
    wget -O Real_HAT_GAN_sharper.pth \
        "https://huggingface.co/Acly/hat/resolve/main/Real_HAT_GAN_sharper.pth"
fi

# ControlNet Models
echo "⬇️  Downloading ControlNet models..."
cd "$MODELS_DIR/controlnet"
if [ ! -f "control_v11p_sd15_inpaint_fp16.safetensors" ]; then
    wget -O control_v11p_sd15_inpaint_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11f1e_sd15_tile_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11f1e_sd15_tile_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11f1e_sd15_tile_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11p_sd15_scribble_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11p_sd15_scribble_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_scribble_fp16.safetensors"
fi
if [ ! -f "control_v11p_sd15_lineart_fp16.safetensors" ]; then
    wget -O control_v11p_sd15_lineart_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_lineart_fp16.safetensors"
fi
if [ ! -f "control_v11p_sd15_softedge_fp16.safetensors" ]; then
    wget -O control_v11p_sd15_softedge_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_softedge_fp16.safetensors"
fi
if [ ! -f "control_v11p_sd15_canny_fp16.safetensors" ]; then
    wget -O control_v11p_sd15_canny_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_canny_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11f1p_sd15_depth_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11f1p_sd15_depth_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11f1p_sd15_depth_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11p_sd15_normalbae_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11p_sd15_normalbae_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_normalbae_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11p_sd15_openpose_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11p_sd15_openpose_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_openpose_fp16.safetensors"
fi
if [ ! -f "control_lora_rank128_v11p_sd15_seg_fp16.safetensors" ]; then
    wget -O control_lora_rank128_v11p_sd15_seg_fp16.safetensors \
        "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_seg_fp16.safetensors"
fi
if [ ! -f "control_v1p_sd15_qrcode_monster.safetensors" ]; then
    wget -O control_v1p_sd15_qrcode_monster.safetensors \
        "https://huggingface.co/monster-labs/control_v1p_sd15_qrcode_monster/resolve/main/control_v1p_sd15_qrcode_monster.safetensors"
fi
if [ ! -f "xinsir-controlnet-union-sdxl-1.0-promax.safetensors" ]; then
    wget -O xinsir-controlnet-union-sdxl-1.0-promax.safetensors \
        "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors"
fi
if [ ! -f "control_v1p_sdxl_qrcode_monster.safetensors" ]; then
    wget -O control_v1p_sdxl_qrcode_monster.safetensors \
        "https://huggingface.co/monster-labs/control_v1p_sdxl_qrcode_monster/resolve/main/diffusion_pytorch_model.safetensors"
fi
if [ ! -f "FLUX.1-dev-Controlnet-Inpainting-Beta.safetensors" ]; then
    wget -O FLUX.1-dev-Controlnet-Inpainting-Beta.safetensors \
        "https://huggingface.co/alimama-creative/FLUX.1-dev-Controlnet-Inpainting-Beta/resolve/main/diffusion_pytorch_model.safetensors"
fi
if [ ! -f "mistoline_flux.dev_v1.safetensors" ]; then
    wget -O mistoline_flux.dev_v1.safetensors \
        "https://huggingface.co/TheMistoAI/MistoLine_Flux.dev/resolve/main/mistoline_flux.dev_v1.safetensors"
fi

# IP-Adapter Models
echo "⬇️  Downloading IP-Adapter models..."
cd "$MODELS_DIR/ipadapter"
if [ ! -f "ip-adapter_sd15.safetensors" ]; then
    wget -O ip-adapter_sd15.safetensors \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors"
fi
if [ ! -f "ip-adapter_sdxl_vit-h.safetensors" ]; then
    wget -O ip-adapter_sdxl_vit-h.safetensors \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors"
fi
if [ ! -f "ip-adapter-faceid-plusv2_sd15.bin" ]; then
    wget -O ip-adapter-faceid-plusv2_sd15.bin \
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin"
fi
if [ ! -f "ip-adapter-faceid-plusv2_sdxl.bin" ]; then
    wget -O ip-adapter-faceid-plusv2_sdxl.bin \
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl.bin"
fi

# LoRA Models
echo "⬇️  Downloading LoRA models..."
cd "$MODELS_DIR/loras"
if [ ! -f "Hyper-SD15-8steps-CFG-lora.safetensors" ]; then
    wget -O Hyper-SD15-8steps-CFG-lora.safetensors \
        "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SD15-8steps-CFG-lora.safetensors"
fi
if [ ! -f "Hyper-SDXL-8steps-CFG-lora.safetensors" ]; then
    wget -O Hyper-SDXL-8steps-CFG-lora.safetensors \
        "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-8steps-CFG-lora.safetensors"
fi
if [ ! -f "ip-adapter-faceid-plusv2_sd15_lora.safetensors" ]; then
    wget -O ip-adapter-faceid-plusv2_sd15_lora.safetensors \
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15_lora.safetensors"
fi
if [ ! -f "ip-adapter-faceid-plusv2_sdxl_lora.safetensors" ]; then
    wget -O ip-adapter-faceid-plusv2_sdxl_lora.safetensors \
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl_lora.safetensors"
fi

# Inpaint Models
echo "⬇️  Downloading Inpaint models..."
cd "$MODELS_DIR/inpaint"
if [ ! -f "fooocus_inpaint_head.pth" ]; then
    wget -O fooocus_inpaint_head.pth \
        "https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/fooocus_inpaint_head.pth"
fi
if [ ! -f "inpaint_v26.fooocus.patch" ]; then
    wget -O inpaint_v26.fooocus.patch \
        "https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/inpaint_v26.fooocus.patch"
fi
if [ ! -f "MAT_Places512_G_fp16.safetensors" ]; then
    wget -O MAT_Places512_G_fp16.safetensors \
        "https://huggingface.co/Acly/MAT/resolve/main/MAT_Places512_G_fp16.safetensors"
fi

# Style Models
echo "⬇️  Downloading Style models..."
cd "$MODELS_DIR/style_models"
if [ ! -f "flux1-redux-dev.safetensors" ]; then
    wget -O flux1-redux-dev.safetensors \
        "https://files.interstice.cloud/models/flux1-redux-dev.safetensors"
fi

# Checkpoints
echo "⬇️  Downloading Checkpoint models..."
cd "$MODELS_DIR/checkpoints"
if [ ! -f "serenity_v21Safetensors.safetensors" ]; then
    wget -O serenity_v21Safetensors.safetensors \
        "https://huggingface.co/Acly/SD-Checkpoints/resolve/main/serenity_v21Safetensors.safetensors"
fi
if [ ! -f "dreamshaper_8.safetensors" ]; then
    wget -O dreamshaper_8.safetensors \
        "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors"
fi
if [ ! -f "flat2DAnimerge_v45Sharp.safetensors" ]; then
    wget -O flat2DAnimerge_v45Sharp.safetensors \
        "https://huggingface.co/Acly/SD-Checkpoints/resolve/main/flat2DAnimerge_v45Sharp.safetensors"
fi
if [ ! -f "RealVisXL_V5.0_fp16.safetensors" ]; then
    wget -O RealVisXL_V5.0_fp16.safetensors \
        "https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/RealVisXL_V5.0_fp16.safetensors"
fi
if [ ! -f "zavychromaxl_v80.safetensors" ]; then
    wget -O zavychromaxl_v80.safetensors \
        "https://huggingface.co/misri/zavychromaxl_v80/resolve/main/zavychromaxl_v80.safetensors"
fi
if [ ! -f "flux1-dev-fp8.safetensors" ]; then
    wget -O flux1-dev-fp8.safetensors \
        "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors"
fi
if [ ! -f "flux1-schnell-fp8.safetensors" ]; then
    wget -O flux1-schnell-fp8.safetensors \
        "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors"
fi

# Special case: Flux Universal ControlNet (goes in models root)
echo "⬇️  Downloading Flux Universal ControlNet..."
cd "$MODELS_DIR"
if [ ! -f "FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8.safetensors" ]; then
    wget -O FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8.safetensors \
        "https://huggingface.co/ABDALLALSWAITI/FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8/resolve/main/diffusion_pytorch_model.safetensors"
fi

echo ""
echo "✅ Model download complete!"
echo ""
echo "📊 Downloaded models:"
echo "   • CLIP Vision: clip-vision_vit-h, sigclip_vision_patch14_384"
echo "   • Upscale: NMKD, OmniSR (x2/x3/x4), HAT, Real HAT GAN"
echo "   • ControlNet: SD1.5 (inpaint,tile,scribble,lineart,softedge,canny,depth,normal,pose,seg,qrcode)"
echo "   • ControlNet: SDXL (union,qrcode), Flux (union,inpaint,lines)"
echo "   • IP-Adapter: SD1.5/SDXL standard + FaceID"
echo "   • LoRAs: Hyper-SD, IP-Adapter FaceID"
echo "   • Inpaint: Fooocus, MAT"
echo "   • Style: Flux Redux"
echo "   • Checkpoints: Serenity, DreamShaper, Flat2D, RealVis, ZavyChroma, Flux dev/schnell"
echo ""
echo "💾 Total storage used: ~25-30 GB"
echo "📁 Models location: $MODELS_DIR"
echo ""
echo "🎨 Ready for Krita AI Diffusion!"