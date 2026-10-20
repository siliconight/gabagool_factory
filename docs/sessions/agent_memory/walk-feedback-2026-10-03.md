---
name: walk-feedback-2026-10-03
description: "Walker's feedback from walking _runs/walk_export_moving (2026-10-03): streetlights not lighting the lot (FIXED Lux 0.64.0: the 12 poles with shadow maps were blacked by their own shaft cap 5 mm under the lamp; the cap/leak finding was a wrong cause, retracted); crowns move as a blob (reworked); entry walkways end at blank walls (Lot centre-to-centre paths, open); heat lamp shipped"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-03T16:01:33.169Z
---

Walked on 2026-10-03 after the crowns shipped. Four items, with what was found:

1. **"quite a few street lamps that aren't putting their light down"**, then
   "this one far away is working but the one closer isn't". FIXED, Lux
   0.64.0 (`patches/patch_lux_streetlight_hang.py`); walker, same day: "lights
   are working now". The first cause written
   down (indoor light leaking onto lot tiles over the 8-light cap, a cap of
   16 priced at +2 ms GPU and refused) was WRONG for the poles and is kept
   as a retraction in `docs/findings/light_cap/NOTES.md`. Measured: 12 of 17
   poles drew nothing, exactly the 12 `apply_shadow_policy` gave shadow maps
   (the High tier's budget, picked by a string sort of paths); the caster
   was the pole's own shaft cap, 5 mm under the lamp (a 6 cm disc that
   close fills the whole 55-degree shadow frustum). `LuxStreetlightRig.
   LAMP_HANG_M` 0.10 hangs the lamp below the lens point; selftest
   `lux/tools/streetlight_shadow_selftest.gd` (windowed) holds it; the
   general instrument is `lux/tools/self_shadow_census.gd`. SUPERSEDED by Lux 0.65.0: the 0.10 hang put the lamp INSIDE the
   pole's shaft (cap 5 mm under the mount); real time hid it (shadow maps cull
   inside faces), the light bake baked those poles to nothing. The lamp now
   sits 0.2 m along the head, 1 cm under the lens. Lesson: check where a
   moved light sits against the SOLIDS around it, not only that the frame
   looks right. Earlier lesson: a light
   that renders nothing with no stored property wrong is a shadow-map
   question first -- toggle `shadow_caster_mask` to 0 before anything else.
   Open: the policy's tie-break (string sort) makes WHICH poles get shadows
   an accident of ids.
2. **"the wind on the leaves doesn't look great ... just a big blob moving
   ... branches don't move unless the wind is really strong, only the
   leaves."** Shader reworked (LF worldskin, SWAY_LEAN_FROM_MS 3.0): the mass
   leans only above 3 m/s; the facets flutter per-vertex (phase from the UV
   hash) across the wind and up, 12 mm at the top in a breath. Walker:
   "trees look better, but I think the species need changes". Still open:
   the crown LOOK -- branches and leaves do not read as different things; a
   Zoo species item (cutout leaf cards or smaller masses showing twig).
3. **"sidewalks don't consistently lead up to doors which seems random"**,
   then "lot still not drawing walkways to open doorways". SHIPPED, Lot
   0.88.0 (`patches/patch_lot_door_paths.py`): `site_paths.snap_to_doors`
   moves every building-owned path end to the nearest ground door on the
   facade it meets (the bank's spur slid 9 m; it had been LF's door spur at
   the building's centre x, not a from/to path). Walk copy:
   `_runs/walk_export_paths`. OPEN and bigger: 312 of 920 door spurs across
   the lots on disk face a wall with NO ground door (LF draws a spur to
   every road-facing face and rotates buildings blind to doors); now a
   printed finding `LOT_PATH_END_OFF_DOOR`. Walker on the 8 m door-to-door bands:
   "these look goofy" -> Lot 0.89.0 draws them as square 3 m legs.
   Then "still have sidewalks going to walls" (a walk to the bank's BREACH:
   the gate counts breaches, garages, vaultable windows as ways in) and
   "research what looks more natural ... between the sides of 2 buildings".
   Lot 0.91.0: walks lead only to kind `door`; no walk to a doorless wall or
   between two buildings (records kept for the street graph); every other
   door gets a 60 in landing (building code). Research in
   `docs/findings/entry_paths/NOTES.md`. Walk copy `_runs/walk_export_landings`.
   Open: a deliberate link between buildings (strip of shops) would be facade
   walks + one square marked crossing; not built. Recommended to the walker: stop
   drawing those walks first, then rotate buildings door-to-street as its
   own piece. Awaiting the walker's call. `docs/findings/entry_paths/`.
4. **"a dim but warm warming light to bring a bit more light to the dogs"**,
   then **"light should show the buns too."** SHIPPED: Zoo 1.57.0 + 1.57.1
   and Lux 0.63.0 (`heat_lamp` rig: an OMNI, 1,900 K, HEAT_LAMP_LEVEL 0.16,
   HEAT_LAMP_ATTENUATION 0.6, range 0.9 m). Lessons: a light a hand's width
   from its subject at the inverse square is a floodlight; `export` does NOT
   rerun lux_apply -- a Lux change needs `run --art --gameplay` (the job
   fingerprint carries the dirty-tree hash). `docs/findings/heat_lamp/`.

**How to apply:** the walker's eye set these; keep the measurements beside the
constants. Never `rm`/`cp` a walk folder by a relative path -- the cwd
drifts, and `_runs/walk_export_moving` was once emptied under a running
Godot; check `tasklist` for godot first. Related: [[work-order-after-crowns]],
[[moving-parts-shipped]].
