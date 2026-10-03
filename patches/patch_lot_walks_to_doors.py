"""Lot 0.91.0: a walk leads to a door, and a side door gets a landing. The
walker, 2026-10-03, walking 0.90.0: "still have sidewalks going to walls",
and of the square walk between two side doors, "looks better, but you
should do some research as to what looks more natural on a path between
the sides of 2 buildings". The research and the measurements are in
`docs/findings/entry_paths/NOTES.md`.

`site_paths.py` replaced whole from `lot_walks_to_doors/` (refuses unless
the file on disk is 0.89.0's, byte for byte: `lot_walk_legs` applied over
`lot_door_paths`); `tests/test_site_paths.py` replaced. Anchored edits
(every anchor once; refuses on a miss): the six readers that draw or
measure a walk read `site_paths.drawn` -- `lot.path_slabs`,
`site_enterability._near_route` (and not a landing), `site_furniture.
path_corridors`, `site_steps.routes`, `site_streets.kerb_crossings`,
`site_surfaces._path_segments`. CHANGELOG and VERSION from
`lot_walks_to_doors/CHANGELOG_0.91.0.md`.

    python patch_lot_walks_to_doors.py
    LOT_ROOT=<copy> python patch_lot_walks_to_doors.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_walks_to_doors"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.90.0", v
    cur = (LOT / "site_paths.py").read_bytes()
    want = (HERE / "lot_walks_to_doors" / "site_paths_089.sha256").read_text().strip()
    assert hashlib.sha256(cur).hexdigest() == want, "site_paths.py is not 0.89.0's"
    _edit(LOT / "lot.py", [
        ('    for i, p in enumerate(site_spec.get("paths", [])):\n'
         '        w = p.get("width", 3.0)\n'
         '        # the resolved ends (0.88.0): a door, where the facade has one\n',
         '    # what is drawn (0.91.0): a walk to a door, a landing at one\n'
         '    for i, p in enumerate(site_paths.drawn(site_spec)):\n'
         '        w = p.get("width", 3.0)\n'
         '        # the resolved ends (0.88.0): a door, where the facade has one\n'),
    ])
    _edit(LOT / "site_enterability.py", [
        ('    bld = {b["id"]: b for b in merged["buildings"]}\n'
         '    import site_paths\n'
         '    for p in paths:\n',
         '    bld = {b["id"]: b for b in merged["buildings"]}\n'
         '    import site_paths\n'
         '    # a walk that is drawn, and not a landing (0.91.0): a landing is where\n'
         '    # a door meets the lot, not a way to it\n'
         '    for p in site_paths.drawn(site_spec):\n'
         '        if p.get("landing_of"):\n'
         '            continue\n'),
    ])
    _edit(LOT / "site_furniture.py", [
        ('    import site_streets\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings") or [] if "id" in b}\n'
         '    out = []\n'
         '    for p in site_spec.get("paths") or []:\n',
         '    import site_paths\n'
         '    import site_streets\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings") or [] if "id" in b}\n'
         '    out = []\n'
         '    for p in site_paths.drawn(site_spec):\n'),
    ])
    _edit(LOT / "site_steps.py", [
        ('    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for p in site_spec.get("paths", []) or []:\n',
         '    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for p in site_paths.drawn(site_spec):\n'),
    ])
    _edit(LOT / "site_streets.py", [
        ('    crossers = [(p, float(p.get("width", 6.0)), "path", 0.0, -1)\n'
         '                for p in site_spec.get("paths", []) or []]\n',
         '    import site_paths\n'
         '    crossers = [(p, float(p.get("width", 6.0)), "path", 0.0, -1)\n'
         '                for p in site_paths.drawn(site_spec)]\n'),
    ])
    _edit(LOT / "site_surfaces.py", [
        ('    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_spec.get("paths", []) or []):\n',
         '    import site_paths\n'
         '    bld = {b["id"]: b for b in site_spec.get("buildings", []) or []}\n'
         '    out = []\n'
         '    for i, p in enumerate(site_paths.drawn(site_spec)):\n'),
    ])
    (LOT / "site_paths.py").write_bytes((SRC / "site_paths.py").read_bytes())
    (LOT / "tests" / "test_site_paths.py").write_bytes((SRC / "test_site_paths.py").read_bytes())
    entry = (SRC / "CHANGELOG_0.91.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## 0.91.0" not in d and d.startswith(b"## 0.90.0")
    cl.write_bytes(entry.encode("utf-8") + d)
    (LOT / "VERSION").write_bytes(b"Lot 0.91.0")
    print("0.90.0 -> 0.91.0")


if __name__ == "__main__":
    main()
