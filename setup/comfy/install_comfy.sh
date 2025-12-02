#!/bin/bash

# ComfyUI Installation Script for RunPod
set -e

echo "========================================================"
echo "ComfyUI Installation"
echo "========================================================"

cd /workspace

# Remove existing ComfyUI if present (fresh install)
if [ -d "ComfyUI" ]; then
    echo "Removing existing ComfyUI installation..."
    rm -rf ComfyUI
fi

echo "Cloning ComfyUI..."
git clone https://github.com/comfyanonymous/ComfyUI

cd /workspace/ComfyUI

echo "Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing PyTorch..."
pip install torch==2.2.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Installing ComfyUI requirements..."
pip install -r requirements.txt

# Remove default xformers if installed
pip uninstall xformers --yes || true

echo "Installing optimized wheels..."
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

echo "Installing shared requirements..."
pip install -r /workspace/runpod-ggs/setup/comfy/requirements.txt

# Install custom nodes
cd custom_nodes

echo "Installing ComfyUI-Manager..."
git clone https://github.com/ltdrdata/ComfyUI-Manager
if [ -f "ComfyUI-Manager/requirements.txt" ]; then
    pip install -r ComfyUI-Manager/requirements.txt
fi

echo "Installing RES4LYF..."
git clone https://github.com/ClownsharkBatwing/RES4LYF
if [ -f "RES4LYF/requirements.txt" ]; then
    pip install -r RES4LYF/requirements.txt
fi

cd /workspace/ComfyUI

# Install psmisc for fuser command
apt-get update
apt-get install -y psmisc

echo ""
echo "========================================================"
echo "ComfyUI Installation complete!"
echo "========================================================"
