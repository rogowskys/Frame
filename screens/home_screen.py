"""
Home Screen - Main menu interface
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class MenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.15, 0.15, 0.2, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(24)
        self.size_hint = (1, None)
        self.height = dp(100)
        self.bold = True


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Set background
        with layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Title
        self.title_label = Label(
            text='[b]VINYL COLLECTION[/b]',
            markup=True,
            font_size=dp(24),
            size_hint=(1, 0.2),
            color=(1, 0.8, 0.2, 1)
        )
        layout.add_widget(self.title_label)
        
        # Status label
        self.status_label = Label(
            text='Connecting to Discogs...',
            font_size=dp(14),
            size_hint=(1, 0.1),
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.status_label)
        
        # Menu buttons
        buttons_layout = GridLayout(cols=1, spacing=dp(15), size_hint=(1, 0.7))
        
        browse_btn = MenuButton(text='BROWSE COLLECTION')
        browse_btn.bind(on_press=self.goto_collection)
        buttons_layout.add_widget(browse_btn)
        
        search_btn = MenuButton(text='SEARCH')
        search_btn.bind(on_press=self.goto_search)
        buttons_layout.add_widget(search_btn)
        
        jukebox_btn = MenuButton(text='JUKEBOX MODE')
        jukebox_btn.bind(on_press=self.goto_jukebox)
        buttons_layout.add_widget(jukebox_btn)
        
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def on_collection_loaded(self):
        """Called when collection is loaded"""
        from kivy.app import App
        app = App.get_running_app()
        if app.discogs and app.discogs.collection:
            count = len(app.discogs.collection)
            username = app.discogs.username
            self.title_label.text = f'[b]{username.upper()}\'S VINYL COLLECTION[/b]'
            self.status_label.text = f'> {count} records loaded'
        else:
            self.status_label.text = '! No records found'
    
    def goto_collection(self, instance):
        self.manager.current = 'collection'
    
    def goto_search(self, instance):
        self.manager.current = 'search'
    
    def goto_jukebox(self, instance):
        self.manager.current = 'jukebox'
