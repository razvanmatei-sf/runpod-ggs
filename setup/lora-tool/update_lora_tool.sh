#!/bin/bash

# LoRA-Tool Update Script - Updates code and dependencies
set -e

echo "========================================================"
echo "LoRA-Tool Update"
echo "========================================================"

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

cd /workspace/lora-tool

echo "Updating LoRA-Tool files from repository..."
# Copy updated files from repo
cp -r "$REPO_DIR/setup/lora-tool/"* /workspace/lora-tool/

echo "Updating Node.js dependencies..."
npm install

echo "Rebuilding application..."
npm run build

echo "========================================================"
echo "Update complete!"
echo "========================================================"
