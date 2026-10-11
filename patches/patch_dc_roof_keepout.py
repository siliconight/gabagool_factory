"""Deli Counter 0.209.0: a roof slot says where a body steps off a ladder, and a composed building
carries a roof-props layer the circulation gate asks its question of (roadmap 181).

Anchored edits in `roofs.py` (`roof_keep_out`: a `2 * LANDING_HALF_M` square around each ladder
whose top is the roof, in the centred coords `floors.room_voids` writes the holes in; every roof
slot's `fit.keep_out`), `portable_building.py` (`build_package(..., roofprops_glb=None)` bundles
and instances a third layer at `art/roofprops/` as node `RoofProps`; `combine_circulation` makes
one `circulation_check` of every arm that ran, the roof props' included), `test_roof_fixtures.py`
(three tests, two failing on 0.208.0) and a new `test_circulation_arms.py`; each file pinned by
hash and each anchor asserted once, nothing written on a miss; the files' own line endings kept.
Applies on 0.208.0. CHANGELOG and VERSION from `dc_roof_keepout/CHANGELOG_0.209.0.md`;
`--results-pending` leaves RESULT_SUITE and RESULT_LIBRARY to `--fill`. The library must be
rebuilt after it lands (`python build.py --all`): each shell's `slots.json` is where the landings
ship.

    python patches/patch_dc_roof_keepout.py --results-pending && cd deli_counter && python -m pytest -q
    python patches/patch_dc_roof_keepout.py --fill
    DC_ROOT=<copy> python patches/patch_dc_roof_keepout.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_roof_keepout"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_LIBRARY": "result_library.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.208.0", b"Deli Counter 0.209.0"
CHANGELOG_HEAD = "## [0.208.0] - a home's room hangs a dome\n"
ROOFS = "roofs.py"
PORTABLE = "portable_building.py"
TESTS = "test_roof_fixtures.py"
NEW_TEST = "test_circulation_arms.py"
SHA = {ROOFS: "7d7d39800a5db2ec", PORTABLE: "7e669d66b0bd23e5", TESTS: "a88eed77d9c1d430"}

# --- roofs.py -------------------------------------------------------------------------------
R_CONST_OLD = ("ROOF_SLOT_ROLE = \"roof\"\n"
               "GREYBOX_REF = \"roof_greybox_01\"\n")
R_CONST_NEW = ("ROOF_SLOT_ROLE = \"roof\"\n"
               "GREYBOX_REF = \"roof_greybox_01\"\n"
               "#: Half-size of the square a body needs where it steps off a ladder onto the\n"
               "#: roof (0.209.0): the hatch cut for it is about 1.3 m across\n"
               "#: (`ladder_geom.through_hole`), and a stride past its edge is 0.85 m.\n"
               "LANDING_HALF_M = 1.5\n")
R_SIG_OLD = ("def _slot(sid, story, cx, cy, cz, sx, sy, ft, room=None, style=1,\n"
             "          material=None, voids=None):\n")
R_SIG_NEW = ("def _slot(sid, story, cx, cy, cz, sx, sy, ft, room=None, style=1,\n"
             "          material=None, voids=None, keep_out=None):\n")
R_FIT_OLD = ("                # there: `openings` is the WALL contract, a hole in a standing\n"
             "                # slab's x/z, and the two are not the same shape.\n"
             "                \"voids\": list(voids or ())},\n"
             "    }\n")
R_FIT_NEW = ("                # there: `openings` is the WALL contract, a hole in a standing\n"
             "                # slab's x/z, and the two are not the same shape.\n"
             "                \"voids\": list(voids or ()),\n"
             "                # Where a body steps off a ladder onto this roof (0.209.0):\n"
             "                # rects in the same centred coords as `voids`, for Zoo's roof\n"
             "                # props (>= 1.101.0) to keep off. Empty on a roof no ladder\n"
             "                # reaches.\n"
             "                \"keep_out\": list(keep_out or ())},\n"
             "    }\n")
R_DEF_OLD = "\n\n\ndef roof_slots(spec, story, cz, ft):\n"
R_DEF_NEW = ("\n\n\n"
             "def roof_keep_out(spec, story, cx, cy, sx, sy):\n"
             "    \"\"\"Where a body steps off a ladder onto the roof that caps ``story``: a\n"
             "    ``2 * LANDING_HALF_M`` square around each ladder whose top story is that\n"
             "    one, in the centred coords ``floors.room_voids`` writes the slab's holes\n"
             "    in (world minus the centre it is handed), dropped when it misses the\n"
             "    rect entirely, as a hole is. Zoo's roof props (>= 1.101.0) keep off\n"
             "    these; a hatch ladder's hole is already in `voids`, and its landing is\n"
             "    the stride beyond the hole, which no hole and no climb volume names.\n"
             "    Pure, tested.\n"
             "    \"\"\"\n"
             "    hx, hy = sx / 2.0, sy / 2.0\n"
             "    out = []\n"
             "    for lad in getattr(spec, \"ladders\", ()) or ():\n"
             "        if int(getattr(lad, \"to_story\", -1)) != int(story):\n"
             "            continue\n"
             "        x0 = float(lad.x) - LANDING_HALF_M - cx\n"
             "        x1 = float(lad.x) + LANDING_HALF_M - cx\n"
             "        y0 = float(lad.y) - LANDING_HALF_M - cy\n"
             "        y1 = float(lad.y) + LANDING_HALF_M - cy\n"
             "        if x1 <= -hx or x0 >= hx or y1 <= -hy or y0 >= hy:\n"
             "            continue\n"
             "        out.append({\"x0\": round(x0, 4), \"y0\": round(y0, 4),\n"
             "                    \"x1\": round(x1, 4), \"y1\": round(y1, 4),\n"
             "                    \"ladder\": getattr(lad, \"id\", None)})\n"
             "    return out\n"
             "\n\n"
             "def roof_slots(spec, story, cz, ft):\n")
R_ROOM_OLD = ("                out.append(_slot(f\"roof_{r.id}\", story, cx, cy, cz,\n"
              "                                 sx, sy, ft, room=r.id,\n"
              "                                 style=style, material=mat,\n"
              "                                 voids=room_voids(spec, r, story,\n"
              "                                                  cx, cy, sx, sy)))\n"
              "        return out\n")
R_ROOM_NEW = ("                out.append(_slot(f\"roof_{r.id}\", story, cx, cy, cz,\n"
              "                                 sx, sy, ft, room=r.id,\n"
              "                                 style=style, material=mat,\n"
              "                                 voids=room_voids(spec, r, story,\n"
              "                                                  cx, cy, sx, sy),\n"
              "                                 keep_out=roof_keep_out(spec, story,\n"
              "                                                        cx, cy, sx, sy)))\n"
              "        return out\n")
R_FOOT_OLD = ("    slot = _slot(\"roof_footprint\", story, (_rx0 + _rx1) / 2.0,\n"
              "                 (_ry0 + _ry1) / 2.0, cz,\n"
              "                 _rx1 - _rx0, _ry1 - _ry0, ft,\n"
              "                 style=style, material=mat,\n"
              "                 voids=room_voids(spec, None, story, 0.0, 0.0,\n"
              "                                  _rx1 - _rx0, _ry1 - _ry0))\n")
R_FOOT_NEW = ("    slot = _slot(\"roof_footprint\", story, (_rx0 + _rx1) / 2.0,\n"
              "                 (_ry0 + _ry1) / 2.0, cz,\n"
              "                 _rx1 - _rx0, _ry1 - _ry0, ft,\n"
              "                 style=style, material=mat,\n"
              "                 voids=room_voids(spec, None, story, 0.0, 0.0,\n"
              "                                  _rx1 - _rx0, _ry1 - _ry0),\n"
              "                 # THE SAME CENTRE THE VOIDS TAKE, 0.0, 0.0: right when the\n"
              "                 # top slab is centred, which every library roof with a\n"
              "                 # hole is (two of 133 roofs stand off-centre, both\n"
              "                 # hole-less, measured 2026-10-11); a stepped building's\n"
              "                 # holes and landings would be off by its inset together.\n"
              "                 keep_out=roof_keep_out(spec, story, 0.0, 0.0,\n"
              "                                        _rx1 - _rx0, _ry1 - _ry0))\n")

# --- portable_building.py -------------------------------------------------------------------
P_SIG_OLD = ("def build_package(slots_path, gameplay_path, module_dir, out_dir, *,\n"
             "                  theme, style=1, building_id=None, greybox_glb=None,\n"
             "                  dressing_glb=None, fixtures_glb=None):\n")
P_SIG_NEW = ("def combine_circulation(arms):\n"
             "    \"\"\"One `circulation_check` from the arms that ran (0.209.0): ``[(name,\n"
             "    check)]``, a check None when its layer was absent. One arm is returned\n"
             "    as itself (it carries its `source`); two or more become ``{\"ok\",\n"
             "    <name>: check, ...}`` with the verdict the AND of theirs -- the shape\n"
             "    0.149.0's readers split by name (`run_presentation_compose.\n"
             "    circulation_gate`, Level Factory's `_circulation_arms`); none is None.\n"
             "    \"\"\"\n"
             "    ran = [(name, check) for name, check in arms if check is not None]\n"
             "    if not ran:\n"
             "        return None\n"
             "    if len(ran) == 1:\n"
             "        return ran[0][1]\n"
             "    out = {\"ok\": all(bool(check.get(\"ok\")) for _, check in ran)}\n"
             "    for name, check in ran:\n"
             "        out[name] = check\n"
             "    return out\n"
             "\n\n"
             "def build_package(slots_path, gameplay_path, module_dir, out_dir, *,\n"
             "                  theme, style=1, building_id=None, greybox_glb=None,\n"
             "                  dressing_glb=None, fixtures_glb=None, roofprops_glb=None):\n")
P_LAYERS_OLD = ("    # turns them into placed lights). Without these the composed building\n"
                "    # is skinned architecture with empty rooms; with them it is the level.\n"
                "    layers = {}\n"
                "    for src, sub, node in ((dressing_glb, \"dressing\", \"Dressing\"),\n"
                "                           (fixtures_glb, \"fixtures\", \"Fixtures\")):\n")
P_LAYERS_NEW = ("    # turns them into placed lights). Without these the composed building\n"
                "    # is skinned architecture with empty rooms; with them it is the level.\n"
                "    # And the ROOF PROPS pass (0.209.0, roadmap 181): Zoo's rooftop units,\n"
                "    # vents, fans, skylights and dishes, planned off the roof's hatches and\n"
                "    # landings (`roofs.roof_keep_out`), one merged mesh a material a roof.\n"
                "    layers = {}\n"
                "    for src, sub, node in ((dressing_glb, \"dressing\", \"Dressing\"),\n"
                "                           (fixtures_glb, \"fixtures\", \"Fixtures\"),\n"
                "                           (roofprops_glb, \"roofprops\", \"RoofProps\")):\n")
P_GATE_OLD = ("    # One key, both arms, and a combined verdict -- a consumer asking \"is\n"
              "    # circulation clear\" must not have to know which pass placed the prop.\n"
              "    if circ is None and circ_dressing is not None:\n"
              "        circ = circ_dressing\n"
              "    elif circ is not None and circ_dressing is not None:\n"
              "        circ = {\"ok\": bool(circ.get(\"ok\")) and bool(circ_dressing.get(\"ok\")),\n"
              "                \"shell\": circ, \"dressing\": circ_dressing}\n")
P_GATE_NEW = ("    # THE ROOF PROPS ARM (0.209.0): the same question of the third layer. A\n"
              "    # ladder's climb volume reaches above its hatch, so a unit standing on\n"
              "    # the hatch is caught here; the landing beside it is Zoo's keep-out\n"
              "    # (`roofs.roof_keep_out`), which no volume names.\n"
              "    circ_roof = None\n"
              "    if layers.get(\"roofprops\"):\n"
              "        try:\n"
              "            import circulation\n"
              "            circ_roof = circulation.check_dressing(\n"
              "                os.path.join(out_dir, \"art\", \"roofprops\", layers[\"roofprops\"]),\n"
              "                slots, gameplay)\n"
              "            circ_roof[\"source\"] = \"roofprops\"\n"
              "        except Exception as ex:  # gate must report, never crash the compose\n"
              "            circ_roof = {\"ok\": False, \"source\": \"roofprops\",\n"
              "                         \"error\": f\"gate failed to run: {ex}\"}\n"
              "\n"
              "    # One key, every arm that ran, and a combined verdict -- a consumer asking\n"
              "    # \"is circulation clear\" must not have to know which pass placed the prop.\n"
              "    circ = combine_circulation([(\"shell\", circ), (\"dressing\", circ_dressing),\n"
              "                                (\"roofprops\", circ_roof)])\n")

# --- test_roof_fixtures.py ------------------------------------------------------------------
T_ADD = '''

# --- 0.209.0: where a body steps off a ladder onto the roof --------------------------

def _ladder(**kw):
    from spec_types import Ladder
    base = dict(x=2.0, y=-5.0, from_story=0, to_story=3, facing="N", id="l0",
                role="roof_access")
    base.update(kw)
    return Ladder(**base)


def test_a_ladder_to_the_roof_writes_its_landing_on_the_roof_slot():
    """FAILS ON 0.208.0: the roof slot carried no `keep_out`."""
    s = _roof(_spec(facade=False, ladders=[_ladder()]))
    assert s["fit"]["keep_out"] == [
        {"x0": 0.5, "y0": -6.5, "x1": 3.5, "y1": -3.5, "ladder": "l0"}]


def test_a_ladder_that_stops_below_the_roof_writes_nothing():
    s = _roof(_spec(facade=False, ladders=[_ladder(to_story=2, id="l1",
                                                   role="service_access")]))
    assert s["fit"]["keep_out"] == []


def test_a_landing_is_in_the_roof_s_centred_coords_and_dropped_off_it():
    """FAILS ON 0.208.0 (no `roof_keep_out`). Written as the holes are: world
    minus the centre handed in, and gone when it misses the rect entirely."""
    sp = _spec(facade=False, ladders=[_ladder(x=20.0, y=0.0)])
    assert roofs.roof_keep_out(sp, 3, 0.0, 0.0, 6.0, 12.0) == []
    sp = _spec(facade=False, ladders=[_ladder(x=4.0, y=1.0)])
    assert roofs.roof_keep_out(sp, 3, 3.0, 1.0, 6.0, 12.0) == [
        {"x0": -0.5, "y0": -1.5, "x1": 2.5, "y1": 1.5, "ladder": "l0"}]
'''


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


def _read(rel):
    p = DC / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.209.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.209.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.209.0.md")
    assert entry.startswith("## [0.209.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    new_test = _src(NEW_TEST + ".txt")
    assert not (DC / NEW_TEST).exists(), "already applied"

    rp, r_eol, roofs = _read(ROOFS)
    assert "roof_keep_out" not in roofs, "already applied"
    roofs = _once(roofs, R_CONST_OLD, R_CONST_NEW, "the constants")
    roofs = _once(roofs, R_SIG_OLD, R_SIG_NEW, "_slot's signature")
    roofs = _once(roofs, R_FIT_OLD, R_FIT_NEW, "the fit dict")
    roofs = _once(roofs, R_DEF_OLD, R_DEF_NEW, "roof_keep_out before roof_slots")
    roofs = _once(roofs, R_ROOM_OLD, R_ROOM_NEW, "the per-room slot")
    roofs = _once(roofs, R_FOOT_OLD, R_FOOT_NEW, "the footprint slot")

    pp, p_eol, port = _read(PORTABLE)
    port = _once(port, P_SIG_OLD, P_SIG_NEW, "build_package's signature")
    port = _once(port, P_LAYERS_OLD, P_LAYERS_NEW, "the layer loop")
    port = _once(port, P_GATE_OLD, P_GATE_NEW, "the gate's arms")

    tp, t_eol, tests = _read(TESTS)
    tests = tests.rstrip("\n") + "\n" + T_ADD

    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(rp, r_eol, roofs)
    _write(pp, p_eol, port)
    _write(tp, t_eol, tests)
    _write(DC / NEW_TEST, t_eol, new_test)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.208.0 -> 0.209.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
