"""Lot 0.102.1: the bus stop stands on its band before the corner is spaced against it.

Roadmap 219, note 6: cold run 9213 stood a news rack 0.11 m from the stop's flag post and
another over the shelter's end. `plan_furniture` never added `_bus_stop`'s pieces to the
band's `placed`, so `_stop_corner`'s `_free` -- and the hydrant passes after it -- could not
see them.

Anchored edits, every anchor once, nothing written until all matched:
- `site_furniture.py`: `placed.extend(stop)` after `_bus_stop`, before `_stop_corner`;
- `tests/test_site_furniture.py`: `test_no_stop_corner_piece_stands_on_the_stop`, after
  `test_the_stop_corner_stands_at_the_bus_stop`.
CHANGELOG and VERSION from `lot_stop_on_band/CHANGELOG_0.102.1.md`.

    python patch_lot_stop_on_band.py
    LOT_ROOT=<copy> python patch_lot_stop_on_band.py [--draft]
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_stop_on_band"
DRAFT = "--draft" in sys.argv

FIX_OLD = (
    "                stop = _bus_stop(road, kerb, placed, n, markers)\n"
    "                n += len(stop)\n"
    "                out.extend(stop)\n"
    "                out.extend(_stop_corner(road, kerb, stop, placed, markers))\n"
)
FIX_NEW = (
    "                stop = _bus_stop(road, kerb, placed, n, markers)\n"
    "                n += len(stop)\n"
    "                out.extend(stop)\n"
    "                # THE STOP STANDS ON THE BAND (0.102.1): its shelter, bench and\n"
    "                # flag join `placed` before anything is spaced against them.\n"
    "                # They did not, so `_stop_corner`'s `_free` could not see\n"
    "                # them, nor could the hydrant passes that read this band's\n"
    "                # `placed` -- cold run 9213 stood a news rack 0.11 m from the\n"
    "                # flag post and another over the shelter's end, both nudged\n"
    "                # there off stations a marker or a tree had taken.\n"
    "                placed.extend(stop)\n"
    "                out.extend(_stop_corner(road, kerb, stop, placed, markers))\n"
)

TEST_ANCHOR = (
    "    for sp in (\"mailbox\", \"newspaper_box\", \"payphone\"):\n"
    "        for p in by[sp]:\n"
    "            assert p[\"kerb\"] == shelter[\"kerb\"]\n"
    "            assert abs(p[\"t\"] - shelter[\"t\"]) < 12.0, p\n"
    "            assert p[\"breaks\"].startswith(\"stop@\")\n"
)
TEST_NEW = (
    TEST_ANCHOR
    + "\n"
    "\n"
    "def _rects_meet(a, b):\n"
    "    ra, rb = site_furniture._piece_rect(a), site_furniture._piece_rect(b)\n"
    "    return ra[0] < rb[2] and rb[0] < ra[2] and ra[1] < rb[3] and rb[1] < ra[3]\n"
    "\n"
    "\n"
    "def test_no_stop_corner_piece_stands_on_the_stop():\n"
    "    \"\"\"FAILS ON 0.102.0. The stop's shelter, bench and flag never reached the\n"
    "    band's `placed`, so the mailbox, the news racks and the payphone were\n"
    "    spaced against everything but the stop. Cold run 9213 stood a rack 0.11 m\n"
    "    from the flag post and another over the shelter's end, both nudged there\n"
    "    off a station something else had taken. One marker swept along the stop's\n"
    "    band, 81 positions 0.25 m apart, finds both on the probe: 22 overlaps on\n"
    "    0.102.0.\"\"\"\n"
    "    spec = _probe()\n"
    "    roads = site_streets.roads(spec)\n"
    "    shelter = next(p for p in site_furniture.plan_furniture(roads, spec[\"buildings\"])\n"
    "                   if p[\"species\"] == \"bus_shelter\")\n"
    "    x0, y = shelter[\"at\"]\n"
    "    seen = 0\n"
    "    for i in range(-60, 21):\n"
    "        pieces = site_furniture.plan_furniture(roads, spec[\"buildings\"],\n"
    "                                               markers=[(x0 + i * 0.25, y)])\n"
    "        stop = [p for p in pieces if p[\"species\"] == \"bus_shelter\"\n"
    "                or (p[\"species\"] == \"sign_post\" and p[\"breaks\"].startswith(\"stop@\"))]\n"
    "        corner = [p for p in pieces\n"
    "                  if p[\"species\"] in (\"mailbox\", \"newspaper_box\", \"payphone\")]\n"
    "        seen += len(corner)\n"
    "        for c in corner:\n"
    "            for s in stop:\n"
    "                assert not _rects_meet(c, s), (i, c[\"name\"], s[\"species\"], c[\"at\"], s[\"at\"])\n"
    "    # the sweep tested something: the corner still stands somewhere\n"
    "    assert seen > 0\n"
)

EDITS = {
    "site_furniture.py": [(FIX_OLD, FIX_NEW)],
    "tests/test_site_furniture.py": [(TEST_ANCHOR, TEST_NEW)],
}


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        raise SystemExit("--draft writes a copy: set LOT_ROOT")
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.102.0", v
    entry = (SRC / "CHANGELOG_0.102.1.md").read_text(encoding="utf-8")
    assert DRAFT or "RESULT_" not in entry, "the changelog still carries an unfilled result"
    staged = {}
    for rel, pairs in EDITS.items():
        p = LOT / rel
        d = p.read_bytes()
        assert b"\r\n" not in d, (rel, "has CRLF; this patch writes LF files")
        t = d.decode("utf-8")
        assert "THE STOP STANDS ON THE BAND" not in t and "test_no_stop_corner_piece" not in t, \
            (rel, "already applied")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.102.1" not in d and d.startswith(b"## 0.102.0")
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes(entry.encode("utf-8").replace(b"\r\n", b"\n") + b"\n" + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.102.1")
    print("Lot 0.102.0 -> 0.102.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
