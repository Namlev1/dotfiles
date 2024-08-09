#!/bin/bash

# Directory containing the .ass files
QUOTE_DIR="/home/namlev/dotfiles/quotes"

# Get a list of all .ass files in the directory
QUOTE_FILES=("$QUOTE_DIR"/*.ass)

# Check if there are any .ass files in the directory
if [ ${#QUOTE_FILES[@]} -eq 0 ]; then
  echo "No .ass files found in $QUOTE_DIR"
  exit 1
fi

# Select a random .ass file
RANDOM_QUOTE_FILE=${QUOTE_FILES[RANDOM % ${#QUOTE_FILES[@]}]}

# Define the paths for the input and output images
INPUT_IMAGE="/home/namlev/Pictures/wallpapers/wallpaper.jpg"
OUTPUT_IMAGE="/home/namlev/Pictures/wallpapers/subtitles.jpg"

# Execute the add_text_to_image.sh script with the selected .ass file
add_text_to_image.sh "$INPUT_IMAGE" "$OUTPUT_IMAGE" "$RANDOM_QUOTE_FILE"

