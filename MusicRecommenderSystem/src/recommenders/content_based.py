import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from MusicRecommenderSystem.src.features.audio_features import AudioFeatureExtractor

class ContentBasedRecommender:
    def __init__(self, spotify_client):
        self.spotify = spotify_client
        self.feature_extractor = AudioFeatureExtractor()

    def recommend(self, seed_track_id, n_recommendations=20):
        """
        Recommend tracks similar to the seed track
        """

        # Get seed track features
        seed_features = self.spotify.get_track_features(seed_track_id)
        seed_vector = self.feature_extractor.extract_features(seed_features)

        # Get Spotify recommendations as candidates

        spotify_recs = self.spotify.get_recommedations(
            seed_tracks = [seed_track_id],
            limit = 100 # Get more candidates to filter
        )

        # Calculate similarity for each candidate 
        candidates = []
        for track in spotify_recs['tracks']:
            track_features = self.spotify.get_track_features(track['id'])
            track_vector = self.feature_extractor.extract_features(track_features)

            similarity = self.feature_extractor.calculate_weighted_similarity(
                seed_vector, track_vector
            )

            candidates.append( {
                'track': track,
                'features': track_features,
                'similarity': similarity
            })

            # Sort by similarity and return top N
            candidates.sort(key=lambda x:x['similarity'], reverse= True)

            return candidates[:n_recommendations]
