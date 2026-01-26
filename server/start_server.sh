#!/bin/bash

# ComfyStudio Startup Script

echo "=========================================="
echo "Starting ComfyStudio"
echo "=========================================="

# Setup SSH for GitHub (copy keys from persistent storage)
mkdir -p ~/.ssh
if [ -d "/workspace/.ssh" ]; then
    cp -r /workspace/.ssh/* ~/.ssh/ 2>/dev/null || true
    chmod 600 ~/.ssh/id_* 2>/dev/null || true
fi
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 2>/dev/null

# Configuration
WORKSPACE_DIR="/workspace"
REPO_URL="https://github.com/razvanmatei-sf/runpod-ggs.git"
REPO_DIR="$WORKSPACE_DIR/runpod-ggs"
COMFYUI_DIR="$WORKSPACE_DIR/ComfyUI"

# Branch to use for setup scripts
BRANCH="feature/upgrade-setup-scripts"

# Clone or update the repository
echo "Syncing repository..."
if [ -d "$REPO_DIR/.git" ]; then
    echo "Repository exists, pulling latest changes..."
    cd "$REPO_DIR"
    git fetch --all || echo "Warning: git fetch failed"
    git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" "origin/$BRANCH" || echo "Warning: checkout failed"
    git reset --hard "origin/$BRANCH" || echo "Warning: reset failed"
    git pull origin "$BRANCH" || echo "Warning: pull failed"
    echo "Repository updated."
else
    echo "Cloning repository..."
    rm -rf "$REPO_DIR"
    if ! git clone -b "$BRANCH" "$REPO_URL" "$REPO_DIR"; then
        echo "Warning: Clone failed, trying main branch..."
        git clone "$REPO_URL" "$REPO_DIR" || echo "Warning: Clone of main also failed"
    fi
    echo "Repository cloned."
fi

# Make all scripts executable
echo "Setting script permissions..."
find "$REPO_DIR/setup" -name "*.sh" -exec chmod +x {} \;
chmod +x "$REPO_DIR/server/start_server.sh" 2>/dev/null || true
chmod +x "$REPO_DIR/server/build_server.sh" 2>/dev/null || true

# Verify network volume is mounted and ComfyUI is installed
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "WARNING: ComfyUI not found at $COMFYUI_DIR"
    echo "Some features may not be available until ComfyUI is installed"
fi

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
fuser -k 8080/tcp 2>/dev/null || true
fuser -k 8888/tcp 2>/dev/null || true
fuser -k 8188/tcp 2>/dev/null || true
sleep 2

# Set working directory
cd "$WORKSPACE_DIR"

echo ""
echo "=========================================="
echo "Repository synced to: $REPO_DIR"
echo "=========================================="
echo ""
echo "Available services:"
echo "  ComfyStudio: http://localhost:8080"
echo "  ComfyUI:     http://localhost:8188"
echo "  JupyterLab:  http://localhost:8888"
echo ""

# Export repo path for the server to use
export REPO_DIR="$REPO_DIR"

echo "Starting Python server..."
echo "Python version: $(python3 --version)"
echo "Server script exists: $(ls -la /usr/local/bin/server.py 2>&1)"

# Start the server from Docker image (runs in foreground)
# This ensures the new UI is used regardless of repo state
exec python3 /usr/local/bin/server.py
