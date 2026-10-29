"""Deli Counter 0.292.0: a parapet stands on the wall below it (the factory's roadmap 324; the walker: "make the
parapets flush").

`_parapets` stands the ring on the walls' outer faces -- the slab's extent plus half `wall_thick` -- and starts each
tile at the top of the wall below, so it covers the roof slab's edge; its top is unchanged. `polybudget` mirrors it.

Proven: tests/test_parapet_flush.py and test_parapet_slots.py's height pin fail on 0.291.0 (fails_on_old.out.txt);
the clone's suite, 1,914 passed, 35 skipped (suite_clone.out.txt); the gate (build.py --all, catalog.py, check.py) on
the clone; seed 9082 rebuilt and priced PASS (the factory's docs/findings/parapet_flush/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'deli_counter'
PINS = {'CHANGELOG.md': 'e5712fdaba05495c', 'VERSION': '7b1fbc4f5198c062', 'deli_counter.py': '8a7189332c148566', 'polybudget.py': 'c9677e111b0c140b', 'tests/test_parapet_slots.py': '434bdb1d957c1aa7'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.291.0] - where a crew stands to drill\n', '## [0.292.0] - a parapet stands on the wall below it\n\nThe factory\'s roadmap 324; the walker, 2026-10-29: "keep going on the edges", then "make the parapets flush".\n`_exterior` centres every storey wall on the slab\'s extent, and the parapet ring took that extent as its OUTER face,\nso it stood half a wall behind the facade it is meant to carry up -- 15 cm on a 0.3 m wall -- with the roof slab\'s\nedge in a recess under it, because the wall stops under that slab (`_cap_thick`). Measured on `bank_branch_a02`\n(the factory\'s `docs/findings/parapet_coping/`): the storey walls\' face at y 11.15 and top at 6.9, the parapet\'s and\nthe slab\'s face at 11.0. The comment above `_record_parapet_slot` said "the wall below it carried past the roof"; the\ncoordinates said otherwise.\n\n### Changed\n- **`_parapets`**: the ring stands on the walls\' outer faces (the slab\'s extent plus half `wall_thick`) and each tile\n  starts at the top of the wall below -- the underside of the slab that caps it -- so it covers the slab\'s edge; its\n  top is unchanged. The corners still belong to N and S. A parapet slot is `cap` taller (the roof\'s thickness): on\n  `bank_branch_a02` 1.1 -> 1.4 m, centred 7.6 where it was 7.75, its N face at 11.15. `polybudget` mirrors the new\n  runs. Seed 9082 rebuilt (the factory\'s `docs/findings/parapet_flush/`): every Empty\'s step strips are gone (14 each)\n  and Patina\'s copings follow the slots onto the facade line; priced PASS over 53 headings, draws median +0, largest\n  +1. Tests: `tests/test_parapet_flush.py` (fails on 0.291.0); `tests/test_parapet_slots.py`\'s height pin follows.\n\n## [0.291.0] - where a crew stands to drill\n')], 'VERSION': [('lines 1-1', 'Deli Counter 0.291.0', 'Deli Counter 0.292.0')], 'deli_counter.py': [('lines 3439-3440', '            _px0, _py0, _px1, _py1 = setbacks_mod.slab_extent(self.s, p.story)\n            hx, hy = (_px1 - _px0) / 2, (_py1 - _py0) / 2\n', "            _px0, _py0, _px1, _py1 = setbacks_mod.slab_extent(self.s, p.story)\n            # A PARAPET STANDS ON THE WALL BELOW IT (0.292.0). That slab's\n            # extent is the walls' CENTRELINE -- `_exterior` centres every\n            # wall on it -- so a ring on it stood half a wall behind the face\n            # it was meant to carry up: 15 cm on a 0.3 m wall, with the roof\n            # slab's edge in a recess under it, because the wall stops under\n            # that slab (`_cap_thick`). Measured on `bank_branch_a02` (the\n            # factory's docs/findings/parapet_coping/): storey walls' face at\n            # y 11.15 and top at 6.9, parapet's and slab's face at 11.0. The\n            # ring now takes the walls' OUTER faces, and each tile starts at\n            # the wall's top, so it covers the slab's edge; its top is where\n            # it was.\n            wt = self.s.wall_thick\n            _px0, _py0, _px1, _py1 = _px0 - wt / 2, _py0 - wt / 2, _px1 + wt / 2, _py1 + wt / 2\n            hx, hy = (_px1 - _px0) / 2, (_py1 - _py0) / 2\n"), ('lines 3443-3443', '            cz = z + p.height / 2\n', '            cap = self._cap_thick(p.story - 1, self._story_range()[1])\n            ph = p.height + cap\n            cz = z - cap + ph / 2\n'), ('lines 3463-3464', '                ("N", (_pcx, _pcy + hy - t / 2, cz), (ex, t, p.height)),\n                ("S", (_pcx, _pcy - hy + t / 2, cz), (ex, t, p.height)),\n', '                ("N", (_pcx, _pcy + hy - t / 2, cz), (ex, t, ph)),\n                ("S", (_pcx, _pcy - hy + t / 2, cz), (ex, t, ph)),\n'), ('lines 3470-3471', '                    ("E", (_pcx + hx - t / 2, _pcy, cz), (t, ey, p.height)),\n                    ("W", (_pcx - hx + t / 2, _pcy, cz), (t, ey, p.height)),\n', '                    ("E", (_pcx + hx - t / 2, _pcy, cz), (t, ey, ph)),\n                    ("W", (_pcx - hx + t / 2, _pcy, cz), (t, ey, ph)),\n')], 'polybudget.py': [('lines 105-107', '        t = para.thick\n        ey = spec.footprint_y - 2 * t\n        runs = [("N", spec.footprint_x, t), ("S", spec.footprint_x, t)]\n', '        # the ring stands on the walls\' outer faces (0.292.0)\n        t, wt = para.thick, spec.wall_thick\n        ey = spec.footprint_y + wt - 2 * t\n        runs = [("N", spec.footprint_x + wt, t), ("S", spec.footprint_x + wt, t)]\n')], 'tests/test_parapet_slots.py': [('lines 70-71', '    # the parapet\'s own size, module-local: (run, thickness, height)\n    assert all(abs(sl["fit"]["dims"][2] - 0.8) < 1e-9 and abs(sl["fit"]["dims"][1] - 0.3) < 1e-9\n', '    # the parapet\'s own size, module-local: (run, thickness, height) -- its\n    # 0.8 m above the roof and, since 0.292.0, the roof slab\'s edge below it\n    spec = spec_from_dict(s)\n    cap = spec.roof_thick or spec.floor_thick\n    assert all(abs(sl["fit"]["dims"][2] - (0.8 + cap)) < 1e-9 and abs(sl["fit"]["dims"][1] - 0.3) < 1e-9\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_parapet_flush.py': '"""A parapet stands on the wall below it (0.292.0).\n\n`_exterior` centres every storey wall on the slab\'s extent, and the parapet\nring took that extent as its OUTER face -- so it stood half a wall behind the\nfacade it was meant to carry up, with the roof slab\'s edge in a recess under\nit, because the wall stops under that slab (`_cap_thick`). Measured on\n`bank_branch_a02` (the factory\'s docs/findings/parapet_coping/): the storey\nwalls\' face at y 11.15 and their top at 6.9, the parapet\'s and the slab\'s face\nat 11.0. The ring now stands on the walls\' outer faces and each tile starts at\nthe wall\'s top; its top is where it was.\n\nRuns without Blender: bpy and bmesh are stubbed when absent, as in\n`test_parapet_slots.py`.\n"""\nimport importlib\nimport os\nimport sys\nimport types\n\nimport pytest\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nsys.path.insert(0, HERE)\n\nimport presets        # noqa: E402\nfrom spec_loader import spec_from_dict   # noqa: E402\n\n\n@pytest.fixture\ndef dc(monkeypatch):\n    for name in ("bpy", "bmesh"):\n        try:\n            importlib.import_module(name)\n        except ImportError:\n            monkeypatch.setitem(sys.modules, name, types.ModuleType(name))\n    monkeypatch.delitem(sys.modules, "deli_counter", raising=False)\n    mod = importlib.import_module("deli_counter")\n    yield mod\n    sys.modules.pop("deli_counter", None)\n\n\ndef _ring(dc, spec_dict):\n    """Every parapet visual\'s (name, centre, size), and the spec."""\n    spec = spec_from_dict(spec_dict)\n    b = dc._Builder(spec)\n    b.slots = []\n    import skin_style\n    b._mat_style = skin_style.material_styles([m.id for m in spec.materials])\n    boxes = []\n    b._box = lambda name, c, size, *a, **k: boxes.append((name, c, size))\n    b._col_box = lambda *a, **k: None\n    b._parapets()\n    return boxes, spec\n\n\ndef _bounds(boxes):\n    lo = [min(c[i] - s[i] / 2 for _n, c, s in boxes) for i in range(3)]\n    hi = [max(c[i] + s[i] / 2 for _n, c, s in boxes) for i in range(3)]\n    return lo, hi\n\n\n@pytest.mark.parametrize("spec_dict", [presets.empty_rowhome(floors=3, wall="brick"),\n                                       dict(presets.empty_rowhome(floors=2), modular=True)])\ndef test_the_ring_stands_on_the_walls_outer_faces_from_the_walls_top(dc, spec_dict):\n    """FAILS ON 0.291.0: the ring\'s outer faces were the walls\' centrelines\n    (+-footprint/2) and its bottom the slab\'s top."""\n    boxes, spec = _ring(dc, spec_dict)\n    assert boxes\n    wt = spec.wall_thick\n    lo, hi = _bounds(boxes)\n    assert hi[0] == pytest.approx(spec.footprint_x / 2 + wt / 2)\n    assert lo[0] == pytest.approx(-spec.footprint_x / 2 - wt / 2)\n    assert hi[1] == pytest.approx(spec.footprint_y / 2 + wt / 2)\n    assert lo[1] == pytest.approx(-spec.footprint_y / 2 - wt / 2)\n    p = spec.parapets[0]\n    z = p.story * spec.story_height\n    cap = spec.roof_thick or spec.floor_thick\n    # the top storey\'s wall stops at the roof slab\'s underside: the parapet\n    # starts there, and its top is unchanged\n    assert lo[2] == pytest.approx(z - cap)\n    assert hi[2] == pytest.approx(z + p.height)\n\n\ndef test_the_corners_still_belong_to_n_and_s(dc):\n    """The ring\'s rule is unchanged on the new extent: N and S span it, E and\n    W stand between their inner faces, and no two runs overlap."""\n    boxes, spec = _ring(dc, presets.empty_rowhome(floors=3, wall="brick"))\n    t = spec.parapets[0].thick\n    side = {k: _bounds([b for b in boxes if b[0].split("_")[1] == k]) for k in "NESW"}\n    wt = spec.wall_thick\n    (nlo, nhi), (elo, ehi) = side["N"], side["E"]\n    assert nhi[0] - nlo[0] == pytest.approx(spec.footprint_x + wt)\n    assert ehi[1] - elo[1] == pytest.approx(spec.footprint_y + wt - 2 * t)\n    assert ehi[1] == pytest.approx(nlo[1])           # E ends at N\'s inner face\n    assert ehi[0] == pytest.approx(nhi[0])           # and shares the outer face\n'}


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
