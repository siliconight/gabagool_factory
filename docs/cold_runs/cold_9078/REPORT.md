# Cold run 9078 — zero interventions

**2026-09-25.** `club_block_014`, the club brief a fifteenth time, at
`seed_base 9078` → candidates 9078 / 9179 / 9280, none previously drawn. The
brief is **byte-identical** to 9077's (sha256 `854bd7c129d0f5d9…`), so the only
variable against that run is the three tool changes below.

## The number

```
interventions NOTED in the journal      0
tool source files CHANGED on disk       3
  attributed to the pipeline, NOT counted   3
    deli_counter/specs/lf_club_block_014_{9078,9179,9280}.json
        "Level Factory writes one DC spec per candidate, per run"
  UNATTRIBUTED, counted                     0
retries (same command re-run)           0
observations (looked, did not touch)    3
INTERVENTIONS: 0
```

`cold_run.py --end` exit 0. Export exit code **read directly**: `EXPORT_EXIT=0`,
closure verdict `ok=true`, 0 issues over 48 resources in a package of 1,082
files, 1,313 external GLB references resolving to 198 files, 0 missing, 0
unportable, 0 unreadable.

## Tool versions at `--begin`

3,072 source files hashed, every repo clean.

```
deli_counter 0.144.0   level_factory 0.112.0   pixelcoat 0.47.0   zoo 1.2.0
lot 0.77.1             lux 0.40.0              patina 0.22.0
dispatch 0.5.2         lasertag 0.23.1         pipeline 0.6.0
```

## What this run was for

Three changes written the day before, none of which had ever run outside a test:

- **Pixelcoat 0.47.0** — `map_sha256` written into every pack manifest by all
  five writers.
- **LF 0.111.0** — `ZooAdapter` hashes each pack's MAP PAYLOADS into its
  fingerprint, not just the manifest.
- **LF 0.112.0** — `PixelcoatAdapter` reports a map present but not matching its
  digest.

All three touch every art job. Every art job succeeded: `pixelcoat_build`, four
`zoo_kit_build`, three `zoo_dressing_build`, `zoo_clutter_build`, three
`patina_apply`, three `patina_dressing`, `patina_surface_dressing`, three
`lux_fixture_gate`, `lux_apply`, `presentation_compose`, `themed_site_assemble`,
`dispatch_handoff`.

**The caching behaved.** In the art leg all three candidates' graybox jobs read
`cache` — correct, they were built in this same run's first leg and nothing
upstream changed. The new map hashing did not cause spurious invalidation,
which was the live risk in LF 0.111.0.

## The legs

| Leg | Result |
|---|---|
| graybox `run` | 12/12 jobs succeeded, 3 distinct candidates, blockers 0, 43 findings, exit 0 |
| `--art --gameplay` | all jobs succeeded, blockers 0, 63 findings, exit 0 |
| `export --mode portable-godot` | exit 0, closure ok, 1,082 files |

Laser Tag: `seed_9078` PASS_WITH_TUNING (4 WARN/3 PASS), `seed_9179` WARN (5/2),
`seed_9280` PASS_WITH_TUNING (4/3).

**`seed_9280` selected**, on the default rule — best grade — because unlike
9077 this run's purpose is candidate-independent. Two candidates tie, so the
tiebreak was metrics: `seed_9078` reports `avg_player_survival_seconds` **10.13**
against 72.46 and 126.89, a sevenfold outlier that its longer engagement
distance (22.01 m vs 18.96) does not offset. Choosing is a decision, not an
intervention; it is in the journal as an observation.

## What is NOT claimed

**`presentation_compose` succeeded, where it exited 3 on the chronic z-fight
gate on runs 9072, 9073, 9075, 9076 and 9077. That is not attributable to this
run's changes.** Nothing in Pixelcoat 0.47.0 or LF 0.111.0/0.112.0 touches
coplanar geometry, and the scenes are not comparable: this `site.tscn` carries
**59 solids with 0 coplanar pairs** against 9077's reported **525 solids and 79
pairs** — a different candidate on a different site with nine times the solid
count. The per-building composes still report stair-vs-floor coplanar findings
(`base:stair0_0_N` against `floor_parts_back` / `floor_stockroom` /
`floor_main_floor`, areas 0.311–0.418) and did not block. Recorded so the next
run does not read this as a fix.

**A near-miss worth recording.** `python tools/check_all.py 2>&1 | tail -35;
echo $?` prints the exit code of `tail`, not of `check_all` — the last command
in a pipeline wins. That figure was almost quoted as a grade. It is the same
shape as the level_factory suite trap written into `docs/COMMANDS.md` the same
day: a number that looks like a verdict and is about something else.

## Against the metric

Runs 9076, 9077 and 9078 are three consecutive genuine zeros. Item 17 asks for
repetition before believing a result, and this is the third — but all three ran
the **same brief family** (`club_block_*`) at different seeds. What is measured
is the pipeline on unseen geometry, not on an unseen vocabulary. A zero on a
brief whose archetype, site shape or theme the tools have not been taught is
still the harder test and has not been run.
