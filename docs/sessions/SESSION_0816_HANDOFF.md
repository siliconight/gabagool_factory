# Handoff — 2026-08-16

*Read this first. It is written so a session that has never seen this project
can start work without asking anything.*

---

## 1. The next task, with the finding already made

**Six of `lot`'s eight test failures are stale callers, not a product bug.**

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory\lot
python -m pytest tests -q          # 328 passed, 8 failed
```

`site_spawns.py` (53,893 B, sha256 `619F4C3C...`) declares:

```python
def opening_engagement_is_fair(candidate, crew_path, occluders,
                               opening_range: float = OPENING_RANGE,
                               clearance: float = OPENING_CLEARANCE) -> bool:
```

and its docstring says why the second parameter is required:

> `crew_path` is required rather than defaulted to `[spawn]`. A default would
> leave both existing callers testing the old thing while this code sat
> unreached, which is precisely the failure this patch exists to correct one
> instance of.

The predicate was deliberately changed from judging the spawn TILE to judging
the stretch of route the crew covers in its first second at `CREW_SPEED` — a
corner that hides an enemy from the spawn but not four metres down the street
was being credited as cover for a fight that starts after the crew has walked
those four metres. Measured, `lot_demo_001` seed 5118: Enemy_0 at 26.5 m
admitted because the crew's OWN spawn building covered 48% of the line from
the tile; Laser Tag's raycast disagreed at 0.08 s and the run graded 45/100
with `route_completion_rate: 0.0`.

`tests/test_site_spawns.py:345` still passes a point:

```python
assert site_spawns.opening_engagement_is_fair(
    point[:2], spawn, occluders), (...)          # spawn = SEED_5320_ROUTE["spawn"][:2]
```

Bound to `crew_path` it iterates to floats and `site_spawns.py:470` raises
`TypeError: 'float' object is not iterable`.

**The fix is to update the six callers to pass a crew path.** The function's
refusal worked exactly as designed; the follow-through never happened.

The six:

```
test_an_enemy_down_an_open_street_inside_sight_range_is_not_fair
test_the_same_enemy_behind_a_building_is_fair
test_and_so_is_one_further_off_than_either_side_can_open_fire
test_the_sight_range_itself_is_not_a_standoff
test_no_enemy_can_shoot_the_crew_before_it_has_moved
test_the_written_positions_are_read_back_and_not_taken_on_trust
```

**Already on disk, no need to re-extract:**
`_scratch\site_spawns_api.txt` — 548 of 1134 lines of `site_spawns.py`,
covering `opening_engagement_is_fair`, `place_enemies`, every `crew_path` and
`reach` use, and `_v3`. Header carries size and sha256.

### The other two failures — NOT yet diagnosed

**`test_site_cover.py::test_the_cover_that_was_planned_is_in_the_scene_that_gets_shipped`**
— `AssertionError: Enemy_5 still sees the crew spawn down 51.9 m of open
ground in the scene that shipped`. HYPOTHESIS ONLY, do not treat as read: if
this test is also written against the spawn-tile contract, it may be
measuring the thing the predicate deliberately stopped measuring. Nobody has
opened it.

**`test_site_spawns.py:461::test_the_walk_scene_carries_the_placed_positions`**
— `AssertionError: (37.735, 19.242160304653307)` under `abs_tol=1e-3`.

> **DO NOT FILE THIS AS A TOLERANCE FAILURE.** 37.735 against 19.242 is 18.5 m
> apart; no `abs_tol` closes it. The assertion's comment is about surviving
> two roundings, which is exactly what would get this written off. The pairing
> is `zip((gx, gy, gz), (sx, sz + 1.0, -sy))` — a site→Godot remap — and the
> FIRST pair fails. An ordering difference or a remap applied twice produces a
> gap that size. The counts agree (`len(written) == len(planned) == 6`); the
> places do not. **Do not widen the bound. Do not skip the test.**

All three are written up as **roadmap item 51**.

---

## 2. State as of this handoff

Everything is committed and pushed. Nothing is half-applied.

| repo | version | tag | commit |
|---|---|---|---|
| level_factory | 0.40.0 | `v0.40.0` | `5bd29d1` |
| factory (coordination) | 1.25.0 | `factory-v1.25.0` | `07c668b` |
| lot | 0.41.0 | — | unchanged, clean tree |

Roadmap: **48, 49, 50 CLOSED** on measurements. **51 OPEN.**

### What changed about the pipeline today

1. **It grades the level it ships.** `_art_run` was read off the invocation's
   planned graph, so `batch create` drew from 123 shells and `run --art` from
   98 — same job id, same seed, two different buildings, with every grader and
   the functional lock measuring the first while the package shipped the
   second. Now keyed on the brief (`lot_library`). Item 48, LF 0.38.0.
2. **Its packages open.** `export_mission` step 2.5 (added 0.37.0) overwrote
   the root `site.tscn` with the assembly scene, which names
   `lot/<id>/site.tscn` — a directory the export never carried. Every
   single-shell themed export since 0.37.0 was unopenable, in BOTH modes.
   `_assembly_building_dir` now reads the assembly scene and puts the composed
   root where it says. Item 49, LF 0.39.0.
3. **One manifest, and it is true.** Packages shipped two: Dispatch's stale
   `resource_manifest.json` (17 entries, `mission.tscn` at 16,246 B beside a
   688 B file) and LF's correct `portable_resource_manifest.json` (58
   resources). The stale one had the better name. Dropped. Item 50, LF 0.40.0.

### Reproducing the test bed

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory
pwsh -File tools\run_3b_unlit.ps1           # ~10 min, Blender + headless Godot
```

Builds `workspaces\unlit-3b-ws` cold: mission `unlit_probe_001`, seed 5017,
ONE building. That workspace currently exists with every job cached, so
re-exporting is seconds:

```powershell
$ws = "workspaces\unlit-3b-ws"
python level_factory\apps\cli\main.py -C $ws export unlit_probe_001 --mode art-unlit --format folder
```

Expect `ok: true`, `issues: []`, `resource_count: 3`,
`unresolved_relative_count: 0`. `resource_count` is a count of scene/script
FILES present, not a reachability measure — 3 is `mission.tscn`, `site.tscn`,
`lot/shell/site.tscn`, and it is correct for one building.

---

## 3. Conventions this project runs on

**Every code change ships as a patch script** in `patches\`, with
`--check`, `--revert`, `--selftest`. Anchored text edits that **refuse on
drift** rather than fuzzy-matching. `.pre_<tag>` sidecars for revert. Print
byte counts and sha256. Check every file it touches exists BEFORE editing any
of them — a patch that half-applies then raises is worse than one that
refuses.

**`_eol()` is keyed off the FILE, never off an anchor.**
`PIPELINE_ROADMAP.md` is CRLF; everything under `level_factory\` is LF. And
`Path.read_text()` normalises newlines, so a check written with `read_text`
reports a CRLF file as LF.

> **SUPERSEDED 2026-08-16 -- the second sentence only.** The rule itself is
> right and is why none of this cost anything: every patch reads its target's
> endings at runtime, so the machinery adapted without a line of change. But
> naming a file's ending as a CONSTANT was wrong even when written.
> `core.autocrlf = input` was storing every blob as LF and never converting
> back on checkout, so `PIPELINE_ROADMAP.md` was 4,525 CRLF on that one disk
> and LF in the repository, `.gitignore` was 32 CRLF and 26 LF at the same
> time, and `CLAUDE.md` was CRLF without anyone noticing -- it lost 379 bytes,
> one per line, when the working copy was brought into line. A fresh clone
> would have produced LF files and failed every selftest asserting CRLF, on
> files that were correct.
>
> `.gitattributes` now sets `* text=auto eol=lf` (commit f2713e9) and the
> working copy has been renormalised, so **LF is canonical in both.** Note
> that `.pre_*` sidecars are gitignored and are byte copies of whatever their
> source was, so older ones are still CRLF and are supposed to be.
>
> Do not replace this with "the roadmap is LF". That would repeat the mistake
> with a different constant. Read the file.

**Selftests must be able to fail.** Recurring mistakes tonight, all caught:
- `A and B or C` — `and` binds tighter, so a loose `C` swallows the test.
  Write strict conjunctions.
- Searching for a string that spans a line break in the source file. Match
  against whitespace-normalised text.
- Substring searches that match the prose explaining the thing rather than
  the thing (`grep` for `mkdir(parents=True)` hitting its own docstring).
- **Prove a new check can fail** by removing the evidence and re-running it.

**Selftests run `tests/unit` whole and read pytest's RETURN CODE**, not its
text. Four releases in the prior arc reported "still green" against 28 tests
while 659 went unrun. `rc=5` (collected nothing) is a FAILURE — it is what a
broken import looks like.

**`level_factory/pyproject.toml` sets `addopts = "-q"`.** Passing `-q` again
makes it `-qq` and pytest drops the count line entirely. Do not pass `-q` for
LF. `lot` has no such setting, so `-q` is fine there.

**After any roadmap edit:**

```powershell
python tools\roadmap_status.py --write
python tools\roadmap_status.py --check
```

The status table is DERIVED. Items carry
`*STATUS: <VERB> <date> -- <evidence>*` one line above them. Vocabulary:
`OPEN` / `CLOSED` / `RETRACTED` / `NARROWED` / `SUPERSEDED` / `ANALYSIS`.

**`level_factory\` is its own git repo** and is gitignored by the factory
repo. Commit LF changes from inside it; commit `PIPELINE_ROADMAP.md`,
`patches\`, `tools\` and `factory.manifest.json` from the factory root.

---

## 4. Two hard-won working rules

**Do not reason ahead of a verified read.** Item 49 got three mechanisms
before the right one. The first two were written from real evidence and
published; both are still in the roadmap, named as wrong, with what refuted
each. The rule the item adopted for itself: *a mechanism claim cites a
verified read or it does not go in.*

**The device bridge serves stale files, sometimes at the correct byte count.**
It happened four times in one session — including a five-day-old
`commands/__init__.py` at 106,667 B when the real file was 126,111, and a
`factory.manifest.json` reporting factory 1.15.0 at the same 8,684 bytes as
the real 1.24.0 one. **The workaround that works:** have the user write a
FRESH scratch file — a file with no previous version cannot be served stale —
stamped with the source's size and sha256:

```powershell
$f = "<path>"
$lines = [System.IO.File]::ReadAllLines((Resolve-Path $f))
$out = Join-Path (Get-Location) "_scratch\<name>.txt"
$hdr = @("FILE   : $f",
         "BYTES  : $((Get-Item $f).Length)",
         "SHA256 : $((Get-FileHash $f -Algorithm SHA256).Hash)",
         "LINES  : $($lines.Count)", "")
[System.IO.File]::WriteAllLines($out, ($hdr + $lines))
```

Then check the reported BYTES against what you expect before trusting a word
of it. `_scratch\` is gitignored.

**Working style the user asked for:** *"either give me the PS to run in shell
or don't give me a verb."* Any action addressed to them arrives as runnable
PowerShell. `pwsh`, not `powershell` — 5.1 writes a BOM and tools refuse it.
No bash heredocs; PowerShell has no `<<'EOF'`.

---

## 5. Everything else still open, ranked

1. **Item 51** — the three `lot` defects above.
2. **`lot_demo_001` re-exported under 0.39.0 / 0.40.0.** Five buildings is
   exactly the shape item 49's fix leaves untouched, and it is the mission
   every earlier measurement was taken on. Nothing has re-measured it.
3. **Lux is decoupled in the DAG but coupled by filename.**
   `lux.applied.tscn`, `lux.quality.json` and `lux.validation.json` are string
   literals across 8 modules / 27 sites (planner `expected_outputs`,
   `export.py` `_PRESENTATION_FILES`, `localize.py`, `closure.py`,
   `facade.py`, `walk_preview.py`, the Lux adapter, the CLI). Change a Lux
   output name and the layer boundary protects none of them — and
   `walk_preview`'s `has_lux` would read False and silently render unlit.
   `_preset_for` also hardcodes Lux preset DISPLAY names ("Blue Hour", …)
   where a wrong name is a silent no-op. One constant Lux owns and the eight
   readers import would finish the separation.
4. **Three version sources disagree.** `doctor` reports drift against
   `packages/tools/contracts.py`'s `GROUNDED` (e.g. lot "certified 0.18.3")
   while `factory.manifest.json` pins lot 0.41.0. Plus `tools.lock.json`.
   Nothing reconciles them.
5. **Roadmap 44 / 45 / 46** — Zoo collision substitutes, non-collision surface
   dressing, interactive state machines. Specified, nothing built.
6. **Dispatch real-tools test is skipped** for missing
   `build/lux/lux.profile.json` fixture data. 9 real_tools, 1 skipped.
7. **The `--unlit` interface shape.** The planner has a real fourth layer
   (`LAYER_LIGHT`, with `_LAYER_REQUIRES = {LAYER_LIGHT: LAYER_ART}`), but the
   CLI expresses it by subtraction: `--art` means art AND light, `--unlit`
   removes light. There is no positive `--light`. Worth deciding before
   anything builds on it.

---

## 6. Artifacts this session produced

- `docs/findings/ITEM48_THE_DRAW_MOVED.md` — full evidence for item 48
  (run log, both site specs, five fingerprints verbatim, sha256 per file),
  written because `_runs/` is gitignored and `fingerprint.last.json` had
  already overwritten the first assemble.
- `tools/probe_lot_own_output.py` — read-only; calls the pipeline's own
  `index` / `source_exclusion` / `require_themed_shells` / `pick_lot` and
  reports the draw, the exclusion list and file dates. It refuted one of my
  own hypotheses and independently reproduced item 48's divergence from the
  library alone.
- `_scratch\` reads: `site_spawns_api.txt`, `export_copies.txt`,
  `closure_api.txt`, `export_mission.txt`, `site_spec_branch.txt` — each
  stamped with size and sha256.

**Known-good hashes** (for spotting a stale bridge read):

```
level_factory/packages/exporting/export.py   37,159 B  sha256 979bf39f...  (0.40.0)
level_factory/packages/exporting/closure.py  12,146 B  sha256 1467E73D...
lot/site_spawns.py                           53,893 B  sha256 619F4C3C...
```
