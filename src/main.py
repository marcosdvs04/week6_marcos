"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for several user profiles (normal and adversarial)
and prints the top 5 songs for each, with the reasons behind every score.
"""

try:
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs  # python src/main.py


# Typical listeners: each profile should clearly favor a different corner of the catalog.
STANDARD_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
}

# Edge cases designed to see whether the scoring logic can be "tricked".
ADVERSARIAL_PROFILES = {
    # Conflicting preferences: sad songs in the catalog are all low energy.
    "Conflicted: Sad but High-Energy": {
        "favorite_genre": "classical",
        "favorite_mood": "sad",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    # Genre and mood that do not exist in songs.csv, so they can never match.
    "Ghost Genre: K-Pop / Dreamy": {
        "favorite_genre": "k-pop",
        "favorite_mood": "dreamy",
        "target_energy": 0.60,
        "likes_acoustic": True,
    },
    # Target energy outside the 0-1 range: no song is within 0.5 of it.
    "Out-of-Range Energy (1.5)": {
        "favorite_genre": "edm",
        "favorite_mood": "euphoric",
        "target_energy": 1.50,
        "likes_acoustic": False,
    },
    # Same taste as Chill Lofi, but with different capitalization and no likes_acoustic key.
    "Messy Input: 'LOFI' / 'Chill', no acoustic key": {
        "favorite_genre": "LOFI",
        "favorite_mood": "Chill",
        "target_energy": 0.40,
    },
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a header for one profile followed by its top k songs."""
    print("=" * 70)
    print(f"Profile: {name}")
    print(f"Prefs:   {user_prefs}")
    print("=" * 70)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} ({song['genre']}, {song['mood']}, energy {song['energy']:.2f}) - Score: {score:.2f}")
        print(f"   Because: {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print()
    for name, prefs in {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES}.items():
        print_recommendations(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
