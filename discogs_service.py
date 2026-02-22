"""
Discogs API Service
Handles all interactions with the Discogs API
"""
import discogs_client
import os
import requests
from io import BytesIO
from PIL import Image
import random
import json
from datetime import datetime, timedelta
import time
import threading


class DiscogsService:
    def __init__(self, user_token, username, cache_dir='./cache'):
        self.client = discogs_client.Client('VinylCollectionApp/1.0', user_token=user_token)
        self.user_token = user_token
        self.username = username
        self.cache_dir = cache_dir
        self.user = None
        self.collection = []
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def authenticate(self):
        """Authenticate and get user info"""
        try:
            self.user = self.client.identity()
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def get_collection(self, page=1, per_page=100, max_items=None, force_refresh=False):
        """Fetch user's vinyl collection (with caching)"""
        cache_file = os.path.join(self.cache_dir, 'collection.json')
        cache_age_hours = 24  # Refresh cache after 24 hours
        
        # Try to load from cache first
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    age = datetime.now() - cache_time
                    
                    if age < timedelta(hours=cache_age_hours):
                        print(f"Loading collection from cache ({len(cache_data['items'])} records)")
                        self.collection = cache_data['items']
                        return self.collection
                    else:
                        print(f"Cache is {age.seconds//3600}h old, refreshing...")
            except Exception as e:
                print(f"Cache read error: {e}, fetching fresh data...")
        
        # Fetch from API using direct requests (faster than iterating)
        try:
            if not self.user:
                self.authenticate()
            
            print("Fetching collection from Discogs API...")
            items = []
            page = 1
            total_pages = None
            
            while True:
                # Use direct API call for pagination
                url = f"https://api.discogs.com/users/{self.username}/collection/folders/0/releases"
                params = {
                    'page': page,
                    'per_page': per_page,
                    'token': self.user_token
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    print(f"API error: {response.status_code}")
                    break
                
                data = response.json()
                
                if total_pages is None:
                    total_pages = data['pagination']['pages']
                    total_items = data['pagination']['items']
                    print(f"Fetching {total_items} records across {total_pages} pages...")
                
                # Process releases from this page
                for item in data['releases']:
                    basic_info = item['basic_information']
                    items.append({
                        'id': basic_info['id'],
                        'title': basic_info['title'],
                        'artist': basic_info['artists'][0]['name'] if basic_info.get('artists') else 'Unknown',
                        'year': basic_info.get('year', 'N/A'),
                        'thumb': basic_info.get('thumb', None),
                        'cover': basic_info['cover_image'] if basic_info.get('cover_image') else None,
                        'genres': basic_info.get('genres', []),
                        'styles': basic_info.get('styles', []),
                    })
                
                print(f"Loaded page {page}/{total_pages} ({len(items)} records so far)")
                
                if max_items and len(items) >= max_items:
                    print(f"Reached limit of {max_items} records")
                    break
                
                if page >= total_pages:
                    break
                
                page += 1
            
            self.collection = items
            
            # Save to cache
            try:
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'items': items
                }
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f)
                print(f"Collection cached ({len(items)} records)")
            except Exception as e:
                print(f"Cache write error: {e}")
            
            return items
        except Exception as e:
            print(f"Error fetching collection: {e}")
            return []
    
    def get_release_details(self, release_id):
        """Get detailed information about a specific release"""
        try:
            release = self.client.release(release_id)
            
            tracklist = []
            if hasattr(release, 'tracklist'):
                for track in release.tracklist:
                    tracklist.append({
                        'position': track.position,
                        'title': track.title,
                        'duration': track.duration
                    })
            
            return {
                'id': release.id,
                'title': release.title,
                'artist': release.artists[0].name if release.artists else 'Unknown',
                'year': release.year if hasattr(release, 'year') else 'N/A',
                'cover': release.images[0]['uri'] if release.images else None,
                'genres': release.genres if hasattr(release, 'genres') else [],
                'styles': release.styles if hasattr(release, 'styles') else [],
                'tracklist': tracklist,
                'label': release.labels[0].name if release.labels else 'Unknown',
                'country': release.country if hasattr(release, 'country') else 'Unknown',
                'notes': release.notes if hasattr(release, 'notes') else '',
            }
        except Exception as e:
            print(f"Error fetching release details: {e}")
            return None
    
    def search_collection(self, query):
        """Search within user's collection"""
        query_lower = query.lower()
        results = []
        
        for item in self.collection:
            if (query_lower in item['title'].lower() or 
                query_lower in item['artist'].lower() or
                any(query_lower in genre.lower() for genre in item['genres'])):
                results.append(item)
        
        return results
    
    def get_random_by_mood(self, mood=None):
        """Get random albums based on mood/genre"""
        # Mood to genre/style mapping
        mood_map = {
            'energetic': ['Rock', 'Punk', 'Electronic', 'Dance', 'Hip Hop'],
            'chill': ['Jazz', 'Ambient', 'Classical', 'Folk', 'Soul'],
            'melancholic': ['Blues', 'Folk', 'Classical', 'Indie'],
            'happy': ['Pop', 'Funk', 'Soul', 'Disco'],
            'dark': ['Metal', 'Industrial', 'Gothic', 'Post-Punk'],
            'groovy': ['Funk', 'Soul', 'Disco', 'R&B'],
        }
        
        if mood and mood.lower() in mood_map:
            # Filter by mood
            matching = []
            target_genres = mood_map[mood.lower()]
            
            for item in self.collection:
                item_genres = item['genres'] + item['styles']
                if any(genre in target_genres for genre in item_genres):
                    matching.append(item)
            
            if matching:
                return random.choice(matching)
        
        # Random from entire collection
        if self.collection:
            return random.choice(self.collection)
        
        return None
    
    def get_random_by_genre(self, genre):
        """Get random album by specific genre"""
        matching = []
        genre_lower = genre.lower()
        
        for item in self.collection:
            item_genres = [g.lower() for g in (item['genres'] + item['styles'])]
            if genre_lower in item_genres:
                matching.append(item)
        
        if matching:
            return random.choice(matching)
        
        return None
    
    def get_all_genres(self):
        """Get all unique genres from collection"""
        genres = set()
        for item in self.collection:
            genres.update(item['genres'])
            genres.update(item['styles'])
        return sorted(list(genres))
    
    def download_cover(self, url, release_id):
        """Download and cache album cover"""
        if not url:
            return None
        
        cache_path = os.path.join(self.cache_dir, f"{release_id}.jpg")
        
        # Return cached version if exists
        if os.path.exists(cache_path):
            return cache_path
        
        # Download cover with retry and rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(0.2)  # Rate limit: 5 per second max
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img.save(cache_path, 'JPEG')
                    return cache_path
                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error downloading cover {release_id}: {e}")
        
        return None
    
    def download_all_covers(self, progress_callback=None, prewarm_count=20):
        """Download all album covers in background with rate limiting.

        - Pre-warm the first `prewarm_count` covers synchronously (fast startup UX)
        - Continue downloading the rest in order
        - Calls `progress_callback(current, total, downloaded, skipped)` periodically
        """
        total = len(self.collection)
        downloaded = 0
        skipped = 0

        # Helper to report progress safely
        def _report(cur):
            if progress_callback:
                try:
                    progress_callback(cur, total, downloaded, skipped)
                except Exception:
                    pass

        # Pre-warm first N covers (attempt up to prewarm_count)
        prewarm_count = min(prewarm_count, total)
        for i in range(prewarm_count):
            album = self.collection[i]
            url = album.get('cover') or album.get('thumb')
            release_id = album['id']
            cache_path = os.path.join(self.cache_dir, f"{release_id}.jpg")
            if os.path.exists(cache_path):
                skipped += 1
            else:
                result = self.download_cover(url, release_id)
                if result:
                    downloaded += 1
            _report(i + 1)

        # Background - remaining covers
        for i in range(prewarm_count, total):
            album = self.collection[i]
            url = album.get('cover') or album.get('thumb')
            release_id = album['id']

            cache_path = os.path.join(self.cache_dir, f"{release_id}.jpg")
            if os.path.exists(cache_path):
                skipped += 1
            else:
                result = self.download_cover(url, release_id)
                if result:
                    downloaded += 1

            # Report every 10 items to avoid UI spam
            if (i + 1) % 10 == 0:
                _report(i + 1)

        # Final report
        _report(total)

        print(f"✓ Cover download complete: {downloaded} new, {skipped} cached")
        return downloaded, skipped
