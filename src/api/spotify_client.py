import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config.settings import Config
import time


class SpotifyClient:
    def __init__(self, use_auth=True):
        """
        Initialize Spotify client
        use_auth: True for user-specific features (playlists), False for general search
        """
        if use_auth:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope="user-library-read playlist-modify-public playlist-modify-private"
            ))
        else:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET
            ))

    def get_track_by_name(self, track_name, artist_name=None):
        """Search for a track by name and optionally artist"""
        query = f"track:{track_name}"
        if artist_name:
            query += f" artist:{artist_name}"

        results = self.sp.search(q=query, type='track', limit=1)

        if results['tracks']['items']:
            return results['tracks']['items'][0]
        return None

    def get_track_features(self, track_id):
        """Get audio features for a track"""
        features = self.sp.audio_features([track_id])[0]
        track_info = self.sp.track(track_id)

        return {
            'id': track_id,
            'name': track_info['name'],
            'artist': track_info['artists'][0]['name'],
            'album': track_info['album']['name'],
            'popularity': track_info['popularity'],
            'duration_ms': track_info['duration_ms'],
            'danceability': features['danceability'],
            'energy': features['energy'],
            'key': features['key'],
            'loudness': features['loudness'],
            'mode': features['mode'],
            'speechiness': features['speechiness'],
            'acousticness': features['acousticness'],
            'instrumentalness': features['instrumentalness'],
            'liveness': features['liveness'],
            'valence': features['valence'],
            'tempo': features['tempo'],
            'time_signature': features['time_signature']
        }

    def get_recommendations(self, seed_tracks=None, seed_artists=None,
                            seed_genres=None, limit=20, **kwargs):
        """
        Get Spotify recommendations
        kwargs can include target_* parameters for audio features
        """
        return self.sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            limit=limit,
            **kwargs
        )

    def get_genre_seeds(self):
        """Get available genre seeds for recommendations"""
        return self.sp.recommendation_genre_seeds()

    def create_playlist(self, user_id, name, track_ids, description=""):
        """Create a new playlist with given tracks"""
        playlist = self.sp.user_playlist_create(
            user_id,
            name,
            public=False,
            description=description
        )

        # Add tracks in batches of 100 (Spotify limit)
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            self.sp.playlist_add_items(playlist['id'], batch)

        return playlist

    def search_tracks_by_features(self, target_features, limit=50):
        """
        Search for tracks matching specific audio features
        """
        results = self.sp.recommendations(
            seed_genres=['pop'],
            limit=limit,
            **{f'target_{k}': v for k, v in target_features.items()}
        )
        return results['tracks']










