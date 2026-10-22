"""Deli Counter 0.260.0, applied to a CLONE (<repo>): the scout model in the walker's handheld palette, and the score
and the props of interest in it (the factory's roadmap 295). Anchored; refuses on a miss; keeps line endings."""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("scout_model.py", [
    # the module docstring: the score and the props of interest
    ("""markers, as the scout view.
""",
     """markers, as the scout view.

THE SCORE AND WHAT IS WORTH KNOWING (0.260.0). The walker: "buildings should show the 'score' location and key props
of interest". Each storey carries a second mesh, ``points``, apart from its structure so a viewer can light or pulse it
on its own: a beacon -- plinth, mast, a block on top -- at every `objective` marker (the score), and at every `loot`
marker, `camera_socket` marker, safe and ATM a lit block where it stands (`POINTS_OF_INTEREST`). The scene's
``extras.points`` lists every one -- kind, label, storey, and where it stands in the model's frame -- so a viewer can
name them. Spawns are not drawn: they are the gameplay layer's, and provisional.
"""),
    ("""#: Colours as they show on screen (sRGB 0-1). The walker picks one (2026-10-22, three put to them).""",
     """#: Colours as they show on screen (sRGB 0-1). The walker's direction (2026-10-22): "roughly be in the style of a
#: 1990s palm pilot...but with a little more backlight and color" -- `palm`, the default since 0.260.0; the three
#: before it were put to them first."""),
    ("""ROLES_READ = ("glass", "door", "entry", "tread", "ladder", "hole_rim")
PALETTES = {""",
     """ROLES_READ = ("glass", "door", "entry", "tread", "ladder", "hole_rim", "score", "poi")
PALETTES = {
    # a 1990s handheld's LCD, backlit: grey-green floors, ink walls, a few lit accents for what a player hunts for
    "palm": {"slab": (0.47, 0.58, 0.45), "slab_side": (0.30, 0.38, 0.29), "wall": (0.16, 0.21, 0.16),
             "cap": (0.06, 0.09, 0.06), "glass": (0.45, 0.85, 0.95), "door": (0.30, 0.40, 0.29),
             "entry": (1.00, 0.55, 0.20), "tread": (1.00, 0.85, 0.35), "ladder": (0.55, 1.00, 0.75),
             "hole_rim": (1.00, 0.40, 0.70), "score": (1.00, 0.22, 0.22), "poi": (0.80, 0.55, 1.00),
             "background": (0.56, 0.68, 0.53)},"""),
    ("""                  "hole_rim": (1.00, 0.30, 0.65), "background": (0.03, 0.06, 0.12)},""",
     """                  "hole_rim": (1.00, 0.30, 0.65), "score": (1.00, 0.20, 0.30), "poi": (0.75, 0.55, 1.00),
                  "background": (0.03, 0.06, 0.12)},"""),
    ("""              "hole_rim": (0.55, 0.25, 0.60), "background": (0.13, 0.14, 0.16)},""",
     """              "hole_rim": (0.55, 0.25, 0.60), "score": (0.85, 0.10, 0.45), "poi": (0.20, 0.45, 0.80),
              "background": (0.13, 0.14, 0.16)},"""),
    ("""                "hole_rim": (0.20, 0.30, 0.55), "background": (0.82, 0.79, 0.70)},""",
     """                "hole_rim": (0.20, 0.30, 0.55), "score": (0.95, 0.35, 0.05), "poi": (0.45, 0.20, 0.55),
                "background": (0.82, 0.79, 0.70)},"""),
    ("""DEFAULT_PALETTE = "blueprint\"""", """DEFAULT_PALETTE = "palm\""""),
    # the points, collected and built
    ("""def model_stats(spec, palette=DEFAULT_PALETTE):""",
     """#: What a scout is shown besides the structure: the score (an `objective` marker) and the props worth knowing
#: about. Markers by type, volumes by the kind their name begins with. Label is what a viewer names it.
POINTS_OF_INTEREST = {
    ("marker", "objective"): ("score", "SCORE"),
    ("marker", "loot"): ("poi", "LOOT"),
    ("marker", "camera_socket"): ("poi", "CAMERA"),
    ("volume", "safe"): ("poi", "SAFE"),
    ("volume", "atm"): ("poi", "ATM"),
}
#: A score beacon: plinth, mast and a block on top, standing over the floor so it reads from any side.
BEACON_H = 3.0


def points(spec):
    \"\"\"Every point of interest, in spec metres: [{kind, label, storey, x, y, z (over its storey's floor), size}],
    markers first then volumes, each in spec order.\"\"\"
    sh = FP._story_height(spec)
    stories = set(FP.stories_in(spec))
    out = []
    for m in getattr(spec, "markers", []) or []:
        hit = POINTS_OF_INTEREST.get(("marker", m.type))
        s = FP._marker_story(spec, m)
        if hit and s in stories:
            out.append({"kind": hit[0], "label": hit[1], "storey": s, "x": m.x, "y": m.y,
                        "z": max(0.0, (getattr(m, "z", 0.0) or 0.0) - s * sh), "size": None})
    for v in getattr(spec, "volumes", []) or []:
        hit = POINTS_OF_INTEREST.get(("volume", str(v.name).split("_")[0]))
        if not hit or not getattr(v, "visual", True):
            continue
        base = (getattr(v, "z", 0.0) or 0.0) - v.size_z / 2
        s = next((k for k in sorted(stories) if k * sh - 0.6 <= base < (k + 1) * sh - 0.6), None)
        if s is None:
            continue
        out.append({"kind": hit[0], "label": hit[1], "storey": s, "x": v.x, "y": v.y,
                    "z": max(0.0, base - s * sh), "size": (v.size_x, v.size_y, v.size_z)})
    return out


def _point_meshes(spec, pal):
    \"\"\"{storey: _Mesh} of the points of interest on it.\"\"\"
    out = {}
    for p in points(spec):
        m = out.setdefault(p["storey"], _Mesh())
        x, y, z = p["x"], p["y"], p["z"]
        col = pal[p["kind"]]
        if p["kind"] == "score":
            m.box(x - 0.45, y - 0.45, z, x + 0.45, y + 0.45, z + 0.10, col)
            m.box(x - 0.10, y - 0.10, z + 0.10, x + 0.10, y + 0.10, z + BEACON_H - 0.7, col)
            m.box(x - 0.40, y - 0.40, z + BEACON_H - 0.7, x + 0.40, y + 0.40, z + BEACON_H, col)
        elif p["size"]:
            sx, sy, sz = p["size"]
            m.box(x - sx / 2, y - sy / 2, z, x + sx / 2, y + sy / 2, z + min(sz, 1.6), col)
        else:
            m.box(x - 0.2, y - 0.2, z, x + 0.2, y + 0.2, z + 0.4, col)
    return out


def model_stats(spec, palette=DEFAULT_PALETTE):"""),
    ("""    \"\"\"The scout model as GLB bytes: a node and a mesh a storey (``storey_<n>``, at its true elevation, with
    ``extras.storey`` and ``extras.elevation``), one material, colour as normalised bytes in ``COLOR_0``.\"\"\"""",
     """    \"\"\"The scout model as GLB bytes: a node and a mesh a storey (``storey_<n>``, at its true elevation, with
    ``extras.storey`` and ``extras.elevation``), and under it, where the storey has any, its points of interest
    (``storey_<n>_points``, a mesh of their own); one material, colour as normalised bytes in ``COLOR_0``; the
    scene's ``extras.points`` naming every point, its ``at`` in the model's frame (x, y up, z south).\"\"\""""),
    ("""    for s, m in sorted(_storeys(spec, pal).items()):
        if not m.idx:
            continue""",
     """    def mesh(name, m):
        p = add(b"".join(struct.pack("<3f", *v) for v in m.pos), 34962, 5126, "VEC3", len(m.pos),
                {"min": [min(v[i] for v in m.pos) for i in range(3)],
                 "max": [max(v[i] for v in m.pos) for i in range(3)]})
        n = add(b"".join(struct.pack("<3f", *v) for v in m.nrm), 34962, 5126, "VEC3", len(m.nrm))
        c = add(b"".join(struct.pack("<4B", *v) for v in m.col), 34962, 5121, "VEC4", len(m.col),
                {"normalized": True})
        i = add(b"".join(struct.pack("<I", v) for v in m.idx), 34963, 5125, "SCALAR", len(m.idx))
        meshes.append({"name": name, "primitives": [
            {"attributes": {"POSITION": p, "NORMAL": n, "COLOR_0": c}, "indices": i, "material": 0}]})
        return len(meshes) - 1

    pts = _point_meshes(spec, pal)
    for s, m in sorted(_storeys(spec, pal).items()):
        if not m.idx:
            continue
        if s in pts:
            nodes.append({"name": "storey_%d_points" % s, "mesh": mesh("storey_%d_points" % s, pts[s]),
                          "extras": {"storey": s, "points": True}})"""),
    ("""        p = add(b"".join(struct.pack("<3f", *v) for v in m.pos), 34962, 5126, "VEC3", len(m.pos),
                {"min": [min(v[i] for v in m.pos) for i in range(3)],
                 "max": [max(v[i] for v in m.pos) for i in range(3)]})
        n = add(b"".join(struct.pack("<3f", *v) for v in m.nrm), 34962, 5126, "VEC3", len(m.nrm))
        c = add(b"".join(struct.pack("<4B", *v) for v in m.col), 34962, 5121, "VEC4", len(m.col),
                {"normalized": True})
        i = add(b"".join(struct.pack("<I", v) for v in m.idx), 34963, 5125, "SCALAR", len(m.idx))
        meshes.append({"name": "storey_%d" % s, "primitives": [
            {"attributes": {"POSITION": p, "NORMAL": n, "COLOR_0": c}, "indices": i, "material": 0}]})
        nodes.append({"name": "storey_%d" % s, "mesh": len(meshes) - 1,
                      "translation": [0.0, round(s * sh, 6), 0.0],
                      "extras": {"storey": s, "elevation": round(s * sh, 6)}})""",
     """        node = {"name": "storey_%d" % s, "mesh": mesh("storey_%d" % s, m),
                "translation": [0.0, round(s * sh, 6), 0.0],
                "extras": {"storey": s, "elevation": round(s * sh, 6)}}
        if s in pts:
            node["children"] = [len(nodes) - 1]
        nodes.append(node)"""),
    ("""            "scene": 0, "scenes": [{"name": spec.name, "nodes": list(range(len(nodes))),
                                    "extras": {"palette": palette,
                                               "background": list(pal["background"])}}],""",
     """            "scene": 0, "scenes": [{"name": spec.name,
                                    "nodes": [k for k, n in enumerate(nodes) if not n["extras"].get("points")],
                                    "extras": {"palette": palette,
                                               "background": list(pal["background"]),
                                               "points": [{"kind": p["kind"], "label": p["label"],
                                                           "storey": p["storey"],
                                                           "at": [round(p["x"], 3), round(p["storey"] * sh + p["z"], 3),
                                                                  round(-p["y"], 3)]}
                                                          for p in points(spec)]}}],"""),
])

edit("test_scout_model.py", [
    ("""        assert [n["extras"]["storey"] for n in g["nodes"]] == stories, name
        for n in g["nodes"]:
            assert abs(n["translation"][1] - n["extras"]["storey"] * sh) < 1e-6, (name, n["name"])
        assert len(g["materials"]) == 1 and len(g["meshes"]) == len(stories), name""",
     """        floors = [n for n in g["nodes"] if not n["extras"].get("points")]
        assert [n["extras"]["storey"] for n in floors] == stories, name
        for n in floors:
            assert abs(n["translation"][1] - n["extras"]["storey"] * sh) < 1e-6, (name, n["name"])
        # a mesh a storey, and one more on each storey with points of interest (0.260.0)
        with_points = len({p["storey"] for p in g["scenes"][0]["extras"]["points"]})
        assert len(g["materials"]) == 1 and len(g["meshes"]) == len(stories) + with_points, name"""),
    ("""def test_doors_in_from_outside_wear_the_entry_colour():""",
     """def test_the_score_and_every_prop_of_interest_is_in_the_model():
    \"\"\"The walker: "buildings should show the 'score' location and key props of interest". Every objective marker
    is a score beacon on its storey, every safe, ATM, loot and camera marker a point; the scene names each one, and
    each storey's points are a node of their own under it.\"\"\"
    seen = {}
    for name in NAMES + ("bank_branch_a02", "apartment_walkup_a01"):
        spec = _load(name)
        want = [(m.type, FP._marker_story(spec, m)) for m in spec.markers
                if m.type in ("objective", "loot", "camera_socket")]
        want += [(v.name.split("_")[0], None) for v in spec.volumes
                 if v.name.split("_")[0] in ("safe", "atm") and getattr(v, "visual", True)]
        g = _gltf(SM.build_glb(spec))
        pts = g["scenes"][0]["extras"]["points"]
        assert len(pts) == len(want), (name, len(pts), len(want))
        scores = [p for p in pts if p["label"] == "SCORE"]
        assert len(scores) == sum(1 for t, _s in want if t == "objective"), name
        for (t, s), p in zip([w for w in want if w[1] is not None], pts):
            assert p["storey"] == s, (name, t, p)
        kids = {n["name"]: n for n in g["nodes"]}
        for s in {p["storey"] for p in pts}:
            parent = kids["storey_%d" % s]
            assert [g["nodes"][c]["name"] for c in parent["children"]] == ["storey_%d_points" % s], name
        for p in pts:
            seen[p["label"]] = seen.get(p["label"], 0) + 1
    assert seen.get("SCORE", 0) >= 5 and seen.get("SAFE", 0) >= 3, seen    # the control: there is something to show


def test_doors_in_from_outside_wear_the_entry_colour():"""),
])

v = R / "VERSION"
assert v.read_bytes().decode("utf-8") == "Deli Counter 0.259.0"
v.write_bytes(b"Deli Counter 0.260.0")
print("edited", R)
