#!/bin/bash

# ComfyStudio Startup Script

set -e

echo "=========================================="
echo "Starting ComfyStudio"
echo "=========================================="

# Network volume paths (these should be mounted)
WORKSPACE_DIR="/workspace"
COMFYUI_DIR="$WORKSPACE_DIR/ComfyUI"
VENV_DIR="$COMFYUI_DIR/venv"

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

echo "Starting ComfyStudio server on port 8080..."
echo ""
echo "Available services:"
echo "  ComfyStudio: http://localhost:8080"
echo "  ComfyUI:     http://localhost:8188"
echo "  JupyterLab:  http://localhost:8888"
echo ""

# Start the server (runs in foreground)
exec python3 /usr/local/bin/server.py
