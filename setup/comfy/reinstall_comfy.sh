#!/bin/bash
set -e

echo "Reinstalling ComfyUI"

cd /workspace

BACKUP_DIR="/workspace/backup/comfy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

[ -d "ComfyUI/output" ] && cp -r ComfyUI/output "$BACKUP_DIR/"
[ -d "ComfyUI/input" ] && cp -r ComfyUI/input "$BACKUP_DIR/"

rm -rf ComfyUI

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/comfy/install_comfy.sh"

[ -d "$BACKUP_DIR/output" ] && cp -r "$BACKUP_DIR/output/"* /workspace/ComfyUI/output/
[ -d "$BACKUP_DIR/input" ] && cp -r "$BACKUP_DIR/input/"* /workspace/ComfyUI/input/

echo "ComfyUI Reinstall complete"
