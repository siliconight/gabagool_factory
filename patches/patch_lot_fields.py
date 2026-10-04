"""Lot 0.94.0: a parking field in a gap between buildings. Step 4 of
`docs/proposals/LAND_USE_DESIGN.md` (open land gets a role), its second use.

`site_fields.py` and `tests/test_site_fields.py` copied from `lot_fields/`.
Anchored edits (every anchor once; refuses on a miss): `lot.py` (the
field's height and greybox colour; `parking` as a skin family;
`field_slabs`; the slab and its bay lines drawn; the skin header; the
planner's call in `assemble`, before the street's furniture, and the
fields kept clear by the pylons and the dumpsters), `site_streets.py` (a
`driveway` crosser; the bay lines in the markings manifest),
`site_furniture.py` (a driveway gets no corner furniture),
`site_surfaces.py` (`tops` declares the fields), `site_steps.py` (a field
is walked on), `site_landuse.py` (`parking` is a use). CHANGELOG and
VERSION from `lot_fields/CHANGELOG_0.94.0.md`.

    python patch_lot_fields.py
    LOT_ROOT=<copy> python patch_lot_fields.py
"""
import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_fields"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.93.0", v
    assert not (LOT / "site_fields.py").exists(), "already applied"
    _edit(LOT / "lot.py", [
        ('YARD_COLOR = (0.50, 0.50, 0.48)\n',
         'YARD_COLOR = (0.50, 0.50, 0.48)\n'
         '#: A parking field (`site_fields`): the lot\'s asphalt, a shade off the road.\n'
         'FIELD_COLOR = (0.30, 0.30, 0.31)\n'),
        ('YARD_THICK = COURT_THICK\n',
         'YARD_THICK = COURT_THICK\n'
         '#: A parking field (`site_fields`, 0.94.0): at the road\'s own height, so the\n'
         '#: asphalt runs on from the carriageway through the driveway\'s dropped\n'
         '#: kerb into the field, and the bay lines sit at `MARKING_Y` over it as\n'
         '#: the road\'s paint does over the road. `plan_fields` never lets a field\n'
         '#: overlap another drawn surface, so the shared tier makes no coplanar face.\n'
         'FIELD_THICK = ROAD_THICK\n'),
        ('SKIN_FAMILIES = ("ground", "path", "courtyard", "road", "sidewalk", "paint", "yard")\n',
         'SKIN_FAMILIES = ("ground", "path", "courtyard", "road", "sidewalk", "paint", "yard",\n'
         '                 "parking")\n'),
        ('def street_slabs(street_roads):\n',
         'def field_slabs(site_spec):\n'
         '    """One slab per parking field (`site_fields`, 0.94.0), `field_<i>`, top\n'
         '    at FIELD_THICK, turned to its road: local x runs along the road."""\n'
         '    out = []\n'
         '    for i, f in enumerate(site_spec.get("fields", []) or []):\n'
         '        cx, cy = f["at"]\n'
         '        sx, sy = f["size"]\n'
         '        out.append(_surface_slab(f"field_{i}", "parking",\n'
         '                                 (sx, FIELD_THICK + GROUND_SINK, sy),\n'
         '                                 (cx, (FIELD_THICK - GROUND_SINK) / 2, -cy),\n'
         '                                 f["yaw_deg"], FIELD_THICK))\n'
         '    return out\n'
         '\n'
         '\n'
         'def street_slabs(street_roads):\n'),
        ('    # the service pads under the dumpsters (`site_yards`, 0.93.0)\n',
         '    # the parking fields in the gaps (`site_fields`, 0.94.0)\n'
         '    for s in field_slabs(site_spec):\n'
         '        bl, sr = _yaw_box_node(s["name"], s["size"], s["centre"], s["yaw_deg"],\n'
         '                               FIELD_COLOR, skin=skins.get("parking"))\n'
         '        body += bl\n'
         '        sub += sr\n'
         '\n'
         '    # the service pads under the dumpsters (`site_yards`, 0.93.0)\n'),
        ('    # THE SHOP SIGNS. A lit cabinet over each door, on the facade that\n',
         '    # THE FIELDS\' BAY LINES (`site_fields`, 0.94.0): the road\'s paint, the\n'
         '    # road\'s quads, at the road\'s height -- a field sits at it.\n'
         '    import site_fields as _site_fields\n'
         '    for n, m in enumerate(_site_fields.markings(site_spec.get("fields") or [], street_roads)):\n'
         '        along, across = m["size"]\n'
         '        paint = skins.get("paint")\n'
         '        offset = (paint_offset(f"{m[\'field\']}|{m[\'kind\']}|{m[\'at\'][0]:.3f}|{m[\'at\'][1]:.3f}")\n'
         '                  if paint else None)\n'
         '        bl, sr = _yaw_quad_node(f"fmark_{n}_{m[\'kind\']}", (along, across),\n'
         '                                (m["at"][0], MARKING_Y, -m["at"][1]),\n'
         '                                m["yaw"], tuple(m["color"]), skin=paint,\n'
         '                                uv_offset=offset)\n'
         '        body += bl\n'
         '        sub += sr\n'
         '\n'
         '    # THE SHOP SIGNS. A lit cabinet over each door, on the facade that\n'),
        ('               "yard": bool(site_spec.get("yards")),\n',
         '               "yard": bool(site_spec.get("yards")),\n'
         '               "parking": bool(site_spec.get("fields")),\n'),
        ('    import site_furniture\n'
         '    import site_parking\n'
         '    import site_streets\n'
         '    furniture_findings = []\n',
         '    # A PARKING FIELD IN A GAP BETWEEN BUILDINGS (site_fields, 0.94.0),\n'
         '    # BEFORE the street\'s furniture: its driveway is a kerb cut, and the\n'
         '    # lamps, the trees and the kerb lane\'s bays already step round a cut.\n'
         '    # The pylons, dumpsters and pads planned after it keep off it.\n'
         '    import site_enterability as _fe\n'
         '    import site_extent as _fx\n'
         '    import site_fields\n'
         '    import site_streets as _fs\n'
         '    import site_surfaces as _fsurf\n'
         '    _rects_f = {}\n'
         '    for _b in site_spec.get("buildings", []) or []:\n'
         '        _r = _fx.rotated_footprint(_b)\n'
         '        if _r is not None:\n'
         '            _rects_f[_b["id"]] = _r\n'
         '    _standing_f = []\n'
         '    for cv in site_spec.get("cover", []) or []:\n'
         '        sx, _sy, sz = cv.get("size", COVER)\n'
         '        _standing_f.append((cv["at"][0] - sx / 2.0, cv["at"][1] - sz / 2.0,\n'
         '                            cv["at"][0] + sx / 2.0, cv["at"][1] + sz / 2.0))\n'
         '    fields = site_fields.plan_fields(site_spec, _fs.roads(site_spec),\n'
         '                                     _fsurf.tops(site_spec, ground=extent), _rects_f,\n'
         '                                     standing=_standing_f, ground=extent.rect)\n'
         '    site_spec["fields"] = fields\n'
         '    site_spec["driveways"] = [f["driveway"] for f in fields]\n'
         '    _aps = [ap for rows in _fe._approach_points(site_spec, merged).values() for (_e, ap, _w) in rows]\n'
         '    field_cars = site_fields.plan_cars(fields, _fs.roads(site_spec), list(cover_points.values()),\n'
         '                                       _aps, standing=_standing_f,\n'
         '                                       enemies=[p for n, p in cover_points.items()\n'
         '                                                if n.startswith("Enemy_")])\n'
         '    _c0 = len(site_spec.setdefault("cover", []))\n'
         '    site_spec["cover"].extend(field_cars)\n'
         '    # the cars and the scene nodes they become (`cover_<i>`), so a probe can\n'
         '    # find them in a built package\n'
         '    merged["field_plan"] = {"placed": fields, "cars": field_cars,\n'
         '                           "cover_index": list(range(_c0, _c0 + len(field_cars)))}\n'
         '    for _f in fields:\n'
         '        print(f"[lot] LOT_FIELD_PLACED: {_f[\'name\']} on road {_f[\'road\']} kerb {_f[\'side\']}, "\n'
         '              f"{_f[\'bays\']} bay(s) a side, {sum(1 for c in field_cars if c[\'field\'] == _f[\'name\'])} car(s)")\n'
         '    _field_rects = [tuple(f["rect"]) for f in fields]\n'
         '    import site_furniture\n'
         '    import site_parking\n'
         '    import site_streets\n'
         '    furniture_findings = []\n'),
        ('        keep_out=site_furniture.path_corridors(site_spec) + _site_spawns.footprints(site_spec, margin=0.5),\n',
         '        keep_out=site_furniture.path_corridors(site_spec) + _site_spawns.footprints(site_spec, margin=0.5)\n'
         '        + _field_rects,\n'),
        ('        keep_out=site_furniture.path_corridors(site_spec),\n',
         '        keep_out=site_furniture.path_corridors(site_spec) + _field_rects,\n'),
    ])
    _edit(LOT / "site_streets.py", [
        ('    crossers += [(r, float(r.get("width", 9.0)), "road", float(r.get("sidewalk") or 0.0), ri)\n'
         '                 for ri, r in enumerate(site_spec.get("roads", []) or [])]\n',
         '    crossers += [(r, float(r.get("width", 9.0)), "road", float(r.get("sidewalk") or 0.0), ri)\n'
         '                 for ri, r in enumerate(site_spec.get("roads", []) or [])]\n'
         '    # A PARKING FIELD\'S DRIVEWAY (`site_fields`, 0.94.0): from the\n'
         '    # carriageway\'s edge to the back of walk, so it drops the one kerb it\n'
         '    # crosses and never meets the centre line -- no crosswalk, no stop bar\n'
         '    crossers += [(d, float(d.get("width", 7.3)), "driveway", 0.0, -1)\n'
         '                 for d in site_spec.get("driveways", []) or []]\n'),
        ('        "markings": markings(rl),\n',
         '        # the road\'s paint, then the parking fields\' bay lines (0.94.0)\n'
         '        "markings": markings(rl) + _field_markings(site_spec, rl),\n'),
        ('def manifest(site_spec, roads_list=None, findings=None) -> dict:\n',
         'def _field_markings(site_spec, rl):\n'
         '    import site_fields\n'
         '    return site_fields.markings(site_spec.get("fields") or [], rl)\n'
         '\n'
         '\n'
         'def manifest(site_spec, roads_list=None, findings=None) -> dict:\n'),
    ])
    _edit(LOT / "tests" / "test_site_streets.py", [
        ('    assert {m["kind"] for m in doc["markings"]} == {"edge_line", "centre_line", "crosswalk_bar",\n'
         '                                                    "stop_bar", "bay_tick"}\n',
         '    # 0.94.0: the probe\'s gaps hold a parking field, whose bay lines are\n'
         '    # in the manifest beside the road\'s paint\n'
         '    assert {m["kind"] for m in doc["markings"]} == {"edge_line", "centre_line", "crosswalk_bar",\n'
         '                                                    "stop_bar", "bay_tick", "bay_line"}\n'),
    ])
    _edit(LOT / "site_furniture.py", [
        ('            for c in sorted(kerb.cuts, key=lambda c: c.t):\n'
         '                half = c.span / 2.0 + CUT_CLEARANCE\n',
         '            for c in sorted(kerb.cuts, key=lambda c: c.t):\n'
         '                # a parking field\'s driveway (0.94.0) is not a crossing:\n'
         '                # nobody is meant to cross there, so no hydrant, bin or blade\n'
         '                if c.kind == "driveway":\n'
         '                    continue\n'
         '                half = c.span / 2.0 + CUT_CLEARANCE\n'),
    ])
    _edit(LOT / "site_surfaces.py", [
        ('              + lot.yard_slabs(site_spec)\n',
         '              + lot.yard_slabs(site_spec) + lot.field_slabs(site_spec)\n'),
    ])
    _edit(LOT / "site_steps.py", [
        ('                     "kerbcut_", "frontage_", "yard_")\n',
         '                     "kerbcut_", "frontage_", "yard_", "field_")\n'),
    ])
    _edit(LOT / "site_landuse.py", [
        ('    (a walk or a landing), ``courtyard``, ``yard`` (a service pad,\n'
         '    `site_yards`);\n',
         '    (a walk or a landing), ``courtyard``, ``yard`` (a service pad,\n'
         '    `site_yards`), ``parking`` (a parking field, `site_fields`);\n'),
        ('USES = ("building", "road", "kerbcut", "sidewalk", "frontage", "path", "courtyard", "yard",\n'
         '        "remainder")\n',
         'USES = ("building", "road", "kerbcut", "sidewalk", "frontage", "path", "courtyard", "yard",\n'
         '        "parking", "remainder")\n'),
    ])
    shutil.copyfile(SRC / "site_fields.py", LOT / "site_fields.py")
    shutil.copyfile(SRC / "test_site_fields.py", LOT / "tests" / "test_site_fields.py")
    ch = LOT / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    entry = (SRC / "CHANGELOG_0.94.0.md").read_text(encoding="utf-8")
    anchor = "## 0.93.0 - "
    assert s.count(anchor) == 1, "changelog anchor"
    ch.write_text(s.replace(anchor, entry.rstrip("\n") + "\n\n" + anchor), encoding="utf-8", newline="\n")
    (LOT / "VERSION").write_text("Lot 0.94.0", encoding="utf-8", newline="\n")
    print("Lot 0.94.0 applied")


if __name__ == "__main__":
    main()
