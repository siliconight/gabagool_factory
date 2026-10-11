"""Lot 0.116.0: a lane lights its own length (the dark lane's design call, 2026-10-11).

Anchored edits in `site_furniture.py` (`LANE_LAMP_SPACING`, `LANE_LAMP_OUT`, `LANE_SIDE_REACH`,
`LANE_NUDGES`, `lane_side` and `plan_lane_lamps` from `lot_lane_lamps/lane_lamps.py.txt`, before
`plan_furniture`; `plan_furniture` takes `keep_out` and gives a road without a sidewalk its lamps
instead of skipping it), in `lot.py` (the planner's call passes the pylons' keep-out: the path
corridors, the building footprints, the parking fields) and a new `tests/test_lane_lamps.py`;
each file pinned by hash and each anchor asserted once,
nothing written on a miss; the file's own line endings kept. Applies on Lot 0.115.0. CHANGELOG and
VERSION from `lot_lane_lamps/CHANGELOG_0.116.0.md`; `--suite-pending` leaves RESULT_SUITE to
`--fill`.

    python patches/patch_lot_lane_lamps.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_lane_lamps.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_lane_lamps.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_lane_lamps"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.115.0", b"Lot 0.116.0"
CHANGELOG_HEAD = "## 0.115.0 - the plate tile follows the bake\n"
SHA = {"site_furniture.py": "343f47fbd4ef4f80",
       "lot.py": "90602408231dc731"}
NEW_TEST = "tests/test_lane_lamps.py"

DEF_OLD = "def plan_furniture(roads_list, buildings=(), markers=(), findings=None,\n"
SIG_OLD = ("def plan_furniture(roads_list, buildings=(), markers=(), findings=None,\n"
           "                   sign_bands=()) -> list:\n")
SIG_NEW = ("def plan_furniture(roads_list, buildings=(), markers=(), findings=None,\n"
           "                   sign_bands=(), keep_out=()) -> list:\n")
DOC_OLD = ("    a tree keeps out of (`_sign_spans`). Returns the list; the caller\n"
           "    extends the spec and the slots.\"\"\"\n")
DOC_NEW = ("    a tree keeps out of (`_sign_spans`). ``keep_out`` (0.116.0) is the rects\n"
           "    a lane's lamp keeps clear of (`plan_lane_lamps`). Returns the list; the\n"
           "    caller extends the spec and the slots.\"\"\"\n")
LOOP_OLD = ("    for road in roads_list:\n"
            "        control = controls[road.index]\n"
            "        if not road.sidewalk:\n"
            "            continue\n")
LOOP_NEW = ("    for road in roads_list:\n"
            "        control = controls[road.index]\n"
            "        if not road.sidewalk:\n"
            "            # A LANE LIGHTS ITS OWN LENGTH (0.116.0): no band, so none of the\n"
            "            # band's pieces -- only its lamps, on its own edge (`plan_lane_lamps`)\n"
            "            lane_lamps = plan_lane_lamps(road, buildings, markers, n, findings,\n"
            "                                         keep_out=keep_out)\n"
            "            n += len(lane_lamps)\n"
            "            out.extend(lane_lamps)\n"
            "            continue\n")

CALL_OLD = ("    furniture = site_furniture.plan_furniture(_furniture_roads,\n"
            "                                              site_spec.get(\"buildings\") or [],\n"
            "                                              list(cover_points.values()),\n"
            "                                              furniture_findings,\n"
            "                                              sign_bands=sign_bands(site_spec,\n"
            "                                                                    _furniture_roads))\n")
CALL_NEW = ("    # a lane's lamps keep clear of what the pylons keep clear of (0.116.0)\n"
            "    import site_spawns as _spawns_for_lanes\n"
            "    furniture = site_furniture.plan_furniture(_furniture_roads,\n"
            "                                              site_spec.get(\"buildings\") or [],\n"
            "                                              list(cover_points.values()),\n"
            "                                              furniture_findings,\n"
            "                                              sign_bands=sign_bands(site_spec,\n"
            "                                                                    _furniture_roads),\n"
            "                                              keep_out=site_furniture.path_corridors(site_spec)\n"
            "                                              + _spawns_for_lanes.footprints(site_spec, margin=0.5)\n"
            "                                              + _field_rects)\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lot 0.116.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.116.0.md")
    assert entry.startswith("## 0.116.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LOT / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    fp, f_eol, furn = _read("site_furniture.py")
    assert "plan_lane_lamps" not in furn, "already applied"
    furn = _once(furn, SIG_OLD, SIG_NEW, "plan_furniture signature")
    furn = _once(furn, DOC_OLD, DOC_NEW, "plan_furniture docstring")
    furn = _once(furn, DEF_OLD, _src("lane_lamps.py.txt") + DEF_OLD, "plan_furniture def")
    furn = _once(furn, LOOP_OLD, LOOP_NEW, "the band loop's skip")

    lp, l_eol, lot = _read("lot.py")
    lot = _once(lot, CALL_OLD, CALL_NEW, "the planner's call")

    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    test = _src("test_lane_lamps.py")
    # Every pin and anchor matched: now write.
    fp.write_bytes(furn.replace("\n", f_eol.decode()).encode("utf-8"))
    lp.write_bytes(lot.replace("\n", l_eol.decode()).encode("utf-8"))
    (LOT / NEW_TEST).write_bytes(test.replace("\n", f_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.115.0 -> 0.116.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
