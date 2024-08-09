#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input_picture output_picture subtitles_file"
    exit 1
fi

# Assign arguments to variables
input_picture="$1"
output_picture="$2"
subtitles_file="$3"

# Run ffmpeg with the provided arguments
ffmpeg -y -i "$input_picture" -vf "subtitles=$subtitles_file" "$output_picture"

