#!/bin/bash
set -e

echo "Updating ComfyUI"

cd /workspace/ComfyUI
source venv/bin/activate

git stash
git pull --force

pip install -r requirements.txt

echo "ComfyUI Update complete"
