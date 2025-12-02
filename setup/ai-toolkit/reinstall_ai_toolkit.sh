#!/bin/bash
set -e

echo "Reinstalling AI-Toolkit"

rm -rf /workspace/ai-toolkit

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/ai-toolkit/install_ai_toolkit.sh"

echo "AI-Toolkit Reinstall complete"
