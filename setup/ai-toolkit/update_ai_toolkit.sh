#!/bin/bash
set -e

echo "Updating AI-Toolkit"

cd /workspace/ai-toolkit
source venv/bin/activate

git stash
git pull --force

pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
pip install -r requirements.txt

cd ui
npm install
npm run build
npm run update_db

echo "AI-Toolkit Update complete"
