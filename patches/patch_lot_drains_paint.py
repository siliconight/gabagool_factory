"""Lot 0.120.1: a storm inlet keeps clear of the paint -- none stands in a crosswalk (factory roadmap
179, found in cold run 9269's frames and measured by docs/cold_runs/cold_9269/drain_paint.py: four of
eight grates over a crosswalk bar, 0.155 m^2 each).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  site_drains.py             the rule in the docstring, `LINES_ALONG`, the paint helpers and
                             `_clear_station`, `plan(roads, cover, marks)`, the inlet's station
  tests/test_site_drains.py  `_plan` passes the paint; the inlet test asks "a hand from the stretch OR
                             from the paint"; `test_no_grate_stands_in_the_paint`
  lot.py                     `_outdoor_nodes` passes `marks`
CHANGELOG and VERSION from `lot_drains_paint/CHANGELOG_0.120.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. `--old-station` (with LOT_ROOT, a copy) applies everything but the station
rule, so the new test can be run against 0.120.0's placement with the helpers beside it.

Read before it was written, in this session: site_drains.py whole (0.120.0, the plan and its helpers),
tests/test_site_drains.py whole, lot.py's drains hook and the `marks` it draws three blocks above
(`site_streets.markings` + `site_fields.markings`, not reassigned between), `site_streets.markings` (the
edge line's offset, `has_parking`, the crosswalks and stop bars and their reach to 0.3 m off the kerb
face), `site_streets.crossing_walks`, `Road.point`/`a`/`along`, `site_furniture.corner_key` (quadrants:
a stepped grate keeps its corner) and `_clear_of_cuts`. Every file LF.

    python patches/patch_lot_drains_paint.py --results-pending
    (python -m pytest -q in lot)
    python patches/patch_lot_drains_paint.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_drains_paint"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
OLD_STATION = "--old-station" in sys.argv
RESULTS = {"RESULT_PLAN": "result_plan.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.120.0", b"Lot 0.120.1"
CHANGELOG_HEAD = "## 0.120.0 - the street's drains: manhole covers and storm inlets\n"
SHA = {"lot.py": "a1aa988f472a31f0", "site_drains.py": "0a0bff381147cc75",
       "tests/test_site_drains.py": "aee56dba3b53d64a"}

DRAINS = [
    # the rule, in the module's docstring
    ("  * A storm inlet upstream of a crosswalk and its ramp, so the water is taken before it crosses where\n"
     "    people walk (TxDOT Hydraulic Design Manual, ch. 10 s. 5): in the gutter against the kerb, on the\n"
     "    block side of a junction's cut, ONE A CORNER as the hydrant is (`site_furniture.CORNER_ONE_EACH`) --\n"
     "    the walker's \"only so many\". Inlets between corners follow the gutter's spread, which needs the\n"
     "    street's grade and a design storm a site has not got: not placed.\n",
     "  * A storm inlet upstream of a crosswalk and its ramp, so the water is taken before it crosses where\n"
     "    people walk (TxDOT Hydraulic Design Manual, ch. 10 s. 5): in the gutter against the kerb, on the\n"
     "    block side of a junction's cut, ONE A CORNER as the hydrant is (`site_furniture.CORNER_ONE_EACH`) --\n"
     "    the walker's \"only so many\". Upstream of the PAINTED crosswalk too (0.120.1): a through road's\n"
     "    crosswalks at a T lie in line with the side street's sidewalks, outside the kerb's dropped\n"
     "    stretch, and 0.120.0 stood four of cold run 9269's eight grates over a crosswalk's bar; a grate\n"
     "    is stepped along the kerb, away from the junction, until it keeps `INLET_CLEAR` from every\n"
     "    marking but the lines along a road (`LINES_ALONG`). Inlets between corners follow the gutter's\n"
     "    spread, which needs the street's grade and a design storm a site has not got: not placed.\n"),
    # the clearance, and the paint it is not asked of
    ("#: from the edge of a junction's cut to the grate's near end: a hand, clear of the ramp\n"
     "INLET_CLEAR = 0.3\n",
     "#: from the edge of a junction's cut to the grate's near end: a hand, clear of the ramp; and the\n"
     "#: least a grate keeps from the paint (0.120.1)\n"
     "INLET_CLEAR = 0.3\n"
     "#: the paint a grate does NOT keep clear of: the lines along a road. A crosswalk is the TxDOT rule's\n"
     "#: own subject, and a stop bar and a bay's tick run across the gutter; but on a street too narrow to\n"
     "#: park on, the edge line runs in the gutter (`site_streets.has_parking`, `EDGE_INSET`), and clearing\n"
     "#: it would place no inlet on that street at all -- the grate is drawn over it\n"
     "LINES_ALONG = (\"centre_line\", \"edge_line\")\n"
     "#: a station stepped to exactly `INLET_CLEAR` from a bar is asked again with this allowed: the step\n"
     "#: and the test are two spellings of one distance, and a float a hair short of it would hold the\n"
     "#: grate where it stands until the search gave up\n"
     "CLEAR_EPS = 1e-6\n"),
    # the helpers, and the plan's signature
    ("        if abs(at[0] - pat[0]) < hx and abs(at[1] - pat[1]) < hy:\n"
     "            return True\n"
     "    return False\n"
     "\n"
     "\n"
     "def plan(roads_list, cover=()):\n"
     "    \"\"\"The site's drains: a list of records, each ``kind`` \"manhole\", \"inlet\" or \"walk_cover\", with\n"
     "    ``at`` (plan), ``yaw`` (degrees, the road's) and ``road``; an inlet also carries ``face`` -- the\n"
     "    point on the kerb face behind its centre -- and ``toward``, the unit plan vector from the kerb face\n"
     "    to the road. ``cover`` is the site's furniture and cover, which a sidewalk lid keeps clear of.\"\"\"\n"
     "    out = []\n",
     "        if abs(at[0] - pat[0]) < hx and abs(at[1] - pat[1]) < hy:\n"
     "            return True\n"
     "    return False\n"
     "\n"
     "\n"
     "def _paint(m):\n"
     "    \"\"\"A marking's plan rectangle (`site_streets._marking`'s record: ``size`` [along, across] at\n"
     "    ``at``, turned by ``yaw`` degrees), its centre, and the radius that holds it.\"\"\"\n"
     "    (cx, cy), (along, across) = m[\"at\"], m[\"size\"]\n"
     "    turn = _rot(cx, cy, m[\"yaw\"])\n"
     "    poly = [turn(-along / 2.0, -across / 2.0), turn(along / 2.0, -across / 2.0),\n"
     "            turn(along / 2.0, across / 2.0), turn(-along / 2.0, across / 2.0)]\n"
     "    return poly, (cx, cy), math.hypot(along, across) / 2.0\n"
     "\n"
     "\n"
     "def _grate(road, kerb, face, t):\n"
     "    \"\"\"An inlet's plan footprint at station ``t``: `INLET_L` along the kerb face, `INLET_D` out into\n"
     "    the road.\"\"\"\n"
     "    out = face - kerb.sign * INLET_D\n"
     "    return [road.point(t - INLET_L / 2.0, face), road.point(t + INLET_L / 2.0, face),\n"
     "            road.point(t + INLET_L / 2.0, out), road.point(t - INLET_L / 2.0, out)]\n"
     "\n"
     "\n"
     "def _meet(a, b):\n"
     "    \"\"\"Whether two convex polygons share a point: no edge of either separates them.\"\"\"\n"
     "    for poly in (a, b):\n"
     "        for i in range(len(poly)):\n"
     "            (x0, y0), (x1, y1) = poly[i - 1], poly[i]\n"
     "            nx, ny = y1 - y0, x0 - x1\n"
     "            pa = [nx * x + ny * y for x, y in a]\n"
     "            pb = [nx * x + ny * y for x, y in b]\n"
     "            if max(pa) < min(pb) or max(pb) < min(pa):\n"
     "                return False\n"
     "    return True\n"
     "\n"
     "\n"
     "def _seg_dist(p, a, b):\n"
     "    dx, dy = b[0] - a[0], b[1] - a[1]\n"
     "    ll = dx * dx + dy * dy\n"
     "    s = 0.0 if ll == 0.0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ll))\n"
     "    return math.hypot(p[0] - a[0] - s * dx, p[1] - a[1] - s * dy)\n"
     "\n"
     "\n"
     "def _gap(a, b):\n"
     "    \"\"\"The distance between two convex polygons, 0 where they meet: from a corner to an edge, never\n"
     "    a margin added per axis, which is a box and over-reports by up to sqrt(2) times it at a corner.\"\"\"\n"
     "    if _meet(a, b):\n"
     "        return 0.0\n"
     "    return min(_seg_dist(p, q[i - 1], q[i]) for r, q in ((a, b), (b, a)) for p in r\n"
     "               for i in range(len(q)))\n"
     "\n"
     "\n"
     "def _clear_station(road, kerb, face, t, side, paint):\n"
     "    \"\"\"The first station from ``t`` along the kerb, away from the junction (``side``), where the\n"
     "    grate keeps `INLET_CLEAR` from all of ``paint`` (`_paint` records): every marking nearer than\n"
     "    that is stepped past whole along the road, and the station asked again. None when the road ends\n"
     "    first.\"\"\"\n"
     "    reach = math.hypot(INLET_L, INLET_D) / 2.0 + INLET_CLEAR\n"
     "    for _ in range(64):\n"
     "        if not (0.0 < t - INLET_L / 2.0 and t + INLET_L / 2.0 < road.length):\n"
     "            return None\n"
     "        grate = _grate(road, kerb, face, t)\n"
     "        gx, gy = road.point(t, face - kerb.sign * INLET_D / 2.0)\n"
     "        near = [poly for poly, (cx, cy), r in paint\n"
     "                if math.hypot(cx - gx, cy - gy) < r + reach\n"
     "                and _gap(grate, poly) < INLET_CLEAR - CLEAR_EPS]\n"
     "        if not near:\n"
     "            return t\n"
     "        ts = [(x - road.a[0]) * road.along[0] + (y - road.a[1]) * road.along[1]\n"
     "              for poly in near for x, y in poly]\n"
     "        if side > 0:\n"
     "            t = max(t, max(ts) + INLET_CLEAR + INLET_L / 2.0)\n"
     "        else:\n"
     "            t = min(t, min(ts) - INLET_CLEAR - INLET_L / 2.0)\n"
     "    return None\n"
     "\n"
     "\n"
     "def plan(roads_list, cover, marks):\n"
     "    \"\"\"The site's drains: a list of records, each ``kind`` \"manhole\", \"inlet\" or \"walk_cover\", with\n"
     "    ``at`` (plan), ``yaw`` (degrees, the road's) and ``road``; an inlet also carries ``face`` -- the\n"
     "    point on the kerb face behind its centre -- and ``toward``, the unit plan vector from the kerb face\n"
     "    to the road. ``cover`` is the site's furniture and cover, which a sidewalk lid keeps clear of;\n"
     "    ``marks`` the paint the site draws (`site_streets.markings` and the fields'), which a grate keeps\n"
     "    clear of -- both asked for, so no caller leaves either out unnoticed (0.120.1).\"\"\"\n"
     "    out = []\n"
     "    paint = [_paint(m) for m in marks if m.get(\"kind\") not in LINES_ALONG]\n"),
]
#: the station rule itself, kept apart so `--old-station` can leave it out of a copy
STATION = (
    "                for side in (-1, 1):\n"
    "                    edge = hi if side > 0 else lo\n"
    "                    t = edge + side * (INLET_CLEAR + INLET_L / 2.0)\n"
    "                    if not (0.0 < t - INLET_L / 2.0 and t + INLET_L / 2.0 < road.length):\n"
    "                        continue\n"
    "                    if not site_furniture._clear_of_cuts(t, INLET_L / 2.0, kerb, 0.0):\n"
    "                        continue\n",
    "                for side in (-1, 1):\n"
    "                    edge = hi if side > 0 else lo\n"
    "                    # a hand past the dropped stretch, and on past any paint (0.120.1)\n"
    "                    t = _clear_station(road, kerb, face, edge + side * (INLET_CLEAR + INLET_L / 2.0),\n"
    "                                       side, paint)\n"
    "                    if t is None:\n"
    "                        continue\n"
    "                    if not site_furniture._clear_of_cuts(t, INLET_L / 2.0, kerb, 0.0):\n"
    "                        continue\n")

TESTS = [
    ("def _plan(rr):\n"
     "    roads = _roads(rr)\n"
     "    cover = site_furniture.plan_furniture(roads, [])\n"
     "    return roads, cover, site_drains.plan(roads, cover)\n",
     "def _plan(rr):\n"
     "    roads = _roads(rr)\n"
     "    cover = site_furniture.plan_furniture(roads, [])\n"
     "    return roads, cover, site_drains.plan(roads, cover, site_streets.markings(roads))\n"),
    ("    for rr, corners in ((X_ROADS, 4), (T_ROADS, None)):\n"
     "        roads, _cover, pieces = _plan(rr)\n"
     "        inlets = _of(pieces, \"inlet\")\n",
     "    for rr, corners in ((X_ROADS, 4), (T_ROADS, None)):\n"
     "        roads, _cover, pieces = _plan(rr)\n"
     "        painted = [site_drains._paint(m)[0] for m in site_streets.markings(roads)\n"
     "                   if m[\"kind\"] not in site_drains.LINES_ALONG]\n"
     "        inlets = _of(pieces, \"inlet\")\n"),
    ("            # next to a junction's cut: its near end a hand from the dropped stretch's edge\n"
     "            near = min(min(abs(p[\"t\"] - lo), abs(p[\"t\"] - hi))\n"
     "                       for lo, hi in (site_drains._cut_span(kerb, c) for c in kerb.cuts if c.kind == \"road\"))\n"
     "            # (a piece's station is kept to the millimetre)\n"
     "            assert abs(near - site_drains.INLET_L / 2.0 - site_drains.INLET_CLEAR) < 6e-4, near\n",
     "            # next to a junction's cut: its near end at least a hand from the dropped stretch's\n"
     "            # edge, and exactly a hand from that edge or from the paint -- as near the junction as\n"
     "            # both let it stand (0.120.1; a piece's station is kept to the millimetre)\n"
     "            near = min(min(abs(p[\"t\"] - lo), abs(p[\"t\"] - hi))\n"
     "                       for lo, hi in (site_drains._cut_span(kerb, c) for c in kerb.cuts if c.kind == \"road\"))\n"
     "            assert near - site_drains.INLET_L / 2.0 - site_drains.INLET_CLEAR > -6e-4, near\n"
     "            grate = site_drains._grate(road, kerb, face, p[\"t\"])\n"
     "            paint = min(site_drains._gap(grate, q) for q in painted)\n"
     "            assert (abs(near - site_drains.INLET_L / 2.0 - site_drains.INLET_CLEAR) < 6e-4\n"
     "                    or abs(paint - site_drains.INLET_CLEAR) < 6e-4), (near, paint)\n"),
    ("def test_a_sidewalk_lid_a_step_behind_an_inlet_and_only_so_many():\n",
     "def test_no_grate_stands_in_the_paint():\n"
     "    \"\"\"0.120.1: a grate keeps `INLET_CLEAR` from every marking but the lines along a road. On\n"
     "    0.120.0 the through road's grates at a T lay over its crosswalk's bars (cold run 9269: four of\n"
     "    eight, 0.155 m^2 each): its crosswalks lie in line with the side street's sidewalks, outside the\n"
     "    kerb's dropped stretch the grate was placed against.\"\"\"\n"
     "    for rr in (X_ROADS, T_ROADS):\n"
     "        roads, _cover, pieces = _plan(rr)\n"
     "        by = {r.index: r for r in roads}\n"
     "        painted = [(m, site_drains._paint(m)[0]) for m in site_streets.markings(roads)\n"
     "                   if m[\"kind\"] not in site_drains.LINES_ALONG]\n"
     "        assert [m for m, _q in painted if m[\"kind\"] == \"crosswalk_bar\"]\n"
     "        assert [m for m, _q in painted if m[\"kind\"] == \"stop_bar\"]\n"
     "        inlets = _of(pieces, \"inlet\")\n"
     "        assert inlets\n"
     "        for p in inlets:\n"
     "            road = by[p[\"road\"]]\n"
     "            kerb = road.kerb(p[\"kerb\"])\n"
     "            grate = site_drains._grate(road, kerb, site_drains._face_offset(road, kerb), p[\"t\"])\n"
     "            for m, q in painted:\n"
     "                # (a piece's station is kept to the millimetre)\n"
     "                gap = site_drains._gap(grate, q)\n"
     "                assert gap > site_drains.INLET_CLEAR - 6e-4, (p[\"at\"], m[\"kind\"], m[\"at\"], gap)\n"
     "\n"
     "\n"
     "def test_a_sidewalk_lid_a_step_behind_an_inlet_and_only_so_many():\n"),
]

HOOK = [
    ("    # the art only, as the wires are: a candidate's greybox lot carries none.\n"
     "    if cover_refs:\n"
     "        import site_drains\n"
     "        drains = site_drains.plan(street_roads, site_spec.get(\"cover\") or [])\n",
     "    # the art only, as the wires are: a candidate's greybox lot carries none.\n"
     "    # A grate keeps clear of the paint drawn above (`marks`, 0.120.1).\n"
     "    if cover_refs:\n"
     "        import site_drains\n"
     "        drains = site_drains.plan(street_roads, site_spec.get(\"cover\") or [], marks)\n"),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.120.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.120.1: results filled")


def main():
    if FILL:
        return fill()
    if OLD_STATION and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --old-station is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.120.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.120.1 - "), entry[:40]
    left = entry
    for key in RESULTS if (PENDING or OLD_STATION) else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    edits = {"site_drains.py": DRAINS + ([] if OLD_STATION else [STATION]),
             "tests/test_site_drains.py": TESTS, "lot.py": HOOK}
    writes = {}
    for rel, pairs in edits.items():
        p = LOT / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.120.0 -> 0.120.1" + (" (OLD STATION, a copy)" if OLD_STATION else ""))


if __name__ == "__main__":
    main()
