#!/bin/bash
# ABOUTME: Updates existing AI-Toolkit installation with latest code and dependencies.
# ABOUTME: Uses uv for fast package installation.

set -e

export UV_SKIP_WHEEL_FILENAME_CHECK=1
export UV_LINK_MODE=copy

echo "Updating AI-Toolkit..."

cd /workspace/ai-toolkit
source venv/bin/activate

git stash
git pull --force

pip install uv

uv pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

uv pip install -r requirements.txt

cd ui
npm install
npm run build
npm run update_db

echo "AI-Toolkit update complete"
