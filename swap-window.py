#!/usr/bin/env python3
"""
Swap the focused window with its neighbour in the given direction,
respecting als_tiling's grid layout on managed workspaces 1-9.

Usage: swap-window.py <h|j|k|l>

On non-managed workspaces falls back to sway's built-in move.
At the edge of the grid (no neighbour), does nothing.

Candidate selection for horizontal moves (left/right):
  - Must be strictly left/right of the focused window (no overlap in x)
  - Must have non-zero y-overlap with the focused window
  - Nearest first; ties broken by topmost window (smallest y)

Candidate selection for vertical moves (up/down):
  - Must be strictly above/below the focused window (no overlap in y)
  - Must have non-zero x-overlap with the focused window
  - Nearest first; ties broken by leftmost window (smallest x)
"""

import sys
import json
import subprocess

MANAGED_WORKSPACES = set(range(1, 10))

DIRECTIONS = {
    'h': 'left', 'j': 'down', 'k': 'up', 'l': 'right',
    'left': 'left', 'down': 'down', 'up': 'up', 'right': 'right',
}


def swaymsg(*args):
    r = subprocess.run(['swaymsg', *args], capture_output=True, text=True)
    return json.loads(r.stdout)


def get_leaves(node):
    """Recursively collect tiled leaf containers with their geometry."""
    children = node.get('nodes', [])
    if not children:
        if node.get('type') == 'con' and node.get('id'):
            return [node]
        return []
    leaves = []
    for child in children:
        leaves.extend(get_leaves(child))
    return leaves


def overlap(a, b, axis):
    """Pixel overlap between rects a and b on the given axis ('x' or 'y')."""
    if axis == 'x':
        lo = max(a['x'], b['x'])
        hi = min(a['x'] + a['width'], b['x'] + b['width'])
    else:
        lo = max(a['y'], b['y'])
        hi = min(a['y'] + a['height'], b['y'] + b['height'])
    return max(0, hi - lo)


def find_target(focused_rect, windows, direction):
    fr = focused_rect
    candidates = []

    for w in windows:
        wr = w['rect']
        if direction == 'right':
            gap = wr['x'] - (fr['x'] + fr['width'])
            if gap >= 0 and overlap(fr, wr, 'y') > 0:
                candidates.append((gap, wr['y'], w))
        elif direction == 'left':
            gap = fr['x'] - (wr['x'] + wr['width'])
            if gap >= 0 and overlap(fr, wr, 'y') > 0:
                candidates.append((gap, wr['y'], w))
        elif direction == 'down':
            gap = wr['y'] - (fr['y'] + fr['height'])
            if gap >= 0 and overlap(fr, wr, 'x') > 0:
                candidates.append((gap, wr['x'], w))
        elif direction == 'up':
            gap = fr['y'] - (wr['y'] + wr['height'])
            if gap >= 0 and overlap(fr, wr, 'x') > 0:
                candidates.append((gap, wr['x'], w))

    if not candidates:
        return None
    candidates.sort(key=lambda c: (c[0], c[1]))
    return candidates[0][2]


def find_workspace_node(node, num):
    if node.get('type') == 'workspace' and node.get('num') == num:
        return node
    for child in node.get('nodes', []):
        result = find_workspace_node(child, num)
        if result:
            return result
    return None


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in DIRECTIONS:
        print(f"Usage: {sys.argv[0]} <h|j|k|l>", file=sys.stderr)
        sys.exit(1)

    direction = DIRECTIONS[sys.argv[1]]

    workspaces = swaymsg('-t', 'get_workspaces')
    focused_ws = next((w for w in workspaces if w['focused']), None)
    if not focused_ws:
        sys.exit(0)

    ws_num = focused_ws.get('num', -1)
    if ws_num not in MANAGED_WORKSPACES:
        # Not a managed workspace — fall back to sway's built-in move
        subprocess.run(['swaymsg', f'move {direction}'])
        return

    tree = swaymsg('-t', 'get_tree')
    ws_node = find_workspace_node(tree, ws_num)
    if not ws_node:
        sys.exit(0)

    windows = get_leaves(ws_node)
    focused = next((w for w in windows if w.get('focused')), None)
    if not focused:
        sys.exit(0)

    target = find_target(focused['rect'], [w for w in windows if w['id'] != focused['id']], direction)
    if not target:
        return  # at the edge — no swap, no move out of workspace

    subprocess.run(['swaymsg', f'swap container with con_id {target["id"]}'])


if __name__ == '__main__':
    main()
