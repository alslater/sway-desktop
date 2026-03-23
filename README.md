# als-sway-config

Personal [sway](https://swaywm.org/) window manager configuration.

## Layout

Two monitors:
- **DP-3** (right, 3840×2160) — workspaces 1–9, managed by `als_sway_tiling` fair grid layout
- **DP-4** (left, 2560×1440) — workspaces 11–19, tabbed layout

Workspace switching moves both screens together as paired virtual desktops (1↔11, 2↔12, etc.).

## Submodules

| Submodule | Purpose |
|-----------|---------|
| `als_sway_tiling/` | Auto-tiling daemon + focus guard for modal dialogs |

Initialise after cloning:
```bash
git submodule update --init
cd als_sway_tiling && python3 -m venv venv && venv/bin/pip install -r requirements.txt
```

## Dependencies

### Core

| Package | Purpose |
|---------|---------|
| `sway` | Wayland compositor |
| `waybar` | Status bar |
| `rofi` | Run dialog / app launcher |
| `dunst` | Notification daemon |
| `swayidle` | Idle / screen lock trigger |
| `swaylock` | Screen locker |

### Screenshot

| Package | Purpose |
|---------|---------|
| `grim` | Wayland screen capture |
| `slurp` | Interactive region selection |
| `xdg-desktop-portal-wlr` | Portal backend for wlroots (needed for screen capture) |

### Clipboard & utilities

| Package | Purpose |
|---------|---------|
| `wl-clipboard` | Wayland clipboard (`wl-copy`, `wl-paste`) |
| `jq` | JSON parsing used by shell scripts |
| `python3-venv` | Python venv for als_sway_tiling |

### Audio

| Package | Purpose |
|---------|---------|
| `pipewire` | Audio server |
| `wireplumber` | PipeWire session manager |
| `wpctl` (via `pipewire-media-session` or `wireplumber`) | Volume control |

### Fonts & appearance

| Package | Purpose |
|---------|---------|
| `fonts-nasalization` (or manual install) | UI font — Nasalization Rg |
| Nerd Fonts (for waybar icons) | `󰕾 󰖁 󰻠 󰍛` icons in waybar |

### Optional

| Package | Purpose |
|---------|---------|
| `nm-applet` | Network Manager tray icon |
| `brightnessctl` | Keyboard brightness keys |
| `mpc` / `mpd` | Media key support |
| `flameshot` | Alternative screenshot tool (currently not functional on this setup) |
| `pavucontrol` | PulseAudio/PipeWire volume GUI (bound to waybar click) |

## XDG portal configuration

`xdg-desktop-portal-wlr` must be started before screen capture works.
It is started via sway's `exec` and routed via
`~/.config/xdg-desktop-portal/portals.conf`.

## Edge / Chrome GPU acceleration

Edge is launched via `~/bin/edge` with `--ozone-platform=x11` to work around
NVIDIA DMA-buf issues on Wayland. The XDG file picker
(`xdg-desktop-portal-gtk`) is configured to use software rendering via
`~/.config/systemd/user/xdg-desktop-portal-gtk.service.d/x11.conf` to avoid
GPU context crashes in the dialog.

## Key bindings

Press `Super+s` at any time for a full keybinding reference.
