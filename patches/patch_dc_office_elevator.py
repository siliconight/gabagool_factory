r"""Move `elevator_block` out of the stair it was authored on top of.

    python patch_dc_office_elevator.py --check
    python patch_dc_office_elevator.py
    python patch_dc_office_elevator.py --selftest   (run it AFTER applying)
    python patch_dc_office_elevator.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

THE DEFECT, MEASURED. `office.json` authors:

    stairs[0]   office_stair_0   x = 0.0  y = 0.0   switchback, stories 0 -> 2
    volumes[0]  elevator_block   x = 0.0  y = 0.0   2.0 x 2.0 x 3.0, convex

The same coordinates. A solid metal box standing in the stairwell. The flight
is 3.20 m wide and the box leaves 0.60 m clear; Godot bakes navigation at
radius 0.40, so it needs 0.80 m and gets none. `office.glb` comes out with no
navmesh at all between y 1.2 and y 3.3 -- 2.1 m of the flight missing -- and
`nav_gate.py` reports:

    stair office_stair_0: no_path (endpoints on disjoint islands
                                   (lower on 1, upper on 2))
    navigable: NO -- a stair is not traversable, so this shell cannot be
                     walked whatever its markers say

That is one of the 7 shells failing `check.py`, which is what blocks the
deli_counter commit.

THE FIX. x 0.0 -> 3.6. The box moves 3.6 m along +X and stops being in the
stair; nothing else moves.

WHY 3.6 AND NOT SOMETHING ELSE. The stair reserves x -1.60..1.60
(`stair_core._core_of`). The box is 2.0 wide, so its centre must sit at
x >= 2.60 for its edge to clear the flight at all. 3.6 leaves its near edge at
2.60 -- exactly 1.00 m of open floor between stair and elevator, which is
walkable by the same 0.80 m agent that could not get past it before. Closer
than that and the corridor between them is the next thing that fails to bake.

WHY NOT MOVE THE STAIR. The stair drives slab cuts, the discharge bridge, and
circulation; the elevator is a prop with a collision box. Moving the smaller
thing is the smaller claim. It also keeps the elevator beside the stair core,
which is where an elevator belongs in an office plan.

WHAT THIS DOES NOT FIX. Six other shells fail the same gate for reasons that
are NOT a volume in the flight -- `cr_deli`, `corner_deli_heist_01` and
`night_deli` have nothing in their stairs at all and bake their ground floor
as an island severed from both the basement and the storeys above. This patch
is one shell. It is the only one of the seven with a diagnosis I can defend.

VERIFY IT YOURSELF -- the rebuild is the real test:

    python deli_counter\build.py --spec deli_counter\specs\office.json
    python deli_counter\nav_gate.py deli_counter\build\office.glb
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter/specs/office.json")
SIDECAR = ".pre_elevator"


OLD = '''  {
   "name": "elevator_block",
   "x": 0.0,
   "y": 0.0,'''

NEW = '''  {
   "name": "elevator_block",
   "x": 3.6,
   "y": 0.0,'''


EDITS = {TARGET: ((OLD, NEW),)}

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
    """Recompute the clear width from the patched spec, on disk."""
    import json
    dc = root / "deli_counter"
    sys.path.insert(0, str(dc))
    try:
        import stair_core
    except ImportError as exc:
        print(f"cannot import stair_core: {exc}")
        return 1

    spec = json.loads((root / TARGET).read_text(encoding="utf-8"))
    sd = spec["stairs"][0]
    fp = stair_core._core_of(spec, sd)["footprint"]
    cross = 0 if (sd.get("facing") or "N") in ("N", "S") else 1
    lo, hi = fp[cross], fp[cross + 2]
    print(f"  {sd['id']}: flight spans x {lo:.2f}..{hi:.2f}  ({hi - lo:.2f} m)")

    spans = []
    for v in spec.get("volumes") or []:
        vr = (v["x"] - v["size_x"] / 2, v["y"] - v["size_y"] / 2,
              v["x"] + v["size_x"] / 2, v["y"] + v["size_y"] / 2)
        if (vr[2] <= fp[0] or vr[0] >= fp[2]
                or vr[3] <= fp[1] or vr[1] >= fp[3]):
            continue
        spans.append((max(lo, vr[cross]), min(hi, vr[cross + 2]), v["name"]))
    for a, b, nm in spans:
        print(f"    still in the flight: {nm}  {a:.2f}..{b:.2f}")

    spans.sort()
    free, cur = [], lo
    for a, b, _n in spans:
        if a > cur:
            free.append(a - cur)
        cur = max(cur, b)
    if cur < hi:
        free.append(hi - cur)
    widest = max(free) if free else 0.0
    print(f"  widest clear strip: {widest:.2f} m   (a nav agent needs 0.80)")

    ev = next(v for v in spec["volumes"] if v["name"] == "elevator_block")
    gap = (ev["x"] - ev["size_x"] / 2) - hi
    print(f"  elevator near edge at x {ev['x'] - ev['size_x'] / 2:.2f}, "
          f"{gap:.2f} m of floor between it and the flight")

    ok = widest >= 0.80 and not spans and gap >= 0.80
    print()
    print("  the stair is clear and the corridor beside it is walkable"
          if ok else "  FAILED: the flight or the corridor is still too narrow")
    print("  NOTE: this is spec arithmetic. The real proof is a rebuild plus\n"
          "  nav_gate on the new office.glb -- run those before believing it.")
    return 0 if ok else 1


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
            print(f"  anchor starts: {old.splitlines()[1].strip()[:70]!r}")
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
        print(f"REFUSING: {path.name} -- the patched spec is not valid JSON: "
              f"{exc}")
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
