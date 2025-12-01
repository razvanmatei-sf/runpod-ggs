#!/bin/bash

# AI-Toolkit Update Script - Updates code and dependencies
set -e

# Suppress UV hardlink warning (can't use hardlinks across filesystems)
export UV_LINK_MODE=copy

echo "========================================================"
echo "AI-Toolkit Update with CUDA 12.8.1 support"
echo "========================================================"

cd /workspace/ai-toolkit

echo "Updating AI-Toolkit repository..."
git stash
git pull --force

echo "Updating PyTorch nightly with CUDA 12.8 using UV..."
uv pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force

echo "Updating Python dependencies with UV..."
uv pip install --python venv/bin/python --no-cache-dir -r requirements.txt

echo "Ensuring setuptools 69.5.1..."
uv pip install --python venv/bin/python --no-cache-dir setuptools==69.5.1

echo "Updating UI dependencies..."
cd ui
npm install

echo "Rebuilding UI assets..."
npm run build

echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo "========================================================"
echo "Update complete!"
echo "PyTorch with CUDA 12.8.1 support updated"
echo "UI rebuilt and database updated"
echo "========================================================"
