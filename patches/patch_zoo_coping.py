"""Zoo 1.146.0: a parapet has a coping (the factory's roadmap 324; the walker: "keep the aluminium, keep going on
the edges").

The `coping` cover: Patina (>= 0.33.0) orders one a parapet run with its plan in `size2`, and Zoo stands a 10 cm
box on the parapet's top, sunk 5 mm into it, in the covers' own material.

Proven: tests/test_coping.py fails on 1.145.0 in Blender, 2 of 3 (fails_on_old.out.txt); the clone's suite, 7070
passed, 546 skipped (bpy), 1 xfailed, and its Blender set (suite_bpy_clone.out.txt). Seed 9082 built against this
clone and Patina's, shot and priced (the factory's docs/findings/parapet_coping/).

Also: tests/test_inner_face.py passes over 1.145.0's window frame as it does the glass (it failed on 1.145.0);
the Blender set's other 14 failures fail on 1.144.0 too (suite_bpy_failures.txt).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': '4dbdcc270429e1dc', 'VERSION': 'a20d3765f765b501', 'tests/test_inner_face.py': '237f9b87b5d7f130', 'zoo_keeper/core/dressing.py': '72842957f3f59435', 'zoo_keeper/recipes/dress_cover.py': 'be5f7d5bced9b9cc'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [1.145.0] - a window has a frame and a sill\n', '## [1.146.0] - a parapet has a coping\n\nThe factory\'s roadmap 324; the walker, 2026-10-29, on the window frames: "keep the aluminium, keep going on the\nedges". A parapet\'s top was capped by Patina\'s roofline `edge_strip`s, 2 m strips 2.5 m apart and centred on the\nwall\'s outer face, which this repo built as a 6 x 10 cm stick: a dashed line along the top of every building with a\nparapet (seed 9082, the factory\'s `docs/findings/parapet_coping/`).\n\n### Added\n- **The `coping` cover** (`core.dressing.coping_parts`, `recipes/dress_cover`): Patina (>= 0.33.0) orders one a\n  parapet run, `size2` = [length, width] in plan with the overhang each face and the corners already in it; Zoo\n  stands a `COPING_H` (10 cm) box on the parapet\'s top, sunk `COPING_SINK` (5 mm) into it so the two never share a\n  plane. In the covers\' own material, so on a side that has a base course it joins that side\'s concrete mesh: seed\n  9082\'s bank kept 8 meshes, its covers\' top rose from 8.35 to 8.395 m and each side\'s concrete widened to the\n  coping\'s 0.43 m. Priced over 53 headings: PASS, draws median +0 and largest +2.\n\n### Fixed\n- **`tests/test_inner_face.py` failed on 1.145.0\'s window**: it asserted that every face looking into the room is\n  drywall, which held while a window was a slab and a pane; 1.145.0\'s aluminium frame is seen from the room as the\n  glass is, and the test now passes it over as it passes over the glass. The window frame\'s change ran a narrower\n  Blender set than this one and missed it. Fourteen other Blender tests fail on 1.144.0 and 1.145.0 alike\n  (`test_club_bpy` 5, `test_interior_bpy` 7, `test_shut_door` 1, `test_front_doors` 1) and are not this release\'s.\n\n## [1.145.0] - a window has a frame and a sill\n')], 'VERSION': [('lines 1-1', '1.145.0', '1.146.0')], 'tests/test_inner_face.py': [('lines 71-71', '        if o.type != "MESH" or o.name.endswith(_COL_SUFFIXES) or "Glass" in o.name:\n', '        # the pane and (1.145.0) the aluminium frame round it are the window\'s,\n        # not the wall\'s: a room sees the frame, as it sees the glass\n        if (o.type != "MESH" or o.name.endswith(_COL_SUFFIXES) or "Glass" in o.name\n                or "_Frame_" in o.name):\n')], 'zoo_keeper/core/dressing.py': [('lines 129-130', 'BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10\n\n', 'BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10\n\n\n#: A PARAPET\'S COPING (1.146.0; Patina >= 0.33.0, the factory\'s roadmap 324).\n#: Patina plans it -- one order a parapet run, ``size2`` = [length, width] in\n#: plan, the overhang on each face already in the width and the corners already\n#: in the length -- and Zoo stands the solid on the parapet\'s top: 10 cm tall,\n#: twice the 6 cm `edge_strip` it replaces and the window sill\'s 5 cm overhang\n#: below it, so at street distance the top of a building reads as a capped wall\n#: rather than a cut one. It sinks `COPING_SINK` into the parapet, so its\n#: underside and the parapet\'s top are never one plane.\nCOPING_H = 0.10\nCOPING_SINK = 0.005\n\n\ndef coping_parts(length: float, width: float):\n    """A coping\'s one box, in cover-local space: x along the run, y across\n    the wall, z up from the parapet\'s top (the order\'s ``pos``)."""\n    return [((0.0, 0.0, COPING_H / 2.0 - COPING_SINK),\n             (max(float(length), 0.05), max(float(width), 0.05), COPING_H))]\n\n')], 'zoo_keeper/recipes/dress_cover.py': [('lines 40-41', '  ``core.dressing.dish_parts``).\n\n', "  ``core.dressing.dish_parts``).\n* ``coping``       — a parapet run's cap, over the whole wall and past both\n  faces (1.146.0; ``size2`` = [length, width] in plan;\n  ``core.dressing.coping_parts``).\n\n"), ('lines 70-70', '                             dish_parts, downspout_parts, frame_strips,\n', '                             coping_parts, dish_parts, downspout_parts, frame_strips,\n'), ('lines 119-120', '            geometry.add_box(bm, center, size)\n    elif cover == "tv_antenna":\n', '            geometry.add_box(bm, center, size)\n    elif cover == "coping":\n        # a parapet run\'s cap (1.146.0); `size2` is [length, width] in plan\n        length, width = (order.get("size2") or [2.0, 0.4])[:2]\n        for center, size in coping_parts(length, width):\n            geometry.add_box(bm, center, size)\n    elif cover == "tv_antenna":\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_coping.py': '"""A parapet\'s coping (1.146.0; Patina >= 0.33.0, the factory\'s roadmap 324).\n\nPatina plans one ``coping`` a parapet run -- ``size2`` = [length, width] in\nplan, overhang and corners included -- and the roofline ``edge_strip``s it\nreplaces are gone from the manifest. Zoo stands a 10 cm solid on the parapet\'s\ntop, sunk 5 mm into it, in the covers\' own concrete, so on a side that has a\nbase course it joins that side\'s mesh at no extra draw. The pure halves run\nanywhere; the merge and the solid\'s extent are measured under Blender.\n"""\nimport pytest\n\nfrom zoo_keeper import TOOL_VERSION\nfrom zoo_keeper.core import dressing as D\nfrom zoo_keeper.core import genome\n\nSPACE = "spec/Blender Z-up raw coords"\nTOP = 8.3                                  # bank_branch_a02\'s parapet top\n# Patina 0.33.0\'s plan for bank_branch_a02 (its slots.json): N and S over the\n# corners, E and W between their overhangs.\nCOPINGS = (((0.0, 10.9), (1.0, 0.0), 30.1, 0.3), ((14.9, 0.0), (0.0, 1.0), 21.5, 0.3),\n           ((0.0, -10.9), (1.0, 0.0), 30.1, 0.3), ((-14.9, 0.0), (0.0, 1.0), 21.5, 0.3))\nWALLS = (((0, 1, 0), (0.0, 11.0)), ((0, -1, 0), (0.0, -11.0)),\n         ((1, 0, 0), (15.0, 0.0)), ((-1, 0, 0), (-15.0, 0.0)))\n\n\ndef _order(cover, pos, normal, size=1.0, **kw):\n    o = {"cover": cover, "pos": list(pos), "normal": list(normal), "size": size,\n         "collision": "none", "seed_offset": 1,\n         "trim_piece": "roof_edge", "uv_region": [0.0, 0.0, 1.0, 1.0]}\n    o.update(kw)\n    return o\n\n\ndef _manifest():\n    orders = [_order("base_course", (x, y, 0.0), n) for n, (x, y) in WALLS]\n    for (x, y), (tx, ty), length, width in COPINGS:\n        orders.append(_order("coping", (x, y, TOP), (0, 0, 1), size=length,\n                             size2=[length, width], tangent=[tx, ty, 0.0]))\n    return {"schema": "patina-dressing/1", "building_id": "t_bank",\n            "space": SPACE, "orders": orders}\n\n\ndef _plans():\n    return D.plan_dressing(_manifest(), genome.load_species("dress_cover"),\n                           "delco_1997", TOOL_VERSION)["plans"]\n\n\ndef test_the_coping_stands_on_the_parapet_sunk_into_it():\n    """FAILS ON 1.145.0: there was no coping."""\n    [(center, size)] = D.coping_parts(30.1, 0.3)\n    assert size == pytest.approx((30.1, 0.3, D.COPING_H))\n    assert center[2] - size[2] / 2.0 == pytest.approx(-D.COPING_SINK)\n    assert center[2] + size[2] / 2.0 == pytest.approx(D.COPING_H - D.COPING_SINK)\n    assert D.COPING_H > D._COVER["edge_strip"]["proud"]\n\n\ndef test_each_coping_is_the_covers_concrete_on_its_own_side():\n    """The material every other concrete cover on that side wears, and the\n    side the run stands on -- so it merges where the strips it replaces did."""\n    sides = {}\n    for p in _plans():\n        if p["order"]["cover"] == "coping":\n            assert p["material"] == "concrete"\n            sides[p["side"]] = p["order"]["size2"][0]\n    assert sides == {"N": 30.1, "E": 21.5, "S": 30.1, "W": 21.5}\n\n\ndef test_bpy_the_copings_add_no_mesh_and_cap_the_ring(tmp_path):\n    """Built under Blender: the four copings join their sides\' concrete --\n    four meshes out, as the base courses make alone -- and the solids reach\n    5 cm past the parapet\'s outer faces and 9.5 cm above its top."""\n    pytest.importorskip("bpy")\n    import bpy\n    from zoo_keeper.bpylayer import build as B\n    res = B.build_dressing(_manifest(), str(tmp_path), theme="delco_1997",\n                           options={"save_blend": False})\n    st = res["merge"]\n    assert st and not st["refused"], st\n    assert st["parts_in"] == 8\n    assert st["meshes_out"] == 4\n    vs = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH"\n          for v in o.data.vertices]\n    assert max(v.z for v in vs) == pytest.approx(TOP + D.COPING_H - D.COPING_SINK, abs=1e-4)\n    assert max(v.x for v in vs) == pytest.approx(15.05, abs=1e-4)\n    assert min(v.x for v in vs) == pytest.approx(-15.05, abs=1e-4)\n    assert max(v.y for v in vs) == pytest.approx(11.05, abs=1e-4)\n'}


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
