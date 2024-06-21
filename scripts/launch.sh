#!/bin/sh
killall waybar
pkill waybar
sleep 0.2 

# Get the number of active monitors
ACTIVE_MONITORS=$(swaymsg -t get_outputs | jq '.[] | select(.active) | .name' | wc -l)

if [ "$ACTIVE_MONITORS" -eq 2 ]; then
  waybar -c ~/.config/waybar/waybar-two-monitors.jsonc -s ~/.config/waybar/styles.css &
else
  waybar -c ~/.config/waybar/waybar-one-monitor.jsonc -s ~/.config/waybar/styles.css &
fi
