# Sample Runs (reproducible execution evidence)

Captured with Python 3.13.18 on 2026-11-19. Re-run any command below from the repo root to reproduce.

## `python -m src.cli "chill music for studying" --trace`

```text
Request: "chill music for studying"
Profile: genre=lofi, mood=focused, energy=0.37, acoustic=True
Based on: [n01] Studying and deep focus (matched: study); [n02] Late night wind down (matched: chill); [n07] Space and atmosphere (matched: chill)
Confidence: 0.98

1. Focus Flow by LoRoom [lofi, focused] score 4.84
   why: genre match (+2.0), mood match (+1.0), energy close to target (+1.46), acoustic fit (+0.39)
2. Library Rain by Paper Lanterns [lofi, chill] score 3.90
   why: genre match (+2.0), energy close to target (+1.47), acoustic fit (+0.43)
3. Midnight Coding by LoRoom [lofi, chill] score 3.03
   why: genre match (+2.0), energy close to target (+1.42), acoustic fit (+0.35), repeat artist (-0.75)
4. Coffee Shop Stories by Slow Stereo [jazz, relaxed] score 1.95
   why: energy close to target (+1.50), acoustic fit (+0.45)
5. Spacewalk Thoughts by Orbit Bloom [ambient, chill] score 1.82
   why: energy close to target (+1.36), acoustic fit (+0.46)

Agent trace:
  GUARD: request accepted (24 chars)
  PLAN: explicit hints none
  RETRIEVE: n01 Studying and deep focus (0.40), n02 Late night wind down (0.21), n07 Space and atmosphere (0.13)
  PROFILE: {'genre': 'lofi', 'mood': 'focused', 'energy': 0.37, 'likes_acoustic': True}
  CHECK: confidence 0.98, output problems none
```

## `python -m src.cli "I need something for the gym" --trace`

```text
Request: "I need something for the gym"
Profile: genre=pop, mood=intense, energy=0.92, acoustic=False
Based on: [n03] Workout and gym (matched: gym)
Confidence: 1.00

1. Gym Hero by Max Pulse [pop, intense] score 4.96
   why: genre match (+2.0), mood match (+1.0), energy close to target (+1.48), acoustic fit (+0.47)
2. Sunrise City by Neon Echo [pop, happy] score 3.76
   why: genre match (+2.0), energy close to target (+1.35), acoustic fit (+0.41)
3. Storm Runner by Voltline [rock, intense] score 2.94
   why: mood match (+1.0), energy close to target (+1.48), acoustic fit (+0.45)
4. Bassline Riot by Kilowatt Kids [edm, euphoric] score 1.93
   why: energy close to target (+1.44), acoustic fit (+0.48)
5. Ashes and Iron by Grave Signal [metal, angry] score 1.92
   why: energy close to target (+1.43), acoustic fit (+0.49)

Agent trace:
  GUARD: request accepted (28 chars)
  PLAN: explicit hints none
  RETRIEVE: n03 Workout and gym (0.41)
  PROFILE: {'genre': 'pop', 'mood': 'intense', 'energy': 0.92, 'likes_acoustic': False}
  CHECK: confidence 1.00, output problems none
```

## `python -m src.cli "jazz for a dinner date" --trace`

```text
Request: "jazz for a dinner date"
Profile: genre=jazz, mood=relaxed, energy=0.43, acoustic=True
Based on: [n08] Coffee shop evening (matched: dinner, jazz); [n12] Date night (matched: date)
Confidence: 0.98

1. Coffee Shop Stories by Slow Stereo [jazz, relaxed] score 4.86
   why: genre match (+2.0), mood match (+1.0), energy close to target (+1.41), acoustic fit (+0.45)
2. Island Morning by Tide Rhythm [reggae, relaxed] score 2.56
   why: mood match (+1.0), energy close to target (+1.32), acoustic fit (+0.24)
3. Focus Flow by LoRoom [lofi, focused] score 1.85
   why: energy close to target (+1.46), acoustic fit (+0.39)
4. Library Rain by Paper Lanterns [lofi, chill] score 1.81
   why: energy close to target (+1.38), acoustic fit (+0.43)
5. Back Porch Letters by Willow Creek [country, nostalgic] score 1.79
   why: energy close to target (+1.42), acoustic fit (+0.37)

Agent trace:
  GUARD: request accepted (22 chars)
  PLAN: explicit hints {'genre': 'jazz'}
  RETRIEVE: n08 Coffee shop evening (0.35), n12 Date night (0.25)
  PROFILE: {'genre': 'jazz', 'mood': 'relaxed', 'energy': 0.43, 'likes_acoustic': True}
  CHECK: confidence 0.98, output problems none
```

## `python -m src.cli "k-pop bangers" --trace`

```text
Request: "k-pop bangers"
Profile: genre=k-pop, mood=happy, energy=0.8, acoustic=False
Based on: [n19] Indie pop brightness (matched: pop); [n04] Feel good sunshine (matched: pop); [n03] Workout and gym (matched: pop)
Confidence: 0.35

1. Sunrise City by Neon Echo [pop, happy] score 2.88
   why: mood match (+1.0), energy close to target (+1.47), acoustic fit (+0.41)
2. Rooftop Lights by Indigo Parade [indie pop, happy] score 2.77
   why: mood match (+1.0), energy close to target (+1.44), acoustic fit (+0.33)
3. Concrete Crown by Blockwise [hip hop, confident] score 1.91
   why: energy close to target (+1.47), acoustic fit (+0.44)
4. Ritmo de Noche by Calle Luna [latin, energetic] score 1.83
   why: energy close to target (+1.43), acoustic fit (+0.40)
5. Storm Runner by Voltline [rock, intense] score 1.78
   why: energy close to target (+1.33), acoustic fit (+0.45)
WARNING: Low confidence (0.35). Results may not match what you meant.
WARNING: Genre 'k-pop' is not in the catalog.

Agent trace:
  GUARD: request accepted (13 chars)
  PLAN: explicit hints {'genre': 'k-pop'}
  RETRIEVE: n19 Indie pop brightness (0.48), n04 Feel good sunshine (0.17), n03 Workout and gym (0.16)
  PROFILE: {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False}
  CHECK: confidence 0.35, output problems none
```

## `python -m src.cli "quiet piano" --trace`

```text
Request: "quiet piano"
Profile: genre=classical, mood=melancholy, energy=0.3, acoustic=True
Based on: [n14] Grief and reflection (matched: piano); [n17] Sad and alone (matched: quiet); [n08] Coffee shop evening (matched: piano)
Confidence: 0.40

1. Requiem for Rain by Halden Quartet [classical, melancholy] score 4.83
   why: genre match (+2.0), mood match (+1.0), energy close to target (+1.35), acoustic fit (+0.48)
2. Spacewalk Thoughts by Orbit Bloom [ambient, chill] score 1.93
   why: energy close to target (+1.47), acoustic fit (+0.46)
3. Library Rain by Paper Lanterns [lofi, chill] score 1.85
   why: energy close to target (+1.42), acoustic fit (+0.43)
4. Coffee Shop Stories by Slow Stereo [jazz, relaxed] score 1.84
   why: energy close to target (+1.40), acoustic fit (+0.45)
5. Empty Station by Ghost Tapes [indie, sad] score 1.79
   why: energy close to target (+1.46), acoustic fit (+0.33)
WARNING: Low confidence (0.40). Results may not match what you meant.

Agent trace:
  GUARD: request accepted (11 chars)
  PLAN: explicit hints {'energy': 0.3}
  RETRIEVE: n14 Grief and reflection (0.14), n17 Sad and alone (0.13), n08 Coffee shop evening (0.13)
  PROFILE: {'genre': 'classical', 'mood': 'melancholy', 'energy': 0.3, 'likes_acoustic': True}
  CHECK: confidence 0.40, output problems none
  REVISE: tried next note n17, confidence 0.36
  REVISE: kept original profile
```

## `python -m src.cli "asdf qwerty" --trace`

```text
Request: "asdf qwerty"
Profile: genre=None, mood=None, energy=0.5, acoustic=False
Confidence: 0.00

1. Velvet Hours by Amara Soul [r&b, romantic] score 1.77
   why: energy close to target (+1.47), acoustic fit (+0.30)
2. Island Morning by Tide Rhythm [reggae, relaxed] score 1.68
   why: energy close to target (+1.42), acoustic fit (+0.26)
3. Back Porch Letters by Willow Creek [country, nostalgic] score 1.60
   why: energy close to target (+1.47), acoustic fit (+0.13)
4. Midnight Coding by LoRoom [lofi, chill] score 1.52
   why: energy close to target (+1.38), acoustic fit (+0.15)
5. Concrete Crown by Blockwise [hip hop, confident] score 1.52
   why: energy close to target (+1.08), acoustic fit (+0.44)
WARNING: No vibe notes matched; showing a neutral mid-energy mix. Try naming an activity, mood or genre.
WARNING: Low confidence (0.00). Results may not match what you meant.

Agent trace:
  GUARD: request accepted (11 chars)
  PLAN: explicit hints none
  RETRIEVE: no matching notes
  PROFILE: {'genre': None, 'mood': None, 'energy': 0.5, 'likes_acoustic': False}
  CHECK: confidence 0.00, output problems none
```

## `python -m src.cli "" --trace`

```text
Sorry, I can't run that request: Request is empty. Try something like 'chill music for studying'.
```

## `python -m pytest -q`

```text
...........................                                              [100%]
27 passed in 0.05s
```

## `python -m src.evaluate`

```text
[PASS] 'chill music for studying'                    conf=0.98  Pass
[PASS] 'I need something for the gym'                conf=1.0  Pass
[PASS] 'breakup, feeling sad and alone'              conf=0.98  Pass
[PASS] 'jazz for a dinner date'                      conf=0.98  Pass
[PASS] 'angry, need to vent'                         conf=1.0  Pass
[PASS] 'late night drive through the city'           conf=0.92  Pass
[PASS] 'party with friends on friday night'          conf=0.75  Pass
[PASS] 'yoga and meditation'                         conf=0.88  Pass
[PASS] 'missing my hometown'                         conf=0.98  Pass
[PASS] 'something uplifting for sunday morning'      conf=0.96  Pass
[PASS] 'k-pop bangers'                               conf=0.35  Pass
[PASS] 'asdf qwerty'                                 conf=0.0  Pass
[PASS] '(empty)'                                     conf=None  Pass: Request is empty. Try something like 'chill music for studying'.
[PASS] 'music'                                       conf=0.0  Pass

14 out of 14 cases passed. Average confidence 0.75 across 13 answered requests (0.94 on in-catalog requests).
Table written to eval/results.md
```

## Excerpt of `logs/vibefinder.log`

```text
2026-11-18 20:39:27,395 WARNING vibefinder.agent: Genre 'k-pop' is not in the catalog.
2026-11-18 20:39:27,395 INFO vibefinder.agent: confidence=0.35 top=['Sunrise City', 'Rooftop Lights', 'Concrete Crown']
2026-11-18 20:39:27,448 INFO vibefinder.agent: query='quiet piano'
2026-11-18 20:39:27,450 INFO vibefinder.agent: retrieved=[('n14', 0.144), ('n17', 0.129), ('n08', 0.125)]
2026-11-18 20:39:27,450 WARNING vibefinder.agent: Low confidence (0.40). Results may not match what you meant.
2026-11-18 20:39:27,450 INFO vibefinder.agent: confidence=0.40 top=['Requiem for Rain', 'Spacewalk Thoughts', 'Library Rain']
2026-11-18 20:39:27,504 INFO vibefinder.agent: query='asdf qwerty'
2026-11-18 20:39:27,506 INFO vibefinder.agent: retrieved=[]
2026-11-18 20:39:27,506 WARNING vibefinder.agent: No vibe notes matched; showing a neutral mid-energy mix. Try naming an activity, mood or genre.
2026-11-18 20:39:27,506 WARNING vibefinder.agent: Low confidence (0.00). Results may not match what you meant.
2026-11-18 20:39:27,506 INFO vibefinder.agent: confidence=0.00 top=['Velvet Hours', 'Island Morning', 'Back Porch Letters']
2026-11-18 20:39:27,561 WARNING vibefinder.cli: rejected: Request is empty. Try something like 'chill music for studying'.
```
