"""Lot 0.118.1: a line's runs start clear of the kerb's own cut span, and a signal keeps its arms'
box rather than a 5 m circle -- so the corner pole beside a signalised T stands (factory roadmap
240; cold run 9262's west side street lost it).

Anchored edits, each asserted once, nothing written until all of them matched:
  site_poles.py             `_runs` from the kerb's spans; the signal's 5 m circle gone, its box in
                            `_room` (the refuted radius kept in the comment)
  tests/test_site_poles.py  one test appended, on cold run 9262's roads
CHANGELOG and VERSION from `lot_pole_corner/CHANGELOG_0.118.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: cold run 9262's drawn spec re-planned, its west side street's first
station refused step by step (a cut at 6.45, then `Signal_1L_0` at every step to 12.45), and the
kerb's spans against its cut records (0.0 to 5.6 against a 10 m cut at 0: `CUT_MARGIN`).

    python patches/patch_lot_pole_corner.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_pole_corner.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_pole_corner.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_pole_corner"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.118.0", b"Lot 0.118.1"
CHANGELOG_HEAD = ("## 0.118.0 - the pole line: one kerb of every street carries wooden utility "
                  "poles, and the poles carry its lamps\n")
POLES = "site_poles.py"
TEST = "tests/test_site_poles.py"
SHA = {POLES: "b2012df2464ab47d"}

RUNS_OLD = '''    """``[(t0, t1)]``: the stretches of this kerb a line runs along, broken
    at each ROAD crossing (a junction mouth, which a span crosses between the
    corner poles each side of it) and trimmed back from every cut's edge. A
    path's or a driveway's cut does not break a run: a pole steps off it."""
    half = POLE_FOOTPRINT[0] / 2.0
    pad = F.CUT_CLEARANCE + END_GAP + half
    edges = [0.0]
    for c in sorted(kerb.cuts, key=lambda c: c.t):
        if c.kind == "road":
            edges += [c.t - c.span / 2.0, c.t + c.span / 2.0]
    edges.append(road.length)
'''
RUNS_NEW = '''    """``[(t0, t1)]``: the stretches of this kerb a line runs along, broken
    at each ROAD crossing (a junction mouth, which a span crosses between the
    corner poles each side of it) and trimmed back from every cut's edge. A
    path's or a driveway's cut does not break a run: a pole steps off it.

    THE KERB'S SPAN, NOT THE CUT'S WIDTH (0.118.1). A cut stands on its kerb
    as its width and `site_streets.CUT_MARGIN` either side (`split_span`), and
    `site_furniture._clear_of_cuts` reads that span. 0.118.0 trimmed the runs
    from the width alone, so every run's first station stood inside the span's
    clearance and was refused as a cut: cold run 9262's west side street, its
    span 0.0 to 5.6 for a 10 m crossing at 0, lost its corner pole that way --
    with the 5 m circle a signal kept refusing every step off it."""
    half = POLE_FOOTPRINT[0] / 2.0
    pad = F.CUT_CLEARANCE + END_GAP + half
    crossings = [c.t for c in kerb.cuts if c.kind == "road"]
    edges = [0.0]
    for t0, t1, is_cut in kerb.spans:
        if is_cut and any(t0 - 1e-9 <= ct <= t1 + 1e-9 for ct in crossings):
            edges += [t0, t1]
    edges.append(road.length)
'''
SIGNAL_OLD = '''#: A traffic signal's arms reach 5 m over the road one way and 3 m the other
#: at 6 to 6.5 m up (Zoo `traffic_signal`, 8 m tip to tip); a pole stands
#: clear of the whole reach, so no cobra-head crosses a mast arm.
SIGNAL_CLEAR = 5.0
'''
SIGNAL_NEW = '''#: A TRAFFIC SIGNAL KEEPS ITS ARMS' BOX (0.118.1). Its module is 8 m of arm
#: along its yaw -- 5 m of mast over the road it meets, 3 m of luminaire arm
#: the other way, at 6 to 6.5 m up -- and 0.62 m across (Zoo `traffic_signal`),
#: so a pole conflicts with it only inside that box. REFUTED, KEPT: 0.118.0
#: kept a 5 m circle round the signal's pole, `SIGNAL_CLEAR`. A signal stands
#: on the furniture line, 1.94 m across the band from the pole line, and the
#: circle refused a corner pole that would have stood 1.63 m clear of the arms
#: (cold run 9262's west side street, `Signal_1L_0` at station 8.40).
'''
ROOM_DOC_OLD = ("    stands in a tree; a signal keeps `SIGNAL_CLEAR`.\"\"\"\n")
ROOM_DOC_NEW = ("    stands in a tree; a signal keeps its arms' box, grown by the pole's\n"
                "    radius and the gap, in its own frame.\"\"\"\n")
ROOM_SIGNAL_OLD = ('        if sp == "traffic_signal":\n'
                   "            if math.hypot(px - ox, py - oy) < SIGNAL_CLEAR:\n"
                   "                return False\n"
                   "            continue\n")
ROOM_SIGNAL_NEW = ('        if sp == "traffic_signal":\n'
                   '            w, d = float(o["dims"][0]), float(o["dims"][1])\n'
                   '            a = math.radians(float(o.get("yaw") or 0.0))\n'
                   "            dx, dy = px - ox, py - oy\n"
                   "            lx = dx * math.cos(a) + dy * math.sin(a)\n"
                   "            ly = -dx * math.sin(a) + dy * math.cos(a)\n"
                   "            if (abs(lx) < w / 2.0 + r + F.PIECE_GAP\n"
                   "                    and abs(ly) < d / 2.0 + r + F.PIECE_GAP):\n"
                   "                return False\n"
                   "            continue\n")


FURNITURE = "site_furniture.py"
BAND_OLD = ("                band = [p for p in out if p.get(\"road\") == road.index\n"
            "                        and p.get(\"kerb\") == kerb.side]\n")
BAND_NEW = ("                # EVERY PIECE PLANNED SO FAR, not this kerb's alone (0.118.1): a\n"
            "                # corner pole stands where two roads' furniture meet, and\n"
            "                # `site_poles._room` reads plan boxes, right across roads\n"
            "                band = list(out)\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.118.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.118.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.118.1.md")
    assert entry.startswith("## 0.118.1 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    pp = LOT / POLES
    raw = pp.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[POLES], (POLES, "is not the file this patch read", got)
    p_eol = _eol(raw, POLES)
    poles = raw.decode("utf-8").replace("\r\n", "\n")
    poles = _once(poles, RUNS_OLD, RUNS_NEW, "_runs")
    poles = _once(poles, SIGNAL_OLD, SIGNAL_NEW, "SIGNAL_CLEAR")
    poles = _once(poles, ROOM_DOC_OLD, ROOM_DOC_NEW, "_room's docstring")
    poles = _once(poles, ROOM_SIGNAL_OLD, ROOM_SIGNAL_NEW, "_room's signal")
    assert "SIGNAL_CLEAR" not in poles.replace("`SIGNAL_CLEAR`", ""), "a reader of SIGNAL_CLEAR is left"
    fp = LOT / FURNITURE
    f_raw = fp.read_bytes()
    f_eol = _eol(f_raw, FURNITURE)
    furniture = _once(f_raw.decode("utf-8").replace("\r\n", "\n"), BAND_OLD, BAND_NEW, "the line's band")
    tp = LOT / TEST
    t_raw = tp.read_bytes()
    t_eol = _eol(t_raw, TEST)
    test = t_raw.decode("utf-8").replace("\r\n", "\n")
    assert "test_every_line_stands_its_corner_poles_beside_a_signal" not in test, "already applied"
    test = test.rstrip("\n") + "\n" + _src("test_corner.py.txt")
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    pp.write_bytes(poles.replace("\n", p_eol.decode()).encode("utf-8"))
    fp.write_bytes(furniture.replace("\n", f_eol.decode()).encode("utf-8"))
    tp.write_bytes(test.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.118.0 -> 0.118.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
