#!/bin/bash

# AI-Toolkit Installation Script
# Base image: runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
# Python 3.12, PyTorch 2.8.0, CUDA 12.8.1

set -e

echo "========================================================"
echo "AI-Toolkit Installation (Python 3.12 + CUDA 12.8)"
echo "========================================================"

cd /workspace

# Remove existing installation if present
if [ -d "ai-toolkit" ]; then
    echo "Removing existing AI-Toolkit installation..."
    rm -rf ai-toolkit
fi

echo "Cloning AI-Toolkit..."
git clone https://github.com/ostris/ai-toolkit.git

cd /workspace/ai-toolkit

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

echo "Installing AI-Toolkit requirements..."
pip install -r requirements.txt

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
