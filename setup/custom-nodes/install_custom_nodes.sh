#!/bin/bash

# ComfyUI Custom Nodes Install Script
set -e

echo "Installing ComfyUI Custom Nodes"

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
NODES_CONFIG="$REPO_DIR/setup/custom-nodes/nodes.txt"
CUSTOM_NODES_DIR="/workspace/ComfyUI/custom_nodes"

if [ ! -d "/workspace/ComfyUI" ]; then
    echo "ERROR: ComfyUI is not installed"
    exit 1
fi

source /workspace/ComfyUI/venv/bin/activate
mkdir -p "$CUSTOM_NODES_DIR"
cd "$CUSTOM_NODES_DIR"

while read -r repo_url || [ -n "$repo_url" ]; do
    [[ "$repo_url" =~ ^#.*$ ]] || [ -z "$repo_url" ] && continue

    repo_name=$(basename "$repo_url" .git)
    node_path="$CUSTOM_NODES_DIR/$repo_name"

    if [ -d "$node_path" ]; then
        echo "Skipping $repo_name (exists)"
        continue
    fi

    echo "Installing $repo_name..."
    git clone "$repo_url"

    cd "$node_path"
    [ -f "requirements.txt" ] && pip install -r requirements.txt
    [ -f "install.py" ] && python install.py
    [ -f "install.sh" ] && bash install.sh
    cd "$CUSTOM_NODES_DIR"

done < "$NODES_CONFIG"

echo "Custom nodes installation complete"
