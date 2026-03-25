#!/bin/bash
# Switch screen 2 (DP-4) to show the workspace paired with the current screen 1 workspace.
# Pairing: workspace N (screen 1) <-> workspace N+10 (screen 2), for N in 1-9.

current_ws=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused) | .num')

if [ "$current_ws" -ge 1 ] && [ "$current_ws" -le 9 ]; then
    target=$((current_ws + 10))
    swaymsg "focus output DP-4; workspace number $target; focus output DP-3"
fi
