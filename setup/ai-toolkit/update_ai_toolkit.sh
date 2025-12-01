#!/bin/bash

# AI-Toolkit Update Script - Updates code and dependencies
set -e

echo "========================================================"
echo "AI-Toolkit Update"
echo "========================================================"

cd /workspace/ai-toolkit

echo "Updating AI-Toolkit repository..."
git stash
git pull --force

echo "Updating Python dependencies with UV..."
uv pip install --python venv/bin/python -r requirements.txt

echo "Updating UI dependencies..."
cd ui
npm install

echo "========================================================"
echo "Update complete!"
echo "========================================================"
