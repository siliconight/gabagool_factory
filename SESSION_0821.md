# SESSION_0821 — the tintable-pack set, and four silent fallbacks

Released `factory-v1.31.0` (`e11eaba`). Everything below is committed and
tagged. The one thing that does NOT work is `export`, deliberately: a gate
blocks it and the reason is not yet known. Nothing was forced.

---

## What shipped

| tool | from | to | tag | commit |
|---|---|---|---|---|
| zoo | 0.38.0 | **0.44.0** | `v0.44.0` | `5e6237c` |
| pixelcoat | 0.12.0 | **0.15.0** | `v0.15.0` | `bd48df5` |
| deli_counter | 0.89.0 | **0.90.0** | `v0.90.0` | `7121245` |
| level_factory | 0.46.0 | **0.47.0** | `v0.47.0` | `3076689` |
| factory | 1.30.0 | **1.31.0** | `factory-v1.31.0` | `e11eaba` |

`verify-manifest`: 10 OK. Zoo suite 305 → **479 passed, 2 skipped**.
deli_counter 522 passed. The last three were sitting uncommitted from
earlier sessions and are now in.

### The substantive change

A Pixelcoat grammar can declare `tintable` — "my albedo is a surface, not a
paint job". Zoo reads it and multiplies the mesh's own colour into such a
pack, keying the material cache on `(kind, theme, colour)` instead of
`(kind, theme)`.

Why it was needed: `make_material` discarded `base_color` the moment a pack
resolved. All 42 species that can wear `metal` shared ONE grey material in a
skinned build; `simple_car`'s police black, racing red and 1970s brown
collapsed into it. A red vending machine rendered as a galvanized box.

Measured end to end, not assumed. `tools/tint_probe.py` built two materials
from one tintable pack, exported, and read the GLB back:

    M_Probe_red   baseColorFactor [0.620, 0.140, 0.140, 1.000]  texture yes
    M_Probe_blue  baseColorFactor [0.140, 0.260, 0.550, 1.000]  texture yes

Blender 5.1.1, hash `b70da489d7f4`. Those are the genome colours to three
decimals. **Re-run that probe on a Blender upgrade** — the fold is the
exporter's choice, not a guarantee of the format.

### The metal split

`metal` is theme-owned (a rusted facade belongs to the building).
`metal_painted` and `metal_bare` are object-owned. TWO kinds and not one
because `METALLIC` is a per-kind lookup: paint is a dielectric (0.0), bare
metal a conductor (0.90).

Scoped by measurement before anything was added. Of the 42 species that can
wear `metal`, only **12** declare a style colour with chroma >= 0.10. The
other 30 are already near-grey; ten of those are architecture (wall,
wallCorner, wallEnd, window, doorway, breach, prop, dress_cover, ceiling,
roof) and MUST stay theme-owned. That is the measured reason the kind could
not simply be made tintable.

Batch 1 moved four species: vending_machine, simple_car, helmet,
queue_stanchion. **Batch 2 is 8 species and not yet started** — see below.

---

## THE FOUR SILENT FALLBACKS

Every one of these continues, looks fine, and produces a green result. This
is the section to read first next session.

**1. `dna.resolve_plan` discards an unlisted material kind.**

    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]

No warning. A style saying `"material": "metal_painted"` is thrown away
unless the kind is ALSO in that species' `materials.options`. Every genome
edit is two places, and the failure mode is a render that looks untouched.
`tests/test_material_options_closed.py` now sweeps all 53 genomes asserting
the invariant that makes this rule a no-op.

**2. `themed_tscn.resolve_slot_ref` falls back to the greybox.**

By design, for progressive art. It means a chain run completing tells you
NOTHING about whether modules resolved. `Structural checks passed (blockers
open: 0)` was true today while the scene still pointed at prop stems that no
longer exist.

**3. `skins.load_pack` takes `sorted(*.pack.json)[0]`,**

and `build_material_pack` does `makedirs(exist_ok=True)` without clearing.
A theme library rebuilt in place keeps BOTH manifests and the
alphabetically-first one wins. `metal_brass_casino` beat
`metal_galvanized_stadium` for weeks that way. `tools/rebuild_theme_libraries.ps1`
deletes before it builds, for this reason.

**4. A stale `.pyc` can hide an applied patch.**

Rewriting `version.py` in the same wall-clock SECOND its `.pyc` was written
left the `.pyc` valid by Python's `(mtime, size)` check — both 366 bytes,
same second — so the interpreter served the OLD constant and the patch
looked like a no-op. Every patch script now purges `__pycache__` after
writing.

---

## `run` AND `export` ARE DIFFERENT COMMANDS

This cost three rounds of filesystem forensics today, so it is written down.

`level-factory run --art --unlit lot_demo_001` builds into
`.level_factory\jobs\<stage>\out`. It does **not** refresh
`.level_factory\exports\LF_lot_demo_001.art-unlit\`, which is a package
produced by the separate `export` command. Reading the export directory as
"the run's output" is wrong and looks convincing — the files are there, they
are just from the last `export`.

Related: there is **no `*_kit.json` anywhere on disk**, before or after a
successful `zoo_kit_build` on five buildings. `build_kit` computes an
`index_file` and `build_kit_run` prints it, so the level_factory art adapter
is either discarding it or writing it somewhere else. That index is exactly
the artifact that would make "did the props resolve?" a lookup instead of
archaeology. **Recommended small patch: have the art adapter persist it.**

---

## OPEN — the export is blocked

    export blocked by functional regression:
      - collision_fingerprint changed after art pass

`level_factory/packages/approvals/lock.py`:

    PROTECTED_KEYS = {
      "collision_fingerprint": ("stair_systems", "ladders", "platforms",
                                "fire_escapes", "openings",
                                "vertical_links", "surfaces", "ground"),
      "anchor_registry_hash":  ("markers", "anchors"),
    }

**Props are NOT protected**, so the prop rebuild is not the cause — that
hypothesis was checked against the source and killed. The live suspect:
`zoo_kit_build` also emits `breach_*` (→ `openings`) and `ceiling_*` (→
`surfaces`), both protected, and zoo 0.40.0 added `shade_by_angle` to
`bm_to_object`, which runs on EVERY mesh the library builds. It only sets
smooth flags, but smoothing changes split normals and split normals change
what the exporter writes.

The 08-18 export succeeded with the old Zoo, which brackets the change to
today's six releases.

**Next step:** read the lock JSON and find WHICH sub-key moved. The gate
reports the parent only. `stair_systems` moving means something very
different from `surfaces` moving. If it is smoothing, the fix is either
making the fingerprint insensitive to it or re-baselining the lock
deliberately with the reason recorded.

If this turns out to be cosmetic smoothing perturbing a collision
signature, that is a finding well beyond this export — a visual-only change
to the Zoo library would be moving collision geometry, which is exactly the
coupling the lock exists to catch. It caught it on the first build after the
change landed.

---

## OPEN — ranked

**Prop stems.** Fix verified: no stem covers two different dim triples in
any of 116 buildings. The old width-only name collided on **75 names across
26 buildings** — `cbp_town_finale_midbalanced` had FIVE distinct solids on
`w500`, from 0.70m to 2.50m deep. Modules rebuilt (7 distinct, 5 buildings),
propagated through `themed_site_assemble` and `presentation_compose`, but
**not exported** — blocked above. 173 old-form GLBs remain in old exports and
job dirs; unreachable, not wrong, safe to sweep once the export lands.
`jobs\lot_demo_001.zoo_kit_build\out` (no building suffix, dated 08-05) is an
orphan from before job dirs were split per building.

**Batch 2 of the metal split** — 8 species. `metal_painted` candidates:
chair, filing_cabinet, water_tank, flat_top_grill, shelving, atm,
vault_door. `metal_bare`: gold_bar (chroma 0.61, but bare metal, not paint).
Wants a per-species table before writing. **`shelving.json` is the one genome
that is NOT byte-exact `json.dumps(indent=1)` round-trippable** — it needs an
anchored edit, not a structural re-dump.

**`simple_car` has a ledge I introduced and never fixed.** `CABIN_W` should
equal `SHOULDER_TOP`; the shoulder's tapered top face reads as a shelf around
the greenhouse. It has also never been rendered with its nine styles, which is
the widest test of the tint path (police black vs racing red).

**`metal_painted_neutral` mottling** is an art call, not a defect. Three
knobs: `bands.macro` 0.14 → 0.06 and `albedo_pattern` 0.5 → 0.3 for less
fading; `roughness.base` 0.42 → 0.30 for gloss; `ROUGHNESS["metal_painted"]`
0.45 → 0.38 in materials.py for depth.

**`laser_tag` pins tag `v0.8.0` and that tag does not exist** — the repo has
only v0.7.0–v0.7.3. Recorded in the manifest description, not resolved:
creating it retroactively is a claim about when 0.8.0 shipped; correcting the
pin down contradicts lasertag's own VERSION file. `verify_manifest` compares
pin / installed VERSION / newest CHANGELOG heading and **never reads the tag
field**, so nothing could have caught it. A verify-manifest that resolved
each tag would close the whole class.

**deli_counter's nav-gate: 3/135 shells fail, 18 have no spawn marker** —
bank_job, warehouse, five lf_category5_baie_dore variants, three lf_lot_demo,
night_auto, night_pawn. Nothing has ever asked whether they connect. v0.90.0
was committed with the hook skipped ONCE, after the gate was measured
identical on a stashed clean HEAD (3/135 both ways); the evidence is in that
commit message.

**Plate/material stem collision, 8 buildings** — plates with identical dims
but different materials share a filename; `dna.resolve_module_plan` reads
`module["material"]` as an override so they build differently. Reported,
never decided.

**Unmapped kinds:** `laminate` (6 species, no profile at all), `paper` (5, no
profile), leather / dirt (profiles exist, unmapped), rubber, tar, gravel,
canvas, carbon, vegetation.

**Lot pool:** the run reported `4 archetype(s) excluded for a missing
manifest: bank, kitbash_demo, rarity_demo, survival_demo` and `11 entries not
offered to the lot`. A quarter of the pool, and `bank` stands out given there
is a whole `bank_tower_block` spec. Never investigated.

---

## Where the deliverables are

`patches/` (committed): `patch_pc_tintable.py`, `patch_zoo_tint.py`,
`patch_plastic_mapping.py`, `patch_metal_split.py`,
`patch_zoo_batch1_painted.py`, `patch_manifest_131.py` + `patch_m.json`,
`prop_stem_sweep.py`, and the three commit scripts.

Every patch carries pre/post sha256 per target, an all-or-nothing pre-flight
sweep, `--check` / `--selftest` / `--revert`, and a falsification that must
FAIL when the change is backed out. `pixelcoat/tools/rebuild_theme_libraries.ps1`
and `zoo/tools/tint_probe.py` are the two tools worth keeping to hand.
