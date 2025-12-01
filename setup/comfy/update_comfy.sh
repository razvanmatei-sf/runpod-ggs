#!/bin/bash

# ComfyUI Update Script - Updates code and dependencies
set -e

# Start timer
START_TIME=$(date +%s)

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

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Update complete!"
echo "========================================================"
echo "⏱️  Total update time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
