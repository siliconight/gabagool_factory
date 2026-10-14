"""Patina 0.31.0: a prop is not the building (factory roadmap 248, found attributing cold run 9303's package).

`surfaces.classify` took the building's bounds from every visual mesh in the shell GLB, and called a vertical face
an exterior wall when it stood within `_BOUNDARY_TOL` of them. Deli Counter greyboxes every `prop` slot as a visual
box named by its `slot_id`, and a stoop (Deli Counter 0.211.0), an awning (0.219.0) and a fire escape (0.220.0)
stand proud of a front. So the box was the front: the wall stopped reading as exterior, the box's face read as
exterior instead, and the anchor pass -- which reads exterior-wall faces only -- put the front's coping, base course
and curbs on the box. Measured on 9303's gs_midrise_a (the factory's `docs/findings/fire_escape/README.md`,
"Found"): its front anchors roofline 12 -> 1, ground edge 8 -> 1, wall base 4 -> 1, the one of each on the stack's
box face, 1.34 m off the wall.

The CLI loads the shell's slots.json before it classifies; `classify` now takes `props`, the mesh names that stand
for a prop, leaves them out of the bounds, and never lets their faces read as exterior wall or roof. Their faces keep
the role their normals give: forcing them to trim, as `slots._ROLE_MAP` reads a prop for tinting, would retint every
prop in the library's 9,933 prop slots, nearly all of them indoors, for nothing this defect needs. A hint still wins.

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched:
  patina/surfaces.py    the module docstring; `_visual_aabb(scene, skip)`; `classify(..., props)`
  patina/slots.py       `SlotManifest.prop_ids()`
  patina/cli.py         `classify` is handed the manifest's props
  tests/test_props_are_not_walls.py   new, from `patina_props_not_walls/test_props_are_not_walls.py.txt`
CHANGELOG and VERSION from `patina_props_not_walls/CHANGELOG_0.31.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `surfaces.py` whole; `anchors.py` (`_exterior_wall_faces`,
`_wall_segments`, `_buried`, `generate`, `_generate_zup`: it reads face roles, and its own `_visual_aabb` result is
unused); `cli.py` (the slot load at 148, `classify` at 202, the anchor options at 374); `slots.py` (`_ROLE_MAP`,
`Slot`, `SlotManifest`, `parse`, `load`); `gltf_io.load_glb` (a mesh is named by its node; `scene.slots` from the
sibling slots.json); `mesh.py` (`SurfaceRole`, `Mesh`); `tests/test_surfaces_ext.py`, `make_fixture._unit_cube`,
`test_gutter_eave_gaps.py`'s use of the sibling Deli Counter build. Every file LF.

    python patches/patch_patina_props_not_walls.py --results-pending
    (python -m pytest -q in patina; docs/findings/patina_props/replay.py)
    python patches/patch_patina_props_not_walls.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PATINA = pathlib.Path(os.environ.get("PATINA_ROOT") or HERE.parent / "patina")
SRC = HERE / "patina_props_not_walls"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_REPLAY": "result_replay.txt"}
VERSION_WAS, VERSION = b"Patina 0.30.0", b"Patina 0.31.0"
CHANGELOG_ANCHOR = "## [0.30.0] - a wall's anchors face out and stand on its face\n"
NEW_TEST = ("tests/test_props_are_not_walls.py", "test_props_are_not_walls.py.txt")
SHA = {"patina/surfaces.py": "40abfdd257aa6578",
       "patina/cli.py": "a3e014846a159b4d",
       "patina/slots.py": "03a54e8a11a38794"}

EDITS = {
    "patina/surfaces.py": [
        ("* **roof** — an up-facing face whose centroid sits at the top of the visual\n"
         "  AABB (within tolerance).\n",
         "* **roof** — an up-facing face whose centroid sits at the top of the visual\n"
         "  AABB (within tolerance).\n"
         "\n"
         "The AABB is the BUILDING's (0.31.0): a mesh the caller names as a prop --\n"
         "the CLI names a slots.json's ``prop`` slots -- is left out of it, and never\n"
         "reads as exterior wall or roof.\n"),
        ("def _visual_aabb(scene: Scene):\n"
         "    lo = np.full(3, np.inf)\n"
         "    hi = np.full(3, -np.inf)\n"
         "    any_pts = False\n"
         "    for mesh in scene.visual_meshes():\n"
         "        for prim in mesh.primitives:\n",
         "def _visual_aabb(scene: Scene, skip=frozenset()):\n"
         "    lo = np.full(3, np.inf)\n"
         "    hi = np.full(3, -np.inf)\n"
         "    any_pts = False\n"
         "    for mesh in scene.visual_meshes():\n"
         "        if mesh.name in skip:\n"
         "            continue\n"
         "        for prim in mesh.primitives:\n"),
        ("def classify(scene: Scene, up_axis: int = 2) -> None:\n"
         "    \"\"\"Fill ``prim.face_roles`` for every visual primitive in place.\n"
         "\n"
         "    ``up_axis`` (0=X, 1=Y, 2=Z) is the vertical axis: 2 for legacy Z-up shells,\n"
         "    1 for DC's Y-up glTF exports. Floor/ceiling/roof read the up axis; the other\n"
         "    two axes form the horizontal plane the exterior-wall test runs in.\n"
         "    \"\"\"\n"
         "    horiz_axes = [a for a in range(3) if a != up_axis]\n"
         "    hints = _hinted_roles(scene)\n"
         "    lo, hi = _visual_aabb(scene)\n"
         "    for mesh in scene.visual_meshes():\n"
         "        forced = hints.get(mesh.name)\n"
         "        if forced is None and any(tok in mesh.name.lower() for tok in _TRIM_TOKENS):\n"
         "            forced = SurfaceRole.TRIM\n"
         "        for prim, fn in _face_normals(mesh):\n",
         "def classify(scene: Scene, up_axis: int = 2, props=frozenset()) -> None:\n"
         "    \"\"\"Fill ``prim.face_roles`` for every visual primitive in place.\n"
         "\n"
         "    ``up_axis`` (0=X, 1=Y, 2=Z) is the vertical axis: 2 for legacy Z-up shells,\n"
         "    1 for DC's Y-up glTF exports. Floor/ceiling/roof read the up axis; the other\n"
         "    two axes form the horizontal plane the exterior-wall test runs in.\n"
         "\n"
         "    ``props`` names the meshes that stand for a prop, not the building (0.31.0,\n"
         "    factory roadmap 248): the CLI passes a slots.json's ``prop`` slots, whose\n"
         "    greybox Deli Counter names by ``slot_id``. Such a mesh is left out of the\n"
         "    AABB and never reads as exterior wall or roof; its faces keep the role\n"
         "    their normals give, and a hint still wins. A stoop, an awning or a fire\n"
         "    escape stands proud of a front, and before this its box WAS the front:\n"
         "    on cold run 9303's gs_midrise_a it moved the bound 1.34 m out, the wall\n"
         "    stopped reading as exterior, and the anchor pass put the front's coping,\n"
         "    base course and curbs on the stack. Leaving a prop out of the AABB alone\n"
         "    would not do: the exterior test accepts a face standing BEYOND the bound.\n"
         "    \"\"\"\n"
         "    horiz_axes = [a for a in range(3) if a != up_axis]\n"
         "    hints = _hinted_roles(scene)\n"
         "    lo, hi = _visual_aabb(scene, props)\n"
         "    for mesh in scene.visual_meshes():\n"
         "        forced = hints.get(mesh.name)\n"
         "        if forced is None and any(tok in mesh.name.lower() for tok in _TRIM_TOKENS):\n"
         "            forced = SurfaceRole.TRIM\n"
         "        prop = mesh.name in props\n"
         "        for prim, fn in _face_normals(mesh):\n"),
        ("            # roof: up-facing at the top of the visual AABB.\n"
         "            roof = up & (centroids[:, up_axis] >= hi[up_axis] - _BOUNDARY_TOL)\n"
         "            roles[roof] = SurfaceRole.ROOF\n"
         "\n"
         "            # exterior wall: vertical face on the AABB boundary along the\n"
         "            # normal's dominant horizontal axis, normal pointing outward.\n"
         "            if vertical.any():\n",
         "            # roof: up-facing at the top of the visual AABB; never a prop's.\n"
         "            roof = up & (centroids[:, up_axis] >= hi[up_axis] - _BOUNDARY_TOL)\n"
         "            if not prop:\n"
         "                roles[roof] = SurfaceRole.ROOF\n"
         "\n"
         "            # exterior wall: vertical face on the AABB boundary along the\n"
         "            # normal's dominant horizontal axis, normal pointing outward;\n"
         "            # never a prop's.\n"
         "            if vertical.any() and not prop:\n"),
    ],
    "patina/slots.py": [
        ("    def role_counts(self) -> dict[str, int]:\n"
         "        out: dict[str, int] = {}\n"
         "        for s in self.slots:\n"
         "            out[s.role] = out.get(s.role, 0) + 1\n"
         "        return out\n",
         "    def role_counts(self) -> dict[str, int]:\n"
         "        out: dict[str, int] = {}\n"
         "        for s in self.slots:\n"
         "            out[s.role] = out.get(s.role, 0) + 1\n"
         "        return out\n"
         "\n"
         "    def prop_ids(self) -> frozenset:\n"
         "        \"\"\"The ids of the slots that stand for a prop, not the building (0.31.0,\n"
         "        factory roadmap 248). Deli Counter names each slot's greybox node by its\n"
         "        id, so these are the props' mesh names too: :func:`surfaces.classify`\n"
         "        leaves them out of the building's bounds.\"\"\"\n"
         "        return frozenset(s.slot_id for s in self.slots if s.role == \"prop\")\n"),
    ],
    "patina/cli.py": [
        ("    surfaces.classify(scene, up_axis)\n",
         "    # A PROP IS NOT THE BUILDING (0.31.0, factory roadmap 248): a stoop, an\n"
         "    # awning or a fire escape greyboxed proud of a wall moved the bounds the\n"
         "    # classifier reads, and the wall stopped reading as exterior.\n"
         "    surfaces.classify(scene, up_axis,\n"
         "                      props=slot_manifest.prop_ids() if slot_manifest is not None\n"
         "                      else frozenset())\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (PATINA / "VERSION").read_bytes().strip() == VERSION, (PATINA / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(PATINA / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.31.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Patina 0.31.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (PATINA / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.31.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.31.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_dst = PATINA / NEW_TEST[0]
    assert not test_dst.exists(), (test_dst, "already exists")
    test_src = (SRC / NEW_TEST[1]).read_bytes().replace(b"\r\n", b"\n")
    writes = {}
    for rel, pairs in EDITS.items():
        p = PATINA / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = PATINA / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.count(CHANGELOG_ANCHOR) == 1, "the changelog's newest entry is not 0.30.0's"
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    test_dst.write_bytes(test_src)
    cl.write_bytes(cl_text.replace(CHANGELOG_ANCHOR, entry.rstrip("\n") + "\n\n" + CHANGELOG_ANCHOR)
                   .encode("utf-8").replace(b"\n", cl_eol))
    (PATINA / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Patina 0.30.0 -> 0.31.0")


if __name__ == "__main__":
    main()
