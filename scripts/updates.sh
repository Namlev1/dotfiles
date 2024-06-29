#!/bin/bash

# Calculate available updates pacman and aur

if ! updates=$(checkupdates-with-aur | wc -l ); then
    updates=0
fi

# Output in JSON format for Waybar Module custom-updates

if [ "$updates" -gt 0 ]; then
    printf '{"text": "%s", "alt": "%s", "tooltip": "Click to update your system", "class": "%s"}' "$updates" "$updates" "$updates" "$css_class"
else
    printf '{"text": "0", "alt": "0", "tooltip": "No updates available", "class": "green"}'
fi

