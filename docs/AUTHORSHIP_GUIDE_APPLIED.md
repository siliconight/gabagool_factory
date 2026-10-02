# The authorship guide, applied to the factory

The walker, 2026-10-02, handed over `docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`
("Human Authorship in Procedural 3D Games") with: "adding this if it helps us
in the Gabagool Factory Level Factory". The guide is kept verbatim. This file
is the reading of it against what the factory does today: what already agrees,
where the factory falls short of it, and what changes because of it. Section
numbers are the guide's.

It bears directly on roadmap item 18 -- "works" and "good" are different
gates and only the first exists. The guide is the first written statement in
this repo of what "good" is made of.

## What the factory already does that the guide asks for

| Guide | Factory |
|---|---|
| A visual contract before assets (2) | `DELCO_1997_ART_DIRECTION.md`, `SET_DRESSING_REFERENCES.md`, `STREET_RULES.md` |
| Text is correct or a clean shape, never gibberish (8.1, 8.8) | Every painted string is written and denylisted (`card_brands`, the fake Delco brands); a line that does not set is reported in `unset`, not cropped |
| A small named type system (8.5) | `smooth_type` faces: display (Blue Highway bold), information (regular, condensed), utility (Minisystem) |
| Gutters and mip-safe padding round glyphs (8.6) | `card_art.atlas(gutter=, bleed=)` |
| Determinism, rejection rules, failure behaviour (13.1) | Seeded streams, genome budgets, `coincident_pairs`, a slot too small raises |
| No coplanar faces, no floating parts (6) | `coplanar_census`, `BURY`, the fit checks |
| Placement by anchors and clearances, not world coordinates (9.3.1) | Slots, `ATT_*` attachments, `REGISTER_CLEAR`, Lot's street rules |
| Review in the player camera (4, 14 step 10) | The walk copy; `look_shots`; in-level frames with every run |
| Profile, then simplify (14 step 11) | The fixed-station perf harness; draws as the budget |
| A golden set before a generator (2.3) | The real-look trial: four props taken to a standard before a rollout |

## Where the factory falls short of it

1. **Uniform treatment (1, 3.3, 7.3, 7.4).** The guide names "the same
   edge-wear mask repeated on every prop", "identical noise scale on wood,
   plastic, metal" and "every edge is beveled because it looks finished" as
   symptoms. `paint.py`'s `grain`, `edge_dark` and `vgrad` were applied to
   every panel of every trial prop at near-identical strengths, and every
   body got a chamfer. That is a uniform recipe. Each move needs a cause per
   prop: where a hand touches, where a mop reaches, what the part is made of.
2. **Wear has no cause (7.4).** Zoo's `Wear` attribute is a seeded amount per
   style. Nothing ties wear to contact, traffic, weather or repair.
3. **Hierarchy of care (1, 3.1).** Every prop of a species gets the same
   polish. Nothing in a room is visibly maintained, improvised or neglected
   relative to its neighbours.
4. **"Why is this here?" (9.4).** Furnishing fills slots from recipes. Rooms
   are not built round an activity, and density is not a per-zone budget.
5. **Repetition in view (5.4, 9.3.4).** Nothing tracks duplicate silhouettes
   or bright accents inside one camera region; only totals are counted.
6. **Text is not measured in the camera (8.6).** Legibility is checked in
   pixels on the atlas (`DIGIT_MIN_M`, `fit_cap`), never as projected height
   at the distance the player reads from, and never after compression.
7. **No review rubric (15).** A level is judged by findings and by the
   walker's eye. There is no recorded score for identity, silhouette,
   construction or composition.

## What changes because of it

**In the real-look rollout, starting now.** Each prop gets a short brief
before it is painted -- what it is made of, who touches it and where, what it
is for -- and the shading moves follow that brief instead of a house recipe.
Quiet surfaces stay quiet. A chamfer goes where a moulded or folded part
would have one. The four trial props are the golden set; a new prop is
compared with them in the level, not in a preview.

**Candidates for instruments, in the order they look cheapest.** None is
built; each would be a "good" gate where today there are none.

1. Text height in the camera: from a walk copy, project every lettered
   surface at its reading spot and report the ones under a per-class minimum
   (guide 8.6, 13.4). The in-level probe written for run 9135 already finds
   props by material and stands a camera in front of them.
2. Duplicate silhouettes per view: at the perf harness's stations, count
   repeated modules in the frustum (5.4, 9.3.4).
3. Density per room kind as an occupied-footprint range rather than a prop
   count (9.3.3, 9.3.7).
4. The review rubric (15) as a recorded score per cold run, filled in by a
   person. It is the one item that needs no code.

**Not adopted, and why.** The guide's warnings about AI-generated meshes and
pseudo-text (12) do not apply: nothing here is model-generated art; every
mesh is planned in code and every string is written. Its reference-board
discipline (18) is already how `SET_DRESSING_REFERENCES.md` is kept, and the
walker's own photographs remain the primary source.
