#!/usr/bin/env python3
"""Roadmap 51, defect two: plan the cover for the crew spawn that ships.

WHAT IS WRONG, MEASURED

`assemble` seats the mission points and NEVER clears the crew spawn
(`lot.py:1867-1874`), so on the `test_site_cover` fixture `walk_pos["spawn"]`
is (-70.0, 30.0) -- the dead centre of building `b0`, whose footprint spans
x -78.0 .. -62.0. It plans the cover from there (`lot.py:1889-1894`).

`write_walk_scene` re-derives the same points independently and DOES clear the
crew spawn, moving it to (-60.5, 30.0), outside the building. That is the spawn
the scene ships.

So the cover in every shipped level is planned for a crew standing INSIDE a
building. From in there the shell occludes most of the map, which is why
`plan_cover` reported `open_lines=0` -- it believed it had broken every
sightline -- while the shipped scene leaves a fully open 51.9 m lane to
`Enemy_5` and `route_open=13`.

`test_the_cover_that_was_planned_is_in_the_scene_that_gets_shipped` is right to
fail, and it is the check the search cannot perform on itself. Roadmap 51 frames
this defect as "either the search or the check is wrong". Neither is. The search
is correct for the inputs it was handed and the check is correct about the scene
that shipped; the two disagree about where the crew stands.

WHAT THIS CHANGES

One statement: `assemble` clears the crew spawn after seating it, before the
cover is planned. `clear_crew_spawn` returns a NEW dict and leaves its input
alone, so nothing upstream moves. Its findings are reported alongside the
seating findings -- `write_walk_scene` drops them deliberately ("assemble runs
the same call on the same inputs and reports them"), and until now assemble did
not make that call, so a pushed crew spawn was reported by nobody.

The shipped crew spawn does NOT move: `write_walk_scene` already cleared it and
still does, and seat+clear is idempotent (measured on this site, `solids=None`:
the spawn moves 0.000000 m on a second application). What moves is the cover,
onto the lines the crew can actually be shot along.

The enemy positions `assemble` places also come into agreement with the scene's
as a consequence, since both derivations now start from identical inputs. That
is a side effect, not the goal: enemy placement belongs to the gameplay layer
and is not what this pipeline ships. Cover is.

NOT DONE HERE, AND WORTH DECIDING SEPARATELY: `assemble` and
`write_walk_scene` still derive the mission points twice, independently. This
patch makes the two derivations agree; it does not make there be one. Cover
planning is also still coupled to `place_enemies`, which is awkward if enemy
placement is leaving this pipeline.

    lot.py : 101,890 B  sha256 386A5FDF...  (post patch_lot_hook_plan.py)

USAGE

    python patches\\patch_lot_cover_ships_spawn.py --check
    python patches\\patch_lot_cover_ships_spawn.py --selftest
    python patches\\patch_lot_cover_ships_spawn.py
    python patches\\patch_lot_cover_ships_spawn.py --revert
"""
from __future__ import annotations

import hashlib
import math
import shutil
import sys
from pathlib import Path

TAG = "r51covspawn"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "lot.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 101890
EXPECT_SHA = "386A5FDFB33FD124B76DA45FC49CB34729080021FD256B734F9912642DC5313E"


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


PLACE_OLD = '''    # The collision reading read four lines up. It was already going to
    # `seat_destinations`; the enemies are placed against sightlines and had
    # been getting declared footprints instead.
    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos, solids=solids)
'''

PLACE_NEW = '''    # ...and then off the wall, BEFORE anything is planned against where the
    # crew stands. `write_walk_scene` clears the crew spawn and ships the
    # cleared one; this did not, so the cover was planned for a crew standing
    # where the scene does not put it. On the `test_site_cover` fixture that is
    # (-70.0, 30.0), the dead centre of `b0` -- from inside a shell almost every
    # sightline reads as already broken, `plan_cover` returned open_lines=0,
    # and the shipped scene still opened with 51.9 m of clear ground to
    # Enemy_5. `clear_crew_spawn` returns a new dict and leaves its input
    # alone, and seat+clear is idempotent, so the shipped spawn does not move --
    # only what gets planned against it.
    #
    # The findings ARE reported here: `write_walk_scene` drops them on the
    # stated grounds that "assemble runs the same call on the same inputs and
    # reports them", and until this line existed assemble did not make the
    # call, so a pushed crew spawn was reported by nobody.
    walk_pos, clear_findings = site_spawns.clear_crew_spawn(site_spec, walk_pos)
    # The collision reading read four lines up. It was already going to
    # `seat_destinations`; the enemies are placed against sightlines and had
    # been getting declared footprints instead.
    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos, solids=solids)
'''

REPORT_OLD = "    for f_ in seat_findings + spawn_plan.findings + cover_findings:\n"
REPORT_NEW = ("    for f_ in (seat_findings + clear_findings + spawn_plan.findings\n"
              "               + cover_findings):\n")

EDITS = [
    ("assemble clears the crew spawn before planning cover", PLACE_OLD, PLACE_NEW),
    ("the clear findings are reported", REPORT_OLD, REPORT_NEW),
]


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
    print("APPLICABLE: all anchors present exactly once." if ok
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
    print(f"  applied {len(EDITS)} edits")
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


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} bytes (got {len(raw)})")
    ok(_sha(raw) == EXPECT_SHA, "target sha256 matches the read")
    ok(eol == "\n", "lot.py reads as LF")

    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    # ORDER IS THE WHOLE POINT. Clearing after the cover is planned would
    # change nothing that matters, so the position is asserted, not just the
    # presence.
    i_clear = out.index("walk_pos, clear_findings = site_spawns.clear_crew_spawn(")
    i_place = out.index("spawn_plan = site_spawns.place_enemies(site_spec, walk_pos")
    i_cover = out.index('cover_points = {"LT_PlayerSpawn"')
    ok(i_clear < i_place, "the clear happens BEFORE the enemies are placed")
    ok(i_clear < i_cover, "the clear happens BEFORE cover_points is built")
    ok(out.count("walk_pos, clear_findings = site_spawns.clear_crew_spawn(") == 1,
       "exactly one clear is added to assemble")

    # `clear_findings` must be defined before it is read, or this raises at
    # runtime on every assemble.
    ok(out.index("clear_findings = ") < out.index("+ clear_findings"),
       "clear_findings is bound before it is reported")

    # Counted on the CALL, not the bare name: the comment added above mentions
    # `clear_crew_spawn` in prose, so a bare-name count reads 4 -> 6 and means
    # nothing. This is the third time in this item that a bare-name count has
    # been wrong; the call form is the thing being asserted about.
    call = "site_spawns.clear_crew_spawn("
    ok(out.count(call) == text.count(call) + 1,
       f"clear_crew_spawn CALL count grows by exactly one "
       f"({text.count(call)} -> {out.count(call)})")

    try:
        compile(out, str(TARGET), "exec")
        ok(True, "lot.py compiles after the edit")
    except SyntaxError as exc:
        ok(False, f"lot.py compiles after the edit ({exc})")

    # -- the fix is not a no-op on the site that exposed it ----------------
    # Measured against site_spawns directly, so this needs no assemble run:
    # the fixture's crew spawn IS moved by the clear, and planning from the
    # moved one gives the enemy set the scene ships rather than the one the
    # cover was planned against.
    sys.path.insert(0, str(TARGET.parent))
    try:
        import site_spawns as S
        half = 8.0
        spec = {"name": "yard", "ground": {"size_x": 220, "size_y": 140},
                "buildings": [{"id": b, "at": list(p), "rot": 0,
                               "footprint": [half * 2, half * 2]}
                              for b, p in (("b0", (-70.0, 30.0)),
                                           ("b1", (70.0, 30.0)))]}
        seated = {"spawn": (-70.0, 30.0, 0.0), "objective": (70.0, 30.0, 0),
                  "extraction": (-70.0, 30.0, 0.0)}
        cleared, _f = S.clear_crew_spawn(spec, seated)
        moved = math.dist(seated["spawn"][:2], cleared["spawn"][:2])
        ok(moved > 1e-6,
           f"the fixture's crew spawn is actually moved by the clear "
           f"({moved:.3f} m: {seated['spawn'][:2]} -> "
           f"{tuple(round(v, 3) for v in cleared['spawn'][:2])})")
        ok(seated["spawn"] == (-70.0, 30.0, 0.0),
           "clear_crew_spawn left its input alone, as documented")

        before_set = [tuple(round(v, 3) for v in p[:2])
                      for p in S.place_enemies(spec, seated).positions]
        after_set = [tuple(round(v, 3) for v in p[:2])
                     for p in S.place_enemies(spec, cleared).positions]
        ok(before_set != after_set,
           "planning from the cleared spawn gives a different set -- the "
           "divergence this patch removes is real on this fixture")
        # The scene ships the cleared-spawn set; this is that set, verbatim
        # from the probe run.
        shipped = [(-8.332, 43.5), (16.786, 28.5), (55.429, 31.5),
                   (45.929, 31.5), (7.286, 28.5), (-31.357, -13.0)]
        ok(all(math.isclose(a, b, abs_tol=5e-3)
               for p, q in zip(after_set, shipped) for a, b in zip(p, q))
           and len(after_set) == len(shipped),
           "and it is the set the walk scene actually ships")
        # Idempotence, so the claim "the shipped spawn does not move" is
        # measured rather than asserted.
        twice, _f2 = S.clear_crew_spawn(spec, cleared)
        ok(math.dist(cleared["spawn"][:2], twice["spawn"][:2]) < 1e-9,
           "seat+clear is idempotent, so the shipped spawn does not move")
    finally:
        if str(TARGET.parent) in sys.path:
            sys.path.remove(str(TARGET.parent))

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
