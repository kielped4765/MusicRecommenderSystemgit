from src.recommenders.content_based import ContentBasedRecommender
from src.features.theme_analyzer import ThemeAnalyzer
import numpy as np

class HybridRecommender:
    def __init__(self, spotify_client):
        self.spotify = spotify_client
        self.content_recommender = ContentBasedRecommender(spotify_client)
        self.theme_analyzer = ThemeAnalyzer()

    def recommend(self, seed_track_id, theme=None, n_recommendations=20):
        content_recs = self.content_recommender.recommend(
            seed_track_id,
            n_recommendations=50
        )

        if not theme:
            for rec in content_recs:
                rec['similarity'] = 1.0
                rec['theme_score'] = 0.0
                rec['hybrid_score'] = 1.0
            return content_recs[:n_recommendations]

        for rec in content_recs:
            track_text = f"{rec['track']['name']} {rec['track']['artists'][0]['name']}"
            theme_scores = self.theme_analyzer.analyze_theme(
                track_text,
                custom_themes=[theme]
            )
            rec['theme_score'] = theme_scores.get(theme, 0)
            rec['hybrid_score'] = rec['theme_score']
            rec['similarity'] = 1.0

        content_recs.sort(key=lambda x: x['hybrid_score'], reverse=True)
        return content_recs[:n_recommendations]