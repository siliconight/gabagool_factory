# The ladder into the solid roof — closed 2026-08-09

**Fixed, walked, and confirmed.** `Ladder_ladder_0`: `climb: true`,
`top_exit: true`, `ok: true`, no `stall` key.

The cause was not geometry. It was **a hand-copied constant in a second repo.**
It took **two** fixes to reach the scene, and a third false finish in between.

Verified end state, all three at once — anything less proves nothing:

```
site.tscn   [ext_resource ... path="art/zoo/roof_rockay_01_w4000_d3000_v72fc6e.glb"]
art/zoo/    roof_rockay_01_w4000_d3000_v72fc6e.glb   229,240 bytes
walk bot    Ladder_ladder_0: climbed to 4.2 m and stood up
```

**`walkbot.json` alone is not evidence the roof is fixed.** A ladder into open
sky reports `climb: true, top_exit: true` exactly like a ladder through a
correct hole, and the top station reads `void 52.66%` in both cases. An earlier
walk this session was taken as proof and was almost certainly run against a
building with no roof at all. Always check the scene reference and the `.glb`
beside the bot report.

---

## The chain, end to end

```
deli_counter/roofs.py          roof slot gains `voids`          (patched 08-09)
deli_counter/deli_counter.py   slot derived AFTER the hole cut  (patched 08-09)
zoo/zoo_keeper/core/arch.py    roof: _SOLID -> PLATE_SPECIES    (patched 08-09)
zoo/zoo_keeper/core/kit.py     roof joins PLATE_ROLES           (patched 08-09)
deli_counter/themed_tscn.py    roof joins PLATE_ROLES           <-- MISSED
```

`themed_tscn.py` carries its own copy of Zoo's tuple, labelled in a comment as
a mirror:

```python
#: Mirror of ``zoo_keeper.core.kit.PLATE_ROLES``.
PLATE_ROLES = ("floor", "ceiling")
```

and that tuple decides two things in `resolve_themed_stem`:

```python
depth_cm = (int(round(dims[1] * 100)) if exact and typ in PLATE_ROLES else None)
vtag     = void_tag(fit.get("voids"))  if typ in PLATE_ROLES else None
```

So Zoo built `roof_rockay_01_w4000_d3000_v72fc6e.glb` and Deli Counter wrote
`roof_rockay_01_w4000.glb` into `site.tscn`. **The scene referenced a module no
job produced.** An orphan of that name from an older run was still sitting in
`art/zoo/` — nothing cleans that directory — so the load succeeded, and the
orphan is a solid plate. That is the ladder.

One word. Two repos. Five gates.

---

## Four hypotheses, and what killed each

Recorded because the refutations were cheap and the guesses were not.

**1. "The Zoo patch never reached the build."** The composed package held an
un-suffixed roof, so the patched code must not have run inside Blender — stale
`__pycache__`, or Level Factory staged a pre-rebuild `slots.json`.

> **Refuted** by the job's own output directory:
> `zoo_kit_build.bank_branch_a04\out\roof_rockay_01_w4000_d3000_v72fc6e.glb`,
> 229,240 bytes, and `bank_branch_a04_kit.built.json` recording
> `"stem": "roof_rockay_01_w4000_d3000_v72fc6e"`. Zoo built it correctly and
> said so. The problem was downstream.

**2. "The old mtime proves the module wasn't rebuilt."**

> **Refuted** by hardlinking. The content-addressed cache hard-links
> byte-identical outputs, so a restored file carries the *cache entry's* mtime.
> Every timestamp in `.level_factory/` is meaningless. This was the second time
> in one session I reasoned from an mtime; both times it was wrong. **In this
> tree, filenames are evidence and timestamps are not.**

**3. "The whole composed package predates depth keying."**

> **Refuted** by one directory listing. `ceiling_rockay_01_w4000_d1700_v38fc4b`,
> `floor_rockay_01_w4000_d1800_v6cd118` — every plate species carried full keys
> matching the job's `out\` byte-for-byte. The package was current. Only `roof`
> was wrong, which is exactly the species the patch had moved.

**4. "The orphan is `rail_station_a02`'s roof — a bare-stem collision."**
Its 189,620 bytes matched rail_station's `_d2600` roof exactly.

> **Refuted** by SHA-256: `E9E8C2B2…` vs `9AB4DF3E…`. Different files. The byte
> match was coincidence — half the `rockay` modules land within a few hundred
> bytes of each other (`wall_…_w200` 189,680, `wallEnd_…_01` 189,576,
> `prop_…_w90` 189,752), because a shared texture payload dominates the file.
> **A size match inside a cluster of near-identical sizes is not identity.**

**5. "The roof is missing from the composed package — Lot, or Lux, drops it."**
After the fingerprint fix, the preview held no roof `.glb` and no roof
`ext_resource`. Four directories were read and three stages suspected.

> **Refuted** by rebuilding the preview. `walk_preview.build_preview` does
> `shutil.rmtree(dest)` and copies the package wholesale — **the preview is
> rebuilt by `walk`, and by nothing else.** Every `run --art` in between left it
> untouched, so what was being inspected was the output of the *previous* walk,
> taken before compose was forced to re-run. The pipeline was correct the whole
> time. Three copies of the same scene, measured in one command, would have
> shown it immediately:
>
> ```
> presentation_compose\out\…       site.tscn 63,610   roof present
> themed_site_assemble\out\…       site.tscn 63,406   roof present   (-204: res:// stripped)
> preview\lot_demo_001_walk\…      site.tscn 63,081   roof ABSENT    (stale: last walk)
> ```
>
> **A directory is only as fresh as the command that writes it.** `run --art`
> and `walk` write different trees, and reading one to judge the other is the
> same error as reading an mtime on a hardlink.

**What actually found it** was one command, run after five wrong guesses:

```powershell
Get-ChildItem <factory> -Recurse -Include *.py |
    Select-String "_SOLID|PLATE_SPECIES|PLATE_ROLES|PLATE_COLLIDES"
```

The patch had searched Zoo, because Zoo was the repo already open. The grep was
always available and would have prevented the whole detour.

---

## What now enforces it

`test_mirror_agreement.py` — spans both repos, no skip path.

* Mirrors are **discovered from `themed_tscn.py`'s own `#: Mirror of …`
  comments**, so a mirror added later is enrolled without anyone remembering.
* Signatures are compared (names *and* order) before values, or the value
  comparison would be comparing two different functions and calling it
  agreement.
* Values compared over a shared corpus, including the asymmetry the docstrings
  promise: `void_tag` must ignore rect order (a plate's voids are a set and
  sort), `opening_tag` must not (only the first opening is cut). Both sides,
  both directions.
* Final case rebuilds `bank_branch_a04`'s roof slot and asserts the stem DC
  writes **is the name Zoo builds**, computed from Zoo's own `module_stem`
  rather than from a `_d`/`_v` spelling the test would then be the only record
  of.

Pre-patch it failed on exactly `PLATE_ROLES equal` and the stem. It also caught
its own coverage gap — my corpus used `vtag`/`otag` where the parameters are
`voids_tag`/`openings_tag`, so `module_stem` was silently never compared. It
reported that as a failure rather than a pass. Post-patch: 16 `module_stem`
calls agree, `void_tag` and `opening_tag` agree exactly.

`themed_tscn.py` 20,557 → 20,565 bytes (+8).
sha256 `e7bd2ede23222df79f6a4d0fa268ac4e2b27d312fb573233810a79da7b9eea98`.

---

## Three defects this exposed, none of them the roof

**1. The scene-writing stage did not fingerprint the code that writes it.**
**FIXED — `patch_lf_presentation_probe.py`.** Applying the mirror fix changed
nothing: `presentation_compose cache`. A manual `cache forget` was required to
get a correct fix to land. `PresentationAdapter.probe` reported
`tool_version=self.adapter_version, repository_commit=None` while its own
docstring says it drives *Deli Counter's* composer — so DC's revision, and the
`+dirty` marker `_read_git_commit` exists to provide, never entered the
fingerprint. **A stage that runs another tool's code must fingerprint that
tool's revision.**

The probe now reports DC's version and revision through `BaseAdapter`'s own
helpers, and `adapter_version` 0.2.0 → 0.3.0 retires entries computed under the
old rules. Verified sensitive *and* stable, which is the pair that matters:
run 1 `presentation_compose succeeded`, run 2 with nothing edited
`presentation_compose cache`. A fingerprint that never hits is as broken as one
that always does.

Note `themed_site_assemble` re-ran in run 1 purely because compose's output
changed — Lot follows its input hashes correctly and needed no fix. It was
suspected twice and was innocent both times.

**2. Nothing checks that a scene's `ext_resource` files exist.** `site.tscn`
named a `.glb` no job produced. It survived compose, assemble, the sweep, a nav
bake, and `blockers open: 0, total findings: 54`, and was caught by a bot
walking into it. `_themed_available` already does the check and its first
branch is `if not library_dir: return True  # trust the plan`. Ten lines at the
writer turns this class of bug into a failed build.

**3. Nothing cleans `art/zoo/`.** The orphan is why the wrong reference *loaded*
instead of erroring. Absent the leftover, defect 2 would have surfaced as a
missing-resource error on the first run.

---

## Recorded findings

* **Void % cannot detect a cap, and cannot detect an absence either** (item 5).
  The known-bad station read 0.0% void; a correctly-open roof reads 52.66%; a
  building with **no roof at all** also reads 52.66%. One number cannot carry
  three states. This misled the diagnosis twice in one session — once at the
  start, once at the false finish.
* **`walk` is the only thing that writes the preview.** `run --art` does not
  touch it. Judging a pipeline change by reading
  `preview/<mission>_walk/**` without walking first reads the previous walk's
  output. Cost roughly an hour and five refuted hypotheses.
* **`--sweep`'s summary miscounts.**
  `bad = sum(1 for _, r in rows if r["error"] or r["mismatch"] or r["missing"])`
  reports unreadable packages as "disagree with their slots", contradicting the
  function's own docstring.
* **Two more copies of these constants**, in pre-patch state, at
  `_bridge_fresh/arch_v2.py:27,34` and `_bridge/sw_0730a.py`. Establish whether
  anything imports them before committing.

## Still open

* `patch_lf_source_library.py` and `patch_map_derived.py` — both unapplied.
  (`building_library.py` is still 18,467 bytes, so item 7 has not landed.)
* Nav-gate re-bake for the rebuilt `bank_branch_a04`; themed selection reads
  that verdict rather than recomputing it.
* `cache forget` has now run on hardware — successfully, as the only way to
  land this fix before defect 1 was fixed. Its first real use was covering for
  a bug, which is worth remembering when judging whether it is well tested.
* **By eye, still owed:** stand on the roof and look at the deck around the
  hole. Every instrument in this document reports the same value for a correct
  roof and for no roof; a human looking down does not.
