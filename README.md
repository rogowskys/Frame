# 🎵 Vinyl Collection App

A modern touchscreen interface for browsing and managing your vinyl record collection on Raspberry Pi. Integrates with Discogs API to display your collection with album artwork, detailed information, and a fun "Jukebox Mode" for random album selection.

![Resolution](https://img.shields.io/badge/Resolution-800x480-blue)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)

## ✨ Features

- **Browse Collection**: Scrollable grid view of your entire vinyl collection with album artwork
- **Album Details**: View comprehensive information including tracklist, label, country, and release year
- **Search**: Quick search by artist, album title, or genre
- **Jukebox Mode**: Randomly pick albums based on:
  - Mood (energetic, chill, melancholic, happy, dark, groovy)
  - Genre
  - Complete random selection
- **Touch-Optimized**: Designed for 7" 800x480 capacitive touchscreen
- **Modern UI**: Sleek dark theme with smooth animations
- **Kiosk Mode**: Full kiosk functionality for dedicated display:
  - Hidden cursor
  - Screen blanking disabled
  - ESC key disabled (emergency exit: Shift+ESC+Q)
  - Auto-restart on crash
  - Auto-start on boot

## 🔧 Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- 7" 800x480 IPS Display with 5-point capacitive touch
- Internet connection (for Discogs API and album covers)

## 📦 Installation

> **💡 Quick Start for Kiosk Mode?** See [KIOSK-SETUP.md](KIOSK-SETUP.md) for a streamlined kiosk setup guide!

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install -y pkg-config libgl1-mesa-dev libgles2-mesa-dev
sudo apt-get install -y python3-setuptools libgstreamer1.0-dev git-core
sudo apt-get install -y gstreamer1.0-plugins-{bad,base,good,ugly}
sudo apt-get install -y gstreamer1.0-{omx,alsa} python3-dev libmtdev-dev
sudo apt-get install -y xclip xsel libjpeg-dev
```

### 2. Clone or Set Up Project

```bash
cd /home/pi
git clone <your-repo-url> vinyl-collection
# OR if you copied files manually, navigate to the project directory
cd vinyl-collection
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Discogs API

1. Get your Discogs API token:
   - Go to https://www.discogs.com/settings/developers
   - Generate a new personal access token
   
2. Edit `config.ini`:
   ```bash
   nano config.ini
   ```
   
3. Add your credentials:
   ```ini
   [Discogs]
   user_token = YOUR_ACTUAL_TOKEN_HERE
   username = YOUR_DISCOGS_USERNAME
   ```

## 🚀 Running the App

### Standard Mode (for testing):

```bash
source venv/bin/activate
python main.py
```

To exit: Press **Shift + ESC + Q** simultaneously

### Kiosk Mode (fullscreen, no cursor, auto-restart):

```bash
./start.sh
```

The app runs in kiosk mode by default with:
- Fullscreen display (no window borders)
- Hidden mouse cursor
- Screen blanking disabled
- Auto-restart on crash
- ESC key disabled (emergency exit: Shift + ESC + Q)

### Auto-start on Boot (Kiosk Mode)

To make the app start automatically in kiosk mode when Raspberry Pi boots:

**Method 1: Desktop Autostart (if using Raspberry Pi OS Desktop)**

1. Create autostart directory and file:
   ```bash
   mkdir -p ~/.config/autostart
   nano ~/.config/autostart/vinyl-collection.desktop
   ```

2. Add this content:
   ```ini
   [Desktop Entry]
   Type=Application
   Name=Vinyl Collection Kiosk
   Exec=/home/pi/vinyl-collection/start.sh
   Terminal=false
   X-GNOME-Autostart-enabled=true
   ```

**Method 2: Systemd Service (more robust)**

1. Copy the service file:
   ```bash
   sudo cp vinyl-collection.service.example /etc/systemd/system/vinyl-collection.service
   ```

2. Edit paths if needed:
   ```bash
   sudo nano /etc/systemd/system/vinyl-collection.service
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable vinyl-collection.service
   sudo systemctl start vinyl-collection.service
   ```

4. Check status:
   ```bash
   sudo systemctl status vinyl-collection.service
   ```

**Method 3: Boot to Kiosk (no desktop environment)**

For truly headless kiosk mode without desktop environment:

1. Install minimal X server:
   ```bash
   sudo apt-get install --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox
   ```

2. Edit ~/.xinitrc:
   ```bash
   echo "exec /home/pi/vinyl-collection/start.sh" > ~/.xinitrc
   ```

3. Auto-start X on boot:
   ```bash
   echo "[[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]] && startx" >> ~/.bash_profile
   ```

## 📱 Usage

### Home Screen
- **Browse Collection**: View all your vinyl records
- **Search**: Find specific albums
- **Jukebox Mode**: Random album picker

### Collection Browser
kiosk_mode = true      # Enable kiosk features
hide_cursor = true     # Hide mouse cursor

[App]
cache_covers = true
cache_dir = ./cache
```

### Kiosk Mode Settings

- **kiosk_mode**: Enable/disable kiosk features
- **hide_cursor**: Show/hide mouse cursor
- **fullscreen**: Run in fullscreen mode
- **Emergency Exit**: Press **Shift + ESC + Q** together to exitiew album artwork, tracklist, and metadata
- Swipe to navigate back

### Search
- Type to search (auto-completes as you type)
- Search by artist, album, or genre
- Tap results to view details

### Jukebox Mode
- Pick a mood for themed selection
- Browse by specific genre
- "Surprise Me" for completely random pick
- View details of selected album

## 🎨 Configuration

Edit `config.ini` to customize:

```ini
[Display]
width = 800
height = 480
fullscreen = true

[App]
cache_covers = true
cache_dir = ./cache
```

## 🗂️ Project Structure

```
vinyl-collection/
├── main.py                    # Main application entry point
├── discogs_service.py         # Discogs API integration
├── requirements.txt           # Python dependencies
├── config.ini                 # Configuration file
├── setup.sh                   # Automated setup script
├── start.sh                   # Kiosk mode startup script
├── kiosk-config.sh           # Kiosk configuration helper
├── README.md                  # Main documentation
├── KIOSK-SETUP.md            # Kiosk mode guide
├── vinyl-collection.service.example  # Systemd service
├── screens/                   # UI screens
│   ├── __init__.py
│   ├── home_screen.py        # Main menu
│   ├── collection_screen.py  # Collection browser
│   ├── detail_screen.py      # Album details
│   ├── search_screen.py      # Search interface
│   └── jukebox_screen.py     # Jukebox mode
└── cache/                     # Album cover cache (auto-created)
```

## 🐛 Troubleshooting

### Display Issues

If the display doesn't show correctly:

1. Check display drivers are installed
2. Verify resolution in config.ini matches your display
3. Try disabling fullscreen temporarily

### Discogs Connection

If you see "Failed to authenticate":

1. Verify your token is correct in config.ini
2. Check internet connection
3. Ensure your Discogs username is correct

### Touch Not Working

1. Verify touch drivers are installed
2. Calibrate touchscreen if needed:
   ```bash
   sudo apt-get install xinput-calibrator
   xinput_calibrator
   ```
5. Boot to console + X only (no desktop environment) for maximum performance

### Kiosk Mode Issues

**App won't exit:**
- Use emergency exit: **Shift + ESC + Q**
- Or SSH in and: `pkill -9 python`
- Or reboot: `sudo reboot`

**Screen blanking:**
- The setup script should disable this
- Manual fix: `xset s off && xset -dpms && xset s noblank`

**Cursor visible:**
- Check `kiosk_mode = true` in config.ini
- Ensure unclutter is installed: `sudo apt-get install unclutter`

**App crashes and doesn't restart:**
- Check start.sh has the while loop
- Or use systemd service with `Restart=on-failure`

### Performance

For better performance on Raspberry Pi:

1. Use Raspberry Pi 4 for best experience
2. Overclock if needed (safely)
3. Reduce cache size if storage is limited
4. Close unnecessary background applications

## 📝 Tips

- **First Load**: The first time you run the app, it will take a moment to load your entire collection
- **Album Covers**: Covers are cached locally after first download for faster loading
- **Touch Targets**: All buttons are sized for easy finger touch (minimum 50dp)
- **Network**: Ensure stable internet connection for best experience

## 🔮 Future Enhancements

Possible additions:
- Statistics and collection insights
- Export/backup collection data
- Multiple user profiles
- Custom mood/genre mappings
- Integration with music streaming services
- Wishlist/want list support

## 📄 License

This project is open source. Feel free to modify and enhance!

## 🙏 Credits

- Built with [Kivy](https://kivy.org/) framework
- Powered by [Discogs API](https://www.discogs.com/developers/)
- Designed for Raspberry Pi enthusiasts

---

**Enjoy your vinyl collection! 🎶**
