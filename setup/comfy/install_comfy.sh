#!/bin/bash

# ComfyUI Installation Script for RunPod
set -e

# Start timer
START_TIME=$(date +%s)

# Ensure PATH includes UV and other tools
export PATH="/root/.cargo/bin:$PATH"
export PATH="/root/.local/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

# Suppress UV hardlink warning (can't use hardlinks across filesystems)
export UV_LINK_MODE=copy

echo "========================================================"
echo "ComfyUI Installation"
echo "========================================================"

# Check if UV is installed, install if not
if ! command -v uv &> /dev/null && [ ! -f "/root/.cargo/bin/uv" ] && [ ! -f "/root/.local/bin/uv" ]; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="/root/.local/bin:$PATH"
    export PATH="/root/.cargo/bin:$PATH"
fi

# Determine UV path
if [ -f "/root/.cargo/bin/uv" ]; then
    UV_CMD="/root/.cargo/bin/uv"
elif [ -f "/root/.local/bin/uv" ]; then
    UV_CMD="/root/.local/bin/uv"
elif command -v uv &> /dev/null; then
    UV_CMD="uv"
else
    echo "ERROR: UV installation failed"
    exit 1
fi

echo "Using UV at: $UV_CMD"

# Define absolute paths
COMFY_DIR="/workspace/ComfyUI"
VENV_PYTHON="$COMFY_DIR/venv/bin/python"
CUSTOM_NODES_DIR="$COMFY_DIR/custom_nodes"

cd /workspace

# Remove existing ComfyUI if present (fresh install)
if [ -d "$COMFY_DIR" ]; then
    echo "Removing existing ComfyUI installation..."
    rm -rf "$COMFY_DIR"
fi

echo "Cloning ComfyUI..."
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI

cd "$COMFY_DIR"

echo "Creating virtual environment with UV..."
$UV_CMD venv venv

echo "Installing PyTorch with UV (10-100x faster than pip)..."
$UV_CMD pip install --python "$VENV_PYTHON" torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129

# Create custom_nodes directory
mkdir -p "$CUSTOM_NODES_DIR"
cd "$CUSTOM_NODES_DIR"

# ComfyUI-Manager
echo "Installing ComfyUI-Manager..."
if [ -d "ComfyUI-Manager" ]; then
    rm -rf ComfyUI-Manager
fi
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager
if [ -f "ComfyUI-Manager/requirements.txt" ]; then
    $UV_CMD pip install --python "$VENV_PYTHON" -r ComfyUI-Manager/requirements.txt
fi

# RES4LYF
echo "Installing RES4LYF..."
if [ -d "RES4LYF" ]; then
    rm -rf RES4LYF
fi
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF
if [ -f "RES4LYF/requirements.txt" ]; then
    $UV_CMD pip install --python "$VENV_PYTHON" -r RES4LYF/requirements.txt
fi

cd "$COMFY_DIR"

echo "Installing ComfyUI requirements..."
$UV_CMD pip install --python "$VENV_PYTHON" -r requirements.txt

# Remove default xformers if installed
$UV_CMD pip uninstall --python "$VENV_PYTHON" xformers --yes || true

echo "Installing optimized wheels with UV..."
$UV_CMD pip install --python "$VENV_PYTHON" https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl
$UV_CMD pip install --python "$VENV_PYTHON" https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl
$UV_CMD pip install --python "$VENV_PYTHON" https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl
$UV_CMD pip install --python "$VENV_PYTHON" https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

echo "Installing shared requirements..."
$UV_CMD pip install --python "$VENV_PYTHON" -r /workspace/runpod-ggs/setup/comfy/requirements.txt

# Install psmisc for fuser command
apt-get update
apt-get install -y psmisc

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "ComfyUI Installation complete!"
echo "========================================================"
echo "⏱️  Total installation time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
