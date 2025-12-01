#!/bin/bash

# AI-Toolkit Update Script
set -e

echo "========================================================"
echo "AI-Toolkit Update"
echo "========================================================"

cd /workspace/ai-toolkit

# Activate venv
source venv/bin/activate

echo "Updating AI-Toolkit repository..."
git stash
git pull --force

echo "Updating PyTorch nightly with CUDA 12.8..."
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo "Updating Python dependencies..."
pip install -r requirements.txt

echo "Installing setuptools..."
pip install setuptools==69.5.1

echo "Updating UI dependencies..."
cd ui
npm install

echo "Rebuilding UI assets..."
npm run build

echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo ""
echo "========================================================"
echo "AI-Toolkit Update complete!"
echo "========================================================"
