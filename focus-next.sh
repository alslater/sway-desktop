#!/bin/bash
# Cycle focus to next window within the current workspace only
focused_ws=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused) | .name')

# Get all window con_ids on the focused workspace in order
mapfile -t wins < <(swaymsg -t get_tree | jq -r --arg ws "$focused_ws" '
  .. | objects | select(.type=="workspace" and .name==$ws) |
  .. | objects | select(.type=="con" and .name != null and .name != "" and (.nodes|length)==0) |
  .id' 2>/dev/null)

count=${#wins[@]}
[ "$count" -le 1 ] && exit 0

# Find index of currently focused window
focused_id=$(swaymsg -t get_tree | jq '.. | objects | select(.focused==true) | .id')
next_id=""
for i in "${!wins[@]}"; do
    if [ "${wins[$i]}" = "$focused_id" ]; then
        next_index=$(( (i + 1) % count ))
        next_id="${wins[$next_index]}"
        break
    fi
done

[ -n "$next_id" ] && swaymsg "[con_id=$next_id] focus"
