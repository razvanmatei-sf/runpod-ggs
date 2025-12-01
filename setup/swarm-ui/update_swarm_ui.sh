#!/bin/bash

# SwarmUI Update Script - Updates code and dependencies
set -e

# Start timer
START_TIME=$(date +%s)

echo "========================================================"
echo "SwarmUI Update"
echo "========================================================"

cd /workspace/SwarmUI

echo "Updating SwarmUI repository..."
git stash
git pull --force

echo "Updating .NET SDK if needed..."
cd launchtools
if [ -f "dotnet-install.sh" ]; then
    ./dotnet-install.sh --channel 8.0 --runtime aspnetcore
    ./dotnet-install.sh --channel 8.0
fi
cd ..

echo "Updating ComfyUI extensions..."
cd src/BuiltinExtensions/ComfyUIBackend/DLNodes

if [ -d "ComfyUI-Frame-Interpolation" ]; then
    echo "Updating ComfyUI-Frame-Interpolation..."
    cd ComfyUI-Frame-Interpolation
    git stash
    git pull --force
    cd ..
fi

if [ -d "ComfyUI-TeaCache" ]; then
    echo "Updating ComfyUI-TeaCache..."
    cd ComfyUI-TeaCache
    git stash
    git pull --force
    cd ..
fi

cd /workspace/SwarmUI

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "Update complete!"
echo "========================================================"
echo "⏱️  Total update time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
