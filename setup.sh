#!/bin/bash
# Vinyl Collection App - Setup Script for Raspberry Pi

echo "================================"
echo "Vinyl Collection App Setup"
echo "================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi/Linux"
fi

echo "Step 1: Installing system dependencies..."
echo "This may take several minutes..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    pkg-config libgl1-mesa-dev libgles2-mesa-dev \
    python3-setuptools libgstreamer1.0-dev git-core \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
    gstreamer1.0-omx gstreamer1.0-alsa python3-dev libmtdev-dev \
    xclip xsel libjpeg-dev unclutter x11-xserver-utils

echo "Step 1b: Configuring kiosk mode settings..."
# Disable screen blanking
sudo raspi-config nonint do_blanking 1
# Disable screensaver
if [ ! -f ~/.xsessionrc ]; then
    echo "xset s off" >> ~/.xsessionrc
    echo "xset -dpms" >> ~/.xsessionrc
    echo "xset s noblank" >> ~/.xsessionrc
fi

echo ""
echo "Step 2: Creating Python virtual environment..."
python3 -m venv venv

echo ""
echo "Step 3: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Creating cache directory..."
mkdir -p cache

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.ini with your Discogs credentials"
echo "   - Get token from: https://www.discogs.com/settings/developers"
echo "   - nano config.ini"
echo ""
echo "2. Run the app:"
echo "   ./start.sh"
echo ""
echo "3. (Optional) Set up auto-start on boot - see README.md"
echo ""
