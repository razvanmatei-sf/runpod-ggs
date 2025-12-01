#!/bin/bash

# ComfyUI Update Script
set -e

echo "========================================================"
echo "ComfyUI Update"
echo "========================================================"

cd /workspace/ComfyUI

# Activate venv
source venv/bin/activate

echo "Updating ComfyUI repository..."
git stash
git pull --force

echo "Updating Python dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================================"
echo "ComfyUI Update complete!"
echo "========================================================"
