# 🎧 Model Card: VibeMatch 1.0

## 1. Model Name

**VibeMatch 1.0**. It matches songs to a listener's vibe.

---

## 2. Goal / Task

VibeMatch suggests songs a listener will probably like.
It gives every song a score based on how well the song fits the listener's taste.
Then it shows the top 5 songs, with a short reason for each score.
It does not learn from what people play or skip. It only compares song features to the listener's stated preferences.

---

## 3. Data Used

- The catalog has **18 songs** in `data/songs.csv`.
- The starter file had 10 songs. I added 8 more to cover more styles, such as metal, classical, country, reggaeton and edm.
- Each song has: genre, mood, energy, tempo, valence, danceability and acousticness.
- There are 15 genres and 14 moods.
- Most genres and moods appear only once. Lofi is the biggest genre, with 3 songs.

**Limits:**
- 18 songs is tiny. Real apps have millions.
- Many tastes are missing, such as k-pop, Latin pop, punk and gospel.
- The numbers (energy, acousticness) were written by hand. They are not measured from real audio.
- There are no lyrics, languages, release years or artist popularity.

---

## 4. Algorithm Summary

Every song starts at 0 points and can earn up to 6.5 points.

- **Genre match: +2.0.** The song's genre is the listener's favorite genre.
- **Mood match: +1.5.** The song's mood is the listener's favorite mood.
- **Energy: up to +2.0.** A song with exactly the listener's target energy gets the full 2 points. The further away it is, the fewer points it gets. If it is 0.5 or more away, it gets 0.
- **Acoustic fit: up to +1.0.** If the listener likes acoustic music, more acoustic songs get more points. If not, less acoustic songs get more points.

Then the system sorts all songs from highest to lowest score and keeps the top 5.

Genre counts a bit more than mood. Genre is the most stable part of someone's taste. But mood is close behind, so a song with the right vibe can still rank well.

---

## 5. Observed Behavior / Biases

**The main bias: labels beat sound.**
A genre match plus a mood match is worth 3.5 points.
Energy and acoustic fit together can only add up to 3.0.
So a song with the right labels always wins, even if it sounds wrong.

Example: I tested a listener who wanted sad classical music at high energy (0.90).
Nocturne in Grey ranked #1. It is classical and sad, but its energy is only 0.15.
It got **zero** energy points and still won.

**Filter bubble for rare tastes.**
Lofi has 3 songs, but most genres have 1. A genre that isn't in the catalog has 0.
A k-pop fan never gets genre points.
Their top 5 is just "whatever is closest in energy." All of those scores are crowded between 1.86 and 2.33.

**Other patterns:**
- **Gym Hero shows up in 4 of my 7 test lists.** It is loud and not acoustic, so it scores well for any high-energy listener.
- **Missing preferences hurt.** If `likes_acoustic` is missing, the system assumes the listener dislikes acoustic music.
- **Bad input is not caught.** A target energy of 1.5 makes every song earn 0 energy points, and no error appears.
- **No variety.** The same artist can fill the top spots. LoRoom has 2 of the top 3 songs for the lofi listener.
- **Some features are ignored.** Tempo, valence and danceability are stored but not scored.

---

## 6. Evaluation Process

I ran `python -m src.main` with 7 listener profiles and checked each top 5. The full output is in the README.

| Profile | Genre / Mood | Energy | Likes acoustic | Why I tested it |
|---|---|---|---|---|
| High-Energy Pop | pop / happy | 0.85 | No | Normal listener |
| Chill Lofi | lofi / chill | 0.40 | Yes | Normal listener |
| Deep Intense Rock | rock / intense | 0.90 | No | Normal listener |
| Sad but High-Energy | classical / sad | 0.90 | No | Preferences that conflict |
| K-Pop / Dreamy | k-pop / dreamy | 0.60 | Yes | Genre and mood not in the catalog |
| Out-of-Range Energy | edm / euphoric | 1.50 | No | Invalid input |
| Messy Input | "LOFI" / "Chill" | 0.40 | (missing) | Capital letters and a missing setting |

**Did it feel right?**
For the 3 normal listeners, yes.
Sunrise City, Library Rain and Storm Runner were the songs I would have picked myself.
The edge cases are where it broke, as described in section 5.

**Comparing profiles:**
- **Pop vs Lofi:** no songs in common. Pop gets loud, non-acoustic songs. Lofi gets quiet, acoustic ones. That makes sense, because they differ on every rule.
- **Pop vs Rock:** 3 songs in common (Sunrise City, Gym Hero, Storm Runner). Both want loud music, so genre and mood decide the order.
- **Lofi vs Rock:** no songs in common, and their energy ranges are opposite. This shows the energy rule works.
- **Rock vs Sad but High-Energy:** both target 0.90 energy, so spots 2–5 are almost the same loud songs. Only #1 differs, because the quiet classical song wins on labels.
- **Lofi vs Messy Input:** the same top 4 songs, so capital letters don't matter. The missing acoustic setting changed the order and swapped out #5.
- **Lofi vs K-Pop:** the k-pop fan's best score is only 2.33, compared with 6.16. Their list is mostly lofi songs anyway, because lofi is the biggest group of mid-energy acoustic songs.
- **Out-of-Range vs Pop:** with energy at 1.5, energy stops counting. Below #1, the list is sorted only by acoustic fit.

**Experiment: halve genre, double energy.**
I changed genre from 2.0 to 1.0 and energy from 2.0 to 4.0. The max score became 7.5, and all scores stayed between 0 and 7.5.
The results were mostly *different*, not *better*.
- **Pop listener:** Rooftop Lights (happy) moved above Gym Hero (intense). That felt better.
- **Sad but High-Energy listener:** they lost their only sad song. That felt worse.

I kept the original weights.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom project for learning how recommenders turn data into rankings.
- Trying out scoring rules and seeing how weights change results.
- Small, made-up catalogs where every score can be explained.

**Not intended for:**
- Real users or a real music app. The catalog is too small and the numbers are made up.
- Judging what music is "good." The score only measures fit with one person's stated preferences.
- Listeners whose taste isn't in the catalog. They will get weak, near-random results.
- Any decision that matters, such as which artists get promoted or paid.

---

## 8. Ideas for Improvement

1. **Give partial credit for similar labels.** For example, "relaxed" could count as close to "chill," and "indie pop" as close to "pop." This would help listeners with rare tastes.
2. **Add variety to the top 5.** Limit each artist to one spot, and lower the score of songs that already appear too often.
3. **Check input and use more features.** Reject energy outside 0–1, ask instead of guessing when a preference is missing, and score tempo, valence and danceability.

---

## 9. Personal Reflection

**What was your biggest learning moment during this project?**

My biggest learning moment was realizing that the “intelligence” of a recommender is really just the weights I choose. When I compared three scoring strategies, small changes completely reshuffled the ranking. With a vibe-first strategy, Spacewalk Thoughts (ambient/chill) beat Focus Flow (lofi/focused), even though my profile says my favorite genre is lofi. I picked a balanced strategy (genre +2.0, mood +1.5, energy up to 2.0, acoustic fit up to 1.0), and I understood that every number is a design decision with a tradeoff, not an objective truth. The energy cutoff taught me the same thing: with a gentle energy formula, a metal song at 0.97 energy still earned points for a calm profile, and only when I made songs 0.5 or more away earn zero did the loud tracks actually fall to the bottom.

**How did using AI tools help you, and when did you need to double-check them?**

AI helped most with brainstorming and boilerplate: it proposed three weighting strategies with tradeoffs, wrote load_songs with the csv module, and explained the difference between .sort() and sorted(). But I had to double-check it several times. I recalculated some of its scores by hand (Library Rain 6.16, Focus Flow 4.78, Spacewalk Thoughts 3.94) before trusting its recommendation. I also hit a real bug that came from the starter code: main.py imported from recommender import ..., which crashed with ModuleNotFoundError when I ran python -m src.main, so I changed it to from src.recommender import ... to match the tests. The lesson was to treat AI output as a draft I verify, especially numbers and anything about how my code actually runs.

**What surprised you about how simple algorithms can still “feel” like recommendations?**

I was surprised that a few if-statements and one distance formula could produce results that feel personal. For my lofi/chill/low-energy profile, the top picks were Library Rain and Midnight Coding, exactly the kind of music I’d put on to study, and intense tracks like Gym Hero landed at the bottom. The “Because” explanations made it feel even smarter, since each recommendation came with reasons like “genre match (+2.0); mood match (+1.5).” But I also saw how fragile it is: “relaxed” earns nothing toward “chill” and “indie pop” earns nothing toward “pop,” because the matching is exact. It feels intelligent only because the dataset is small and clean; it doesn’t actually understand music.

**What would you try next if you extended this project?**

First, I’d add partial credit for related moods and genres (for example, “relaxed” counting halfway toward “chill,” or “indie pop” toward “pop”) so the system stops treating near-matches as total misses. Second, I’d use the features I’m not scoring yet, like valence, danceability and tempo_bpm, and let the user choose how much each one matters. Third, I’d add a diversity rule so the top 5 isn’t dominated by one artist or genre. Finally, I’d test the recommender with several very different user profiles (for example, a high-energy workout listener) to check that the weights work for everyone and not just for my own taste.
