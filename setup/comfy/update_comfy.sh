#!/bin/bash

# ComfyUI Update Script - Updates code and dependencies
set -e

echo "========================================================"
echo "ComfyUI Update"
echo "========================================================"

cd /workspace/ComfyUI

echo "Updating ComfyUI repository..."
git stash
git pull --force

echo "Activating virtual environment..."
source venv/bin/activate

echo "Updating Python dependencies..."
pip install -r requirements.txt

echo "========================================================"
echo "Update complete!"
echo "========================================================"
