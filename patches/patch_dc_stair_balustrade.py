"""Deli Counter 0.268.0: a stair hole's rail is a balustrade -- Zoo's `stoop_railing`, painted iron where the palette
has it -- the walker, walking cold run 9386: "the walling/railing doesn't loook natural yet" (the factory's
`docs/findings/walk_2026-10-23_9386/`, finding 6).

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `prop_species.py`, `deli_counter.py` and `tests/test_ramp_cut.py` (anchored hunks); the new
`tests/test_stair_balustrade.py`; VERSION; the CHANGELOG entry, prepended. Generated from a proven clone
(`patches/dc_stair_balustrade/gen_dc_stair_balustrade.py`), dry-run on a fresh clone to the clone's every byte, a
second run refused (`patches/dc_stair_balustrade/dry_run_*.out.txt`).

    python patches/patch_dc_stair_balustrade.py
    cd deli_counter && python build.py --all && python nav_gate.py --all && python -m pytest -q && python check.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "deli_counter"
PINS = {'prop_species.py': '594f343c6fef0bf5', 'deli_counter.py': '56fd60ae38c125c6', 'tests/test_ramp_cut.py': '8418c2ddc4191eaf'}
EDITS = {'prop_species.py': [('lines 35-36', 'PROP_SPECIES = (\n    # INTERIOR SPECIES (Zoo 0.84.0), each placed IMMEDIATELY AHEAD of the\n', 'PROP_SPECIES = (\n    # A STAIR\'S RAIL IS A BALUSTRADE (0.268.0). The walker, walking cold run\n    # 9386, of the office stair\'s hole ringed by solid wood guard boxes: "the\n    # walling/railing doesn\'t loook natural yet". `_stair_guards` names each\n    # rail `stair_guard_rail_<k>`, a stair\'s or a ramp\'s; Zoo\'s `stoop_railing`\n    # (>= 1.128.0, 8 m long and 0.12 m deep) draws it as its LEVEL form, posts\n    # at least every 2.0 m and pickets between. No other row\'s keyword is in\n    # those names, and no authored volume carries one, so first is as good as\n    # anywhere; first, so a later row can never claim them.\n    (("stair_guard_rail",), "stoop_railing"),\n    # INTERIOR SPECIES (Zoo 0.84.0), each placed IMMEDIATELY AHEAD of the\n')], 'deli_counter.py': [('lines 1863-1864', '                # a piece may name its own (0.241.0: a ramp\'s rail is steel)\n                mat = g.get("material") or ("wood" if "wood" in have else None)\n', '                # a piece may name its own (0.241.0: a ramp\'s rail is steel);\n                # a stair\'s is painted iron where the palette has it, else wood\n                # (0.268.0, `prop_species`\'s balustrade row)\n                mat = g.get("material") or next(\n                    (m for m in ("metal_painted", "wood") if m in have), None)\n'), ('lines 1884-1884', '                material=mat))\n', '                material=mat, form=("level" if g["kind"] == "rail" else None)))\n')], 'tests/test_ramp_cut.py': [('lines 125-125', '    assert \'mat = g.get("material") or ("wood" if "wood" in have else None)\' in src\n', '    # the piece\'s own material first, still (0.268.0 made the default painted iron, then wood)\n    assert \'mat = g.get("material") or next(\' in src\n')]}
REPLACED = {}
NEW_FILES = {'tests/test_stair_balustrade.py': '"""A stair hole\'s rail is a balustrade (0.268.0): Zoo\'s `stoop_railing`, its level form, painted iron where the palette\nhas it, the rail\'s own collider kept. The walker, walking cold run 9386, of the office stair\'s solid wood guard boxes:\n"the walling/railing doesn\'t loook natural yet". FAILS ON 0.267.0 (no species, wood)."""\nimport importlib\nimport json\nimport os\nimport sys\nimport types\n\nimport pytest\n\nimport prop_species\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n\n\ndef test_a_stairs_rail_names_the_balustrade_and_nothing_else_does():\n    for name in ("stair_guard_rail_0", "stair_guard_rail_11"):\n        assert prop_species.species_for_name(name) == "stoop_railing", name\n    for name in ("stair_guard_side_0", "stair_guard_back_10"):\n        assert prop_species.species_for_name(name) is None, name\n    assert not prop_species.owns_collision("stoop_railing")\n\n\n@pytest.fixture\ndef dc(monkeypatch):\n    """deli_counter against stub bpy/bmesh, as test_depth_long does."""\n    for name in ("bpy", "bmesh"):\n        try:\n            importlib.import_module(name)\n        except ImportError:\n            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))\n    monkeypatch.delitem(sys.modules, "deli_counter", raising=False)\n    mod = importlib.import_module("deli_counter")\n    yield mod\n    sys.modules.pop("deli_counter", None)\n\n\ndef test_the_offices_rails_are_iron_balustrades_and_keep_their_colliders(dc):\n    import skin_style\n    from spec_loader import spec_from_dict\n    spec = spec_from_dict(json.load(open(os.path.join(HERE, "specs", "office.json"), encoding="utf-8")))\n    b = dc._Builder(spec)\n    b.slots = []\n    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])\n    cols = []\n    b._box = lambda *a, **k: None\n    b._col_box = lambda name, *a, **k: cols.append(name)\n    b._record_surface = lambda *a, **k: None\n    b._stair_guards()\n    b._volumes()\n    rails = [s for s in b.slots if s["slot_id"].startswith("stair_guard_rail_")]\n    assert len(rails) == 6, [s["slot_id"] for s in rails]\n    for s in rails:\n        assert (s["species"], s["form"], s["material"]) == ("stoop_railing", "level", "metal_painted"), s\n        assert s["slot_id"] + "_col" in cols, s["slot_id"]\n    walls = [s for s in b.slots if s["slot_id"].startswith(("stair_guard_side_", "stair_guard_back_"))]\n    assert walls and all(s["species"] is None and s["form"] is None for s in walls)\n'}
CHANGELOG = '## [0.268.0] - a stair hole\'s rail is a balustrade\n\n**The walker, walking cold run 9386** (the factory\'s `docs/findings/walk_2026-10-23_9386/`, finding 6), of the office\'s\ndouble stair -- its hole ringed by solid wood guard boxes 1.07 m high, a flight walled where it should be open: "something\nabout the doulbe stairs still needs some work to not look so odd...mainly the walling/railing doesn\'t loook natural yet".\nTheir pick for the form: the compact U, walls where they enclose the well, a rail between the flights. This is the\nfirst step: the rails.\n\n### Changed\n- **A stair hole\'s rail is Zoo\'s `stoop_railing`** (>= 1.128.0, its level form, posts at least every 2.0 m and\n  pickets between): `prop_species` routes `stair_guard_rail_<k>` to it, first in the table (no other row\'s keyword is in\n  those names, and no authored volume carries one), and `_stair_guards` gives a rail `form: level`.\n- **Painted iron where the palette has it, else wood**: a stair\'s rail took `wood` wherever the palette had it; a\n  ramp\'s still names its own steel. 117 of the library\'s 305 stair specs have `metal_painted`.\n- **The collider is unchanged**: each rail keeps its own `_col` box; Zoo\'s species builds no collision.\n\n### Still open\n- The seam wall a switchback\'s upper flight carries over the lower one\'s edge -- the plain block the walker circled --\n  becomes a raking rail in a later step; its underside stands a body\'s height up so the lower flight keeps its\n  headroom, and that has to hold.\n\n### Tests\n- `tests/test_stair_balustrade.py` (new): the rail\'s name routes to the balustrade and a side or back wall\'s does not;\n  the office\'s six rails are iron balustrades in the level form and keep their colliders, its walls stay walls. Both\n  fail on 0.267.0. `tests/test_ramp_cut.py`\'s pin on the builder\'s material line follows it.\n\n### Measured, the clone\n- `build.py --all` and `nav_gate.py --all` exit 0, 157 shells passed; the suite 1,829 tests, 0 failed but the ramp\n  test\'s pin, since followed (the factory\'s `patches/dc_stair_balustrade/prove.out.txt`).\n\n'
OLD_VERSION, NEW_VERSION = 'Deli Counter 0.267.0', 'Deli Counter 0.268.0'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: deli_counter/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: deli_counter/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: deli_counter/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    # a refurnished spec is carried whole, the file it replaces pinned like any other
    for name, text in REPLACED.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: deli_counter/%s exists already; nothing written" % name)
    v = REPO / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.split()[-1].encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("%s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in deli_counter/: build.py --all, "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
