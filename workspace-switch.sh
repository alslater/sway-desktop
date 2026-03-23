#!/bin/bash
# Switch both outputs to a "virtual" workspace together.
# DP-3 uses workspaces 1-9, DP-4 uses 11-19 as paired companions.

direction=$1

current=$(swaymsg -t get_workspaces | jq '[.[] | select(.output=="DP-3" and .visible==true)] | .[0].num')
focused=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')

case $direction in
    next) target=$((current + 1)) ;;
    prev) target=$((current - 1)) ;;
    goto) target=$2 ;;
    *) exit 1 ;;
esac

[ $target -lt 1 ] && target=9
[ $target -gt 9 ] && target=1

# Switch the unfocused output first so focus ends up back where it started
if [ "$focused" = "DP-3" ]; then
    swaymsg focus output DP-4 && swaymsg workspace number $((target + 10))
    swaymsg focus output DP-3 && swaymsg workspace number $target
else
    swaymsg focus output DP-3 && swaymsg workspace number $target
    swaymsg focus output DP-4 && swaymsg workspace number $((target + 10))
fi
