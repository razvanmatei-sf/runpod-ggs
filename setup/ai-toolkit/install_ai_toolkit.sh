#!/bin/bash
set -e

echo "Installing AI-Toolkit..."

cd /workspace

# Clone the repository
if [ -d "ai-toolkit" ]; then
    echo "AI-Toolkit directory already exists, removing..."
    rm -rf ai-toolkit
fi

git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install PyTorch with CUDA 12.6 support
echo "Installing PyTorch 2.7.0 with CUDA 12.6..."
pip3 install --no-cache-dir torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126

# Install requirements
echo "Installing AI-Toolkit requirements..."
pip3 install -r requirements.txt

echo "AI-Toolkit installation complete!"
