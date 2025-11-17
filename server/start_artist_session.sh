#!/bin/bash

# Artist Session Startup Script
# This script starts the artist name selection server

set -e

echo "=========================================="
echo "🎨 Starting Artist Session Manager"
echo "=========================================="

# Network volume paths (these should be mounted)
WORKSPACE_DIR="/workspace"
COMFYUI_DIR="$WORKSPACE_DIR/ComfyUI"
VENV_DIR="$WORKSPACE_DIR/venv"
STARTUP_SCRIPT="$WORKSPACE_DIR/start_comfyui.sh"

# Verify network volume is mounted and ComfyUI is installed
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "❌ ERROR: ComfyUI not found at $COMFYUI_DIR"
    echo "Please ensure the network volume is properly mounted"
    exit 1
fi

if [ ! -f "$STARTUP_SCRIPT" ]; then
    echo "❌ ERROR: ComfyUI startup script not found at $STARTUP_SCRIPT"
    echo "Please ensure ComfyUI installation is complete"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ ERROR: Virtual environment not found at $VENV_DIR"
    echo "Please ensure ComfyUI installation is complete"
    exit 1
fi

# Kill any existing processes on our ports
echo "🔄 Cleaning up existing processes..."
fuser -k 8080/tcp 2>/dev/null || true
fuser -k 8888/tcp 2>/dev/null || true
fuser -k 8188/tcp 2>/dev/null || true
sleep 2

# Set working directory
cd "$WORKSPACE_DIR"

echo "🌐 Starting Artist Name Selection Server on port 8080..."
echo "📋 Artists can access: http://localhost:8080"
echo "🎨 ComfyUI will be available on: http://localhost:8188"
echo "📚 Jupyter Lab will be available on: http://localhost:8888"
echo ""
echo "Waiting for artist to select their name..."

# Start the artist name selection server (runs in foreground)
exec python3 /usr/local/bin/artist_name_server.py