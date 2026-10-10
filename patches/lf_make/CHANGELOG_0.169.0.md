## [0.169.0] - make: one level from a batch, start to finish; pick names the candidate

**Roadmap 202.** A level is ten commands: batch create, plan, the shell leg,
three approvals, the art leg, export, and walk. The cold runs drive them from
`tools/cold_drive/cold_drive.sh` in the factory, which has two problems for
somebody else:
- **It is bash.** A Windows machine with Blender and Godot has no bash: Git
  for Windows is what supplies it on the machine that wrote it.
- **One approval needs a choice nothing gave them.** `candidate_selected`
  needs one of three candidates. `status` lists jobs, not candidates, so
  there was nothing to choose by. The driver picks with a root script,
  `tools/cold_drive/pick_candidate.py`, which is outside Level Factory.

### What it is now

**`level-factory pick <mission>`** (`packages/pipeline/pick.py`):
- prints each candidate's major findings, route completion and what put it
  out, with the candidate id to select on the last line;
- `--json` gives the same as data.

It uses the rule every cold run since 9194 has picked with, moved here
unchanged:
- **Out:** a candidate whose walk test is not ok, or against which Laser Tag
  raised a major `LT_ROUTE_NEVER_COMPLETED` or
  `LT_MAP_ENEMY_PATHING_BROKEN`.
- **Among the rest:** the fewest major findings, then the highest route
  completion, then the lowest seed.
- **If every candidate is out,** the fewest major findings is still picked,
  and it says so.
- **Refusals:** a mission with no candidates, or no readable validation file,
  is refused rather than guessed.

Run over every cold workspace on the machine that wrote it, 46 missions, it
picks what the root script picks in all 46.

**`level-factory -C <workspace> make <batch.json>`** runs these steps:
1. `init` (only when the workspace is new);
2. `batch create`;
3. `plan`;
4. the shell leg;
5. the pick;
6. the three approvals;
7. the art leg;
8. `export --mode portable-godot`.

How it runs them:
- **Each step is its own `level-factory` process,** with the arguments a
  person would type. That is how the cold driver runs them and how they were
  proven: in one process, state one command leaves behind would reach the
  next.
- **Their output is shown as it comes.**
- **It stops at the first failure and says which step.** A step fails when
  it exits with an error, or, for the shell and art legs, when it does not
  print "blockers open: 0". That is the line the cold driver checks.
- **The flags:**
  - `--seed N` selects that candidate instead of the pick;
  - `--mission` chooses one of a batch's missions;
  - `--no-bake-lights` reaches the export.
- **It refuses a folder that is neither a workspace nor empty.** That stops
  it making a workspace inside the factory's own root.
- **It ends by naming the export and the command that walks it:**
  `level-factory -C <workspace> walk <mission> --play`.

### Tests
`tests/unit/test_make_and_pick.py`, 14. The pick's tests read a workspace
built in a temporary directory:
- the fewest major findings, then completion, then the lowest seed;
- a candidate is out on its walk test or a major route finding;
- when every candidate is out, the fewest major findings is still picked;
- a missing report sorts last and reads as unknown;
- no candidates, or no validation file, refuses;
- `pick` prints the candidate id last.

The make tests answer each step with a stand-in runner, as the real command
prints. It records every command line, so `make` is held to its sequence
without Blender or Godot:
- the steps in the cold driver's order, with the picked candidate approved;
- a new workspace is initialised first;
- `make` stops at the shell leg on an open blocker;
- it stops when the art leg prints no blocker count, and on a failed export;
- `--seed` selects instead of the pick, and `--no-bake-lights` reaches the
  export;
- a busy folder that is not a workspace is refused;
- a batch naming two missions asks which.

On 0.168.0 the file fails to collect, because `packages.pipeline.pick` does
not exist. With only that module added, the five tests on the rule pass and
the nine on `pick` and `make` fail: neither command exists.

**What is not proven here: a level made with `make`.** The stand-in runner
holds the sequence, not the tools. The first real `make` is the install run
from a fresh unpack.

Suite: 2,129 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.168.0 gave
2,113. The 14 tests here account for 14 of the 16. The other two are
`test_sibling_locator`'s guard, which runs once per `.py` in the repo: 312
cases on 0.168.0 and 314 here, one for each new file.
