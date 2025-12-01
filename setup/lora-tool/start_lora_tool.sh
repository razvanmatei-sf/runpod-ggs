#!/bin/bash
set -e

echo "Starting LoRA-Tool..."

cd /workspace/lora-tool

# Start the Vite dev server on port 3000
echo "Launching LoRA-Tool on port 3000..."
npm run dev
