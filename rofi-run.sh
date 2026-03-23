#!/bin/bash
# Open rofi on the currently focused output
# Source bashrc so PATH includes ~/bin and other user additions
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
rofi -show run -monitor "$output"
