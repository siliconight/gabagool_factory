"""Patina 0.36.0: a band at the roof line, and every band round its corners (the factory's roadmap 324).

`framing._roof_line_bands` orders a band at a parapet's foot over the roof slab's depth; `framing._corner_bands` closes
every band round the building's outside corners, N and S on past the side face, E and W to the N and S bands' backs.

Proven: tests/test_string_courses.py's roof-line and corner tests fail on 0.35.0 (fails_on_old.out.txt); the clone's
suite (suite_clone.out.txt); the slice rebuilt and priced (the factory's docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'patina'
PINS = {'CHANGELOG.md': '87d75e75235e2455', 'VERSION': '3e110061930cbcff', 'patina/framing.py': 'ee55bb04d5c4a711', 'patina/version.py': '1526206d0419b6fe', 'tests/test_string_courses.py': 'b7d506a6a605ad92'}
EDITS = {'CHANGELOG.md': [('lines 4-5', 'versioning follows [SemVer](https://semver.org/).\n\n', 'versioning follows [SemVer](https://semver.org/).\n\n## [0.36.0] - a band at the roof line, and every band round its corners\n\nThe factory\'s roadmap 324; the walker, 2026-10-29: "detail and placement of hard surfaces". The vertical slice\'s\nfourth build (the factory\'s `docs/findings/slice_look/`).\n\n### Added\n- **A roof-line band under a parapet** (`framing._roof_line_bands`, ordered with the string courses): Deli Counter\n  0.292.0 stands a parapet on the wall below it, so a facade ran from the ground to the coping with nothing marking\n  where the roof is. A band at the parapet\'s foot over the roof slab\'s depth (read from the roof slot under it, as\n  `scupper_sides` does) is the cornice line. Against a parapet standing on its roof there is no depth and no band.\n\n### Fixed\n- **A band stopped a wall short of every outside corner** (`framing._corner_bands`). Deli Counter\'s N and S wall runs\n  stop at the side walls\' inner faces and a corner post seats the corner, so 0.35.0\'s string courses ended there.\n  Per band level, an N or S run reaching an E or W face runs on to it plus the band\'s projection, and an E or W run\n  stops at the N or S band\'s back: they meet, do not overlap, and share no face -- the coping\'s corner rule.\n\nSlice 4: the bank and the card shop carry a cream band at the floor line and another under the parapet, wrapped round\ntheir corners; priced against slice 3b, draws median +0, largest +11 (control floor 21), p95 median +0.031 ms.\nTests: tests/test_string_courses.py, the roof line and the corners (fail on 0.35.0).\n\n')], 'VERSION': [('lines 1-1', 'Patina 0.35.0', 'Patina 0.36.0')], 'patina/framing.py': [('lines 580-580', '    return _join_bands(orders, manifest)\n', '    orders += _roof_line_bands(manifest, uv, seed)\n    return _corner_bands(_join_bands(orders, manifest))\n\n\n#: A ROOF-LINE BAND UNDER A PARAPET (0.36.0, the factory\'s roadmap 324). Deli Counter 0.292.0 stands a parapet on\n#: the wall below it, so a facade runs from the ground to the coping with nothing marking where the roof is. A\n#: commercial front marks it: a band at the parapet\'s foot over the roof slab\'s depth, the cornice line. Patina knows\n#: that depth from the roof slot under the parapet (as `scupper_sides` does). Against a parapet standing on its roof\n#: (Deli Counter < 0.292.0) there is no depth and no band.\n_PARAPET_NORMAL = {"N": (0.0, 1.0), "S": (0.0, -1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0)}\n\n\ndef _roof_line_bands(manifest: SlotManifest, uv, seed: int) -> list[dict]:\n    roofs = [r for r in manifest.slots if r.role == "roof" and r.dims]\n    out = []\n    for s in sorted((s for s in manifest.slots if _is_parapet(s) and s.dims), key=lambda s: s.slot_id):\n        n = _PARAPET_NORMAL.get(str(s.slot_id)[len("parapet_"):][:1])\n        if n is None:\n            continue\n        run, thick, h = s.size()\n        foot = _base_z(s)\n        tops = [r.base_z() + r.size()[2] for r in roofs]\n        tops = [z for z in tops if foot - 1e-6 <= z <= foot + h]\n        if not tops or max(tops) - foot < STRING_MIN_GAP:\n            continue\n        roof_z = max(tops)\n        height = roof_z - foot + 2.0 * STRING_OVER\n        tx, ty = float(s.translation[0]), float(s.translation[1])\n        pos = [round(tx + n[0] * thick / 2.0, 3), round(ty + n[1] * thick / 2.0, 3), round((foot + roof_z) / 2.0, 3)]\n        rng = rng_for(seed, "roof_line", s.slot_id)\n        out.append({\n            "anchor_kind": "roof_line", "cover": "string_course", "collision": "none",\n            "trim_piece": "base_course", "uv_region": uv, "slot_id": s.slot_id,\n            "pos": pos, "normal": [n[0], n[1], 0.0],\n            "size": round(run, 3), "size2": [round(run, 3), round(height, 3)],\n            "seed_offset": int(rng.integers(0, 1_000_000)),\n        })\n    return out\n\n\n#: Zoo\'s string course stands this far out of its face (`core.dressing.STRING_PROUD`) and this far into it\n#: (`STRING_INTO`): mirrored, so a corner can be closed round the band\'s own depth.\n_BAND_PROUD, _BAND_INTO = 0.06, 0.01\n#: A run whose end stands this near the perpendicular face\'s plane ends at a corner.\n_CORNER_REACH = 0.6\n\n\ndef _corner_bands(runs: list[dict]) -> list[dict]:\n    """Close every outside corner round a band, the way the coping closes its own (0.36.0).\n\n    Deli Counter\'s N and S wall runs stop at the side walls\' INNER faces and a corner post seats the corner, so a\n    band built from wall slots stopped short of every corner by a wall. Per band level: an N or S run reaching\n    toward an E or W face plane runs on to that plane plus the band\'s projection, and an E or W run reaching toward\n    an N or S face plane stops at that band\'s back (the plane less `_BAND_INTO`) -- so the two meet and do not\n    overlap, and no face is shared."""\n    levels: dict = {}\n    for o in runs:\n        levels.setdefault((round(o["pos"][2], 3), o["size2"][1]), []).append(o)\n    out = []\n    for _key, group in sorted(levels.items()):\n        planes = {}\n        for o in group:\n            nx, ny = round(o["normal"][0]), round(o["normal"][1])\n            planes[(nx, ny)] = o["pos"][0] if nx else o["pos"][1]\n        for o in group:\n            nx, ny = round(o["normal"][0]), round(o["normal"][1])\n            ax = 0 if nx == 0 else 1\n            half = o["size2"][0] / 2.0\n            a0, a1 = o["pos"][ax] - half, o["pos"][ax] + half\n            lo_key, hi_key = ((-1, 0), (1, 0)) if ax == 0 else ((0, -1), (0, 1))\n            for key, is_hi in ((lo_key, False), (hi_key, True)):\n                if key not in planes:\n                    continue\n                plane = planes[key]\n                end = a1 if is_hi else a0\n                if abs(end - plane) > _CORNER_REACH:\n                    continue\n                if ax == 0:      # N or S: on past the side face by the band\'s projection\n                    target = plane + _BAND_PROUD if is_hi else plane - _BAND_PROUD\n                else:            # E or W: stop at the N or S band\'s back\n                    target = plane - _BAND_INTO if is_hi else plane + _BAND_INTO\n                if is_hi:\n                    a1 = target\n                else:\n                    a0 = target\n            o = dict(o)\n            length = round(a1 - a0, 4)\n            pos = list(o["pos"])\n            pos[ax] = round((a0 + a1) / 2.0, 4)\n            o.update(pos=pos, size=length, size2=[length, o["size2"][1]])\n            out.append(o)\n    return out\n')], 'patina/version.py': [('lines 9-9', '__version__ = "0.35.0"\n', '__version__ = "0.36.0"\n')], 'tests/test_string_courses.py': [('lines 49-49', '        assert x["size2"][0] == pytest.approx(6.0) and len(x["slot_ids"]) == 3   # three 2 m slots, one band\n', '        # three 2 m slots, one band; N and S on round both corners, E and W to the N and S bands\' backs (0.36.0)\n        ns = abs(x["normal"][1]) > 0.5\n        face = 3.15\n        want = 2 * (face + framing._BAND_PROUD) if ns else 2 * (face - framing._BAND_INTO)\n        assert x["size2"][0] == pytest.approx(want) and len(x["slot_ids"]) == 3\n'), ('lines 61-61', '    assert sum(x["size2"][0] for x in north) == pytest.approx(4.0)\n', '    # the two 2 m pieces either side of the door, each run on round its corner (0.36.0)\n    assert sum(x["size2"][0] for x in north) == pytest.approx(4.0 + 2 * (0.15 + framing._BAND_PROUD))\n'), ('lines 73-73', '    assert "ext_1_N_open0" not in {x["slot_id"] for x in o}\n', '    assert "ext_1_N_open0" not in {x["slot_id"] for x in o}\n\n\ndef _parapeted(storeys=2):\n    """`_block` with Deli Counter 0.292.0\'s parapet -- on the walls\' outer faces from the top storey\'s wall top,\n    1.4 m -- and the roof slab under it, 0.3 m thick."""\n    m = _block(storeys=storeys)\n    top = (storeys - 1) * (WALL_H + SLAB) + WALL_H\n    for side, (x, y, rot, run) in {"N": (0.0, 3.05, 0.0, 6.3), "S": (0.0, -3.05, 180.0, 6.3),\n                                   "E": (3.05, 0.0, 90.0, 5.9), "W": (-3.05, 0.0, 270.0, 5.9)}.items():\n        m.slots.append(Slot(slot_id=f"parapet_{side}_t0_0", role="wall", current_ref="wall_greybox_01",\n                            facing=side, story=storeys, translation=(x, y, top + 0.7), rot_y=rot,\n                            dims=(run, 0.2, 1.4)))\n    m.slots.append(Slot(slot_id="roof_footprint", role="roof", current_ref="roof_greybox_01", story=storeys,\n                        translation=(0.0, 0.0, top + SLAB / 2.0), dims=(6.0, 6.0, SLAB)))\n    return m\n\n\ndef test_a_band_marks_the_roof_line_under_a_parapet():\n    """FAILS ON 0.35.0: no band where the roof is."""\n    o = framing.string_course_orders(_parapeted(storeys=2), _regions(), seed=1999)\n    roof = [x for x in o if x["anchor_kind"] == "roof_line"]\n    assert len(roof) == 4\n    top = WALL_H + SLAB + WALL_H\n    for x in roof:\n        assert x["pos"][2] == pytest.approx(top + SLAB / 2.0)\n        assert x["size2"][1] == pytest.approx(SLAB + 2 * framing.STRING_OVER)\n\n\ndef test_the_bands_close_every_outside_corner_without_overlapping():\n    """FAILS ON 0.35.0: a band built from wall slots stopped a wall short of every corner."""\n    o = framing.string_course_orders(_parapeted(storeys=2), _regions(), seed=1999)\n    for level in ("floor_line", "roof_line"):\n        runs = [x for x in o if x["anchor_kind"] == level]\n        n = next(x for x in runs if x["normal"][1] > 0.5)\n        e = next(x for x in runs if x["normal"][0] > 0.5)\n        n_face, e_face = n["pos"][1], e["pos"][0]\n        assert n["pos"][0] + n["size2"][0] / 2 == pytest.approx(e_face + framing._BAND_PROUD)\n        assert e["pos"][1] + e["size2"][0] / 2 == pytest.approx(n_face - framing._BAND_INTO)\n')]}
WHOLE = {}
NEW_FILES = {}


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
