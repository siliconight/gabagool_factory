r"""L17: a spec must not park a solid volume in a stair it reserved.

    python patch_dc_stair_volume_lint.py --check
    python patch_dc_stair_volume_lint.py
    python patch_dc_stair_volume_lint.py --selftest   (run it AFTER applying)
    python patch_dc_stair_volume_lint.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

WHAT IT CATCHES, AND WHAT IT HONESTLY DOES NOT.

`office.json` authors a stair at (0.0, 0.0) and a `volume` named
`elevator_block` at (0.0, 0.0) -- a 2.0 x 2.0 x 3.0 m solid metal box on the
exact coordinates of a 3.2 m wide switchback. It leaves 0.60 m of the flight
clear. A Godot nav agent of radius 0.40 needs 0.80 m to walk through, so no
navmesh generates across it, and `office_stair_0` bakes as two disjoint
islands. That is one of the 7 shells failing `check.py`'s nav gate.

THIS RULE EXPLAINS EXACTLY ONE OF THOSE SEVEN, AND IT IS THE ONLY SPEC-LEVEL
RULE I COULD FIND THAT SURVIVES ITS OWN CONTROLS. Measured on the specs to
hand, `free width < 0.8 m` fires on 1 of 8 failing stairs and 0 of 8 passing
ones. Three richer hypotheses were tested and killed:

    volume overlaps the stair well    5 of 7 shells, but 2 FALSE POSITIVES
                                      (a vault, a power cabinet -- both bake
                                      fine) and 2 false negatives
    volume in the climb envelope      2 of 8, 1 false positive -- worse
    stair crosses a basement          4 of 8, but 4 passing stairs do too

So this is NOT "the cause of the nav-gate failures". It is one authoring
error, provably wrong on its own terms: a spec that reserves a stairwell and
then puts a box in it is incorrect whether or not the bake happens to
survive, and no existing rule looks. The other six failing stairs remain
undiagnosed and none of them has a volume in the flight at all.

WHY THE THRESHOLD IS WHAT IT IS. 0.80 m is 2 x the 0.40 m agent radius the
nav bake actually runs with (`nav_gate.py`: radius 0.40 cell 0.10). Below it
the navmesh cannot exist, which is a fact about the bake and not a taste
call. Above it the rule says nothing -- deliberately, because the evidence
above shows overlap on its own does not predict a failure.

FOOTPRINT COMES FROM `stair_core._core_of`, NOT FROM ARITHMETIC HERE. That is
the function the authoring tool already uses to reserve a stair, so the lint
and the placer cannot disagree about where a stair is. It is a little smaller
than the envelope the builder finally cuts, which makes the rule conservative
-- it under-reports rather than inventing failures.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter/layout_lint.py")
SIDECAR = ".pre_stairvol"


OLD_IMPORT = '''from partition_bounds import partition_overshoot'''

NEW_IMPORT = '''from partition_bounds import partition_overshoot'''


OLD_CONST = '''COVER_REPEAT_MAX = 3         # identical cover volumes in a row (D2)'''

NEW_CONST = '''COVER_REPEAT_MAX = 3         # identical cover volumes in a row (D2)
# L17: the nav bake runs at radius 0.40 (nav_gate.py, "bake: radius 0.40 cell
# 0.10"), so a walkable strip narrower than twice that cannot hold a navmesh
# at all. Not a taste threshold -- below this the geometry is unwalkable by
# the engine that has to walk it.
AGENT_DIAMETER = 0.80'''


OLD_CALL = '''    warns += bounds_findings(spec)          # L13 partition-in-footprint (advisory)'''

NEW_CALL = '''    warns += bounds_findings(spec)          # L13 partition-in-footprint (advisory)
    fails += stair_volume_findings(spec)    # L17 volume parked in a stair flight'''


OLD_FN = '''def ladder_findings(spec):'''

NEW_FN = '''def stair_volume_findings(spec):
    """L17 (FAIL): a solid volume must not narrow a stair flight below the
    width a nav agent needs to walk it.

    `office.json` puts `elevator_block` (2.0 x 2.0 x 3.0, convex collision) at
    (0.0, 0.0) and `office_stair_0` at (0.0, 0.0). The box leaves 0.60 m of a
    3.20 m flight, the bake needs 0.80 m, and the stair comes out of Godot as
    two disjoint navmesh islands -- unwalkable, with nothing in the toolchain
    saying so until the engine gate ran.

    SCOPE, STATED PLAINLY. This fires on volumes that eat the WIDTH. It is not
    a theory of why every stair fails its nav bake: measured across the specs
    to hand it catches 1 of 8 failing stairs and fires on 0 of 8 passing ones.
    A wider rule -- any volume overlapping the stair -- was tested and
    rejected, because it flags a vault and a power cabinet that both bake
    perfectly well. Precision was chosen over recall deliberately: a lint that
    fails working buildings gets switched off, and then it protects nothing.

    The footprint comes from `stair_core._core_of`, the same reservation the
    stair placer uses, so this cannot disagree with the tool that put the
    stair there.
    """
    fails = []
    stairs = spec.get("stairs") or []
    vols = spec.get("volumes") or []
    if not stairs or not vols:
        return fails
    try:
        import stair_core
    except ImportError:                      # authoring tool absent; say
        return fails                         # nothing rather than guess

    for sd in stairs:
        try:
            fp = stair_core._core_of(spec, sd)["footprint"]
        except Exception:
            continue                         # a stair this lint cannot place
                                             # is not a stair it may judge
        facing = (sd.get("facing") or "N")
        cross = 0 if facing in ("N", "S") else 1
        lo, hi = fp[cross], fp[cross + 2]
        spans, names = [], []
        for v in vols:
            vr = (v["x"] - v["size_x"] / 2, v["y"] - v["size_y"] / 2,
                  v["x"] + v["size_x"] / 2, v["y"] + v["size_y"] / 2)
            if (vr[2] <= fp[0] or vr[0] >= fp[2]
                    or vr[3] <= fp[1] or vr[1] >= fp[3]):
                continue
            spans.append((max(lo, vr[cross]), min(hi, vr[cross + 2])))
            names.append(v.get("name", "?"))
        if not spans:
            continue
        # Widest strip left clear across the flight, merging overlaps.
        spans.sort()
        free, cur = [], lo
        for a, b in spans:
            if a > cur:
                free.append(a - cur)
            cur = max(cur, b)
        if cur < hi:
            free.append(hi - cur)
        widest = max(free) if free else 0.0
        if widest < AGENT_DIAMETER:
            fails.append(
                f"L17 volume in stair flight: '{sd.get('id') or 'stair'}' is "
                f"{hi - lo:.2f} m wide and {', '.join(sorted(set(names)))} "
                f"leave{'' if len(set(names)) > 1 else 's'} {widest:.2f} m "
                f"clear (a nav agent needs {AGENT_DIAMETER:.2f} m) -- the "
                f"flight bakes as disjoint navmesh islands and cannot be "
                f"walked")
    return fails


def ladder_findings(spec):'''


EDITS = {TARGET: ((OLD_CONST, NEW_CONST), (OLD_FN, NEW_FN), (OLD_CALL, NEW_CALL))}

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


def selftest(root: Path) -> int:
    """Run the rule against specs whose nav-gate verdict is already known."""
    dc = root / "deli_counter"
    sys.path.insert(0, str(dc))
    import json
    try:
        from layout_lint import stair_volume_findings
    except ImportError as exc:
        print(f"cannot import the patched rule: {exc}")
        return 1

    # (spec, stair, does nav_gate FAIL it?) -- measured 2026-08-13.
    KNOWN = [("office", True), ("bank_branch_a04", False),
             ("warehouse_a02", False), ("lf_lot_demo_001_5118", False),
             ("night_deli", True), ("cr_deli", True),
             ("corner_deli_heist_01", True), ("primos_pizza", True),
             ("night_pawn", True),
             ("cbp_town_finale_midbalanced_schemafixed", True)]
    bad = fired_bad = fired_ok = 0
    for name, nav_fails in KNOWN:
        p = dc / "specs" / f"{name}.json"
        if not p.is_file():
            print(f"  skip {name} (no spec)")
            continue
        found = stair_volume_findings(json.loads(p.read_text(encoding="utf-8")))
        mark = "L17" if found else "  -"
        print(f"  {mark}  {name:<42} nav gate: "
              f"{'FAILS' if nav_fails else 'ok'}")
        for f in found:
            print(f"        {f}")
        if found and nav_fails:
            fired_bad += 1
        elif found and not nav_fails:
            fired_ok += 1
            bad += 1                          # a false positive IS a failure
    print()
    print(f"  fires on {fired_bad} shell(s) the nav gate fails, and "
          f"{fired_ok} it passes")
    if fired_ok:
        print("  A LINT THAT FAILS A WORKING BUILDING GETS SWITCHED OFF. "
              "This is a defect.")
    elif fired_bad:
        print("  no false positives; the rule is narrow and correct on what "
              "it claims")
    return 1 if bad else 0


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
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--selftest" in argv:
        return selftest(root)

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
