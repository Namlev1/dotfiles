#!/bin/sh
killall waybar
pkill waybar
sleep 0.2 

GAP_FILE="$HOME/.config/sway/current_gap"

if [ ! -f "$GAP_FILE" ]; then
    echo 0 > "$GAP_FILE"
fi

current_gap=$(cat "$GAP_FILE")
if [ "$current_gap" -eq 10 ]; then
    new_gap=0
else
    new_gap=10
fi

echo "$new_gap" > "$GAP_FILE"

swaymsg gaps inner all set "$new_gap"

# if gap == 10, show waybar
if [ "$new_gap" -eq 10 ]; then
    # Get the number of active monitors
    ACTIVE_MONITORS=$(swaymsg -t get_outputs | jq '.[] | select(.active) | .name' | wc -l)

    if [ "$ACTIVE_MONITORS" -eq 2 ]; then
        waybar -c ~/.config/waybar/waybar-two-monitors.jsonc -s ~/.config/waybar/styles.css &
    else
        waybar -c ~/.config/waybar/waybar-one-monitor.jsonc -s ~/.config/waybar/styles.css &
    fi
fi
