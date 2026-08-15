# Session 0815 — the emptier the package, the more certainly it passed

Continues `SESSION_0812.md`. The 0814 work — export naming, the functional
lock — is in `level_factory/CHANGELOG.md` rather than a session doc. Five tool
releases with five amendments, two certified sets, and seven defects that were
all the same animal.

**The short version:** `scan_closure` walks the package **from its entry
scene**. An entry that references nothing is therefore trivially closed. Three
separate export modes shipped packages that opened to an empty level, and every
instrument in the toolchain called them fine — the closure scan loudest of all,
because the less a package contained the less there was for it to fail on.

---

## The headline: a check that starts from the wrong end

The first real `art-unlit` export of `lot_demo_001`:

```
180 files      28,684,156 bytes of themed geometry
export_closure_scan.json  {"ok": true, "resource_count": 6,
                           "missing_resource_count": 0}
```

Six resources in a 180-file package. And the entry, in its entirety:

```gdscript
func _ready() -> void:
	print('scene instantiated ok')
```

No `load()`, no `add_child()`. The portability test would have agreed as well —
that marker prints whether or not a child was added. Three green readings over
an empty level.

**Why it was empty.** There is no `site.tscn` at the export root — in *either*
package. `themed_site_assemble` writes one, 31,872 bytes, and it reached no
package at all. The lit export got away with it because
`presentation/lux.applied.tscn` is Lux's output *over* that assembly and stands
in for it. Drop Lux and the five `lot/<archetype>/site.tscn` packages are left
with nothing that positions them.

`write_entry_scene`'s `elif site.exists()` could never have caught it: the file
it looks for was never in the package.

**And the guard written for that found two more.** Pure-shell had been hollow
since this mission grew a `dispatch_handoff` — `base_dir` chose the handoff
**or** the graybox, where the comment three lines above already calls the
handoff a *layer*, and a layer goes on a base. Two exports of the same mission
measure it:

```
lot_demo_001.pure-shell     2026-08-10   site.tscn 25,378 B   entry 688 B
LF_lot_demo_001.art-unlit   2026-08-15   absent               entry 571 B
```

Two closure test fixtures then turned out to have described empty packages
since the day they were written.

---

## Five releases, five amendments

| release | what | amended by |
|---|---|---|
| 0.33.0 | the stub Zoo's `--dress` published no geometry; `zoo_dressing_build` declares its `.glb`; the integration test reads the status word | 0.33.0b — the export names changed under it |
| 0.34.0 | `_layers_produced`: the art layer stops being inferred from Lux's output | 0.34.0b — the test helper, written twice |
| 0.35.0 | `LAYER_LIGHT` — Lux's apply pass becomes declinable | 0.35.0b — one version, read from one file |
| 0.36.0 | `MODE_ART_UNLIT` — the same build, shipped twice | 0.36.0b — a fourth list nobody knew was a list |
| 0.37.0 | the assembly scene ships; an entry that instances nothing raises | 0.37.0b, 0.37.0c — pure-shell, and the 659 tests |

`factory-v1.23.0` pinned 0.32.0 → 0.34.0 (skipping 0.33.0, which was tagged
while its suite was still being measured). `factory-v1.24.0` pinned
0.34.0 → 0.37.0.

---

## Item 43, answered

`factory-v1.22.0` recorded nine failing tests and refused to say whether 0.32.0
caused them: *"the comparison is one revert and two runs, and it has not been
run."* It was run. The answer is no.

The nine were **one** failure with eight downstream absences.
`presentation_compose` failed on a missing `*_dressing.glb`, so
`themed_site_assemble`, `lux_apply` and `dispatch_handoff` never ran. The cause
was the test fixture: the stub Zoo's `--dress` branch wrote its index and no
geometry, while its own `--fixtures` branch twenty lines above had always
written both — which is exactly why `lux_fixture_gate` succeeded in the run this
broke.

`dressing_glb", "_dressing.glb"` appears twice in
`adapters/presentation/__init__.py.pre_032` and twice in the current file,
unchanged. The guard predates 0.32.0 by about nine days. 0.32.0 repaired
collection and turned the lights on in a room dark since 2026-08-06.

---

## Seven defects, one family

Each is a check that could not see what it claimed to cover.

1. **A stage name in stdout proves nothing.** The line
   `bank_block_001.presentation_compose  failed` *contains*
   `presentation_compose`, so `assert stage in r.stdout` passed on the stage
   that broke the run. Six of eight checks would pass on a totally failed run;
   the two that caught anything did so by never appearing at all.

2. **A bake that declared only its index.** `zoo_dressing_build` listed
   `{bid}_dressing.built.json` as its expected output and not the `.glb`, so a
   bake that published no geometry reported SUCCEEDED and the failure surfaced
   two stages later as somebody else's input error, naming a directory upstream.

3. **The art layer inferred from Lux.** `cmd_export` answered "did the art layer
   run?" with `lux_dir.exists()`. A mission whose Pixelcoat/Zoo/Patina pass
   succeeded and whose Lux stage failed exported a manifest declaring no art
   layer, on a package full of art. Nothing reads that field, so nothing
   objected.

4. **An identity dict that only ever raised.** `cmd_export` held
   `mode_map = {"portable-godot": MODE_PORTABLE, ...}` — every entry mapping a
   value to *itself*, since `MODE_PORTABLE` **is** the string. Its only real
   behaviour was `KeyError` on a mode it had not been told about, and it did
   exactly that the first time `art-unlit` was typed at a real workspace.
   `cmd_portability_test` twelve lines below already read `args.mode` straight
   through.

5. **Three packages that opened to nothing** — the headline above.

6. **28 tests standing in for 659.** Mine. See below.

7. **A test helper written twice**, one copy with `exist_ok=True` and one
   without. The copy that passed was the one that will never run in CI.

---

## What was measured, and what was not

```
level_factory tests/unit                    659 passed
level_factory tests/service + integration    28 passed
level_factory tests/real_tools                9 passed, 1 skipped
```

On `lot_demo_001`, all three modes exported and compared file by file:

```
             files          bytes    entry
lit            214     28,967,463    708 B  -> presentation/lux.applied.tscn
unlit          181     28,716,346    688 B  -> site.tscn
only in lit     33                          Lux's outputs AND its whole runtime
only in unlit    0
```

The unlit entry went from **571 bytes instancing nothing** to **688 bytes
instancing `res://site.tscn`** — the same size as the 2026-08-10 pure-shell
entry that worked. Both packages share an interior folder name, so a recipient
can swap one for the other without every `res://` path moving.

**Not measured, and the certification says so.** No mission has been RUN with
`--art --unlit` through Blender and Godot. The art-unlit packages here were
built by exporting a mission that *ran* Lux and subtracting — the case the A/B
needs, not the case a collaborator producing their own unlit level would hit.
Roadmap 47 stage 3b.

The one skipped real-tool test is the **Dispatch** adapter, skipped for missing
example build inputs including `build/lux/lux.profile.json`. It is the only test
in the repository that exercises Dispatch consuming Lux's output — the exact
relationship 0.35.0's `dispatch_dep` conditional rewired. Skipped for want of
fixture data, not by this work, and named in the manifest entry rather than
counted as green.

---

## My own instrument failure

0.34.0, 0.35.0, 0.36.0 and 0.37.0 each reported **"still green"** against 28
tests from `tests/service` and `tests/integration`. `tests/unit` is 659 and none
of them ran it. `test_fanout.py` was red from 0.35.0 onward — its `_plan` asks
for `layers={LAYER_ART}` and asserts `lux_apply` is planned once — and said so
to nobody for three releases.

0.35.0 fixed exactly that assertion in `test_planner_graph.py` and missed this
file, because the search was *"the file I know about"* rather than
`grep -rn lux_apply tests`. That grep now runs inside 0.37.0c's selftest and
prints what it finds.

A subset described as the suite is the same failure this whole session is
about, one level up. Every level_factory selftest now runs `tests/unit` whole.

Three smaller versions of the same thing, all in checks I wrote:

- `pyproject.toml` drifted eleven releases from `VERSION`; 0.34.0 corrected it
  and added a check, and **0.35.0 drifted again by one release in the very next
  patch**. Fixed by deleting the second copy — `dynamic = ["version"]` reading
  `VERSION` — because a check that two files agree has to be remembered by every
  future release, and the one that forgets is the one that drifts.
- Two attempts to detect "did the test run" by reading pytest's prose were both
  wrong. `pyproject.toml` carries `addopts = "-q"`, so every `pytest … -q` runs
  at `-qq` and the count line disappears: a green 28-test suite writes **80
  bytes of dots** with no `28 passed` in it. The return code was always the
  answer.
- A check searched a whole file for `export_build_dir_name` and failed on the
  comment explaining why that function is *not* used. Stripping `#` lines does
  not help — it was a docstring. Parse the file and look at the calls.

---

## Open, in the order I would take them

1. **Roadmap 47 stage 3b.** A real `--art --unlit` run through Blender and
   Godot, exported both ways and portability-tested. The only claim in this arc
   resting on inference rather than a reading.
2. **Dispatch's discarded `mission.tscn`.** It writes 65,493 bytes — the
   composed mission scene — and every export throws it away and writes a
   ~600 byte stub. `export.py` says that is deliberate, an export carrying one
   entry. Nobody has opened the 65 KB scene to see what is in it. Third artifact
   this session doing less than its name implies.
3. **The `fixtures` branch's undeclared `.glb`.** Same shape as defect 2 above,
   deliberately left: no run has failed on it, and a mission with zero light
   fixtures might legitimately bake no geometry. Measured and open, not fixed
   blind.
4. **The `HANDOFF.md` assertion is loose on purpose.** It searches the package
   rather than asserting a path, because whether a folder export nests an
   interior `LF_<mission>/` had not been observed. It has now — it does not —
   so this can be tightened.
5. **`build/` fixture data for the real-tools Dispatch test**, which would
   un-skip the only test exercising Dispatch against Lux's output.
6. Carried: 57 stale buildings, `cbp`/`night_pawn`/`primos_pizza` failing
   nav_gate, `laser_tag` without a CHANGELOG, `docs/INTERACTIVES.md`'s zoo twin
   uncompared, items 44/45/46 (Zoo collision substitutes, non-collision surface
   dressing, the interactive state machines that reach no package).

---

## Things now known that were not

- **Closure walks from the entry, so an empty package is a closed package.**
  `ok: true, resource_count: 6` on 180 files is not a bug in the scanner; it is
  the scanner answering the question it was asked. The guard belongs where the
  entry is written, not in any one mode.
- **A guard that knows about modes guards only the modes it knows.**
  `write_entry_scene` raising is what makes a mode nobody has written yet unable
  to ship hollow — and it is what found pure-shell, which nothing in item 47 was
  looking at.
- **"Does this mode ship Lux's result?" and "does this mode ship the art?" are
  two questions.** `profile.mode == MODE_PURE_SHELL` answered both correctly for
  as long as pure-shell was the only mode that declined anything.
- **A layer goes on a base.** `handoff if handoff.exists() else graybox` reads
  as a sensible default and is a silent subtraction the moment the optional
  thing appears.
- **Identity maps are lists in disguise.** `{v: v}` keyed by its own values does
  nothing except require maintenance and raise on what it has not learned. The
  fix is deletion; the guard is a test that parses the CLI's `choices` out of
  the source and asserts both directions against the code's own set.
- **The fixture can be healthier than the thing it stands for.** 0.36.0's
  fourteen tests all built a handoff containing `site.tscn`, so every package
  had something to instance and the real defect was invisible to all of them.
  Real `lot_demo_001` has no such file.
- **A probe that spells its own paths is worth the duplication.**
  `probe_unlit_ab.py` writes out `LF_<mission>.<mode>` rather than importing
  `export_build_dir_name`, because a probe that asks the code what to look for
  cannot notice the code looking in the wrong place.
- **Stage 3 found in twenty minutes what three stages of unit tests could not.**
  Every one of the seven defects was found by running the real command against
  real data, or by a test written after that run — never by a check written
  alongside the code it covers.
