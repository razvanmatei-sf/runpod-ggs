#!/bin/bash

# AI-Toolkit Update Script - Updates code and dependencies
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
echo "AI-Toolkit Update with CUDA 12.8.1 support"
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

cd /workspace/ai-toolkit

echo "Updating AI-Toolkit repository..."
git stash
git pull --force

echo "Updating PyTorch nightly with CUDA 12.8 using UV..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force-reinstall

echo "Updating Python dependencies with UV..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir -r requirements.txt

echo "Ensuring setuptools 69.5.1..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir setuptools==69.5.1

echo "Updating UI dependencies..."
cd ui
npm install

echo "Rebuilding UI assets..."
npm run build

echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Update complete!"
echo "PyTorch with CUDA 12.8.1 support updated"
echo "UI rebuilt and database updated"
echo "========================================================"
echo "⏱️  Total update time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
