#!/usr/bin/env python3
"""Roadmap 51, defect two: serve the crew's sightlines before the rest.

WHAT IS WRONG, MEASURED

`plan_cover`'s opening pass takes lines from `open_sightlines`, which returns
every marker pair over `opening_range`, LONGEST FIRST. On the `test_site_cover`
yard that ordering spent the entire 12-piece opening budget without placing one
piece on a line the crew stands on:

    Cover_0  Extraction -> Objective     Cover_6   Enemy_0 -> Extraction
    Cover_1  Enemy_5 -> Objective        Cover_7   Enemy_4 -> Objective
    Cover_2  Enemy_2 -> Enemy_5   <--    Cover_8   Enemy_0 -> Enemy_5   <--
    Cover_3  Enemy_3 -> Enemy_5   <--    Cover_9   Enemy_5 -> Extraction
    Cover_4  Enemy_0 -> Objective        Cover_10  Enemy_4 -> Enemy_5   <--
    Cover_5  Enemy_1 -> Enemy_5   <--    Cover_11  Enemy_0 -> Enemy_3   <--

Zero of the twelve involve `LT_PlayerSpawn`. SIX break enemy-to-enemy
sightlines -- cover so one enemy cannot see another, which describes nothing
about who opens fire on the crew, since they are the same team. The crew had
seven open lines (130.5, 115.9, 106.4, 77.3, 67.8, 53.9, 51.9 m) and got
nothing, and the shipped scene left a clear 51.9 m lane from the crew spawn to
the nearest enemy. `unbreakable` was 0, so a placeable spot existed the whole
time; the budget was simply spent elsewhere.

THE HEURISTIC IS NOT WRONG, ITS SCOPE WAS. "Longest first: the worst line on a
site is usually the one whose fix also shortens three others" is sound, and is
KEPT -- inside each group, by sorting stably on a single boolean so the existing
order survives untouched. What changes is that lines the crew stands on are
served first. `open_sightlines`' own docstring calls what it returns "the set of
lines along which somebody can fire the moment the run starts"; the opening
engagement is about who can fire on the CREW.

MEASURED, same fixture, same 12-piece budget:

                        opening pieces  touching crew  total  open_lines  test
    longest first                   12              0     23           1  FAILS
    crew lines first                12              3     23           0  PASSES

Three pieces close all seven crew lines -- the "one fix shortens three others"
reasoning working, now pointed at the lines that matter. No budget increase, no
change to what counts as a sightline, and `test_site_cover` passes WITHOUT
being modified.

NOT DONE HERE. Enemy-to-enemy pairs are still enumerated and can still consume
budget after the crew is served; excluding them outright measured at 7 opening
pieces and 18 total (fewer pieces, same zero open lines) and is a separate
decision about what `open_sightlines` should return at all.

    lot/site_cover.py : 38,819 B  sha256 46138A10...

USAGE

    python patches\\patch_lot_cover_crew_first.py --check
    python patches\\patch_lot_cover_crew_first.py --selftest
    python patches\\patch_lot_cover_crew_first.py
    python patches\\patch_lot_cover_crew_first.py --revert
"""
from __future__ import annotations

import hashlib
import math
import shutil
import sys
from pathlib import Path

TAG = "r51crewfirst"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "site_cover.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 38819
EXPECT_SHA = "46138A10AD21FE64FEED28A4C77024FA8180EFB14A26073AA3FB9845D1A11F79"


def _eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings.")
    return "\r\n" if crlf else "\n"


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


OLD = '''    def outstanding():
        return [line for line in open_sightlines(points, measured, limit=opening_range)
                if (line[0], line[1]) not in refused]
'''

NEW = '''    def outstanding():
        lines = [line for line in open_sightlines(points, measured,
                                                  limit=opening_range)
                 if (line[0], line[1]) not in refused]
        # THE CREW'S LINES FIRST. `open_sightlines` returns longest first, on
        # the reasoning that the worst line's fix usually shortens three
        # others -- which is sound and is kept, INSIDE each group, because
        # sorting stably on one boolean leaves the existing order alone.
        #
        # Longest-first ALONE spent this site's whole 12-piece opening budget
        # without placing one piece on a line the crew stands on. Measured on
        # the `test_site_cover` yard: 12 pieces, 0 involving the crew, 6 of
        # them breaking enemy-to-enemy lines -- cover so one enemy cannot see
        # another, which says nothing about who opens fire on the crew -- and
        # the shipped scene left a clear 51.9 m lane from the crew spawn to
        # the nearest enemy. `unbreakable` was 0 the whole time, so a spot
        # existed and the budget had simply gone elsewhere.
        #
        # The opening engagement is who can shoot the CREW at t=0. With the
        # same budget, three pieces now close all seven of its lines.
        return sorted(lines, key=lambda line: crew not in (line[0], line[1]))
'''

EDITS = [("plan_cover: crew sightlines are served first", OLD, NEW)]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    got = _sha(raw)
    print(f"  {TARGET.relative_to(ROOT)}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {got}{'' if got == EXPECT_SHA else '   <-- differs'}")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    ok = True
    for name, old, _new in EDITS:
        n = text.count(_n(old))
        print(f"  [{'ok' if n == 1 else 'MISSING'}]  {name}  (found {n})")
        ok = ok and n == 1
    print()
    print("APPLICABLE: anchor present exactly once." if ok
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if ok else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    for name, old, _new in EDITS:
        if text.count(_n(old)) != 1:
            raise SystemExit(f"REFUSING: anchor for {name} not present exactly "
                             f"once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  applied {len(EDITS)} edit")
    print(f"  sidecar : {SIDECAR.name}")
    print(f"  bytes   : {len(raw)} -> {len(data)}  ({len(data) - len(raw):+d})")
    print(f"  sha256  : {_sha(data)}")
    print()
    print("  NEXT: cd lot; python -m pytest tests -q")
    print("        python tools\\probe_r51_cover_enemies.py")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} bytes, sha256 {_sha(after)}")
    return 0


#: The fixture's cover_points, verbatim from the probe run against the shipped
#: pipeline. Carried rather than recomputed so the selftest measures the same
#: arrangement the defect was found on.
POINTS = {"Enemy_0": (-8.332, 43.5), "Enemy_1": (16.786, 28.5),
          "Enemy_2": (55.429, 31.5), "Enemy_3": (45.929, 31.5),
          "Enemy_4": (7.286, 28.5), "Enemy_5": (-31.357, -13.0),
          "LT_ExtractionPoint": (-70.0, 30.0), "LT_ObjectivePoint": (70.0, 30.0),
          "LT_PlayerSpawn": (-60.5, 30.0)}
_H = 8.0
RECTS = [(-70 - _H, 30 - _H, -70 + _H, 30 + _H),
         (70 - _H, 30 - _H, 70 + _H, 30 + _H)]
GROUND = (-110.0, -70.0, 110.0, 70.0)


def _run(module):
    """Plan cover with `module` and report what it did, in one dict."""
    plan = module.plan_cover(
        POINTS, RECTS, GROUND, opening_range=45.0,
        route=[POINTS["LT_PlayerSpawn"], POINTS["LT_ObjectivePoint"],
               POINTS["LT_ExtractionPoint"]])
    opening = [c for c in plan.cover if c.breaks
               and not c.breaks.startswith("route@")]
    solids = RECTS + [c.rect for c in plan.cover]
    crew = POINTS["LT_PlayerSpawn"]
    exposed = [n for n, p in POINTS.items()
               if n.startswith("Enemy_")
               and not module.open_span(crew, p, solids)
               < math.dist(crew, p) - 1e-6]
    return {"opening": len(opening),
            "crew_pieces": sum(1 for c in opening
                               if module.CREW_MARKER in c.breaks),
            "total": len(plan.cover),
            "open_lines": len(plan.open_lines),
            "unbreakable": len(plan.unbreakable),
            "exposed": exposed}


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} bytes (got {len(raw)})")
    ok(_sha(raw) == EXPECT_SHA, "target sha256 matches the read")
    ok(eol == "\n", "site_cover.py reads as LF")
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edit changes the file")

    # `crew` must be in scope inside the closure or this raises on every call.
    ok("crew: str = CREW_MARKER" in out,
       "plan_cover still takes `crew`, which the new sort closes over")
    ok(out.count("sorted(lines, key=lambda line: crew not in") == 1,
       "exactly one crew-first sort is added")

    try:
        compile(out, str(TARGET), "exec")
        ok(True, "site_cover.py compiles after the edit")
    except SyntaxError as exc:
        ok(False, f"site_cover.py compiles after the edit ({exc})")

    # -- BOTH versions are executed and compared. The claim is behavioural,
    # -- so reading the diff proves nothing on its own.
    import importlib.util
    lot_dir = str(TARGET.parent)
    if lot_dir not in sys.path:
        sys.path.insert(0, lot_dir)
    saved = sys.modules.pop("site_cover", None)

    def _mod(name, source):
        spec = importlib.util.spec_from_loader(name, loader=None)
        m = importlib.util.module_from_spec(spec)
        m.__file__ = str(TARGET)
        sys.modules[name] = m
        exec(compile(source, str(TARGET), "exec"), m.__dict__)
        return m

    try:
        before = _run(_mod("_r51_cov_old", text))
        after = _run(_mod("_r51_cov_new", out))
        print(f"        before: {before}")
        print(f"        after : {after}")

        ok(before["crew_pieces"] == 0,
           f"before: the opening budget touched NO crew line "
           f"({before['crew_pieces']} of {before['opening']})")
        ok(after["crew_pieces"] > 0,
           f"after: the crew's lines are served "
           f"({after['crew_pieces']} of {after['opening']})")
        ok(before["exposed"] and not after["exposed"],
           f"before left {before['exposed']} exposed to the crew spawn; "
           f"after leaves none")
        ok(after["open_lines"] == 0 and before["open_lines"] > 0,
           f"open_lines {before['open_lines']} -> {after['open_lines']}")
        ok(after["opening"] == before["opening"],
           f"the opening budget is UNCHANGED ({before['opening']} pieces) -- "
           f"this reorders, it does not spend more")
        ok(after["unbreakable"] == before["unbreakable"] == 0,
           "no line became unbreakable")
        # The heuristic inside each group must survive: the very first line
        # taken should still be the LONGEST of the crew's, not just any.
        import importlib
        newmod = sys.modules["_r51_cov_new"]
        lines = newmod.open_sightlines(POINTS, RECTS, limit=45.0)
        first = sorted(lines, key=lambda l: newmod.CREW_MARKER not in (l[0], l[1]))[0]
        crew_lines = [l for l in lines if newmod.CREW_MARKER in (l[0], l[1])]
        ok(first[4] == max(l[4] for l in crew_lines),
           f"longest-first survives inside the crew group "
           f"(first taken is {first[4]:.2f} m, longest crew line is "
           f"{max(l[4] for l in crew_lines):.2f} m)")
        ok(len(lines) == len(sorted(lines, key=lambda l: 0)),
           "the sort drops no lines")
    finally:
        for k in ("_r51_cov_old", "_r51_cov_new"):
            sys.modules.pop(k, None)
        if saved is not None:
            sys.modules["site_cover"] = saved

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
