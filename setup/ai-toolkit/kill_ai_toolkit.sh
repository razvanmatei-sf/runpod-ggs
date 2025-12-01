#!/bin/bash

# AI-Toolkit Kill Script
echo "Stopping AI-Toolkit..."
fuser -k 8675/tcp
echo "AI-Toolkit stopped"
