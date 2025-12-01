#!/bin/bash
set -e

echo "Installing LoRA-Tool..."

cd /workspace

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Copy LoRA-Tool files from repo to workspace
echo "Copying LoRA-Tool files to /workspace/lora-tool..."
if [ -d "lora-tool" ]; then
    echo "LoRA-Tool directory already exists, removing..."
    rm -rf lora-tool
fi

# Copy the entire lora-tool directory from the repo
cp -r "$REPO_DIR/setup/lora-tool" /workspace/lora-tool

cd /workspace/lora-tool

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the application
echo "Building LoRA-Tool..."
npm run build

echo "LoRA-Tool installation complete!"
echo "LoRA-Tool will be available on port 3000"
