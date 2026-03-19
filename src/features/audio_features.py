import numpy as np
from sklearn.preprocessing import StandardScaler
from MusicRecommenderSystem.config.settings import Config

class AudioFeatureExtractor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = list(Config.FEATURE_WEIGHTS.keys())


    def extract_features(self, track_data):
        """Extract normalized audio features from track data"""
        features = []
        for feature in self.feature_names:
            value = track_data.get(feature, 0)
            #Normalize tempo seperately (different scale)
            if feature == 'tempo':
                value = value / 200.0 #Normalize tempo to 0-1 range
            features.append(value)

        return np.array(features)

    def calculate_weighted_similarity(self, features1, features2):
        """Calculate weighted cosine similarity between two feature vectors"""
        weights = np.array([Config.FEATURE_WEIGHTS[f] for f in self.feature_names])

        # Weighted features
        weighted1 = features1 * weights
        weighted2 = features2 * weights

        # Cosine similarity
        dot_product = np.dot(weighted1, weighted2)
        norm1 = np.linalg.norm(weighted1)
        norm2 = np.linalg.norm(weighted2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def classify_mood(self,features):
        """Classify track mood based on valence and energy"""
        valence = features.get('valence', 0.5)
        energy = features.get('energy', 0.5)

        if valence > 0.5 and energy > 0.5:
            return 'happy_energetic'
        elif valence > 0.5 and energy <= 0.5:
            return 'happy_calm'
        elif valence <= 0.5 and energy > 0.5:
            return 'sad_energetic'
        else:
            return 'sad_calm'
