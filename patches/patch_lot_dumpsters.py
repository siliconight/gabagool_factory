"""Lot 0.90.0: a dumpster at each building's service side. The walker,
2026-10-03: "we should have some trash dumpsters next to buildings (sides or
back where its not in the way of where customers would naturally walk into
the building)". Zoo 1.58.0 builds the species; `site_dumpsters` decides
where one stands.

`site_dumpsters.py` and `tests/test_site_dumpsters.py` copied from
`lot_dumpsters/`. Anchored edits (every anchor once; refuses on a miss):
`site_furniture.py` (`SPECIES`), `lot.py` (`COVER_MATERIALS`; the slot's
`variant`; the module name's variant rung; the planner's call in
`assemble`). CHANGELOG and VERSION from `lot_dumpsters/CHANGELOG_0.90.0.md`.

    python patch_lot_dumpsters.py
    LOT_ROOT=<copy> python patch_lot_dumpsters.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_dumpsters"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:60])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.89.0", v
    assert not (LOT / "site_dumpsters.py").exists(), "already applied"
    _edit(LOT / "site_furniture.py", [
        ('    "price_pylon": (3.4, 0.7, 9.0),\n}\n',
         '    "price_pylon": (3.4, 0.7, 9.0),\n'
         '    # THE DUMPSTER (Zoo 1.58.0), against a building\'s back or side\n'
         '    # (`site_dumpsters.plan_dumpsters`). The genome\'s default, a 3-yard\n'
         '    # front-load container.\n'
         '    "dumpster": (1.83, 1.1, 1.3),\n}\n'),
    ])
    _edit(LOT / "lot.py", [
        ('                   "price_pylon": "metal_painted",\n',
         '                   "price_pylon": "metal_painted",\n'
         '                   # the dumpster at a building\'s service side (site_dumpsters)\n'
         '                   "dumpster": "metal_painted",\n'),
        ('        if cv.get("blade"):\n'
         '            slots[-1]["form"] = str(cv["blade"])\n',
         '        if cv.get("blade"):\n'
         '            slots[-1]["form"] = str(cv["blade"])\n'
         '        # A PIECE\'S OWN VARIANT (0.90.0): a dumpster\'s hauler, which is its\n'
         '        # paint. Zoo reads the slot\'s `variant` into the stem as `_n<v>`,\n'
         '        # non-zero only, so no slot written before this moves.\n'
         '        if cv.get("variant"):\n'
         '            slots[-1]["variant"] = int(cv["variant"])\n'),
        ('        if key == "cover" or not form:\n'
         '            tried.append(cover_module_stem(sp, theme, st, dims))\n',
         '        # ...and a piece with a variant and no form asks for its own\n'
         '        # module before the plain one (0.90.0): the second hauler\'s\n'
         '        # dumpster, falling back to the first\'s rather than to a box.\n'
         '        if not form and cv.get("variant"):\n'
         '            tried.append(cover_module_stem(sp, theme, st, dims,\n'
         '                                           variant=cv["variant"]))\n'
         '        if key == "cover" or not form:\n'
         '            tried.append(cover_module_stem(sp, theme, st, dims))\n'),
        ('    site_spec["cover"].extend(pylons)\n'
         '    furniture = furniture + pylons\n',
         '    site_spec["cover"].extend(pylons)\n'
         '    furniture = furniture + pylons\n'
         '    # A DUMPSTER AT EACH BUILDING\'S SERVICE SIDE (site_dumpsters, 0.90.0):\n'
         '    # against the back or a side, never a street face, clear of every\n'
         '    # way in, of the paths and walks, of what already stands, of the\n'
         '    # markers, and on the plate. After the street and the pylons so it\n'
         '    # yields to them; before the cover planner so it stands in its\n'
         '    # measurement, as the street does.\n'
         '    import site_dumpsters\n'
         '    dumpsters = site_dumpsters.plan_dumpsters(\n'
         '        site_spec, merged, site_streets.roads(site_spec), list(cover_points.values()),\n'
         '        standing=_standing0 + [site_furniture._piece_rect(_p) for _p in pylons],\n'
         '        keep_out=site_furniture.path_corridors(site_spec),\n'
         '        ground=extent.rect, findings=furniture_findings)\n'
         '    site_spec["cover"].extend(dumpsters)\n'
         '    furniture = furniture + dumpsters\n'
         '    for _p in dumpsters:\n'
         '        print(f"[lot] LOT_DUMPSTER_PLACED: {_p[\'name\']} at ({_p[\'at\'][0]}, {_p[\'at\'][1]}) "\n'
         '              f"yaw {_p[\'yaw\']} against {_p[\'building\']}\'s {_p[\'wall\']} wall, hauler {_p[\'variant\']}")\n'),
    ])
    (LOT / "site_dumpsters.py").write_bytes((SRC / "site_dumpsters.py").read_bytes())
    (LOT / "tests" / "test_site_dumpsters.py").write_bytes((SRC / "test_site_dumpsters.py").read_bytes())
    entry = (SRC / "CHANGELOG_0.90.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.90.0" not in d and d.startswith(b"## 0.89.0")
    cl.write_bytes(entry.encode("utf-8") + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.90.0")
    print("0.89.0 -> 0.90.0")


if __name__ == "__main__":
    main()
