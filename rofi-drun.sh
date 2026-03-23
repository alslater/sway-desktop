#!/bin/bash
# Open XDG application menu on the currently focused output
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
rofi -show drun -monitor "$output"
