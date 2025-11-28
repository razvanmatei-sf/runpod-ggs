#!/bin/bash

# ComfyUI Installation Script for RunPod
set -e

echo "========================================================"
echo "ComfyUI Installation"
echo "========================================================"

cd /workspace

git clone --depth 1 https://github.com/comfyanonymous/ComfyUI

cd /workspace/ComfyUI

git reset --hard
git stash
git pull --force

python -m venv venv

source venv/bin/activate

python -m pip install --upgrade pip

pip install torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129

cd custom_nodes

# ComfyUI-Manager
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager
cd ComfyUI-Manager
git stash
git reset --hard
git pull --force
pip install -r requirements.txt
cd ..

# RES4LYF
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF
cd RES4LYF
git stash
git reset --hard
git pull --force
pip install -r requirements.txt
cd ..

cd ..

echo "Installing ComfyUI requirements..."

pip install -r requirements.txt

pip uninstall xformers --yes

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

cd ..

echo "Installing shared requirements..."

pip install -r /workspace/runpod-ggs/setup/comfy/requirements.txt

apt update
apt install -y psmisc

echo "========================================================"
echo "Installation complete!"
echo "========================================================"
