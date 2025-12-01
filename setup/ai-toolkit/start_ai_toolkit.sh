#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Ensure the build exists
if [ ! -d ".next" ]; then
    echo "Building UI..."
    npm run build
fi

# Start the worker in the background
echo "Starting background worker..."
node dist/cron/worker.js &

# Start the Next.js production server on port 8675
echo "Starting Next.js UI on port 8675..."
PORT=8675 npx next start --hostname 0.0.0.0
