#!/usr/bin/env python3
"""Roadmap 51, defect three: the scene DID carry the plan. The test held another.

WHAT THE ROADMAP SAYS, AND WHY IT IS WRONG

Item 51 files this as "THE ONE THAT MATTERS MOST: the scene does not carry the
position the planner chose", and puts it in roadmap 48's family -- the graded
artefact not being the shipped artefact. Measured, it is not that. It is item
51 defect ONE's family: a stale caller.

`_lasertag_hook_nodes` does not plan against the positions it is handed. It
seats the nav hooks onto floor, clears the crew spawn off the wall it is
standing against, and spreads the enemies along the route THOSE TWO STEPS
produce (`lot.py`, the three statements this patch moves). The test planned
from the raw `route()` dict instead:

    planned = site_spawns.place_enemies(BAIE_DORE, route()).positions

On `BAIE_DORE` the crew spawn (51.0, -5.0) is the dead centre of `b1`, a
44 x 44 shell at (51, -5). `clear_crew_spawn` moves it to (51.0, 18.5) --
23.5 m -- and `seat_destinations` drops the objective from z 0.9 to 0.0. The
route's first point moves, so every enemy on it moves:

      i    planned x (test)   product x (scene)
      0           19.242160           37.734968     <- the assertion's pair
      1           64.683855           36.919915
      2           69.055220           48.119216
      3           73.426585           65.310451
      4           88.003898           82.593142
      5          107.547001           99.869736

`37.73496811511527` through `_v3`'s `{:g}` is `37.735`, which is the number in
the traceback. Recomputing the plan from the same `pos` the scene was written
from: 0 of 18 coordinate pairs fail at `abs_tol=1e-3`. The scene carries its
plan exactly. Nothing else was hiding behind it.

The roadmap's own warnings still stand and are the reason this was findable: do
not widen the bound, do not skip the test. An 18.5 m gap was real. Only the
mechanism was misattributed -- two artefacts compared without establishing they
came from the same build, which is the failure `CLAUDE.md` rule 1 names.

WHAT THIS CHANGES, AND WHY IT IS NOT A TEST-ONLY FIX

The test could re-run those two steps itself. That is what it was already doing
by omission, and it is what drifted: because `_lasertag_hook_nodes` returned
only the scene body, the one question worth asking of it -- are the positions
in the scene the positions that were planned -- could ONLY be asked by
reproducing its derivation by hand. A third preprocessing step added later
would desync it again, silently, and the next reader would get another 18.5 m
mystery.

So the derivation moves into `_lasertag_hook_plan`, which returns the resolved
positions, route and enemies; `_lasertag_hook_nodes` calls it and writes the
same body it always did. The scene body is byte-identical -- that is asserted
in --selftest, not hoped for. The test then asks the tool which plan it used.

    lot.py                      : 99,766 B  sha256 7BE6D556...
    lot/tests/test_site_spawns.py: 26,875 B  sha256 5008C8AD...  (post
                                   patch_lot_stale_spawn_callers.py)

USAGE

    python patches\patch_lot_hook_plan.py --check
    python patches\patch_lot_hook_plan.py --selftest
    python patches\patch_lot_hook_plan.py
    python patches\patch_lot_hook_plan.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r51hookplan"

ROOT = Path(__file__).resolve().parent.parent
LOT = ROOT / "lot" / "lot.py"
TEST = ROOT / "lot" / "tests" / "test_site_spawns.py"

EXPECT = {
    LOT: (99766, "7BE6D5569C4F549EB7D87768CB53E1E23A5A135F1AF4EC63764960A433A10829"),
    TEST: (26875, "5008C8ADE1B2571CBB753BC679045E04F6838405775A72EC8310847E84A63AB1"),
}


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _eol(raw: bytes, who: str) -> str:
    """The file's line ending, or a refusal. Keyed off the FILE, never an anchor."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {who} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {who} has no line endings at all.")
    return "\r\n" if crlf else "\n"


def _n(text: str) -> str:
    return text.replace("\r\n", "\n")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


# ---------------------------------------------------------------------------
# lot.py
# ---------------------------------------------------------------------------
LOT_OLD = '''def _lasertag_hook_nodes(pos, site_spec=None, enemy_count=6, lateral=1.5,
                         solids=None, bounds=None):
'''

LOT_NEW = '''def _lasertag_hook_plan(pos, site_spec=None, enemy_count=6, lateral=1.5,
                        solids=None, bounds=None) -> dict:
    """The positions the walk scene will be written from, before it is written.

    `_lasertag_hook_nodes` does not place anything where its caller pointed. It
    seats the nav hooks onto floor, clears the crew spawn off the wall it is
    standing against, and only then spreads the enemies along the route those
    two steps produced. That is correct and stays. What was wrong is that it
    returned only the scene body, so the one question worth asking of it --
    "are the positions in the scene the positions that were planned" -- could
    be asked only by re-running the derivation by hand.

    `tests/test_site_spawns.py` did exactly that and drifted. It planned from
    the RAW route dict, and on `BAIE_DORE`, whose crew spawn sits at the dead
    centre of a 44 x 44 shell, `clear_crew_spawn` moves the spawn 23.5 m and
    every enemy spread along the route with it -- 19.242 planned against 37.735
    written on the first pair, all six disagreeing. Read as the scene losing
    the plan, filed as roadmap 48's family. The scene carried its own plan to
    0 of 18 failing pairs at `abs_tol=1e-3`; the plan the test held was of a
    route this tool never uses.

    Returning the resolved values is what stops that recurring: a caller
    checking the scene against the plan asks which plan was used instead of
    reproducing how it was derived, so a THIRD preprocessing step added here
    cannot silently desync anybody.
    """
    import site_spawns

    # The nav hooks first: a destination on top of a counter has no route to
    # it, and every point below is derived from these three. `solids` is the
    # site's collision reading when the caller has one -- without it the hook
    # is only floored, not moved off whatever it is standing in.
    pos = site_spawns.seat_destinations(
        pos, solids=solids, bounds=bounds)[0]
    # And then off the wall it is standing against. Seating answers "is there
    # floor under this point"; this answers "will the bake leave a polygon on
    # it", which is a different question and the one the bot actually needs.
    pos = site_spawns.clear_crew_spawn(site_spec or {}, pos)[0]
    # `solids` here for the same reason `seat_destinations` gets it above: the
    # scene Laser Tag evaluates is written from THIS call, and a placement that
    # judged cover differently from the one in the site report would make the
    # report describe a map nobody plays.
    enemies = site_spawns.place_enemies(
        site_spec or {}, pos, enemy_count=enemy_count,
        lateral=lateral, solids=solids).positions
    return {"positions": pos,
            "route": [pos["spawn"], pos["objective"], pos["extraction"]],
            "enemies": enemies}


def _lasertag_hook_nodes(pos, site_spec=None, enemy_count=6, lateral=1.5,
                         solids=None, bounds=None):
'''

#: The three statements the plan helper now owns, replaced by the call.
LOT_BODY_OLD = '''    import site_spawns

    # The nav hooks first: a destination on top of a counter has no route to
    # it, and every point below is derived from these three. `solids` is the
    # site's collision reading when the caller has one -- without it the hook
    # is only floored, not moved off whatever it is standing in.
    pos = site_spawns.seat_destinations(
        pos, solids=solids, bounds=bounds)[0]
    # And then off the wall it is standing against. Seating answers "is there
    # floor under this point"; this answers "will the bake leave a polygon on
    # it", which is a different question and the one the bot actually needs.
    pos = site_spawns.clear_crew_spawn(site_spec or {}, pos)[0]
    route = [pos["spawn"], pos["objective"], pos["extraction"]]
    # `solids` here for the same reason `seat_destinations` gets it above: the
    # scene Laser Tag evaluates is written from THIS call, and a placement that
    # judged cover differently from the one in the site report would make the
    # report describe a map nobody plays.
    enemies = site_spawns.place_enemies(
        site_spec or {}, pos, enemy_count=enemy_count,
        lateral=lateral, solids=solids).positions
'''

LOT_BODY_NEW = '''    import site_spawns

    # Every position this scene is written from, resolved by the tool rather
    # than by whoever is reading it afterwards. `_lasertag_hook_plan` carries
    # why that distinction is worth a function.
    _plan = _lasertag_hook_plan(pos, site_spec, enemy_count=enemy_count,
                                lateral=lateral, solids=solids, bounds=bounds)
    pos = _plan["positions"]
    route = _plan["route"]
    enemies = _plan["enemies"]
'''

# ---------------------------------------------------------------------------
# tests/test_site_spawns.py
# ---------------------------------------------------------------------------
TEST_OLD = '''    written = _enemy_vectors(text)
    planned = site_spawns.place_enemies(BAIE_DORE, route()).positions
'''

TEST_NEW = '''    written = _enemy_vectors(text)
    # The plan the TOOL used, asked of the tool. Planning from `route()` here
    # planned against a route `_lasertag_hook_nodes` never uses: it seats the
    # hooks and clears the crew spawn first, and on BAIE_DORE that moves the
    # spawn 23.5 m out of the shell it starts inside, taking all six enemies
    # with it. The 18.5 m disagreement that followed read as the scene losing
    # the plan, and was this line.
    planned = lot._lasertag_hook_plan(route(), BAIE_DORE)["enemies"]
'''

EDITS = [
    (LOT, "lot.py: add _lasertag_hook_plan above _lasertag_hook_nodes",
     LOT_OLD, LOT_NEW),
    (LOT, "lot.py: _lasertag_hook_nodes calls the plan helper",
     LOT_BODY_OLD, LOT_BODY_NEW),
    (TEST, "test: plan from the tool, not from the raw route",
     TEST_OLD, TEST_NEW),
]


# ---------------------------------------------------------------------------
def _load(p: Path):
    raw = p.read_bytes()
    return raw, _eol(raw, p.name), _n(raw.decode("utf-8"))


def _preflight():
    """Every file exists and every anchor is present, BEFORE anything is written.

    A patch that half-applies and then raises is worse than one that refuses,
    and this one touches two files in two repos' worth of consequence.
    """
    missing = [p for p in (LOT, TEST) if not p.exists()]
    if missing:
        raise SystemExit("REFUSING: missing " + ", ".join(str(m) for m in missing))
    texts = {p: _load(p)[2] for p in (LOT, TEST)}
    problems = []
    for path, name, old, _new in EDITS:
        n = texts[path].count(_n(old))
        if n != 1:
            problems.append(f"{name}: anchor found {n} times, wanted 1")
    return texts, problems


def _identity():
    for p in (LOT, TEST):
        if not p.exists():
            print(f"  {p.name}: MISSING")
            continue
        raw = p.read_bytes()
        want_b, want_s = EXPECT[p]
        got_s = _sha(raw)
        mark = "" if len(raw) == want_b else "   <-- not the size this was read against"
        print(f"  {p.relative_to(ROOT)}")
        print(f"    bytes  : {len(raw)}   (expected {want_b}){mark}")
        print(f"    sha256 : {got_s}{'' if got_s == want_s else '   <-- differs'}")


def check() -> int:
    _identity()
    print()
    _texts, problems = _preflight()
    for path, name, old, _new in EDITS:
        n = _texts[path].count(_n(old))
        print(f"  [{'ok' if n == 1 else 'MISSING'}]  {name}")
    print()
    if problems:
        print("NOT APPLICABLE: refusing rather than fuzzy-matching.")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"APPLICABLE: all {len(EDITS)} anchors present exactly once.")
    return 0


def apply() -> int:
    _identity()
    texts, problems = _preflight()
    if problems:
        raise SystemExit("REFUSING: " + "; ".join(problems) + ". Nothing written.")
    for p in (LOT, TEST):
        if _sidecar(p).exists():
            raise SystemExit(f"REFUSING: {_sidecar(p).name} exists -- looks "
                             f"applied. Use --revert first.")

    out = {}
    for p in (LOT, TEST):
        raw, eol, text = _load(p)
        for path, _name, old, new in EDITS:
            if path == p:
                text = text.replace(_n(old), _n(new), 1)
        out[p] = (raw, eol, text)

    # Only now does anything hit disk.
    print()
    for p, (raw, eol, text) in out.items():
        shutil.copy2(p, _sidecar(p))
        data = text.replace("\n", eol).encode("utf-8") if eol != "\n" \
            else text.encode("utf-8")
        p.write_bytes(data)
        print(f"  {p.relative_to(ROOT)}: {len(raw)} -> {len(data)} "
              f"({len(data) - len(raw):+d})  sha256 {_sha(data)}")
    return 0


def revert() -> int:
    any_done = False
    for p in (LOT, TEST):
        s = _sidecar(p)
        if not s.exists():
            print(f"  {p.name}: no sidecar, left alone")
            continue
        shutil.copy2(s, p)
        s.unlink()
        print(f"  {p.relative_to(ROOT)}: restored, {len(p.read_bytes())} B "
              f"sha256 {_sha(p.read_bytes())}")
        any_done = True
    if not any_done:
        raise SystemExit("REFUSING: nothing to revert.")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    texts, problems = _preflight()
    ok(not problems, f"all {len(EDITS)} anchors present exactly once")
    if problems:
        for p in problems:
            print(f"        {p}")
        print("\nSELFTEST FAILED")
        return 1

    lot_before, test_before = texts[LOT], texts[TEST]
    lot_after, test_after = lot_before, test_before
    for path, _name, old, new in EDITS:
        if path == LOT:
            lot_after = lot_after.replace(_n(old), _n(new), 1)
        else:
            test_after = test_after.replace(_n(old), _n(new), 1)

    # -- shape -------------------------------------------------------------
    ok("def _lasertag_hook_plan(" not in lot_before
       and lot_after.count("def _lasertag_hook_plan(") == 1,
       "lot.py gains exactly one _lasertag_hook_plan (0 -> 1)")
    ok(lot_after.count("def _lasertag_hook_nodes(") == 1,
       "lot.py still has exactly one _lasertag_hook_nodes")
    # The derivation MOVED rather than being duplicated. Asserted as
    # "the count did not change", not as "the count is 1": `clear_crew_spawn`
    # has a second, unrelated call site at lot.py:1414 (the walk-scene writer),
    # so a flat ==1 here fails for a reason that has nothing to do with this
    # patch -- and would have hidden a real duplication behind a wrong number.
    for call in ("site_spawns.seat_destinations(\n        pos, solids=solids",
                 "site_spawns.clear_crew_spawn(site_spec or {}, pos)[0]",
                 "site_spawns.place_enemies(\n        site_spec or {}, pos"):
        before_n, after_n = lot_before.count(call), lot_after.count(call)
        ok(before_n == after_n and before_n >= 1,
           f"derivation moved, not duplicated ({before_n} -> {after_n}): "
           f"{call.splitlines()[0][:44]}...")
    ok(test_before.count("lot._lasertag_hook_plan(") == 0
       and test_after.count("lot._lasertag_hook_plan(") == 1,
       "the test asks the tool for the plan (0 -> 1)")
    # Counted, not merely absent: `test_placement_is_deterministic` runs the
    # same call twice on purpose at lines 443-444 and must keep it. Only the
    # scene comparison's copy goes, so the count drops by exactly one.
    stale = "site_spawns.place_enemies(BAIE_DORE, route()).positions"
    ok(test_before.count(stale) == 3 and test_after.count(stale) == 2,
       f"the scene test's raw-route plan goes, the determinism test's two stay "
       f"({test_before.count(stale)} -> {test_after.count(stale)})")
    ok(_n(TEST_OLD) in test_before and _n(TEST_OLD) not in test_after,
       "and it is the scene comparison's copy specifically that went")

    # -- both files still parse -------------------------------------------
    for label, src, path in (("lot.py", lot_after, LOT),
                             ("test_site_spawns.py", test_after, TEST)):
        try:
            compile(src, str(path), "exec")
            ok(True, f"{label} compiles after the edit")
        except SyntaxError as exc:
            ok(False, f"{label} compiles after the edit ({exc})")

    # -- THE ONE THAT MATTERS: the scene body must not move ---------------
    # A refactor of the code that writes a shipped artefact is worth nothing
    # if it changes the artefact. Both versions are executed and their output
    # compared, rather than the equivalence being argued for.
    import importlib.util
    import io
    import contextlib

    def _load_mod(name, source):
        spec = importlib.util.spec_from_loader(name, loader=None)
        mod = importlib.util.module_from_spec(spec)
        mod.__file__ = str(LOT)
        sys.modules[name] = mod
        exec(compile(source, str(LOT), "exec"), mod.__dict__)
        return mod

    lot_dir = str(LOT.parent)
    if lot_dir not in sys.path:
        sys.path.insert(0, lot_dir)
    saved = sys.modules.pop("lot", None)
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

        with contextlib.redirect_stdout(io.StringIO()):
            old_mod = _load_mod("_r51_lot_old", lot_before)
            new_mod = _load_mod("_r51_lot_new", lot_after)
            body_old = old_mod._lasertag_hook_nodes(dict(rt), spec)
            body_new = new_mod._lasertag_hook_nodes(dict(rt), spec)

        ok(body_old == body_new,
           f"the scene body is unchanged by the refactor "
           f"({len(body_old)} lines, identical)")

        # ...and prove that comparison could have failed, by perturbing one
        # input and confirming the bodies then differ. A byte-equality check
        # that cannot distinguish anything has established nothing.
        with contextlib.redirect_stdout(io.StringIO()):
            other = new_mod._lasertag_hook_nodes(
                dict(rt, spawn=(60.0, -5.0, 0.0)), spec)
        ok(other != body_new,
           "that comparison CAN fail -- a moved spawn changes the body")

        # The plan helper agrees with the scene it produced: this is the
        # assertion the repaired test will make, made here against both.
        with contextlib.redirect_stdout(io.StringIO()):
            plan = new_mod._lasertag_hook_plan(dict(rt), spec)
        blk = "\n".join(body_new)
        blk = blk[blk.index('name="LT_EnemySpawnPoints"'):
                  blk.index('name="LT_ObjectivePoint"')]
        written = [tuple(float(n) for n in
                         line[len("transform = Transform3D("):-1].split(",")[9:12])
                   for line in blk.splitlines()
                   if line.startswith("transform = Transform3D(")]
        import math
        pairs_ok = (len(written) == len(plan["enemies"]) == 6) and all(
            math.isclose(g, w, abs_tol=1e-3)
            for (gx, gy, gz), (sx, sy, sz) in zip(written, plan["enemies"])
            for g, w in zip((gx, gy, gz), (sx, sz + 1.0, -sy)))
        ok(pairs_ok, "the plan helper matches the scene it produced, 18/18 pairs")
    finally:
        for k in ("_r51_lot_old", "_r51_lot_new"):
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
