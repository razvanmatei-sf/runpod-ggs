#!/bin/bash
set -e

echo "Building ComfyStudio Docker Image"

IMAGE_NAME="runpod-ggs:latest"
REGISTRY_NAME="ghcr.io/razvanmatei-sf/runpod-ggs:latest"

docker buildx build --platform linux/amd64 --load -t "$IMAGE_NAME" .
docker tag "$IMAGE_NAME" "$REGISTRY_NAME"

echo $(gh auth token) | docker login ghcr.io -u razvanmatei-sf --password-stdin
docker push "$REGISTRY_NAME"

echo "Build complete"
