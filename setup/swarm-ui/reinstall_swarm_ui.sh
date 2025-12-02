#!/bin/bash
set -e

echo "Reinstalling SwarmUI"

cd /workspace

BACKUP_DIR="/workspace/backup/swarm-ui-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

[ -d "SwarmUI/Output" ] && cp -r SwarmUI/Output "$BACKUP_DIR/"
[ -d "SwarmUI/Models" ] && cp -r SwarmUI/Models "$BACKUP_DIR/"
[ -d "SwarmUI/Data" ] && cp -r SwarmUI/Data "$BACKUP_DIR/"

rm -rf SwarmUI

REPO_DIR="${REPO_DIR:-/workspace/runpod-ggs}"
bash "$REPO_DIR/setup/swarm-ui/install_swarm_ui.sh"

[ -d "$BACKUP_DIR/Output" ] && cp -r "$BACKUP_DIR/Output/"* /workspace/SwarmUI/Output/
[ -d "$BACKUP_DIR/Models" ] && cp -r "$BACKUP_DIR/Models/"* /workspace/SwarmUI/Models/
[ -d "$BACKUP_DIR/Data" ] && cp -r "$BACKUP_DIR/Data/"* /workspace/SwarmUI/Data/

echo "SwarmUI Reinstall complete"
