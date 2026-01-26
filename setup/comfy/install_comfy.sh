#!/bin/bash
# ABOUTME: Installs ComfyUI with PyTorch 2.9.1, CUDA 13.0, and essential custom nodes.
# ABOUTME: Uses uv for fast package installation. Calls setup_comfy_folders.sh at the end.

set -e

export UV_SKIP_WHEEL_FILENAME_CHECK=1
export UV_LINK_MODE=copy

echo "Installing ComfyUI..."

cd /workspace

git clone --depth 1 https://github.com/Comfy-Org/ComfyUI

cd /workspace/ComfyUI

git reset --hard
git stash
git pull --force

# Check Python 3.10 availability
echo "Checking Python 3.10 availability..."

PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    if [ "$PYTHON_VERSION" = "3.10" ]; then
        echo "Default python3 is Python 3.10"
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    if command -v python3.10 &> /dev/null; then
        echo "Found python3.10 command"
        PYTHON_CMD="python3.10"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Python 3.10 not found. Installing Python 3.10..."
    apt update
    apt install -y python3.10 python3.10-venv python3.10-dev
    
    if command -v python3.10 &> /dev/null; then
        echo "Python 3.10 installed successfully"
        PYTHON_CMD="python3.10"
    else
        echo "Failed to install Python 3.10. Exiting..."
        exit 1
    fi
fi

echo "Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

source venv/bin/activate

python3 -m pip install --upgrade pip

pip install uv

uv pip install torch==2.9.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

cd custom_nodes

# Core custom nodes
echo "Installing custom nodes..."

git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF
git clone --depth 1 https://github.com/rgthree/rgthree-comfy
git clone --depth 1 https://github.com/silveroxides/ComfyUI-QuantOps
git clone --depth 1 https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
git clone --depth 1 https://github.com/FurkanGozukara/ComfyUI-TeaCache
git clone --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF

# Setup ComfyUI-Manager
cd ComfyUI-Manager
git stash
git reset --hard
git pull --force
uv pip install -r requirements.txt
cd ..

# Setup ComfyUI-GGUF
cd ComfyUI-GGUF
git stash
git reset --hard
git pull --force
uv pip install -r requirements.txt
cd ..

# Setup rgthree-comfy
cd rgthree-comfy
git stash
git reset --hard
git pull --force
[ -f "requirements.txt" ] && uv pip install -r requirements.txt
cd ..

# Setup ComfyUI-QuantOps
cd ComfyUI-QuantOps
git reset --hard
git pull
cd ..

# Setup ComfyUI-TeaCache
cd ComfyUI-TeaCache
git remote set-url origin https://github.com/FurkanGozukara/ComfyUI-TeaCache
git stash
git reset --hard
git pull --force
cd ..

# Setup RES4LYF
cd RES4LYF
git stash
git reset --hard
git pull --force
uv pip install -r requirements.txt
cd ..

# Install SwarmUI ExtraNodes
echo "Installing SwarmUI ExtraNodes..."

git clone --depth 1 --filter=blob:none --sparse https://github.com/mcmonkeyprojects/SwarmUI
cd SwarmUI
git sparse-checkout set --no-cone \
  src/BuiltinExtensions/ComfyUIBackend/ExtraNodes/SwarmComfyCommon \
  src/BuiltinExtensions/ComfyUIBackend/ExtraNodes/SwarmComfyExtra
git checkout

cp -r src/BuiltinExtensions/ComfyUIBackend/ExtraNodes/SwarmComfyCommon ../SwarmComfyCommon
cp -r src/BuiltinExtensions/ComfyUIBackend/ExtraNodes/SwarmComfyExtra ../SwarmComfyExtra
cd ..
rm -rf SwarmUI

echo "SwarmUI ExtraNodes installed"

cd ..

echo "Installing ComfyUI requirements..."

uv pip install -r requirements.txt
uv pip install -r /workspace/runpod-ggs/setup/comfy/requirements.txt

pip uninstall xformers -y

uv pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.3+torch2.9.1.cuda13.1-cp310-cp310-linux_x86_64.whl
uv pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.34+41531cee.d20260109-cp39-abi3-linux_x86_64.whl
uv pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0+torch2.9.1.cuda13.1-cp39-abi3-linux_x86_64.whl
uv pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

uv pip install deepspeed

apt update
apt install -y psmisc

# Setup folder structure (models, outputs, inputs, workflows -> /workspace with symlinks)
echo "Setting up folder structure..."
/workspace/runpod-ggs/setup/comfy/symlinks.sh

echo "ComfyUI installation complete"
