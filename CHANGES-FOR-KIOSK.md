# Changes Made for Kiosk Mode

This document summarizes all the changes made to enable proper kiosk mode functionality.

## What Changed

### 1. **main.py** - Application Core
- ✅ Disabled ESC key exit (`exit_on_escape = 0`)
- ✅ Added cursor hiding based on config
- ✅ Added emergency exit combo: **Shift + ESC + Q**
- ✅ Window binding for keyboard events

### 2. **config.ini** - Configuration
- ✅ Added `kiosk_mode = true` setting
- ✅ Added `hide_cursor = true` setting
- ✅ Fullscreen enabled by default

### 3. **start.sh** - Startup Script
- ✅ Disables screen blanking (xset commands)
- ✅ Hides cursor with unclutter
- ✅ Auto-restart loop (app restarts on crash)
- ✅ Sets DISPLAY environment variable

### 4. **setup.sh** - Installation Script
- ✅ Installs `unclutter` (cursor hiding)
- ✅ Installs `x11-xserver-utils` (xset commands)
- ✅ Disables screen blanking via raspi-config
- ✅ Creates ~/.xsessionrc with display settings

### 5. **New Files Created**

#### **kiosk-config.sh** - Kiosk Configuration Helper
- Interactive script to configure Raspberry Pi for kiosk mode
- Disables screen blanking
- Configures X session
- Optimizes boot settings
- Creates watchdog script

#### **KIOSK-SETUP.md** - Complete Kiosk Guide
- Step-by-step kiosk setup instructions
- Three boot options (desktop/minimal/systemd)
- Troubleshooting guide
- Emergency access methods
- Performance tuning tips
- Remote management instructions

#### **vinyl-collection.service.example** - Systemd Service
- Service file for running as systemd service
- Auto-restart on failure
- Proper environment variables
- User/group settings

### 6. **README.md** - Documentation Updates
- ✅ Kiosk mode features highlighted
- ✅ Emergency exit instructions
- ✅ Auto-start methods (3 options)
- ✅ Kiosk troubleshooting section
- ✅ Link to KIOSK-SETUP.md

## Key Features Enabled

| Feature | How It Works | Files Modified |
|---------|--------------|----------------|
| **Hidden Cursor** | Kivy `Window.show_cursor = False` + unclutter | main.py, start.sh |
| **No Screen Blanking** | xset commands + raspi-config | start.sh, setup.sh, kiosk-config.sh |
| **ESC Disabled** | Kivy config `exit_on_escape = 0` | main.py |
| **Emergency Exit** | Shift+ESC+Q keyboard handler | main.py |
| **Auto-Restart** | While loop in start.sh | start.sh |
| **Auto-Start** | Desktop autostart or systemd | vinyl-collection.service.example |
| **Crash Recovery** | Systemd `Restart=on-failure` | vinyl-collection.service.example |

## Emergency Exit

The app can be exited using:
- **Keyboard**: Press **Shift + ESC + Q** simultaneously
- **SSH**: `ssh pi@raspberrypi.local` then `pkill -9 python`
- **Force Reboot**: Hold power button for 5 seconds

## Configuration Options

In `config.ini`:

```ini
[Display]
kiosk_mode = true    # Enable/disable kiosk features
hide_cursor = true   # Show/hide mouse cursor
fullscreen = true    # Run in fullscreen
```

## Auto-Start Options

### Option 1: Desktop Autostart (Easiest)
- File: `~/.config/autostart/vinyl-collection.desktop`
- Starts after desktop loads
- Easy to disable

### Option 2: Systemd Service (Robust)
- File: `/etc/systemd/system/vinyl-collection.service`
- Starts before user login
- Auto-restart on crash
- Best for production

### Option 3: Minimal X (Fastest)
- File: `~/.xinitrc` + `~/.bash_profile`
- No desktop environment
- Fastest boot
- Requires SSH for access

## Testing Kiosk Mode

### Quick Test
```bash
cd ~/vinyl-collection
./start.sh
```

The app should:
1. Fill the entire screen
2. Hide the cursor after movement
3. Not exit when pressing ESC
4. Exit when pressing Shift+ESC+Q together
5. Restart automatically if killed

### Full Test Checklist
- [ ] App starts fullscreen
- [ ] Cursor is hidden
- [ ] ESC key does not exit
- [ ] Shift+ESC+Q exits app
- [ ] Screen does not blank after 10 minutes
- [ ] App restarts after crash (kill it with `pkill python`)
- [ ] Collection loads from Discogs
- [ ] Touchscreen works correctly
- [ ] All screens (browse, search, jukebox) work

## Comparison: Before vs After

### Before (Standard Mode)
- Runs in window
- Cursor visible
- ESC exits immediately
- No auto-restart
- Manual start required
- Screen may blank

### After (Kiosk Mode)
- ✅ Runs fullscreen
- ✅ Cursor hidden
- ✅ ESC disabled (emergency exit only)
- ✅ Auto-restart on crash
- ✅ Auto-start on boot
- ✅ Screen never blanks
- ✅ Production-ready

## Files Summary

```
New Files:
├── kiosk-config.sh              # Kiosk configuration script
├── KIOSK-SETUP.md              # Kiosk setup guide
├── CHANGES-FOR-KIOSK.md        # This file
└── vinyl-collection.service.example  # Systemd service

Modified Files:
├── main.py                      # Added kiosk features
├── config.ini                   # Added kiosk settings
├── start.sh                     # Added kiosk startup
├── setup.sh                     # Added kiosk packages
└── README.md                    # Added kiosk docs
```

## Next Steps

1. **Test the app** in standard mode first:
   ```bash
   python main.py
   ```

2. **Test kiosk mode** with start.sh:
   ```bash
   ./start.sh
   ```

3. **Configure auto-start** using your preferred method from [KIOSK-SETUP.md](KIOSK-SETUP.md)

4. **Reboot and enjoy** your dedicated vinyl collection kiosk!

## Support

- Main docs: [README.md](README.md)
- Kiosk guide: [KIOSK-SETUP.md](KIOSK-SETUP.md)
- Emergency exit: **Shift + ESC + Q**

---

**Your vinyl collection app is now kiosk-ready! 🎵**
