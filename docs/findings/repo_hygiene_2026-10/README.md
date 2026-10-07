# Repo hygiene, 2026-10: what is where, what is loose, and the plan

Surveyed 2026-10-06 (`hygiene_survey.py`, plus the repo's own
`tools/factory_root_audit.py`, `factory_tidy.py` and `factory_folders.py`,
all in report mode). The question asked was "can everything be found", so
the survey measured three things: what git thinks of each file, where the
bulk is, and what has no index.

## The tool repos are nearly clean

| repo | root files | loose | what is off |
|---|---|---|---|
| deli_counter | 235 | 2 | 120 `test_*.py` at the root by design (COMMANDS.md). 21 `migrate_*.py`, 7 `phase*_status.py`, 5 `patch_dc_*.py` and about 10 one-shots stand beside the builder; the README's Layout section lists 22 files. Two untracked captures from August. |
| lot | 44 | 0 | `test_ladders_reach_the_site.py` at the root beside `tests/`; a tracked directory literally named `--out-dir/` (one file, a CLI accident); 6 one-shots (`p3_collect`, `phase3m/4m_status`, `remediate_s3`, `patch_lot_portable`). |
| zoo | 8 | 306 | `_preview/` (19 MB) and `_census/` (15 MB) are untracked and NOT ignored: the rule is `_preview_*/`, which needs the underscore. |
| lux | 5 | 12 | 12 `.gd.uid` sidecars untracked, 68 of 80 tracked. Godot 4.4+ wants them committed. |
| level_factory, patina, pixelcoat, dispatch, lasertag, pipeline | 5 to 9 | 0 | clean |

**Which Deli Counter root files anything still references** (grep over the
repo, its docs and COMMANDS.md): every `migrate_*` but four is imported by a
test, a preset, `level_design.py` or another migration, so they are live
code, not history. Unreferenced by anything: `p2_collect`, `remediate_l5`,
`probe_fights`, `sweep_stair_obstruction`, `walk_harness`, `review_render`,
`review_sheet`, all seven `phase*_status`, four of the five `patch_dc_*`, and
`generated_sweep.json`, `rockay_sweep.json`, `stair_sweep.json`.

## The factory root is where the mess is

`factory_root_audit.py`: 10 tool repos, 19 tracked entries, 13 ignored, and
**6 LOOSE** (neither tracked nor ignored; `git add -A` would commit them):
`.claude/`, `.pytest_cache/`, `Claude outputs/`, `scratchpad/`,
`film_perf_gpu.json`, `film_render_gpu.json`.

- **`scratchpad/`** is 766 MB of untracked session output in 42 entries
  (`ws_tex2` 317 MB, `dc_density` 131 MB, `dc_flatart` 121 MB, `occ3` 48 MB,
  suite logs). It is what `_scratch/` (ignored) exists for.
- **Tracked at the root and belonging elsewhere:** `SESSION_0815.md` and
  `SESSION_0821.md` (`docs/sessions/` holds the other 14; `factory_tidy.py`
  already classifies these two), `census7.json` (a light census from
  2026-08-23). The loose `film_*_gpu.json` are a 2026-09-02 film probe's
  output. `_runs/measurements/` is the tracked home for such things.
- **Ignored but on disk:** nine debugging captures from 2026-08-15
  (`compose_diag.txt` ... `unlit_ab2.txt`), listed by name in `.gitignore`.
- `factory_tidy.py` refuses to move `PIPELINE_MAP.md` and
  `PIPELINE_ROADMAP.md` because scripts write them, and five tool repos link
  them by `../` path 22 times. They stay.

### The bulk: 45 GB, almost all regenerable

| where | size | what |
|---|---|---|
| `workspaces/` | 22.7 GB, 54 dirs | 48 are October cold-run workspaces at about 700 MB each (9164 to 9188). Three are tracked (`rockay-ws`, `lot-demo-ws`, `unlit-3b-ws`): 255 files, of which 229 are Godot import caches (`.godot/imported/*.ctex`, `*.md5`) under rockay-ws that should never have been tracked. |
| `_runs/perf_inner/` | 9.6 GB, 75 dirs | perf price copies (about 250 MB each). The rule since cold run 9163 filled the disk: delete the copy once its JSON exists. 72 are from October. |
| `_runs/walk_export_*/` | 4.4 GB, 28 dirs | walk copies of exported levels, 33 to 312 MB each. Regenerable from the export. |
| `_runs/` root | about 700 loose entries | probe outputs (`ab_*`, `accent*`, `3b`, ...). `_runs/cold/` (217 journals, 147 MB) and `_runs/measurements/` (tracked) are the two parts worth keeping. |
| `docs/cold_runs/` | 682 MB, 192 runs | committed; `cold_7003` alone holds 164 MB of `shots_*` screenshots. History cannot shrink without a rewrite; the fix is to stop committing frames. |
| `docs/findings/` | 309 MB, 68 entries | see below |

The disk is at 96%, 20 GB free. One cold run needs about 1.5 GB.

### What has no index

- **`docs/findings/`**: 47 directories and 21 top-level files, mixed
  `CAPS.md` and lowercase names, 6 of the 47 directories have a README.
  98 links point into it (16 from the roadmap, 48 from docs, 34 from tool
  repos' changelogs), so **renaming is off the table**; an index is the fix.
- **`patches/`**: 978 files in 87 topic subdirectories, no README. Named
  `patch_<repo>_<topic>.py` (roadmap 124, lf 116, dc 76, zoo 58, lot 34,
  manifest 18). `migrations/` next door has `MIGRATIONS.md` with a table of
  what each script did; `patches/` has nothing.
- **`tools/`**: 111 entries, 20 censuses and 11 probes beside the standing
  tools. 93 are referenced by some doc or script; 16 by nothing
  (`anchor_planes_diff`, `anchor_storeys`, `check_coplanar`, `glb_materials`,
  `landuse_census`, `library_clean`, `make_factory_package.ps1`,
  `marker_meta_probe`, `navmesh_demo`, `probe_opening`, `room_intrusion`,
  `shot_contrast`, `site_fights`, `species_census`, `sweep_fights`,
  `test_dressing_in_nav_refuses`).
- **`docs/`**: 27 top-level documents including five `PHASE*_REPORT.md` from
  2026-08-01 and `NEXT.md` from 2026-08-12, beside the live ones.
  `docs/references/` is empty; `docs/walks/` holds one file.
- **`PIPELINE_MAP.md`**, the architecture map, has a generated DAG section
  whose generator fails its own selftest: three stages it does not know
  (`lot_site_surfaces`, `patina_surface_dressing`, `zoo_clutter_build`) and
  a changed `lux_apply` dependency. The map cannot be regenerated until
  that is fixed, so the "what runs after what" table is stale by design.

## The plan

The doctrine is the repo's own (`docs/CLEANUP.md`, `scripts/tidy_*.ps1`,
`migrations/MIGRATIONS.md`): allow-list, never guess; dry-run by default;
archive one-shots, never delete them, because a patch script is the only
record of how the source came to be; a generated index beats a typed one
because `--check` can see it drift.

**Phase 1, reversible file moves and ignore rules.** `git mv` the two
SESSION files to `docs/sessions/` and the three measurement files to
`_runs/measurements/`; archive the eleven stray captures and `scratchpad/`
under `_scratch/` (ignored, nothing deleted); ignore `.claude/` and
`.pytest_cache/` at the root and `_preview/` and `_census/` in Zoo; track
Lux's 12 uid sidecars; move Lot's root test under `tests/` and drop the
`--out-dir/` accident; untrack rockay-ws's 229 import caches (index only,
the files stay).

**Phase 2, findability.** A generator, `tools/factory_index.py`, writes and
checks a README in `docs/findings/`, `patches/` and `tools/`, one line per
entry from its first heading or docstring; a "where things live" map at the
root README; `docs/history/` for the phase reports and `NEXT.md`;
`factory_map.py`'s selftest brought up to the planner so the DAG table is a
measurement again; Deli Counter's README Layout regenerated from the tree.

**Phase 3, the walker's calls.** The 36 GB of regenerable output; the
`Claude outputs/` folder; moving Deli Counter's migrations and one-shots
under a folder, which is a code change (tests and `level_design.py` import
them) and ships as a release with the suite as proof.

**Phase 4, making it stick.** `factory_root_audit.py` LOOSE = 0 and the
index `--check`s join COMMANDS.md and SHIPPING_A_CHANGE's list; a retention
script for `_runs/` and `workspaces/`, dry-run by default, so the disk stops
filling between passes.

## What the pass did, 2026-10-06

**Walker's calls:** delete the perf copies that have their JSON (done,
70 copies, 9.2 GB; the five without a JSON stay); file `Claude outputs/`
under `docs/findings/claude_outputs_2026-09/` (done); move Deli Counter's
one-shots only (done, 0.193.0). The older cold-run workspaces were not
ticked at first; on the walker's later word `factory_retire.py --apply`
retired them: 13 workspaces, cold-9164 to cold-9176, 8.0 GB. The rule kept
cold-9180 and cold-9185 because a finding names them, and the newest
twelve (9177 to 9188). The disk went from 20 GB free to 38 GB.

**Pushed, 2026-10-06:** all ten tool repos are level with `origin/main`,
six of them pushed in this pass (deli_counter, lot, zoo, level_factory,
pixelcoat, lux). The factory root was pushed by the walker.

**Phase 1, landed.** `SESSION_0815/0821.md` to `docs/sessions/`;
`census7.json` and the two film JSONs to `_runs/measurements/`; the nine
2026-08-15 captures, Deli Counter's two, the 766 MB root `scratchpad/` and
eleven staged-but-never-run cold-run folders (`cold_9079`-`9089`, each
holding only a copied batch and briefs) archived under
`_scratch/archive/2026-10-06_hygiene/`, nothing deleted. `.claude/`,
`.pytest_cache/`, `.godot/` and `workspaces/` ignored (tracked files in the
three legacy workspaces stay tracked, as `_runs/measurements/` does);
rockay-ws's 228 Godot import caches untracked by pathspec file. Zoo ignores
`_preview/` and `_census/`; Lux tracks its 12 uid sidecars; Lot 0.97.4 moves
its root test and drops `--out-dir/`; Deli Counter 0.193.0 moves 23
one-shots under `migrations/` (nothing imported them: measured).

**The orphans decided.** Ten patches from earlier sessions and two
modified patch copies committed (both copies are the versions their repos
carry: checked by diff). `shape_sweep_9500` committed, matching the other
experiment folders. The three greybox frames got a README; cold_9113's
comparison sheet got the sentence in its NOTES that justifies keeping it.
`PHASE0-4_REPORT.md`, `PHASE1_MATRIX.md` and `NEXT.md` (nothing links them)
to `docs/history/`; the empty `docs/references/` removed.

**Phase 2 and 4, landed.** `docs/FILING.md`; a CLAUDE.md hard rule; a
`## Hygiene` section in COMMANDS.md and a line in SHIPPING_A_CHANGE's step
8; `tools/factory_index.py` writing nine generated READMEs;
`tools/factory_hygiene.py --check` (LOOSE, UNTRACKED, RECORDS, INDEX fail;
UNDESCRIBED, RETIRABLE, FINDINGS reported); `tools/factory_retire.py`;
`cold_run.py --end` printing the hygiene line.

**Refuted first, kept.** The retire rule's first version retired a walk
export "older than its mission's newest". There is one directory per name,
overwritten by each export, so it could never fire; its own selftest said
so. The rule is age (30 days untouched).

**After the pass:** LOOSE 0, UNTRACKED 0 in every tool repo, RECORDS 0,
INDEX 0. Reported, not failing: 20 undescribed entries (twelve old helper
scripts in `patches/`, two in `scripts/`, six Deli Counter phase reports),
and 40 finding folders without a README. Those are the to-do the indexes
now show.

## What is not established

- What `lot/cater.py` and `lot/mp_smoke.py` are for today; the map names
  `mp_smoke.py` as a site gate. Neither is moved on this survey's say-so.
- Whether any of the 16 unreferenced tools is run by hand. Unreferenced is
  not unused.
- ~~Which cold-run workspaces a finding still reads.~~ Run: the grep
  found cold-7001, 7301, 8001, 9001, 9067, 9080, 9180 and 9185 named under
  `docs/`. `factory_retire.py` does that grep before retiring anything, and
  of those names only 9180 and 9185 were still on disk.
