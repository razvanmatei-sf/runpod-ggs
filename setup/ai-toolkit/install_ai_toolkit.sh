#!/bin/bash
# ABOUTME: Installs AI-Toolkit with PyTorch nightly (CUDA 12.8) and builds the UI.
# ABOUTME: Uses uv for fast package installation.

set -e

export UV_SKIP_WHEEL_FILENAME_CHECK=1
export UV_LINK_MODE=copy

echo "Installing AI-Toolkit..."

cd /workspace

rm -rf ai-toolkit
git clone --depth 1 https://github.com/ostris/ai-toolkit.git
cd /workspace/ai-toolkit

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

uv pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

uv pip install -r requirements.txt

cd ui
npm install
npm run build
npm run update_db

echo "AI-Toolkit installation complete"
