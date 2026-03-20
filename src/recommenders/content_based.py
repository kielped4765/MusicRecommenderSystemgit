class ContentBasedRecommender:
    def __init__(self, spotify_client):
        self.spotify = spotify_client

    def recommend(self, seed_track_id, n_recommendations=20):
        # Get seed track info
        track_info = self.spotify.sp.track(seed_track_id)
        artist_name = track_info['artists'][0]['name']
        track_name = track_info['name']

        candidates = []
        seen = set([seed_track_id])

        # Search for more tracks by same artist
        results = self.spotify.sp.search(
            q=f"artist:{artist_name}", type='track', limit=10
        )
        for track in results['tracks']['items']:
            if track['id'] not in seen:
                seen.add(track['id'])
                candidates.append({
                    'track': track,
                    'features': {},
                    'similarity': 1.0
                })

        # Search for tracks using track name
        results2 = self.spotify.sp.search(
            q=track_name, type='track', limit=10
        )
        for track in results2['tracks']['items']:
            if track['id'] not in seen:
                seen.add(track['id'])
                candidates.append({
                    'track': track,
                    'features': {},
                    'similarity': 0.7
                })

        return candidates[:n_recommendations]