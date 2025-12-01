#!/bin/bash
set -e

echo "Installing AI-Toolkit with CUDA 12.8.1 support..."

cd /workspace

# Clone the repository
if [ -d "ai-toolkit" ]; then
    echo "AI-Toolkit directory already exists, removing..."
    rm -rf ai-toolkit
fi

git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit

# Create virtual environment with UV
echo "Creating virtual environment with UV..."
uv venv venv

# Install PyTorch nightly with CUDA 12.8 support using UV (no activation needed)
echo "Installing PyTorch nightly with CUDA 12.8 using UV (10-100x faster)..."
uv pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install requirements with UV
echo "Installing AI-Toolkit requirements with UV..."
uv pip install --python venv/bin/python --no-cache-dir -r requirements.txt

# Reinstall PyTorch to ensure correct version (force)
echo "Ensuring PyTorch nightly with CUDA 12.8..."
uv pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force

# Install specific setuptools version for compatibility
echo "Installing setuptools 69.5.1..."
uv pip install --python venv/bin/python --no-cache-dir setuptools==69.5.1

# Build UI
echo "Building AI-Toolkit UI..."
cd ui

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the UI
echo "Building UI assets..."
npm run build

# Update database
echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo "AI-Toolkit installation complete!"
echo "PyTorch with CUDA 12.8.1 support installed"
echo "UI built and ready to use"
