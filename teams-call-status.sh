#!/bin/bash
# Outputs a microphone icon when a Teams call is active (idle is inhibited).
[ -f /tmp/teams-in-call ] && echo "󰍬 In call"
