"""Deli Counter 0.198.0: VERSION and CHANGELOG for the z-fight gate's facing rule.

    python patch_dc_0198_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.198.0] - the z-fight gate judges a pair by the side its faces face: 436 pairs were 5

**The measurement** (roadmap 177's open question: nobody had looked at the
pairs). Cold run 9189's composed buildings, by `zfight_gate`'s own raw
pairs:

| building | visible, 0.197.0's rule | buried by it | visible by what the faces face |
|---|---|---|---|
| deli_a01 | 198 | 19 | **2** |
| office | 121 | 0 | **2** |
| rail_station_a02 | 117 | 0 | **1** |

Nearly every pair was two bottoms on one plane, facing down into a slab:
- a chair, a counter or a stool and the floor module it stands in;
- a stair tread and the stairwell's floor module.

No camera can reach either face of such a pair. The rule buried a pair only
inside a solid with matter on BOTH sides of the plane, which holds for a
face inside a wall band and never for one pressed against a slab.

**The rule.** A same-facing pair can be seen only from the side its faces
face. `visible_fights` now buries it when solids starting within
`OUTWARD_GAP` of the plane on that side, and reaching `OCCLUDE_MARGIN` past
it, cover the shared rectangle.
- `OUTWARD_GAP` is the composer's own wall-family sink
  (`themed_tscn.SLAB_CAP_SINK`, mirrored and pinned by a test) plus the
  gate's tolerance: 5.5 mm. That shuts the caps the composer sinks 4 mm
  under the slab above them. A 5 cm gap read the same.
- Matter on both sides is matter on the facing side, so every pair the old
  rule buried, this one buries too. All 12 old tests pass unchanged.

**The cover is 2-D now** (`_rect_covered`, replacing the 1-D
`_union_covers`).
- The 1-D union needed one box to span the shared rectangle across, so four
  slab tiles meeting in a corner under a desk read as uncovered.
- **The tolerance is load-bearing.** 9189's slab tiles meet at -9.333000183
  and -9.332999944, a float32 seam of 2.4e-7 m. **Refuted, kept:** the
  census's first 2-D cover had no tolerance and called every seam a hole,
  leaving 31 of deli_a01's pairs; the gate's own 1-D union had always
  carried `tol`.

**The 5 left are worth a frame.**
- **deli_a01 (2) and rail_station_a02 (1):** a partition's end runs into
  the exterior wall where one wall segment is exactly the partition's
  width, so their faces share a plane at the junction. Where the next
  segment is a window opening, the faces show on the jamb.
- **office (2):** the reception desk stands on a greybox ledge of exactly
  its width, and their sides are coplanar, facing the room.

**Tests:** `test_zfight_gate.py` +8.
- Five failed before the change: bottoms pressed on a slab, float32 seams
  between tiles, a 2 x 2 corner of tiles, caps sunk under the next slab,
  and the gap's derivation.
- Three guards pass either side of it, so the rule cannot hide too much:
  the same bottoms with nothing under them, a rug on the floor, and the
  office's flush desk.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.197.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.197.0] - open floor is a way in"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.198.0")
    print("Deli Counter 0.198.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
