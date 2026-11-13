import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient

from web_app import app, get_spotify_client


def make_track(track_id, name, artist):
    return {
        "id": track_id,
        "name": name,
        "artists": [{"name": artist}],
        "album": {"name": "Test album", "images": []},
        "external_urls": {"spotify": f"https://open.spotify.com/track/{track_id}"},
        "preview_url": None,
    }


class FakeSpotifyClient:
    def __init__(self):
        self.seed = make_track("seed-id", "Seed Song", "Seed Artist")
        self.similar = make_track("similar-id", "Similar Song", "Similar Artist")
        self.sp = SimpleNamespace(
            track=lambda track_id: self.seed,
            search=lambda **kwargs: {
                "tracks": {"items": [self.similar]}
            },
        )

    def get_track_by_name(self, track_name, artist_name=None):
        if track_name.casefold() == "seed song":
            return self.seed
        return None


class WebAppTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_spotify_client] = lambda: FakeSpotifyClient()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_homepage_is_served(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Music Recommender", response.text)

    def test_health_does_not_require_spotify_credentials(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_search_returns_a_compact_track(self):
        response = self.client.get("/api/search", params={"q": "Seed Song"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["track"]["id"], "seed-id")

    def test_search_reports_a_missing_track(self):
        response = self.client.get("/api/search", params={"q": "Unknown Song"})
        self.assertEqual(response.status_code, 404)

    def test_recommendations_use_the_existing_recommender(self):
        response = self.client.get(
            "/api/recommendations",
            params={"seed_track_id": "seed-id", "limit": 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["recommendations"][0]["id"],
            "similar-id",
        )


if __name__ == "__main__":
    unittest.main()
