"""Deli Counter 0.269.0: a switchback's seam draws as a raking rail -- the walker, walking cold run 9386: "the
walling/railing doesn't loook natural yet" (the factory's `docs/findings/walk_2026-10-23_9386/`, finding 6).

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `stairwell.py` and `deli_counter.py` (anchored hunks); the new `tests/test_stair_rake.py`; VERSION; the
CHANGELOG entry, prepended. Generated from a proven clone (`patches/dc_stair_rake/gen_dc_stair_rake.py`), dry-run on a
fresh clone to the clone's every byte, a second run refused (`patches/dc_stair_rake/dry_run_*.out.txt`).

    python patches/patch_dc_stair_rake.py
    cd deli_counter && python build.py --all && python nav_gate.py --all && python -m pytest -q && python check.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "deli_counter"
PINS = {'stairwell.py': '06bee18b27bcc162', 'deli_counter.py': '9f3655e2e4020071'}
EDITS = {'stairwell.py': [('lines 851-851', 'def _seam_pieces(st, H, s, sid, travel, pos, span):\n', 'def _seam_pieces(st, H, s, sid, travel, pos, span, rises_hi=True):\n'), ('lines 874-876', '    z_lo = s * H + agent_contract.body_height()\n    return [{"stair": sid, "story": s, "kind": "side", "axis": travel,\n             "pos": pos, "lo": span[0], "hi": span[1], "z_lo": round(z_lo, 4)}]\n', '    z_lo = s * H + agent_contract.body_height()\n    # `rises_hi` (0.269.0): whether the leg climbs toward ``hi`` -- the raking\n    # rail the builder draws along it points its high end that way\n    return [{"stair": sid, "story": s, "kind": "side", "axis": travel,\n             "pos": pos, "lo": span[0], "hi": span[1], "z_lo": round(z_lo, 4),\n             "rises_hi": bool(rises_hi)}]\n'), ('lines 1085-1085', '                                        s_span)\n', '                                        s_span, rises_hi=arrive_hi)\n')], 'deli_counter.py': [('lines 1834-1835', '\n    def _stair_guards(self):\n', "\n    #: a seam's raking rail's depth across (0.269.0): the top rail's width, inside Zoo's genome's 0.03..0.12\n    RAKE_THICK_M = 0.05\n\n    def _stair_guards(self):\n"), ('lines 1870-1871', '            # stays at the slab underside (`stairwell._seam_pieces`).\n            if "z_lo" in g:\n', '            # stays at the slab underside (`stairwell._seam_pieces`).\n            seam = "z_lo" in g\n            seam_z0 = z0\n            if "z_lo" in g:\n'), ('lines 1887-1887', '                material=mat, form=("level" if g["kind"] == "rail" else None)))\n', '                material=mat, form=("level" if g["kind"] == "rail" else None),\n                visual=not seam))\n            # A SEAM DRAWS AS A RAKING RAIL (0.269.0). The walker, walking cold\n            # run 9386, circled the block a switchback\'s upper flight carries\n            # over the lower one\'s edge: "the walling/railing doesn\'t loook\n            # natural yet"; their pick, the compact U, a rail between the\n            # flights. The block stays a collider, unseen -- its underside a\n            # body\'s height up so the lower flight keeps its headroom\n            # (`stairwell._seam_pieces`), which a rail\'s collider following the\n            # upper flight down to its treads would not -- and a visual-only\n            # `stoop_railing` flight (Zoo >= 1.129.0) follows the upper flight\'s\n            # inner edge, from its foot on the storey\'s floor to RAIL_H over its\n            # head. Zoo draws the high end at +X; the volume\'s long-side turn\n            # sends +X along -Y for a Y run, so a rail rising toward +Y turns a\n            # further 180, and an X run rising toward -X turns 180\n            # (`stoop.RAIL_ROT_Y`\'s measured convention).\n            if seam:\n                hr = H + stoop.RAIL_H\n                rises_hi = bool(g.get("rises_hi", True))\n                # Zoo draws the high end at +X; the composer turns +X by rot_y to plan +X (0), -Y (90), -X (180)\n                # or +Y (270) (`stoop.RAIL_ROT_Y`\'s measured convention)\n                if g["axis"] == "Y":\n                    rot = 270.0 if rises_hi else 90.0\n                else:\n                    rot = 0.0 if rises_hi else 180.0\n                # A SLOT WITH NO GREYBOX BOX, deliberately: a greybox visual box is navigation data to Lot\'s walk\n                # bake (the factory\'s memory `greybox-is-in-the-walk-navmesh`, cold run 9340), and this one would\n                # stand a thin wall from the storey\'s floor at the seam -- the floor-height seam 0.225.0 measured\n                # cutting the lower flight. With no greybox node the composer places the module by the slot\'s own\n                # transform and turn (`themed_tscn`: no extent to fit), and the bake sees the seam\'s collider alone.\n                rmat = next((m for m in ("metal_painted", "wood") if m in have), None) or self.s.default_material\n                self.slots.append({\n                    "slot_id": f"stair_guard_rake_{k}", "role": "prop", "size_mod": "full",\n                    "style": skin_style.style_for(rmat, self._mat_style, self.s.default_material),\n                    "material": rmat, "species": "stoop_railing", "stock": None, "variant": 0,\n                    "form": "flight", "current_ref": "prop_greybox_01", "kit_axis": "material",\n                    "wall": None, "story": None, "facing": None,\n                    "transform": {"translation": [round(x, 4), round(y, 4), round(seam_z0 + hr / 2.0, 4)],\n                                  "rot_y": rot, "scale": [1.0, 1.0, 1.0]},\n                    "fit": {"dims": [round(along, 4), self.RAKE_THICK_M, round(hr, 4)],\n                            "pivot": "center", "openings": [], "collision": "none"},\n                })\n')]}
REPLACED = {}
NEW_FILES = {'tests/test_stair_rake.py': '"""A switchback\'s seam draws as a raking rail (0.269.0): its collider kept where it was, unseen; a visual-only\n`stoop_railing` flight along the upper flight, its high end up the flight. The walker, walking cold run 9386, of the\nblock over the office switchback\'s upper flight: "the walling/railing doesn\'t loook natural yet". FAILS ON 0.268.0."""\nimport importlib\nimport json\nimport os\nimport sys\nimport types\n\nimport pytest\n\nimport stoop\nimport stairwell\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n\n\n@pytest.fixture\ndef dc(monkeypatch):\n    for name in ("bpy", "bmesh"):\n        try:\n            importlib.import_module(name)\n        except ImportError:\n            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))\n    monkeypatch.delitem(sys.modules, "deli_counter", raising=False)\n    mod = importlib.import_module("deli_counter")\n    yield mod\n    sys.modules.pop("deli_counter", None)\n\n\ndef _office(dc):\n    import skin_style\n    from spec_loader import spec_from_dict\n    spec = spec_from_dict(json.load(open(os.path.join(HERE, "specs", "office.json"), encoding="utf-8")))\n    b = dc._Builder(spec)\n    b.slots = []\n    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])\n    cols = []\n    b._box = lambda *a, **k: None\n    b._col_box = lambda name, *a, **k: cols.append(name)\n    b._record_surface = lambda *a, **k: None\n    b._stair_guards()\n    b._volumes()\n    return spec, b, cols\n\n\ndef test_the_seam_keeps_its_collider_unseen_and_gains_a_raking_rail(dc):\n    spec, b, cols = _office(dc)\n    seams = [(k, g) for k, g in enumerate(stairwell.stair_guards(spec)) if "z_lo" in g]\n    assert len(seams) == 1, seams\n    k, g = seams[0]\n    side = "stair_guard_side_%d" % k\n    assert side + "_col" in cols\n    assert side not in {s["slot_id"] for s in b.slots}\n    rake = [s for s in b.slots if s["slot_id"] == "stair_guard_rake_%d" % k]\n    assert len(rake) == 1, [s["slot_id"] for s in b.slots if "rake" in s["slot_id"]]\n    r = rake[0]\n    assert (r["species"], r["form"], r["fit"]["collision"]) == ("stoop_railing", "flight", "none"), r\n    along = round(g["hi"] - g["lo"], 4)\n    assert r["fit"]["dims"] == [along, b.RAKE_THICK_M, round(spec.story_height + stoop.RAIL_H, 4)], r["fit"]\n    want = 270.0 if g["rises_hi"] else 90.0\n    if g["axis"] == "X":\n        want = 0.0 if g["rises_hi"] else 180.0\n    assert r["transform"]["rot_y"] == want, (r["transform"], g)\n    assert "stair_guard_rake_%d_col" % k not in cols\n\n\ndef test_the_rake_draws_no_greybox_box(dc):\n    """A greybox visual box is navigation data to Lot\'s walk bake; the rake has none."""\n    import skin_style\n    from spec_loader import spec_from_dict\n    spec = spec_from_dict(json.load(open(os.path.join(HERE, "specs", "office.json"), encoding="utf-8")))\n    b = dc._Builder(spec)\n    b.slots = []\n    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])\n    boxes = []\n    b._box = lambda name, *a, **k: boxes.append(name)\n    b._col_box = lambda *a, **k: None\n    b._record_surface = lambda *a, **k: None\n    b._stair_guards()\n    b._volumes()\n    assert not [n for n in boxes if "rake" in n], boxes\n'}
CHANGELOG = '## [0.269.0] - a switchback\'s seam draws as a raking rail\n\n**The walker, walking cold run 9386** (the factory\'s `docs/findings/walk_2026-10-23_9386/`, finding 6), circling the\nplain block over the office switchback\'s upper flight: "the walling/railing doesn\'t loook natural yet". Their pick, the\ncompact U: walls where they enclose the well, a rail between the flights. 0.268.0 made the hole\'s rails balustrades;\nthis is the block.\n\n### Changed\n- **The seam\'s collider stays exactly where it was, unseen** (`visual: false`): its underside a body\'s height over\n  the storey\'s floor so the lower flight keeps its headroom (`stairwell._seam_pieces`, 0.225.0\'s measurement), which a\n  rail\'s collider following the upper flight down to its treads would not.\n- **A raking rail along the upper flight\'s inner edge**: Zoo\'s `stoop_railing` flight form (>= 1.129.0), from the\n  storey\'s floor at the flight\'s foot to `stoop.RAIL_H` over its head, its high end up the flight (`rises_hi`, which\n  `_seam_pieces` now records from the leg\'s arrival end). A SLOT WITH NO GREYBOX BOX and no collider: a greybox visual\n  box is navigation data to Lot\'s walk bake, and this one would stand a thin wall from the floor at the seam -- the\n  floor-height seam 0.225.0 measured cutting the lower flight. With no greybox node the composer places the module by\n  the slot\'s own transform and turn, and the bake sees the seam\'s collider alone, as before.\n\n### Tests\n- `tests/test_stair_rake.py` (new): the office\'s seam keeps its collider, draws no box of its own and gains one raking\n  rail -- `stoop_railing`, flight, no collision, the seam\'s length by a storey and a rail, turned up the flight -- and\n  the rake draws no greybox box. The first fails on 0.268.0.\n\n### Measured, the clone\n- `build.py --all` and `nav_gate.py --all` exit 0, 157 shells passed -- the seam\'s collider is where it was, so\n  the walk bake meets what it met; the suite 1,831 tests, 0 failed, 31 skipped (the factory\'s\n  `patches/dc_stair_rake/prove.out.txt`).\n\n'
OLD_VERSION, NEW_VERSION = 'Deli Counter 0.268.0', 'Deli Counter 0.269.0'


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
