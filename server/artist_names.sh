#!/bin/bash

# Artist names - add or remove names here
ARTISTS=(
    "Rosa Macak Cizmesija"
    "Karlo Vukovic"
    "Marko Kahlina"
    "Katarina Zidar"
    "Oleg Moskaljov"
    "Ivan Murat"
    "Matej Urukalo"
    "Ivor Strelar"
    "Ivan Prlic"
    "Josipa Filipcic Mazar"
    "Viktorija Samardzic"
    "Serhii Yashyn"
)

# Admins - users who can access admin mode (these names also appear in the dropdown)
ADMINS=(
    "Razvan Matei"
)

OUTPUT_DIR="/workspace/ComfyUI/output"

echo "Creating artist folders in $OUTPUT_DIR..."

for artist in "${ARTISTS[@]}"; do
    mkdir -p "$OUTPUT_DIR/$artist"
    echo "Created: $OUTPUT_DIR/$artist"
done

echo "Done"
