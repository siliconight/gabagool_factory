"""Lot 0.93.0: a concrete service pad under each dumpster. Step 4 of
`docs/proposals/LAND_USE_DESIGN.md` (open land gets a role), its first use.

`site_yards.py` and `tests/test_site_yards.py` copied from `lot_yards/`.
Anchored edits (every anchor once; refuses on a miss): `lot.py` (the
pad's height and greybox colour; `yard` as a skin family; `yard_slabs`;
the drawing; the skin header; the planner's call in `assemble`),
`site_surfaces.py` (`tops` declares the pads), `site_steps.py` (a pad is
walked on), `site_landuse.py` (`yard` is a use). CHANGELOG and VERSION
from `lot_yards/CHANGELOG_0.93.0.md`.

    python patch_lot_yards.py
    LOT_ROOT=<copy> python patch_lot_yards.py
"""
import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_yards"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:60])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.92.0", v
    assert not (LOT / "site_yards.py").exists(), "already applied"
    _edit(LOT / "lot.py", [
        ('COURT_COLOR = (0.48, 0.52, 0.55)       # 0.514 -- path\'s band, cool cast names it apart\n',
         'COURT_COLOR = (0.48, 0.52, 0.55)       # 0.514 -- path\'s band, cool cast names it apart\n'
         '#: A service pad (`site_yards`): plain concrete, greyer than the walk.\n'
         'YARD_COLOR = (0.50, 0.50, 0.48)\n'),
        ('COURT_THICK = SURFACE_BASE + 2 * SURFACE_TIER\n',
         'COURT_THICK = SURFACE_BASE + 2 * SURFACE_TIER\n'
         '#: A service pad under a dumpster (`site_yards`, 0.93.0). It shares the\n'
         '#: courtyard\'s tier because `plan_yards` never lets a pad overlap any\n'
         '#: other drawn surface, so there is no coplanar face for a tier to part.\n'
         'YARD_THICK = COURT_THICK\n'),
        ('SKIN_FAMILIES = ("ground", "path", "courtyard", "road", "sidewalk", "paint")\n',
         'SKIN_FAMILIES = ("ground", "path", "courtyard", "road", "sidewalk", "paint", "yard")\n'),
        ('def street_slabs(street_roads):\n',
         'def yard_slabs(site_spec):\n'
         '    """One axis-aligned slab per service pad (`site_yards`, 0.93.0),\n'
         '    `yard_<i>`, top at YARD_THICK -- a courtyard\'s shape."""\n'
         '    out = []\n'
         '    for i, y in enumerate(site_spec.get("yards", []) or []):\n'
         '        cx, cy = y["at"]\n'
         '        sx, sy = y["size_x"], y["size_y"]\n'
         '        out.append(_surface_slab(f"yard_{i}", "yard",\n'
         '                                 (sx, YARD_THICK + GROUND_SINK, sy),\n'
         '                                 (cx, (YARD_THICK - GROUND_SINK) / 2, -cy),\n'
         '                                 None, YARD_THICK))\n'
         '    return out\n'
         '\n'
         '\n'
         'def street_slabs(street_roads):\n'),
        ('    for s in courtyard_slabs(site_spec):\n'
         '        bl, sr = _box_node(s["name"], s["size"], s["centre"],\n'
         '                           COURT_COLOR, skin=skins.get("courtyard"))\n'
         '        body += bl\n'
         '        sub += sr\n',
         '    for s in courtyard_slabs(site_spec):\n'
         '        bl, sr = _box_node(s["name"], s["size"], s["centre"],\n'
         '                           COURT_COLOR, skin=skins.get("courtyard"))\n'
         '        body += bl\n'
         '        sub += sr\n'
         '\n'
         '    # the service pads under the dumpsters (`site_yards`, 0.93.0)\n'
         '    for s in yard_slabs(site_spec):\n'
         '        bl, sr = _box_node(s["name"], s["size"], s["centre"],\n'
         '                           YARD_COLOR, skin=skins.get("yard"))\n'
         '        body += bl\n'
         '        sub += sr\n'),
        ('               "courtyard": bool(site_spec.get("courtyards")),\n',
         '               "courtyard": bool(site_spec.get("courtyards")),\n'
         '               "yard": bool(site_spec.get("yards")),\n'),
        ('    for _p in dumpsters:\n'
         '        print(f"[lot] LOT_DUMPSTER_PLACED: {_p[\'name\']} at ({_p[\'at\'][0]}, {_p[\'at\'][1]}) "\n'
         '              f"yaw {_p[\'yaw\']} against {_p[\'building\']}\'s {_p[\'wall\']} wall, hauler {_p[\'variant\']}")\n',
         '    for _p in dumpsters:\n'
         '        print(f"[lot] LOT_DUMPSTER_PLACED: {_p[\'name\']} at ({_p[\'at\'][0]}, {_p[\'at\'][1]}) "\n'
         '              f"yaw {_p[\'yaw\']} against {_p[\'building\']}\'s {_p[\'wall\']} wall, hauler {_p[\'variant\']}")\n'
         '    # ...ON A CONCRETE PAD (site_yards, 0.93.0): the ground under and in\n'
         '    # front of each dumpster, clear of every surface already drawn, of\n'
         '    # the neighbours, of what stands and of the plate\'s edge. Drawn as\n'
         '    # `yard` slabs; the plate under them stops being remainder.\n'
         '    import site_surfaces as _yard_surfaces\n'
         '    import site_yards\n'
         '    _yard_findings = []\n'
         '    _standing_y = []\n'
         '    for cv in site_spec["cover"]:\n'
         '        sx, _sy, sz = cv.get("size", COVER)\n'
         '        _standing_y.append((cv["at"][0] - sx / 2.0, cv["at"][1] - sz / 2.0,\n'
         '                            cv["at"][0] + sx / 2.0, cv["at"][1] + sz / 2.0))\n'
         '    yards = site_yards.plan_yards(\n'
         '        site_spec, dumpsters, _yard_surfaces.tops(site_spec, ground=extent),\n'
         '        standing=_standing_y, ground=extent.rect, findings=_yard_findings)\n'
         '    site_spec["yards"] = list(site_spec.get("yards") or []) + yards\n'
         '    merged["yard_plan"] = {"placed": yards, "findings": _yard_findings}\n'
         '    for _y in yards:\n'
         '        print(f"[lot] LOT_YARD_PLACED: pad {_y[\'size_x\']} x {_y[\'size_y\']} m at "\n'
         '              f"({_y[\'at\'][0]}, {_y[\'at\'][1]}) under {_y[\'dumpster\']}, apron {_y[\'apron\']} m")\n'
         '    for f_ in _yard_findings:\n'
         '        print(f"[lot] {f_}")\n'),
    ])
    _edit(LOT / "site_surfaces.py", [
        ('    for s in (lot.path_slabs(site_spec) + lot.courtyard_slabs(site_spec)\n'
         '              + lot.street_slabs(street)\n',
         '    for s in (lot.path_slabs(site_spec) + lot.courtyard_slabs(site_spec)\n'
         '              + lot.yard_slabs(site_spec)\n'
         '              + lot.street_slabs(street)\n'),
    ])
    _edit(LOT / "site_steps.py", [
        ('WALKABLE_PREFIXES = ("Ground", "road_", "sidewalk_", "path_", "courtyard_",\n'
         '                     "kerbcut_", "frontage_")\n',
         'WALKABLE_PREFIXES = ("Ground", "road_", "sidewalk_", "path_", "courtyard_",\n'
         '                     "kerbcut_", "frontage_", "yard_")\n'),
    ])
    _edit(LOT / "site_landuse.py", [
        ('    (a walk or a landing), ``courtyard``;\n',
         '    (a walk or a landing), ``courtyard``, ``yard`` (a service pad,\n'
         '    `site_yards`);\n'),
        ('USES = ("building", "road", "kerbcut", "sidewalk", "frontage", "path", "courtyard", "remainder")\n',
         'USES = ("building", "road", "kerbcut", "sidewalk", "frontage", "path", "courtyard", "yard",\n'
         '        "remainder")\n'),
    ])
    shutil.copyfile(SRC / "site_yards.py", LOT / "site_yards.py")
    shutil.copyfile(SRC / "test_site_yards.py", LOT / "tests" / "test_site_yards.py")
    ch = LOT / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    entry = (SRC / "CHANGELOG_0.93.0.md").read_text(encoding="utf-8")
    anchor = "## 0.92.0 - "
    assert s.count(anchor) == 1, "changelog anchor"
    ch.write_text(s.replace(anchor, entry.rstrip("\n") + "\n\n" + anchor), encoding="utf-8", newline="\n")
    (LOT / "VERSION").write_text("Lot 0.93.0", encoding="utf-8", newline="\n")
    print("Lot 0.93.0 applied")


if __name__ == "__main__":
    main()
