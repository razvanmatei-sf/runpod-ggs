#!/bin/bash
# ABOUTME: Downloads Wan 2.2 LoRA models for video generation
# ABOUTME: Includes LightX2V, relight, and lightning LoRAs

set -e
cd /workspace
source "$(dirname "$0")/download_helper.sh"

echo "Downloading Wan 2.2 LoRAs..."

download "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"

download "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors"

download "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_relight/WanAnimate_relight_lora_fp16_resized_from_128_to_dynamic_22.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/WanAnimate_relight_lora_fp16_resized_from_128_to_dynamic_22.safetensors"

download "https://huggingface.co/vrgamedevgirl84/Wan14BT2VFusioniX/resolve/8a92890503180afd45ff65dce32d94f1b914544c/OtherLoRa's/Wan14B_RealismBoost.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/Wan14B_RealismBoost.safetensors"

download "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_Lightx2v/Wan_2_2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/Wan_2_2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors"

download "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22-Lightning/old/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors"

download "https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors" \
    "/workspace/ComfyUI/models/loras/Wan/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors"

echo "Download finished"
