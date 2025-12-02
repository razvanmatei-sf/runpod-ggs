#!/bin/bash
set -e

echo "Installing SwarmUI"

cd /workspace

rm -f ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz
wget https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2025-01-31-12-58/ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz
tar xvf ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz --no-same-owner
mv ffmpeg-N-118385-g0225fe857d-linux64-gpl/bin/ffmpeg /usr/local/bin/
mv ffmpeg-N-118385-g0225fe857d-linux64-gpl/bin/ffprobe /usr/local/bin/
chmod +x /usr/local/bin/ffmpeg
chmod +x /usr/local/bin/ffprobe

rm -f cloudflared-linux-amd64.deb
wget https://github.com/cloudflare/cloudflared/releases/download/2025.7.0/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

rm -rf SwarmUI
git clone https://github.com/mcmonkeyprojects/SwarmUI

mkdir -p SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-Frame-Interpolation
git clone https://github.com/welltop-cn/ComfyUI-TeaCache SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-TeaCache

cd SwarmUI

cd launchtools
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0 --runtime aspnetcore --install-dir /workspace/.dotnet
./dotnet-install.sh --channel 8.0 --install-dir /workspace/.dotnet
cd ..

export DOTNET_ROOT="/workspace/.dotnet"
export PATH="$PATH:$DOTNET_ROOT:$DOTNET_ROOT/tools"

./launch-linux.sh --launch_mode none --cloudflared-path cloudflared --port 7861

echo "SwarmUI Installation complete"
