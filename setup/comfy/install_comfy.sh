#!/bin/bash

set -e

echo "Installing ComfyUI"

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

git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF
git clone --depth 1 https://github.com/rgthree/rgthree-comfy

cd ComfyUI-Manager
git stash
git reset --hard
git pull --force
[ -f "requirements.txt" ] && pip install -r requirements.txt
cd ..

cd ComfyUI-GGUF
git stash
git reset --hard
git pull --force
[ -f "requirements.txt" ] && pip install -r requirements.txt
cd ..

cd RES4LYF
git stash
git reset --hard
git pull --force
[ -f "requirements.txt" ] && pip install -r requirements.txt
cd ..

cd rgthree-comfy
git stash
git reset --hard
git pull --force
[ -f "requirements.txt" ] && pip install -r requirements.txt
cd ..

cd ..

pip install -r requirements.txt

pip uninstall xformers --yes

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

apt update
apt install psmisc

echo "ComfyUI Installation complete"
