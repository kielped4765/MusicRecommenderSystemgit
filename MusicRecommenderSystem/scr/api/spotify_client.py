import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config.settings import Config
import time


class SpotifyClient:
    def __init__(self, use_auth=True):
        """
        Initalize Spotify client
        use_auth: True for user-specific features (playlists), False for general search
        """

        if use_auth:
            self.sp = spotify.Spotify(auth_manager=SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_url=Config.SPOTIFY_REDIRECT_URL,
                scope="user-library-read playlist-modify-public playlist-modify-private"
              ))
        else:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET
            ))
    
    def get_track_by_name(self, track_name, artist_name=None):
        """Search for a track by name and optionally artist"""
        query=f"track: {track_name}"
        if artist_name:
            query += f"artist: {artist_name}"

        results = self.sp.search(q=query, type='track', limit=1)

        if results['tracks']['items']:
            return results['tracks']['items'][0]
        return None

    def get_track_features(self, track_id):
        """Get audio features for a track"""
        features = self.sp.audio_features([track_id])[0]
        track_info = self.sp.track(track_id)

        return {
            }

