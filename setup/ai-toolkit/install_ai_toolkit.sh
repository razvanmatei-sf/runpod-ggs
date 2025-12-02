#!/bin/bash
set -e

echo "Installing AI-Toolkit"

cd /workspace

rm -rf ai-toolkit
git clone https://github.com/ostris/ai-toolkit.git
cd /workspace/ai-toolkit

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
pip install -r requirements.txt

cd ui
npm install
npm run build
npm run update_db

echo "AI-Toolkit Installation complete"
