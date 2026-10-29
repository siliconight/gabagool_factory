"""Patina 0.38.0: quoins up a civic building's corners (the factory's roadmap 324).

`framing.quoin_orders` emits dressed stone blocks up each outside corner of a bank, credit union, courthouse, library
or post office that is not an Empty -- alternately long and short on each face, wrapped by the bands' corner rule,
clear of the bands and of keep-outs -- as `string_course` orders in the stone trim; the CLI emits them after the
string courses.

Proven: tests/test_quoins.py fails on 0.37.0 (fails_on_old.out.txt); the clone's suite, 417 passed, 11 skipped
(suite_clone.out.txt); the slice rebuilt and priced (the factory's docs/findings/slice_look/, slice 8).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'patina'
PINS = {'CHANGELOG.md': 'fa99986c1e4bbb71', 'VERSION': 'e7d5409ac465a167', 'patina/cli.py': '62bb2eecf09224b7', 'patina/framing.py': '30bbc49c2ddee750', 'patina/version.py': '49d1e24621f6c4ec'}
EDITS = {'CHANGELOG.md': [('lines 4-5', 'versioning follows [SemVer](https://semver.org/).\n\n', 'versioning follows [SemVer](https://semver.org/).\n\n## [0.38.0] - quoins up a civic building\'s corners\n\nThe factory\'s roadmap 324; the walker, 2026-10-29, of the game\'s vertical slice: "Things still look simple, and\ncomputer made", and of the target, "detail and placement of hard surfaces". The slice\'s bank had bands at its floor\nlines and roof line and plain corners between them: the stone stopped where the walls met.\n\n### Added\n- **`framing.quoin_orders`**: on a building whose id carries one of `CIVIC_WORDS` (a bank, a credit union, a\n  courthouse, a library, a post office...) and that is not an Empty, a column of dressed blocks up each outside\n  corner -- `QUOIN_H` tall with a `QUOIN_JOINT` between, alternately `QUOIN_LONG` and `QUOIN_SHORT` along each face,\n  the long face swapping at every course, as a laid quoin does -- in the stone trim the string course is\n  (`string_course` orders with `anchor_kind` "quoin"), wrapped round the corner by the band\'s own rule, and a block\n  within `QUOIN_BAND_CLEAR` of a band left out so the two do not overlap. A pair either half of which meets a\n  keep-out (an opening, a downspout) is dropped whole. The CLI emits them after the string courses, which they read.\n  On the slice (the factory\'s `docs/findings/slice_look/`, slice 8): bank_branch_a02 136 blocks over 17 courses, the\n  card shop none; priced against slice 7, draws median +0, largest +2 -- the blocks merge into the side\'s\n  string-course mesh; the frame time was read while Deli Counter\'s library gate ran, the controls 1.5 ms apart, so\n  its median +0.08 ms says nothing either way. Tests: tests/test_quoins.py (fails on 0.37.0).\n\n')], 'VERSION': [('lines 1-1', 'Patina 0.37.0', 'Patina 0.38.0')], 'patina/cli.py': [('lines 468-470', "                panels += framing.string_course_orders(\n                    slot_manifest, regions, seed=args.seed)\n            # The keep-out rule needs DC's openings, which only the slot\n", "                bands = framing.string_course_orders(\n                    slot_manifest, regions, seed=args.seed)\n                panels += bands\n                # and quoins up a civic building's corners, clear of the bands (0.38.0)\n                panels += framing.quoin_orders(\n                    slot_manifest, regions, seed=args.seed, bands=bands)\n            # The keep-out rule needs DC's openings, which only the slot\n")], 'patina/framing.py': [('lines 717-718', '\ndef _is_parapet(slot) -> bool:\n', '\n#: QUOINS AT A CIVIC BUILDING\'S CORNERS (0.38.0, the factory\'s roadmap 324). The walker\'s comps, 2026-10-29: a bank\n#: reads as a bank from 50 m -- "an architectural language per building type" (the factory\'s\n#: docs/findings/slice_look/). The slice\'s bank read as a two-storey commercial box with two cream bands. Quoins --\n#: dressed stone blocks at the outside corners, alternately long and short on the two faces -- are what makes a civic\n#: front read solid and deliberate. Each block on each face is a short `string_course` in the stone trim (Zoo builds it\n#: as it builds the bands), closed round the corner by the bands\' rule (`_corner_bands`): the N or S block runs on past\n#: the side face by the band\'s projection, the E or W block stops at its back. A block within `QUOIN_BAND_CLEAR` of a\n#: band is left out -- both stand `_BAND_PROUD` from the face, and where they crossed their fronts would be one plane.\nCIVIC_WORDS = ("bank", "credit", "courthouse", "landmark", "municipal", "library", "post_office")\nQUOIN_H = 0.32\nQUOIN_JOINT = 0.03\nQUOIN_LONG = 0.62\nQUOIN_SHORT = 0.36\nQUOIN_BAND_CLEAR = 0.05\n\n\ndef quoin_orders(manifest: SlotManifest, regions: list, *, seed: int, bands=()) -> list[dict]:\n    """Quoins up every outside corner of a civic building that is not an Empty, as `string_course` orders."""\n    bid = str(manifest.building_id or "").lower()\n    if not any(w in bid for w in CIVIC_WORDS) or any(s.glazing == "facade" for s in manifest.slots):\n        return []\n    from . import openings as _openings\n    uv = _uv(regions, "base_course")\n    center = footprint_center(manifest)\n    thick_m = modal_thickness(manifest)\n    faces = [s for s in manifest.slots if s.dims and str(s.slot_id).startswith("ext_")\n             and s.story is not None and (s.role == "wall" or s.role in _FACE_ROLES)]\n    if not faces:\n        return []\n    planes: dict = {}\n    for s in faces:\n        frame = wall_frame(s, center, thick_m)\n        pos, _n = _face(s, 0.0, 0.0, frame)\n        key = _side(frame)\n        planes.setdefault(key, []).append(pos[0] if key[0] else pos[1])\n    planes = {k: sorted(v)[len(v) // 2] for k, v in planes.items()}\n    if not all(k in planes for k in ((0, 1), (0, -1), (1, 0), (-1, 0))):\n        return []\n    ground_floor = [s for s in faces if int(s.story) == 0] or faces\n    ground = min(_base_z(s) for s in ground_floor)\n    top = max(_base_z(s) + s.size()[2] for s in faces)\n    clear = [(b["pos"][2] - b["size2"][1] / 2.0 - QUOIN_BAND_CLEAR, b["pos"][2] + b["size2"][1] / 2.0 + QUOIN_BAND_CLEAR)\n             for b in bands]\n    boxes = _openings.keep_out_boxes(manifest)\n    n_y, s_y, e_x, w_x = planes[(0, 1)], planes[(0, -1)], planes[(1, 0)], planes[(-1, 0)]\n    orders = []\n    z, k = ground, 0\n    while z + QUOIN_H <= top + 1e-6:\n        zc = z + QUOIN_H / 2.0\n        if not any(lo < zc + QUOIN_H / 2.0 and zc - QUOIN_H / 2.0 < hi for lo, hi in clear):\n            for ex, ey in ((1, 1), (1, -1), (-1, 1), (-1, -1)):\n                long_ns = (k + (ex > 0) + (ey > 0)) % 2 == 0\n                a = QUOIN_LONG if long_ns else QUOIN_SHORT\n                b = QUOIN_SHORT if long_ns else QUOIN_LONG\n                yp = n_y if ey > 0 else s_y\n                xp = e_x if ex > 0 else w_x\n                # N or S face: from the corner inward by a, on past the side face by the band\'s projection\n                x0, x1 = sorted((xp - ex * a, xp + ex * _BAND_PROUD))\n                # E or W face: from the N or S face inward by b, to that block\'s back\n                y0, y1 = sorted((yp - ey * b, yp - ey * _BAND_INTO))\n                pair = []\n                for nrm, pos, length in (((0.0, float(ey), 0.0), [(x0 + x1) / 2.0, yp, zc], x1 - x0),\n                                         ((float(ex), 0.0, 0.0), [xp, (y0 + y1) / 2.0, zc], y1 - y0)):\n                    rng = rng_for(seed, "quoin", f"{ex}{ey}{k}{nrm[0]}")\n                    pair.append({\n                        "anchor_kind": "quoin", "cover": "string_course", "collision": "none",\n                        "trim_piece": "base_course", "uv_region": uv, "slot_id": f"quoin_{ex}{ey}_{k}",\n                        "pos": [round(v, 4) for v in pos], "normal": list(nrm),\n                        "size": round(length, 4), "size2": [round(length, 4), QUOIN_H],\n                        "seed_offset": int(rng.integers(0, 1_000_000)),\n                    })\n                if boxes and any(_openings.hits(o, boxes) for o in pair):\n                    continue\n                orders.extend(pair)\n        z += QUOIN_H + QUOIN_JOINT\n        k += 1\n    return orders\n\n\ndef _is_parapet(slot) -> bool:\n')], 'patina/version.py': [('lines 9-9', '__version__ = "0.37.0"\n', '__version__ = "0.38.0"\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_quoins.py': '"""Quoins up a civic building\'s corners (0.38.0, the factory\'s roadmap 324).\n\nThe slice\'s bank read as a two-storey commercial box. Dressed stone blocks at its outside corners, alternately long and\nshort on the two faces, closed round each corner by the bands\' rule and kept clear of the bands themselves.\n"""\nimport pytest\n\nfrom patina import framing, trim\nfrom patina.slots import SlotManifest\nfrom tests.test_string_courses import _block, _regions  # noqa: F401  (the string courses\' own fixture)\n\n\ndef _named(m, bid):\n    return SlotManifest(version=m.version, building_id=bid, theme=m.theme, module_library=m.module_library,\n                        module_size=m.module_size, space=m.space, slots=m.slots)\n\n\ndef test_a_bank_carries_quoins_and_a_shop_does_not():\n    """FAILS ON 0.37.0: no quoins."""\n    m = _block(storeys=2)\n    bands = framing.string_course_orders(m, _regions(), seed=1999)\n    bank = framing.quoin_orders(_named(m, "bank_branch_a02"), _regions(), seed=1999, bands=bands)\n    assert bank and all(o["cover"] == "string_course" and o["anchor_kind"] == "quoin" for o in bank)\n    assert framing.quoin_orders(_named(m, "card_shop_a01"), _regions(), seed=1999, bands=bands) == []\n\n\ndef test_blocks_alternate_close_their_corners_and_keep_clear_of_the_bands():\n    m = _block(storeys=2)\n    bands = framing.string_course_orders(m, _regions(), seed=1999)\n    q = framing.quoin_orders(_named(m, "bank_branch_a02"), _regions(), seed=1999, bands=bands)\n    face = 3.15                                                        # the fixture\'s walls\' outer faces\n    ne = [o for o in q if o["slot_id"].startswith("quoin_11_")]\n    by_level = {}\n    for o in ne:\n        by_level.setdefault(o["pos"][2], []).append(o)\n    lens = []\n    for zc, pair in sorted(by_level.items()):\n        n = next(o for o in pair if o["normal"][1] > 0.5)\n        e = next(o for o in pair if o["normal"][0] > 0.5)\n        assert n["pos"][0] + n["size2"][0] / 2 == pytest.approx(face + framing._BAND_PROUD)   # wraps the corner\n        assert e["pos"][1] + e["size2"][0] / 2 == pytest.approx(face - framing._BAND_INTO)    # stops at its back\n        lens.append(round(n["size2"][0], 3))\n        for b in bands:                                                 # never across a band\n            assert abs(zc - b["pos"][2]) >= (framing.QUOIN_H + b["size2"][1]) / 2\n    # long and short on the N face, by course: a course skipped at a band breaks strict neighbour alternation, so\n    # what is held is that both lengths stand at the corner, each with its wrap\n    assert set(lens) == {round(framing.QUOIN_LONG + framing._BAND_PROUD, 3),\n                         round(framing.QUOIN_SHORT + framing._BAND_PROUD, 3)}\n'}


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
