r"""Move the two consoles standing on cbp's switchback runs.

    python patch_dc_cbp_consoles.py --check
    python patch_dc_cbp_consoles.py
    python patch_dc_cbp_consoles.py --selftest   (run it AFTER applying)
    python patch_dc_cbp_consoles.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

TWO STAIRS, ONE SHAPE OF DEFECT. `cbp_town_finale_midbalanced_schemafixed`
fails `nav_gate` on both of its switchbacks. A switchback's two runs meet at
the stair's own x, and each run is half the flight -- 2.20 m here. A volume
sitting on one run has to leave 0.80 m of it, which is what a Godot agent of
radius 0.40 needs to walk:

    stair_1   flight x  31.80 ..  36.20   runs meet at  34.00
              cash_counting_tables       x 26.50 .. 33.50
              -> descending run keeps 0.50 m.  Nothing bakes. Dead.

    stair_0   flight x -36.20 .. -31.80   runs meet at -34.00
              security_console_cluster   x -33.00 .. -27.00
              -> ascending run keeps 1.00 m.  A 0.20 m ribbon survives the
                 0.40 m erosion on each side, which at cell 0.10 is two cells
                 wide and entirely at the mercy of quantisation.

Both stairs report `no_path (endpoints on disjoint islands)`. 0.50 m is
unambiguous; 1.00 m is the more interesting one, because it is the width that
looks fine in a plan view and is not fine to a nav bake.

THE FIX.

    cash_counting_tables       x 30 -> 27     spans 23.50 .. 30.50
                                              1.30 m clear of the flight
    security_console_cluster   x -30 -> -27   spans -30.00 .. -24.00
                                              1.80 m clear of the flight

Both checked against every other volume that shares their footprint -- no
clashes. `x = 28` was the tighter option for the console and was rejected: it
collides with `security_keycard_wall_box`. Neither volume has a derived
`cover_from_volume` marker, so unlike `night_deli`'s planter there is nothing
else that has to travel with them.

WHY MOVE THE CONSOLES AND NOT THE STAIRS. These two stairs are the building's
egress cores -- they set the slab cuts and the discharge bridges on three
storeys. A console is a box with a collision hull. Move the thing whose
position nothing else depends on.

NOT VERIFIED BY A BAKE YET:

    python deli_counter\build.py deli_counter\specs\cbp_town_finale_midbalanced_schemafixed.json
    python deli_counter\nav_gate.py deli_counter\build\cbp_town_finale_midbalanced_schemafixed.glb
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter/specs/cbp_town_finale_midbalanced_schemafixed.json")
SIDECAR = ".pre_consoles"

OLD_CONSOLE = '''   "name": "security_console_cluster",
   "x": -30,'''

NEW_CONSOLE = '''   "name": "security_console_cluster",
   "x": -27,'''

OLD_TABLES = '''   "name": "cash_counting_tables",
   "x": 30,'''

NEW_TABLES = '''   "name": "cash_counting_tables",
   "x": 27,'''

EDITS = {TARGET: ((OLD_CONSOLE, NEW_CONSOLE), (OLD_TABLES, NEW_TABLES))}

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
    bad = 0
    for sd in spec.get("stairs") or []:
        fp = stair_core._core_of(spec, sd)["footprint"]
        # ONLY a switchback (and a scissor) has two runs meeting at the
        # stair's own x. A straight flight is one run the full width of its
        # footprint, and splitting it down the middle invents an obstruction
        # that is not there -- this selftest did exactly that on `stair_2`
        # and called a stair the engine passes a failure.
        split = sd.get("style", "switchback") in ("switchback", "scissor")
        seam = sd["x"] if split else None
        hits = []
        for v in spec.get("volumes") or []:
            vx0, vx1 = v["x"] - v["size_x"] / 2, v["x"] + v["size_x"] / 2
            vy0, vy1 = v["y"] - v["size_y"] / 2, v["y"] + v["size_y"] / 2
            if vx1 <= fp[0] or vx0 >= fp[2] or vy1 <= fp[1] or vy0 >= fp[3]:
                continue
            if split:
                asc = max(min(vx1, fp[2]) - max(vx0, seam), 0.0)
                desc = max(min(vx1, seam) - max(vx0, fp[0]), 0.0)
                fa, fd = (fp[2] - seam) - asc, (seam - fp[0]) - desc
                ok = fa >= AGENT and fd >= AGENT
                hits.append((ok, v["name"],
                             f"ascending {fa:.2f} m, descending {fd:.2f} m"))
            else:
                blocked = max(min(vx1, fp[2]) - max(vx0, fp[0]), 0.0)
                free = (fp[2] - fp[0]) - blocked
                ok = free >= AGENT
                hits.append((ok, v["name"],
                             f"leaves {free:.2f} m of {fp[2] - fp[0]:.2f}"))
            bad += 0 if ok else 1
        if hits:
            for ok, nm, why in hits:
                print(f"  {'ok  ' if ok else 'FAIL'} {sd['id'][:36]:<36} "
                      f"{nm:<26} {why}")
        else:
            print(f"  ok   {sd['id'][:36]:<36} nothing stands on either run")
    print()
    print("  both switchbacks are clear on both runs" if not bad
          else f"  {bad} run(s) still obstructed")
    print("  NOTE: spec arithmetic. Rebuild cbp and run nav_gate -- the bake\n"
          "  is the only thing that settles it.")
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
