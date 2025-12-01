#!/bin/bash
set -e

# Ensure PATH includes UV and other tools
export PATH="/root/.cargo/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

echo "Installing AI-Toolkit with CUDA 12.8 support for RTX 50-series..."

# Check if UV is installed, install if not
if ! command -v uv &> /dev/null && [ ! -f "/root/.cargo/bin/uv" ]; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="/root/.cargo/bin:$PATH"
fi

# Determine UV path
if [ -f "/root/.cargo/bin/uv" ]; then
    UV_CMD="/root/.cargo/bin/uv"
elif command -v uv &> /dev/null; then
    UV_CMD="uv"
else
    echo "ERROR: UV installation failed"
    exit 1
fi

echo "Using UV at: $UV_CMD"

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
$UV_CMD venv venv

# Install PyTorch nightly with CUDA 12.8 support using UV (required for RTX 50-series)
echo "Installing PyTorch nightly with CUDA 12.8 using UV (10-100x faster)..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install requirements with UV
echo "Installing AI-Toolkit requirements with UV..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir -r requirements.txt

# Reinstall PyTorch to ensure correct version (force)
echo "Ensuring PyTorch nightly with CUDA 12.8..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --force-reinstall

# Install specific setuptools version for compatibility
echo "Installing setuptools 69.5.1..."
$UV_CMD pip install --python venv/bin/python --no-cache-dir setuptools==69.5.1

# Build UI
echo "Building AI-Toolkit UI..."
cd ui

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Build the UI
echo "Building UI assets..."
npm run build

# Update database
echo "Updating database..."
npm run update_db

cd /workspace/ai-toolkit

echo "AI-Toolkit installation complete!"
echo "PyTorch nightly with CUDA 12.8 installed (RTX 50-series compatible)"
echo "UI built and ready to use"
