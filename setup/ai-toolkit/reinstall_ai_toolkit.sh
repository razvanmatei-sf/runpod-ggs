#!/bin/bash
# ABOUTME: Removes existing AI-Toolkit installation and reinstalls from scratch.
# ABOUTME: Delegates to install_ai_toolkit.sh for the actual installation.

set -e

echo "Reinstalling AI-Toolkit..."

rm -rf /workspace/ai-toolkit

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"

echo "AI-Toolkit reinstall complete"
