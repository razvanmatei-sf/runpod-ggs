#!/bin/bash

# ComfyUI Update Script - Updates code and dependencies
set -e

# Suppress UV hardlink warning (can't use hardlinks across filesystems)
export UV_LINK_MODE=copy

echo "========================================================"
echo "ComfyUI Update"
echo "========================================================"

cd /workspace/ComfyUI

echo "Updating ComfyUI repository..."
git stash
git pull --force

echo "Updating Python dependencies with UV..."
uv pip install --python venv/bin/python -r requirements.txt

echo "========================================================"
echo "Update complete!"
echo "========================================================"
