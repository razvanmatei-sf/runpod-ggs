#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Install Node.js dependencies if not present
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start the UI server on port 8675
echo "Starting AI-Toolkit UI on port 8675..."
npx concurrently --restart-tries -1 --restart-after 1000 -n WORKER,UI "node dist/cron/worker.js" "npx next start --port 8675 --hostname 0.0.0.0"

echo "AI-Toolkit UI started"
