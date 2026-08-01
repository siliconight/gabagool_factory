"""CLAUDE.md gains the thing it never stated: what the factory is FOR.

WHY IT MATTERS THAT THIS WAS MISSING. Every rule in the file is a rule about how
to work safely -- ground before patching, measure before concluding, do not let a
null result refute a theory. All good, all second-order. None of them say what
counts as progress, so any careful, well-grounded, well-measured change reads as
progress, including the ones that only make the next patch safer.

That gap produced a concrete error the day this was written. `rockay-ws` was
skipped in a checker on the grounds that it is "evidence, not ours to fix" --
correct outcome, wrong reason, and the wrong reason inverts the value of a whole
class of finding. A defect found in genuinely GENERATED output is a defect in the
generator, which is the most actionable finding available. It only reads as
unactionable if the workspace is mistaken for the product.

The two edits:

  1. A new opening section stating the deliverable and the metric, ahead of
     everything else, because it governs everything else.
  2. `Where fixes land` corrected: rockay-ws is a level to iterate against, not
     evidence to be preserved, and the distinction changes what its contents
     mean.

Asserts every target, refuses on a miss, idempotent. Preserves CRLF -- text-mode
round-trip translates on write, which is how the file kept its endings through
the earlier passes.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CM = ROOT / "CLAUDE.md"

HEAD_OLD = """# Repository conventions

## Attribution"""

HEAD_NEW = """# Repository conventions

## What this is for, and what counts as progress

**The deliverable is the pipeline, not any level it makes.** The end state is
that somebody who has never seen this repo points these tools at their own game
and gets levels out: procedurally generated, working as intended, and good
enough to ship — which means they have to look and feel deliberate, not merely
be traversable.

**The metric is interventions-per-level.** A level the pipeline produced with
nobody touching anything is the product. A level that needed six hand-patches on
the way is six defects wearing a level's clothes, and counting it as a success is
how a toolchain stays permanently one fix away from working. Nobody has measured
this number yet (`PIPELINE_ROADMAP.md` item 17), and until somebody does, no
result in this repo answers the question the repo exists to answer.

Three consequences worth stating, because each has already been got wrong:

- **A fix that does not generalise has not moved the deliverable.** Making one
  workspace's level work is worth doing only for what it teaches about the tool
  that built it. `rockay-ws` is a level to iterate against; it is not the
  product and it is not proof of one.
- **Hardening the process of patching is second-order.** Guardrails, checkers
  and tidy roots make the next intervention safer and cheaper. They do not
  reduce the number of interventions, and it is easy to spend a long stretch
  feeling productive while that number does not move. Before starting a piece of
  work, say which of the two it is.
- **"Works" and "good" are different gates, and only the first exists.** Every
  guardrail here measures traversal correctness — can a body get from A to B.
  None measures whether the result reads as designed rather than generated. Of
  the three problems found by actually playing a generated level, one was caught
  by an instrument and two were caught by a person looking at the screen. That
  gap is a dependency on a human playing every level, and it is tracked as
  roadmap item 18 rather than treated as unavoidable.

A run that is measured, grounded, well-reasoned and does not reduce
interventions-per-level is a good piece of work on the wrong problem. Say so
rather than counting it.

## Attribution"""

FIXES_OLD = """Fixes land in the tool repos — `lot`, `level_factory`, `deli_counter`, and their
siblings — never in a mission workspace. `rockay-ws` is evidence: read it, do not
edit it."""

FIXES_NEW = """Fixes land in the tool repos — `lot`, `level_factory`, `deli_counter`, and their
siblings — never in a mission workspace. `rockay-ws` is a level to iterate
against: read it, do not edit it. Hand-editing it produces a level that works and
a pipeline that still does not, which is the failure mode this whole file exists
to prevent.

**Be exact about what a file under `rockay-ws` actually is, because the answer
changes what a finding there means.** Output the tools GENERATED is the most
valuable thing to check anywhere in the repo — a defect in it is a defect in the
generator, reproducible on the next run. A vendored COPY of a tool addon is
worth nothing to check, because the original is checked at its own repo and a
reader who acts on the copy is patching a file that is not the file. Both live
under `rockay-ws` and they look identical from the path. Its 342 `.gd` files are
copies (`shared/lux`, `shared/patina`, `shared/pixelcoat`, `shared/zoo`, and
`walk_preview_rebuilt/.../addons/lux`); the tools emit `.tscn`, `.glb` and
`.json`, not GDScript. Check which kind before deciding a directory is not worth
looking at — the path is not the answer."""


def main() -> int:
    if not CM.exists():
        raise SystemExit(f"missing {CM}. Nothing written.")
    src = CM.read_text(encoding="utf-8")
    before = len(src)
    if "What this is for, and what counts as progress" in src:
        print("CLAUDE.md: the goal section is already there")
        return 0
    if "## Attribution" not in src:
        raise SystemExit("CLAUDE.md has no Attribution section -- this is not "
                         "the file this patch was written against. NOTHING "
                         "WRITTEN.")
    done = []
    for old, new, label in (
        (HEAD_OLD, HEAD_NEW,
         "CLAUDE.md: the deliverable and the metric, as the opening section"),
        (FIXES_OLD, FIXES_NEW,
         "CLAUDE.md: rockay-ws is a level to iterate against, not evidence"),
    ):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: anchor appears {n} time(s), expected "
                             f"exactly 1. NOTHING WRITTEN.")
        src = src.replace(old, new)
        done.append(label)

    backup = CM.with_suffix(".md.pre_goal")
    if not backup.exists():
        shutil.copy2(CM, backup)
    CM.write_text(src, encoding="utf-8")
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  {before} -> {len(src)} characters; previous file kept at "
          f"{backup.name}")
    print("\n  Nothing executable changed. The file now opens with what the "
          "work is for,\n  ahead of the rules about how to do it safely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
