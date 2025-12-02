#!/bin/bash

# Build script for ComfyStudio Docker Image

set -e

echo "=========================================="
echo "Building ComfyStudio Docker Image"
echo "=========================================="

# Configuration
IMAGE_NAME="runpod-ggs"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"
REGISTRY_NAME="ghcr.io/razvanmatei-sf/runpod-ggs:latest"

# Check if required files exist
if [ ! -f "Dockerfile" ]; then
    echo "ERROR: Dockerfile not found in current directory"
    exit 1
fi

if [ ! -f "start_server.sh" ]; then
    echo "ERROR: start_server.sh not found in current directory"
    exit 1
fi

if [ ! -f "server.py" ]; then
    echo "ERROR: server.py not found in current directory"
    exit 1
fi

if [ ! -f "artist_names.sh" ]; then
    echo "ERROR: artist_names.sh not found in current directory"
    exit 1
fi

echo "Building from: $(pwd)"
echo "Local image: $FULL_IMAGE_NAME"
echo "Registry image: $REGISTRY_NAME"
echo ""
echo "Base image: runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04"

# Build the Docker image
echo "Building Docker image for linux/amd64 platform..."
docker buildx build --platform linux/amd64 --load -t "$FULL_IMAGE_NAME" .

# Tag for registry
echo "Tagging image for registry..."
docker tag "$FULL_IMAGE_NAME" "$REGISTRY_NAME"

# Login to GitHub Container Registry
echo "Logging into GitHub Container Registry..."
echo $(gh auth token) | docker login ghcr.io -u razvanmatei-sf --password-stdin

# Push to registry
echo "Pushing to GitHub Container Registry..."
docker push "$REGISTRY_NAME"

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""
echo "Images built:"
echo "  Local: $FULL_IMAGE_NAME"
echo "  Registry: $REGISTRY_NAME"
echo ""
echo "Test locally:"
echo "  docker run -it --rm \\"
echo "    -p 8080:8080 -p 8888:8888 -p 8188:8188 \\"
echo "    -v /path/to/workspace:/workspace \\"
echo "    $REGISTRY_NAME"
echo ""
echo "=========================================="
