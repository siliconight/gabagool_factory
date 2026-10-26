# Jobs that re-run with every recorded input unchanged

2026-10-26. Opened from roadmap 316's remainder ("the site re-assembles for every layout on a lighting change").

## Retracted: "a lighting change re-assembles every layout's site"

`docs/AUTHORING_LOOP.md` increment 6 recorded that changing the time of day (revision 1 to 2 of `levels/panel_trial`)
re-ran `lot_assemble` for all three layouts, and 316 carried it as "the site re-assembles for every layout". **The
time of day was never shown to be the cause, and the evidence says it is not:**

- Neither the plain nor the themed site spec Lot reads (`.level_factory/temp/panel_trial_001/candidate_seed_*/site.json`)
  contains the time of day, in any field.
- Revision 1's walk, which changed nothing after generation, ALSO re-ran all three `lot_assemble` jobs
  (`evidence/walk_jobs.txt`).
- `launcher_trial`'s walk, with no change either, cache-hit all three (`evidence/launcher_walk_jobs.txt`).

## Measured

| Run (job lists in `evidence/`) | Interpreter that ran the CLI | `deli_generate` x3 | `lot_assemble` x3 |
|---|---|---|---|
| panel_trial generate 06:21 (`generate_jobs.txt`) | system Python 3.14 | ran | ran |
| panel_trial walk, revision 1, 06:48 (`walk_jobs.txt`) | system Python 3.14 | cache | **ran** |
| panel_trial walk, revision 2, 07:10 (`walk2_jobs.txt`) | system Python 3.14 | cache | **ran** |
| launcher_trial walk 08:21 (`launcher_walk_jobs.txt`) | `.venv` Python 3.13 | cache | cache |
| probe: panel_trial `run --art --gameplay`, nothing changed, 09:5x (`probe_jobs.txt`) | `.venv` Python 3.13 | **ran** | **ran** (81 of 90 jobs ran) |

Probe, seed 9003's `lot_assemble` receipt before and after (`evidence/lot_9003_receipt_*.json`): every recorded input
-- the building hashes, `shell.glb`, `site_spec_hash`, `navqa`, `walkable` -- identical; the site spec file
byte-identical (0 differing fields); the digest different (`400d3522...` -> `199a43c4...`).

## Why the receipt could not say

`Scheduler._attempt_job` (packages/jobs/scheduler.py) hashes twelve components into the digest
(`BuildFingerprint.digest`, packages/artifacts/provenance.py): adapter id and version, tool version, repository
commit, executable versions, normalised arguments, input hashes, upstream artifact hashes, declared environment,
seed, schema versions, output contract. The receipt, whose comment says it records "WHAT this decision was based
on", wrote the adapter version, tool version, repository commit and inputs -- not the executable versions, arguments,
environment, upstream hashes, seed or output contract. It also overwrote itself, so the receipt from the run that
built the cached output was gone. A re-run with identical recorded inputs was unattributable from disk.

Level Factory 0.254.0 writes the whole fingerprint into the receipt and keeps the previous receipt when the digest
moves; `packages/jobs/receipts.differences(job_dir)` names what moved.

## Not yet known (each is a hypothesis, not a finding)

- The probe changed interpreter (3.14 -> 3.13): the executable versions are in the digest, so that may account for
  the probe's 81 re-runs. Unproven until a receipt pair says so.
- The two panel_trial walks re-ran `lot_assemble` on ONE interpreter while `deli_generate` cache-hit. Something in
  `lot_assemble`'s digest outside its recorded inputs moved between generate and walk: argument, environment or
  upstream hashes are the candidates. Unproven.

Next: on 0.254.0, run panel_trial's art build twice on one interpreter, then once after a time-of-day change, and read
`receipts.differences` for every job that ran.
