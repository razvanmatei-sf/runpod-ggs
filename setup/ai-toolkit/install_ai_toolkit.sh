#!/bin/bash
set -e

echo "Installing AI-Toolkit (following official installation method)..."

cd /workspace

# Clone the repository
if [ -d "ai-toolkit" ]; then
    echo "AI-Toolkit directory already exists, removing..."
    rm -rf ai-toolkit
fi

git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit

# Create virtual environment with standard Python venv
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install PyTorch first (official method - CUDA 12.6 stable, has all wheels)
echo "Installing PyTorch 2.7.0 with CUDA 12.6..."
pip3 install --no-cache-dir torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126

# Install requirements (uses pre-built wheels, much faster)
echo "Installing AI-Toolkit requirements..."
pip3 install --no-cache-dir -r requirements.txt

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
echo "PyTorch 2.7.0 with CUDA 12.6 installed"
echo "UI built and ready to use"
