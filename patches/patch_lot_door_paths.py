"""Lot 0.88.0: a path meets a door, not the middle of a wall. The walker,
2026-10-03: "sidewalks don't consistently lead up to doors which seems
random" / "lot still not drawing walkways to open doorways". A new
`site_paths` module snaps every path end that belongs to a building to the
nearest door on the facade it meets, once, after the gameplay merge; one
`endpoints` reader replaces the seven inline resolutions to building
centres.

Anchored edits (every anchor once per file; refuses on a miss): `lot.py`
(`path_slabs`, and the call in `assemble` after the merge),
`site_enterability.py` (`_near_route`), `site_surfaces.py`, `site_steps.py`,
`site_streets.py` (`_endpoints`), `site_extent.py` (`_ends`).
`site_paths.py` and `tests/test_site_paths.py` copied from `lot_door_paths/`;
CHANGELOG and VERSION from `lot_door_paths/CHANGELOG_0.88.0.md`.

    python patch_lot_door_paths.py
    LOT_ROOT=<copy> python patch_lot_door_paths.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_door_paths"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:60])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.87.0", v
    assert not (LOT / "site_paths.py").exists(), "already applied"

    _edit(LOT / "lot.py", [
        ('    bld = {b["id"]: b for b in site_spec["buildings"]}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_spec.get("paths", [])):\n'
         '        w = p.get("width", 3.0)\n'
         '        a = bld[p["from"]]["at"] if "from" in p else p["a"]\n'
         '        b2 = bld[p["to"]]["at"] if "to" in p else p["b"]\n',
         '    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec["buildings"]}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_spec.get("paths", [])):\n'
         '        w = p.get("width", 3.0)\n'
         '        # the resolved ends (0.88.0): a door, where the facade has one\n'
         '        a, b2 = site_paths.endpoints(p, bld)\n'),
        ('    merged = merge_gameplay(site_spec, base_dir)\n'
         '    merged["tactical"] = tactical_report\n',
         '    merged = merge_gameplay(site_spec, base_dir)\n'
         '    merged["tactical"] = tactical_report\n'
         '\n'
         '    # Every path end that belongs to a building meets one of its doors\n'
         '    # (0.88.0). Here, after the merge that knows the doors and before\n'
         '    # anything reads a path: the slabs, the surface zones, the step and\n'
         '    # kerb gates, the plate extent and the enterability route check all\n'
         '    # read the same resolved ends from the spec\'s own path records.\n'
         '    import site_paths\n'
         '    for f_ in site_paths.snap_to_doors(site_spec, merged):\n'
         '        tactical_report.setdefault("findings", []).append(f_)\n'
         '        print(f"[lot] {f_[\'code\']}: {f_[\'message\']}")\n'),
    ])
    _edit(LOT / "site_enterability.py", [
        ('    for p in paths:\n'
         '        a = bld[p["from"]]["at"] if "from" in p else p.get("a")\n'
         '        b2 = bld[p["to"]]["at"] if "to" in p else p.get("b")\n'
         '        if a is None or b2 is None:\n'
         '            continue\n',
         '    import site_paths\n'
         '    for p in paths:\n'
         '        a, b2 = site_paths.endpoints_or_none(p, bld)\n'
         '        if a is None or b2 is None:\n'
         '            continue\n'),
    ])
    _edit(LOT / "site_surfaces.py", [
        ('        try:\n'
         '            a = bld[p["from"]]["at"] if "from" in p else p["a"]\n'
         '            b = bld[p["to"]]["at"] if "to" in p else p["b"]\n'
         '        except (KeyError, TypeError):\n'
         '            continue\n'
         '        label = (f"{p.get(\'from\', \'a\')}_{p.get(\'to\', \'b\')}"\n',
         '        try:\n'
         '            a, b = site_paths.endpoints(p, bld)\n'
         '        except (KeyError, TypeError):\n'
         '            continue\n'
         '        label = (f"{p.get(\'from\', \'a\')}_{p.get(\'to\', \'b\')}"\n'),
        ('    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_spec.get("paths", []) or []):\n'
         '        try:\n'
         '            a, b = site_paths.endpoints(p, bld)\n',
         '    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_spec.get("paths", []) or []):\n'
         '        try:\n'
         '            a, b = site_paths.endpoints(p, bld)\n'),
    ])
    _edit(LOT / "site_steps.py", [
        ('    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for p in site_spec.get("paths", []) or []:\n'
         '        try:\n'
         '            a = bld[p["from"]]["at"] if "from" in p else p["a"]\n'
         '            b = bld[p["to"]]["at"] if "to" in p else p["b"]\n'
         '        except (KeyError, TypeError):\n'
         '            continue\n',
         '    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for p in site_spec.get("paths", []) or []:\n'
         '        try:\n'
         '            a, b = site_paths.endpoints(p, bld)\n'
         '        except (KeyError, TypeError):\n'
         '            continue\n'),
    ])
    _edit(LOT / "site_streets.py", [
        ('def _endpoints(rec, bld):\n'
         '    a = bld[rec["from"]]["at"] if "from" in rec else rec["a"]\n'
         '    b = bld[rec["to"]]["at"] if "to" in rec else rec["b"]\n'
         '    return (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))\n',
         'def _endpoints(rec, bld):\n'
         '    # the one reader (0.88.0): resolved a/b first, centres otherwise\n'
         '    import site_paths\n'
         '    return site_paths.endpoints(rec, bld)\n'),
    ])
    _edit(LOT / "site_extent.py", [
        ('    def _ends(defn):\n'
         '        a = at_of.get(defn.get("from")) if "from" in defn else _point(defn.get("a"))\n'
         '        b = at_of.get(defn.get("to")) if "to" in defn else _point(defn.get("b"))\n'
         '        return a, b\n',
         '    def _ends(defn):\n'
         '        # the one reader (0.88.0): resolved a/b first, centres otherwise\n'
         '        import site_paths\n'
         '        a, b = site_paths.endpoints_or_none(\n'
         '            defn, {k: {"at": v} for k, v in at_of.items() if v is not None})\n'
         '        return _point(a), _point(b)\n'),
    ])
    (LOT / "site_paths.py").write_bytes((SRC / "site_paths.py").read_bytes())
    (LOT / "tests" / "test_site_paths.py").write_bytes((SRC / "test_site_paths.py").read_bytes())
    entry = (SRC / "CHANGELOG_0.88.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.88.0" not in d
    head = b"## 0.87.0"
    assert d.startswith(head)
    cl.write_bytes(entry.encode("utf-8") + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.88.0")
    print("0.87.0 -> 0.88.0")


if __name__ == "__main__":
    main()
