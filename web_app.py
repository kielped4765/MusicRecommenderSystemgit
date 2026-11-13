"""HTTP API and web entry point for the Docker-hosted music recommender."""

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import Config
from src.api.spotify_client import SpotifyClient
from src.api.youtube_client import YouTubeClient
from src.recommenders.content_based import ContentBasedRecommender


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Music Recommender System", version="1.0.0")
# The browser UI and API share an origin, so the app does not need permissive CORS.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_spotify_client(request: Request) -> SpotifyClient:
    """Create one Spotify client per app process, after checking its credentials."""
    if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail=(
                "Spotify is not configured. Set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET in the container environment."
            ),
        )

    client = getattr(request.app.state, "spotify_client", None)
    if client is None:
        # Reuse the client so Spotipy can reuse its app token across requests.
        client = SpotifyClient()
        request.app.state.spotify_client = client
    return client


def serialize_track(track: dict[str, Any]) -> dict[str, Any]:
    """Return an allowlist of track fields instead of the full Spotify response."""
    images = track.get("album", {}).get("images", [])
    return {
        "id": track.get("id"),
        "name": track.get("name", "Unknown track"),
        "artists": [artist.get("name", "Unknown artist") for artist in track.get("artists", [])],
        "album": track.get("album", {}).get("name"),
        "image_url": images[0].get("url") if images else None,
        "spotify_url": track.get("external_urls", {}).get("spotify"),
        "preview_url": track.get("preview_url"),
    }


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Serve the browser UI from the same origin as the API."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    """Docker and Azure can use this endpoint to check whether the app is responding."""
    return {
        "status": "ok",
        "spotify_configured": bool(
            Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET
        ),
    }


@app.get("/api/search")
def search_track(
    q: str = Query(min_length=1, max_length=120),
    artist: str | None = Query(default=None, max_length=120),
    spotify: SpotifyClient = Depends(get_spotify_client),
) -> dict[str, Any]:
    """Find one Spotify track by name and, optionally, artist."""
    track = spotify.get_track_by_name(q.strip(), artist.strip() if artist else None)
    if track is None:
        raise HTTPException(status_code=404, detail="No matching track was found.")
    return {"track": serialize_track(track)}


@app.get("/api/recommendations")
def get_recommendations(
    seed_track_id: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
    spotify: SpotifyClient = Depends(get_spotify_client),
) -> dict[str, Any]:
    """Recommend tracks related to an existing Spotify track ID."""
    # Keep recommendations on the existing content-based algorithm path.
    recommender = ContentBasedRecommender(spotify)
    results = recommender.recommend(seed_track_id.strip(), n_recommendations=limit)
    return {
        "seed_track_id": seed_track_id,
        "recommendations": [
            {
                **serialize_track(result["track"]),
                "similarity": result.get("similarity"),
            }
            for result in results
        ],
    }


@app.get("/api/youtube")
def search_youtube(
    track: str = Query(min_length=1, max_length=120),
    artist: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    """Look up music videos when a YouTube Data API key is configured."""
    if not Config.YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="YouTube is not configured. Set YOUTUBE_API_KEY to enable video search.",
        )
    youtube = YouTubeClient()
    return {"videos": youtube.search_music_video(track.strip(), artist.strip())}
