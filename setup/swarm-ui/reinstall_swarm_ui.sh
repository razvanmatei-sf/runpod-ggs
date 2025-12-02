#!/bin/bash
set -e

echo "Reinstalling SwarmUI"

cd /workspace
rm -rf SwarmUI

bash /workspace/runpod-ggs/setup/swarm-ui/install_swarm_ui.sh

echo "SwarmUI Reinstall complete"
