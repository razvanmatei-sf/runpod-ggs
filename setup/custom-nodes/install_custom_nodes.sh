#!/bin/bash

# ComfyUI Custom Nodes Install Script
set -e

# Start timer
START_TIME=$(date +%s)

# Ensure PATH includes UV and other tools
export PATH="/root/.cargo/bin:$PATH"
export PATH="/root/.local/bin:$PATH"
export PATH="/usr/local/bin:$PATH"

# Suppress UV hardlink warning (can't use hardlinks across filesystems)
export UV_LINK_MODE=copy

echo "========================================================"
echo "Installing ComfyUI Custom Nodes"
echo "========================================================"

# Check if UV is installed, install if not
if ! command -v uv &> /dev/null && [ ! -f "/root/.cargo/bin/uv" ] && [ ! -f "/root/.local/bin/uv" ]; then
    echo "UV not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="/root/.local/bin:$PATH"
    export PATH="/root/.cargo/bin:$PATH"
fi

# Determine UV path
if [ -f "/root/.cargo/bin/uv" ]; then
    UV_CMD="/root/.cargo/bin/uv"
elif [ -f "/root/.local/bin/uv" ]; then
    UV_CMD="/root/.local/bin/uv"
elif command -v uv &> /dev/null; then
    UV_CMD="uv"
else
    echo "ERROR: UV installation failed"
    exit 1
fi

echo "Using UV at: $UV_CMD"

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
        $UV_CMD pip install --python "$PYTHON_BIN" -r requirements.txt
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

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Custom nodes installation complete!"
echo "========================================================"
echo "⏱️  Total installation time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
