"""Zoo 1.148.0: a string course (the factory's roadmap 324).

The `string_course` cover, Patina's floor-line band, built 6 cm proud of the face in the stone trim.

Proven: tests/test_string_course.py fails on 1.147.0 (fails_on_old.out.txt); the clone's suite, 7,075 passed, 546
skipped, 1 xfailed, and its whole Blender set, 3,150 passed; the slice rebuilt and priced (the factory's
docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': 'd514f2dd515a9545', 'VERSION': '9846f4a0b8d4a3b1', 'zoo_keeper/core/dressing.py': '3a0690b9036db30d', 'zoo_keeper/recipes/dress_cover.py': 'a22eb8e9b7c42f44'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [1.147.0] - a scupper and a conductor head\n', '## [1.148.0] - a string course\n\nThe factory\'s roadmap 324; the walker, 2026-10-29: "Things still look simple, and computer made", and of the target,\n"the detail and placement of hard surfaces ... contrast of colors used". Patina (>= 0.35.0) orders a band at every\nfloor line of a building that is not an Empty, over the slab edge Deli Counter leaves recessed half a wall there.\n\n### Added\n- **The `string_course` cover** (`core.dressing.string_course_parts`): a box `STRING_PROUD` (6 cm) out of the face\n  and `STRING_INTO` (1 cm) into it over the run and height Patina declares, in the STONE TRIM (`STONE_TRIM_COVERS`,\n  the Empties\' lintels\' and sills\' cream plaster): in the covers\' concrete it vanished into a concrete wall on the\n  slice. Slice 3b (the factory\'s `docs/findings/slice_look/`): the bank\'s flank groove is a continuous cream band,\n  the card shop has a stone band between its brick and its storefront; priced against slice 2, draws median +3,\n  largest +10.5 (control floor 21), p95 median +0.014 ms. Tests: tests/test_string_course.py (fails on 1.147.0).\n\n## [1.147.0] - a scupper and a conductor head\n')], 'VERSION': [('lines 1-1', '1.147.0', '1.148.0')], 'zoo_keeper/core/dressing.py': [('lines 113-113', 'STONE_TRIM_COVERS = ("lintel", "window_sill")\n', 'STONE_TRIM_COVERS = ("lintel", "window_sill", "string_course")\n'), ('lines 156-157', '             (max(float(length), 0.05), max(float(width), 0.05), COPING_H))]\n\n', '             (max(float(length), 0.05), max(float(width), 0.05), COPING_H))]\n\n\n#: A STRING COURSE (Patina\'s floor-line band, the factory\'s roadmap 324): a band across a facade at a floor line,\n#: over the slab\'s recessed edge, `size2` = [run, height] from Patina. IN THE STONE TRIM (`STONE_TRIM_COVERS`): built\n#: in the covers\' concrete it vanished into a concrete wall on the slice (the factory\'s docs/findings/slice_look/,\n#: slice 3), and the walker asks for "contrast of colors used"; a cream band reads on brick and on render alike. It stands `STRING_PROUD` out of the wall face\n#: and reaches `STRING_INTO` into it, so its back is never the face\'s plane; its top is bevelled by the cover\'s own\n#: bevel. Six centimetres proud reads as a shadow line at street distance, as the window sill\'s five does.\nSTRING_PROUD = 0.06\nSTRING_INTO = 0.01\n\n\ndef string_course_parts(run: float, height: float):\n    """A string course\'s one box, in cover-local space: x along the wall, y out of the face, z about its middle."""\n    y0, y1 = -STRING_INTO, STRING_PROUD\n    return [((0.0, (y0 + y1) / 2.0, 0.0), (max(float(run), 0.05), y1 - y0, max(float(height), 0.05)))]\n\n')], 'zoo_keeper/recipes/dress_cover.py': [('lines 40-41', "  ``core.dressing.dish_parts``).\n* ``coping``       — a parapet run's cap, over the whole wall and past both\n", "  ``core.dressing.dish_parts``).\n* ``string_course`` — a band across a facade at a floor line (``size2`` =\n  [run, height]; ``core.dressing.string_course_parts``).\n* ``coping``       — a parapet run's cap, over the whole wall and past both\n"), ('lines 73-74', '                             coping_parts, dish_parts, downspout_parts, frame_strips,\n                             gutter_parts, lintel_parts, security_door_parts,\n', '                             coping_parts, dish_parts, downspout_parts, frame_strips,\n                             string_course_parts,\n                             gutter_parts, lintel_parts, security_door_parts,\n'), ('lines 121-122', '        for center, size in parts:\n            geometry.add_box(bm, center, size)\n', '        for center, size in parts:\n            geometry.add_box(bm, center, size)\n    elif cover == "string_course":\n        # a floor line\'s band; `size2` is [run, height]\n        run, height = (order.get("size2") or [2.0, 0.4])[:2]\n        for center, size in string_course_parts(run, height):\n            geometry.add_box(bm, center, size)\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_string_course.py': '"""A string course (the factory\'s roadmap 324): Patina\'s floor-line band, built proud of the face, into the wall a\ncentimetre, over its declared height, in the stone trim."""\nimport pytest\n\nfrom zoo_keeper import TOOL_VERSION\nfrom zoo_keeper.core import dressing as D\nfrom zoo_keeper.core import genome\n\n\ndef test_the_band_stands_out_of_the_face_and_into_the_wall():\n    """FAILS ON 1.147.0: no string course."""\n    [(c, s)] = D.string_course_parts(2.0, 0.4)\n    assert s == pytest.approx((2.0, D.STRING_PROUD + D.STRING_INTO, 0.4))\n    assert c[1] - s[1] / 2 == pytest.approx(-D.STRING_INTO)\n    assert c[1] + s[1] / 2 == pytest.approx(D.STRING_PROUD)\n    assert c[2] == 0.0\n\n\ndef test_it_is_the_stone_trim():\n    order = {"cover": "string_course", "pos": [0, 3.15, 3.45], "normal": [0, 1, 0], "size": 2.0,\n             "size2": [2.0, 0.4], "collision": "none", "seed_offset": 1}\n    plan = D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997",\n                        "spec/Blender Z-up raw coords", TOOL_VERSION)\n    assert plan["material"] == D.STONE_TRIM_KIND and plan["order"]["size2"] == [2.0, 0.4]\n'}


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
