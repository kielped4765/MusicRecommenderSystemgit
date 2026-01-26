import os
from dotenv import load_dotenv


load_dotenv()

class config:
    #Spotify info (fix this once spotify allows me to actually creaste an API key)
    # Spotify_Client_ID = os.getenv
    # Spotify_CLient_Secret = os.getenv
    # Spotify_Redirect_URL = 


    #Youtbie info
    Youtube_API_Key = os.getenv('AIzaSyDVYeG9xnqulNgapLNs8ikM3tQSYn2S9W0')

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