print(">>> main.py started <<<")

from src.api.spotify_client import SpotifyClient
from src.api.youtube_client import YouTubeClient
from src.playlist.generator import PlaylistGenerator
from src.recommenders.hybrid import HybridRecommender
import json

def main():
    print("🎵 Advanced Music Recommender System\n")

    spotify = SpotifyClient(use_auth=True)
    youtube = YouTubeClient()

    recommender = HybridRecommender(spotify)
    playlist_gen = PlaylistGenerator(spotify)

    while True:
        print("\nChoose an option:")
        print("1. Get recommendations from a song")
        print("2. Generate playlist from seed track")
        print("3. Generate theme-based playlist")
        print("4. Generate playlist by genre and mood")
        print("5. Find YouTube music video")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ")

        if choice == '1':
            song_name = input("Enter song name: ")
            artist = input("Enter artist name (optional): ")
            theme = input("Enter theme (optional, e.g., 'party', 'workout'): ")

            track = spotify.get_track_by_name(song_name, artist if artist else None)

            if track:
                print(f"\nFound: {track['name']} by {track['artists'][0]['name']}")
                recs = recommender.recommend(
                    track['id'],
                    theme=theme if theme else None,
                    n_recommendations=10
                )
                print("\nRecommended tracks:")
                for i, rec in enumerate(recs, 1):
                    print(f"{i}. {rec['track']['name']} - {rec['track']['artists'][0]['name']}")
                    print(f"   Similarity: {rec['similarity']:.2f}", end="")
                    if theme:
                        print(f" | Theme match: {rec['theme_score']:.2f}")
                    else:
                        print()
            else:
                print("Track not found!")

        elif choice == '2':
            song_name = input("Enter seed song name: ")
            artist = input("Enter artist name (optional): ")
            length = int(input("Playlist length (default 30): ") or 30)
            theme = input("Theme (optional): ")
            variety = float(input("Variety 0-1 (default 0.3): ") or 0.3)

            track = spotify.get_track_by_name(song_name, artist if artist else None)

            if track:
                print(f"\nGenerating playlist from: {track['name']}...")
                playlist = playlist_gen.generate_from_seed(
                    track['id'],
                    playlist_length=length,
                    theme=theme if theme else None,
                    variety=variety
                )
                print(f"\n📝 Generated playlist ({len(playlist)} tracks):")
                for i, t in enumerate(playlist, 1):
                    print(f"{i}. {t['name']} - {t['artists'][0]['name']}")

                save = input("\nSave to Spotify? (y/n): ")
                if save.lower() == 'y':
                    name = input("Playlist name: ")
                    user_id = spotify.sp.current_user()['id']
                    saved = playlist_gen.save_playlist(user_id, name, playlist)
                    print(f"✅ Playlist saved! URL: {saved['external_urls']['spotify']}")

        elif choice == '3':
            print("\nAvailable themes:")
            themes = ['party', 'workout', 'relaxation', 'romance',
                      'melancholy', 'focus', 'road_trip', 'sleep']
            for i, t in enumerate(themes, 1):
                print(f"{i}. {t}")

            theme = input("\nEnter theme name: ")
            length = int(input("Playlist length (default 30): ") or 30)

            print(f"\nGenerating {theme} playlist...")
            playlist = playlist_gen.generate_by_theme(theme, length)

            print(f"\n📝 Generated playlist ({len(playlist)} tracks):")
            for i, t in enumerate(playlist, 1):
                print(f"{i}. {t['name']} - {t['artists'][0]['name']}")

        elif choice == '4':
            genres = input("Enter genres (comma-separated, e.g., 'rock,indie'): ").split(',')
            genres = [g.strip() for g in genres]

            print("\nEnter target mood features (0-1 scale):")
            energy = float(input("Energy (0-1): "))
            valence = float(input("Valence/happiness (0-1): "))
            danceability = float(input("Danceability (0-1): "))

            mood_features = {
                'energy': energy,
                'valence': valence,
                'danceability': danceability
            }

            length = int(input("Playlist length (default 30): ") or 30)

            playlist = playlist_gen.generate_by_genre_and_mood(
                genres, mood_features, length
            )

            print(f"\n📝 Generated playlist ({len(playlist)} tracks):")
            for i, t in enumerate(playlist, 1):
                print(f"{i}. {t['name']} - {t['artists'][0]['name']}")

        elif choice == '5':
            song_name = input("Enter song name: ")
            artist = input("Enter artist name: ")

            videos = youtube.search_music_video(song_name, artist)

            if videos:
                print("\n🎬 Found videos:")
                for i, video in enumerate(videos, 1):
                    print(f"{i}. {video['title']}")
                    print(f"   Channel: {video['channel']}")
                    print(f"   URL: https://youtube.com/watch?v={video['video_id']}\n")
            else:
                print("No videos found!")

        elif choice == '6':
            print("Goodbye! 🎵")
            break

if __name__ == "__main__":
    main()
