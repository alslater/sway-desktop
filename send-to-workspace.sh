#!/bin/bash
# Send focused window to workspace N, paired to the current screen.
# Screen 1 (DP-3): workspaces 1-9
# Screen 2 (DP-4): workspaces 11-19
# Pressing N while on screen 2 sends to workspace N+10.

n=$1
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
current_ws=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused) | .num')

if [ "$output" = "DP-4" ]; then
    target=$((n + 10))
else
    target=$n
fi

swaymsg "move container to workspace number $target"

# For screen 2 destinations: briefly switch to the target workspace and apply
# layout tabbed at the workspace root, then switch back.  Without this the
# moved window can land inside a nested sub-container and miss the tabbed layout.
if [ "$target" -ge 11 ] && [ "$target" -le 19 ] && [ "$target" -ne "$current_ws" ]; then
    swaymsg "workspace number $target"
    swaymsg "layout tabbed"
    swaymsg "workspace number $current_ws"
fi
