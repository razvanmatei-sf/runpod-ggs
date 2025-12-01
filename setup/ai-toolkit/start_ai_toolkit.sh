#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Start the UI server on port 8675
echo "Starting AI-Toolkit UI on port 8675..."
npm run start -- --port 8675 --host 0.0.0.0

echo "AI-Toolkit UI started"
