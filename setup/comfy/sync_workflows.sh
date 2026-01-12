#!/bin/bash
# ABOUTME: Syncs workflows from GitHub workflows branch to ComfyUI
# ABOUTME: GitHub files overwrite local, but local-only workflows are kept

set -e

REPO_URL="git@github.com:razvanmatei-sf/runpod-ggs.git"
BRANCH="workflows"
WORKFLOWS_DIR="/workspace/ComfyUI/user/default/workflows"
TEMP_DIR="/tmp/workflows-sync"

echo "[Workflow Sync] Starting sync from GitHub..."

# Setup SSH keys from persistent storage (for private repo access)
mkdir -p ~/.ssh
if [ -d "/workspace/.ssh" ]; then
    cp -r /workspace/.ssh/* ~/.ssh/ 2>/dev/null || true
    chmod 600 ~/.ssh/id_* 2>/dev/null || true
fi
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 2>/dev/null

# Ensure workflows directory exists
mkdir -p "$WORKFLOWS_DIR"

# Clean temp directory
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Clone only the workflows branch (shallow clone for speed)
git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TEMP_DIR" 2>/dev/null

# Copy workflow files (overwrites existing, keeps local-only)
cd "$TEMP_DIR"
for file in *.json; do
    if [ -f "$file" ]; then
        cp "$file" "$WORKFLOWS_DIR/"
        echo "[Workflow Sync] Synced: $file"
    fi
done

# Cleanup
rm -rf "$TEMP_DIR"

echo "[Workflow Sync] Complete!"
