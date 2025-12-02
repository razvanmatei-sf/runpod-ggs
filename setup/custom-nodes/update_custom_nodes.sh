#!/bin/bash

# ComfyUI Custom Nodes Update Script
set -e

echo "========================================================"
echo "Updating ComfyUI Custom Nodes"
echo "========================================================"

# Get the repo directory from environment or use default
REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
NODES_CONFIG="$REPO_DIR/setup/custom-nodes/nodes.txt"
CUSTOM_NODES_DIR="/workspace/ComfyUI/custom_nodes"

# Check if ComfyUI is installed
if [ ! -d "/workspace/ComfyUI" ]; then
    echo "ERROR: ComfyUI is not installed. Please install ComfyUI first."
    exit 1
fi

# Check if custom_nodes directory exists
if [ ! -d "$CUSTOM_NODES_DIR" ]; then
    echo "ERROR: Custom nodes directory not found. No nodes to update."
    exit 1
fi

# Activate ComfyUI virtual environment
source /workspace/ComfyUI/venv/bin/activate

# Read nodes from config and update them
echo "Reading custom nodes from: $NODES_CONFIG"
echo ""

while read -r repo_url || [ -n "$repo_url" ]; do
    # Skip comments and empty lines
    if [[ "$repo_url" =~ ^#.*$ ]] || [ -z "$repo_url" ]; then
        continue
    fi

    # Trim whitespace
    repo_url=$(echo "$repo_url" | xargs)

    # Extract repo name from URL (last part without .git)
    repo_name=$(basename "$repo_url" .git)
    node_path="$CUSTOM_NODES_DIR/$repo_name"

    # Only update if the node is installed
    if [ ! -d "$node_path" ]; then
        echo "⊘ Skipping $repo_name (not installed)"
        continue
    fi

    echo "----------------------------------------"
    echo "Updating: $repo_name"
    echo "Path: $node_path"
    echo "----------------------------------------"

    cd "$node_path"

    # Update the repository
    echo "Pulling latest changes for $repo_name..."
    git stash
    git pull --force

    # Check for and update dependencies
    if [ -f "requirements.txt" ]; then
        echo "Updating Python requirements for $repo_name..."
        pip install -r requirements.txt
        echo "Requirements updated for $repo_name"
    elif [ -f "install.py" ]; then
        echo "Running install.py for $repo_name..."
        python install.py
        echo "Install script completed for $repo_name"
    elif [ -f "install.sh" ]; then
        echo "Running install.sh for $repo_name..."
        bash install.sh
        echo "Install script completed for $repo_name"
    else
        echo "No dependencies to update for $repo_name"
    fi

    echo "✓ $repo_name updated successfully"
    echo ""

done < "$NODES_CONFIG"

echo ""
echo "========================================================"
echo "Custom nodes update complete!"
echo "========================================================"
