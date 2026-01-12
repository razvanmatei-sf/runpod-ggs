#!/bin/bash
# ABOUTME: Downloads models required for Krita AI Diffusion plugin
# ABOUTME: Includes CLIP Vision, upscalers, ControlNets, IP-Adapters, LoRAs, and checkpoints

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Krita AI Diffusion models..."

# CLIP Vision
download "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
    "/workspace/models/clip_vision/clip-vision_vit-h.safetensors"
download "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors" \
    "/workspace/models/clip_vision/sigclip_vision_patch14_384.safetensors"

# Upscale models
download "https://huggingface.co/gemasai/4x_NMKD-Superscale-SP_178000_G/resolve/main/4x_NMKD-Superscale-SP_178000_G.pth" \
    "/workspace/models/upscale_models/4x_NMKD-Superscale-SP_178000_G.pth"
download "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X2_DIV2K.safetensors" \
    "/workspace/models/upscale_models/OmniSR_X2_DIV2K.safetensors"
download "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X3_DIV2K.safetensors" \
    "/workspace/models/upscale_models/OmniSR_X3_DIV2K.safetensors"
download "https://huggingface.co/Acly/Omni-SR/resolve/main/OmniSR_X4_DIV2K.safetensors" \
    "/workspace/models/upscale_models/OmniSR_X4_DIV2K.safetensors"
download "https://huggingface.co/Acly/hat/resolve/main/HAT_SRx4_ImageNet-pretrain.pth" \
    "/workspace/models/upscale_models/HAT_SRx4_ImageNet-pretrain.pth"
download "https://huggingface.co/Acly/hat/resolve/main/Real_HAT_GAN_sharper.pth" \
    "/workspace/models/upscale_models/Real_HAT_GAN_sharper.pth"

# ControlNet SD1.5
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors" \
    "/workspace/models/controlnet/control_v11p_sd15_inpaint_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11f1e_sd15_tile_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11f1e_sd15_tile_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_scribble_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11p_sd15_scribble_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_lineart_fp16.safetensors" \
    "/workspace/models/controlnet/control_v11p_sd15_lineart_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_softedge_fp16.safetensors" \
    "/workspace/models/controlnet/control_v11p_sd15_softedge_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_canny_fp16.safetensors" \
    "/workspace/models/controlnet/control_v11p_sd15_canny_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11f1p_sd15_depth_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11f1p_sd15_depth_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_normalbae_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11p_sd15_normalbae_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_openpose_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11p_sd15_openpose_fp16.safetensors"
download "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_lora_rank128_v11p_sd15_seg_fp16.safetensors" \
    "/workspace/models/controlnet/control_lora_rank128_v11p_sd15_seg_fp16.safetensors"
download "https://huggingface.co/monster-labs/control_v1p_sd15_qrcode_monster/resolve/main/control_v1p_sd15_qrcode_monster.safetensors" \
    "/workspace/models/controlnet/control_v1p_sd15_qrcode_monster.safetensors"

# ControlNet SDXL
download "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors" \
    "/workspace/models/controlnet/xinsir-controlnet-union-sdxl-1.0-promax.safetensors"
download "https://huggingface.co/monster-labs/control_v1p_sdxl_qrcode_monster/resolve/main/diffusion_pytorch_model.safetensors" \
    "/workspace/models/controlnet/control_v1p_sdxl_qrcode_monster.safetensors"

# ControlNet Flux
download "https://huggingface.co/alimama-creative/FLUX.1-dev-Controlnet-Inpainting-Beta/resolve/main/diffusion_pytorch_model.safetensors" \
    "/workspace/models/controlnet/FLUX.1-dev-Controlnet-Inpainting-Beta.safetensors"
download "https://huggingface.co/TheMistoAI/MistoLine_Flux.dev/resolve/main/mistoline_flux.dev_v1.safetensors" \
    "/workspace/models/controlnet/mistoline_flux.dev_v1.safetensors"
download "https://huggingface.co/ABDALLALSWAITI/FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8/resolve/main/diffusion_pytorch_model.safetensors" \
    "/workspace/models/controlnet/FLUX.1-dev-ControlNet-Union-Pro-2.0-fp8.safetensors"

# IP-Adapter
download "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors" \
    "/workspace/models/ipadapter/ip-adapter_sd15.safetensors"
download "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors" \
    "/workspace/models/ipadapter/ip-adapter_sdxl_vit-h.safetensors"
download "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin" \
    "/workspace/models/ipadapter/ip-adapter-faceid-plusv2_sd15.bin"
download "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl.bin" \
    "/workspace/models/ipadapter/ip-adapter-faceid-plusv2_sdxl.bin"

# LoRAs
download "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SD15-8steps-CFG-lora.safetensors" \
    "/workspace/models/loras/Hyper-SD15-8steps-CFG-lora.safetensors"
download "https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-8steps-CFG-lora.safetensors" \
    "/workspace/models/loras/Hyper-SDXL-8steps-CFG-lora.safetensors"
download "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15_lora.safetensors" \
    "/workspace/models/loras/ip-adapter-faceid-plusv2_sd15_lora.safetensors"
download "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl_lora.safetensors" \
    "/workspace/models/loras/ip-adapter-faceid-plusv2_sdxl_lora.safetensors"

# Inpaint
download "https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/fooocus_inpaint_head.pth" \
    "/workspace/models/inpaint/fooocus_inpaint_head.pth"
download "https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/inpaint_v26.fooocus.patch" \
    "/workspace/models/inpaint/inpaint_v26.fooocus.patch"
download "https://huggingface.co/Acly/MAT/resolve/main/MAT_Places512_G_fp16.safetensors" \
    "/workspace/models/inpaint/MAT_Places512_G_fp16.safetensors"

# Style models
download "https://files.interstice.cloud/models/flux1-redux-dev.safetensors" \
    "/workspace/models/style_models/flux1-redux-dev.safetensors"

# Checkpoints
download "https://huggingface.co/Acly/SD-Checkpoints/resolve/main/serenity_v21Safetensors.safetensors" \
    "/workspace/models/checkpoints/serenity_v21Safetensors.safetensors"
download "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors" \
    "/workspace/models/checkpoints/dreamshaper_8.safetensors"
download "https://huggingface.co/Acly/SD-Checkpoints/resolve/main/flat2DAnimerge_v45Sharp.safetensors" \
    "/workspace/models/checkpoints/flat2DAnimerge_v45Sharp.safetensors"
download "https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/RealVisXL_V5.0_fp16.safetensors" \
    "/workspace/models/checkpoints/RealVisXL_V5.0_fp16.safetensors"
download "https://huggingface.co/misri/zavychromaxl_v80/resolve/main/zavychromaxl_v80.safetensors" \
    "/workspace/models/checkpoints/zavychromaxl_v80.safetensors"
download "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
    "/workspace/models/checkpoints/flux1-dev-fp8.safetensors"
download "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors" \
    "/workspace/models/checkpoints/flux1-schnell-fp8.safetensors"

echo "Download finished"
