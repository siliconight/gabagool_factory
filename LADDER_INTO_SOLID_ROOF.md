# The ladder into the solid slab — cause, and the fix

It was never a slab. **Deli Counter cut the hole correctly; the art pass laid a
solid roof over it.**

Built and **held**, same as item 7. `patch_dc_roof_voids.py` is unapplied.
The pure half is proved here; the builder half needs your Blender rebuild.

---

## The evidence, in the order it closed

**1. The bot's own report.** `lot-demo-ws/.level_factory/preview/
lot_demo_001_walk/walkbot.json`, from the 08-09 run:

```json
"ladder": "Ladder_ladder_0", "climb": false, "top_exit": false,
"climb_height_reached": 2.1,
"stall": { "blocker": "Roof", "blocker_rel_y": 3.9,
           "aperture_z": [], "aperture_admits_capsule": false,
           "reason": "no opening at all at rel_y 3.90 -- the slab is solid over the ladder" }
```

`blocker` is **present**, so 3.90 is a measured height and not the probe's
`rel.y + 1.0` fallback. That distinction matters and the report cannot normally
show it — see the instrument notes at the end.

**2. Which building.** `bank_branch_a04` — the only one of the five placed with
a `Ladder_` node (3 hits; the other four have 0).

**3. The numbers close.** The node is at `(16.0, 4.2, −12.0)` with
`metadata/climb_height = 4.2` and `TopOfLadder` at local +4.0. So the storey
height is 4.2, the ladder runs storey 1 → 2, and 2 is the top. The top slab is
centred at `2×4.2 − 0.15` at thickness 0.3, spanning world **8.10–8.40**.
`blocker_rel_y 3.9` → world `4.2 + 3.9 = 8.10`. The slab underside, exact.

(The "3.9" in the 08-09 sweep table is the *wall* height — `4.2 − 0.3` floor
thickness, because `_cap_thick` stops walls under the slab. The two numbers
reconcile; they are not the same number twice.)

**4. The hole IS cut.** `slab_col_2-colonly` in the shipped `site_base.glb` has
**76 vertices** — a box has 8 — with vertices at exactly `x=15.45`, `x=16.55`,
`z=−10.90`, which is precisely
`ladder_geom.through_hole(16, 12, 0.5, "S")`. Deli Counter did its job.

**5. So what is `Roof`?** There is no node of that name among the 762 in
`site_base.glb`. The only other geometry at 8.10–8.40 is `roof_footprint`,
instancing `art/zoo/roof_rockay_01_w4000.glb` — Zoo's roof module, the full
40 m plan, `collision: trimesh`, no void. The bot's ray passed cleanly through
Deli Counter's hole and hit the themed roof coincident with it.

*(The Zoo `.glb` itself would not stage — HTTP 400, twice. That is the
hardlinked-file refusal this repo already records: the content-addressed cache
hard-links byte-identical modules. So step 5's last inch is inference from the
762-node listing rather than a direct read. `godot --headless` with the overlay,
or any glTF node dump of that file, settles it in one command.)*

---

## Two causes, and they compound

**The roof slot cannot express a hole.** `roofs._slot` emits
`"openings": []` and **no `voids` key at all**. `floors._slot` has carried
`voids` since the floor and ceiling skins were given theirs, with a comment
saying why the two names differ — `openings` is the wall contract, a hole in a
standing slab's x/z, a different shape. The roof was never given the other one.

**And it is derived before any hole exists.** `_record_roof_slots` was called
from `_slabs()` — **build step one**. `_ladders` does not append a hole until
step five; `_slab_holes_cut` runs at step eleven. So `spec.slab_holes` was empty
by construction at the moment the roof slot was built. `_record_slab_slots` sits
at step twelve, immediately after the cut, and its comment has said exactly why
since it was written:

> *"by here every stairwell, ramp and hatch has appended its hole, so a floor or
> ceiling skin can be given the same openings the slab just got."*

The roof never got that sentence applied to it.

**Why this one blocks and the others do not.** A floor or ceiling slot is
`collision: "none"` at `SKIN_THICK` — a forgotten void there is something you
see through and walk through. A roof slot is the slab's *real* thickness with
`collision: "trimesh"`. A forgotten void there is a wall. Of the three surfaces
that lay art over a cut slab, the roof is the only one where the bug is
gameplay-blocking, and it is the only one that was missed.

Simulated with the real functions in the real order, no Blender:

```
OLD ORDER (_slabs -> roof slot, then _ladders):   voids = []
NEW ORDER (_ladders -> cut -> roof slot):
    voids = [{x0: 15.45, y0: 10.9, x1: 16.55, y1: 12.2}]
```

— the same rectangle already measured in `slab_col_2-colonly`, to the
centimetre.

## Why five gates passed

L14 checks the hole against the footprint. L15 checks partitions crossing it.
The compose gate counts climb volumes. `test_ladder_geom` checks the hole's
geometry. `nav_gate` bakes the greybox. **Every one of them checks Deli
Counter's own geometry, which was correct.** Nothing checks that what is laid
*on* the slab preserves the opening.

So this is greybox-clean and themed-broken. "The ladder used to work" is true,
nothing regressed, and it will reproduce on any building whose ladder reaches
the roof — this is not one bad shell.

---

## The fix

Two edits, both mirroring code already in the tree.

* **`roofs._slot` gains `voids`**, and `roof_slots` fills it from
  `floors.room_voids` — imported, not restated, the same rule `ladder_geom`
  states for the hole itself. `room_voids` clips to the rect it is handed and
  **never reads its `room` argument**, so it was already the general function
  this needed. (That dead parameter is its own small finding — the repo's
  "an unused parameter is an unfinished thought" rule, hit again.)
* **`_record_roof_slots` moves** out of `_slabs()` to sit beside
  `_record_slab_slots`, after `_slab_holes_cut`. It now takes its own geometry
  rather than the slab loop's, so the call site is free to move. `roof: "none"`
  still emits nothing; `"open"` still emits, per the original comment.

7 new cases in `test_roofs.py`, all failing on the pre-patch file with
`KeyError: 'voids'`. They include the clean case — a roof over nothing gets
`voids == []` — because "it cut the hole for the broken building" cannot tell
you it would not also punch one in a solid roof. The regression case rebuilds
`bank_branch_a04`'s real numbers and asserts the void admits the climbing
capsule at `CLIMB_STANDOFF ± capsule radius`.

```
test_roofs  test_floors  test_ladder_geom  test_partition_bounds
test_lights_voids  test_ladder_hatch          all green, before and after
```

Apply / `--check` / `--revert` round-trips to the exact original byte counts
(2,823 / 125,456 / 2,216). Refuses on drift with a whole-file SHA-256.

**One slot-order note.** Roof slots used to be the *first* entries in the
manifest; they now sit after the wall and opening slots, before floors and
ceilings. Nothing reads slot order — `plan_kit` buckets by dims — but the
manifest bytes change, so the fingerprint changes and those jobs re-run. That
was going to happen anyway, since the roof slot's content changes.

---

## What this does not prove

The builder half needs Blender. Sequence:

```
$env:BLENDER="C:\blender\blender.exe"
cd C:\Projects\gabagool_studios\gabagool_factory\deli_counter
python patch_dc_roof_voids.py --check
python patch_dc_roof_voids.py
python test_roofs.py
python build.py specs\bank_branch_a04.json --out build\bank_branch_a04.glb --blender $env:BLENDER
```

Then confirm the roof slot carries a void:

```
python -c "import json;d=json.load(open(r'build\bank_branch_a04.slots.json'));print([s['fit'].get('voids') for s in d['slots'] if s['role']=='roof'])"
```

Then the full run, and the walk — where the bot should report `climb: true,
top_exit: true` for `Ladder_ladder_0`, and you should be able to come out on
the roof by eye.

**Sequencing.** This is a fourth unverified change on top of three, in a second
repo. The order that respects the state-of-the-tree note is unchanged: verify
the six first, then `cache forget`, then walk — and the walk is now worth more,
because it has something specific to look for.

---

## Instruments — three things the walk bot should say and does not

None of these caused the bug; all three made it harder to find, and the first
one sent everybody to the wrong file for two days.

**It names a cause in its reason string.** `"the slab is solid over the ladder"`
— it was not a slab, and its own `blocker` field said `Roof` one key away. The
hard rule in `CLAUDE.md` is that a probe prints what it measured and stops; the
cause belongs in the reply where it can be argued with. Here the fixed sentence
outranked the measurement beside it.

**`probe_y` silently substitutes.** When neither overhead ray hits,
`probe_y = rel.y + 1.0` — a height nothing was measured at — and the reason
string is byte-identical to the measured case. A reader cannot tell whether
`3.90` is a slab or an offset from where the bot got stuck. It happened to be
measured this time. That is the exact defect the Instruments rule opens with: a
cheap observable standing in for an expensive truth with nothing recording the
substitution.

**The aperture sweep varies `z` only, at hardcoded local `x = 0`.** Its own
docstring names both axes — *"X across the ladder, Z out from its face"* — and
it never sweeps x. A hole present but offset *across* the ladder would report
`aperture_z: []`, "no opening at all", identically to a solid roof.
