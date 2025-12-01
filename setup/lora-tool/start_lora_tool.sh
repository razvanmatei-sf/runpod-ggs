#!/bin/bash
set -e

echo "Starting LoRA-Tool..."

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
cd "$REPO_DIR/setup/lora-tool"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the Vite dev server on port 3000
echo "Launching LoRA-Tool on port 3000..."
npm run dev
