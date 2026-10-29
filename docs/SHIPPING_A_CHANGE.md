# Shipping a change to a tool repo

The sequence every change in this repo follows. It was reconstructed by
imitation for months and written down after the fourth time somebody rebuilt it
from scratch. Nothing here overrides `CLAUDE.md`; this is the mechanical
order, and `CLAUDE.md` is the judgment.

**Before anything: is a cold run in flight?** If one is, stop. The run hashes
the ten tool repos at `--begin`, and a mid-flight edit is an intervention
whether or not anybody writes it down — it voids the zero. Cold run 9037
counted seven that way. The factory root (`CLAUDE.md`, `docs/`,
`PIPELINE_ROADMAP.md`) is outside the hashed set and is safe.

---

## 1. Say which problem this is

`CLAUDE.md` opens by asking for this, and it is the step most often skipped.
Before starting, say whether the work reduces **interventions-per-level** or
merely makes the next intervention cheaper. Both are worth doing; only one moves
the deliverable, and a run that is measured, grounded and well-reasoned can
still be a good piece of work on the wrong problem.

## 2. Ground it

Read the files the change will touch, **in this session**, and say so out loud
in the first reply — what was read and what the byte counts said. A compaction
summary is a lossy recollection of source, not source. Re-read the signature and
adjacent comments of anything you are about to call, in the turn you call it,
including helpers you wrote yesterday.

## 3. Write an anchored patch script, not an inline edit

Under `patches/` or the session scratchpad. It must:

- assert every anchor matches **exactly once** and refuse to write on a miss;
- check line endings deliberately (`b"\r\n" in data`), because these files are
  a mix and a wrong guess writes bare LF into a CRLF document;
- stage every file and write nothing until every anchor in every file matched,
  so a half-applied multi-file change is impossible;
- record the exact before-and-after text, so a poisoned file can be rebuilt from
  the nearest clean ancestor plus the patches that followed it.

## 4. Write the test that fails without the change

Then **prove it fails**, by stashing the change and running it:

```bash
git stash push -q -- <the changed files>
python -m pytest <the new test file> -q
git stash pop -q
```

Say how many failed and which. A check that cannot fail is indistinguishable
from one that passed. Read one real instance of any artefact before writing the
code that reads it, and make an unrecognised shape FAIL rather than pass.

## 5. Run the suite, and read the summary honestly

`docs/COMMANDS.md` has the per-repo command and the trap in level_factory's
(its conftest suppresses the pass/fail line). Quote the real number.

**SMOKE FIRST, SUITE ONCE (the walker's yes, 2026-10-28).** Measured that day,
a change spent most of its wall clock re-proving itself: Zoo's suite on the
clone (8 min) and again on the real repo (7.7 min); Deli Counter's build, nav
gate and suite on the clone, again on the real repo, and a third time in its
commit hook (6.9 min). And the defects that cost most were found at the end of
the chain -- a money rack built in wood (the level's frames), a designer's
level name refused by a guard (14 s into the first real build).

- **Smoke the change in a clone before any long suite**: make the smallest level
  that exercises it (`tools/ship_change.py smoke`). A defect a build can show
  costs seconds there and a suite cycle anywhere later.
- **Run the full suite ONCE, on the clone.** The patch's dry run proves the
  applied repo byte-identical to that clone, so a real-repo suite re-proves
  nothing; run one after the apply only when the apply wrote something the clone
  did not (build output, a migration run against the real specs). A repo's own
  commit hook is NOT skipped: it is the repo's gate, and `--no-verify` stays
  forbidden.
- **Light jobs may overlap; heavy ones may not.** Two unit suites can run side
  by side. A walk, a price or a level build has the machine to itself -- the
  rule from the bank's walk that timed out under load.

**BATCH THE LOOKS (the walker's yes, 2026-10-28).** A level build to shoot and
price a visual change -- make, walk, frames, three price arms -- is 30-40 minutes
and runs alone; on 2026-10-28 three bank steps took three of them. Ship related
visual changes to their tool repos one by one, then build, shoot and price the
level ONCE for the batch. The price's draws and frame time are per station, so
a batch that prices badly is split by building its halves, not guessed at.
Two guards keep it from costing the product:
- **No release or package while a batch is unpriced.** CLAUDE.md's rule is
  "price a look before shipping it"; the tool repos may run ahead of the price,
  a release may not, because a release is what reaches a player's machine.
- **Each change still gets its cheap look before it ships to its repo** -- a Zoo
  specimen render, an in-memory measure of what a Deli Counter rule places. The
  wooden money rack was caught in a level frame and fixed before the rows were
  built on it; batched without a per-change look, the rows would have been built
  on wood. Only the 30-40 minute level build is batched.
A batch prices what a player gets -- several looks each under the noise floor
can sum past it, which per-change prices never see.

**A PRICE ENDS IN A VERDICT AND ITS ACTION (the walker, 2026-10-28: "clear
actions should be taken from the pricing that becomes standardized").**
`python tools/price_verdict.py --dir <finding> --prefix <perf_x_>` reads the
three arms and prints PASS, WATCH or FAIL with the one action each prescribes:
PASS releases; WATCH releases and names the headings whose frames get looked
at; FAIL blocks the release and splits the batch until one change owns the
cost, which is then made cheaper or reverted. Its thresholds are chosen and
written in its docstring; every rule was shown to fire on a synthetic subject
before it was trusted. It names headings and numbers, never a cause.
`python tools/price_batch.py --control <ws> --subject <ws> --mission <id> --out
<finding> --prefix <perf_x_>` runs the three arms and ends in that verdict. It
imports the control once (import was 60% of a price, timed on 2026-10-28), and
a floor past 1.0 ms is itself a WATCH: a wide floor would let a real cost pass.

`tools/ship_change.py` carries these steps -- clone, smoke, generate, dry run,
prove on the old version, apply, commit, push, and the release checks (a tool's
HEAD at its tag, nothing stale, `factory_index` written before the commit).

**A repo whose commit hook runs more than its suite is gated on the clone.**
Deli Counter's hook runs `check.py`: spec validation, the content audit,
`layout_lint`, the stair sweep, build freshness, the nav gate and the catalog.
The first apply of Deli Counter 0.290.0 passed the clone's suite and nav gate
and was then refused at commit by `layout_lint`'s L22 -- a new vault door's
leaf swung across a stair -- one rebuild and one hook run late.
`ship_change.py gate <repo> <clone>` runs that gate on the clone (for Deli
Counter: rebuild, refresh the catalog, `check.py`), names the failing steps,
and stamps the clone with a hash of its exact changes; `patch` refuses a gated
repo's clone whose stamp does not match. `check.py`'s children print to the
console, not to a captured pipe, so on a failure `gate` re-runs the cheap steps
one at a time to say which.

## 6. Version and changelog

- Bump `VERSION`. Patch for a fix, minor for a capability.
- Add a `## [x.y.z] - <a title that says what changed>` entry at the TOP of
  `CHANGELOG.md`, in the house voice: bold capitalised lead-ins, figures rather
  than adjectives, file paths with line numbers, and **the measurement that
  motivated the change**. Say what it invalidates before it happens, and say
  plainly which numbers were chosen rather than derived.
- Keep refutations. A claim that turned out wrong is recorded above the finding
  that replaced it; it is cheaper to keep than to rediscover.
- Some repos carry a second version source — check for a test that pins them
  together before assuming one file is enough.

## 7. Commit and push

Plain messages. **No `Co-Authored-By`, no "Generated with", no assistant
first-person narration in code comments** — `CLAUDE.md` makes this a hard rule
that overrides any default tooling instruction, in every repo under this
workspace.

The message carries the same content as the changelog entry, compressed: what
changed, the measurement, what it invalidates, and what remains unproven.

```bash
cd <repo> && git add -A && git commit -q -F - <<'EOF'
...
EOF
git log --oneline -1 && git push -q origin main; git log --oneline origin/main -1
```

**Read `git log` to confirm the commit landed.** A wrapper's exit code has
reported success for a commit that failed.

## 8. Record it where the next person will look

- The roadmap item this belongs to: status block and body, then
  `python tools/roadmap_status.py --write` and `--check`. Diff against a
  pre-patch copy and account for every changed region.
- If it closes something a proposal asked for, write the result into the
  proposal **above the sentence it refutes**, not only into the changelog.
- If you found something real and out of scope, say so plainly rather than
  widening the change.
- The record shipped with the work: `python tools/factory_hygiene.py --check`
  is clean -- nothing untracked under `docs/` or `patches/`, nothing loose at
  the root, every generated index matching its folder (`docs/FILING.md`).
  After adding to an indexed folder, `python tools/factory_index.py --write`.

## 9. Say what is still unproven

The last paragraph of the report names what was measured, what was inferred,
and what nobody has looked at yet. A residual section is what stops the next
session treating an inference as a measurement.
