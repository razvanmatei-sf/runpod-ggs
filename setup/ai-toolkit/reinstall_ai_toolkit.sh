#!/bin/bash

# AI-Toolkit Reinstall Script - Backs up data and reinstalls
set -e

echo "========================================================"
echo "AI-Toolkit Reinstall (with backup)"
echo "========================================================"

cd /workspace

# Create backup directory with timestamp
BACKUP_DIR="/workspace/backup/ai-toolkit-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup any important data if needed
if [ -d "/workspace/ai-toolkit" ]; then
    echo "Backing up AI-Toolkit configuration..."

    # Backup config files if they exist
    if [ -d "/workspace/ai-toolkit/config" ]; then
        cp -r /workspace/ai-toolkit/config "$BACKUP_DIR/config"
        echo "Config backed up to: $BACKUP_DIR/config"
    fi

    # Backup any trained models or outputs if they exist
    if [ -d "/workspace/ai-toolkit/output" ]; then
        cp -r /workspace/ai-toolkit/output "$BACKUP_DIR/output"
        echo "Output backed up to: $BACKUP_DIR/output"
    fi
fi

# Delete the current AI-Toolkit folder
echo "Removing existing AI-Toolkit installation..."
rm -rf /workspace/ai-toolkit

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Run the install script
echo "Running fresh installation..."
if [ -f "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh" ]; then
    bash "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"
else
    echo "ERROR: Install script not found at $REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"
    exit 1
fi

# Restore backups if they exist
echo "Restoring backed up data..."

if [ -d "$BACKUP_DIR/config" ]; then
    echo "Restoring config..."
    mkdir -p /workspace/ai-toolkit/config
    cp -r "$BACKUP_DIR/config/"* /workspace/ai-toolkit/config/
    echo "Config restored"
fi

if [ -d "$BACKUP_DIR/output" ]; then
    echo "Restoring output..."
    mkdir -p /workspace/ai-toolkit/output
    cp -r "$BACKUP_DIR/output/"* /workspace/ai-toolkit/output/
    echo "Output restored"
fi

echo ""
echo "========================================================"
echo "AI-Toolkit Reinstall complete!"
echo "Backups saved in: $BACKUP_DIR"
echo "========================================================"
