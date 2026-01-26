#!/bin/bash
# ABOUTME: Updates ComfyUI to the latest version.
# ABOUTME: Pulls latest code and reinstalls requirements.

set -e

echo "Updating ComfyUI..."

cd /workspace/ComfyUI
source venv/bin/activate

git stash
git pull --force

uv pip install -r requirements.txt

echo "ComfyUI update complete"
