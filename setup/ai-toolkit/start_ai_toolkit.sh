#!/bin/bash
set -e

echo "Starting AI-Toolkit UI..."

cd /workspace/ai-toolkit/ui

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Generate Prisma client if needed
if [ ! -d "node_modules/.prisma" ]; then
    echo "Generating Prisma client..."
    npx prisma generate
fi

# Check if .next build directory exists, rebuild if missing
if [ ! -d ".next" ]; then
    echo "Next.js build not found, rebuilding..."
    npm run build
fi

# Start AI-Toolkit UI (runs worker and Next.js server via concurrently)
echo "Starting AI-Toolkit on port 8675..."
npm run start
