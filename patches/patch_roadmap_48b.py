r"""Roadmap item 48b -- the mechanism, located, and the finding preserved.

    python patches\patch_roadmap_48b.py --check
    python patches\patch_roadmap_48b.py
    python patches\patch_roadmap_48b.py --selftest
    python patches\patch_roadmap_48b.py --revert

Run from the FACTORY ROOT, AFTER patch_roadmap_48.py. Then:

    python tools\roadmap_status.py --write

WHAT CHANGED SINCE 48 WAS WRITTEN

48 was written from measurements and left the mechanism as a question. The
mechanism is now located, and it is one boolean:

    commands/__init__.py:238   _art_run = any(j.stage_id == "themed_site_assemble"
                                              for j in plan.graph.jobs())
    commands/__init__.py:942   if themed_map or art_run:  -> narrow 123 to 98

`_art_run` is a property of THE INVOCATION'S PLANNED GRAPH, not of the
mission. `batch create` plans no art layer, so it draws from 123; the art run
plans one, so it draws from 98. Same job, same seed, different list.

This matters enough to change 48's shape: question 2 stops being "should we?"
and becomes "make the narrowing depend on the brief instead of on this
invocation." So the item gets a new section and a STATUS that names the line.

NO CODE IS TOUCHED BY THIS PATCH. The one-line condition change re-selects
buildings for every mission carrying `lot_library`, and whether the draw may
move behind `candidate_selected` at all is question 1, which is not mine to
answer.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
FINDING = "docs/findings/ITEM48_THE_DRAW_MOVED.md"
SIDECAR = ".pre_r48b"

OLD_STATUS_TAIL = (
    "The functional lock caught it and refused the export -- this item is "
    "the redraw, not the lock*"
)
NEW_STATUS_TAIL = (
    "The functional lock caught it and refused the export -- this item is "
    "the redraw, not the lock. MECHANISM LOCATED: `commands/__init__.py:238` "
    "computes `_art_run` from THIS INVOCATION'S planned graph, and `:942` "
    "narrows the greybox pool on it -- so `batch create` draws from 123 and "
    "the art run draws from 98, and `pick_lot` is handed a different list "
    "for the same seed. Evidence preserved in "
    "`docs/findings/ITEM48_THE_DRAW_MOVED.md` because `_runs/` is "
    "gitignored*"
)

ANCHOR = "THE SECOND HALF: NOTHING CAN JOIN A GRADE TO A SITE"

INSERT = '''WHERE IT IS, EXACTLY

```python
# commands/__init__.py:238 -- DOES THIS RUN HAVE AN ART LAYER?
_art_run = any(j.stage_id == "themed_site_assemble"
               for j in plan.graph.jobs())

# commands/__init__.py:942, in _write_site_spec -- which pool GREYBOX draws from
if themed_map or art_run:
    complete = building_library.require_themed_shells(complete, count)
lot = building_library.pick_lot(complete, seed, count)
```

`_art_run` is read off **the graph planned by this invocation**. It is not a
property of the mission, the brief, or the candidate:

```
batch create                    plans no themed_site_assemble   123 -> cr_garage
run --art --unlit --gameplay    plans one                        98 -> landmark_hall_a03
```

**And this was a deliberate change, made for a good reason, that moved the
defect instead of closing it.** The comment above line 942 records that the
narrowing was extended to the greybox branch because
`probe_pool_divergence.py` had measured, on `lot_demo_001`, that 14 of 15
building slots already carried an archetype other than the one Laser Tag
graded, and 13 graded archetypes never shipped at all. The stated goal --
"grade the pool that ships" -- is right.

It made the greybox pass and the themed pass agree WITHIN one invocation. It
could not make them agree ACROSS invocations, because `batch create` plans no
art layer, and `batch create` is where the graders, the structural checks and
the functional lock all run. The divergence moved from inside a run to
between the run that grades and the run that ships, where the lock is the
only thing standing.

`building_library.lot_for()` is NOT this path -- it returns `[], []` below
`building_count < 2` and this brief asked for one building -- but its own
comment carries the same warning from the other side: *"a narrower pool
re-selects every lot already built and graded."* Two selectors, one hazard,
written down twice, and neither writing-down was a check.

**So question 2 below is no longer "should we?" but "keyed on what?"** The
narrowing wants to depend on something true of the MISSION for its whole
life. `lot_library` on the brief is the obvious candidate: it is already what
gates the art layer, it is set before `batch create` runs, and a mission
without it never reaches this branch at all, so existing single-shell
missions stay byte-for-byte. That is a one-line change and it is deliberately
NOT made yet, because it re-selects buildings for every mission carrying
`lot_library` and question 1 outranks it.

**The evidence is preserved.** `.gitignore:20` ignores `_runs/`, and
`fingerprint.last.json` has already overwritten the first graybox assemble.
`docs/findings/ITEM48_THE_DRAW_MOVED.md` carries the run log, both site
specs' counts, all five fingerprints verbatim, and a sha256 for every file
quoted -- so this item survives the workspace being deleted.

'''

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor. See patch_roadmap_48.py."""
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    if _as("**48. The same job and the same seed draw", eol) not in body:
        print("REFUSING: item 48 is not in the file -- run "
              "patches\\patch_roadmap_48.py first")
        return 1

    out = body
    already = 0

    # -- edit 1: the STATUS line names the mechanism ---------------------
    o, n = _as(OLD_STATUS_TAIL, eol), _as(NEW_STATUS_TAIL, eol)
    if n in out:
        already += 1
    elif out.count(o) == 1:
        out = out.replace(o, n, 1)
    else:
        print(f"REFUSING: item 48's STATUS tail occurs {out.count(o)} "
              f"time(s), expected 1")
        return 1

    # -- edit 2: the new section, above THE SECOND HALF ------------------
    anchor = _as(ANCHOR, eol)
    if _as("WHERE IT IS, EXACTLY", eol) in out:
        already += 1
    elif out.count(anchor) == 1:
        out = out.replace(anchor, _as(INSERT + ANCHOR, eol), 1)
    else:
        print(f"REFUSING: the item 48 second-half heading occurs "
              f"{out.count(anchor)} time(s), expected 1")
        return 1

    if already == 2:
        print(f"  already applied  {ROADMAP}")
        return 0
    if already == 1:
        print("REFUSING: exactly one of the two edits is present -- the file "
              "is half-patched. Revert or fix by hand.")
        return 1

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        if not (root / FINDING).is_file():
            print(f"  NOTE: {FINDING} is not here yet -- the STATUS line "
                  f"will point at a file that does not exist")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    disk = (root / ROADMAP).read_bytes().decode("utf-8")
    check("the file's line endings are preserved",
          disk.count(_CRLF) > 0 or "\r" not in disk)
    md = disk.replace(_CRLF, "\n")

    marker = "**48. The same job and the same seed draw"
    check("item 48 is present", marker in md)
    if marker not in md:
        print(f"\n  {bad} FAILURE(S) -- run patch_roadmap_48.py first")
        return 1
    i48 = md.index(marker)
    s48 = md[:i48].rstrip().splitlines()[-1]
    body = md[i48:md.index("### Not to be worked on", i48)]
    bflat = " ".join(body.split())

    check("the STATUS line names the mechanism",
          "MECHANISM LOCATED" in s48 and "commands/__init__.py:238" in s48
          and "`:942`" in s48)
    check("...and the numbers that make it concrete",
          "draws from 123" in s48 and "draws from 98" in s48)
    check("...and points at the preserved evidence",
          "docs/findings/ITEM48_THE_DRAW_MOVED.md" in s48)

    check("the new section is in item 48, not after it",
          "WHERE IT IS, EXACTLY" in body)
    check("it quotes both lines of code",
          '_art_run = any(j.stage_id == "themed_site_assemble"' in body
          and "if themed_map or art_run:" in body)
    check("it says _art_run is per-invocation, not per-mission",
          "the graph planned by this invocation" in bflat
          and "not a property of the mission" in bflat)
    check("it credits the change that moved the defect",
          "probe_pool_divergence.py" in body and "14 of 15" in body
          and "13 graded archetypes never shipped" in bflat)
    check("...and says the goal of that change was RIGHT",
          "grade the pool that ships" in bflat and "is right" in bflat)
    # WITH the backticks. Written without them this passed nothing and failed
    # loudly on prose that was already correct -- the check was typed from
    # intent, the file has `batch create` in code voice.
    check("it explains why batch create is the other side",
          "because `batch create` plans no art layer" in bflat
          and "the run that grades and the run that ships" in bflat)
    check("it distinguishes lot_for from this path",
          "lot_for()` is NOT this path" in bflat
          and "building_count < 2" in body)
    check("it reframes question 2 rather than answering question 1",
          "no longer \"should we?\" but \"keyed on what?\"" in bflat
          and "question 1 outranks it" in bflat)
    check("it says explicitly that no code is changed yet",
          "deliberately\nNOT made yet" in body or "NOT made yet" in bflat)
    check("it records why the evidence had to be copied",
          ".gitignore:20" in body and "ignores `_runs/`" in bflat)

    check("the new section sits ABOVE the joinability half",
          body.index("WHERE IT IS, EXACTLY") < body.index(ANCHOR))
    check("every fenced block in item 48 is still closed",
          body.count("```") % 2 == 0)
    check("the four questions survived the insert",
          "1. **May the draw narrow" in body
          and "4. **What does a fingerprint have to carry" in body)

    f = root / FINDING
    check(f"{FINDING} exists", f.is_file())
    if f.is_file():
        ft = f.read_bytes().decode("utf-8").replace(_CRLF, "\n")
        check("...and its fences are balanced", ft.count("```") % 2 == 0)
        check("...and it carries all five fingerprints",
              ft.count('"adapter_version"') >= 5)
        check("...and a sha256 for every file it quotes",
              ft.count("| `_runs/3b/") == 8)
        check("...and the run log lines the item cites",
              "run.log" in ft and "lux_fixture_gate" in ft)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  the mechanism is one boolean, and it is written down"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {ROADMAP}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {ROADMAP}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_roadmap_48b.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
