"""Lot 0.102.2: a parking meter's windows face across the kerb, one to the sidewalk.

Roadmap 219, the walker's note 4: "street parking payment 'boxes' should face toward the
sidewalk, rotating 90 Degrees". Zoo's `parking_meter` carries a display window on each wide
face, at its +-Y; `plan_meters` stood every meter at the road's angle + 90, which points those
faces along the street (`plate_facing(yaw) . road.along` = +-1, measured on the kerb probe).
At + 0 they point across it, one to the sidewalk and one to the bay, on either kerb: the head
is two-faced, so no kerb needs turning round.

Anchored edits, every anchor once, nothing written until all matched:
- `site_furniture.py`: `plan_meters` passes `yaw_extra` 0.0;
- `tests/test_site_furniture.py`: `test_a_meter_faces_across_the_kerb`.
CHANGELOG and VERSION from `lot_meters_face_kerb/CHANGELOG_0.102.2.md`.

    python patch_lot_meters_face_kerb.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = HERE.parent / "lot"
SRC = HERE / "lot_meters_face_kerb"

FIX_OLD = (
    "        piece = _piece(f\"Meter_{road.index}{bay['side']}{bay['index']}\",\n"
    "                       \"parking_meter\", road, kerb, t, offset, 90.0,\n"
    "                       breaks=f\"bay {bay['side']}{bay['index']}\")\n"
)
FIX_NEW = (
    "        # FACING ACROSS THE KERB (0.102.2). Zoo's meter has a display window\n"
    "        # on each wide face, its +-Y; at the road's angle those look across\n"
    "        # the kerb, one to the sidewalk and one to the bay, on either side.\n"
    "        # 0.102.1 and before added 90 and pointed them along the street --\n"
    "        # the walker: \"should face toward the sidewalk, rotating 90 Degrees\".\n"
    "        piece = _piece(f\"Meter_{road.index}{bay['side']}{bay['index']}\",\n"
    "                       \"parking_meter\", road, kerb, t, offset, 0.0,\n"
    "                       breaks=f\"bay {bay['side']}{bay['index']}\")\n"
)
TEST_ANCHOR = (
    "    for m in meters:\n"
    "        assert m[\"species\"] == \"parking_meter\" and m[\"base\"] == \"sidewalk\"\n"
    "        # on the band, nearer the road than a lamp is\n"
    "        assert 5.0 <= abs(m[\"at\"][1]) <= 6.0, m\n"
)
TEST_NEW = (
    TEST_ANCHOR
    + "\n"
    "\n"
    "def test_a_meter_faces_across_the_kerb():\n"
    "    \"\"\"FAILS ON 0.102.1. Zoo's meter shows a window on each wide face; the\n"
    "    walker wants one of them to the sidewalk, so both look across the kerb:\n"
    "    the face's plan direction is square to the road on either side. 0.102.1\n"
    "    stood them at the road's angle + 90, faces along the street.\"\"\"\n"
    "    (road,) = site_streets.roads(_probe())\n"
    "    meters = site_furniture.plan_meters(road)\n"
    "    assert {m[\"kerb\"] for m in meters} == {\"L\", \"R\"}\n"
    "    for m in meters:\n"
    "        fx, fy = site_furniture.plate_facing(m[\"yaw\"])\n"
    "        along = fx * road.along[0] + fy * road.along[1]\n"
    "        across = fx * road.perp[0] + fy * road.perp[1]\n"
    "        assert abs(along) < 1e-6 and abs(abs(across) - 1.0) < 1e-6, m\n"
)

EDITS = {
    "site_furniture.py": [(FIX_OLD, FIX_NEW)],
    "tests/test_site_furniture.py": [(TEST_ANCHOR, TEST_NEW)],
}


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.102.1", v
    entry = (SRC / "CHANGELOG_0.102.2.md").read_text(encoding="utf-8")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    staged = {}
    for rel, pairs in EDITS.items():
        p = LOT / rel
        d = p.read_bytes()
        assert b"\r\n" not in d, (rel, "has CRLF; this patch writes LF files")
        t = d.decode("utf-8")
        assert "FACING ACROSS THE KERB" not in t and "test_a_meter_faces_across" not in t, \
            (rel, "already applied")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.102.2" not in d and d.startswith(b"## 0.102.1")
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes(entry.encode("utf-8").replace(b"\r\n", b"\n") + b"\n" + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.102.2")
    print("Lot 0.102.1 -> 0.102.2")


if __name__ == "__main__":
    main()
