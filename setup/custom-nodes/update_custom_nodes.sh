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

while IFS='|' read -r display_name repo_url || [ -n "$display_name" ]; do
    # Skip comments and empty lines
    if [[ "$display_name" =~ ^#.*$ ]] || [ -z "$display_name" ]; then
        continue
    fi

    # Trim whitespace
    display_name=$(echo "$display_name" | xargs)
    repo_url=$(echo "$repo_url" | xargs)

    # Extract repo name from URL (last part without .git)
    repo_name=$(basename "$repo_url" .git)
    node_path="$CUSTOM_NODES_DIR/$repo_name"

    # Only update if the node is installed
    if [ ! -d "$node_path" ]; then
        echo "⊘ Skipping $display_name (not installed)"
        continue
    fi

    echo "----------------------------------------"
    echo "Updating: $display_name"
    echo "Path: $node_path"
    echo "----------------------------------------"

    cd "$node_path"

    # Update the repository
    echo "Pulling latest changes for $display_name..."
    git stash
    git pull --force

    # Check for and update dependencies
    if [ -f "requirements.txt" ]; then
        echo "Updating Python requirements for $display_name..."
        pip install -r requirements.txt
        echo "Requirements updated for $display_name"
    elif [ -f "install.py" ]; then
        echo "Running install.py for $display_name..."
        python install.py
        echo "Install script completed for $display_name"
    elif [ -f "install.sh" ]; then
        echo "Running install.sh for $display_name..."
        bash install.sh
        echo "Install script completed for $display_name"
    else
        echo "No dependencies to update for $display_name"
    fi

    echo "✓ $display_name updated successfully"
    echo ""

done < "$NODES_CONFIG"

echo "========================================================"
echo "Custom nodes update complete!"
echo "========================================================"
