"""Lot 0.118.0: the pole line -- one kerb of every street carries wooden utility poles, and the poles
carry the street's lamps (factory roadmap 240, the walker's calls of 2026-10-12).

New files, each refused if it exists:
  site_poles.py                     the line's planner and Zoo's mirrored numbers (`site_poles.py.txt`)
  tests/test_site_poles.py          eleven tests (`test_site_poles.py.txt`)
Anchored edits, each asserted once, nothing written until all of them matched:
  site_furniture.py   the docstring's pole paragraph; SPECIES/FOOTPRINT gain the pole; plan_furniture
                      imports site_poles, stands trees without lamps, and stands the line last on its kerb
  lot.py              _streetlight_anchors hangs a pole's light at its lens; write_site_slots stands a
                      pole's module at `module_at` and writes its form; the scene writer stands the
                      module at `module_at`; COVER_MATERIALS gains the pole
  site_posters.py     POLES gains the pole, its sleeve clearing the corners at grade
  tests/test_site_furniture.py, tests/test_site_band_clear.py, tests/test_lot.py,
  tests/test_lane_lamps.py   the tests that held a steel lamp on both kerbs, restated for the line
CHANGELOG and VERSION from `lot_pole_line/CHANGELOG_0.118.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

    python patches/patch_lot_pole_line.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_pole_line.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_pole_line.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_pole_line"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.117.0", b"Lot 0.118.0"
CHANGELOG_HEAD = ("## 0.117.0 - the walk test's navigation updates on its own thread, so its clock "
                  "need not wait\n")
NEW = {"site_poles.py": "site_poles.py.txt", "tests/test_site_poles.py": "test_site_poles.py.txt"}

EDITS = {
    "site_furniture.py": [
        ("the docstring's pole paragraph",
         "step limit and carries collision.\n\nThe waiting places",
         "step limit and carries collision.\n\n"
         "THE LAMPS ARE ON THE POLES (0.118.0, factory roadmap 240): a road with a\n"
         "band stands no steel `streetlight` now. One of its kerbs carries the pole\n"
         "line (`site_poles`), every pole a cobra-head, planned last on its band so\n"
         "it steps clear of what already stands there; the trees keep the stations\n"
         "the lamps' spacing gave them. A lane, which has no band, keeps its own\n"
         "lamps (`plan_lane_lamps`).\n\n"
         "The waiting places"),
        ("the pole's species and footprint",
         'FOOTPRINT["sign_post"] = (0.1, 0.1)\n',
         'FOOTPRINT["sign_post"] = (0.1, 0.1)\n'
         "#: THE UTILITY POLE (0.118.0, `site_poles`): its slot is Zoo's module --\n"
         "#: the cobra-head's reach and the crossarm's, `site_poles.POLE_DIMS` -- and\n"
         "#: what a body meets is the pole.\n"
         'SPECIES["utility_pole"] = (0.3, 3.67, 10.4)\n'
         'FOOTPRINT["utility_pole"] = (0.3, 0.3)\n'),
        ("plan_furniture's import",
         '    caller extends the spec and the slots."""\n    out = []\n    n = 0\n',
         '    caller extends the spec and the slots."""\n'
         "    # the pole line (0.118.0); it imports this module, so it is imported here\n"
         "    import site_poles\n"
         "    out = []\n    n = 0\n"),
        ("the lamp loop",
         "        species_tree = species_for[road.index]\n"
         "        for kerb in road.kerbs:\n"
         "            # this band's pieces, for `_free`, starting with its control\n"
         '            placed = [p for p in control if p["kerb"] == kerb.side]\n'
         "            outer = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - BAND_INSET)\n"
         "            tree_off = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - TREE_INSET)\n"
         "            # lamps at a spacing, skipping the cuts, and a tree between each pair,\n"
         "            # each kept out of the shop bands facing this kerb (0.106.0)\n"
         "            spans = _sign_spans(road, kerb, sign_bands, roads_list)\n"
         "            t = LAMP_START\n"
         "            while t < road.length - LAMP_START:\n"
         '                w, d, h = SPECIES["streetlight"]\n'
         '                lamp = _nudged(lambda s: _piece(f"Lamp_{n}", "streetlight", road, kerb, s, outer),\n'
         "                               t, d / 2.0, kerb, placed, markers, avoid=spans)\n"
         "                if spans and not _clear_of_spans(t, d / 2.0, spans) and _clear_of_cuts(t, d / 2.0, kerb):\n"
         '                    kept_clear.append((f"Lamp_{n}", t, lamp["t"] if lamp else None))\n'
         "                if lamp:\n"
         "                    placed.append(lamp)\n"
         "                    n += 1\n"
         "                tt = t + TREE_OFFSET\n",
         "        species_tree = species_for[road.index]\n"
         "        # THE LAMPS ARE ON THE POLES (0.118.0, factory roadmap 240): one kerb\n"
         "        # of this road carries the pole line, every pole a cobra-head\n"
         "        # (`site_poles`), and neither kerb stands a steel lamp -- the\n"
         "        # walker's call of 2026-10-12. The trees keep the lamps' stations.\n"
         "        line_kerb = site_poles.pole_kerb(road, sign_bands, roads_list)\n"
         "        for kerb in road.kerbs:\n"
         "            # this band's pieces, for `_free`, starting with its control\n"
         '            placed = [p for p in control if p["kerb"] == kerb.side]\n'
         "            outer = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - BAND_INSET)\n"
         "            tree_off = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - TREE_INSET)\n"
         "            # a tree halfway between two of the lamps' stations, skipping the\n"
         "            # cuts and kept out of the shop bands facing this kerb (0.106.0)\n"
         "            spans = _sign_spans(road, kerb, sign_bands, roads_list)\n"
         "            t = LAMP_START\n"
         "            while t < road.length - LAMP_START:\n"
         "                tt = t + TREE_OFFSET\n"),
        ("the line, last on its kerb",
         "                out.extend(_stop_corner(road, kerb, stop, placed, markers))\n"
         "        # a meter at every bay\n",
         "                out.extend(_stop_corner(road, kerb, stop, placed, markers))\n"
         "            # THE POLE LINE (0.118.0), last on its band: it steps clear of\n"
         "            # everything the band already stands, the meters `plan_meters`\n"
         "            # will stand and the shop bands, so nothing else has to know\n"
         "            if kerb is line_kerb:\n"
         "                band = [p for p in out if p.get(\"road\") == road.index\n"
         "                        and p.get(\"kerb\") == kerb.side]\n"
         "                poles = site_poles.plan_line(road, kerb, band, markers, spans, n,\n"
         "                                             buildings, kept_clear)\n"
         "                n += len(poles)\n"
         "                out.extend(poles)\n"
         "        # a meter at every bay\n"),
    ],
    "lot.py": [
        ("the anchors' species",
         "    anchors = []\n"
         '    for i, cv in enumerate(site_spec.get("cover") or []):\n'
         '        if cv.get("species") != "streetlight":\n'
         "            continue\n",
         "    import site_poles\n"
         "    anchors = []\n"
         '    for i, cv in enumerate(site_spec.get("cover") or []):\n'
         '        if cv.get("species") not in ("streetlight", "utility_pole"):\n'
         "            continue\n"),
        ("the anchor's point",
         '        base = SIDEWALK_H if cv.get("base") == "sidewalk" else 0.0\n'
         '        x, y = cv["at"]\n'
         "        anchors.append({\n",
         '        base = SIDEWALK_H if cv.get("base") == "sidewalk" else 0.0\n'
         '        if cv.get("species") == "utility_pole":\n'
         "            # THE COBRA-HEAD'S LENS (0.118.0, `site_poles`): 2.171 m toward\n"
         "            # the road on its arm and 7.401 m up, where Zoo hangs it --\n"
         "            # under the lens, as a steel lamp's light is under its own\n"
         "            x, y, z = site_poles.lens_point(cv, base)\n"
         "        else:\n"
         '            x, y = cv["at"]\n'
         "            z = base + h - STREETLIGHT_LENS_DROP\n"
         "        anchors.append({\n"),
        ("the anchor's pos",
         '            "pos": [round(float(x), 3), round(float(y), 3),\n'
         "                    round(base + h - STREETLIGHT_LENS_DROP, 3)],\n",
         '            "pos": [round(float(x), 3), round(float(y), 3), round(float(z), 3)],\n'),
        ("the slot's centre",
         '        cx, cy = cv["at"]\n'
         '        base = SIDEWALK_H if cv.get("base") == "sidewalk" else 0.0\n'
         "        slots.append({\n",
         "        # A POLE'S MODULE IS NOT CENTRED ON THE POLE (0.118.0): the record's\n"
         "        # `at` is the pole a body meets, `module_at` the slot's centre\n"
         '        cx, cy = cv.get("module_at") or cv["at"]\n'
         '        base = SIDEWALK_H if cv.get("base") == "sidewalk" else 0.0\n'
         "        slots.append({\n"),
        ("the slot's form",
         '        if cv.get("blade"):\n'
         '            slots[-1]["form"] = str(cv["blade"])\n',
         '        if cv.get("blade"):\n'
         '            slots[-1]["form"] = str(cv["blade"])\n'
         "        # A POLE'S CAN (0.118.0): `site_poles` names `transformer` on the\n"
         "        # poles that carry one; `auto` is none, as Zoo reads it\n"
         '        elif cv.get("form"):\n'
         '            slots[-1]["form"] = str(cv["form"])\n'),
        ("the scene's module",
         "            xform = _godot_transform((cx, cy), float(cv.get(\"yaw\") or 0.0),\n"
         "                                     z=base + sy / 2)\n"
         "            body += [f'[node name=\"cover_{i}\" parent=\".\" '\n",
         "            # a pole's module stands at the slot's centre, not the pole's\n"
         "            # (0.118.0): the box below, if it is drawn, is the pole\n"
         '            mx, my = cv.get("module_at") or (cx, cy)\n'
         "            xform = _godot_transform((mx, my), float(cv.get(\"yaw\") or 0.0),\n"
         "                                     z=base + sy / 2)\n"
         "            body += [f'[node name=\"cover_{i}\" parent=\".\" '\n"),
        ("the pole's material",
         '                   "streetlight": "metal", "fire_hydrant": "metal_painted",\n',
         '                   "streetlight": "metal", "fire_hydrant": "metal_painted",\n'
         "                   # the pole line (site_poles, 0.118.0): Zoo 1.104.0's one\n"
         "                   # option, creosoted wood\n"
         '                   "utility_pole": "wood",\n'),
    ],
    "site_posters.py": [
        ("the flyers' poles",
         'POLES = {"streetlight": 0.06, "sign_post": 0.0707}\n',
         "#: A UTILITY POLE (0.118.0, `site_poles`) is a ten-sided wooden pole 0.30 m\n"
         "#: across at grade and 0.19 m at the top: a sleeve at its corners' radius at\n"
         "#: grade clears every corner above, the paper a centimetre off the pole at\n"
         "#: reach. The classic flyer pole, and on a band road the only pole left.\n"
         'POLES = {"streetlight": 0.06, "sign_post": 0.0707, "utility_pole": 0.15}\n'),
    ],
    "tests/test_site_furniture.py": [
        ("the lamps' spacing test",
         "def test_lamps_at_the_spacing_and_the_corner_set_at_every_cut():\n"
         "    roads = site_streets.roads(_probe())\n"
         "    pieces = site_furniture.plan_furniture(roads)\n"
         "    by = {}\n"
         "    for p in pieces:\n"
         '        by.setdefault(p["species"], []).append(p)\n'
         '    lamps = sorted(p["at"][0] for p in by["streetlight"] if p["kerb"] == "L")\n'
         "    gaps = [b - a for a, b in zip(lamps, lamps[1:])]\n"
         "    assert gaps and all(abs(g - site_furniture.LAMP_SPACING) < 1e-6\n"
         "                        or g > site_furniture.LAMP_SPACING for g in gaps)\n",
         "def test_the_line_on_one_kerb_and_the_corner_set_at_every_cut():\n"
         "    roads = site_streets.roads(_probe())\n"
         "    pieces = site_furniture.plan_furniture(roads)\n"
         "    by = {}\n"
         "    for p in pieces:\n"
         '        by.setdefault(p["species"], []).append(p)\n'
         "    # THE LAMPS ARE ON THE POLES (0.118.0): no steel lamp on a band road,\n"
         "    # the line on one kerb (`tests/test_site_poles.py` holds its spacing)\n"
         '    assert "streetlight" not in by\n'
         '    assert by["utility_pole"] and len({p["kerb"] for p in by["utility_pole"]}) == 1\n'),
        ("the slots' height test",
         '    lamps = [s for s in doc["slots"] if s["species"] == "streetlight"]\n'
         "    assert lamps\n"
         "    for s in lamps:\n"
         '        assert abs(s["transform"]["translation"][2] - (lot.SIDEWALK_H + 3.0)) < 1e-6\n'
         '        assert s["fit"]["collision"] == "convex"\n',
         "    # a pole (0.118.0): its module 10.4 m tall, standing on the band's top\n"
         '    poles = [s for s in doc["slots"] if s["species"] == "utility_pole"]\n'
         "    assert poles\n"
         "    for s in poles:\n"
         '        assert abs(s["transform"]["translation"][2] - (lot.SIDEWALK_H + 5.2)) < 1e-6\n'
         '        assert s["fit"]["collision"] == "convex"\n'),
        ("the scene's box test",
         "    # and the box the scene draws for a lamp stands on the band's top (the\n"
         "    # kerb line is planned first, so the first lamp is the first slot)\n"
         '    txt = (tmp_path / "coldrun_kerb_probe.tscn").read_text(encoding="utf-8")\n'
         '    first_lamp = next(i for i, s in enumerate(doc["slots"]) if s["species"] == "streetlight")\n'
         "    i = txt.index('name=\"cover_%d\"' % first_lamp)\n"
         '    assert f", {lot.SIDEWALK_H + 3.0:g}, " in txt[i:].split("\\n")[1]\n',
         "    # and the box the scene draws for a pole stands on the band's top, at\n"
         "    # the pole: no module was built here, so the box is the pole's column\n"
         '    txt = (tmp_path / "coldrun_kerb_probe.tscn").read_text(encoding="utf-8")\n'
         '    first = next(s["slot_id"] for s in doc["slots"] if s["species"] == "utility_pole")\n'
         "    i = txt.index('name=\"%s\"' % first)\n"
         '    assert f", {lot.SIDEWALK_H + 5.2:g}, " in txt[i:].split("\\n")[1]\n'),
        ("the trees' test",
         "def test_a_tree_stands_between_every_two_lamps_on_the_grates_footprint():\n"
         "    roads = site_streets.roads(_probe())\n"
         "    (road,) = roads\n"
         "    pieces = site_furniture.plan_furniture(roads)\n"
         "    species = site_furniture.tree_for(road)\n"
         '    trees = [p for p in pieces if p["species"] == species]\n'
         '    lamps = [p for p in pieces if p["species"] == "streetlight"]\n'
         "    assert trees and len(trees) <= len(lamps)\n",
         "def test_a_tree_keeps_the_lamps_stations_on_the_grates_footprint():\n"
         "    roads = site_streets.roads(_probe())\n"
         "    (road,) = roads\n"
         "    pieces = site_furniture.plan_furniture(roads)\n"
         "    species = site_furniture.tree_for(road)\n"
         '    trees = [p for p in pieces if p["species"] == species]\n'
         "    # the lamps went onto the poles (0.118.0); the trees kept their stations,\n"
         "    # at most one a kerb at each\n"
         "    stations = len(range(int(site_furniture.LAMP_START),\n"
         "                         int(road.length - site_furniture.LAMP_START),\n"
         "                         int(site_furniture.LAMP_SPACING)))\n"
         "    assert trees and len(trees) <= 2 * stations\n"),
        ("the markers' test",
         "    lamp = next(p for p in bare if p[\"species\"] == \"streetlight\")\n"
         "    marker = tuple(lamp[\"at\"])\n"
         "    pieces = site_furniture.plan_furniture(roads, markers=[marker])\n"
         "    for p in pieces:\n"
         "        assert site_furniture._clear_of_markers(p, [marker]), p\n"
         "    # the lamp stepped along its band rather than vanishing\n"
         "    moved = [p for p in pieces if p[\"species\"] == \"streetlight\" and p[\"kerb\"] == lamp[\"kerb\"]\n"
         "             and abs(p[\"t\"] - lamp[\"t\"]) <= 4.0 + 1e-6]\n"
         "    assert moved and moved[0][\"t\"] != lamp[\"t\"]\n",
         "    # a pole (0.118.0), the street's lamps being on its poles now\n"
         "    pole = next(p for p in bare if p[\"species\"] == \"utility_pole\")\n"
         "    marker = tuple(pole[\"at\"])\n"
         "    pieces = site_furniture.plan_furniture(roads, markers=[marker])\n"
         "    for p in pieces:\n"
         "        assert site_furniture._clear_of_markers(p, [marker]), p\n"
         "    # the pole stepped along its band rather than vanishing\n"
         "    moved = [p for p in pieces if p[\"species\"] == \"utility_pole\" and p[\"kerb\"] == pole[\"kerb\"]\n"
         "             and abs(p[\"t\"] - pole[\"t\"]) <= max(site_poles.POLE_STEPS) + 1e-6]\n"
         "    assert moved and pole[\"t\"] not in [p[\"t\"] for p in moved]\n"),
        ("the hydrants' test",
         "    hydrants = [p for p in site_furniture.plan_furniture(roads)\n"
         "                if p[\"species\"] == \"fire_hydrant\"]\n"
         "    assert {p[\"kerb\"] for p in hydrants} == {\"L\", \"R\"}\n",
         "    # WITH THE LAMPS ON THE POLES (0.118.0) the probe's first kerb takes\n"
         "    # every corner hydrant the site's spacing allows -- its lamps had\n"
         "    # refused two of them, which left room on the other kerb -- so the\n"
         "    # right kerb's hydrants this test turns are made the way a marker\n"
         "    # makes them: one on each left-kerb hydrant skips it\n"
         "    left = [tuple(p[\"at\"]) for p in site_furniture.plan_furniture(roads)\n"
         "            if p[\"species\"] == \"fire_hydrant\" and p[\"kerb\"] == \"L\"]\n"
         "    hydrants = [p for p in site_furniture.plan_furniture(roads, markers=left)\n"
         "                if p[\"species\"] == \"fire_hydrant\"]\n"
         "    assert \"R\" in {p[\"kerb\"] for p in hydrants}\n"),
        ("the import",
         "import site_furniture   # noqa: E402\n"
         "import site_streets     # noqa: E402\n",
         "import site_furniture   # noqa: E402\n"
         "import site_poles       # noqa: E402\n"
         "import site_streets     # noqa: E402\n"),
    ],
    "tests/test_site_band_clear.py": [
        ("the docstring",
         '"""A lamp or a tree keeps out of a shop band\'s span (0.106.0).\n',
         '"""A pole or a tree keeps out of a shop band\'s span (0.106.0; the pole since 0.118.0).\n'),
        ("the lamp helper and the lamp tests",
         "def _lamps(pieces, kerb):\n"
         '    return sorted(p["t"] for p in pieces if p["species"] == "streetlight" and p["kerb"] == kerb)\n',
         "def _poles(pieces, kerb=None):\n"
         '    return sorted(p["t"] for p in pieces if p["species"] == "utility_pole"\n'
         '                  and (kerb is None or p["kerb"] == kerb))\n'
         "\n\n"
         "def _line_kerb(pieces):\n"
         '    (side,) = {p["kerb"] for p in pieces if p["species"] == "utility_pole"}\n'
         "    return side\n"),
        ("the lamp-steps test",
         "def test_a_lamp_in_front_of_a_band_steps_to_its_nearer_end():\n"
         "    roads = _roads()\n"
         '    assert 55.0 in _lamps(site_furniture.plan_furniture(roads), "L")\n'
         "    # the band behind the left kerb, centred at station 56: 51.5 to 60.5, widened to 51 to 61\n"
         '    pieces = site_furniture.plan_furniture(roads, sign_bands=[_band(-54.0, 12.0)])\n'
         '    left = _lamps(pieces, "L")\n'
         "    assert 55.0 not in left\n"
         '    half = site_furniture.SPECIES["streetlight"][1] / 2.0\n'
         "    assert abs(min(left, key=lambda t: abs(t - 51.0)) - (51.0 - half - site_furniture.PIECE_GAP)) < 1e-9\n"
         "    assert not [t for t in left if 51.0 - half < t < 61.0 + half]\n",
         "def _a_band_on_a_pole(roads):\n"
         '    """A pole of the bare plan standing at its own station -- stepped off\n'
         "    nothing, so the station a finding names is the pole's -- and a 9 m band\n"
         "    centred on it behind its kerb (the probe road runs along x from -110, so\n"
         '    station t is x = t - 110)."""\n'
         "    bare = site_furniture.plan_furniture(roads)\n"
         "    side = _line_kerb(bare)\n"
         "    sign = 1.0 if side == \"L\" else -1.0\n"
         "    (road,) = [r for r in roads if r.a[1] == 0.0]\n"
         "    nominal = [round(t, 3) for t, _r0, _r1 in site_poles.stations(road, road.kerb(side))]\n"
         "    for t in _poles(bare, side):\n"
         "        if 20.0 < t < 200.0 and t in nominal:\n"
         "            # and the same band behind the other kerb: a band on one kerb\n"
         "            # alone would move the whole line across the road (`pole_kerb`\n"
         "            # takes the kerb with less to dodge), which is not what is tried\n"
         "            return bare, side, t, [_band(t - 110.0, 12.0 * sign),\n"
         "                                   _band(t - 110.0, -12.0 * sign)]\n"
         '    raise AssertionError("no pole of the probe stands at its own station")\n'
         "\n\n"
         "def test_a_pole_in_front_of_a_band_steps_out_of_it():\n"
         "    roads = _roads()\n"
         "    bare, side, t, bands = _a_band_on_a_pole(roads)\n"
         "    pieces = site_furniture.plan_furniture(roads, sign_bands=bands)\n"
         "    got = _poles(pieces, side)\n"
         "    assert t not in got\n"
         "    # the band is t-4.5..t+4.5, widened by SIGN_CLEAR; no pole's column inside it\n"
         "    half = site_poles.POLE_FOOTPRINT[0] / 2.0\n"
         "    lo, hi = t - 4.5 - site_furniture.SIGN_CLEAR, t + 4.5 + site_furniture.SIGN_CLEAR\n"
         "    assert not [s for s in got if lo - half < s < hi + half]\n"
         "    # and it stepped out rather than vanishing: a pole's own steps come first\n"
         "    # (6 m clears a 9 m band from its middle), the band's ends after them\n"
         "    assert len(got) == len(_poles(bare, side))\n"
         "    end = 4.5 + site_furniture.SIGN_CLEAR + half + site_furniture.PIECE_GAP\n"
         "    assert min(abs(s - t) for s in got) <= max(max(site_poles.POLE_STEPS), end) + 1e-6\n"),
        ("the across-the-road test",
         "def test_a_band_across_the_road_moves_nothing_on_this_kerb():\n"
         "    roads = _roads()\n"
         "    bare = site_furniture.plan_furniture(roads)\n"
         '    pieces = site_furniture.plan_furniture(roads, sign_bands=[_band(-54.0, -12.0)])\n'
         '    assert _lamps(pieces, "L") == _lamps(bare, "L")\n'
         '    assert 55.0 in _lamps(bare, "R") and 55.0 not in _lamps(pieces, "R")\n',
         "def test_a_band_across_the_road_moves_no_pole():\n"
         "    roads = _roads()\n"
         "    bare, side, t, bands = _a_band_on_a_pole(roads)\n"
         "    pieces = site_furniture.plan_furniture(roads, sign_bands=bands[1:])\n"
         "    assert _poles(pieces) == _poles(bare)\n"),
        ("the other-road test",
         "    near = [r for r in roads if r.a[1] == 0.0][0]\n"
         '    ours = lambda ps: sorted(p["t"] for p in ps if p["species"] == "streetlight"\n'
         '                             and p["road"] == near.index)\n',
         "    near = [r for r in roads if r.a[1] == 0.0][0]\n"
         '    ours = lambda ps: sorted(p["t"] for p in ps if p["species"] == "utility_pole"\n'
         '                             and p["road"] == near.index)\n'),
        ("the finding test",
         "def test_the_finding_names_the_piece_and_both_stations():\n"
         "    findings = []\n"
         "    site_furniture.plan_furniture(_roads(), findings=findings, sign_bands=[_band(-54.0, 12.0)])\n"
         '    said = [f for f in findings if f.startswith("LOT_BAND_KEPT_CLEAR:")]\n'
         "    assert len(said) == 1\n"
         '    assert "would have stood at station 55.00" in said[0] and "it stands at 50.55" in said[0]\n',
         "def test_the_finding_names_the_pole_and_both_stations():\n"
         "    roads = _roads()\n"
         "    bare, side, t, bands = _a_band_on_a_pole(roads)\n"
         "    findings = []\n"
         "    pieces = site_furniture.plan_furniture(roads, findings=findings, sign_bands=bands)\n"
         '    said = [f for f in findings if f.startswith("LOT_BAND_KEPT_CLEAR: Pole_")]\n'
         "    assert len(said) == 1, said\n"
         "    moved = min(_poles(pieces, side), key=lambda s: abs(s - t))\n"
         '    assert f"would have stood at station {t:.2f}" in said[0], said[0]\n'
         '    assert f"it stands at {moved:.2f}" in said[0], said[0]\n'),
        ("the import",
         "import lot              # noqa: E402\n"
         "import site_furniture   # noqa: E402\n",
         "import lot              # noqa: E402\n"
         "import site_furniture   # noqa: E402\n"
         "import site_poles       # noqa: E402\n"),
    ],
    "tests/test_lot.py": [
        ("the lights-on-poles test",
         '    poles = [p for p in site_furniture.plan_furniture(site_streets.roads(spec))\n'
         '             if p["species"] == "streetlight"]\n'
         '    assert poles, "the probe spec stands no lamps, so this proves nothing"\n',
         "    import site_poles\n"
         "    # THE LAMPS ARE ON THE POLES (0.118.0): a cobra-head on every utility\n"
         "    # pole, its light at the lens -- 2.171 m out on its arm, not on the axis\n"
         '    poles = [p for p in site_furniture.plan_furniture(site_streets.roads(spec))\n'
         '             if p["species"] == "utility_pole"]\n'
         '    assert poles, "the probe spec stands no poles, so this proves nothing"\n'),
        ("the coincidence check",
         "    for a in lights:\n"
         '        best = min(math.hypot(a["pos"][0] - p["at"][0], a["pos"][1] - p["at"][1])\n'
         "                   for p in poles)\n"
         '        assert best <= 0.001, (a["id"], best)     # coincident, not merely near\n'
         "        # the lamp point is under the lens, which is 0.175 below the module's\n"
         "        # top -- a light at the top would be inside the shoebox head\n"
         "        # rounded to 3 dp the way every other anchor coordinate is, so the\n"
         "        # expected value is rounded too rather than given a tolerance that\n"
         "        # would also pass for a light 4 mm into the head\n"
         '        assert a["pos"][2] == round(\n'
         "            lot.SIDEWALK_H + 6.0 - lot.STREETLIGHT_LENS_DROP, 3)\n",
         "    lenses = [site_poles.lens_point(p, lot.SIDEWALK_H) for p in poles]\n"
         "    for a in lights:\n"
         '        best = min(math.hypot(a["pos"][0] - lx, a["pos"][1] - ly) for lx, ly, _lz in lenses)\n'
         '        assert best <= 0.001, (a["id"], best)     # at its lens, not merely near\n'
         "        # the lens's own height, rounded as every anchor coordinate is\n"
         '        assert a["pos"][2] == round(lot.SIDEWALK_H + site_poles.LENS_AT[1], 3)\n'),
    ],
    "tests/test_lane_lamps.py": [
        ("the streets' half",
         '    assert street and all(p.get("base") == "sidewalk" for p in street if p["species"] == "streetlight")\n',
         "    # a street's lamps are on its poles (0.118.0), and they stand on the band\n"
         '    poles = [p for p in street if p["species"] == "utility_pole"]\n'
         '    assert street and poles and all(p.get("base") == "sidewalk" for p in poles)\n'
         '    assert not [p for p in street if p["species"] == "streetlight"]\n'),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.118.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.118.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.118.0.md")
    assert entry.startswith("## 0.118.0 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LOT / rel).exists(), (rel, "already exists")
    new_text = {rel: _src(name) for rel, name in NEW.items()}
    staged = {}
    for rel, edits in EDITS.items():
        p = LOT / rel
        raw = p.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for what, old, new in edits:
            assert text.count(old) == 1, (rel, what, text.count(old))
            text = text.replace(old, new)
        staged[p] = (eol, text)
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    for rel, text in new_text.items():
        (LOT / rel).write_bytes(text.encode("utf-8"))
    for p, (eol, text) in staged.items():
        p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.117.0 -> 0.118.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
