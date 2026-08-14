r"""Grade the pool that ships. Addendum item J, measured before it was moved.

    python patch_lf_grade_what_ships.py --check
    python patch_lf_grade_what_ships.py
    python patch_lf_grade_what_ships.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

`require_themed_shells` narrowed 123 -> 97 on the THEMED path only, so an
`--art` run graded a draw from 123 and shipped a draw from 97. Measured
2026-08-12 by `probe_pool_divergence.py` on lot_demo_001's three candidates:

    seed 5017   0/5 slots hold their archetype
    seed 5118   1/5
    seed 5219   0/5
    -----------------------------------------------
    15 slots: 13 graded archetypes never ship,
              14 slots hold something other than what was graded

ONE building in the whole mission -- `supermarket_a01` on seed 5118 -- is both
graded and shipped in the same slot. `seed_5219` was selected over `seed_5118`
on 60% route completion against 0%, and the two draws share one building.

THE ARGUMENT THIS OVERTURNS, in its own words, from the comment it replaces:

    NOT applied to the greybox branch. That places levels already built and
    graded, and re-selecting them would be different levels wearing the same
    grades.

That protects the stability of a grade. The measurement shows the grade was
never about the deliverable: 14 slots of 15 already carry something other than
what was graded, so the stability being preserved is the stability of a number
describing a level nobody ships. Correct on the day it was written, and the
thing it feared has already happened.

THE RULE, and it is one sentence: grade the pool that ships. Which pool ships
depends on the run -- with an art layer the themed pool is the deliverable, so
the greybox draw narrows to it too; without one the greybox IS the deliverable
and today's behaviour is already right.

DERIVED, NOT DECLARED. Whether a run has an art layer is read off the planned
graph -- `themed_site_assemble` is present or it is not -- rather than threaded
down as a new flag. `_job_specs_for_plan` already holds `plan`. A parameter
somebody has to remember to pass is the shape of defect this file keeps
finding one layer down.

WHAT IT COSTS, stated plainly because it is not free: every recorded Laser Tag
grade becomes historical. 45, 48, the 60% route completion, the plateau finding
in SESSION_0811 -- all describe draws this code will no longer produce. That is
the trade: a set of numbers you have, for a set of numbers about the right
thing.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_gradeships"


OLD_SIG = '''def _write_site_spec(ws: Workspace, model: MissionBrief, deli_out: Path,
                     *, seed: int, themed_scene: str | None = None) -> Path:'''

NEW_SIG = '''def _write_site_spec(ws: Workspace, model: MissionBrief, deli_out: Path,
                     *, seed: int, themed_scene: str | None = None,
                     art_run: bool = False) -> Path:'''


OLD_NARROW = '''        if themed_map:
            # The themed pool is narrower, and it must be the SAME narrowing
            # `_lot_for_compose` applied: compose published one scene per
            # archetype and `themed_map` is keyed on those ids. A wider pool
            # here selects buildings that have no composed scene, `_source`
            # finds no match, and the row stands as greybox with every stage
            # reporting success -- the defect this file keeps finding, one
            # layer down.
            #
            # NOT applied to the greybox branch. That places levels already
            # built and graded, and re-selecting them would be different
            # levels wearing the same grades.
            before = len(complete)
            complete = building_library.require_themed_shells(complete, count)
            print(f"[site] themed lot: {len(complete)} of {before} shell(s) "
                  f"can carry a theme")'''

NEW_NARROW = '''        if themed_map or art_run:
            # The themed pool is narrower, and it must be the SAME narrowing
            # `_lot_for_compose` applied: compose published one scene per
            # archetype and `themed_map` is keyed on those ids. A wider pool
            # here selects buildings that have no composed scene, `_source`
            # finds no match, and the row stands as greybox with every stage
            # reporting success -- the defect this file keeps finding, one
            # layer down.
            #
            # NOW APPLIED TO THE GREYBOX BRANCH TOO, when the run has an art
            # layer. The comment that used to sit here said the opposite:
            # "NOT applied to the greybox branch. That places levels already
            # built and graded, and re-selecting them would be different levels
            # wearing the same grades." That protected the STABILITY of a
            # grade, and `probe_pool_divergence.py` measured what it was
            # stabilising -- across lot_demo_001's three candidates, 14 of 15
            # building slots already carried an archetype other than the one
            # Laser Tag graded, and 13 graded archetypes never shipped at all.
            # One slot in the mission agreed. The thing that comment feared had
            # already happened; keeping the wider draw preserved the
            # consistency of a number about a level nobody receives.
            #
            # So: grade the pool that ships. With an art layer the themed pool
            # is the deliverable, so the greybox pass draws from it as well.
            # Without one the greybox IS the deliverable and this does not
            # fire -- `art_run` is false and nothing changes.
            before = len(complete)
            complete = building_library.require_themed_shells(complete, count)
            which = "themed lot" if themed_map else "graded lot (art run)"
            print(f"[site] {which}: {len(complete)} of {before} shell(s) "
                  f"can carry a theme -- the graded draw and the shipped draw "
                  f"come from the same pool")'''


OLD_CALL = '''            site_spec = _write_site_spec(
                ws, model, deli_out, seed=seed, themed_scene=themed_scene)'''

NEW_CALL = '''            site_spec = _write_site_spec(
                ws, model, deli_out, seed=seed, themed_scene=themed_scene,
                art_run=_art_run)'''


OLD_HDR = '''    """Map each planned job to the adapter job spec it needs to run."""
    specs: dict[str, dict] = {}
    jobs_dir = ws.jobs_dir'''

NEW_HDR = '''    """Map each planned job to the adapter job spec it needs to run."""
    specs: dict[str, dict] = {}
    jobs_dir = ws.jobs_dir

    # DOES THIS RUN HAVE AN ART LAYER? Read off the planned graph rather than
    # threaded down as a flag: `themed_site_assemble` is planned or it is not,
    # and a parameter somebody has to remember to pass is the shape of defect
    # this file keeps finding. It decides which pool the GREYBOX pass draws
    # from -- see the narrowing in `_write_site_spec`, and addendum item J.
    _art_run = any(j.stage_id == "themed_site_assemble"
                   for j in plan.graph.jobs())'''


EDITS = {COMMANDS: ((OLD_HDR, NEW_HDR), (OLD_CALL, NEW_CALL),
                    (OLD_SIG, NEW_SIG), (OLD_NARROW, NEW_NARROW))}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
    # `_art_run` must be bound before it is used, or a graybox run dies on a
    # NameError in the one code path that never exercises the art layer.
    if out.index("_art_run = any(") > out.index("art_run=_art_run"):
        print(f"REFUSING: {path.name} -- `_art_run` is used before it is bound.")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        print(f"  _art_run bound before use")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    print(f"  NOTE: every recorded Laser Tag grade now describes a draw this "
          f"code no longer produces")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
