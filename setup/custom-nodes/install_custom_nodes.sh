#!/bin/bash

# ComfyUI Custom Nodes Install Script
set -e

echo "========================================================"
echo "Installing ComfyUI Custom Nodes"
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

# Check if nodes config exists
if [ ! -f "$NODES_CONFIG" ]; then
    echo "ERROR: Custom nodes configuration not found at $NODES_CONFIG"
    exit 1
fi

# Activate ComfyUI virtual environment
source /workspace/ComfyUI/venv/bin/activate

# Create custom_nodes directory if it doesn't exist
mkdir -p "$CUSTOM_NODES_DIR"

# Read nodes from config and install them
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

    echo "----------------------------------------"
    echo "Installing: $repo_name"
    echo "Repository: $repo_url"
    echo "----------------------------------------"

    # Clone or update the repository
    if [ -d "$node_path" ]; then
        echo "Node already exists, skipping clone: $repo_name"
    else
        echo "Cloning $repo_name..."
        cd "$CUSTOM_NODES_DIR"
        git clone "$repo_url"
        echo "Clone completed: $repo_name"
    fi

    # Check for and install dependencies
    cd "$node_path"

    if [ -f "requirements.txt" ]; then
        echo "Installing Python requirements for $repo_name..."
        pip install -r requirements.txt
        echo "Requirements installed for $repo_name"
    elif [ -f "install.py" ]; then
        echo "Running install.py for $repo_name..."
        python install.py
        echo "Install script completed for $repo_name"
    elif [ -f "install.sh" ]; then
        echo "Running install.sh for $repo_name..."
        bash install.sh
        echo "Install script completed for $repo_name"
    else
        echo "No dependencies to install for $repo_name"
    fi

    echo "✓ $repo_name installed successfully"
    echo ""

done < "$NODES_CONFIG"

echo ""
echo "========================================================"
echo "Custom nodes installation complete!"
echo "========================================================"
