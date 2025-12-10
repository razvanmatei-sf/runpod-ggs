#!/bin/bash
# ABOUTME: Shared download helper for model downloads
# ABOUTME: Uses aria2c for fast parallel downloads with wget fallback

# Download a file with aria2c (fast) or wget (fallback)
# Usage: download <url> <destination>
download() {
    local url="$1"
    local dest="$2"
    local token="${HF_TOKEN:-$HUGGING_FACE_HUB_TOKEN}"

    mkdir -p "$(dirname "$dest")"

    if [ -f "$dest" ]; then
        echo "Skipping $(basename "$dest") - exists"
        return 0
    fi

    echo "Downloading $(basename "$dest")..."

    if command -v aria2c &> /dev/null; then
        if [ -n "$token" ]; then
            aria2c -x 16 -s 16 -k 1M -q --file-allocation=none \
                --header="Authorization: Bearer $token" \
                -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url"
        else
            aria2c -x 16 -s 16 -k 1M -q --file-allocation=none \
                -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url"
        fi
    elif [ -n "$token" ]; then
        wget -q --show-progress --header="Authorization: Bearer $token" -O "$dest" "$url"
    else
        wget -q --show-progress -O "$dest" "$url"
    fi
}
