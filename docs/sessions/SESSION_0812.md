# Session 0812 — the package was 98% empty and every instrument said fine

Continues `SESSION_0811.md`. Eleven patches, one defect that no single tool
caused, the closure gate promoted from a warning to a wall, and a verification
section added to `CLAUDE.md` after ten wrong calls in two days.

**The short version:** `res://` is absolute. Deli Counter stages each themed
building as its own `res://` root and is right to; Lot references them by
package path and is right to; the export copies them in and is right to.
**Correctness did not survive composition.** Five building scenes arrived in the
package with 137 references still pointing at a root that was no longer theirs,
and the closure scanner certified the result `ok: true, 0 missing` because it
resolved `res://` by suffix.

---

## The headline: a reference that resolves is not a reference that is right

Of the 137, **132 dangled** — Godot drops those silently, which is the floating
plates and the empty sky. The other five are worse.

```
                                     bytes    what it actually is
res://site_base.glb  at the root    255,344  the SITE's base mesh
lot/<archetype>/site_base.glb       108,368  the BUILDING's base mesh
```

Every one of the five building scenes names `res://site_base.glb`. At the export
root that **resolves** — to the wrong file. Not missing. Not misrooted. Not
absolute, not external, not an addon. **No closure category in the toolchain has
anything to say about it**, and five buildings stood the site's base geometry
instead of their own without one warning anywhere.

The arithmetic is the tell that both instruments were right:

```
scan_closure, after the suffix match was removed      132 misrooted
--probe, references rooted at the wrong package       137
difference                                              5   the shadowed ones
```

The scanner counted 132 because the 5 shadowed refs **resolved**, so by its
definition they were fine.

---

## Eleven patches

| patch | file(s) | bytes | sidecar |
|---|---|---|---|
| `patch_lf_walk_the_export.py` | `preview/walk_preview.py`, `cli/commands/__init__.py` | 13,810 → 15,509; 104,856 → 106,667 | `.pre_walkexport` |
| `patch_lf_export_closure.py` | `exporting/export.py`, `exporting/localize.py` | 16,397 → 19,558; 15,261 → 16,852 | `.pre_exportclosure` |
| `patch_lf_closure_misrooted.py` | `exporting/closure.py` | 6,556 → 8,855 | `.pre_misrooted` |
| `patch_claude_md_verification.py` | `CLAUDE.md` | 17,020 → 22,441 | `.pre_verification` |
| `patch_lf_reroot_packages.py` | `exporting/localize.py` | 16,852 → 20,452 | `.pre_reroot` |
| `patch_lf_walk_doc_drift.py` | `cli/main.py`, `preview/walk_preview.py`, `cli/commands/__init__.py` | 11,508 → 11,580; 15,509 → 15,937; 106,667 → 106,835 | `.pre_walkdoc` |
| `patch_lf_closure_relative.py` | `exporting/closure.py` | 8,855 → 11,760 | `.pre_relative` |
| `patch_lf_closure_enforce.py` | `exporting/export.py` | 19,558 → 21,411 | `.pre_enforce` |
| `patch_lf_strip_walk_chrome.py` | `exporting/localize.py` | 20,452 → 22,643 | `.pre_walkchrome` |
| `patch_lf_closure_issue_paths.py` | `exporting/closure.py` | 11,760 → 12,146 | `.pre_issuepaths` |

Plus four instruments, every one of which measures a real export without needing
anything applied: `probe_lux_free.py`, and the `--probe` modes on
`patch_lf_reroot_packages.py`, `patch_lf_closure_relative.py` and
`patch_lf_strip_walk_chrome.py`.

### Walk what ships

The preview walked the job outputs. `lux.applied.tscn` there references
`res://addons/lux/` six times and renders nothing without the Lux checkout on
disk — which `PIPELINE_MAP` calls an instrument that escaped. `cmd_walk` now
runs `export_mission` and wraps the `mission.tscn` that comes out of it, so what
gets walked is what gets shipped.

The first attempt was to copy the addons into the preview project. **The README
killed it**: the outputs are not allowed dependencies or add-ons. Wrapping the
export was the correction and it is what surfaced everything below — walking the
deliverable is what made the deliverable's emptiness visible.

### The export closure

Twenty-one unresolved references on first measurement. `_QA_HARNESS_FILES`
strips `site_navqa.tscn`, `lot_navqa_setup.gd` and `mp_smoke*` — the nav-QA
harness had been shipping, referencing
`res://addons/heist_nav_qa/nav_qa_director.gd`, an addon a portable package
cannot contain by contract. `ENGINE_GATES` names these files as disposable and
nothing had ever removed them.

`_root_site_wanted` lets the presentation scene decide whether the composer's
root `site.tscn` ships, because a single-shell compose inlines its geometry and
names `res://site.tscn` while a themed multi-building site instances five
packages and names `res://lot/<archetype>/site.tscn` instead. 21 → 0.

### The scanner that resolved by suffix

```python
found_at = next((pr for pr in sorted(present)
                 if pr.endswith("/" + rel) or pr == rel), None)
```

The old line was `any(pr.endswith(rel) for pr in present)`. **Godot has never
resolved a `res://` path by suffix.** That one line certified the export at
`ok: true, 0 missing` while five building scenes dangled 33 references each. The
suffix search is kept and renamed to what it actually finds: a reference that
fails where it points while the file exists elsewhere is a scene that moved
without being rewritten — a specific defect with a specific fix, and saying so
beats a bare "unresolved". 0 missing → **132 misrooted, `ok: False`**.

### The reroot

A file not at the export root may have been written against a `res://` root that
is now one of its own ancestors. **Ask the disk which.** Walk from the file's
directory upward, take the deepest ancestor under which strictly more of its
references resolve than resolve at the export root, rewrite only the references
that actually resolve there. No ancestor wins → no edit.

It never assumes `lot/<id>` is a package boundary; it concludes it. On the real
export every building was unanimous, which is the strongest evidence the
heuristic could have produced:

```
                           refs resolving at   at the
                             its own root     export root
lot/bank_branch_a04             34 / 34            1
lot/construction_site_a03       32 / 32            1
lot/funeral_home_a03            24 / 24            1
lot/rail_station_a02            21 / 21            1
lot/supermarket_a01             26 / 26            1
                               -------
                                 137 rerooted, 5 of them SHADOWED
```

Ordered **before** the bare-ref repair deliberately: that pass rewrites a
root-level `res://<name>` to `res://assets/<name>` on a basename match, which for
`res://site_base.glb` would have pointed five buildings at the site's bundled
base — the same wrong mesh by another route.

Verdict on the fresh export: `misrooted 0, missing 0, ok: true`, and this time
`ok: true` means something.

### The scanner's other blind spot

`scan_closure` matched `res://([^"\')\s]+)`. A reference that never says
`res://` was not matched, not counted, not reported — **no opinion in either
direction**. The graybox site is written exactly that way:
`lot.write_godot_scene(portable=True)` emits ext_resource paths relative to the
scene file, on purpose, so a scene and its siblings form a drop-anywhere folder.
The root `site.tscn` names its five buildings as `path="buildings/<name>.glb"`
and the scan counted the file while saying nothing about the five.

The patch reports the **count** so the number stops being invisible, and fails
only on a relative path that resolves to nothing or climbs out of the package —
broken under every reading of how the engine treats it, and therefore safe to
call a defect without betting on which reading is right. If the count matters,
the portability test is the instrument that has the engine's actual answer.

---

### Arming the gate, and what that turned up

`CLOSURE_ENFORCED` was False with a written precondition: "wants the missing-art
copy fixed first — otherwise it fails on a defect it did not cause." That was
met, so it is now True.

**Flipping a one-character flag was not a one-character patch.**
`ClosureResult.ok` reads seven counters. The summary that goes into the
exception named five: `misrooted_resource_count` and
`unresolved_relative_count` were both added after that string was written and
neither was threaded in. An export failing purely on either would have raised
with every number in its own message reading zero:

```
EXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 absolute path(s),
0 external reference(s), 0 required plugin(s), 0 required autoload(s)
```

Harmless while it only printed a warning nobody had to act on. The moment it
raises, that string IS the diagnosis. Same shape as the `--verify` that printed
"closure verdict clean" over a broken export — a number describing part of a
table, reading as if it described all of it. Verified by cross-checking the
format string against `ok()`: seven counters, seven placeholders, seven
arguments.

The patch also refuses to apply if `closure.py` lacks those fields, since
formatting a field the dataclass does not carry turns a closure failure into an
`AttributeError` — a worse error than the one it was reporting.

### A player controller in a shell

Measured on the first `pure-shell` export run under the armed gate:
`lot_player.gd` (10,878 bytes) and `lot_site_walk.gd` both shipped, referenced
by nothing. They belonged to the walk scene; `strip_walk` deleted the scene and
left the two scripts it was the sole referrer of. Closure scanning cannot see
this — an unreferenced file resolves fine, it simply has no business in a
package whose own mode is documented as functional geometry, collision and
anchors only.

They are NOT in `_QA_HARNESS_FILES`, and the difference is the point. That list
goes unconditionally because nothing may ever ask for a QA harness. These two
ARE asked for: `lot.py` emits the walk scene naming both, so an `--include-walk`
export needs them, and stripping them unconditionally would leave that profile's
scene naming two files that are gone — which, with the gate now armed, is a
failed export rather than a warning. So they go only alongside the walk scene,
and only when `_still_referenced` finds nothing else naming them. Deleting by
basename across a tree without checking is `skip`-vs-`skip_rel` in a new
costume.

### Issues that name the file

Every issue `scan_closure` reported was labelled `f.name`, so all five building
scenes reported as `site.tscn` — the six-identically-named-files ambiguity,
inside the instrument built to diagnose it. Tolerable as a warning; with the
gate armed those strings are the exception body. They now carry the
package-relative path. `f.name` is kept where it is correct, against the
`_METADATA_FILES` basename set.

### Is Lux needed? Only to build.

Two claims, and only one is true. The FACTORY needs the Lux checkout: `lux_apply`
is a pipeline job running the real addon. The PACKAGE must not, and now
demonstrably does not.

`probe_lux_free.py` checks four things, one of which nothing else could:
GDScript's second reference mechanism. A global class name carries no path, so
a script pulled in by name leaves nothing for a `res://` scanner to follow —
the hole that shipped in v0.10.1 as 30 parse errors from a package that scanned
clean.

First run reported 8 unresolved names. **All 8 were the instrument.** Six were
node-name assignments (`sun.name = &"LuxSun"`), one was inside a comment, one
was prose in a preset's `description` field. The precise checks — `extends` and
`script_class=` — were clean throughout. The `Lux*` scan now runs on code
positions in `.gd` only, with strings and comments blanked first, and is
verified against a fixture carrying all three false-positive shapes plus both
genuine failures. An instrument that cries wolf gets switched off.

Then the engine agreed:

```
engine_check: passed      parser_error_count: 0     shader_error_count: 0
scene_instantiated: true  required_plugin_count: 0  status: PASS
```

### Where both modes finished

```
                        portable-godot        pure-shell
resource_count                      36                 2
missing / misrooted               0 / 0             0 / 0
relative refs / unresolved          5 / 0             5 / 0
absolute / external / plugin / autoload   all 0       all 0
ok                                true              true
```

`relative_reference_count: 5` is the graybox site's bare paths, counted for the
first time in either mode. `resource_count` fell 38 → 36 in `portable-godot`:
exactly the two orphaned scripts.

## The other arc: ten wrong calls, and a section about them

`CLAUDE.md` gains `## Verification — what you remember is not what is there`,
placed straight after `Grounding` because it is the next failure along.
`Grounding` says read the repo before changing it, and **all ten of these
happened with that rule followed**. The files had been read. Then a claim got
made from the memory of them.

Three shapes, three rules:

1. **Name what produced an artefact before concluding anything from it.** Four
   of the ten. Five different files are called `site.tscn`, one mission has a
   greybox build and a themed build standing different shells, and
   `export_closure.json` (the fixer's log) sits beside `export_closure_scan.json`
   (the judge's verdict).
2. **Re-read the interface in the turn you call it.** `_copy_tree`'s `skip`
   matches basenames anywhere in the tree; used to exclude one root `site.tscn`
   it took all six, and the review frame went 88% void → 98%. The comment saying
   so sits four lines above the call and had been quoted correctly in that same
   patch's docstring an hour earlier.
3. **Never write a checker against a guessed schema.** A `--verify` looked for
   `unresolved`/`missing`; the file writes `ok`, `issues`,
   `missing_resource_count`. `or []` turned the absence into an empty problem
   list and it printed **"closure verdict clean"** three lines under
   `EXPORT_CLOSURE_BROKEN: 21 unresolved`.

**The tell: a turn that ends with something shipped and nothing re-read.**

The tenth was made while writing the section, which is the most useful thing
about it. The patch installing it reuses the standard `_apply` helper, whose
line-ending test asks `_CRLF in anchor` — correct in every patch before it,
because every anchor before it spanned several lines. This anchor is
`## Where fixes land`: one line, no newline in it at all. The test answered LF
for a CRLF document and the first run wrote **81 bare LF lines** into
`CLAUDE.md`. Caught by counting endings in the output, not by re-reading the
helper. `_eol` now derives the ending from the file and a mixed result refuses.

`ENEMY_SIGHT_RANGE` is separated out in the section and is not one of the ten:
sound reasoning, bad measured outcome, reverted with its numbers written into the
constant it moved. That is what measurement is for.

---

## Open, in the order I would take them

1. **Re-run the mission.** Every Laser Tag number in `SESSION_0811.md` was
   measured against a package that was 98% missing its geometry. `sightlines`
   10/20, `npc_pathing` 10/20, the 1,179 `player_stuck_events` — none of those
   are known to be real. The plateau finding itself may not survive a level
   that actually has walls. This is now the single highest-value thing to do.
2. **`PIPELINE_MAP.md` has drifted and the audit has never been acted on.**
   `factory_map.py --check` reports `walktest_navqa` and `themed_site_assemble`
   named nowhere in it — two of the three drifts the script's own docstring
   recorded on 2026-08-09. The doc has no generated block, so the script can
   only audit by name. Paste the generated section over the hand-written DAG
   table, markers included, and `--write`/`--check` maintain it from then on.
3. **The DAG picture covers only half the pipeline.** `dag_light.png` stops at
   `lux_apply`; nothing about export, localize, closure or the package is on
   it. `factory_for_engineers.svg` covers that half, and is hand-drawn, so it
   drifts the same way — that is what item 2 fixes for the table and nothing
   fixes for the pictures.
4. **Surface the continuous metrics** on the run line and in candidate
   comparison. Unchanged from 0811.
5. Carried from 0811: `sightlines` enemy distribution, `npc_pathing`,
   `enemy_count` not reaching Lot, `patch_map_derived.py` unapplied, nav-gate
   re-bake, `--sweep` miscount, `_bridge*` plate constants, by-eye roof check.

## Things now known that were not

- **`res://` is absolute, and that is a composition hazard, not a detail.** Three
  tools each correct in isolation produced a broken package because a path
  written against one root was copied under another. Any future stage that moves
  a staged package is the same bug waiting.
- **A resolving reference can be the wrong reference.** `missing`, `misrooted`,
  `absolute` and `external` between them do not cover it. The only reason it was
  found is that `--probe` printed which refs also resolved at the export root.
- **The judge and the fixer must be named apart.** `export_closure.json` is the
  fixer's log and its `unresolved` list fills only when a repair was attempted
  and failed. A scene referencing art that was never copied leaves no trace in
  it at all. One name answering two questions is how an empty export read as
  clean.
- **Walking the deliverable finds what walking the outputs cannot.** Everything
  in this session followed from wrapping the export instead of the job outputs.
- **A probe that runs before its own patch is worth writing.** Four patches now
  carry `--probe`, measuring a real export without the patch applied. The
  137/132 arithmetic that confirmed both instruments came from running one
  against the other's output.
- **Promoting a warning to an error audits the error message.** Flipping
  `CLOSURE_ENFORCED` surfaced a summary that named five of seven counters and
  would have raised with all zeros. A string nobody had to act on had never
  been read.
- **An instrument's first run is about the instrument.** `probe_lux_free.py`
  reported 8 failures and all 8 were its own regex. The fix was in the probe,
  and it took reading every one of the 8 to know that — which is the rule the
  morning's CLAUDE.md section states.
- **Closure scanning cannot see an unreferenced file.** It resolves fine. The
  player controller in the shell was found by reading a directory listing, not
  by any check.
