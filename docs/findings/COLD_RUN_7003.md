# Cold run 3 — `bank_block_001`, seed_base 7003

**Begun** 2026-08-29 11:59:22 · **Ended** 15:05:11 · 2357 source files hashed
across 10 tools
**Journal / snapshots:** `_runs/cold/cold_7003/`
**Brief:** `docs/cold_runs/cold_7003/` (seed_base 7003 → seeds 7003 / 7104 / 7205)

## Result

```
interventions NOTED in the journal      0
tool source files CHANGED on disk       5
  attributed to the pipeline             4
  UNATTRIBUTED, counted                  1
retries (same command re-run)           0
observations                            2

INTERVENTIONS: 1   (journal 0, unattributed files 1)
```

The instrument flagged its own DISAGREEMENT: a file changed that nothing wrote
down and nothing claims. It is right to. The count is **1**.

**And no package came out.** The art pass was gate-clean and needed nothing,
and the export was then refused by the functional lock. Item 17 asks whether a
walkable, gated package comes out of one command with nobody touching
anything; on this run the answer is still no, for a reason that has nothing to
do with the count.

| run | seed_base | interventions | retries | outcome |
|---|---|---|---|---|
| cold_7001 | 7001 | 0 | 1 | exported — but the verdict rested on a gate later found broken (item 71) |
| cold_7002 | 7002 | 1 | 1 | blocked — brief named a Pixelcoat theme profile that does not exist (item 72) |
| cold_7003 | 7003 | **1** | **0** | blocked at export — functional regression (item 73) |

## The one intervention

`level_factory/apps/cli/commands/__init__.py`, hash-changed, journal-silent.

One clock, from file mtimes and the job logs:

| | |
|---|---|
| 11:59:22 | `--begin cold_7003`, 2357 files hashed |
| **12:05:38** | **`commands/__init__.py` written — 6 min 17 s INTO the run** |
| 12:06:31.899 | functional shell lock approved |
| 12:06:33.247 | `deli_generate` re-evaluated |
| 12:06:38.478 | `lot_assemble` re-evaluated |
| 12:07:03 | themed compose output |

The file ends the run at 130,113 bytes, which is its size after the item-72
theme-preflight patch (127,726 before). The likeliest account is that the
re-application of that patch — the one that had to be redone because the first
attempt was applied to `out/` and then clobbered by a copy from an unpatched
sandbox — landed six minutes after `--begin` instead of before it.

**That account is not proven and should not be quoted as fact.** `before.json`
stores hashes, not content, there is no backup sidecar beside the file, and
nothing on disk records what those bytes were at 11:59:22. What is established
is narrow and sufficient: the file changed during the run, 55 seconds before
the first job wrote output, and nobody wrote it down.

If the account is right, the count is a procedure error and not a defect: the
run needed no patch, but `--begin` was run before setup had finished landing.
COLD_RUN.md's rule is "setup before `--begin` isn't counted", and its unstated
corollary — that `--begin` must come after setup is complete — was not kept.
Either way the number stands at 1. An instrument that can be talked down from
its reading is not an instrument.

## Why the export was refused

Recorded as an observation, not a patch. `verify_no_drift` reported
`gameplay-anchor registry changed after art pass` and `interactive registry
changed after art pass`. **`collision_fingerprint` did NOT drift** — the shape
of the level is unchanged; only the registries the lock also fingerprints
moved.

The lock was approved at 12:06:31.899. `deli_generate` re-evaluated at
12:06:33.247, `lot_assemble` at 12:06:38.478 — 1.3 and 6.6 seconds later. The
art run cache-missed and re-ran the very jobs the lock had just fingerprinted,
because Level Factory writes its DC specs into `deli_counter/specs/` and so
dirties the repo whose dirty-tree hash is part of the build fingerprint. The
lock fingerprints a tree the pipeline is still writing to.

**The lock was deliberately not re-approved.** Re-approving would have cleared
the block and destroyed the evidence, and the block is correct: the registries
really did change. Roadmap item 73, which was filed as "two runs disagreed
about findings" and is now the thing standing between a clean art pass and a
package.

## Two findings for the instrument

1. **`--begin` cannot tell that a run is starting mid-edit.** It hashes and
   proceeds. A repo that is dirty at `--begin` is invisible until something in
   it changes, at which point the change is indistinguishable from a patch made
   to rescue the run. Recording each tool repo's dirty state at `--begin` would
   have made this reading unambiguous in three seconds instead of an
   archaeology of mtimes. Worth filing.

2. **`--observe` earned its keep.** Two observations recorded, neither counted.
   On `cold_7001` the same material had to go in with `--note` for want of it
   and inflated that run by one (roadmap 70). The separation is doing its job.

## What this run does not tell us

Whether the level is any good. It walked, the corners read correctly on both
the greybox and the themed pass, and walking it is what produced the facade
repetition finding (`docs/findings/REPETITION_BASELINE.md`) — but none of that
is what this number measures, and the cold run stops at the count.
