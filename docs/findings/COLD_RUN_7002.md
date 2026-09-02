# cold_7002 — the second cold run, and the correction it forces

Roadmap **item 17**, run 2. 2026-08-28.

    interventions   1     (the tool said 1, and 1 is right — no hand-classifying)
    retries         1
    observations    4
    outcome         BLOCKED, no package — the run needed a second intervention it did not get

Run 1 (`cold_7001`) changed the geometry and held the vocabulary. This one
changed the vocabulary: `bank_block_001` — `urban_bank`, `street_block`,
3 buildings, 3 candidates, `delco_1997` — byte-for-byte unchanged
(md5 `41b8cd6e5e3915bd745abb724c9cc3a8`) at `seed_base 7002`, deriving
7002 / 7103 / 7204. Fresh workspace, `doctor` green before `--begin`,
2,350 source files hashed across the ten repos.

---

## THE CORRECTION TO RUN 1, first, because it matters most

`docs/findings/COLD_RUN_7001.md` and item 17 both said run 1 reached **a gated
package with nobody's hands in it**. The zero is still true. **"Gated" is not.**

cold_7001 carried two `LUX_FIXTURE_COLOCATION` blockers on its selected
candidate. It printed `Structural checks passed` only because Level Factory
0.49.0 discounted them as belonging to an eliminated candidate — roadmap 68,
found and fixed the same day. Under 0.50.0 that identical run reports
**`Blocked: unresolved blocking issues (blockers open: 2)`**, which is what
cold_7002 does on the same two blockers.

So the honest statement of run 1 is: *it produced an exported package having
needed zero interventions, and the verdict that called that package sound
rested on a gate since proven wrong.* The measurement stands; the adjective
does not. This is recorded here rather than quietly edited because a
correction that leaves no trace is the failure this whole exercise measures.

---

## The one intervention

`pixelcoat_build` exited 1:

    $ python3 -m pixelcoat.cli.main theme-library --theme delco_1997 ...
    pixelcoat: error: no theme profile for 'delco_1997' at
      C:\...\pixelcoat\profiles\themes\delco_1997.json

The brief says `"theme": "delco_1997"`. Pixelcoat ships `delco.json`; Zoo
carries a `delco` style on its species. Nothing maps one name to the other.

**Intervention 1: `delco_1997` -> `delco`, in the brief and the batch.** Of
the three options on the table — author the missing profile, point the spec at
the theme that exists, or stop the run and record it — the second was chosen:
cheapest, and it let run 2 go on to measure the rest of the pipeline. The
discomfort is real and is recorded rather than argued away: editing the spec
until the output works is the failure mode item 17 is named after. The defence
is that the spec named an asset that does not exist, which is a correction
rather than a tuning.

**It resolved completely.** Pixelcoat, `zoo_fixtures_build`, `zoo_kit_build`,
`zoo_dressing_build`, Patina, `presentation_compose`, `themed_site_assemble`,
`lux_apply` and `dispatch_handoff` all succeeded. The fall-through was exactly
one missing file, nothing deeper.

**The instrument could not have caught this one.** The cold spec lives in
`docs/cold_runs/`, outside the ten hashed repos — deliberately, so that
authoring it is not counted — which means editing it is not hash-detected
either. The journal was the only record. That is a hole in how run 1's method
was built, and it is why the `--note` was mandatory rather than belt-and-braces.

---

## What blocked it

The same defect that was hiding inside run 1:

    cold_7001   20 of 37 fixture markers, worst 0.25 m
    cold_7002   12 of 19 fixture markers, worst 0.25 m

Different theme, different archetype, different building count, different
seeds — and **the worst distance is identical to the centimetre**.

> **CORRECTION, same day.** This was first written as "something applies a
> constant 0.25 m displacement between Deli Counter's fixture markers and the
> lamps Lux spawns on them", and filed as a producer bug. Reading the producer
> refuted it. `lux_light_loader.gd` sets `mount_height = -0.25` in the
> `"fluorescent"` branch alone — every other type is 0.0 — under a comment
> explaining that real tubes hang below the ceiling plane, and that a lamp
> sitting flush streaks and scorches a ring (walked 2026-08-23). The spawner
> puts the rig root exactly on the marker; the rig then hangs its bulb 0.25 m
> below. `LuxValidator.check_fixture_colocation` compares the marker to the
> `Light3D`, not to the rig, against a flat 0.10 m tolerance — so it measures
> the deliberate bracket-to-bulb drop and calls it floating light. **The gate
> is the defect, not the lamps.** It accounts for every number: the distance is
> constant because it is a constant, the counts vary because only fluorescents
> hang, and `markers == spawned` because nothing was ever missing. Roadmap 71
> is retracted as filed and reframed. The constant was read as evidence of a
> bug when it was evidence of a decision — the third time this project has
> blamed a producer before reading it.

Reaching a package from here needs a second intervention, and that one would
be a real tool fix rather than a config correction. The run was ended instead:
a defect the pipeline reproduces across specs is worth more as a filed defect
than as a patch applied to get a package out.

---

## What else it found

**Roadmap 69 confirmed on a second brief.** Deli Counter built
`lf_bank_block_001_7002` with `seed=1999` — against `seed=1989` for the rockay
brief. So DC's seed is not a global constant; it varies by brief and still
never carries the candidate seed. Same defect, second spec, and the second
data point rules out the tidiest wrong explanation.

**Two identical consecutive runs disagreed.** `run bank_block_001` was issued
twice with nothing changed between them. Neither cache-hit — all 12 jobs
re-executed both times — and the findings total moved **49 -> 42**. The
scheduler keeps only attempt `1/`, so the second run overwrote the first's
reports and the difference is unattributable. Filed with the mechanism that
explains half of it and the observation that refutes the tidy version.

**Nothing checks a theme resolves before the graybox leg runs.** `doctor`
passed, `plan` passed, twelve jobs of Blender and Godot were spent, and then
the art pass failed on a missing JSON file that a millisecond's check would
have caught at plan time. Filed.

**Level results.** Walktest PASS on all three candidates (spines 197 / 178 /
115 m). Laser Tag FAIL on all three — 45 / 40 / 40, `exit=2` — and the graybox
leg still reported `Structural checks passed`, because LT's findings top out
at `major` and never block. Advisory by design, per the Authority Statement,
but a tool grading the level FAIL while the run reports passed is worth
knowing about.

---

## The instrument, on its second outing

`cold_run.py` needed no hand-classifying this time — the point of roadmap 70:

    interventions NOTED in the journal        1
    tool source files CHANGED on disk         4
      attributed to the pipeline, NOT counted 4
      UNATTRIBUTED, counted                   0
    retries (same command re-run)             1
    observations (looked, did not touch)      4
    INTERVENTIONS: 1   (journal 1, unattributed files 0)

All four changed files were Level Factory writing DC specs and Deli Counter
regenerating its index, each printed with the reason it was excused. On run 1
that same set produced a headline of `INTERVENTIONS: 1` for a run that needed
none. `--observe` carried four notes that would otherwise have had to be filed
as interventions.

---

## Where the two runs leave item 17

    cold_7001   0 interventions, 1 retry   exported a package; the verdict on it
                                           was wrong, and is now Blocked (2)
    cold_7002   1 intervention,  1 retry   blocked on the same two lux blockers

Two runs, two vocabularies, and the same defect stops both. Neither run needed
the pipeline patched to produce geometry: DC, Lot, Laser Tag and walktest ran
clean on unseen specs in both. What neither run has produced is a package that
passes its own gate.

That is a better answer than either run alone, and it is not the answer this
item hoped for.

## Afterword, same day — and it is not a cold-run result

The blocker was the gate, not the lamps (roadmap 71, retracted and reframed
above). Lux 0.26.0 made `check_fixture_colocation` measure rig roots instead
of bulbs, and `cold_7002`'s workspace was re-run:

    lux_fixture_gate   blocked   ->   succeeded
    blockers open: 2, findings: 55   ->   blockers open: 0, findings: 53
    exported bank_block_001 [portable-godot]

**55 − 2 = 53.** Exactly the two blockers gone and nothing else moved, which
is the arithmetic that separates a fix from a loosened tolerance. And that
`Structural checks passed` is the first in this exercise that means what it
says, because it ran under LF 0.50.0, where a blocker on the selected
candidate can no longer be discounted into silence.

**None of this changes run 2's number.** It happened after `--end`, on a tool
that had been patched in between. No package in either cold run was produced
cold, and this one least of all. What it changes is what to do next: a third
run was pointless while every cold run ended on the same blocker, and is now
worth taking. Items 69 and 73 are what it would be measured against.
