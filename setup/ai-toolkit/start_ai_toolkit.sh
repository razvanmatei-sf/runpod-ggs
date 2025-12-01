#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Force npm install to ensure all dependencies are present
echo "Installing/updating Node.js dependencies..."
npm install

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

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
