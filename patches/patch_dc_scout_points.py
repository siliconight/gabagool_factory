"""Deli Counter 0.260.0 (the factory's roadmap 295): the scout model in the walker's handheld palette, with the score
and the props of interest in it.

The walker: "roughly be in the style of a 1990s palm pilot...but with a little more backlight and color", and
"buildings should show the 'score' location and key props of interest". `palm` becomes the default palette; every
objective marker stands a score beacon, every loot and camera marker, safe and ATM a lit block, each storey's a mesh
of their own under it, the scene's `extras.points` naming each.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `scout_model.py` and `test_scout_model.py` (anchored hunks); VERSION; the CHANGELOG entry, prepended.
Generated from a proven clone (`patches/dc_scout_points/gen_dc_scout_points.py`), dry-run on a fresh clone to the
clone's every byte, a second run refused (`patches/dc_scout_points/dry_run_*.out.txt`).

    python patches/patch_dc_scout_points.py
    cd deli_counter && python -m pytest -q && python check.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "deli_counter"
PINS = {'scout_model.py': 'b5861f6b7fe6cb9d', 'test_scout_model.py': '4545ef2c622fa9f0'}
EDITS = {'scout_model.py': [('lines 10-11', 'markers, as the scout view.\n\n', 'markers, as the scout view.\n\nTHE SCORE AND WHAT IS WORTH KNOWING (0.260.0). The walker: "buildings should show the \'score\' location and key props\nof interest". Each storey carries a second mesh, ``points``, apart from its structure so a viewer can light or pulse it\non its own: a beacon -- plinth, mast, a block on top -- at every `objective` marker (the score), and at every `loot`\nmarker, `camera_socket` marker, safe and ATM a lit block where it stands (`POINTS_OF_INTEREST`). The scene\'s\n``extras.points`` lists every one -- kind, label, storey, and where it stands in the model\'s frame -- so a viewer can\nname them. Spawns are not drawn: they are the gameplay layer\'s, and provisional.\n\n'), ('lines 43-43', '#: Colours as they show on screen (sRGB 0-1). The walker picks one (2026-10-22, three put to them). Every role a\n', '#: Colours as they show on screen (sRGB 0-1). The walker\'s direction (2026-10-22): "roughly be in the style of a\n#: 1990s palm pilot...but with a little more backlight and color" -- `palm`, the default since 0.260.0; the three\n#: before it were put to them first. Every role a\n'), ('lines 46-48', 'ROLES_READ = ("glass", "door", "entry", "tread", "ladder", "hole_rim")\nPALETTES = {\n    "blueprint": {"slab": (0.10, 0.20, 0.38), "slab_side": (0.07, 0.14, 0.28), "wall": (0.62, 0.82, 0.95),\n', 'ROLES_READ = ("glass", "door", "entry", "tread", "ladder", "hole_rim", "score", "poi")\nPALETTES = {\n    # a 1990s handheld\'s LCD, backlit: grey-green floors, ink walls, a few lit accents for what a player hunts for\n    "palm": {"slab": (0.47, 0.58, 0.45), "slab_side": (0.30, 0.38, 0.29), "wall": (0.16, 0.21, 0.16),\n             "cap": (0.06, 0.09, 0.06), "glass": (0.45, 0.85, 0.95), "door": (0.30, 0.40, 0.29),\n             "entry": (1.00, 0.55, 0.20), "tread": (1.00, 0.85, 0.35), "ladder": (0.55, 1.00, 0.75),\n             "hole_rim": (1.00, 0.40, 0.70), "score": (1.00, 0.22, 0.22), "poi": (0.80, 0.55, 1.00),\n             "background": (0.56, 0.68, 0.53)},\n    "blueprint": {"slab": (0.10, 0.20, 0.38), "slab_side": (0.07, 0.14, 0.28), "wall": (0.62, 0.82, 0.95),\n'), ('lines 51-51', '                  "hole_rim": (1.00, 0.30, 0.65), "background": (0.03, 0.06, 0.12)},\n', '                  "hole_rim": (1.00, 0.30, 0.65), "score": (1.00, 0.20, 0.30), "poi": (0.75, 0.55, 1.00),\n                  "background": (0.03, 0.06, 0.12)},\n'), ('lines 55-55', '              "hole_rim": (0.55, 0.25, 0.60), "background": (0.13, 0.14, 0.16)},\n', '              "hole_rim": (0.55, 0.25, 0.60), "score": (0.85, 0.10, 0.45), "poi": (0.20, 0.45, 0.80),\n              "background": (0.13, 0.14, 0.16)},\n'), ('lines 59-59', '                "hole_rim": (0.20, 0.30, 0.55), "background": (0.82, 0.79, 0.70)},\n', '                "hole_rim": (0.20, 0.30, 0.55), "score": (0.95, 0.35, 0.05), "poi": (0.45, 0.20, 0.55),\n                "background": (0.82, 0.79, 0.70)},\n'), ('lines 61-61', 'DEFAULT_PALETTE = "blueprint"\n', 'DEFAULT_PALETTE = "palm"\n'), ('lines 209-210', '\ndef model_stats(spec, palette=DEFAULT_PALETTE):\n', '\n#: What a scout is shown besides the structure: the score (an `objective` marker) and the props worth knowing\n#: about. Markers by type, volumes by the kind their name begins with. Label is what a viewer names it.\nPOINTS_OF_INTEREST = {\n    ("marker", "objective"): ("score", "SCORE"),\n    ("marker", "loot"): ("poi", "LOOT"),\n    ("marker", "camera_socket"): ("poi", "CAMERA"),\n    ("volume", "safe"): ("poi", "SAFE"),\n    ("volume", "atm"): ("poi", "ATM"),\n}\n#: A score beacon: plinth, mast and a block on top, standing over the floor so it reads from any side.\nBEACON_H = 3.0\n\n\ndef points(spec):\n    """Every point of interest, in spec metres: [{kind, label, storey, x, y, z (over its storey\'s floor), size}],\n    markers first then volumes, each in spec order."""\n    sh = FP._story_height(spec)\n    stories = set(FP.stories_in(spec))\n    out = []\n    for m in getattr(spec, "markers", []) or []:\n        hit = POINTS_OF_INTEREST.get(("marker", m.type))\n        s = FP._marker_story(spec, m)\n        if hit and s in stories:\n            out.append({"kind": hit[0], "label": hit[1], "storey": s, "x": m.x, "y": m.y,\n                        "z": max(0.0, (getattr(m, "z", 0.0) or 0.0) - s * sh), "size": None})\n    for v in getattr(spec, "volumes", []) or []:\n        hit = POINTS_OF_INTEREST.get(("volume", str(v.name).split("_")[0]))\n        if not hit or not getattr(v, "visual", True):\n            continue\n        base = (getattr(v, "z", 0.0) or 0.0) - v.size_z / 2\n        s = next((k for k in sorted(stories) if k * sh - 0.6 <= base < (k + 1) * sh - 0.6), None)\n        if s is None:\n            continue\n        out.append({"kind": hit[0], "label": hit[1], "storey": s, "x": v.x, "y": v.y,\n                    "z": max(0.0, base - s * sh), "size": (v.size_x, v.size_y, v.size_z)})\n    return out\n\n\ndef _point_meshes(spec, pal):\n    """{storey: _Mesh} of the points of interest on it."""\n    out = {}\n    for p in points(spec):\n        m = out.setdefault(p["storey"], _Mesh())\n        x, y, z = p["x"], p["y"], p["z"]\n        col = pal[p["kind"]]\n        if p["kind"] == "score":\n            m.box(x - 0.45, y - 0.45, z, x + 0.45, y + 0.45, z + 0.10, col)\n            m.box(x - 0.10, y - 0.10, z + 0.10, x + 0.10, y + 0.10, z + BEACON_H - 0.7, col)\n            m.box(x - 0.40, y - 0.40, z + BEACON_H - 0.7, x + 0.40, y + 0.40, z + BEACON_H, col)\n        elif p["size"]:\n            sx, sy, sz = p["size"]\n            m.box(x - sx / 2, y - sy / 2, z, x + sx / 2, y + sy / 2, z + min(sz, 1.6), col)\n        else:\n            m.box(x - 0.2, y - 0.2, z, x + 0.2, y + 0.2, z + 0.4, col)\n    return out\n\n\ndef model_stats(spec, palette=DEFAULT_PALETTE):\n'), ('lines 217-217', '    ``extras.storey`` and ``extras.elevation``), one material, colour as normalised bytes in ``COLOR_0``."""\n', '    ``extras.storey`` and ``extras.elevation``), and under it, where the storey has any, its points of interest\n    (``storey_<n>_points``, a mesh of their own); one material, colour as normalised bytes in ``COLOR_0``; the\n    scene\'s ``extras.points`` naming every point, its ``at`` in the model\'s frame (x, y up, z south)."""\n'), ('lines 233-235', '    for s, m in sorted(_storeys(spec, pal).items()):\n        if not m.idx:\n            continue\n', '    def mesh(name, m):\n'), ('lines 243-243', '        meshes.append({"name": "storey_%d" % s, "primitives": [\n', '        meshes.append({"name": name, "primitives": [\n'), ('lines 245-247', '        nodes.append({"name": "storey_%d" % s, "mesh": len(meshes) - 1,\n                      "translation": [0.0, round(s * sh, 6), 0.0],\n                      "extras": {"storey": s, "elevation": round(s * sh, 6)}})\n', '        return len(meshes) - 1\n\n    pts = _point_meshes(spec, pal)\n    for s, m in sorted(_storeys(spec, pal).items()):\n        if not m.idx:\n            continue\n        if s in pts:\n            nodes.append({"name": "storey_%d_points" % s, "mesh": mesh("storey_%d_points" % s, pts[s]),\n                          "extras": {"storey": s, "points": True}})\n        node = {"name": "storey_%d" % s, "mesh": mesh("storey_%d" % s, m),\n                "translation": [0.0, round(s * sh, 6), 0.0],\n                "extras": {"storey": s, "elevation": round(s * sh, 6)}}\n        if s in pts:\n            node["children"] = [len(nodes) - 1]\n        nodes.append(node)\n'), ('lines 249-249', '            "scene": 0, "scenes": [{"name": spec.name, "nodes": list(range(len(nodes))),\n', '            "scene": 0, "scenes": [{"name": spec.name,\n                                    "nodes": [k for k, n in enumerate(nodes) if not n["extras"].get("points")],\n'), ('lines 251-251', '                                               "background": list(pal["background"])}}],\n', '                                               "background": list(pal["background"]),\n                                               "points": [{"kind": p["kind"], "label": p["label"],\n                                                           "storey": p["storey"],\n                                                           "at": [round(p["x"], 3), round(p["storey"] * sh + p["z"], 3),\n                                                                  round(-p["y"], 3)]}\n                                                          for p in points(spec)]}}],\n')], 'test_scout_model.py': [('lines 49-50', '        assert [n["extras"]["storey"] for n in g["nodes"]] == stories, name\n        for n in g["nodes"]:\n', '        floors = [n for n in g["nodes"] if not n["extras"].get("points")]\n        assert [n["extras"]["storey"] for n in floors] == stories, name\n        for n in floors:\n'), ('lines 52-52', '        assert len(g["materials"]) == 1 and len(g["meshes"]) == len(stories), name\n', '        # a mesh a storey, and one more on each storey with points of interest (0.260.0)\n        with_points = len({p["storey"] for p in g["scenes"][0]["extras"]["points"]})\n        assert len(g["materials"]) == 1 and len(g["meshes"]) == len(stories) + with_points, name\n'), ('lines 106-107', '\ndef test_doors_in_from_outside_wear_the_entry_colour():\n', '\ndef test_the_score_and_every_prop_of_interest_is_in_the_model():\n    """The walker: "buildings should show the \'score\' location and key props of interest". Every objective marker\n    is a score beacon on its storey, every safe, ATM, loot and camera marker a point; the scene names each one, and\n    each storey\'s points are a node of their own under it."""\n    seen = {}\n    for name in NAMES + ("bank_branch_a02", "apartment_walkup_a01"):\n        spec = _load(name)\n        want = [(m.type, FP._marker_story(spec, m)) for m in spec.markers\n                if m.type in ("objective", "loot", "camera_socket")]\n        want += [(v.name.split("_")[0], None) for v in spec.volumes\n                 if v.name.split("_")[0] in ("safe", "atm") and getattr(v, "visual", True)]\n        g = _gltf(SM.build_glb(spec))\n        pts = g["scenes"][0]["extras"]["points"]\n        assert len(pts) == len(want), (name, len(pts), len(want))\n        scores = [p for p in pts if p["label"] == "SCORE"]\n        assert len(scores) == sum(1 for t, _s in want if t == "objective"), name\n        for (t, s), p in zip([w for w in want if w[1] is not None], pts):\n            assert p["storey"] == s, (name, t, p)\n        kids = {n["name"]: n for n in g["nodes"]}\n        for s in {p["storey"] for p in pts}:\n            parent = kids["storey_%d" % s]\n            assert [g["nodes"][c]["name"] for c in parent["children"]] == ["storey_%d_points" % s], name\n        for p in pts:\n            seen[p["label"]] = seen.get(p["label"], 0) + 1\n    assert seen.get("SCORE", 0) >= 5 and seen.get("SAFE", 0) >= 3, seen    # the control: there is something to show\n\n\ndef test_doors_in_from_outside_wear_the_entry_colour():\n')]}
REPLACED = {}
NEW_FILES = {}
CHANGELOG = '## [0.260.0] - the scout model in the handheld\'s colours, with the score and the props worth knowing about\n\n**The factory\'s roadmap 295.** The walker, on the first frames: it "should roughly be in the style of a 1990s palm\npilot...but with a little more backlight and color (so a blend of what was and what could be that makes it more\nlegible)", and "buildings should show the \'score\' location and key props of interest".\n\n### Added\n- **The `palm` palette, the default**: a handheld\'s grey-green LCD floors, ink walls with a darker cut, and lit\n  accents for what a player hunts for -- the entry, the stairs, a ladder, a hole, a window, and now the score and the\n  props of interest, every one its own colour (`ROLES_READ`). The three palettes before it stay, for comparison.\n- **The score and the props of interest** (`POINTS_OF_INTEREST`, `points`): a beacon -- plinth, mast, a block on\n  top, 3.0 m -- at every `objective` marker, and a lit block at every `loot` and `camera_socket` marker, safe and\n  ATM. Each storey\'s are a mesh of their own, `storey_<n>_points`, a child of the storey so they ride it when a viewer\n  lifts the storeys apart, and the scene\'s `extras.points` names every one: kind, label, storey, and where it stands\n  in the model\'s frame. Across the library\'s buildings with an inside: 131 scores, 139 cameras, 131 safes, 69 ATMs,\n  13 loot. Spawns are not drawn: they are the gameplay layer\'s, and provisional.\n\n### Tests\n- `test_scout_model.py`: every objective marker is a score on its storey and every safe, ATM, loot and camera a\n  point, named in the scene, each storey\'s under it (five buildings, the control at least five scores and three\n  safes); a mesh a storey and one more on each storey with points; the score and the props of interest their own\n  colours in every palette.\n\n'
OLD_VERSION, NEW_VERSION = 'Deli Counter 0.259.0', 'Deli Counter 0.260.0'


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
