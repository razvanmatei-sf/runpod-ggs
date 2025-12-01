#!/bin/bash

# LoRA-Tool Kill Script
echo "Stopping LoRA-Tool..."
fuser -k 3000/tcp
echo "LoRA-Tool stopped"
