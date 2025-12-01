#!/bin/bash

# ComfyUI Installation Script for RunPod
set -e

# Start timer
START_TIME=$(date +%s)

# Suppress UV hardlink warning (can't use hardlinks across filesystems)
export UV_LINK_MODE=copy

echo "========================================================"
echo "ComfyUI Installation"
echo "========================================================"

cd /workspace

git clone --depth 1 https://github.com/comfyanonymous/ComfyUI

cd /workspace/ComfyUI

git reset --hard
git stash
git pull --force

echo "Creating virtual environment with UV..."
uv venv venv

echo "Installing PyTorch with UV (10-100x faster than pip)..."
uv pip install --python venv/bin/python torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129

cd custom_nodes

# ComfyUI-Manager
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager
cd ComfyUI-Manager
git stash
git reset --hard
git pull --force
uv pip install --python ../venv/bin/python -r requirements.txt
cd ..

# RES4LYF
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF
cd RES4LYF
git stash
git reset --hard
git pull --force
uv pip install --python ../venv/bin/python -r requirements.txt
cd ..

cd ..

echo "Installing ComfyUI requirements..."

uv pip install --python venv/bin/python -r requirements.txt

uv pip uninstall --python venv/bin/python xformers --yes

echo "Installing optimized wheels with UV..."
uv pip install --python venv/bin/python https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
uv pip install --python venv/bin/python https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
uv pip install --python venv/bin/python https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
uv pip install --python venv/bin/python https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

cd ..

echo "Installing shared requirements..."

uv pip install --python venv/bin/python -r /workspace/runpod-ggs/setup/comfy/requirements.txt

apt update
apt install -y psmisc

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Installation complete!"
echo "========================================================"
echo "⏱️  Total installation time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
