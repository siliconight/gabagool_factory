# cold_7001 — the first cold run, and what it cost

Roadmap **item 17**, answered once. 2026-08-26 → 2026-08-27.

    interventions   0     (the tool printed 1; see "The number" below)
    retries         1
    outcome         a portable-godot package, exported -- but see the
                    correction below

> **CORRECTION, 2026-08-28, from `cold_7002`.** This document first called the
> outcome "a gated portable-godot package". The zero interventions stands.
> **"Gated" does not.** This run carried two `LUX_FIXTURE_COLOCATION` blockers
> on its selected candidate (roadmap 71) and printed `Structural checks
> passed` only because Level Factory 0.49.0 discounted them as belonging to an
> eliminated candidate -- roadmap 68, found and fixed the same day this was
> written. Under 0.50.0 the identical run reports `Blocked: unresolved
> blocking issues (blockers open: 2)`, which is exactly what `cold_7002`
> reports on the same two blockers. What this run actually shows is narrower:
> it produced an exported package having needed nobody's hands, and the
> verdict that called that package sound came from a gate since proven wrong.
> Left in place rather than edited away, because a correction with no trace is
> the failure this whole exercise measures.

The number is the deliverable. Everything else here is the working that
justifies it, and the three defects the run surfaced on the way.

---

## What was run

`category5_baie_dore_001` — the Baie Doré hero brief, **byte-for-byte
unchanged** (md5 `5665e2cd565dd8f47fd5af51b4e79c75`, verified on both sides of
the copy) — at `seed_base 7001`, a base the factory had never drawn.
`derive_seeds` (`packages/pipeline/planner.py:137`, `seed_base + i*101`) gave
**7001, 7102, 7203, 7304, 7405**; spent seeds were 1997, 2199, 5017, 5118,
5219, 5320, 5421. No collision.

Fresh workspace at `workspaces/cold-7001-ws`, `tools.local.json` copied from
`rockay-ws`, `doctor` green before `--begin`. Spec at
`docs/cold_runs/cold_7001/`, outside all ten tool repos on purpose.

Full path: `init` → `doctor` → `--begin` → `batch create` → `plan` → `run`
(graybox) → 3 gates → `run --art --gameplay` → `export --mode portable-godot`
→ `--end`.

### The tools this number describes

Seven of the ten had drifted from the certified set, which is why they are
recorded rather than assumed:

    deli_counter 0.102.1   dispatch 0.4.2    lasertag 0.9.0
    level_factory 0.49.0   lot 0.49.0        lux 0.25.0
    patina 0.21.0          pipeline 0.6.0    pixelcoat 0.16.0   zoo 0.50.0

2,344 source files hashed at `--begin`. Blender 5.1.1, Godot 4.7.stable.

---

## The number

`cold_run.py --end` printed **INTERVENTIONS: 1**. The honest figure is **0**,
and the gap is the instrument's, not the pipeline's.

Six files were hash-detected. All six were written by the pipeline:

    changed  deli_counter/specs/CATALOG.md
    added    deli_counter/specs/lf_category5_baie_dore_001_7001.json
    added    deli_counter/specs/lf_category5_baie_dore_001_7102.json
    added    deli_counter/specs/lf_category5_baie_dore_001_7203.json
    added    deli_counter/specs/lf_category5_baie_dore_001_7304.json
    added    deli_counter/specs/lf_category5_baie_dore_001_7405.json

Level Factory writes its per-candidate DC specs into the Deli Counter repo;
DC regenerates `CATALOG.md` when it does. Neither is a human reaching into
the machine. The one journal entry marked `intervention` is a **correction to
an earlier journal line**, filed with `--note` because there is no way to
record an observation. Both gaps are roadmap item 70.

**No tool source was edited during this run.** No VERSION moved. Nothing was
removed.

### The retry, stated plainly

One. The run was begun 2026-08-26 21:37 UTC, reached end-of-graybox by 22:15
(the validation report is stamped 22:15:43), and its console was left in
Windows QuickEdit `Select`. The identical command was re-issued at 10:47 UTC
the next morning; DC and Lot cache-hit, the Godot jobs re-ran because the
SQLite index had never committed its WAL.

That re-run was later killed mid-flight —
`walktest_navqa.candidate.seed_7405` exited **3221225786** (`0xC000013A`,
`STATUS_CONTROL_C_EXIT`) and `seed_7304`'s log has no exit line at all — and
issued a third time to completion. Operator-side, both times. Counted as one
retry rather than three because the command never changed.

**The journal's first retry line says "run interrupted", which is probably
wrong** — the evidence says the 08-26 run finished and only looked stalled.
The correction is in the journal beneath it. Left uncorrected in place
because rewriting a journal after the fact is a worse habit than an
inaccurate line with a correction under it.

---

## What the run does and does not prove

**Proves:** handed geometry it has never seen, this pipeline reaches a gated,
exported package with nobody's hands in it. That is the first real evidence
item 17 has ever had.

**Does not prove:** the brief's *vocabulary* — archetype, theme, site shape —
was familiar to the tools even though the geometry was not. One run proves
less than it feels like. Run 2 (`bank_block_001` at 7002: different
archetype, site shape, theme family) is owed before either result is
believed, and item 17 says so itself.

**And the part worth saying loudest: zero interventions is not zero
defects.** The run needed no patches *and* produced three findings. Those two
facts are not in tension — they are the whole argument for measuring this way
instead of measuring how many guardrails exist.

---

## What it found

### 1 — a blocker on the selected candidate was discounted (item 68)

The run printed `Structural checks passed (blockers open: 0, total findings:
119)` on a mission whose **selected** candidate carried two unresolved
blockers.

    .level_factory/approvals/category5_baie_dore_001.selected
        category5_baie_dore_001.candidate.seed_7001

    validation/category5_baie_dore_001.json
        2 issues, severity "blocker", blocking: true
        both candidate_id: category5_baie_dore_001.candidate.seed_7001
        LUX_FIXTURE_COLOCATION  20 marker(s) with no lamp within 0.10 m
        LUX_FIXTURE_COLOCATION  20 lamp(s) more than 0.10 m from any marker

    console
        1 candidate(s) eliminated (the rest carried on): ...seed_7001
        2 blocker(s) belong to eliminated candidate(s) and do not block the mission
        Structural checks passed  (blockers open: 0, total findings: 119)

`packages/validation/model.py:121` decides it, and the predicate never
consults `.selected`. Full mechanism and remedy in item 68.

Two smaller things from the same episode: `lux_fixture_gate` was marked
`blocked` and `lux_apply` ran after it anyway, and the gate process exited
**0** while printing `colocation_errors=2`.

### 2 — every candidate is the same building (item 69)

All five DC specs carry `"seed": 1989`. The 7001 and 7405 specs differ in
**three lines**, all name strings; all five `shell.glb` are 625,404 bytes.
LF computes and passes the right seed at `commands/__init__.py:282` and Lot
uses it at :287 — where it is lost between there and the file DC reads is
**not yet located**, and item 69 does not guess.

The candidates are not identical: Lot varies the layout, and they measure
differently (LT 65/50/50/55/50; nav-qa PASS on 7001 and 7203, FAIL on the
rest; spines 973–1106 m). What is missing is building variety.

LF's own check printed `candidates: 5 built, all distinct` — true, and
shallow: it compares assembled sites.

### 3 — the instrument counts the pipeline's own writes (item 70)

Above, under "The number". Found by its own first real use, which is the good
case for an instrument.

---

## Findings about the level, not the pipeline

These are the toolchain working, not failing, and belong to whoever tunes the
level rather than to item 17.

**Three of five candidates fail nav-qa the same way, and it is not random.**
Every failing path terminates at **y = −3.7** while its target stands at
**y ≈ 0.2** — the below-sea-level vault approach the brief calls for, on a
navmesh island disconnected from the main network.

    7102  proxy_7  -> proxy_8   63.13 m short, disjoint islands
    7304  proxy_11 -> proxy_12  71.78 m short, disjoint islands
    7405  proxy_11 -> proxy_12  72.52 m short, disjoint islands

The buildings are identical across all five (see item 69), so this is Lot's
layout deciding whether the sub-basement connects — which makes it a
placement question, not a building question.

**Laser Tag failed the same line on every candidate**, across five different
layouts: `Bot rarely completed the route (0% of runs) [FAIL]`. All five graded
WARN, all five exited 1, scores 65/55/50/50/50. Five layouts, one failure —
that is not a layout problem, and it is worth its own investigation.

**The selected candidate is the odd one.** seed_7001 scored best (65, 6%
overexposed, crew under fire at 3.1s — inside the target window) but logged
**521 player-stuck events** and took **688 s** against ~60 s for every other
candidate. Selected anyway, deliberately, and the anomaly is recorded rather
than resolved.

---

## Method notes, for the next run

- **Setup is not the measurement.** Everything through a green `doctor`
  happened before `--begin`. A missing Blender path is a laptop problem and
  counting it would slander the tools.
- **Approving a gate is not an intervention.** Three approvals, zero counted.
  Choosing *which* candidate is a decision; making a candidate work is an
  intervention.
- **The console lies about progress.** LF streams nothing while a subprocess
  runs; `jobs/<job>/1/job.log` is the truth. A silent console was misread as a
  hang twice in this run, once by each of us.
- **Windows QuickEdit will stall a long run.** A click in the buffer blocks
  the next stdout write. It cost this run twelve hours.
- **Do not fix what the run finds, while it runs.** Every instinct says patch
  it. Patching erases the evidence that a patch was needed, which is the only
  thing being measured.
