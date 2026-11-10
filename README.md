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

Output of `python -m src.main` (top 5 per profile). The first three are typical listeners; the last four are adversarial profiles built to try to trick the scoring logic.

### Standard profiles

**High-Energy Pop**

```
Profile: High-Energy Pop
Prefs:   {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': 0.85, 'likes_acoustic': False}
1. Sunrise City (pop, happy, energy 0.82) - Score: 6.20
   Because: genre match (+2.0); mood match (+1.5); energy 0.82 vs target 0.85 (+1.88); acoustic fit (+0.82)
2. Gym Hero (pop, intense, energy 0.93) - Score: 4.63
   Because: genre match (+2.0); energy 0.93 vs target 0.85 (+1.68); acoustic fit (+0.95)
3. Rooftop Lights (indie pop, happy, energy 0.76) - Score: 3.79
   Because: mood match (+1.5); energy 0.76 vs target 0.85 (+1.64); acoustic fit (+0.65)
4. Concrete Verses (hip hop, energetic, energy 0.80) - Score: 2.68
   Because: energy 0.80 vs target 0.85 (+1.80); acoustic fit (+0.88)
5. Storm Runner (rock, intense, energy 0.91) - Score: 2.66
   Because: energy 0.91 vs target 0.85 (+1.76); acoustic fit (+0.90)
```

**Chill Lofi**

```
Profile: Chill Lofi
Prefs:   {'favorite_genre': 'lofi', 'favorite_mood': 'chill', 'target_energy': 0.4, 'likes_acoustic': True}
1. Library Rain (lofi, chill, energy 0.35) - Score: 6.16
   Because: genre match (+2.0); mood match (+1.5); energy 0.35 vs target 0.40 (+1.80); acoustic fit (+0.86)
2. Midnight Coding (lofi, chill, energy 0.42) - Score: 6.13
   Because: genre match (+2.0); mood match (+1.5); energy 0.42 vs target 0.40 (+1.92); acoustic fit (+0.71)
3. Focus Flow (lofi, focused, energy 0.40) - Score: 4.78
   Because: genre match (+2.0); energy 0.40 vs target 0.40 (+2.00); acoustic fit (+0.78)
4. Spacewalk Thoughts (ambient, chill, energy 0.28) - Score: 3.94
   Because: mood match (+1.5); energy 0.28 vs target 0.40 (+1.52); acoustic fit (+0.92)
5. Coffee Shop Stories (jazz, relaxed, energy 0.37) - Score: 2.77
   Because: energy 0.37 vs target 0.40 (+1.88); acoustic fit (+0.89)
```

**Deep Intense Rock**

```
Profile: Deep Intense Rock
Prefs:   {'favorite_genre': 'rock', 'favorite_mood': 'intense', 'target_energy': 0.9, 'likes_acoustic': False}
1. Storm Runner (rock, intense, energy 0.91) - Score: 6.36
   Because: genre match (+2.0); mood match (+1.5); energy 0.91 vs target 0.90 (+1.96); acoustic fit (+0.90)
2. Gym Hero (pop, intense, energy 0.93) - Score: 4.33
   Because: mood match (+1.5); energy 0.93 vs target 0.90 (+1.88); acoustic fit (+0.95)
3. Neon Euphoria (edm, euphoric, energy 0.95) - Score: 2.78
   Because: energy 0.95 vs target 0.90 (+1.80); acoustic fit (+0.98)
4. Iron Furnace (metal, angry, energy 0.97) - Score: 2.69
   Because: energy 0.97 vs target 0.90 (+1.72); acoustic fit (+0.97)
5. Sunrise City (pop, happy, energy 0.82) - Score: 2.50
   Because: energy 0.82 vs target 0.90 (+1.68); acoustic fit (+0.82)
```

### Adversarial / edge-case profiles

**Conflicted: Sad but High-Energy**

```
Profile: Conflicted: Sad but High-Energy
Prefs:   {'favorite_genre': 'classical', 'favorite_mood': 'sad', 'target_energy': 0.9, 'likes_acoustic': False}
1. Nocturne in Grey (classical, sad, energy 0.15) - Score: 3.53
   Because: genre match (+2.0); mood match (+1.5); energy 0.15 vs target 0.90 (+0.00); acoustic fit (+0.03)
2. Storm Runner (rock, intense, energy 0.91) - Score: 2.86
   Because: energy 0.91 vs target 0.90 (+1.96); acoustic fit (+0.90)
3. Gym Hero (pop, intense, energy 0.93) - Score: 2.83
   Because: energy 0.93 vs target 0.90 (+1.88); acoustic fit (+0.95)
4. Neon Euphoria (edm, euphoric, energy 0.95) - Score: 2.78
   Because: energy 0.95 vs target 0.90 (+1.80); acoustic fit (+0.98)
5. Iron Furnace (metal, angry, energy 0.97) - Score: 2.69
   Because: energy 0.97 vs target 0.90 (+1.72); acoustic fit (+0.97)
```

**Ghost Genre: K-Pop / Dreamy**

```
Profile: Ghost Genre: K-Pop / Dreamy
Prefs:   {'favorite_genre': 'k-pop', 'favorite_mood': 'dreamy', 'target_energy': 0.6, 'likes_acoustic': True}
1. Porch Light Memories (country, nostalgic, energy 0.52) - Score: 2.33
   Because: energy 0.52 vs target 0.60 (+1.68); acoustic fit (+0.65)
2. Midnight Coding (lofi, chill, energy 0.42) - Score: 1.99
   Because: energy 0.42 vs target 0.60 (+1.28); acoustic fit (+0.71)
3. Focus Flow (lofi, focused, energy 0.40) - Score: 1.98
   Because: energy 0.40 vs target 0.60 (+1.20); acoustic fit (+0.78)
4. Coffee Shop Stories (jazz, relaxed, energy 0.37) - Score: 1.97
   Because: energy 0.37 vs target 0.60 (+1.08); acoustic fit (+0.89)
5. Library Rain (lofi, chill, energy 0.35) - Score: 1.86
   Because: energy 0.35 vs target 0.60 (+1.00); acoustic fit (+0.86)
```

**Out-of-Range Energy (1.5)**

```
Profile: Out-of-Range Energy (1.5)
Prefs:   {'favorite_genre': 'edm', 'favorite_mood': 'euphoric', 'target_energy': 1.5, 'likes_acoustic': False}
1. Neon Euphoria (edm, euphoric, energy 0.95) - Score: 4.48
   Because: genre match (+2.0); mood match (+1.5); energy 0.95 vs target 1.50 (+0.00); acoustic fit (+0.98)
2. Iron Furnace (metal, angry, energy 0.97) - Score: 0.97
   Because: energy 0.97 vs target 1.50 (+0.00); acoustic fit (+0.97)
3. Gym Hero (pop, intense, energy 0.93) - Score: 0.95
   Because: energy 0.93 vs target 1.50 (+0.00); acoustic fit (+0.95)
4. Storm Runner (rock, intense, energy 0.91) - Score: 0.90
   Because: energy 0.91 vs target 1.50 (+0.00); acoustic fit (+0.90)
5. Concrete Verses (hip hop, energetic, energy 0.80) - Score: 0.88
   Because: energy 0.80 vs target 1.50 (+0.00); acoustic fit (+0.88)
```

**Messy Input: 'LOFI' / 'Chill', no acoustic key**

```
Profile: Messy Input: 'LOFI' / 'Chill', no acoustic key
Prefs:   {'favorite_genre': 'LOFI', 'favorite_mood': 'Chill', 'target_energy': 0.4}
1. Midnight Coding (lofi, chill, energy 0.42) - Score: 5.71
   Because: genre match (+2.0); mood match (+1.5); energy 0.42 vs target 0.40 (+1.92); acoustic fit (+0.29)
2. Library Rain (lofi, chill, energy 0.35) - Score: 5.44
   Because: genre match (+2.0); mood match (+1.5); energy 0.35 vs target 0.40 (+1.80); acoustic fit (+0.14)
3. Focus Flow (lofi, focused, energy 0.40) - Score: 4.22
   Because: genre match (+2.0); energy 0.40 vs target 0.40 (+2.00); acoustic fit (+0.22)
4. Spacewalk Thoughts (ambient, chill, energy 0.28) - Score: 3.10
   Because: mood match (+1.5); energy 0.28 vs target 0.40 (+1.52); acoustic fit (+0.08)
5. Velvet Promise (r&b, romantic, energy 0.48) - Score: 2.36
   Because: energy 0.48 vs target 0.40 (+1.68); acoustic fit (+0.68)
```

---

## Experiments You Tried

### Weight shift: halve genre, double energy

**Change:** `GENRE_WEIGHT` 2.0 → 1.0 and `ENERGY_WEIGHT` 2.0 → 4.0 (mood 1.5 and acoustic 1.0 unchanged). I ran this temporarily by overriding the constants, then kept the original Strategy B weights in `recommender.py`.

**Math check:** the maximum score becomes 1.0 + 1.5 + 4.0 + 1.0 = **7.5**. A perfect song (lofi, chill, energy 0.40, acousticness 1.0) scored exactly 7.5 for the Chill Lofi profile, and every score across all 7 profiles and 18 songs stayed between 0 and 7.5, so the formula is still valid.

**Top 5, before → after:**

| Profile | Before (Strategy B) | After (genre 1.0, energy 4.0) |
|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights, Concrete Verses, Storm Runner | Sunrise City, **Rooftop Lights, Gym Hero**, Concrete Verses, Storm Runner |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories | **Midnight Coding, Library Rain**, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories |
| Deep Intense Rock | Storm Runner, Gym Hero, Neon Euphoria, Iron Furnace, Sunrise City | unchanged |
| Conflicted: Sad but High-Energy | **Nocturne in Grey**, Storm Runner, Gym Hero, Neon Euphoria, Iron Furnace | Storm Runner, Gym Hero, Neon Euphoria, Iron Furnace, **Sunrise City** (Nocturne in Grey drops out) |

**More accurate or just different?** Mostly just different. The top song stayed the same for 3 of the 4 profiles, and the changes were mostly neighbors swapping places:
- **High-Energy Pop:** Rooftop Lights (indie pop, *happy*) moved above Gym Hero (pop, *intense*). That arguably fits a happy-pop listener better.
- **Chill Lofi:** Midnight Coding overtook Library Rain because its energy is closer to 0.40.
- **Conflicted profile:** the sad classical song disappeared entirely, and the list became generic loud tracks. With energy worth 4.0, the system now ignores the listener's genre and mood whenever they disagree with their energy.

I kept the original weights because the experiment traded one bias (labels beat sound) for the opposite one (energy beats everything).

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



