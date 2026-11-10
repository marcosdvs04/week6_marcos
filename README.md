# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify or YouTube mix two ideas. **Collaborative filtering** says "people who liked what you liked also liked this." **Content-based filtering** says "this song has similar attributes to what you like." They score thousands of candidates, then rank and filter them, adding variety and freshness. My version is a small content-based recommender. It doesn't learn from other users. Instead, it compares each song's attributes directly against a user's taste profile. It weights **genre** slightly above **mood**, because genre is the most stable part of someone's taste, but a song with the right mood can still beat one that only matches the genre. Then it looks at how close a song's **energy** is to the user's target, and finally whether its acoustic feel fits. The goal is to match the overall "vibe," not just pick the most energetic or most popular track.

**`Song` features used:**
- `genre`: categorical, exact match
- `mood`: categorical, exact match
- `energy`: 0–1, scored by closeness to the user's target
- `acousticness`: 0–1, scored by whether the user likes acoustic sound
- (stored but not scored yet: `tempo_bpm`, `valence`, `danceability`)

**`UserProfile` features:**
- `favorite_genre`
- `favorite_mood`
- `target_energy` (0–1)
- `likes_acoustic` (True/False)

### Data Flow

```
INPUT                         PROCESS (recommend_songs)              OUTPUT
songs.csv ─► load_songs() ─┐  for each song in the catalog:          sort by score, high → low
                           ├─►  score_song(user_prefs, song)    ─►   keep the top k
user_prefs ────────────────┘    → (score, reasons)                   print title, score, reasons
```

Each song is scored independently against the user's profile. Songs are only compared with each other in the final sort.

### Algorithm Recipe (finalized)

**Step 1: Score one song (max 6.5 points)**

| Rule | Points | Why |
|---|---|---|
| Genre matches `favorite_genre` | +2.0 | Genre is the most stable signal of taste, so it gets the largest weight. |
| Mood matches `favorite_mood` | +1.5 | Close to genre, so a "right vibe, wrong genre" song can still rank well. |
| Energy closeness | +2.0 × max(0, 1 − \|energy − target_energy\| / 0.5) | An exact match earns 2.0. Points shrink as the gap grows, and a gap of 0.5 or more earns 0, so very loud songs are penalized for a calm listener. |
| Acoustic fit | +1.0 × acousticness (or × (1 − acousticness) if `likes_acoustic` is False) | A texture preference, so it counts less than a genre or mood match. |

Genre and mood are exact, case-insensitive string matches. Each rule records a short reason (for example, `mood match (chill) +1.50`) so every score comes with an explanation.

**Step 2: Rank the catalog.** Score all songs, sort from highest to lowest, and return the top *k* as `(song, score, explanation)`.

**Example** (lofi / chill / energy 0.40 / likes acoustic): Library Rain 6.16, Midnight Coding 6.13, Focus Flow 4.78 at the top; Gym Hero 0.05, Iron Furnace 0.03, Neon Euphoria 0.02 at the bottom.

**Why this weighting:** I compared three options. A genre-first version (genre 3.0, mood 1.5) barely separated the non-lofi songs. A mood-first version (genre 1.0, mood 2.0) let an ambient song beat a lofi one for a user who explicitly named lofi as their favorite genre. This version keeps genre slightly ahead while still giving mood real weight.

### Expected Biases and Limitations

- **Genre can still outweigh mood.** A genre match (+2.0) is worth more than a mood match (+1.5). For example, Focus Flow (lofi, *focused*) outranks Spacewalk Thoughts (ambient, *chill*), even though Spacewalk has exactly the mood the user asked for.
- **Exact matching misses near-misses.** "relaxed" earns nothing toward "chill", and "indie pop" earns nothing toward "pop", so similar songs can be overlooked just because of their labels.
- **Uneven catalog.** Lofi has 3 songs, but most genres have only 1. A lofi fan gets several strong matches, while a metal or classical fan gets one, and the rest of their list is filled by energy and acoustic points alone.
- **The acoustic rule is all-or-nothing.** `likes_acoustic` is True/False, so a user who dislikes acoustic music automatically gets electronic and pop songs pushed up, whether they want them or not.
- **No variety control.** Nothing stops the same artist from filling the top spots. LoRoom has 2 of the top 3 songs for the lofi profile.
- **Ignored features.** `tempo_bpm`, `valence`, and `danceability` are stored but not scored, so two songs that feel very different can tie if their genre, mood, energy, and acousticness match.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



