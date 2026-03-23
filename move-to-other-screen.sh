#!/bin/bash
# Move focused window to the paired workspace on the other screen
# Pairing: workspaces 1-9 (DP-3) <-> 11-19 (DP-4)

current_ws=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused) | .num')

if [ "$current_ws" -le 9 ]; then
    target=$((current_ws + 10))
    swaymsg "move container to workspace number $target; workspace number $target; layout tabbed"
else
    target=$((current_ws - 10))
    swaymsg "move container to workspace number $target; focus output DP-3"
fi
