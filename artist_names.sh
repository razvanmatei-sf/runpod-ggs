#!/bin/bash

# Artist names - add or remove names here
ARTISTS=(
    "razvan"
    "serhii"
    "ivor"
)

OUTPUT_DIR="/ComfyUI/output"

echo "Creating artist folders in $OUTPUT_DIR..."

for artist in "${ARTISTS[@]}"; do
    mkdir -p "$OUTPUT_DIR/$artist"
    echo "Created: $OUTPUT_DIR/$artist"
done

echo "Done"
