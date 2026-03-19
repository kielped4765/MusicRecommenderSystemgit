import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))

class Config:
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    CACHE_ENABLED = True
    CACHE_TTL = 86400
    DEFAULT_RECOMMENDATION_COUNT = 20
    SIMILARITY_THRESHOLD = 0.7
    FEATURE_WEIGHTS = {
        'danceability': 1.0,
        'energy': 1.0,
        'valence': 0.8,
        'tempo': 0.6,
        'acousticness': 0.7,
        'instrumentalness': 0.5,
        'speechiness': 0.4
    }