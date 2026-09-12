"""Roadmap batch 21, 2026-09-11: item 139 narrowed by Lux 0.33.0, with the
refutation of its own first claim kept. REPLACE mode; the old status block
is kept verbatim inside the new one. Asserts the anchor matches once.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD = """*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON; THE RESIDUE LUX 0.30.1 WROTE
DOWN, NOW SEEN*

**139. The sign is a white box with a white square standing off it.**"""

NEW = """*STATUS: NARROWED 2026-09-11 -- THE SQUARE IS FIXED (LUX 0.33.0) AND ITS
CAUSE WAS NOT THE ONE THIS ITEM NAMED; THE BOX IS MEASURED AND NOT FIXED.
REFUTED, kept above what replaced it: the body says Zoo writes the marker
"with a translation only (`build.py:661`)". It does not -- `build.py` has
stamped the anchor's `rot_z` on the marker (`Translation @ rot`) since the
markers existed, and `LuxFixtureSpawner` copies the marker's whole
transform. The saved rig in the walked copy has an identity basis because
the sign's `rot_y` IS 0. What was missing was the QUARTER TURN: the marker's
facing is its local +X, an area rig faces local +Z, and `_place` (Lux
0.30.1, f = t + 90) had it while the spawner did not. Lux 0.33.0: the
spawner applies the same turn to area rigs, turns the rig's preview quad
off under spawned hardware (the cabinet carries its own `M_SignBox_Face`;
the quad through it was the square), and `rig_for_anchor("sign")` stands
the source 0.29 m ahead of the face -- the anchor is the face plane, Zoo
mounts `sign_box` centred on it, 0.18 m deep, so the omni sat inside the
cabinet 0.09 m from a 0.28-grey box at energy 3.0. `colocation_selftest`
case E holds the facing (dot 1.0) and the absence of the quad. MEASURED on
the walked copy, its fixtures re-spawned with the 0.33.0 runtime and
`look_shots --station` at the sign from the street and from along the
wall: the square is gone from the along-wall frame; the bar above the door
is white in BOTH frames -- 27.3% of the sign crop at >= 250 before, 34.5%
after, the same 250 x 50 px bounding box -- so the "white box" is not the
lamp lighting the cabinet, it is the FACE'S OWN EMISSION: Zoo's sign
recipe gives it `emissive_strength` 2.2 (its style default) over the whole
3.0 x 0.6 panel, which clips to white at Lux's exposure with no text or
pack detail surviving. CONFOUND, named: the two frames ran different Lux
runtimes (the walk copy's vendored pre-0.32 addon before, 0.33.0 after),
and the after frame is darker overall with a flat sky -- crushed 13% ->
62% -- which is the runtime refresh, not the spawner; the only node the
re-pack dropped is the quad. **WHAT WOULD CLOSE THIS:** the sign face's
emission against the tonemap -- a Zoo sign style row, measured by the
near-clip figure of this station, so the pack's colour and text read
instead of a white slab; then the re-walk. EARLIER STATUS, KEPT VERBATIM:
OPEN 2026-09-11 -- FOUND BY A PERSON; THE RESIDUE LUX 0.30.1 WROTE DOWN,
NOW SEEN*

**139. The sign is a white box with a white square standing off it.**"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); item 139 narrowed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
