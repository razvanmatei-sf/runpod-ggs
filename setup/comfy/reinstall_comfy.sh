#!/bin/bash

# ComfyUI Reinstall Script - Backs up data and reinstalls
set -e

# Start timer
START_TIME=$(date +%s)

echo "========================================================"
echo "ComfyUI Reinstall (with backup)"
echo "========================================================"

cd /workspace

# Create backup directory with timestamp
BACKUP_DIR="/workspace/backup/comfy-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup output folder if it exists
if [ -d "/workspace/ComfyUI/output" ]; then
    echo "Backing up output folder..."
    cp -r /workspace/ComfyUI/output "$BACKUP_DIR/output"
    echo "Output backed up to: $BACKUP_DIR/output"
fi

# Backup input folder if it exists
if [ -d "/workspace/ComfyUI/input" ]; then
    echo "Backing up input folder..."
    cp -r /workspace/ComfyUI/input "$BACKUP_DIR/input"
    echo "Input backed up to: $BACKUP_DIR/input"
fi

# Delete the current ComfyUI folder
echo "Removing existing ComfyUI installation..."
rm -rf /workspace/ComfyUI

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Run the install script
echo "Running fresh installation..."
if [ -f "$REPO_DIR/setup/comfy/install_comfy.sh" ]; then
    bash "$REPO_DIR/setup/comfy/install_comfy.sh"
else
    echo "ERROR: Install script not found at $REPO_DIR/setup/comfy/install_comfy.sh"
    exit 1
fi

# Restore backups
echo "Restoring backed up data..."

if [ -d "$BACKUP_DIR/output" ]; then
    echo "Restoring output folder..."
    mkdir -p /workspace/ComfyUI/output
    cp -r "$BACKUP_DIR/output/"* /workspace/ComfyUI/output/
    echo "Output restored"
fi

if [ -d "$BACKUP_DIR/input" ]; then
    echo "Restoring input folder..."
    mkdir -p /workspace/ComfyUI/input
    cp -r "$BACKUP_DIR/input/"* /workspace/ComfyUI/input/
    echo "Input restored"
fi

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Reinstall complete!"
echo "Backups saved in: $BACKUP_DIR"
echo "========================================================"
echo "⏱️  Total reinstall time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
