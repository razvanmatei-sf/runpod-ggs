#!/bin/bash

# SwarmUI Reinstall Script - Backs up data and reinstalls
set -e

# Start timer
START_TIME=$(date +%s)

echo "========================================================"
echo "SwarmUI Reinstall (with backup)"
echo "========================================================"

cd /workspace

# Create backup directory with timestamp
BACKUP_DIR="/workspace/backup/swarm-ui-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup any important data if needed
if [ -d "/workspace/SwarmUI" ]; then
    echo "Backing up SwarmUI data..."

    # Backup output folder if it exists
    if [ -d "/workspace/SwarmUI/Output" ]; then
        cp -r /workspace/SwarmUI/Output "$BACKUP_DIR/Output"
        echo "Output backed up to: $BACKUP_DIR/Output"
    fi

    # Backup models folder if it exists
    if [ -d "/workspace/SwarmUI/Models" ]; then
        cp -r /workspace/SwarmUI/Models "$BACKUP_DIR/Models"
        echo "Models backed up to: $BACKUP_DIR/Models"
    fi

    # Backup settings if they exist
    if [ -d "/workspace/SwarmUI/Data" ]; then
        cp -r /workspace/SwarmUI/Data "$BACKUP_DIR/Data"
        echo "Data backed up to: $BACKUP_DIR/Data"
    fi
fi

# Delete the current SwarmUI folder
echo "Removing existing SwarmUI installation..."
rm -rf /workspace/SwarmUI

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"

# Run the install script
echo "Running fresh installation..."
if [ -f "$REPO_DIR/setup/swarm-ui/install_swarm_ui.sh" ]; then
    bash "$REPO_DIR/setup/swarm-ui/install_swarm_ui.sh"
else
    echo "ERROR: Install script not found at $REPO_DIR/setup/swarm-ui/install_swarm_ui.sh"
    exit 1
fi

# Restore backups if they exist
echo "Restoring backed up data..."

if [ -d "$BACKUP_DIR/Output" ]; then
    echo "Restoring output..."
    mkdir -p /workspace/SwarmUI/Output
    cp -r "$BACKUP_DIR/Output/"* /workspace/SwarmUI/Output/
    echo "Output restored"
fi

if [ -d "$BACKUP_DIR/Models" ]; then
    echo "Restoring models..."
    mkdir -p /workspace/SwarmUI/Models
    cp -r "$BACKUP_DIR/Models/"* /workspace/SwarmUI/Models/
    echo "Models restored"
fi

if [ -d "$BACKUP_DIR/Data" ]; then
    echo "Restoring data..."
    mkdir -p /workspace/SwarmUI/Data
    cp -r "$BACKUP_DIR/Data/"* /workspace/SwarmUI/Data/
    echo "Data restored"
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
