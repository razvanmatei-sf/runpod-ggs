#!/bin/bash

# ComfyUI Kill Script
echo "Stopping ComfyUI..."
fuser -k 8188/tcp
echo "ComfyUI stopped"
