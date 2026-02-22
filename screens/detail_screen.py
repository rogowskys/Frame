"""
Detail Screen - Show detailed album information
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
import os


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_album = None
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
        
        header.add_widget(back_btn)
        header.add_widget(Label())  # Spacer
        
        layout.add_widget(header)
        
        # Scroll view for content
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        self.content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(15)
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll.add_widget(self.content_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def set_album(self, album_data):
        """Set the album to display"""
        self.current_album = album_data
        Clock.schedule_once(self.load_details, 0.1)
    
    def load_details(self, dt):
        """Load and display album details"""
        self.content_layout.clear_widgets()
        
        if not self.current_album:
            return
        
        # Album cover and basic info section
        top_section = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(200),
            spacing=dp(20)
        )
        
        # Cover image
        cover_container = BoxLayout(size_hint=(None, 1), width=dp(200))
        cache_path = f"./cache/{self.current_album['id']}.jpg"
        if os.path.exists(cache_path):
            cover_img = Image(
                source=cache_path,
                allow_stretch=True,
                keep_ratio=True
            )
            cover_container.add_widget(cover_img)
        else:
            placeholder = Label(text='♪', font_size=dp(80))
            cover_container.add_widget(placeholder)
        
        top_section.add_widget(cover_container)
        
        # Basic info
        info_layout = BoxLayout(orientation='vertical', spacing=dp(8))
        
        title = Label(
            text=f"[b]{self.current_album['title']}[/b]",
            markup=True,
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(60),
            color=(1, 0.8, 0.2, 1),
            halign='left',
            valign='top'
        )
        title.bind(size=title.setter('text_size'))
        
        artist = Label(
            text=f"[b]Artist:[/b] {self.current_album['artist']}",
            markup=True,
            font_size=dp(16),
            size_hint=(1, None),
            height=dp(30),
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        artist.bind(size=artist.setter('text_size'))
        
        year = Label(
            text=f"[b]Year:[/b] {self.current_album.get('year', 'N/A')}",
            markup=True,
            font_size=dp(14),
            size_hint=(1, None),
            height=dp(25),
            color=(0.8, 0.8, 0.8, 1),
            halign='left',
            valign='middle'
        )
        year.bind(size=year.setter('text_size'))
        
        genres_text = ', '.join(self.current_album.get('genres', [])) or 'N/A'
        genres = Label(
            text=f"[b]Genres:[/b] {genres_text}",
            markup=True,
            font_size=dp(14),
            size_hint=(1, None),
            height=dp(25),
            color=(0.8, 0.8, 0.8, 1),
            halign='left',
            valign='middle'
        )
        genres.bind(size=genres.setter('text_size'))
        
        info_layout.add_widget(title)
        info_layout.add_widget(artist)
        info_layout.add_widget(year)
        info_layout.add_widget(genres)
        
        top_section.add_widget(info_layout)
        self.content_layout.add_widget(top_section)
        
        # Fetch and display detailed information
        from kivy.app import App
        app = App.get_running_app()
        if app.discogs:
            Clock.schedule_once(lambda dt: self.load_full_details(app.discogs), 0.2)
    
    def load_full_details(self, discogs_service):
        """Load full release details from Discogs"""
        release_id = self.current_album['id']
        details = discogs_service.get_release_details(release_id)
        
        if not details:
            return
        
        # Separator
        separator = Label(
            text='─' * 80,
            size_hint=(1, None),
            height=dp(20),
            color=(0.3, 0.3, 0.4, 1)
        )
        self.content_layout.add_widget(separator)
        
        # Additional details
        if details.get('label'):
            label_info = Label(
                text=f"[b]Label:[/b] {details['label']}",
                markup=True,
                font_size=dp(14),
                size_hint=(1, None),
                height=dp(25),
                color=(0.8, 0.8, 0.8, 1),
                halign='left',
                valign='middle'
            )
            label_info.bind(size=label_info.setter('text_size'))
            self.content_layout.add_widget(label_info)
        
        if details.get('country'):
            country_info = Label(
                text=f"[b]Country:[/b] {details['country']}",
                markup=True,
                font_size=dp(14),
                size_hint=(1, None),
                height=dp(25),
                color=(0.8, 0.8, 0.8, 1),
                halign='left',
                valign='middle'
            )
            country_info.bind(size=country_info.setter('text_size'))
            self.content_layout.add_widget(country_info)
        
        # Tracklist
        if details.get('tracklist'):
            tracklist_title = Label(
                text='[b]TRACKLIST[/b]',
                markup=True,
                font_size=dp(18),
                size_hint=(1, None),
                height=dp(40),
                color=(1, 0.8, 0.2, 1),
                halign='left',
                valign='middle'
            )
            tracklist_title.bind(size=tracklist_title.setter('text_size'))
            self.content_layout.add_widget(tracklist_title)
            
            for track in details['tracklist']:
                track_text = f"{track['position']}. {track['title']}"
                if track.get('duration'):
                    track_text += f" ({track['duration']})"
                
                track_label = Label(
                    text=track_text,
                    font_size=dp(12),
                    size_hint=(1, None),
                    height=dp(25),
                    color=(0.9, 0.9, 0.9, 1),
                    halign='left',
                    valign='middle'
                )
                track_label.bind(size=track_label.setter('text_size'))
                self.content_layout.add_widget(track_label)
    
    def go_back(self, instance):
        self.manager.current = 'collection'
