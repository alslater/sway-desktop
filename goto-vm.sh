#!/bin/bash
# Switch to workspace 20 only if a VirtualBox VM is running there.
has_vm=$(swaymsg -t get_tree | python3 -c "
import json, sys
tree = json.load(sys.stdin)
for output in tree.get('nodes', []):
    for ws in output.get('nodes', []):
        if ws.get('num') == 20:
            leaves = ws.get('nodes', []) + ws.get('floating_nodes', [])
            if leaves:
                print('yes')
            break
")
[ "$has_vm" = "yes" ] && swaymsg 'workspace number 20'
