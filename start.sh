#!/bin/bash
# Startup script for Vinyl Collection App in Kiosk Mode

# Navigate to app directory
cd "$(dirname "$0")"

# Kiosk mode: Disable screen blanking and hide cursor
export DISPLAY=:0
xset s off
xset -dpms
xset s noblank

# Hide cursor (will be hidden by app, but this is backup)
unclutter -idle 0.1 -root &

# Activate virtual environment
source venv/bin/activate

# Run the app (loop to restart on crash in kiosk mode)
while true; do
    python main.py
    sleep 2
done
