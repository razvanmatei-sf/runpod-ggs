#!/bin/bash
# ABOUTME: Reinstalls ComfyUI from scratch while preserving user data.
# ABOUTME: Models, outputs, inputs, and workflows are preserved via symlinks in /workspace.

set -e

echo "Reinstalling ComfyUI..."

cd /workspace

# With the new symlink structure, models/outputs/inputs/workflows
# are stored in /workspace/ and won't be deleted with ComfyUI
rm -rf ComfyUI

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/comfy/install_comfy.sh"

echo "ComfyUI reinstall complete"
