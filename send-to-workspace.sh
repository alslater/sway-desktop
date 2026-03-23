#!/bin/bash
# Send focused window to workspace N, paired to the current screen.
# Screen 1 (DP-3): workspaces 1-9
# Screen 2 (DP-4): workspaces 11-19
# Pressing N while on screen 2 sends to workspace N+10.

n=$1
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')

if [ "$output" = "DP-4" ]; then
    target=$((n + 10))
else
    target=$n
fi

swaymsg "move container to workspace number $target"
