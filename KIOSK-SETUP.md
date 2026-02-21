# 🖥️ Kiosk Mode Quick Setup Guide

This guide will help you set up the Vinyl Collection App in true kiosk mode on your Raspberry Pi.

## What is Kiosk Mode?

Kiosk mode means the app runs fullscreen with:
- ✅ No desktop environment visible
- ✅ Hidden mouse cursor
- ✅ Screen never blanks/sleeps
- ✅ ESC key disabled (emergency exit only)
- ✅ Auto-restart on crashes
- ✅ Auto-start on boot

## Quick Setup (5 minutes)

### 1. Run Setup Script
```bash
cd ~/vinyl-collection
./setup.sh
```

### 2. Configure Kiosk Mode
```bash
./kiosk-config.sh
```

### 3. Add Your Discogs Credentials
```bash
nano config.ini
```
Add your token and username from https://www.discogs.com/settings/developers

### 4. Set Auto-Start
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/vinyl-collection.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Vinyl Collection
Exec=/home/pi/vinyl-collection/start.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
```

### 5. Reboot
```bash
sudo reboot
```

## Manual Testing

Before setting up auto-start, test the app:

```bash
cd ~/vinyl-collection
./start.sh
```

**To exit:** Press **Shift + ESC + Q** simultaneously

## Kiosk Mode Features

| Feature | Status | How to Verify |
|---------|--------|---------------|
| Fullscreen | ✅ Auto | Should fill entire screen |
| Hidden Cursor | ✅ Auto | Move mouse - cursor invisible |
| Screen Never Blanks | ✅ Auto | Leave running for hours |
| ESC Disabled | ✅ Auto | Press ESC - nothing happens |
| Emergency Exit | ⌨️ Shift+ESC+Q | All 3 keys together |
| Auto-Restart | ✅ Auto | Kill app - restarts in 2s |
| Auto-Start | ⚙️ Configure | Reboots into app |

## Boot Options

### Option A: Desktop Environment (easiest)
- Boots to desktop, then app starts
- Uses autostart desktop file
- Easy to troubleshoot
- Slightly slower boot

### Option B: Minimal X (fastest)
- Boots directly to app
- No desktop environment
- Fastest performance
- Requires SSH for maintenance

To enable minimal X:
```bash
# Install minimal X
sudo apt-get install --no-install-recommends xserver-xorg xinit openbox

# Auto-start app
echo 'exec ~/vinyl-collection/start.sh' > ~/.xinitrc

# Auto-start X on boot
echo '[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && startx' >> ~/.bash_profile
```

### Option C: Systemd Service (most robust)
- Runs as a system service
- Auto-restart on failure
- Works without user login
- Best for unattended kiosks

```bash
sudo cp vinyl-collection.service.example /etc/systemd/system/vinyl-collection.service
sudo systemctl enable vinyl-collection.service
sudo systemctl start vinyl-collection.service
```

## Emergency Access

If the app is stuck or you need to access the Pi:

### Method 1: SSH (recommended)
```bash
ssh pi@raspberrypi.local
pkill -9 python
```

### Method 2: Emergency Exit
Press **Shift + ESC + Q** together

### Method 3: Disable Auto-Start
```bash
# SSH in first
rm ~/.config/autostart/vinyl-collection.desktop
# OR
sudo systemctl disable vinyl-collection.service
sudo reboot
```

### Method 4: Boot to Console
Add this to `/boot/cmdline.txt`:
```
systemd.unit=multi-user.target
```

## Troubleshooting

### Screen Blanks After Time
```bash
# Run these commands
xset s off
xset -dpms
xset s noblank

# Or run kiosk-config.sh again
./kiosk-config.sh
```

### Cursor Still Visible
```bash
# Install unclutter
sudo apt-get install unclutter

# Or manually hide
unclutter -idle 0.1 -root &
```

### App Doesn't Auto-Start
```bash
# Check if service is enabled
systemctl is-enabled vinyl-collection.service

# Check if desktop file exists
ls -la ~/.config/autostart/

# Check logs
journalctl -u vinyl-collection.service -f
```

### App Crashes
```bash
# Check Python errors
journalctl -u vinyl-collection.service -n 50

# Test manually
cd ~/vinyl-collection
source venv/bin/activate
python main.py
```

### Can't Exit App
- Press: **Shift + ESC + Q** together
- Or SSH and: `pkill -9 python`
- Or force reboot: Hold power button

## Performance Tuning

### Faster Boot
```bash
# Disable unnecessary services
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service
sudo systemctl disable avahi-daemon.service

# Reduce boot delay
sudo nano /boot/config.txt
# Add: boot_delay=0
```

### More Memory
```bash
# Reduce GPU memory if not using HDMI-CEC
sudo nano /boot/config.txt
# Change: gpu_mem=16
```

### Overclock (Pi 4)
```bash
sudo raspi-config
# Performance Options > Overclock
# Choose: Modest or Medium
```

## Maintenance Mode

To temporarily disable kiosk mode for maintenance:

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Stop the app
pkill python

# Disable auto-start temporarily
sudo systemctl stop vinyl-collection.service

# Do your maintenance...

# Re-enable when done
sudo systemctl start vinyl-collection.service
```

## Checklist

Before deploying as a permanent kiosk:

- [ ] Discogs credentials added to config.ini
- [ ] App tested and loads collection successfully
- [ ] Touchscreen calibrated (if needed)
- [ ] Auto-start configured
- [ ] Emergency exit tested (Shift+ESC+Q)
- [ ] SSH enabled for remote access
- [ ] Static IP set (optional but recommended)
- [ ] Pi secured in case/mount
- [ ] Power supply adequate (3A+ recommended)
- [ ] Network connection reliable

## Remote Management

### Enable SSH (if not already)
```bash
sudo raspi-config
# Interface Options > SSH > Enable
```

### Set Static IP (recommended)
```bash
sudo nano /etc/dhcpcd.conf
```

Add:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

### Update Remotely
```bash
ssh pi@192.168.1.100
cd ~/vinyl-collection
git pull  # if using git
sudo systemctl restart vinyl-collection.service
```

## Need Help?

- Check main [README.md](README.md) for detailed documentation
- Review logs: `journalctl -u vinyl-collection.service`
- Test in non-kiosk mode first: `python main.py`
- Ensure Discogs API credentials are correct

---

**You're all set! Reboot and enjoy your vinyl collection kiosk! 🎵**
