#!/bin/bash

input_file="$1"

# Ensure input file is provided and exists
if [[ -z "$input_file" || ! -f "$input_file" ]]; then
    echo "Usage: $0 input_file"
    exit 1
fi

# Read the input file line by line
count=1
while IFS= read -r line; do
    # Skip the header
    if [[ $count -eq 1 ]]; then
        count=$((count + 1))
        continue
    fi

    # Create the .ass subtitle file for each line
    subtitle_file="o_postepowaniu_${count}.ass"
    cat <<EOL > "$subtitle_file"
[Script Info]
Title: Subtitle $count
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,10,&H00FFFFFF,&H000000FF,&H80000000,&H60FFFFFF,0,0,0,0,100,100,0,0,3,1,0,2,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,Default,,0,0,0,,$line
EOL

    echo "Created $subtitle_file"
    count=$((count + 1))
done < "$input_file"

