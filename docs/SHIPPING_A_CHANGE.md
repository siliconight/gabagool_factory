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

## 9. Say what is still unproven

The last paragraph of the report names what was measured, what was inferred,
and what nobody has looked at yet. A residual section is what stops the next
session treating an inference as a measurement.
