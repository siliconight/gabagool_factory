r"""Move the planter that blocks night_deli's stair at the first-floor crossing.

    python patch_dc_night_deli_planter.py --check
    python patch_dc_night_deli_planter.py
    python patch_dc_night_deli_planter.py --selftest   (run it AFTER applying)
    python patch_dc_night_deli_planter.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

THE SECOND HALF OF NIGHT_DELI. `patch_dc_deli_stair_door.py` widened the
ground-floor stair door in all three deli clones. `cr_deli` and
`corner_deli_heist_01` went green -- `cr_deli` now bakes as ONE island,
y -3.00 .. 6.90, 483 polygons, which is the signature every passing shell
has. `night_deli` did not, because it has a second obstruction the other two
do not, and the door fix moved its break up one floor instead of closing it:

    before the door fix    islands -3.00..0.30 | 0.30..0.45 | 0.60..6.90
    after  the door fix    islands -3.00..3.45 | 3.60..6.90

The basement-to-first-floor run now connects. The break that is left sits at
3.45 -> 3.60, the FIRST-floor crossing, and this is what is standing there:

    planter_box_upper_hall_1   x -15.06 .. -14.36   z 3.30 .. 4.20

The ascending run of the switchback is x -15.00 .. -13.60, so the planter
covers -15.00 .. -14.36 of it and leaves 0.76 m. A Godot nav agent bakes at
radius 0.40 and needs 0.80 m. It misses by 4 centimetres, and 4 centimetres
is the whole difference between a shell that walks and a shell that does not.

THE FIX. x -14.71 -> -12.40, leaving the planter 0.85 m clear of the stair
well and clashing with nothing else on that floor (checked against every
volume whose z-range meets 3.30..4.20).

THE MARKER MOVES WITH IT. `AUTO_PLANTER_BOX_UPPER_HALL_1` is a `cover_low`
marker with `meta.auto = "cover_from_volume"` and `meta.from =
"planter_box_upper_hall_1"` -- it is derived from this volume and carries the
same coordinates. Moving the box and leaving the marker would leave a cover
point hanging in the stairwell the box just vacated, which is worse than the
defect being fixed: Laser Tag would route a bot to take cover behind nothing,
in the one place the level cannot afford clutter. Both edits or neither.

WHY NOT NUDGE IT 4 cm. Because the number to clear is not 0.76 -> 0.80. A
value sitting exactly on the threshold bakes at the mercy of cell
quantisation (cell 0.10), and the next person to touch this level would have
no idea they were standing on a cliff edge. 0.85 m of daylight between the
prop and the stair is a margin somebody can see.

NOT VERIFIED BY A BAKE YET:

    python deli_counter\build.py deli_counter\specs\night_deli.json
    python deli_counter\nav_gate.py deli_counter\build\night_deli.glb
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter/specs/night_deli.json")
SIDECAR = ".pre_planter"

OLD_VOLUME = '''      "name": "planter_box_upper_hall_1",
      "x": -14.71,'''

NEW_VOLUME = '''      "name": "planter_box_upper_hall_1",
      "x": -12.4,'''

OLD_MARKER = '''      "id": "AUTO_PLANTER_BOX_UPPER_HALL_1",
      "x": -14.71,'''

NEW_MARKER = '''      "id": "AUTO_PLANTER_BOX_UPPER_HALL_1",
      "x": -12.4,'''

EDITS = {TARGET: ((OLD_VOLUME, NEW_VOLUME), (OLD_MARKER, NEW_MARKER))}

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
    import json
    dc = root / "deli_counter"
    sys.path.insert(0, str(dc))
    try:
        import stair_core
    except ImportError as exc:
        print(f"cannot import stair_core: {exc}")
        return 1

    AGENT = 0.80
    spec = json.loads((root / TARGET).read_text(encoding="utf-8"))
    sd = spec["stairs"][0]
    core = stair_core._core_of(spec, sd)
    fp, well = core["footprint"], core["well"]
    seam = sd["x"]
    bad = 0

    print(f"  flight x {fp[0]:.2f}..{fp[2]:.2f}   runs meet at x {seam:.2f}")
    for v in spec.get("volumes") or []:
        vx0, vx1 = v["x"] - v["size_x"] / 2, v["x"] + v["size_x"] / 2
        vy0, vy1 = v["y"] - v["size_y"] / 2, v["y"] + v["size_y"] / 2
        if vx1 <= fp[0] or vx0 >= fp[2] or vy1 <= fp[1] or vy0 >= fp[3]:
            continue
        asc = max(min(vx1, fp[2]) - max(vx0, seam), 0.0)
        desc = max(min(vx1, seam) - max(vx0, fp[0]), 0.0)
        free_a, free_d = (fp[2] - seam) - asc, (seam - fp[0]) - desc
        ok = free_a >= AGENT and free_d >= AGENT
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {v['name']:<28} leaves "
              f"ascending {free_a:.2f} m, descending {free_d:.2f} m")
    if not any(True for v in spec.get("volumes") or []
               if not (v["x"] + v["size_x"] / 2 <= fp[0]
                       or v["x"] - v["size_x"] / 2 >= fp[2]
                       or v["y"] + v["size_y"] / 2 <= fp[1]
                       or v["y"] - v["size_y"] / 2 >= fp[3])):
        print("  no volume overlaps the flight at all")

    # the derived marker must have travelled with its volume
    vol = next(v for v in spec["volumes"] if v["name"] == "planter_box_upper_hall_1")
    mk = next((m for m in spec.get("markers") or []
               if m.get("meta", {}).get("from") == "planter_box_upper_hall_1"), None)
    if mk is None:
        print("  no derived cover marker found (unexpected)")
        bad += 1
    else:
        together = abs(mk["x"] - vol["x"]) < 1e-6 and abs(mk["y"] - vol["y"]) < 1e-6
        bad += 0 if together else 1
        print(f"  {'ok  ' if together else 'FAIL'} {mk['id']} at "
              f"({mk['x']}, {mk['y']}) vs volume ({vol['x']}, {vol['y']})"
              f"{'' if together else '  -- STRANDED'}")
        gap = (mk["x"] - 0.35) - well[2]
        print(f"       {gap:+.2f} m clear of the stair well")

    print()
    print("  the flight is clear and the cover marker moved with its box"
          if not bad else f"  {bad} problem(s) remain")
    print("  NOTE: spec arithmetic. Rebuild night_deli and run nav_gate --\n"
          "  the bake is the only thing that settles it.")
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
              f"present -- the volume and its marker must move together.")
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
