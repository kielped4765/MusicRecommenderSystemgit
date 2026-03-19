from MusicRecommenderSystem.src.recommenders.hybrid import HybridRecommender
from MusicRecommenderSystem.src.features.audio_features import AudioFeatureExtractor
import random

class PlaylistGenerator:
    def __init__(self, spotify_client):
        self.spotify = spotify_client
        self.recommender = HybridRecommender(spotify_client)
        self.feature_extractor = AudioFeatureExtractor()

    def generate_from_seed(self, seed_track_id, playlist_length=30,
                           theme = None, variety = 0.3):
        """
        Generate a playlist from a seed track
        variety: 0-1, higher = more diverse recommendations
        """
        tracks = []
        used_ids = set([seed_track_id])

        # Add seed track
        seed_track = self.spotify.sp.track(seed_track_id)
        tracks.append(seed_track)

        current_seed = seed_track_id

        while len(tracks) < playlist_length:
            # Get recommendations
            recs = self.recommender.recommend(
                current_seed,
                theme=theme,
                n_recommendations = 20
            )

            # Filter out alrerady used tracks
            available_recs = [r for r in recs if r['track']['id'] not in used_ids]

            if not available_recs:
                break

            #Select next trrack based on variety parameter

            if random.random() < variety:

                # Higher variety: select from broader range
                idx = random.randint(10, len(available_recs)-1)

            else:
                # lower variety: stick to most similar
                idx = 0

            selected = available_recs[idx]
            tracks.append(selected['track'])
            used_ids.add(selected['track']['id'])

            # Use last track as new seed occasionally for variety
            if random.random() < 0.3:
                current_seed = selected['track']['id']

        return tracks

    def generate_by_genre_and_mood(self, genres, mood_features,
                                       playlist_length = 30):
            
            """
            Generate playlist based on genre and specific mood/audio features
            mood_features: dict like {'energy': 0.8, 'valence': 0.6}
            """

            # Search for tracks matching criteria
            tracks = self.spotify.search_tracks_by_features(
                target_features=mood_features,
                limit=playlist_length*2
            )

            # Filter by genres if specific
            if genres:
                filtered_tracks = []
                for track in tracks:
                    artist_id = track['artists'][0]['id']
                    artist = self.spotify.sp.artist(artist_id)
                    artist.genres = artist['genres']

                    if any(g in artist.genres for g in genres):
                        filtered_tracks.append(track)

                    tracks = filtered_tracks

            return tracks[:playlist_length]

    def generate_by_theme(self, theme, playlist_length = 30):
            """
            Generate playlist based on a specific theme
            """
            from src.features.theme_analyzer import ThemeAnalyzer
            analyzer = ThemeAnalyzer()

            # Get theme keywords
            keywords = analyzer.get_theme_keywords(theme)

            # Search with keywords and build playlist
            all_tracks = []
            for keyword in keywords[:3]: # Use top 3 keywords
                results = self.spotify.sp.search(q=keyword, type='track', limit = 20)
                all_tracks.extend(results['tracks']['items'])

            # Remove duplications
            unique_tracks = {t['id']: t for t in all_tracks}.values()

            # Score by theme and select best matches
            scored_tracks = []
            for track in unique_tracks:
                text = f"{track['name']} {track['artists'][0]['name']}"
                theme_scores = analyzer.analyze_theme(text, custom_themes=[theme])
                scored_tracks.append({
                    'track':track,
                    'score':theme_scores.get(theme, 0)
                })

            # Sort and return top tracks
            scored_tracks.sort(key=lambda x:x['score'], reverse=True)
            return[st['track'] for st in scored_tracks[:playlist_length]]

    def save_playlist(self, user_id, name, tracks, description=""):
            """Save generated playlist to Spotify"""
            track_ids = [t['id'] if isinstance(t, dict) else t for t in tracks]
            return self.spotify.create_playlist(user_id, name, track_ids, description)


