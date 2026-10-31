"""Lot 0.141.0: a shop sign hangs where its building has room for one.

facade_frame from Deli Counter's gameplay and slots; sign_band: the fascia, else the roof edge, sized to the
building.

Proven: tests/test_sign_band.py fails on 0.140.0 (fails_on_old.out.txt); the clone suite fails only the 12
location-only tests an untouched Lot does (suite_clone.out.txt); built into the slice.
"""
import base64
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'lot'
PINS = {'CHANGELOG.md': 'd6ef932b83224f73', 'VERSION': '076a11b838f3c542', 'lot.py': 'c0696bc4f4f98abc'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## 0.140.0 - a utility cut has an age\n', '## 0.141.0 - a shop sign hangs where its building has room for one\n\nThe walker, 2026-10-31: "store signage still looks...wrong ... placement, size of font", with three photographs (the\nfactory\'s `docs/reference/STORE_SIGNAGE_COMPS.md`): a shop\'s name runs across the fascia between the head of its shop\nfront and the eave or the windows above, or, on a low box with no fascia, stands on its roof edge. The band hung at\n`SIGN_Z` (3.6 m) on every building and stopped at `SIGN_MAX_W` (9 m): on the slice\'s self-storage, wall to 3.1 m and\nroof edge 3.4 m, it stood 2.85 to 4.35 m, most of it in the air over the roof; on a 36 m front it was a plaque.\n\n### Added\n- **`facade_frame`**: each face\'s highest storey-0 opening head, lowest storey-1 sill, storey-0 wall top and top\n  (walls, parapet, roof), from Deli Counter\'s gameplay record and the slot manifest beside it; `merge_gameplay` notes\n  it on the building\'s site entry (`_facade`), as it notes the footprint.\n- **`sign_band`**: the FASCIA where there is one -- `SIGN_GAP` (0.2 m) above the shop front\'s heads to `SIGN_GAP` under\n  the storey above\'s sills, or `SIGN_OVER_FLOOR` over a blank upper storey\'s floor line, or the one storey\'s top less\n  `SIGN_COPING` -- `SIGN_FILL` of it, at most `SIGN_MAX_H` (2.2 m); a fascia under `SIGN_MIN_H` (0.6 m) puts the sign\n  on the ROOF EDGE, its foot on the face\'s top, its height from the frontage. `SIGN_ASPECT` wide, to `SIGN_SPAN_MAX` of\n  the facade and `SIGN_MAX_W_FRAMED` (16 m). The scene\'s band and `sign_bands` (the span poles keep out of) both read\n  it. A building with no record keeps the old band. On the slice: the banks and the card shop on their fascias across\n  the floor line (2.5-4.2 m), the self-storage on its roof edge (3.4-5.6 m, 13.2 m wide), the gas station\'s store on\n  its roof edge, the 50 m fronts 13 m wide.\n\nTests: tests/test_sign_band.py (fails on 0.140.0: no `facade_frame` or `sign_band`).\n\n## 0.140.0 - a utility cut has an age\n')], 'VERSION': [('lines 1-1', 'Lot 0.140.0', 'Lot 0.141.0')], 'lot.py': [('lines 359-360', '            b["_footprint"] = gp.get("footprint")\n        site["buildings"].append(record)\n', '            b["_footprint"] = gp.get("footprint")\n        # ITS FACADES\' FRAME (0.141.0): where each face\'s openings and top are, for the sign over its shop front\n        # (`sign_band`), from the gameplay record and the slot manifest Deli Counter writes beside it\n        slots_path = gp_path[:-len(".gameplay.json")] + ".slots.json" if gp_path.endswith(".gameplay.json") else None\n        if slots_path and os.path.exists(slots_path):\n            with open(slots_path, encoding="utf-8") as f:\n                frame = facade_frame(gp, json.load(f))\n            if frame:\n                b["_facade"] = frame\n        site["buildings"].append(record)\n'), ('lines 1231-1232', '\n#: Outdoor families a site spec may skin, and the ext_resource id stem each\n', '\n\n#: A SHOP SIGN HANGS WHERE ITS BUILDING HAS ROOM FOR ONE (0.141.0). The walker, 2026-10-31: "store signage still\n#: looks...wrong ... placement, size of font", with three photographs (the factory\'s\n#: docs/reference/STORE_SIGNAGE_COMPS.md): a shop\'s name runs across the fascia between the head of its shop front\n#: and the eave or the windows above, or -- on a low box with no fascia -- stands on its roof edge. The band hung at\n#: `SIGN_Z` (3.6 m) whatever the building: on the slice\'s self-storage, whose wall stops at 3.1 m and roof edge at\n#: 3.4 m, it stood 2.85 to 4.35 m, most of it in the air over the roof; and it stopped at `SIGN_MAX_W` (9 m) on a\n#: 36 m front. Where the building\'s own record says where its openings and its wall\'s top are (`facade_frame`), the\n#: band takes the FASCIA: `SIGN_GAP` above the highest shop-front head to `SIGN_GAP` under the lowest sill of the\n#: storey above -- or, a storey above with no window on this face, `SIGN_OVER_FLOOR` over the floor line; or the\n#: wall\'s top less `SIGN_COPING` on one storey -- `SIGN_FILL` of it high, at most `SIGN_MAX_H`. A fascia under\n#: `SIGN_MIN_H` puts the sign on the ROOF EDGE, its foot on the wall\'s top, its height from the frontage\n#: (`SIGN_ROOF_PER_M`). Either way it is `SIGN_ASPECT` wide, to `SIGN_SPAN_MAX` of the facade and `SIGN_MAX_W_FRAMED`;\n#: a frontage too short for the width takes the height down with it. A building with no record keeps the old band.\nSIGN_GAP = 0.2\nSIGN_COPING = 0.1\nSIGN_OVER_FLOOR = 1.0\nSIGN_MIN_H = 0.6\nSIGN_MAX_H = 2.2\nSIGN_FILL = 0.85\nSIGN_SPAN_MAX = 0.85\nSIGN_MAX_W_FRAMED = 16.0\nSIGN_ROOF_PER_M = 1.0 / 14.0\nSIGN_ROOF_H = (0.9, 2.2)\n\n\ndef facade_frame(gameplay, slots):\n    """``{side: {"head", "sill1", "top0", "top"}}`` of a building, in its own frame (metres above its floor):\n    the highest storey-0 exterior opening\'s head, the lowest storey-1 exterior opening\'s sill (None when the storey\n    above has no opening on that side), the storey-0 wall\'s top, and the face\'s top (its walls, its parapet, the\n    roof). From Deli Counter\'s gameplay record (its ``openings``) and its slot manifest (each wall, window and\n    doorway slot\'s ``facing``, ``story`` and box)."""\n    out = {}\n\n    def side(s):\n        return out.setdefault(s, {"head": None, "sill1": None, "top0": None, "top": None})\n\n    for o in (gameplay or {}).get("openings") or []:\n        wall = str(o.get("wall") or "")\n        if not wall.startswith("ext_") or wall[-1:] not in "NSEW":\n            continue\n        st = int(o.get("story", 0))\n        z, h = float(o.get("z", 0.0)), float(o.get("height") or 0.0)\n        f = side(wall[-1])\n        if st == 0:\n            f["head"] = max(f["head"] or 0.0, z + h / 2.0)\n        elif st == 1:\n            f["sill1"] = z - h / 2.0 if f["sill1"] is None else min(f["sill1"], z - h / 2.0)\n    roof = None\n    for s in (slots or {}).get("slots") or []:\n        tr, fit = s.get("transform") or {}, s.get("fit") or {}\n        if "translation" not in tr or "dims" not in fit:\n            continue\n        top = float(tr["translation"][2]) + float(fit["dims"][2]) / 2.0\n        if s.get("role") == "roof":\n            roof = top if roof is None else max(roof, top)\n            continue\n        fc = s.get("facing")\n        if fc not in ("N", "S", "E", "W") or s.get("role") not in ("wall", "window", "doorway"):\n            continue\n        st = int(s.get("story") or 0)\n        if st < 0:\n            continue\n        f = side(fc)\n        f["top"] = max(f["top"] or 0.0, top)\n        if st == 0:\n            f["top0"] = max(f["top0"] or 0.0, top)\n    for f in out.values():\n        if roof is not None and f["top"] is not None:\n            f["top"] = max(f["top"], roof)\n    return {k: v for k, v in out.items() if v["head"] is not None and v["top0"] is not None}\n\n\n#: plan yaw of a facade\'s outward normal -> the side it is\n_YAW_SIDE = {0: "E", 90: "N", 180: "W", 270: "S"}\n\n\ndef sign_band(bdef, yaw: float, facade_w: float):\n    """``(z, (w, h), mount)`` for a building\'s sign on the facade facing plan ``yaw``: the band\'s centre above grade,\n    its size, and "fascia", "roof" or "legacy" (no frame: `SIGN_Z` and `sign_size`, as before)."""\n    frame = bdef.get("_facade") or {}\n    local = _YAW_SIDE.get(int(round(float(yaw) - float(bdef.get("rot", 0) or 0))) % 360)\n    f = frame.get(local)\n    if not f:\n        return SIGN_Z, sign_size(facade_w), "legacy"\n    lo = f["head"] + SIGN_GAP\n    if f["sill1"] is not None:\n        hi = f["sill1"] - SIGN_GAP\n    elif f["top"] > f["top0"] + 0.5:\n        hi = f["top0"] + SIGN_OVER_FLOOR\n    else:\n        hi = f["top"] - SIGN_COPING\n    w_cap = min(SIGN_MAX_W_FRAMED, max(SIGN_MIN_W, facade_w * SIGN_SPAN_MAX))\n    if hi - lo >= SIGN_MIN_H:\n        h = min(SIGN_MAX_H, (hi - lo) * SIGN_FILL)\n        w = min(h * SIGN_ASPECT, w_cap)\n        h = w / SIGN_ASPECT\n        return (lo + hi) / 2.0, (w, h), "fascia"\n    h = max(SIGN_ROOF_H[0], min(SIGN_ROOF_H[1], facade_w * SIGN_ROOF_PER_M))\n    w = min(h * SIGN_ASPECT, w_cap)\n    h = w / SIGN_ASPECT\n    return f["top"] + h / 2.0, (w, h), "roof"\n\n#: Outdoor families a site spec may skin, and the ext_resource id stem each\n'), ('lines 1501-1501', '        w, _h = sign_size(facade)\n', '        _z, (w, _h), _mount = sign_band(b, yaw, facade)\n'), ('lines 2758-2759', '        bl, sr = _sign_node(f"sign_{b[\'id\']}", (sx, SIGN_Z, -sy),\n                            sign_facing(yaw), sign, sign_size(facade))\n', '        # where the building has room for it (0.141.0, `sign_band`)\n        sz, ssize, _mount = sign_band(b, yaw, facade)\n        bl, sr = _sign_node(f"sign_{b[\'id\']}", (sx, sz, -sy),\n                            sign_facing(yaw), sign, ssize)\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_sign_band.py': '"""A shop sign hangs where its building has room for one (Lot 0.141.0).\n\nThe walker, 2026-10-31: "store signage still looks...wrong ... placement, size of font". The band hung at 3.6 m on\nevery building and stopped at 9 m: on the slice\'s self-storage (wall to 3.1 m, roof edge 3.4 m) it stood mostly over\nthe roof, and on a 36 m front it was a plaque. FAILS ON 0.140.0: there is no `facade_frame` or `sign_band`.\n"""\nimport os\nimport sys\n\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nimport lot  # noqa: E402\n\n\ndef _slot(role, facing, story, z_top, h=3.0):\n    return {"role": role, "facing": facing, "story": story,\n            "transform": {"translation": [0.0, 0.0, z_top - h / 2.0]}, "fit": {"dims": [2.0, 0.3, h]}}\n\n\ndef _op(story, z, h, side="S"):\n    return {"wall": "ext_%d_%s" % (story, side), "story": story, "z": z, "height": h}\n\n\ndef test_a_two_storey_shop_signs_its_fascia_between_the_shop_front_and_the_windows_above():\n    """The card shop\'s own numbers: heads 2.2 m, the upper sills 4.4 m, its storey-0 wall to 3.15 m."""\n    gp = {"openings": [_op(0, 1.1, 2.2), _op(0, 1.0, 2.0), _op(1, 5.1, 1.4)]}\n    slots = {"slots": [_slot("wall", "S", 0, 3.15), _slot("wall", "S", 1, 6.55), _slot("roof", "up", 2, 6.8, 0.3)]}\n    frame = lot.facade_frame(gp, slots)\n    assert frame["S"]["head"] == 2.2 and abs(frame["S"]["sill1"] - 4.4) < 1e-9 and frame["S"]["top0"] == 3.15\n    b = {"id": "b0", "rot": 0, "_facade": frame}\n    z, (w, h), mount = lot.sign_band(b, 270.0, 20.0)\n    assert mount == "fascia"\n    assert 2.2 + lot.SIGN_GAP <= z - h / 2.0 and z + h / 2.0 <= 4.4 - lot.SIGN_GAP\n    assert abs(w / h - lot.SIGN_ASPECT) < 1e-9 and w <= 20.0 * lot.SIGN_SPAN_MAX\n\n\ndef test_a_low_box_with_no_fascia_signs_its_roof_edge():\n    """The self-storage: a garage head at 3.0 m, the wall to 3.1 m, the roof to 3.4 m -- no room under the eave, so\n    the sign stands on the roof edge, its foot on the face\'s top; a 36 m front gets a sign bigger than 9 m."""\n    gp = {"openings": [_op(0, 1.1, 2.2), _op(0, 1.5, 3.0)]}\n    slots = {"slots": [_slot("wall", "S", 0, 3.1), _slot("doorway", "S", 0, 3.1), _slot("roof", "up", 1, 3.4, 0.3)]}\n    b = {"id": "b3", "rot": 0, "_facade": lot.facade_frame(gp, slots)}\n    z, (w, h), mount = lot.sign_band(b, 270.0, 36.0)\n    assert mount == "roof"\n    assert abs((z - h / 2.0) - 3.4) < 1e-9\n    assert w > lot.SIGN_MAX_W and w <= lot.SIGN_MAX_W_FRAMED\n\n\ndef test_a_turned_building_reads_its_own_side_and_no_record_keeps_the_old_band():\n    gp = {"openings": [_op(0, 1.1, 2.2, side="N")]}\n    slots = {"slots": [_slot("wall", "N", 0, 3.9), _slot("roof", "up", 1, 4.2, 0.3)]}\n    b = {"id": "b0", "rot": 180, "_facade": lot.facade_frame(gp, slots)}\n    # turned half round, its local north faces plan south\n    assert lot.sign_band(b, 270.0, 20.0)[2] == "fascia"\n    assert lot.sign_band({"id": "b1", "rot": 0}, 270.0, 20.0) == (lot.SIGN_Z, lot.sign_size(20.0), "legacy")\n'}
#: binary files (a font, a texture): base64, each pinned by its sha256
BINARY_FILES = {}


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
    for name in list(NEW_FILES) + list(BINARY_FILES):
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    blobs = {}
    for name, (digest, b64) in BINARY_FILES.items():
        blobs[name] = base64.b64decode(b64)
        if hashlib.sha256(blobs[name]).hexdigest() != digest:
            raise SystemExit("REFUSED: %s/%s does not decode to its sha256; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, raw in blobs.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(raw)
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES) + len(blobs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
