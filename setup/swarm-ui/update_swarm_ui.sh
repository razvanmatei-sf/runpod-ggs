#!/bin/bash
set -e

echo "Updating SwarmUI"

cd /workspace/SwarmUI

git stash
git pull --force

cd launchtools
[ -f "dotnet-install.sh" ] && ./dotnet-install.sh --channel 8.0 --runtime aspnetcore
[ -f "dotnet-install.sh" ] && ./dotnet-install.sh --channel 8.0
cd ..

cd src/BuiltinExtensions/ComfyUIBackend/DLNodes

[ -d "ComfyUI-Frame-Interpolation" ] && cd ComfyUI-Frame-Interpolation && git stash && git pull --force && cd ..
[ -d "ComfyUI-TeaCache" ] && cd ComfyUI-TeaCache && git stash && git pull --force && cd ..

echo "SwarmUI Update complete"
