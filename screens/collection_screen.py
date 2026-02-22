"""
Collection Screen - Browse vinyl collection
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock


class AlbumCard(BoxLayout):
    def __init__(self, album_data, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(160), dp(200))
        self.padding = dp(5)
        self.spacing = dp(5)
        self.album_data = album_data
        self.callback = callback
        
        # Background
        with self.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Album cover button
        cover_btn = Button(
            size_hint=(1, 0.7),
            background_normal='',
            background_color=(0.2, 0.2, 0.25, 1)
        )
        
        if album_data.get('thumb'):
            cover_img = AsyncImage(
                source=album_data['thumb'],
                allow_stretch=True,
                keep_ratio=True
            )
            cover_btn.add_widget(cover_img)
        else:
            placeholder = Label(text='♪', font_size=dp(40))
            cover_btn.add_widget(placeholder)
        
        cover_btn.bind(on_press=lambda x: self.callback(album_data))
        self.add_widget(cover_btn)
        
        # Album info
        info_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=dp(2))
        
        title = Label(
            text=album_data['title'][:25] + '...' if len(album_data['title']) > 25 else album_data['title'],
            font_size=dp(11),
            bold=True,
            size_hint=(1, 0.6),
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        
        artist = Label(
            text=album_data['artist'][:25] + '...' if len(album_data['artist']) > 25 else album_data['artist'],
            font_size=dp(9),
            size_hint=(1, 0.4),
            color=(0.7, 0.7, 0.7, 1),
            halign='center',
            valign='middle'
        )
        artist.bind(size=artist.setter('text_size'))
        
        info_layout.add_widget(title)
        info_layout.add_widget(artist)
        self.add_widget(info_layout)
    
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size


class CollectionScreen(Screen):
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
            text='[b]MY COLLECTION[/b]',
            markup=True,
            font_size=dp(24),
            color=(1, 0.8, 0.2, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        layout.add_widget(header)
        
        # Scroll view for albums
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=dp(10))
        
        self.albums_grid = GridLayout(
            cols=4,
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None
        )
        self.albums_grid.bind(minimum_height=self.albums_grid.setter('height'))
        
        scroll.add_widget(self.albums_grid)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def on_pre_enter(self):
        """Load albums when entering screen"""
        Clock.schedule_once(self.load_albums, 0.1)
    
    def load_albums(self, dt):
        """Load and display albums"""
        self.albums_grid.clear_widgets()
        
        app = self.manager.get_screen('home').get_root_window().children[0].app
        if app.discogs and app.discogs.collection:
            for album in app.discogs.collection:
                card = AlbumCard(album, self.show_detail)
                self.albums_grid.add_widget(card)
    
    def on_collection_loaded(self):
        """Called when collection is loaded"""
        if self.manager.current == 'collection':
            Clock.schedule_once(self.load_albums, 0.1)
    
    def show_detail(self, album_data):
        """Navigate to detail screen"""
        detail_screen = self.manager.get_screen('detail')
        detail_screen.set_album(album_data)
        self.manager.current = 'detail'
    
    def go_back(self, instance):
        self.manager.current = 'home'
