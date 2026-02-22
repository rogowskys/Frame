"""
Vinyl Collection App - Main Application
Raspberry Pi 7" Touchscreen Interface
"""
import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
import configparser
import threading

from discogs_service import DiscogsService
from screens.home_screen import HomeScreen
from screens.collection_screen import CollectionScreen
from screens.detail_screen import DetailScreen
from screens.search_screen import SearchScreen
from screens.jukebox_screen import JukeboxScreen


class VinylApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.discogs = None
        self.config_parser = None
        
    def build(self):
        # Load configuration
        self.load_config()
        
        # Kiosk mode configuration
        from kivy.config import Config
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.set('graphics', 'window_state', 'maximized')
        Config.set('kivy', 'exit_on_escape', '0')  # Disable ESC to exit
        Config.set('kivy', 'keyboard_mode', 'system')  # Enable virtual keyboard
        
        # Set window size for Raspberry Pi display
        Window.size = (800, 480)
        if self.config_parser.getboolean('Display', 'fullscreen', fallback=True):
            Window.fullscreen = 'auto'
        
        # Hide cursor in kiosk mode
        if self.config_parser.getboolean('Display', 'kiosk_mode', fallback=True):
            Window.show_cursor = False
            # Bind ESC+Q+Shift as emergency exit
            Window.bind(on_keyboard=self.on_keyboard)
        
        # Initialize screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CollectionScreen(name='collection'))
        sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(JukeboxScreen(name='jukebox'))
        
        # Initialize Discogs service in background
        Clock.schedule_once(self.init_discogs, 0.5)
        
        return sm
    
    def load_config(self):
        """Load configuration from config.ini"""
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read('config.ini')
    
    def init_discogs(self, dt):
        """Initialize Discogs service"""
        try:
            token = self.config_parser.get('Discogs', 'user_token')
            username = self.config_parser.get('Discogs', 'username')
            cache_dir = self.config_parser.get('App', 'cache_dir', fallback='./cache')
            
            self.discogs = DiscogsService(token, username, cache_dir)
            
            if self.discogs.authenticate():
                print("✓ Authenticated with Discogs")
                # Load collection in background
                Clock.schedule_once(self.load_collection, 0.1)
            else:
                print("✗ Failed to authenticate with Discogs")
        except Exception as e:
            print(f"Configuration error: {e}")
            print("Please update config.ini with your Discogs credentials")
    
    def load_collection(self, dt):
        """Load user's vinyl collection in background thread"""
        print("Loading collection...")
        
        def fetch_in_background():
            self.discogs.get_collection()
            Clock.schedule_once(self.on_collection_loaded, 0)
        
        thread = threading.Thread(target=fetch_in_background, daemon=True)
        thread.start()
    
    def on_collection_loaded(self, dt):
        """Called when collection loading is complete"""
        print(f"✓ Loaded {len(self.discogs.collection)} records")
        
        # Notify screens that collection is loaded
        for screen in self.root.screens:
            if hasattr(screen, 'on_collection_loaded'):
                screen.on_collection_loaded()
        
        # Start downloading covers in background
        Clock.schedule_once(self.download_covers_background, 1.0)
    
    def download_covers_background(self, dt):
        """Download all album covers in background"""
        def download_task():
            from kivy.clock import Clock
            def progress(current, total, downloaded, skipped):
                # Schedule UI update on main thread
                def _update(dt):
                    from kivy.app import App
                    app = App.get_running_app()
                    try:
                        home = app.root.get_screen('home')
                        home.status_label.text = f'Downloading covers: {current}/{total} ({downloaded} new, {skipped} cached)'
                    except Exception:
                        pass
                Clock.schedule_once(_update, 0)

            # Prewarm 24 covers for quick startup, then continue
            self.discogs.download_all_covers(progress_callback=progress, prewarm_count=24)

            # Final UI completion message
            def _done(dt):
                from kivy.app import App
                app = App.get_running_app()
                try:
                    home = app.root.get_screen('home')
                    home.status_label.text = f'✓ Covers cached'
                except Exception:
                    pass
            Clock.schedule_once(_done, 0)

        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Emergency exit: ESC + Shift + Q"""
        if key == 27 and 'shift' in modifier and codepoint == 'q':  # ESC+Shift+Q
            print("Emergency exit triggered")
            self.stop()
            return True
        return False


if __name__ == '__main__':
    VinylApp().run()
