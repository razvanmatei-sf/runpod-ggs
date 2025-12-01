#!/bin/bash

# AI-Toolkit Installation Script
set -e

echo "========================================================"
echo "AI-Toolkit Installation (CUDA 12.8 for RTX 50-series)"
echo "========================================================"

# Install system dependencies (from AI-Toolkit Dockerfile)
echo "Installing system dependencies..."
apt-get update
apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    wget \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    ffmpeg \
    tmux \
    htop \
    nvtop \
    python3-opencv \
    openssh-client \
    openssh-server \
    openssl \
    rsync \
    unzip \
    libgl1

cd /workspace

# Remove existing installation if present
if [ -d "ai-toolkit" ]; then
    echo "Removing existing AI-Toolkit installation..."
    rm -rf ai-toolkit
fi

echo "Cloning AI-Toolkit..."
git clone https://github.com/ostris/ai-toolkit.git

cd /workspace/ai-toolkit

echo "Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing PyTorch nightly with CUDA 12.8..."
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo "Installing AI-Toolkit requirements..."
pip install -r requirements.txt

echo "Reinstalling PyTorch nightly (ensuring correct version)..."
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force-reinstall

echo "Installing setuptools..."
pip install setuptools==69.5.1

# Build UI
echo "Building AI-Toolkit UI..."
cd ui

echo "Installing Node.js dependencies..."
npm install

echo "Generating Prisma client..."
npx prisma generate

echo "Building UI assets..."
npm run build

echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo ""
echo "========================================================"
echo "AI-Toolkit Installation complete!"
echo "========================================================"
