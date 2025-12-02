#!/bin/bash

# ComfyUI Installation Script for RunPod
set -e

echo "Installing ComfyUI"

cd /workspace

if [ -d "ComfyUI" ]; then
    echo "Removing existing ComfyUI installation..."
    rm -rf ComfyUI
fi

git clone https://github.com/comfyanonymous/ComfyUI
cd /workspace/ComfyUI

python3 -m venv --system-site-packages venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Remove default xformers if installed
pip uninstall xformers --yes || true

echo "Installing optimized wheels..."
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

pip install -r /workspace/runpod-ggs/setup/comfy/requirements.txt

cd custom_nodes

git clone https://github.com/ltdrdata/ComfyUI-Manager
[ -f "ComfyUI-Manager/requirements.txt" ] && pip install -r ComfyUI-Manager/requirements.txt

git clone https://github.com/ClownsharkBatwing/RES4LYF
[ -f "RES4LYF/requirements.txt" ] && pip install -r RES4LYF/requirements.txt

cd /workspace/ComfyUI

apt-get update && apt-get install -y psmisc

echo "ComfyUI Installation complete"
