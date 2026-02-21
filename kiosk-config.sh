#!/bin/bash
# Configure Raspberry Pi for Kiosk Mode

echo "================================"
echo "Kiosk Mode Configuration"
echo "================================"
echo ""

echo "This script will configure your Raspberry Pi for kiosk mode:"
echo "  - Disable screen blanking"
echo "  - Disable screensaver"
echo "  - Hide cursor when idle"
echo "  - Optimize boot settings"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Step 1: Disabling screen blanking..."
sudo raspi-config nonint do_blanking 1

echo ""
echo "Step 2: Creating X session config..."
cat > ~/.xsessionrc << 'EOF'
# Disable screen blanking and power management
xset s off
xset -dpms
xset s noblank

# Hide cursor after 0.1 seconds of inactivity
unclutter -idle 0.1 -root &
EOF

echo ""
echo "Step 3: Configuring console blanking..."
# Disable console blanking
sudo bash -c 'echo -e "\n# Disable console blanking\nconsoleblank=0" >> /boot/cmdline.txt' 2>/dev/null || true

echo ""
echo "Step 4: Optimizing boot (optional)..."
read -p "Hide boot messages for cleaner startup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo raspi-config nonint do_boot_splash 0
    echo "Boot splash enabled"
fi

echo ""
echo "Step 5: Setting up crash recovery..."
cat > ~/restart-app.sh << 'EOF'
#!/bin/bash
# Simple watchdog script
while true; do
    if ! pgrep -f "python.*main.py" > /dev/null; then
        echo "App not running, starting..."
        cd ~/vinyl-collection && ./start.sh &
    fi
    sleep 30
done
EOF
chmod +x ~/restart-app.sh

echo ""
echo "✅ Kiosk mode configuration complete!"
echo ""
echo "Changes will take effect on next reboot."
echo ""
echo "Recommended: Set up auto-start (see README.md)"
echo ""
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo reboot
fi
