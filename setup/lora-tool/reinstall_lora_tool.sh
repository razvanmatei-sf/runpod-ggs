#!/bin/bash

# LoRA-Tool Reinstall Script - Backs up data and reinstalls
set -e

echo "========================================================"
echo "LoRA-Tool Reinstall (with backup)"
echo "========================================================"

cd /workspace

# Create backup directory with timestamp
BACKUP_DIR="/workspace/backup/lora-tool-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup any important data if needed
if [ -d "/workspace/lora-tool" ]; then
    echo "Backing up LoRA-Tool data..."

    # Backup any generated datasets or outputs if they exist
    if [ -d "/workspace/lora-tool/datasets" ]; then
        cp -r /workspace/lora-tool/datasets "$BACKUP_DIR/datasets"
        echo "Datasets backed up to: $BACKUP_DIR/datasets"
    fi

    # Backup any user files if they exist
    if [ -d "/workspace/lora-tool/output" ]; then
        cp -r /workspace/lora-tool/output "$BACKUP_DIR/output"
        echo "Output backed up to: $BACKUP_DIR/output"
    fi
fi

# Delete the current LoRA-Tool folder
echo "Removing existing LoRA-Tool installation..."
rm -rf /workspace/lora-tool

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Run the install script
echo "Running fresh installation..."
if [ -f "$REPO_DIR/setup/lora-tool/install_lora_tool.sh" ]; then
    bash "$REPO_DIR/setup/lora-tool/install_lora_tool.sh"
else
    echo "ERROR: Install script not found at $REPO_DIR/setup/lora-tool/install_lora_tool.sh"
    exit 1
fi

# Restore backups if they exist
echo "Restoring backed up data..."

if [ -d "$BACKUP_DIR/datasets" ]; then
    echo "Restoring datasets..."
    mkdir -p /workspace/lora-tool/datasets
    cp -r "$BACKUP_DIR/datasets/"* /workspace/lora-tool/datasets/
    echo "Datasets restored"
fi

if [ -d "$BACKUP_DIR/output" ]; then
    echo "Restoring output..."
    mkdir -p /workspace/lora-tool/output
    cp -r "$BACKUP_DIR/output/"* /workspace/lora-tool/output/
    echo "Output restored"
fi

echo "========================================================"
echo "Reinstall complete!"
echo "Backups saved in: $BACKUP_DIR"
echo "========================================================"
