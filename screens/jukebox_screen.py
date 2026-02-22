"""
Jukebox Screen - Random album picker based on mood/genre
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
from kivy.animation import Animation


class MoodButton(Button):
    def __init__(self, mood, emoji, color, **kwargs):
        super().__init__(**kwargs)
        self.mood = mood
        self.text = f'{emoji}\n{mood.upper()}'
        self.background_normal = ''
        self.background_color = color
        self.font_size = dp(16)
        self.bold = True
        self.size_hint = (None, None)
        self.size = (dp(110), dp(90))


class JukeboxScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_selection = None
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
            text='[b]JUKEBOX MODE[/b]',
            markup=True,
            font_size=dp(24),
            color=(1, 0.8, 0.2, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        layout.add_widget(header)
        
        # Instructions
        instructions = Label(
            text='Pick a mood or genre for a random album selection',
            size_hint=(1, None),
            height=dp(30),
            font_size=dp(14),
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(instructions)
        
        # Scroll view for content
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(20)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Mood selection section
        mood_label = Label(
            text='[b]SELECT A MOOD[/b]',
            markup=True,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(40),
            color=(1, 0.8, 0.2, 1),
            halign='left'
        )
        mood_label.bind(size=mood_label.setter('text_size'))
        content.add_widget(mood_label)
        
        # Mood buttons
        mood_grid = GridLayout(
            cols=3,
            spacing=dp(15),
            size_hint=(1, None),
            height=dp(200)
        )
        
        moods = [
            ('energetic', '*', (0.9, 0.3, 0.3, 1)),
            ('chill', '~', (0.3, 0.6, 0.8, 1)),
            ('melancholic', '-', (0.4, 0.4, 0.6, 1)),
            ('happy', '+', (0.9, 0.8, 0.2, 1)),
            ('dark', '•', (0.3, 0.2, 0.4, 1)),
            ('groovy', '♪', (0.8, 0.4, 0.8, 1)),
        ]
        
        for mood, emoji, color in moods:
            btn = MoodButton(mood, emoji, color)
            btn.bind(on_press=lambda x, m=mood: self.pick_by_mood(m))
            mood_grid.add_widget(btn)
        
        content.add_widget(mood_grid)
        
        # Random button
        random_btn = Button(
            text='SURPRISE ME!',
            size_hint=(1, None),
            height=dp(60),
            background_normal='',
            background_color=(0.5, 0.3, 0.7, 1),
            font_size=dp(20),
            bold=True
        )
        random_btn.bind(on_press=lambda x: self.pick_random())
        content.add_widget(random_btn)
        
        # Genre selection section
        self.genre_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(10)
        )
        self.genre_section.bind(minimum_height=self.genre_section.setter('height'))
        
        genre_label = Label(
            text='[b]OR BROWSE BY GENRE[/b]',
            markup=True,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(40),
            color=(1, 0.8, 0.2, 1),
            halign='left'
        )
        genre_label.bind(size=genre_label.setter('text_size'))
        self.genre_section.add_widget(genre_label)
        
        content.add_widget(self.genre_section)
        
        # Result display area
        self.result_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(15)
        )
        self.result_container.bind(minimum_height=self.result_container.setter('height'))
        
        content.add_widget(self.result_container)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def on_pre_enter(self):
        """Load genres when entering screen"""
        self.load_genres()
    
    def load_genres(self):
        """Load and display available genres"""
        from kivy.app import App
        app = App.get_running_app()
        if not app.discogs or not app.discogs.collection:
            return
        
        # Clear existing genre buttons (keep label)
        children_to_remove = list(self.genre_section.children)[:-1]
        for child in children_to_remove:
            self.genre_section.remove_widget(child)
        
        genres = app.discogs.get_all_genres()
        
        if genres:
            genre_grid = GridLayout(
                cols=3,
                spacing=dp(10),
                size_hint=(1, None)
            )
            genre_grid.bind(minimum_height=genre_grid.setter('height'))
            
            for genre in genres[:18]:  # Limit to 18 genres for space
                btn = Button(
                    text=genre,
                    size_hint=(1, None),
                    height=dp(50),
                    background_normal='',
                    background_color=(0.2, 0.3, 0.35, 1),
                    font_size=dp(12)
                )
                btn.bind(on_press=lambda x, g=genre: self.pick_by_genre(g))
                genre_grid.add_widget(btn)
            
            self.genre_section.add_widget(genre_grid)
    
    def pick_by_mood(self, mood):
        """Pick random album by mood"""
        from kivy.app import App
        app = App.get_running_app()
        if not app.discogs:
            return
        
        album = app.discogs.get_random_by_mood(mood)
        if album:
            self.display_selection(album, f'Mood: {mood.upper()}')
    
    def pick_by_genre(self, genre):
        """Pick random album by genre"""
        from kivy.app import App
        app = App.get_running_app()
        if not app.discogs:
            return
        
        album = app.discogs.get_random_by_genre(genre)
        if album:
            self.display_selection(album, f'Genre: {genre}')
    
    def pick_random(self):
        """Pick completely random album"""
        from kivy.app import App
        app = App.get_running_app()
        if not app.discogs:
            return
        
        album = app.discogs.get_random_by_mood(None)
        if album:
            self.display_selection(album, 'Random Pick')
    
    def display_selection(self, album, selection_type):
        """Display the selected album"""
        self.result_container.clear_widgets()
        self.current_selection = album
        
        # Selection type label
        type_label = Label(
            text=f'[b]YOUR SELECTION: {selection_type}[/b]',
            markup=True,
            font_size=dp(18),
            size_hint=(1, None),
            height=dp(40),
            color=(0.3, 0.9, 0.5, 1)
        )
        self.result_container.add_widget(type_label)
        
        # Album display
        album_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(250),
            spacing=dp(20)
        )
        
        # Cover
        cover_box = BoxLayout(size_hint=(None, 1), width=dp(250))
        
        with cover_box.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.cover_bg = RoundedRectangle(pos=cover_box.pos, size=cover_box.size, radius=[dp(10)])
        
        cover_box.bind(pos=self.update_cover_bg, size=self.update_cover_bg)
        
        if album.get('cover') or album.get('thumb'):
            cover_img = AsyncImage(
                source=album.get('cover') or album.get('thumb'),
                allow_stretch=True,
                keep_ratio=True
            )
            cover_box.add_widget(cover_img)
        else:
            placeholder = Label(text='♪', font_size=dp(80))
            cover_box.add_widget(placeholder)
        
        album_container.add_widget(cover_box)
        
        # Info
        info_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        title = Label(
            text=f"[b]{album['title']}[/b]",
            markup=True,
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(60),
            color=(1, 1, 1, 1),
            halign='left',
            valign='top'
        )
        title.bind(size=title.setter('text_size'))
        
        artist = Label(
            text=f"by {album['artist']}",
            font_size=dp(16),
            size_hint=(1, None),
            height=dp(30),
            color=(0.8, 0.8, 0.8, 1),
            halign='left',
            valign='middle'
        )
        artist.bind(size=artist.setter('text_size'))
        
        year = Label(
            text=f"Released: {album.get('year', 'N/A')}",
            font_size=dp(14),
            size_hint=(1, None),
            height=dp(25),
            color=(0.7, 0.7, 0.7, 1),
            halign='left',
            valign='middle'
        )
        year.bind(size=year.setter('text_size'))
        
        view_btn = Button(
            text='VIEW DETAILS →',
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(0.3, 0.5, 0.7, 1),
            font_size=dp(14)
        )
        view_btn.bind(on_press=lambda x: self.view_details())
        
        info_layout.add_widget(title)
        info_layout.add_widget(artist)
        info_layout.add_widget(year)
        info_layout.add_widget(Label())  # Spacer
        info_layout.add_widget(view_btn)
        
        album_container.add_widget(info_layout)
        self.result_container.add_widget(album_container)
        
        # Animate the result
        album_container.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(album_container)
    
    def update_cover_bg(self, instance, value):
        self.cover_bg.pos = instance.pos
        self.cover_bg.size = instance.size
    
    def view_details(self):
        """Navigate to detail screen"""
        if self.current_selection:
            detail_screen = self.manager.get_screen('detail')
            detail_screen.set_album(self.current_selection)
            self.manager.current = 'detail'
    
    def on_collection_loaded(self):
        """Called when collection is loaded"""
        if self.manager.current == 'jukebox':
            self.load_genres()
    
    def go_back(self, instance):
        self.manager.current = 'home'
