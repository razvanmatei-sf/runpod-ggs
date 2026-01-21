#!/bin/bash
# ABOUTME: Simple download helper using aria2c with conditional-get for smart skipping
# ABOUTME: Tracks downloads and provides a summary at the end automatically

# Arrays to track download results
DOWNLOAD_ATTEMPTED=()
DOWNLOAD_SUCCESS=()
DOWNLOAD_SKIPPED=()
DOWNLOAD_FAILED=()

# Check available disk space and warn if low
check_disk_space() {
    local path="${1:-/workspace}"
    local min_gb="${2:-5}"

    if [ -d "$path" ]; then
        local available_kb=$(df "$path" | tail -1 | awk '{print $4}')
        local available_gb=$((available_kb / 1024 / 1024))

        if [ "$available_gb" -lt "$min_gb" ]; then
            echo ""
            echo "⚠️  WARNING: Low disk space on $path"
            echo "   Available: ${available_gb}GB (minimum recommended: ${min_gb}GB)"
            echo ""
            return 1
        fi
    fi
    return 0
}

# Simple download function using aria2c
# Usage: download <url> <destination>
download() {
    local url="$1"
    local dest="$2"
    local dir="$(dirname "$dest")"
    local filename="$(basename "$dest")"
    local token="${HF_TOKEN:-$HUGGING_FACE_HUB_TOKEN}"

    DOWNLOAD_ATTEMPTED+=("$filename")
    mkdir -p "$dir"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 $filename"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local aria_args=(
        -x 16 -s 16
        -d "$dir"
        -o "$filename"
        --auto-file-renaming=false
        --conditional-get=true
        --allow-overwrite=true
        --console-log-level=notice
        --summary-interval=5
    )

    # Add auth header if token is available
    if [ -n "$token" ]; then
        aria_args+=(--header="Authorization: Bearer $token")
    fi

    # Capture aria2c output to detect skipped files
    local output
    output=$(aria2c "${aria_args[@]}" "$url" 2>&1)
    local exit_code=$?

    echo "$output"

    # Check for disk space errors in output
    if echo "$output" | grep -qi "no space left\|disk full\|not enough space\|ENOSPC"; then
        DOWNLOAD_FAILED+=("$filename")
        echo ""
        echo "❌ $filename - FAILED: DISK FULL"
        echo "┌─────────────────────────────────────────────────────────────┐"
        echo "│  ERROR: No disk space remaining!                            │"
        echo "│  Please free up space on your network volume and try again. │"
        echo "└─────────────────────────────────────────────────────────────┘"
        df -h "$dir" 2>/dev/null || true
        echo ""
        return 1
    fi

    # Exit code 0 = success, 13 = file already exists (conditional-get), 17 = file already exists
    if [ $exit_code -eq 0 ]; then
        # Check if file was skipped (already complete)
        if echo "$output" | grep -q "already completed\|Download complete\|Nothing to download"; then
            DOWNLOAD_SKIPPED+=("$filename")
            echo "⏭️  $filename (already exists)"
        else
            DOWNLOAD_SUCCESS+=("$filename")
            echo "✅ $filename"
        fi
    elif [ $exit_code -eq 13 ] || [ $exit_code -eq 17 ]; then
        # File already exists - treat as skipped, not failure
        DOWNLOAD_SKIPPED+=("$filename")
        echo "⏭️  $filename (already exists)"
    elif [ $exit_code -eq 1 ]; then
        # Exit code 1 can be various errors - check for common issues
        DOWNLOAD_FAILED+=("$filename")
        echo "❌ $filename - FAILED (exit code: $exit_code)"
        # Show disk space info to help diagnose
        echo "   Disk space on $dir:"
        df -h "$dir" 2>/dev/null | tail -1 || true
        return 1
    else
        DOWNLOAD_FAILED+=("$filename")
        echo "❌ $filename - FAILED (exit code: $exit_code)"
        return 1
    fi
}

# Print download summary
_print_summary() {
    local total=${#DOWNLOAD_ATTEMPTED[@]}
    local success=${#DOWNLOAD_SUCCESS[@]}
    local skipped=${#DOWNLOAD_SKIPPED[@]}
    local failed=${#DOWNLOAD_FAILED[@]}

    # Only print if we attempted any downloads
    if [ $total -eq 0 ]; then
        return
    fi

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                     DOWNLOAD SUMMARY                         ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    printf "║  📊 Total attempted: %-40s║\n" "$total"
    printf "║  ✅ Downloaded:      %-40s║\n" "$success"
    printf "║  ⏭️  Skipped:         %-40s║\n" "$skipped"
    printf "║  ❌ Failed:          %-40s║\n" "$failed"
    echo "╚══════════════════════════════════════════════════════════════╝"

    if [ ${#DOWNLOAD_FAILED[@]} -gt 0 ]; then
        echo ""
        echo "❌ Failed downloads:"
        for file in "${DOWNLOAD_FAILED[@]}"; do
            echo "   • $file"
        done
    fi

    if [ ${#DOWNLOAD_SUCCESS[@]} -gt 0 ]; then
        echo ""
        echo "✅ Downloaded:"
        for file in "${DOWNLOAD_SUCCESS[@]}"; do
            echo "   • $file"
        done
    fi

    if [ ${#DOWNLOAD_SKIPPED[@]} -gt 0 ]; then
        echo ""
        echo "⏭️  Skipped (already exist):"
        for file in "${DOWNLOAD_SKIPPED[@]}"; do
            echo "   • $file"
        done
    fi

    echo ""
}

# Trap to ensure summary is printed when script exits
trap _print_summary EXIT
