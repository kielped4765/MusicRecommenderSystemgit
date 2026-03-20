"""
Music Recommender System - GUI
Run with: python gui.py
Requires: pip install customtkinter
"""

import customtkinter as ctk
import threading
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.spotify_client import SpotifyClient
from src.api.youtube_client import YouTubeClient
from src.playlist.generator import PlaylistGenerator
from src.recommenders.hybrid import HybridRecommender

# ── Theme ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SPOTIFY_GREEN = "#1DB954"
BG_DARK       = "#121212"
BG_CARD       = "#1E1E1E"
BG_INPUT      = "#2A2A2A"
TEXT_PRIMARY  = "#FFFFFF"
TEXT_MUTED    = "#B3B3B3"
ACCENT        = "#1DB954"


# ── Helpers ──────────────────────────────────────────────────────────────────
def run_in_thread(fn):
    """Decorator: run a method in a background thread."""
    def wrapper(self, *args, **kwargs):
        threading.Thread(target=fn, args=(self, *args), kwargs=kwargs, daemon=True).start()
    return wrapper


# ── Main App ─────────────────────────────────────────────────────────────────
class MusicRecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎵 Music Recommender")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(fg_color=BG_DARK)

        self.spotify  = None
        self.youtube  = None
        self.recommender  = None
        self.playlist_gen = None

        self._build_ui()
        self._init_clients()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=BG_CARD, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="🎵", font=ctk.CTkFont(size=36)
        ).pack(pady=(30, 4))
        ctk.CTkLabel(
            self.sidebar, text="Music\nRecommender",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(0, 30))

        self.nav_buttons = {}
        nav_items = [
            ("🔍  Recommendations", "recommend"),
            ("📝  Playlist Generator", "playlist"),
            ("🎭  Theme Playlist", "theme"),
            ("🎬  YouTube Finder", "youtube"),
        ]
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, width=180, height=40,
                fg_color="transparent", hover_color="#2A2A2A",
                text_color=TEXT_MUTED, anchor="w",
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(pady=3, padx=10)
            self.nav_buttons[key] = btn

        # Status bar at bottom of sidebar
        self.status_label = ctk.CTkLabel(
            self.sidebar, text="● Connecting...",
            text_color="#FFA500", font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="bottom", pady=20)

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Tab frames
        self.tabs = {}
        self.tabs["recommend"] = self._build_recommend_tab()
        self.tabs["playlist"]  = self._build_playlist_tab()
        self.tabs["theme"]     = self._build_theme_tab()
        self.tabs["youtube"]   = self._build_youtube_tab()

        self._switch_tab("recommend")

    def _switch_tab(self, key):
        for k, frame in self.tabs.items():
            frame.pack_forget()
        self.tabs[key].pack(fill="both", expand=True)

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=ACCENT, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

    # ── Tab: Recommendations ─────────────────────────────────────────────────
    def _build_recommend_tab(self):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        ctk.CTkLabel(frame, text="Song Recommendations",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 16))

        # Inputs
        input_card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        input_card.pack(fill="x", pady=(0, 12))

        row1 = ctk.CTkFrame(input_card, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(row1, text="Song Name", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row1, text="Artist (optional)", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=(16, 0))
        ctk.CTkLabel(row1, text="Theme (optional)", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, sticky="w", padx=(16, 0))

        self.rec_song   = ctk.CTkEntry(row1, width=220, fg_color=BG_INPUT, border_width=0, placeholder_text="e.g. Blinding Lights")
        self.rec_artist = ctk.CTkEntry(row1, width=180, fg_color=BG_INPUT, border_width=0, placeholder_text="e.g. The Weeknd")
        self.rec_theme  = ctk.CTkEntry(row1, width=160, fg_color=BG_INPUT, border_width=0, placeholder_text="e.g. workout")

        self.rec_song.grid(row=1, column=0, pady=6)
        self.rec_artist.grid(row=1, column=1, padx=(16, 0), pady=6)
        self.rec_theme.grid(row=1, column=2, padx=(16, 0), pady=6)

        row1.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            input_card, text="Get Recommendations", fg_color=ACCENT,
            hover_color="#17a349", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._do_recommend
        ).pack(anchor="w", padx=16, pady=(0, 16))

        # Results
        self.rec_results = self._build_results_box(frame)
        return frame

    # ── Tab: Playlist Generator ───────────────────────────────────────────────
    def _build_playlist_tab(self):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        ctk.CTkLabel(frame, text="Playlist Generator",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 16))

        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 12))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=16)

        labels = ["Seed Song", "Artist (optional)", "Theme (optional)", "Length", "Variety (0-1)"]
        for i, l in enumerate(labels):
            ctk.CTkLabel(grid, text=l, text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=12)).grid(row=0, column=i, sticky="w", padx=(0 if i==0 else 12, 0))

        self.pl_song    = ctk.CTkEntry(grid, width=180, fg_color=BG_INPUT, border_width=0, placeholder_text="Song name")
        self.pl_artist  = ctk.CTkEntry(grid, width=150, fg_color=BG_INPUT, border_width=0, placeholder_text="Artist")
        self.pl_theme   = ctk.CTkEntry(grid, width=130, fg_color=BG_INPUT, border_width=0, placeholder_text="Theme")
        self.pl_length  = ctk.CTkEntry(grid, width=80,  fg_color=BG_INPUT, border_width=0, placeholder_text="30")
        self.pl_variety = ctk.CTkEntry(grid, width=80,  fg_color=BG_INPUT, border_width=0, placeholder_text="0.3")

        for i, w in enumerate([self.pl_song, self.pl_artist, self.pl_theme, self.pl_length, self.pl_variety]):
            w.grid(row=1, column=i, pady=6, padx=(0 if i==0 else 12, 0))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))

        ctk.CTkButton(btn_row, text="Generate Playlist", fg_color=ACCENT,
                      hover_color="#17a349", font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_playlist).pack(side="left")

        self.pl_save_btn = ctk.CTkButton(btn_row, text="💾 Save to Spotify",
                      fg_color="#333", hover_color="#444",
                      font=ctk.CTkFont(size=13),
                      command=self._do_save_playlist, state="disabled")
        self.pl_save_btn.pack(side="left", padx=(12, 0))

        self._last_playlist = []
        self.pl_results = self._build_results_box(frame)
        return frame

    # ── Tab: Theme Playlist ───────────────────────────────────────────────────
    def _build_theme_tab(self):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        ctk.CTkLabel(frame, text="Theme-Based Playlist",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 16))

        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(card, text="Select a Theme", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(16, 6))

        themes = ['party', 'workout', 'relaxation', 'romance', 'melancholy', 'focus', 'road_trip', 'sleep']
        self.theme_var = ctk.StringVar(value=themes[0])

        theme_grid = ctk.CTkFrame(card, fg_color="transparent")
        theme_grid.pack(fill="x", padx=16, pady=(0, 8))

        self.theme_btns = {}
        for i, t in enumerate(themes):
            btn = ctk.CTkButton(
                theme_grid, text=t.replace("_", " ").title(),
                width=110, height=34,
                fg_color=ACCENT if i == 0 else BG_INPUT,
                hover_color="#17a349",
                font=ctk.CTkFont(size=12),
                command=lambda th=t: self._select_theme(th)
            )
            btn.grid(row=i//4, column=i%4, padx=6, pady=4)
            self.theme_btns[t] = btn

        self._selected_theme = themes[0]

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(4, 16))
        ctk.CTkLabel(row, text="Length:", text_color=TEXT_MUTED).pack(side="left")
        self.theme_length = ctk.CTkEntry(row, width=70, fg_color=BG_INPUT, border_width=0, placeholder_text="30")
        self.theme_length.pack(side="left", padx=(8, 16))
        ctk.CTkButton(row, text="Generate", fg_color=ACCENT, hover_color="#17a349",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_theme_playlist).pack(side="left")

        self.theme_results = self._build_results_box(frame)
        return frame

    # ── Tab: YouTube Finder ───────────────────────────────────────────────────
    def _build_youtube_tab(self):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        ctk.CTkLabel(frame, text="YouTube Video Finder",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 16))

        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 12))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(row, text="Song:", text_color=TEXT_MUTED).pack(side="left")
        self.yt_song = ctk.CTkEntry(row, width=220, fg_color=BG_INPUT, border_width=0, placeholder_text="Song name")
        self.yt_song.pack(side="left", padx=(8, 16))

        ctk.CTkLabel(row, text="Artist:", text_color=TEXT_MUTED).pack(side="left")
        self.yt_artist = ctk.CTkEntry(row, width=180, fg_color=BG_INPUT, border_width=0, placeholder_text="Artist name")
        self.yt_artist.pack(side="left", padx=(8, 16))

        ctk.CTkButton(row, text="Search", fg_color=ACCENT, hover_color="#17a349",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_youtube).pack(side="left")

        self.yt_results = self._build_results_box(frame)
        return frame

    # ── Shared Results Box ────────────────────────────────────────────────────
    def _build_results_box(self, parent):
        box = ctk.CTkTextbox(
            parent, fg_color=BG_CARD, text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Courier New", size=13),
            corner_radius=12, border_width=0, wrap="word"
        )
        box.pack(fill="both", expand=True)
        box.configure(state="disabled")
        return box

    def _write(self, box, text, clear=True):
        box.configure(state="normal")
        if clear:
            box.delete("1.0", "end")
        box.insert("end", text)
        box.configure(state="disabled")

    def _loading(self, box, msg="Loading..."):
        self._write(box, f"⏳  {msg}")

    # ── Init Clients ──────────────────────────────────────────────────────────
    @run_in_thread
    def _init_clients(self):
        try:
            self.spotify      = SpotifyClient(use_auth=True)
            self.youtube      = YouTubeClient()
            self.recommender  = HybridRecommender(self.spotify)
            self.playlist_gen = PlaylistGenerator(self.spotify)
            self.status_label.configure(text="● Connected", text_color=SPOTIFY_GREEN)
        except Exception as e:
            self.status_label.configure(text="● Error", text_color="#FF4444")
            for box in [self.rec_results, self.pl_results, self.theme_results, self.yt_results]:
                self._write(box, f"❌ Failed to connect:\n{e}")

    # ── Actions ───────────────────────────────────────────────────────────────
    @run_in_thread
    def _do_recommend(self):
        if not self.spotify:
            return
        box = self.rec_results
        song   = self.rec_song.get().strip()
        artist = self.rec_artist.get().strip()
        theme  = self.rec_theme.get().strip()

        if not song:
            self._write(box, "⚠️  Please enter a song name.")
            return

        self._loading(box, f"Searching for '{song}'...")

        track = self.spotify.get_track_by_name(song, artist or None)
        if not track:
            self._write(box, f"❌ Track not found: '{song}'")
            return

        self._write(box, f"✅ Found: {track['name']} — {track['artists'][0]['name']}\n\n⏳ Getting recommendations...\n")

        try:
            recs = self.recommender.recommend(
                track['id'], theme=theme or None, n_recommendations=10
            )
        except Exception as e:
            self._write(box, f"❌ Error getting recommendations:\n{e}")
            return

        lines = [f"🎧  Recommendations for '{track['name']}'\n{'─'*50}\n"]
        for i, rec in enumerate(recs, 1):
            name   = rec['track']['name']
            artist = rec['track']['artists'][0]['name']
            sim    = rec['similarity']
            line   = f"{i:>2}.  {name} — {artist}\n      Similarity: {sim:.0%}"
            if theme and 'theme_score' in rec:
                line += f"  |  Theme match: {rec['theme_score']:.0%}"
            lines.append(line)

        self._write(box, "\n".join(lines))

    @run_in_thread
    def _do_playlist(self):
        if not self.spotify:
            return
        box = self.pl_results
        song    = self.pl_song.get().strip()
        artist  = self.pl_artist.get().strip()
        theme   = self.pl_theme.get().strip()
        length  = int(self.pl_length.get().strip() or 30)
        variety = float(self.pl_variety.get().strip() or 0.3)

        if not song:
            self._write(box, "⚠️  Please enter a seed song name.")
            return

        self._loading(box, f"Generating playlist from '{song}'...")

        track = self.spotify.get_track_by_name(song, artist or None)
        if not track:
            self._write(box, f"❌ Track not found: '{song}'")
            return

        try:
            playlist = self.playlist_gen.generate_from_seed(
                track['id'], playlist_length=length,
                theme=theme or None, variety=variety
            )
        except Exception as e:
            self._write(box, f"❌ Error generating playlist:\n{e}")
            return

        self._last_playlist = playlist
        self.pl_save_btn.configure(state="normal")

        lines = [f"📝  Playlist from '{track['name']}' ({len(playlist)} tracks)\n{'─'*50}\n"]
        for i, t in enumerate(playlist, 1):
            lines.append(f"{i:>2}.  {t['name']} — {t['artists'][0]['name']}")

        self._write(box, "\n".join(lines))

    @run_in_thread
    def _do_save_playlist(self):
        if not self._last_playlist:
            return
        box = self.pl_results
        try:
            user_id = self.spotify.sp.current_user()['id']
            name = f"Generated Playlist — {self.pl_song.get().strip()}"
            saved = self.playlist_gen.save_playlist(user_id, name, self._last_playlist)
            url = saved['external_urls']['spotify']
            self._write(box, f"✅ Playlist saved!\n\n🔗 {url}", clear=False)
            self._write(box, f"\n\n✅ Saved to Spotify: {url}", clear=False)
        except Exception as e:
            self._write(box, f"\n\n❌ Save failed: {e}", clear=False)

    def _select_theme(self, theme):
        self._selected_theme = theme
        for t, btn in self.theme_btns.items():
            btn.configure(fg_color=ACCENT if t == theme else BG_INPUT)

    @run_in_thread
    def _do_theme_playlist(self):
        if not self.spotify:
            return
        box    = self.theme_results
        theme  = self._selected_theme
        length = int(self.theme_length.get().strip() or 30)

        self._loading(box, f"Generating '{theme}' playlist...")

        try:
            playlist = self.playlist_gen.generate_by_theme(theme, length)
        except Exception as e:
            self._write(box, f"❌ Error:\n{e}")
            return

        lines = [f"🎭  {theme.replace('_',' ').title()} Playlist ({len(playlist)} tracks)\n{'─'*50}\n"]
        for i, t in enumerate(playlist, 1):
            lines.append(f"{i:>2}.  {t['name']} — {t['artists'][0]['name']}")

        self._write(box, "\n".join(lines))

    @run_in_thread
    def _do_youtube(self):
        if not self.youtube:
            return
        box    = self.yt_results
        song   = self.yt_song.get().strip()
        artist = self.yt_artist.get().strip()

        if not song or not artist:
            self._write(box, "⚠️  Please enter both a song name and artist.")
            return

        self._loading(box, f"Searching YouTube for '{song}'...")

        try:
            videos = self.youtube.search_music_video(song, artist)
        except Exception as e:
            self._write(box, f"❌ Error:\n{e}")
            return

        if not videos:
            self._write(box, "❌ No videos found.")
            return

        lines = [f"🎬  YouTube results for '{song} — {artist}'\n{'─'*50}\n"]
        for i, v in enumerate(videos, 1):
            lines.append(f"{i}.  {v['title']}")
            lines.append(f"    Channel: {v['channel']}")
            lines.append(f"    URL: https://youtube.com/watch?v={v['video_id']}\n")

        self._write(box, "\n".join(lines))


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MusicRecommenderApp()
    app.mainloop()
