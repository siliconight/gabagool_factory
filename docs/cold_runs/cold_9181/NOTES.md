# Cold run 9181 -- 0 interventions; the generated Flappahs store, from a brief never run before

The proof run for the store work of 2026-10-06:
- Deli Counter 0.188.0: the `convenience_store` recipe; the window sign,
  posters and `preset` key on a generated store.
- Zoo 1.75.0: FLAPPAHS, and FLAPPAHS at a convenience store's door.
- Pixelcoat 0.58.0: FLAPPAHS alone in the gas and convenience families.
- Level Factory 0.146.0: the brief words, the generated row's family, and
  names-only dealing.

**The brief is new** (`briefs/convenience_001.json`):
- `convenience_store`, ONE building, a street block, at night.
- One building gets no lot library, so the store is generated from the
  recipe. That is the path the walker's request was about.
- It is also the first one-building brief on a street block. The only other
  one-building brief, `county_hospital_001`, is on a campus.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** The three
changed files were the candidates' `lf_*.json` specs, which the clock
attributes to the pipeline.

**The generated store** (`deli_counter/specs/lf_convenience_001_<seed>.json`,
all three seeds):
- `preset: convenience_store`.
- One `window_sign` and one `window_poster`.
- No pump and no canopy.
- The slush machine, roller grill, ATM, two video poker machines, coffee,
  cooler and gondolas.

**In the package** (`LF_convenience_001.portable-godot`):
- **The band:** `signs/sign_flappahs_*.png`, FLAPPAHS (`1 shop sign(s):
  b0=flappahs`).
- **The door box:** FLAPPAHS (`SignBox_Face_256x52_*`, read from the fixtures
  GLB's texture).
- **Inside:** the store's modules (slush machine, roller grill, video poker
  x2, ATM, coffee island, cooler run, snack gondola, counter, window neon,
  poster walls).
- No pump, canopy or pylon anywhere.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 29 findings.
  - seed_9181: 0 majors, and the driver picked it.
  - seed_9282: 1 major, `LT_MAP_ENEMY_PATHING_BROKEN`.
- **Art:** 0 blockers of 43 findings.
- **Bake:** 802 users, 33.3 s in the editor.
- **The driver's findings diff** (0 -> 43) is against 9180's workspace, a
  different mission. It counts this mission's findings, not a change.
- **Not priced:** one building, and no new look.

**Seen, not acted on:**
- **One brand, two colours.** The band is cream on red (Pixelcoat's FLAPPAHS
  panel and `flappahs_red.svg`). The door box is cream on green, the pylon's
  colourway 0 in Zoo (`price_pylon_forms.COLOURWAYS[0]`). Which one is the
  brand is the walker's call.
- **The extraction zone keeps the forecourt's id.**
  - `forecourt_extract` stands in front of the store, where the station's
    forecourt was: bounds [-12, -24, 12, -14] against a 32 x 22 footprint.
  - `gas_station(forecourt=False)` filters parts and rooms, not zones.
  - It works as an extraction area; only its name is the station's.
