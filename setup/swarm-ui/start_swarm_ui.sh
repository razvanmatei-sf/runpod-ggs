#!/bin/bash
set -e

echo "Starting SwarmUI..."

cd /workspace/SwarmUI

# Start SwarmUI on port 7861
echo "Launching SwarmUI on port 7861..."
./launch-linux.sh --launch_mode web --cloudflared-path cloudflared --port 7861
