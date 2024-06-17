#!/bin/sh
killall waybar
pkill waybar
sleep 0.2 
waybar -l debug -c ~/.config/waybar/waybar.jsonc -s ~/.config/waybar/styles.css &
