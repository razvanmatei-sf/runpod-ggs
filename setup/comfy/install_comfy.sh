#!/bin/bash

# ComfyUI Installation Script for RunPod
# Base image: runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
# Python 3.12, PyTorch 2.8.0, CUDA 12.8.1
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

# Use --system-site-packages to inherit PyTorch 2.8.0 cu128 from base image
# This avoids reinstalling PyTorch (~2.5GB) and speeds up installation
echo "Creating virtual environment (inheriting system packages)..."
python3 -m venv venv --system-site-packages

# Activate venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

# PyTorch 2.8.0 cu128 is inherited from base image, no need to reinstall
echo "Using PyTorch from base image:"
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA {torch.version.cuda}')"

echo "Installing ComfyUI requirements (excluding torch to keep base image version)..."
# Filter out torch packages from requirements.txt to prevent reinstalling/upgrading
grep -v "^torch" requirements.txt | pip install -r /dev/stdin

# Remove default xformers if installed (we'll install the correct version)
pip uninstall xformers --yes || true

echo "Installing optimized wheels for Python 3.12 + PyTorch 2.8 + CUDA 12..."

# flash_attn 2.8.3 - Official wheel for torch2.8 + cp312 + CUDA 12
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3%2Bcu12torch2.8cxx11abiTRUE-cp312-cp312-linux_x86_64.whl

# xformers - From PyTorch index for cu128, ABI3 wheel works with Python 3.9+
pip install xformers --index-url https://download.pytorch.org/whl/cu128

# sageattention - cp312 wheel from Kijai's precompiled wheels
pip install https://huggingface.co/Kijai/PrecompiledWheels/resolve/main/sageattention-2.2.0-cp312-cp312-linux_x86_64.whl

# insightface - No Python 3.12 prebuilt wheel available yet, skipping
# Can be installed later if needed: pip install insightface

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
