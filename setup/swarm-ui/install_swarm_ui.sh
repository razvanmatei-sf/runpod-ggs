#!/bin/bash
set -e

# Start timer
START_TIME=$(date +%s)

echo "Installing SwarmUI..."

cd /workspace

# Download and install FFmpeg
echo "Installing FFmpeg..."
rm -f ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz
wget https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2025-01-31-12-58/ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz
tar xvf ffmpeg-N-118385-g0225fe857d-linux64-gpl.tar.xz --no-same-owner
mv ffmpeg-N-118385-g0225fe857d-linux64-gpl/bin/ffmpeg /usr/local/bin/
mv ffmpeg-N-118385-g0225fe857d-linux64-gpl/bin/ffprobe /usr/local/bin/
chmod +x /usr/local/bin/ffmpeg
chmod +x /usr/local/bin/ffprobe
echo "FFmpeg installed successfully"

# Download and install cloudflared
echo "Installing cloudflared..."
rm -f cloudflared-linux-amd64.deb
wget https://github.com/cloudflare/cloudflared/releases/download/2025.7.0/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb
echo "cloudflared installed successfully"

# Clone SwarmUI repository
echo "Cloning SwarmUI repository..."
if [ -d "SwarmUI" ]; then
    echo "SwarmUI directory exists, updating..."
    cd SwarmUI
    git reset --hard
    git stash
    git pull
    cd ..
else
    git clone --depth 1 https://github.com/mcmonkeyprojects/SwarmUI
fi

# Clone ComfyUI extensions into SwarmUI
echo "Cloning ComfyUI extensions..."
mkdir -p SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes

if [ -d "SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-Frame-Interpolation" ]; then
    echo "ComfyUI-Frame-Interpolation already exists, skipping..."
else
    git clone --depth 1 https://github.com/Fannovel16/ComfyUI-Frame-Interpolation SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-Frame-Interpolation
fi

if [ -d "SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-TeaCache" ]; then
    echo "ComfyUI-TeaCache already exists, skipping..."
else
    git clone --depth 1 https://github.com/welltop-cn/ComfyUI-TeaCache SwarmUI/src/BuiltinExtensions/ComfyUIBackend/DLNodes/ComfyUI-TeaCache
fi

# Enter SwarmUI directory
cd SwarmUI

# Reset and update again to be safe
git reset --hard
git stash
git pull

# Install .NET SDK
echo "Installing .NET SDK..."
cd launchtools
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 8.0 --runtime aspnetcore
./dotnet-install.sh --channel 8.0
cd ..

# Run initial launch to set up SwarmUI
echo "Setting up SwarmUI (this may take a while)..."
./launch-linux.sh --launch_mode none --cloudflared-path cloudflared --port 7861

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================================"
echo "SwarmUI installation complete!"
echo "========================================================"
echo "⏱️  Total installation time: ${MINUTES}m ${SECONDS}s"
echo "========================================================"
