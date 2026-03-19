import unittest
from src.recommenders.hybrid import HybridRecommender

class TestHybridRecommender(unittest.TestCase):
    def setUp(self):
        self.recommender = HybridRecommender(mock_spotify_client)

    def test_recommendations_not_empty(self):

        recs = self.recommender.recommend('track_id_123')
        self.assertGreater(len(recs),0)