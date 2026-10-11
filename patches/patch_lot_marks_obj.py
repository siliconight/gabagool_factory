"""Lot 0.114.0: the road paint as one mesh per colour, beside the scene (roadmap 231).

Anchored edits in `lot.py` (`_mat_sub` takes `triplanar`, `_outdoor_nodes` takes `files` and lays
the paint through `_marking_meshes` from `lot_marks_obj/lot_marking_meshes.py.txt`, the scene
writer writes the OBJs beside the scene and declares them), four test adaptations (the tests that
pinned `mark_<n>_<kind>` nodes and per-marking materials now read the quads) and a new
`tests/test_marking_meshes.py`; each file pinned by hash and each anchor asserted once, nothing
written on a miss; the file's own line endings kept. Applies on Lot 0.113.0. CHANGELOG and
VERSION from `lot_marks_obj/CHANGELOG_0.114.0.md`; `--suite-pending` leaves RESULT_SUITE to
`--fill`.

    python patches/patch_lot_marks_obj.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_marks_obj.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_marks_obj.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_marks_obj"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.113.0", b"Lot 0.114.0"
CHANGELOG_HEAD = "## 0.113.0 - a lane stops at a street, and the audit counts it\n"
SHA = {"lot.py": "f2644945fe64626c",
       "tests/test_site_streets.py": "64ac4e3f71706765",
       "tests/test_street_rules.py": "54fc0e85392cbff0",
       "tests/test_site_fields.py": "47ba78352c285a36",
       "tests/test_diagonal_slabs.py": "df01d5ec35230360"}
NEW = {"tests/test_marking_meshes.py": "test_marking_meshes.py"}

# --- lot.py -------------------------------------------------------------------------------------
MAT_SIG_OLD = "def _mat_sub(name, color, skin=None, tint=None, uv_offset=None):\n"
MAT_SIG_NEW = "def _mat_sub(name, color, skin=None, tint=None, uv_offset=None, triplanar=True):\n"
TRI_OLD = (
    "        lines.append('uv1_triplanar = true')\n"
    "        lines.append('uv1_world_triplanar = true')\n"
    "        lines.append(f'uv1_scale = Vector3({s:g}, {s:g}, {s:g})')\n")
TRI_NEW = (
    "        if triplanar:\n"
    "            lines.append('uv1_triplanar = true')\n"
    "            lines.append('uv1_world_triplanar = true')\n"
    "            lines.append(f'uv1_scale = Vector3({s:g}, {s:g}, {s:g})')\n"
    "        else:\n"
    "            # the mesh carries its own UVs in the pack's tile units\n"
    "            # (`_marking_meshes`, 0.114.0): one material for every marking\n"
    "            lines.append('uv1_scale = Vector3(1, 1, 1)')\n")
SIG_OLD = (
    "def _outdoor_nodes(site_spec, preview=False, self_flooring=None, skins=None,\n"
    "                   cover_refs=None, signs=None, hung_refs=None):\n")
SIG_NEW = (
    "def _outdoor_nodes(site_spec, preview=False, self_flooring=None, skins=None,\n"
    "                   cover_refs=None, signs=None, hung_refs=None, files=None):\n")
LOOPS_OLD = (
    "    for n, m in enumerate(site_streets.markings(street_roads)):\n"
    "        along, across = m[\"size\"]\n"
    "        paint = skins.get(\"paint\")\n"
    "        offset = (paint_offset(f\"{m['road']}|{m['kind']}|{m['at'][0]:.3f}|{m['at'][1]:.3f}\")\n"
    "                  if paint else None)\n"
    "        bl, sr = _yaw_quad_node(f\"mark_{n}_{m['kind']}\", (along, across),\n"
    "                                (m[\"at\"][0], MARKING_Y, -m[\"at\"][1]),\n"
    "                                m[\"yaw\"], tuple(m[\"color\"]), skin=paint,\n"
    "                                uv_offset=offset)\n"
    "        body += bl\n"
    "        sub += sr\n"
    "\n"
    "    # THE FIELDS' BAY LINES (`site_fields`, 0.94.0): the road's paint, the\n"
    "    # road's quads, at the road's height -- a field sits at it.\n"
    "    import site_fields as _site_fields\n"
    "    for n, m in enumerate(_site_fields.markings(site_spec.get(\"fields\") or [], street_roads)):\n"
    "        along, across = m[\"size\"]\n"
    "        paint = skins.get(\"paint\")\n"
    "        offset = (paint_offset(f\"{m['field']}|{m['kind']}|{m['at'][0]:.3f}|{m['at'][1]:.3f}\")\n"
    "                  if paint else None)\n"
    "        bl, sr = _yaw_quad_node(f\"fmark_{n}_{m['kind']}\", (along, across),\n"
    "                                (m[\"at\"][0], MARKING_Y, -m[\"at\"][1]),\n"
    "                                m[\"yaw\"], tuple(m[\"color\"]), skin=paint,\n"
    "                                uv_offset=offset)\n"
    "        body += bl\n"
    "        sub += sr\n")
LOOPS_NEW = (
    "    # ONE MESH A COLOUR (0.114.0, roadmap 231): the road's paint and the\n"
    "    # fields' bay lines (`site_fields`, 0.94.0, at the road's height) as\n"
    "    # quads in an OBJ beside the scene, one MeshInstance3D and one material\n"
    "    # a colour, the wear offset in the UVs -- `_marking_meshes` says why.\n"
    "    # The texts go to `files` for the scene writer; a caller with none\n"
    "    # (the tests) gets the nodes and no file.\n"
    "    import site_fields as _site_fields\n"
    "    marks = list(site_streets.markings(street_roads))\n"
    "    marks += list(_site_fields.markings(site_spec.get(\"fields\") or [], street_roads))\n"
    "    mb, ms, mf = _marking_meshes(marks, skins)\n"
    "    body += mb\n"
    "    sub += ms\n"
    "    if files is not None:\n"
    "        files.update(mf)\n")
CALL_OLD = (
    "    outdoor_body, outdoor_sub = _outdoor_nodes(\n"
    "        site_spec, preview=preview, self_flooring=self_flooring, skins=skins,\n"
    "        cover_refs=cover_refs, signs=signs, hung_refs=hung_refs)\n")
CALL_NEW = (
    "    marks_files = {}\n"
    "    outdoor_body, outdoor_sub = _outdoor_nodes(\n"
    "        site_spec, preview=preview, self_flooring=self_flooring, skins=skins,\n"
    "        cover_refs=cover_refs, signs=signs, hung_refs=hung_refs, files=marks_files)\n"
    "    # the paint's meshes beside the scene (0.114.0): written here, declared\n"
    "    # as the Mesh ext_resources the paint nodes name, imported by the engine\n"
    "    for fname, text in sorted(marks_files.items()):\n"
    "        with open(os.path.join(os.path.dirname(os.path.abspath(out_path)), fname), \"w\",\n"
    "                  encoding=\"utf-8\", newline=\"\\n\") as mf:\n"
    "            mf.write(text)\n"
    "        res_lines.append(f'[ext_resource type=\"Mesh\" path=\"{prefix}{fname}\" id=\"{fname[:-4]}\"]')\n")

# --- the tests that pinned the old form -----------------------------------------------------------
STREETS_OLD = (
    "def test_paint_has_no_collision_and_sits_on_the_road():\n"
    "    body, sub = lot._outdoor_nodes(_probe())\n"
    "    marks = [l for l in body if l.startswith('[node name=\"mark_')]\n"
    "    assert marks and all('type=\"Node3D\"' in l for l in marks)\n"
    "    txt = \"\\n\".join(body)\n"
    "    assert 'parent=\"./mark_0_edge_line\"]' in txt\n"
    "    i = txt.index('name=\"mark_0_edge_line\"')\n"
    "    tf = txt[i:].split(\"\\n\")[1]\n"
    "    assert f\", {lot.MARKING_Y:g}, \" in tf\n"
    "    assert lot.MARKING_Y > lot.ROAD_THICK\n"
    "    # no collision shape under any marking\n"
    "    for l in body:\n"
    "        if 'type=\"CollisionShape3D\"' in l:\n"
    "            assert \"/mark_\" not in l\n")
STREETS_NEW = (
    "def test_paint_has_no_collision_and_sits_on_the_road():\n"
    "    files = {}\n"
    "    body, sub = lot._outdoor_nodes(_probe(), files=files)\n"
    "    marks = [l for l in body if l.startswith('[node name=\"site_marks_')]\n"
    "    assert marks and files and all('type=\"MeshInstance3D\"' in l for l in marks)\n"
    "    # the paint's quads lie a hair above the road, in the mesh beside the scene (0.114.0)\n"
    "    top = lot.MARKING_Y + lot.SURFACE_TIER / 2.0\n"
    "    for text in files.values():\n"
    "        ys = [float(l.split()[2]) for l in text.splitlines() if l.startswith(\"v \")]\n"
    "        assert ys and all(abs(y - top) < 1e-6 for y in ys)\n"
    "    assert lot.MARKING_Y > lot.ROAD_THICK\n"
    "    # no collision shape under any marking\n"
    "    for l in body:\n"
    "        if 'type=\"CollisionShape3D\"' in l:\n"
    "            assert \"/site_marks_\" not in l and \"/mark_\" not in l\n")
STREETS_NONE_OLD = "    assert not any(l.startswith('[node name=\"mark_') for l in body)\n"
STREETS_NONE_NEW = ("    assert not any(l.startswith('[node name=\"mark_') or l.startswith('[node name=\"site_marks_')\n"
                    "                   for l in body)\n")
RULES_OLD = (
    "    def offsets():\n"
    "        _body, sub = lot._outdoor_nodes(spec, skins=skins)\n"
    "        txt = \"\\n\".join(sub)\n"
    "        found = re.findall(r'id=\"Mat_(mark_\\d+_\\w+)\"\\]\\n(?:[^\\[]*?)uv1_offset = Vector3\\(([^)]*)\\)',\n"
    "                           txt)\n"
    "        return dict(found)\n")
RULES_NEW = (
    "    def offsets():\n"
    "        # 0.114.0: the offset lives in each quad's UVs -- what the first corner's UV is\n"
    "        # past its world position times the pack's tile scale\n"
    "        files = {}\n"
    "        lot._outdoor_nodes(spec, skins=skins, files=files)\n"
    "        s = 1.0 / 8.0\n"
    "        found = {}\n"
    "        for name, text in sorted(files.items()):\n"
    "            v = [tuple(float(x) for x in l.split()[1:]) for l in text.splitlines() if l.startswith(\"v \")]\n"
    "            vt = [tuple(float(x) for x in l.split()[1:]) for l in text.splitlines() if l.startswith(\"vt \")]\n"
    "            for i in range(0, len(v), 4):\n"
    "                found[f\"{name}:{i // 4}\"] = (round(vt[i][0] - v[i][0] * s, 4),\n"
    "                                            round(vt[i][1] - v[i][2] * s, 4))\n"
    "        return found\n")
FIELDS_OLD = (
    "    body, _sub = lot._outdoor_nodes(spec)\n"
    "    assert any(line.startswith('[node name=\"field_0\"') for line in body)\n"
    "    assert sum(1 for line in body if line.startswith('[node name=\"fmark_')) == 2 * (fields[0][\"bays\"] + 1)\n")
FIELDS_NEW = (
    "    files = {}\n"
    "    body, _sub = lot._outdoor_nodes(spec, files=files)\n"
    "    assert any(line.startswith('[node name=\"field_0\"') for line in body)\n"
    "    # the field's bay lines are quads in the paint meshes beside the road's own (0.114.0)\n"
    "    n_quads = sum(sum(1 for l in t.splitlines() if l.startswith(\"f \")) // 2 for t in files.values())\n"
    "    n_road = len(site_streets.markings(site_streets.roads(spec)))\n"
    "    assert n_quads - n_road == 2 * (fields[0][\"bays\"] + 1)\n")
DIAG_OLD = (
    "    # the paint: every marking's length runs along the road\n"
    "    marks = [n for n in drawn if n.startswith(\"mark_\")]\n"
    "    assert marks\n"
    "    for n in marks:\n"
    "        ax = drawn[n][1]\n"
    "        assert abs(ax[0] - road.along[0]) < 1e-5 and abs(ax[1] - road.along[1]) < 1e-5, (angle, n, ax)\n")
DIAG_NEW = (
    "    # the paint: every marking's length runs along the road -- read off its quads in the\n"
    "    # mesh beside the scene (0.114.0), whose first edge is the marking's `along`\n"
    "    files = {}\n"
    "    lot._outdoor_nodes(spec, files=files)\n"
    "    quads = 0\n"
    "    for text in files.values():\n"
    "        v = [tuple(float(x) for x in l.split()[1:]) for l in text.splitlines() if l.startswith(\"v \")]\n"
    "        for i in range(0, len(v), 4):\n"
    "            dx, dz = v[i + 1][0] - v[i][0], v[i + 1][2] - v[i][2]\n"
    "            ln = math.hypot(dx, dz)\n"
    "            ax = (dx / ln, -dz / ln)\n"
    "            assert abs(ax[0] - road.along[0]) < 1e-4 and abs(ax[1] - road.along[1]) < 1e-4, (angle, i, ax)\n"
    "            quads += 1\n"
    "    assert quads\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lot 0.114.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.114.0.md").decode("utf-8")
    assert entry.startswith("## 0.114.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    funcs = _src("lot_marking_meshes.py.txt").decode("utf-8")
    assert funcs.startswith("def _marking_quad(") and "def _marking_meshes(" in funcs and funcs.endswith("\n\n\n")

    lp, l_eol, lot = _read("lot.py")
    assert "_marking_meshes" not in lot, "already applied"
    lot = _once(lot, MAT_SIG_OLD, MAT_SIG_NEW, "_mat_sub's signature")
    lot = _once(lot, TRI_OLD, TRI_NEW, "the triplanar lines")
    # the new functions stand right before `_outdoor_nodes`, whose signature gains `files`
    lot = _once(lot, SIG_OLD, funcs + SIG_NEW, "_outdoor_nodes's signature")
    lot = _once(lot, LOOPS_OLD, LOOPS_NEW, "the marking loops")
    lot = _once(lot, CALL_OLD, CALL_NEW, "the scene writer's call")

    sp, s_eol, streets = _read("tests/test_site_streets.py")
    streets = _once(streets, STREETS_OLD, STREETS_NEW, "the paint test")
    streets = _once(streets, STREETS_NONE_OLD, STREETS_NONE_NEW, "the no-roads test")

    rp, r_eol, rules = _read("tests/test_street_rules.py")
    rules = _once(rules, RULES_OLD, RULES_NEW, "the offsets helper")

    fp, f_eol, fields = _read("tests/test_site_fields.py")
    fields = _once(fields, FIELDS_OLD, FIELDS_NEW, "the field's bay lines")

    dp, d_eol, diag = _read("tests/test_diagonal_slabs.py")
    diag = _once(diag, DIAG_OLD, DIAG_NEW, "the diagonal paint")

    for rel in NEW:
        assert not (LOT / rel).exists(), (rel, "already exists")
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    lp.write_bytes(lot.replace("\n", l_eol.decode()).encode("utf-8"))
    sp.write_bytes(streets.replace("\n", s_eol.decode()).encode("utf-8"))
    rp.write_bytes(rules.replace("\n", r_eol.decode()).encode("utf-8"))
    fp.write_bytes(fields.replace("\n", f_eol.decode()).encode("utf-8"))
    dp.write_bytes(diag.replace("\n", d_eol.decode()).encode("utf-8"))
    for rel, name in NEW.items():
        (LOT / rel).write_bytes(_src(name))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.113.0 -> 0.114.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
