#!/bin/bash

# SwarmUI Kill Script
echo "Stopping SwarmUI..."
fuser -k 7861/tcp
echo "SwarmUI stopped"
