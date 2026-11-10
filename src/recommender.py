from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# --- Strategy B: balanced scoring, genre slightly ahead of mood (max 6.5) ---
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 2.0
ENERGY_CUTOFF = 0.5  # energy gap at which a song earns zero energy points
ACOUSTIC_WEIGHT = 1.0
MAX_SCORE = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT + ACOUSTIC_WEIGHT


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = asdict(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = score_song(asdict(user), asdict(song))
        return f"{score:.2f}/{MAX_SCORE:.1f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            songs.append(row)
    print(f"Loaded songs: {len(songs)} (from {csv_path})")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using Strategy B.
    Returns (score, reasons), where reasons lists the points each rule earned.
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match: +2.0
    if song["genre"].lower() == user_prefs["favorite_genre"].lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT})")

    # Mood match: +1.5
    if song["mood"].lower() == user_prefs["favorite_mood"].lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT})")

    # Energy closeness: full points at an exact match, zero at a gap of 0.5 or more
    gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_points = ENERGY_WEIGHT * max(0.0, 1 - gap / ENERGY_CUTOFF)
    score += energy_points
    reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})")

    # Acoustic fit: reward acousticness if liked, otherwise reward its absence
    if user_prefs.get("likes_acoustic", False):
        acoustic_fit = song["acousticness"]
    else:
        acoustic_fit = 1 - song["acousticness"]
    acoustic_points = ACOUSTIC_WEIGHT * acoustic_fit
    score += acoustic_points
    reasons.append(f"acoustic fit (+{acoustic_points:.2f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Returns the top k songs as (song_dict, score, explanation), highest score first.
    """
    # Judge every song: score_song returns (score, reasons)
    judged = [(song, *score_song(user_prefs, song)) for song in songs]

    # Turn each reasons list into one readable explanation string
    scored = [(song, score, "; ".join(reasons)) for song, score, reasons in judged]

    # Rank from highest to lowest score and keep the top k
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
