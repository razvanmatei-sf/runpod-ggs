#!/bin/bash

# AI-Toolkit Reinstall Script - Clean reinstall
set -e

echo "========================================================"
echo "AI-Toolkit Reinstall"
echo "========================================================"

cd /workspace

# Delete the current AI-Toolkit folder
if [ -d "ai-toolkit" ]; then
    echo "Removing existing AI-Toolkit installation..."
    rm -rf ai-toolkit
fi

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Run the install script
echo "Running fresh installation..."
if [ -f "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh" ]; then
    bash "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"
else
    echo "ERROR: Install script not found at $REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"
    exit 1
fi

echo ""
echo "========================================================"
echo "AI-Toolkit Reinstall complete!"
echo "========================================================"
