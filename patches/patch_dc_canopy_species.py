"""Deli Counter 0.293.0: a filling station's canopy is built (the factory's roadmap 324).

Two rows of `prop_species.PROP_SPECIES`, ahead of the box row, route `canopy_roof` and `canopy_col` to Zoo 1.149.0's
`fuel_canopy` and `canopy_column`; `SPECIES_MATERIALS` mirrors their material.

Proven: tests/test_canopy_species.py fails on 0.292.0 (fails_on_old.out.txt); the gate on the clone; the slice rebuilt
with the canopy built and priced (the factory's docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'deli_counter'
PINS = {'CHANGELOG.md': '72fb0990583cd6da', 'VERSION': 'f63caf407e9d2fec', 'prop_species.py': '169aeb3aa90bfd06'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.292.0] - a parapet stands on the wall below it\n', '## [0.293.0] - a filling station\'s canopy is built\n\nThe factory\'s roadmap 324; the walker, 2026-10-29, of the game\'s vertical slice: "Things still look simple, and\ncomputer made". The specs author a filling station\'s canopy as volumes, `canopy_roof` (16 decks) on `canopy_col`\n(96 columns), and the box row of `prop_species.PROP_SPECIES` held both to a greybox box through its `canopy` and\n`col_`: the forecourt\'s landmark shipped as a grey slab on grey posts (the factory\'s `docs/findings/slice_look/`).\nTwo rows ahead of the box row route them to Zoo 1.149.0\'s `fuel_canopy` and `canopy_column`, each asking for\n`metal_painted` (`SPECIES_MATERIALS`); no other authored name carries either keyword. Tests:\ntests/test_canopy_species.py (fails on 0.292.0).\n\n## [0.292.0] - a parapet stands on the wall below it\n')], 'VERSION': [('lines 1-1', 'Deli Counter 0.292.0', 'Deli Counter 0.293.0')], 'prop_species.py': [('lines 82-83', '    (("cash_cart",), "cash_cart"),\n    (("crate", "col_", "pillar", "column", "stack", "pump_island",\n', '    (("cash_cart",), "cash_cart"),\n    # A FILLING STATION\'S CANOPY (0.293.0, Zoo 1.149.0, the factory\'s roadmap 324): the specs author it as\n    # `canopy_roof` on six `canopy_col`, and the box row\'s `canopy` and `col_` held both to a greybox box -- the\n    # forecourt\'s landmark a grey slab on grey posts (the factory\'s docs/findings/slice_look/). Ahead of that row and\n    # no further up; no other authored name carries either keyword (16 decks, 96 columns, measured over specs/).\n    (("canopy_roof",), "fuel_canopy"),\n    (("canopy_col",), "canopy_column"),\n    (("crate", "col_", "pillar", "column", "stack", "pump_island",\n'), ('lines 394-395', "    'atm': ('metal_painted', ('metal_painted', 'plastic')),\n    'back_bar': ('wood_stained', ('wood_stained', 'wood', 'laminate')),\n", "    'atm': ('metal_painted', ('metal_painted', 'plastic')),\n    'canopy_column': ('metal_painted', ('metal_painted',)),\n    'back_bar': ('wood_stained', ('wood_stained', 'wood', 'laminate')),\n"), ('lines 423-424', "    'folding_table': ('plastic', ('plastic', 'laminate', 'wood', 'metal_painted')),\n    'furnace': ('metal_painted', ('metal_painted',)),\n", "    'folding_table': ('plastic', ('plastic', 'laminate', 'wood', 'metal_painted')),\n    'fuel_canopy': ('metal_painted', ('metal_painted',)),\n    'furnace': ('metal_painted', ('metal_painted',)),\n")]}
WHOLE = {}
NEW_FILES = {'tests/test_canopy_species.py': '"""A filling station\'s canopy is built by its species (0.293.0, Zoo 1.149.0, the factory\'s roadmap 324).\n\nThe box row\'s `canopy` and `col_` held every authored `canopy_roof` and `canopy_col` to a greybox box -- the forecourt\'s\nlandmark a grey slab on grey posts. They route to Zoo\'s `fuel_canopy` and `canopy_column`, ahead of that row.\n"""\nimport glob\nimport json\nimport os\nimport sys\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nsys.path.insert(0, HERE)\n\nimport prop_species as P  # noqa: E402\n\n\ndef test_the_canopy_routes_to_its_species():\n    """FAILS ON 0.292.0: both were None, a box."""\n    assert P.species_for_name("canopy_roof") == "fuel_canopy"\n    assert P.species_for_name("canopy_col_4") == "canopy_column"\n    assert P.material_for("fuel_canopy", "canopy_steel") == "metal_painted"\n    assert P.material_for("canopy_column", "metal") == "metal_painted"\n\n\ndef test_no_other_authored_name_is_claimed():\n    """Every authored name the two rows now route is a canopy\'s: the rows steal nothing from the box row below."""\n    routed = set()\n    for f in glob.glob(os.path.join(HERE, "specs", "*.json")):\n        try:\n            d = json.load(open(f, encoding="utf-8"))\n        except (ValueError, OSError):\n            continue\n        for v in (d.get("volumes") or []) + (d.get("placements") or []):\n            n = v.get("name", "")\n            if P.species_for_name(n) in ("fuel_canopy", "canopy_column"):\n                routed.add(n.rstrip("0123456789_"))\n    assert routed <= {"canopy_roof", "canopy_col"}, routed\n'}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
