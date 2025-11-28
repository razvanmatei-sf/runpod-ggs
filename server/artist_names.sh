#!/bin/bash

# Users list - add ":admin" suffix for admin privileges
# Example: "John Doe:admin" or just "John Doe" for regular user
USERS=(
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
    "Razvan Matei:admin"
)

OUTPUT_DIR="/workspace/ComfyUI/output"

echo "Creating user folders in $OUTPUT_DIR..."

for user in "${USERS[@]}"; do
    # Remove :admin suffix if present to get clean name
    name="${user%:admin}"
    mkdir -p "$OUTPUT_DIR/$name"
    echo "Created: $OUTPUT_DIR/$name"
done

echo "Done"
