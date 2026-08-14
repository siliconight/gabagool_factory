r"""Widen the stair door the switchback's two runs each get half of.

    python patch_dc_deli_stair_door.py --check
    python patch_dc_deli_stair_door.py
    python patch_dc_deli_stair_door.py --selftest   (run it AFTER applying)
    python patch_dc_deli_stair_door.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

THREE SHELLS, ONE BUG. `cr_deli`, `corner_deli_heist_01` and `night_deli` are
clones of one authored deli: the same stair at (-15.0, 9.0), width 1.4,
run 5.5, switchback facing S, stories -1 -> 2, and the same ground-floor
partition carrying `office_stair_door`. They fail `nav_gate` identically, down
to the same 186-polygon ground-floor island. Fixing the spec fixes all three.

MEASURED IN `cr_deli.glb`, NOT INFERRED:

    doorway, as built           x -15.60 .. -14.40    1.20 m
    descending run (ramp_-1)    x -16.40 .. -15.00
    ascending  run (ramp_0)     x -15.00 .. -13.60    1.40 m wide
    wall segment int_0_1_seg2   x -14.40 .. -12.40

A switchback's two runs meet at x = -15.00 and the doorway is centred on that
seam. So each run gets exactly half the opening: the ascending run is clear
from -15.00 to -14.40, which is 0.60 m. Godot bakes navigation at radius 0.40
and needs 0.80 m. No navmesh forms on the ascending run where it crosses the
door, and the flight is severed there:

    island 2   polys 107   y -3.00 .. 0.30      basement, ground floor, stair
    island 1   polys 186   y  0.30 .. 0.45      stranded between the two
    island 3   polys 184   y  0.60 .. 6.90      everything above
    stair cr_deli_stair_0: no_path (endpoints on disjoint islands
                                    (lower on 2, upper on 3))

A passing shell bakes as ONE island over the whole height -- `lf_lot_demo_001_5118`
is island 0, 293 polys, y -3.30 .. 4.05, and its stair also crosses a basement.

WHY THE BAKE SEES THE WALL AT ALL. `nav_gate.gd` sets
`geometry_parsed_geometry_type = PARSED_GEOMETRY_MESH_INSTANCES`, so the bake
walks visual meshes. The wall is a visual mesh. This is not a case of a
collider being wrong; the geometry really does block the way.

THE FIX. `office_stair_door` width 1.2 -> 2.4, in all three specs. Centred on
the same seam, that leaves:

    descending run   -16.20 .. -15.00   1.20 m clear
    ascending  run   -15.00 .. -13.80   1.20 m clear

Both comfortably past 0.80. 1.6 m would also clear the threshold but leaves
exactly 0.80 on each side, and a nav agent that fits with nothing to spare is
a bake away from not fitting -- the margin is the point.

WHY NOT MOVE THE DOOR OFF THE SEAM. A 1.2 m door shifted to sit wholly over
the ascending run would let a climber up but leave the descending run walled
off, so half the stair still would not bake. The opening has to span the
stair, because the stair is what it serves.

WHY NOT TRIM THE WALL. `stair_core._trim_partition` exists to cut partitions
back at a flight's edge and would be the better fix, but it runs in the
authoring tool (`stair_place --write`), not the builder, so it never touched
these hand-authored specs. Making the builder trim walls at stair footprints
is a real change to `deli_counter.py` that would move geometry in all 135
shells; it should be measured against the whole library, not slipped in
behind three demo levels. This patch is the spec-level fix. The builder
question is worth its own pass.

NOT VERIFIED BY A BAKE YET. Every number above is measured off the built GLB
and the recorded islands, but the proof is a rebuild:

    python deli_counter\build.py deli_counter\specs\cr_deli.json
    python deli_counter\build.py deli_counter\specs\corner_deli_heist_01.json
    python deli_counter\build.py deli_counter\specs\night_deli.json
    python deli_counter\nav_gate.py --all
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SPECS = ("cr_deli", "corner_deli_heist_01", "night_deli")
SIDECAR = ".pre_stairdoor"

OLD = '''          "kind": "door",
          "pos": -0.4,
          "width": 1.2,
          "tag": "office_stair_door"'''

NEW = '''          "kind": "door",
          "pos": -0.4,
          "width": 2.4,
          "tag": "office_stair_door"'''

EDITS = {Path(f"deli_counter/specs/{n}.json"): ((OLD, NEW),) for n in SPECS}

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
    """Re-derive the clear width each run gets through the opening."""
    import json
    dc = root / "deli_counter"
    sys.path.insert(0, str(dc))
    try:
        import stair_core
    except ImportError as exc:
        print(f"cannot import stair_core: {exc}")
        return 1

    AGENT = 0.80
    bad = 0
    for name in SPECS:
        p = dc / "specs" / f"{name}.json"
        if not p.is_file():
            print(f"  skip {name} (no spec)")
            continue
        spec = json.loads(p.read_text(encoding="utf-8"))
        sd = spec["stairs"][0]
        fp = stair_core._core_of(spec, sd)["footprint"]
        seam = sd["x"]                       # the two runs of a switchback meet here
        door = next((o for pt in spec.get("partitions", [])
                     for o in (pt.get("openings") or [])
                     if o.get("tag") == "office_stair_door"), None)
        if not door:
            print(f"  {name}: no office_stair_door found")
            bad = 1
            continue
        half = door["width"] / 2
        lo, hi = seam - half, seam + half
        desc = min(hi, seam) - max(lo, fp[0])       # descending run share
        asc = min(hi, fp[2]) - max(lo, seam)        # ascending run share
        ok = desc >= AGENT and asc >= AGENT
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<24} door {door['width']:.1f} m "
              f"-> descending {desc:.2f} m, ascending {asc:.2f} m "
              f"(need {AGENT:.2f})")
    print()
    print("  both runs of every switchback fit through the opening"
          if not bad else f"  {bad} spec(s) still too narrow")
    print("  NOTE: spec arithmetic. Rebuild the three shells and run nav_gate\n"
          "  before believing it -- that is the only thing that bakes.")
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
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    import json
    try:
        json.loads(out)
    except ValueError as exc:
        print(f"REFUSING: {path.name} -- not valid JSON after the edit: {exc}")
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
