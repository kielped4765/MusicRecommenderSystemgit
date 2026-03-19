from MusicRecommenderSystem.src.recommenders.content_based import ContentBasedRecommender
from MusicRecommenderSystem.src.features.theme_analyzer import ThemeAnalyzer
import numpy as np

class HybridRecommender:
    def __init__(self, spotify_client):
        self.spotify = spotify_client
        self.content_recommender = ContentBasedRecommender(spotify_client)
        self.theme_analyzer = ThemeAnalyzer()

    def recommend(self, seed_track_id, theme=None, n_recommendations=20):
        """
        Hybrid recommendations combining content-based filtering and theme analysis
        """

        # Get content-based recommendations
        content_recs = self.content_recommender.recommend(
            seed_track_id,
            n_recommendations=50 # Get more to filter by theme
        )

        if not theme:
            return content_recs[:n_recommendations]

        # Score tracks by theme relevance
        for rec in content_recs:
            track_text = f"{rec['track']['name']} {rec['track']['artists'][0]['name']}"
            theme_scores = self.theme_analyzer.analyze_theme(
                track_text,
                custom_themes=[theme]
            )

            # Conbine content similarity with theme song
            rec['theme_score'] = theme_scores.get(theme, 0)
            rec['hybrid_score'] = (0.6 * rec['similarity']) + (0.4 * rec['theme_score'])

        # Re-sort by hybrid score
        content_recs.sort(key=lambda x:x['hybrid_score'], reverse = True)

        return content_recs[:n_recommendations]