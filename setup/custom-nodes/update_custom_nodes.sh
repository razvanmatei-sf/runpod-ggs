#!/bin/bash

# ComfyUI Custom Nodes Update Script
set -e

echo "Updating ComfyUI Custom Nodes"

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
NODES_CONFIG="$REPO_DIR/setup/custom-nodes/nodes.txt"
CUSTOM_NODES_DIR="/workspace/ComfyUI/custom_nodes"

if [ ! -d "/workspace/ComfyUI" ]; then
    echo "ERROR: ComfyUI is not installed"
    exit 1
fi

source /workspace/ComfyUI/venv/bin/activate

while read -r repo_url || [ -n "$repo_url" ]; do
    [[ "$repo_url" =~ ^#.*$ ]] || [ -z "$repo_url" ] && continue

    repo_name=$(basename "$repo_url" .git)
    node_path="$CUSTOM_NODES_DIR/$repo_name"

    if [ ! -d "$node_path" ]; then
        echo "Skipping $repo_name (not installed)"
        continue
    fi

    echo "Updating $repo_name..."
    cd "$node_path"
    git stash
    git pull --force

    [ -f "requirements.txt" ] && pip install -r requirements.txt
    [ -f "install.py" ] && python install.py
    [ -f "install.sh" ] && bash install.sh

done < "$NODES_CONFIG"

echo "Custom nodes update complete"
