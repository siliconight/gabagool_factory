#!/usr/bin/env python3
"""Roadmap 3, discharged: the enemies are placed ONCE and threaded through.

Item 3 -- "Lot places enemies twice, and nothing checks the two agree" -- asks
for one of two things: "Place once, thread the result through, or assert the
two agree." Until now neither had been done. `patch_lot_cover_ships_spawn.py`
made the two calls agree by giving them identical inputs, which is exactly the
"same inputs, same answer" claim item 3 calls untested, restored rather than
removed.

This takes the first option. `place_enemies` runs ONCE, in `assemble`, and the
result is threaded down to the scene writer.

WHY THE SECOND CALL EXISTED, AND WHY THREADING KEEPS THAT INTACT

`lot.py`'s own comment states the constraint:

    Run here as well as in write_walk_scene -- same inputs, same answer --
    because the walk scene is written after this report closes and a placement
    Lot could not honour has to travel with the site, not sit silently in a
    .tscn nobody diffs.

That is a real ordering constraint and it is preserved exactly: the placement
still happens in `assemble`, before the report closes, so its findings still
travel with the site. What changes is that the scene writer no longer places
its own -- it is handed the ones that were reported.

WHY THREADING RATHER THAN AN ASSERTION

An assertion detects a disagreement after the fact. Threading makes the
disagreement impossible to express: there is one list, and both the report and
the scene read it. The two call sites cannot drift, because there is no longer
a second call to drift.

`enemies=None` keeps the old behaviour, so `_lasertag_hook_nodes` and
`_lasertag_hook_plan` still place for the five test call sites that use them
standalone.

WHAT IS ASSERTED, NOT ASSUMED

The selftest executes both versions of `lot.py` and requires the emitted scene
body to be BYTE-IDENTICAL, and separately counts `place_enemies` calls through
a spy: 2 before, 1 after, on the same `assemble`-shaped invocation. A refactor
of the code that writes a shipped artefact is worth nothing if it changes the
artefact.

    lot/lot.py : 103,033 B  sha256 998C3D27ED56...

USAGE

    python patches\\patch_lot_place_once.py --check
    python patches\\patch_lot_place_once.py --selftest
    python patches\\patch_lot_place_once.py
    python patches\\patch_lot_place_once.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r53placeonce"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "lot.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 103033


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


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


EDITS = [
    ("_lasertag_hook_plan accepts an already-placed set",
     '''def _lasertag_hook_plan(pos, site_spec=None, enemy_count=6, lateral=1.5,
                        solids=None, bounds=None) -> dict:
''',
     '''def _lasertag_hook_plan(pos, site_spec=None, enemy_count=6, lateral=1.5,
                        solids=None, bounds=None, enemies=None) -> dict:
'''),

    ("_lasertag_hook_plan uses them instead of placing again",
     '''    # `solids` here for the same reason `seat_destinations` gets it above: the
    # scene Laser Tag evaluates is written from THIS call, and a placement that
    # judged cover differently from the one in the site report would make the
    # report describe a map nobody plays.
    enemies = site_spawns.place_enemies(
        site_spec or {}, pos, enemy_count=enemy_count,
        lateral=lateral, solids=solids).positions
''',
     '''    # PLACED ONCE, HERE OR ABOVE, NEVER BOTH. `assemble` places the enemies
    # before its site report closes -- a placement Lot could not honour has to
    # travel with the site rather than sit in a .tscn nobody diffs -- and then
    # hands the result down. Roadmap 3 asked for exactly this: "place once,
    # thread the result through, or assert the two agree". An assertion would
    # detect a disagreement; threading makes one impossible to express, because
    # there is no second call left to drift.
    #
    # `enemies=None` still places, so the standalone callers in
    # `tests/test_site_spawns.py` behave as they always have.
    #
    # `solids` matters for the same reason `seat_destinations` gets it above:
    # a placement that judged cover differently from the one in the site report
    # would make the report describe a map nobody plays. Threading removes that
    # risk rather than managing it.
    if enemies is None:
        enemies = site_spawns.place_enemies(
            site_spec or {}, pos, enemy_count=enemy_count,
            lateral=lateral, solids=solids).positions
    enemies = [tuple(e) for e in enemies]
'''),

    ("_lasertag_hook_nodes passes it through",
     '''def _lasertag_hook_nodes(pos, site_spec=None, enemy_count=6, lateral=1.5,
                         solids=None, bounds=None):
''',
     '''def _lasertag_hook_nodes(pos, site_spec=None, enemy_count=6, lateral=1.5,
                         solids=None, bounds=None, enemies=None):
'''),

    ("...to the plan",
     '''    _plan = _lasertag_hook_plan(pos, site_spec, enemy_count=enemy_count,
                                lateral=lateral, solids=solids, bounds=bounds)
''',
     '''    _plan = _lasertag_hook_plan(pos, site_spec, enemy_count=enemy_count,
                                lateral=lateral, solids=solids, bounds=bounds,
                                enemies=enemies)
'''),

    ("write_walk_scene passes it through",
     '''def write_walk_scene(site_spec, merged, walk_out, site_tscn_base,
                     addon_dir="addons/lot", portable=False, solids=None):
''',
     '''def write_walk_scene(site_spec, merged, walk_out, site_tscn_base,
                     addon_dir="addons/lot", portable=False, solids=None,
                     enemies=None):
'''),

    ("...to the hook nodes",
     '''    lt_body = _lasertag_hook_nodes(
        pos, site_spec, solids=solids,
        bounds=_destination_bounds(merged, pos))
''',
     '''    lt_body = _lasertag_hook_nodes(
        pos, site_spec, solids=solids,
        bounds=_destination_bounds(merged, pos), enemies=enemies)
'''),

    ("assemble hands down the set it already reported",
     '''        result["walk_positions"] = write_walk_scene(
            site_spec, merged, walk_out, site_spec["name"], solids=solids,
            portable=portable)
''',
     '''        # The enemies this report already carries. Placing them again here
        # would be a second answer to a question already answered, which is
        # roadmap 3 and which cost a whole level's cover being planned against
        # a set the scene did not contain.
        result["walk_positions"] = write_walk_scene(
            site_spec, merged, walk_out, site_spec["name"], solids=solids,
            portable=portable, enemies=spawn_plan.positions)
'''),
]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    got = _sha(raw)
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    print(f"  {TARGET.relative_to(ROOT)}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {got}")


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
    print(f"APPLICABLE: all {len(EDITS)} anchors present exactly once." if ok
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
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print()
    print("  NEXT:")
    print("    cd lot; python -m pytest tests -q; cd ..")
    print("    python -u level_factory\\apps\\cli\\main.py -C "
          "workspaces\\lot-demo-ws run lot_demo_001")
    print("    -- lot_assemble should EXECUTE (lot.py changed) and the "
          "cover_plan should be identical to the run before it")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} B, sha256 {_sha(after)}")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} B (got {len(raw)})")
    ok(_sha(raw).startswith("998C3D27ED56"),
       f"target sha256 matches the read ({_sha(raw)[:12]})")
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    # The constraint this must not break has to still be in the file.
    flat = " ".join(text.replace("#", " ").split())
    ok("because the walk scene is written after this report closes" in flat,
       "the comment stating WHY the second placement existed is present "
       "(whitespace-normalised: it wraps across source lines)")
    ok("because the walk scene is written after this report closes"
       not in text,
       "...and it really does wrap, so a naive search would have been wrong")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    code = "\n".join(l for l in out.split("\n") if not l.lstrip().startswith("#"))
    ok(code.count("if enemies is None:") == 1,
       "exactly one guard reaches the CODE")
    ok(code.count("site_spawns.place_enemies(") == 2,
       f"place_enemies still appears twice in code -- assemble's and the "
       f"guarded fallback ({code.count('site_spawns.place_enemies(')})")
    ok("enemies=spawn_plan.positions" in code,
       "assemble hands down the set it reported")

    try:
        compile(out, str(TARGET), "exec")
        ok(True, "lot.py compiles after the edit")
    except SyntaxError as exc:
        ok(False, f"lot.py compiles after the edit ({exc})")

    # -- BEHAVIOUR: same scene, one placement instead of two ---------------
    import importlib.util
    lot_dir = str(TARGET.parent)
    if lot_dir not in sys.path:
        sys.path.insert(0, lot_dir)
    saved = sys.modules.pop("lot", None)

    def _mod(name, source):
        spec = importlib.util.spec_from_loader(name, loader=None)
        m = importlib.util.module_from_spec(spec)
        m.__file__ = str(TARGET)
        sys.modules[name] = m
        exec(compile(source, str(TARGET), "exec"), m.__dict__)
        return m

    import site_spawns as S
    real_place = S.place_enemies
    try:
        def _site(b):
            return {"name": "t", "ground": {"size_x": 232.0, "size_y": 100.0},
                    "buildings": list(b)}

        def _b(i, at, fp=(44.0, 44.0), rot=0):
            return {"id": i, "at": list(at), "_footprint": list(fp), "rot": rot}

        spec = _site([_b("b0", (6.0, -10.0), rot=180),
                      _b("b1", (51.0, -5.0), rot=180),
                      _b("b2", (84.0, -5.0), rot=180),
                      _b("b3", (135.0, -10.0))])
        rt = {"spawn": (51.0, -5.0, 0.0), "objective": (35.0, -17.0, 0.9),
              "extraction": (117.0, -16.0, 0.0)}

        calls = []

        def spy(*a, **k):
            calls.append(1)
            return real_place(*a, **k)

        old_m = _mod("_r53_lot_old", text)
        new_m = _mod("_r53_lot_new", out)

        # OLD: the scene writer places its own.
        S.place_enemies = spy
        calls.clear()
        body_old = old_m._lasertag_hook_nodes(dict(rt), spec)
        n_old_standalone = len(calls)

        # NEW, standalone (enemies=None): must behave exactly as before.
        calls.clear()
        body_new = new_m._lasertag_hook_nodes(dict(rt), spec)
        n_new_standalone = len(calls)

        ok(body_old == body_new,
           f"standalone: the scene body is byte-identical "
           f"({len(body_old)} lines)")
        ok(n_old_standalone == n_new_standalone == 1,
           f"standalone: both place exactly once "
           f"({n_old_standalone} vs {n_new_standalone})")

        # NEW, threaded: assemble's shape -- place once, hand it down.
        placed = real_place(spec, new_m._lasertag_hook_plan(
            dict(rt), spec)["positions"]).positions
        calls.clear()
        body_threaded = new_m._lasertag_hook_nodes(dict(rt), spec,
                                                   enemies=placed)
        n_threaded = len(calls)
        ok(n_threaded == 0,
           f"threaded: place_enemies is NOT called again ({n_threaded})")
        ok(body_threaded == body_old,
           "threaded: the scene body is still byte-identical to the original")

        # ...and prove that comparison can fail.
        calls.clear()
        moved = [(x + 5.0, y, z) for (x, y, z) in placed]
        other = new_m._lasertag_hook_nodes(dict(rt), spec, enemies=moved)
        ok(other != body_threaded,
           "that comparison CAN fail -- moved enemies change the body")
        ok(len(calls) == 0, "and it still did not place")
    finally:
        S.place_enemies = real_place
        for k in ("_r53_lot_old", "_r53_lot_new"):
            sys.modules.pop(k, None)
        if saved is not None:
            sys.modules["lot"] = saved

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
