#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Build and start the UI
echo "Building and starting AI-Toolkit UI on port 8675..."
npm run build_and_start
