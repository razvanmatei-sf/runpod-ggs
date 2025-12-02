#!/bin/bash

# AI-Toolkit Installation Script
set -e

echo "========================================================"
echo "AI-Toolkit Installation"
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

echo "Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing PyTorch nightly with CUDA 12.8..."
pip install --pre --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo "Installing AI-Toolkit requirements..."
pip install --no-cache-dir -r requirements.txt

# Build UI
echo "Building AI-Toolkit UI..."
cd ui

echo "Installing Node.js dependencies..."
npm install

echo "Building UI assets..."
npm run build

echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo ""
echo "========================================================"
echo "AI-Toolkit Installation complete!"
echo "========================================================"
