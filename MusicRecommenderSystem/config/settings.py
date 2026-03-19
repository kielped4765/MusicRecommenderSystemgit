import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    #Spotify info (fix this once spotify allows me to actually creaste an API key)
    #SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    #SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    #SPOTIFY_REDIRECT_URI = 


    #Youtbie info
    YOUTUBE_API_KEY = os.getenv('AIzaSyDVYeG9xnqulNgapLNs8ikM3tQSYn2S9W0')

    #Cashe settings
    CACHE_ENABLED = True
    CACHE_TTL = 86400 #24 hours run time

    #Recommender parameters
    DEFAULT_RECOMMENDATION_COUNT = 20
    SIMILARITY_THRESHOLD = 0.7

    #Audio feature weights for similarity
    FEATURE_WEIGHTS = {
    'danceability': 1.0,
    'energy': 1.0,
    'valence': 0.8,
    'tempo': 0.6,
    'acousticness': 0.7,
    'instrumentalness': 0.5,
    'speechiness': 0.4
}