"""Lot 0.95.0: a parking field is its own dressing zone, at a road's density.

Lot 0.94.0 drew the fields and declared their slabs in `tops`, but gave
`site_surfaces.zones` nothing for them, so the ground scatter dressed them as
open ground, at MEDIUM: on cold run 9141 all 256 pieces on the fields came
from `open_ground` (0.29 a m2), and the walker's frames read pebble-strewn
aisles. A lot's aisle is a carriageway, and the guide's reading of a road's
centre is LOW. With Patina 0.23.0 (a zone dresses only the ground it owns)
the field's own zone is the one that decides.

Anchored edits (every anchor once; refuses on a miss): `site_surfaces.py`
(`DENSITY_BY_ZONE`, `PRECEDENCE`, the zone's top, one zone a field),
`tests/test_site_surfaces_field_zone.py` copied from `lot_field_zone/`.
CHANGELOG and VERSION from `lot_field_zone/CHANGELOG_0.95.0.md`.

    python patch_lot_field_zone.py
"""
import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_field_zone"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.94.0", v
    _edit(LOT / "site_surfaces.py", [
        ('    "road": "low",\n',
         '    "road": "low",\n'
         '    # A parking field (0.95.0): its aisle is a carriageway, so a road\'s\n'
         '    # reading, not open ground\'s.\n'
         '    "parking": "low",\n'),
        ('PRECEDENCE = ("path", "sidewalk", "wall_base", "road", "courtyard", "perimeter",\n'
         '              "open")\n',
         'PRECEDENCE = ("path", "sidewalk", "wall_base", "road", "parking", "courtyard",\n'
         '              "perimeter", "open")\n'),
        ('        "courtyard": lot.COURT_THICK,\n'
         '        "perimeter": lot.PLATE_TOP,\n',
         '        "courtyard": lot.COURT_THICK,\n'
         '        "parking": lot.FIELD_THICK,\n'
         '        "perimeter": lot.PLATE_TOP,\n'),
        ('    # --- perimeter: outside the content, by definition -----------------------\n',
         '    # --- parking fields (0.95.0): the lot is not open ground ---------------\n'
         '    for i, f in enumerate(site_spec.get("fields", []) or []):\n'
         '        rect = tuple(float(v) for v in f["rect"])\n'
         '        out.append(_zone(f"field_{i}", "ground", "parking", rect,\n'
         '                         *zr("parking"), "play_space",\n'
         '                         ["parking", f"road:{f[\'road\']}"]))\n'
         '\n'
         '    # --- perimeter: outside the content, by definition -----------------------\n'),
    ])
    shutil.copyfile(SRC / "test_site_surfaces_field_zone.py", LOT / "tests" / "test_site_surfaces_field_zone.py")
    ch = LOT / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    anchor = "## 0.94.0 - "
    assert s.count(anchor) == 1, "changelog anchor"
    ch.write_text(s.replace(anchor, (SRC / "CHANGELOG_0.95.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + anchor), encoding="utf-8", newline="\n")
    (LOT / "VERSION").write_text("Lot 0.95.0", encoding="utf-8", newline="\n")
    print("Lot 0.95.0 applied")


if __name__ == "__main__":
    main()
