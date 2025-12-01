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

# Create custom_nodes directory if it doesn't exist
mkdir -p "$CUSTOM_NODES_DIR"

# Use ComfyUI virtual environment with UV (no activation needed)
PYTHON_BIN="/workspace/ComfyUI/venv/bin/python"

# Read nodes from config and install them
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

    echo "----------------------------------------"
    echo "Installing: $display_name"
    echo "Repository: $repo_url"
    echo "----------------------------------------"

    # Extract repo name from URL (last part without .git)
    repo_name=$(basename "$repo_url" .git)
    node_path="$CUSTOM_NODES_DIR/$repo_name"

    # Clone or update the repository
    if [ -d "$node_path" ]; then
        echo "Node already exists, skipping clone: $repo_name"
    else
        echo "Cloning $repo_name..."
        cd "$CUSTOM_NODES_DIR"
        git clone --depth 1 "$repo_url"
        echo "Clone completed: $repo_name"
    fi

    # Check for and install dependencies
    cd "$node_path"

    if [ -f "requirements.txt" ]; then
        echo "Installing Python requirements for $display_name with UV..."
        uv pip install --python "$PYTHON_BIN" -r requirements.txt
        echo "Requirements installed for $display_name"
    elif [ -f "install.py" ]; then
        echo "Running install.py for $display_name..."
        python install.py
        echo "Install script completed for $display_name"
    elif [ -f "install.sh" ]; then
        echo "Running install.sh for $display_name..."
        bash install.sh
        echo "Install script completed for $display_name"
    else
        echo "No dependencies to install for $display_name"
    fi

    echo "✓ $display_name installed successfully"
    echo ""

done < "$NODES_CONFIG"

echo "========================================================"
echo "Custom nodes installation complete!"
echo "========================================================"
