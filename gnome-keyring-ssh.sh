#!/bin/sh
# Start the GNOME Keyring SSH agent component and export SSH_AUTH_SOCK
# so all sway processes (terminals, apps) inherit it.
#
# GDM auto-unlocks the keyring at login via pam_gnome_keyring.so, so once
# this runs, SSH keys added via ssh-add are available without passphrases.

eval $(gnome-keyring-daemon --start --components=ssh)
export SSH_AUTH_SOCK

# Also register with the systemd user session so processes started via
# systemd --user (e.g. xdg-desktop-portal) inherit the socket.
systemctl --user set-environment SSH_AUTH_SOCK="$SSH_AUTH_SOCK"
