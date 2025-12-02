#!/bin/bash
set -e

echo "Reinstalling SwarmUI"

cd /workspace

rm -rf SwarmUI

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/swarm-ui/install_swarm_ui.sh"

echo "SwarmUI Reinstall complete"
