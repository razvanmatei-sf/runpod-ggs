#!/bin/bash
# ABOUTME: Shared download helper for model downloads
# ABOUTME: Uses aria2c for fast parallel downloads with wget fallback, validates file sizes

# Get remote file size via HEAD request
# Usage: get_remote_size <url> [token]
get_remote_size() {
    local url="$1"
    local token="$2"
    local size

    if [ -n "$token" ]; then
        size=$(curl -sI -H "Authorization: Bearer $token" "$url" | grep -i content-length | tail -1 | tr -d '\r' | awk '{print $2}')
    else
        size=$(curl -sI "$url" | grep -i content-length | tail -1 | tr -d '\r' | awk '{print $2}')
    fi

    echo "${size:-0}"
}

# Download a file with aria2c (fast) or wget (fallback)
# Validates file size to detect incomplete downloads
# Usage: download <url> <destination>
download() {
    local url="$1"
    local dest="$2"
    local token="${HF_TOKEN:-$HUGGING_FACE_HUB_TOKEN}"

    mkdir -p "$(dirname "$dest")"

    # Check for aria2 control file (incomplete download)
    if [ -f "${dest}.aria2" ]; then
        echo "Resuming incomplete download: $(basename "$dest")..."
    elif [ -f "$dest" ]; then
        # File exists, verify size
        local local_size=$(stat -c%s "$dest" 2>/dev/null || stat -f%z "$dest" 2>/dev/null)
        local remote_size=$(get_remote_size "$url" "$token")

        if [ "$remote_size" -gt 0 ] && [ "$local_size" -eq "$remote_size" ]; then
            echo "Skipping $(basename "$dest") - complete (${local_size} bytes)"
            return 0
        elif [ "$remote_size" -gt 0 ]; then
            echo "Re-downloading $(basename "$dest") - size mismatch (local: ${local_size}, remote: ${remote_size})"
            rm -f "$dest"
        else
            echo "Skipping $(basename "$dest") - exists (could not verify size)"
            return 0
        fi
    else
        echo "Downloading $(basename "$dest")..."
    fi

    if command -v aria2c &> /dev/null; then
        if [ -n "$token" ]; then
            aria2c -x 16 -s 16 -k 1M --summary-interval=1 --file-allocation=none \
                --auto-file-renaming=false --allow-overwrite=true \
                --header="Authorization: Bearer $token" \
                -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url"
        else
            aria2c -x 16 -s 16 -k 1M --summary-interval=1 --file-allocation=none \
                --auto-file-renaming=false --allow-overwrite=true \
                -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url"
        fi
    elif [ -n "$token" ]; then
        wget -c -q --show-progress --header="Authorization: Bearer $token" -O "$dest" "$url"
    else
        wget -c -q --show-progress -O "$dest" "$url"
    fi

    # Verify download completed successfully
    if [ -f "$dest" ]; then
        local final_size=$(stat -c%s "$dest" 2>/dev/null || stat -f%z "$dest" 2>/dev/null)
        local expected_size=$(get_remote_size "$url" "$token")

        if [ "$expected_size" -gt 0 ] && [ "$final_size" -ne "$expected_size" ]; then
            echo "WARNING: $(basename "$dest") may be incomplete (got ${final_size}, expected ${expected_size})"
            return 1
        fi
    else
        echo "ERROR: Failed to download $(basename "$dest")"
        return 1
    fi
}
