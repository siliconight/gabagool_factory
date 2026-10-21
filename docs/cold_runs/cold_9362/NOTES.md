# Cold run 9362 -- VOID: the seed it named is not one of its batch's candidates

**What it was for.** Roadmap 275: Deli Counter 0.244.0's teller-line queue in a shipped package, on bank_block_001 at
seed 9281, which `lot_for_brief` says draws bank_branch_a02
(`docs/findings/crowd_barrier_267/find_arena_seed.py` over the brief, seeds 9000 to 9300).

**Why it is void.** It was staged from cold run 9352 (`stage_batch.py 9362 9352 ...`), whose batch carries
`seed_base` 9054, so the shell leg built the candidates 9054, 9155 and 9256 -- and the drive was told seed 9281.
Level Factory's `approve candidate_selected --candidate bank_block_001.candidate.seed_9281` accepted a candidate no job
had built, and the next approval, `functional_shell_locked`, refused: "THIS LOCK PROTECTS NOTHING ... the site file
contributed NO protected key" -- true of a candidate that does not exist, and no help in finding the mistake. The
drive stopped at `approve3`, before the art leg.

**`INTERVENTIONS: 0`, and it is not a clean run.** `cold_run.py --end` counted no journal note and no changed tool
file (01:01:49 to the stop at approvals), which is what the count measures; it made no level, and the count does
not say so. Read a stopped run's zero with its driver log.

**What changed because of it.** `tools/cold_drive/cold_drive.sh` now refuses a named seed with no built candidate
before any approval, and lists the batch's own -- tried against this run's workspace: seed 9281 refused ("candidates
9054 9155 9256"), seed 9054 passed. That Level Factory's `approve candidate_selected` accepts an unbuilt candidate at
all is filed (roadmap 278). Cold run 9363 runs the same level with its batch's `seed_base` set to 9281.

**Tools:** Zoo 1.119.0 (3f54314), Deli Counter 0.244.0 (33e81109); the rest as 9361.
