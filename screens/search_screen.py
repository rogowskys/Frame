"""
Search Screen - Search vinyl collection
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from screens.collection_screen import AlbumCard


class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Set background
        with layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint=(1, None), height=dp(60), padding=dp(10))
        
        back_btn = Button(
            text='← BACK',
            size_hint=(None, 1),
            width=dp(100),
            background_normal='',
            background_color=(0.2, 0.2, 0.3, 1),
            font_size=dp(16)
        )
        back_btn.bind(on_press=self.go_back)
        
        title = Label(
            text='[b]SEARCH[/b]',
            markup=True,
            font_size=dp(24),
            color=(1, 0.8, 0.2, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        layout.add_widget(header)
        
        # Search box
        search_container = BoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        
        self.search_input = TextInput(
            hint_text='Search by artist, album, or genre...',
            font_size=dp(16),
            multiline=False,
            size_hint=(0.75, 1),
            background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0.8, 0.2, 1),
            padding=[dp(15), dp(15)],
            keyboard_mode='managed'
        )
        self.search_input.bind(text=self.on_search_text)
        self.search_input.bind(focus=self.on_search_focus)
        
        search_btn = Button(
            text='SEARCH',
            size_hint=(0.25, 1),
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1),
            font_size=dp(14)
        )
        search_btn.bind(on_press=self.do_search)
        
        search_container.add_widget(self.search_input)
        search_container.add_widget(search_btn)
        
        layout.add_widget(search_container)
        
        # Results label
        self.results_label = Label(
            text='Enter search query above',
            size_hint=(1, None),
            height=dp(30),
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.results_label)
        
        # Scroll view for results
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(10))
        
        self.results_grid = GridLayout(
            cols=4,
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None
        )
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        
        scroll.add_widget(self.results_grid)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def on_search_focus(self, instance, value):
        """Handle focus change to show/hide keyboard"""
        if value:  # Gained focus
            instance.focus = True
    
    def on_search_text(self, instance, value):
        """Auto-search as user types (with debounce)"""
        if hasattr(self, '_search_clock'):
            self._search_clock.cancel()
        
        if len(value) >= 2:
            self._search_clock = Clock.schedule_once(lambda dt: self.do_search(None), 0.5)
    
    def do_search(self, instance):
        """Perform search"""
        query = self.search_input.text.strip()
        
        if not query:
            self.results_label.text = 'Enter search query above'
            self.results_grid.clear_widgets()
            return
        
        self.results_grid.clear_widgets()
        
        from kivy.app import App
        app = App.get_running_app()
        if not app.discogs or not app.discogs.collection:
            self.results_label.text = 'Collection not loaded'
            return
        
        results = app.discogs.search_collection(query)
        
        if results:
            self.results_label.text = f'Found {len(results)} result(s)'
            for album in results:
                card = AlbumCard(album, self.show_detail)
                self.results_grid.add_widget(card)
        else:
            self.results_label.text = f'No results found for "{query}"'
    
    def show_detail(self, album_data):
        """Navigate to detail screen"""
        detail_screen = self.manager.get_screen('detail')
        detail_screen.set_album(album_data)
        self.manager.current = 'detail'
    
    def on_enter(self):
        """Called when entering the screen"""
        # Auto-focus search input to show keyboard
        Clock.schedule_once(lambda dt: setattr(self.search_input, 'focus', True), 0.1)
    
    def on_collection_loaded(self):
        """Called when collection is loaded"""
        pass
    
    def go_back(self, instance):
        self.manager.current = 'home'
