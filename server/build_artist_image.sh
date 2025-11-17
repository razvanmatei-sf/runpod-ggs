#!/bin/bash

# Build script for Artist ComfyUI Docker Image

set -e

echo "=========================================="
echo "🐳 Building Artist ComfyUI Docker Image"
echo "=========================================="

# Configuration
IMAGE_NAME="runpod-nanobit"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"
REGISTRY_NAME="ghcr.io/razvanmatei-sf/runpod-nanobit:latest"

# Check if required files exist
if [ ! -f "Dockerfile" ]; then
    echo "❌ ERROR: Dockerfile not found in current directory"
    exit 1
fi

if [ ! -f "start_artist_session.sh" ]; then
    echo "❌ ERROR: start_artist_session.sh not found in current directory"
    exit 1
fi

if [ ! -f "artist_name_server.py" ]; then
    echo "❌ ERROR: artist_name_server.py not found in current directory"
    exit 1
fi

echo "📁 Building from current directory: $(pwd)"
echo "🏷️  Local image: $FULL_IMAGE_NAME"
echo "🏷️  Registry image: $REGISTRY_NAME"
echo ""
echo "📌 Base image: runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04"

# Build the Docker image
echo "🔨 Building Docker image for linux/amd64 platform..."
docker buildx build --platform linux/amd64 --load -t "$FULL_IMAGE_NAME" .

# Tag for registry
echo "🏷️  Tagging image for registry..."
docker tag "$FULL_IMAGE_NAME" "$REGISTRY_NAME"

# Login to GitHub Container Registry
echo "🔑 Logging into GitHub Container Registry..."
echo $(gh auth token) | docker login ghcr.io -u razvanmatei-sf --password-stdin

# Push to registry
echo "📤 Pushing to GitHub Container Registry..."
docker push "$REGISTRY_NAME"

echo ""
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
echo ""
echo "🐳 Images built:"
echo "   Local: $FULL_IMAGE_NAME"
echo "   Registry: $REGISTRY_NAME"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Test locally:"
echo "   docker run -it --rm \\"
echo "     -p 8080:8080 -p 8888:8888 -p 8188:8188 \\"
echo "     -v /path/to/network/volume:/workspace \\"
echo "     $REGISTRY_NAME"
echo ""
echo "2. Use in RunPod Template:"
echo "   Image: $REGISTRY_NAME"
echo "   Base: PyTorch 2.2.0, Python 3.10, CUDA 12.1.1"
echo "   Network Volume: /workspace"
echo "   Ports: 8080 (Artist Login), 8888 (Jupyter), 8188 (ComfyUI)"
echo ""
echo "3. Artist Access:"
echo "   Connect to port 8080 → Enter name → Start creating!"
echo ""
echo "=========================================="