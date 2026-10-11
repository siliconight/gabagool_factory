"""Zoo 1.101.0: a roof's props keep off its hatches and landings, stand in the box they occupy, and
draw as one roof (roadmap 181).

Anchored edits: `zoo_keeper/core/roofprops.py` (`roof_slots` reads the slot's `fit.voids` and
`fit.keep_out`; `scatter` draws the yaw first and clamps and overlap-tests the footprint's extents
at it, places nothing on a hole's ring or a landing, and plans a water tank only on a roof
`TANK_MIN_ROOF_M` or more up; `_extents`, `forbidden_rects`), `zoo_keeper/bpylayer/build.py`
(`build_roof_props` bakes each prop's placement into its vertices and exports merged by material,
the merge's stats in the index), `tools/zoo_cli.py` (`--no-merge-parts` reaches the roof props;
the merge printed), and `tests/test_roofprops.py` replaced by `zoo_roof_props/test_roofprops.py.txt`
(eight of its thirteen tests fail on 1.100.0, run against it first). Each file pinned by hash and
each anchor asserted once, nothing written on a miss; the files' own line endings kept. Applies on
Zoo 1.100.0. CHANGELOG and VERSION from `zoo_roof_props/CHANGELOG_1.101.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

    python patches/patch_zoo_roof_props.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_roof_props.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_roof_props.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_roof_props"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BPY": "result_bpy.txt"}
VERSION_WAS, VERSION = b"1.100.0", b"1.101.0"
CHANGELOG_HEAD = "## [1.100.0] - a fixture's same-material parts are one mesh, inside it and never across two\n"
ROOF = "zoo_keeper/core/roofprops.py"
BUILD = "zoo_keeper/bpylayer/build.py"
CLI = "tools/zoo_cli.py"
TEST = "tests/test_roofprops.py"
SHA = {ROOF: "f6d0212954ec9aed", BUILD: "79c2b5b4f0ea68b3", CLI: "9fa113133ee49471",
       TEST: "039cfd5b7198a508"}

# --- roofprops.py ---------------------------------------------------------------------------
R_DOC_OLD = ("the manifest's own spec / Blender Z-up space, sitting on the roof slot's top\n"
             "surface \u2014 the builder only has to lift each prop by half its own height.\n"
             "\"\"\"\n")
R_DOC_NEW = ("the manifest's own spec / Blender Z-up space, sitting on the roof slot's top\n"
             "surface \u2014 the builder only has to lift each prop by half its own height.\n"
             "\n"
             "WHAT A PROP KEEPS OFF (1.101.0, roadmap 181). The roof slot carries the\n"
             "slab's holes (``fit.voids``: stair heads and ladder hatches, in the plate's\n"
             "own centred coords) and the landings Deli Counter 0.209.0 writes for the\n"
             "ladders that top out on it (``fit.keep_out``, the same frame). A prop never\n"
             "stands on a hole, and keeps ``VOID_CLEAR`` from its edge -- the stride a\n"
             "body takes climbing out -- nor on a landing. A YAWED PROP IS TESTED AS THE\n"
             "BOX IT OCCUPIES: the yaw is drawn before the position, and the footprint's\n"
             "extents at that yaw decide both the edge clamp and the overlap. 0.25 read\n"
             "the unrotated box for both; the 0.35 m clearance happened to absorb the\n"
             "overlap for every current species, but a 90-degree HVAC (1.8 x 1.1) at a\n"
             "long edge reached 0.25 m from the footprint's edge, inside a 0.35 m\n"
             "parapet, and a 1.6 m tank yawed 149 degrees stood 9 cm past the margin. A\n"
             "WATER TANK NEEDS HEIGHT: a gravity tank serves floors below it and a\n"
             "one-storey roof is on street pressure, so one is planned only on a roof\n"
             "``TANK_MIN_ROOF_M`` or more above the plan.\n"
             "\"\"\"\n")
R_DEF_OLD = "\n\n\ndef roof_slots(manifest: dict) -> list[dict]:\n"
R_DEF_NEW = ("\n\n\n"
             "#: A hole's edge is where a body climbs out; this is the stride it takes\n"
             "#: (1.101.0), grown around every void of the roof slot.\n"
             "VOID_CLEAR = 1.0\n"
             "#: A gravity tank serves floors below it; a roof whose top is lower than this\n"
             "#: is on street pressure and plans none (1.101.0). Delco's library stands 3.2\n"
             "#: to 13 m above its plan; two roofs of 133 reach 12.\n"
             "TANK_MIN_ROOF_M = 12.0\n"
             "\n\n"
             "def roof_slots(manifest: dict) -> list[dict]:\n")
R_SLOT_OLD = ("            \"dims\": [float(v) for v in dims],\n"
              "            \"pivot\": fit.get(\"pivot\", \"center\"),\n"
              "        })\n"
              "    return out\n")
R_SLOT_NEW = ("            \"dims\": [float(v) for v in dims],\n"
              "            \"pivot\": fit.get(\"pivot\", \"center\"),\n"
              "            # the plate's holes and its landings, in its own centred coords\n"
              "            \"voids\": [dict(v) for v in (fit.get(\"voids\") or ())],\n"
              "            \"keep_out\": [dict(k) for k in (fit.get(\"keep_out\") or ())],\n"
              "        })\n"
              "    return out\n")
R_FOOT_OLD = ("def _footprint(species: str) -> tuple[float, float, float]:\n"
              "    \"\"\"(width, depth, height) defaults from the species genome.\"\"\"\n"
              "    g = genome_mod.load_species(species)\n"
              "    d = g[\"dimensions\"]\n"
              "    return (d[\"width\"][\"default\"], d[\"depth\"][\"default\"],\n"
              "            d[\"height\"][\"default\"])\n")
R_FOOT_NEW = (R_FOOT_OLD +
              "\n\n"
              "def _extents(fw: float, fd: float, yaw_deg: float) -> tuple[float, float]:\n"
              "    \"\"\"Half-extents along the slot's x and y of a ``fw x fd`` footprint yawed\n"
              "    by ``yaw_deg`` -- the box the prop actually occupies (1.101.0).\"\"\"\n"
              "    c = abs(math.cos(math.radians(yaw_deg)))\n"
              "    s = abs(math.sin(math.radians(yaw_deg)))\n"
              "    return (fw / 2.0 * c + fd / 2.0 * s, fw / 2.0 * s + fd / 2.0 * c)\n"
              "\n\n"
              "def forbidden_rects(slot: dict, clear: float = VOID_CLEAR) -> list[tuple]:\n"
              "    \"\"\"Where no prop may stand on ``slot``, as (x0, y0, x1, y1) in its own\n"
              "    centred coords: every void grown by ``clear``, every keep_out as given.\"\"\"\n"
              "    out = []\n"
              "    for v in slot.get(\"voids\", ()):\n"
              "        out.append((float(v[\"x0\"]) - clear, float(v[\"y0\"]) - clear,\n"
              "                    float(v[\"x1\"]) + clear, float(v[\"y1\"]) + clear))\n"
              "    for k in slot.get(\"keep_out\", ()):\n"
              "        out.append((float(k[\"x0\"]), float(k[\"y0\"]),\n"
              "                    float(k[\"x1\"]), float(k[\"y1\"])))\n"
              "    return out\n"
              "\n\n"
              "def _overlaps(box, rects) -> bool:\n"
              "    return any(not (box[2] < r[0] or box[0] > r[2]\n"
              "                    or box[3] < r[1] or box[1] > r[3]) for r in rects)\n")
R_SDOC_OLD = ("    Each placement: species, slot_id, ``pos`` on the roof's top surface\n"
              "    (spec space), ``rot_z`` degrees, ``footprint`` [w, d], ``seed_offset``.\n"
              "    \"\"\"\n")
R_SDOC_NEW = ("    Each placement: species, slot_id, ``pos`` on the roof's top surface\n"
              "    (spec space), ``rot_z`` degrees, ``footprint`` [w, d], ``local`` [lx, ly]\n"
              "    and ``extents`` [ex, ey] -- the box it occupies in the slot's own centred\n"
              "    coords (1.101.0) -- and ``seed_offset``. ``forbidden`` counts the rects\n"
              "    each roof kept its props off.\n"
              "    \"\"\"\n")
R_INIT_OLD = ("    placements: list[dict] = []\n"
              "    counts: dict[str, int] = {}\n")
R_INIT_NEW = ("    placements: list[dict] = []\n"
              "    counts: dict[str, int] = {}\n"
              "    forbidden_by_slot: dict[str, int] = {}\n")
R_LOOP_OLD = (
    "        taken: list[tuple[float, float, float, float]] = []  # local AABBs\n"
    "\n"
    "        for name, min_area, base, per_m2, cap, bias in _RULES:\n"
    "            if name not in allowed or area < min_area:\n"
    "                continue\n"
    "            want = min(cap, int(round((base + area * per_m2) * density)))\n"
    "            fw, fd, fh = _footprint(name)\n"
    "            half_w = w / 2.0 - margin - fw / 2.0\n"
    "            half_d = d / 2.0 - margin - fd / 2.0\n"
    "            if want < 1 or half_w <= 0 or half_d <= 0:\n"
    "                continue\n"
    "            rng = seeding.RNGStreams(seeding.root_key(\n"
    "                building, name, seed, slot[\"slot_id\"])).stream(\"scatter\")\n"
    "            for k in range(want):\n"
    "                placed = False\n"
    "                for _ in range(_ATTEMPTS):\n"
    "                    if bias == _EDGE:\n"
    "                        lx = rng.choice([-1.0, 1.0]) * rng.uniform(\n"
    "                            half_w * 0.6, half_w)\n"
    "                        ly = rng.uniform(-half_d, half_d)\n"
    "                    elif bias == _CENTER:\n"
    "                        lx = rng.uniform(-half_w * 0.5, half_w * 0.5)\n"
    "                        ly = rng.uniform(-half_d * 0.5, half_d * 0.5)\n"
    "                    else:\n"
    "                        lx = rng.uniform(-half_w, half_w)\n"
    "                        ly = rng.uniform(-half_d, half_d)\n"
    "                    box = (lx - fw / 2 - _CLEARANCE, ly - fd / 2 - _CLEARANCE,\n"
    "                           lx + fw / 2 + _CLEARANCE, ly + fd / 2 + _CLEARANCE)\n"
    "                    if any(not (box[2] < t[0] or box[0] > t[2]\n"
    "                                or box[3] < t[1] or box[1] > t[3])\n"
    "                           for t in taken):\n"
    "                        continue\n"
    "                    taken.append(box)\n"
    "                    px = slot[\"translation\"][0] + lx * cos_r - ly * sin_r\n"
    "                    py = slot[\"translation\"][1] + lx * sin_r + ly * cos_r\n"
    "                    rot_z = (slot[\"rot_y\"] +\n"
    "                             (rng.choice([0.0, 90.0]) if name in\n"
    "                              (\"hvac_unit\", \"skylight\")\n"
    "                              else rng.uniform(0.0, 360.0)))\n"
    "                    placements.append({\n"
    "                        \"species\": name,\n"
    "                        \"slot_id\": slot[\"slot_id\"],\n"
    "                        \"pos\": [round(px, 3), round(py, 3), round(tz_top, 3)],\n"
    "                        \"rot_z\": round(rot_z % 360.0, 1),\n"
    "                        \"footprint\": [fw, fd],\n"
    "                        \"seed_offset\": rng.randrange(1_000_000),\n"
    "                    })\n"
    "                    counts[name] = counts.get(name, 0) + 1\n"
    "                    placed = True\n"
    "                    break\n"
    "                if not placed:\n"
    "                    break   # roof is full for this species\n")
R_LOOP_NEW = (
    "        taken: list[tuple[float, float, float, float]] = []  # local AABBs\n"
    "        # the holes (grown by the stride out of them) and the landings\n"
    "        forbidden = forbidden_rects(slot)\n"
    "        forbidden_by_slot[slot[\"slot_id\"]] = len(forbidden)\n"
    "\n"
    "        for name, min_area, base, per_m2, cap, bias in _RULES:\n"
    "            if name not in allowed or area < min_area:\n"
    "                continue\n"
    "            if name == \"water_tank\" and tz_top < TANK_MIN_ROOF_M:\n"
    "                continue   # a low roof is on street pressure\n"
    "            want = min(cap, int(round((base + area * per_m2) * density)))\n"
    "            fw, fd, fh = _footprint(name)\n"
    "            if want < 1:\n"
    "                continue\n"
    "            rng = seeding.RNGStreams(seeding.root_key(\n"
    "                building, name, seed, slot[\"slot_id\"])).stream(\"scatter\")\n"
    "            for k in range(want):\n"
    "                placed = False\n"
    "                for _ in range(_ATTEMPTS):\n"
    "                    # THE YAW FIRST (1.101.0), so the box it is tested in is\n"
    "                    # the box it occupies: the clamp and the overlap read the\n"
    "                    # footprint's extents at this yaw, not the unrotated\n"
    "                    # fw x fd. Units and skylights sit square to the roof.\n"
    "                    yaw = (rng.choice([0.0, 90.0]) if name in\n"
    "                           (\"hvac_unit\", \"skylight\")\n"
    "                           else rng.uniform(0.0, 360.0))\n"
    "                    ex, ey = _extents(fw, fd, yaw)\n"
    "                    half_w = w / 2.0 - margin - ex\n"
    "                    half_d = d / 2.0 - margin - ey\n"
    "                    if half_w <= 0 or half_d <= 0:\n"
    "                        continue   # does not fit at this yaw\n"
    "                    if bias == _EDGE:\n"
    "                        lx = rng.choice([-1.0, 1.0]) * rng.uniform(\n"
    "                            half_w * 0.6, half_w)\n"
    "                        ly = rng.uniform(-half_d, half_d)\n"
    "                    elif bias == _CENTER:\n"
    "                        lx = rng.uniform(-half_w * 0.5, half_w * 0.5)\n"
    "                        ly = rng.uniform(-half_d * 0.5, half_d * 0.5)\n"
    "                    else:\n"
    "                        lx = rng.uniform(-half_w, half_w)\n"
    "                        ly = rng.uniform(-half_d, half_d)\n"
    "                    box = (lx - ex - _CLEARANCE, ly - ey - _CLEARANCE,\n"
    "                           lx + ex + _CLEARANCE, ly + ey + _CLEARANCE)\n"
    "                    if _overlaps(box, taken):\n"
    "                        continue\n"
    "                    # a hole or a landing: the clearance there is the ring's\n"
    "                    if _overlaps((lx - ex, ly - ey, lx + ex, ly + ey), forbidden):\n"
    "                        continue\n"
    "                    taken.append(box)\n"
    "                    px = slot[\"translation\"][0] + lx * cos_r - ly * sin_r\n"
    "                    py = slot[\"translation\"][1] + lx * sin_r + ly * cos_r\n"
    "                    rot_z = slot[\"rot_y\"] + yaw\n"
    "                    placements.append({\n"
    "                        \"species\": name,\n"
    "                        \"slot_id\": slot[\"slot_id\"],\n"
    "                        \"pos\": [round(px, 3), round(py, 3), round(tz_top, 3)],\n"
    "                        \"rot_z\": round(rot_z % 360.0, 1),\n"
    "                        \"footprint\": [fw, fd],\n"
    "                        # the box it occupies, in the slot's own centred coords\n"
    "                        \"local\": [round(lx, 3), round(ly, 3)],\n"
    "                        \"extents\": [round(ex, 3), round(ey, 3)],\n"
    "                        \"seed_offset\": rng.randrange(1_000_000),\n"
    "                    })\n"
    "                    counts[name] = counts.get(name, 0) + 1\n"
    "                    placed = True\n"
    "                    break\n"
    "                if not placed:\n"
    "                    break   # roof is full for this species\n")
R_RET_OLD = ("    return {\"building_id\": building, \"seed\": seed,\n"
             "            \"space\": manifest.get(\"space\", \"\"),\n"
             "            \"placements\": placements, \"counts\": dict(sorted(counts.items()))}\n")
R_RET_NEW = ("    return {\"building_id\": building, \"seed\": seed,\n"
             "            \"space\": manifest.get(\"space\", \"\"),\n"
             "            \"placements\": placements, \"counts\": dict(sorted(counts.items())),\n"
             "            # how many rects each roof kept its props off (1.101.0)\n"
             "            \"forbidden\": forbidden_by_slot}\n")

# --- build.py -------------------------------------------------------------------------------
B_PLACE_OLD = ("        m = trans @ rot\n"
               "        for obj in new_objs:\n"
               "            obj.matrix_world = m @ obj.matrix_world\n"
               "        built += 1\n")
B_PLACE_NEW = ("        m = trans @ rot\n"
               "        for obj in new_objs:\n"
               "            # BUILT IN PLACE (1.101.0), as the dressing's covers are since\n"
               "            # 1.68.0: the placement goes into the vertices and the object\n"
               "            # stays at identity, so the merge below can take it -- it reads\n"
               "            # raw coordinates and leaves an object carrying a transform as\n"
               "            # it is (`merge._identity`). A collider proxy moves the same way.\n"
               "            if obj.type != \"MESH\":\n"
               "                obj.matrix_world = m @ obj.matrix_world\n"
               "                continue\n"
               "            if obj.data.users != 1:\n"
               "                obj.data = obj.data.copy()\n"
               "            obj.data.transform(m @ obj.matrix_world)\n"
               "            obj.matrix_world = mathutils.Matrix.Identity(4)\n"
               "        built += 1\n")
B_EXPORT_OLD = ("    files = {\"glb\": f\"{building_id}_roofprops.glb\"}\n"
                "    # A whole roof's props, each placed at its own anchor: a layer, not a\n"
                "    # module. See the note in `build_dressing`.\n"
                "    export.export_glb(base + \".glb\", coll, merge_parts=False,\n"
                "                      weighted_normals=opts[\"weighted_normals\"])\n")
B_EXPORT_NEW = ("    files = {\"glb\": f\"{building_id}_roofprops.glb\"}\n"
                "    # MERGED ACROSS THE ROOF (1.101.0, roadmap 181). Until this version the\n"
                "    # props were exported unmerged as \"a layer, not a module\", every part\n"
                "    # its own draw: 8 to 18 props a roof over the library, each of three to\n"
                "    # five parts. The unit a merge keeps is the chunk that enters and leaves\n"
                "    # view as one thing -- the dressing's is a side, a fixture's its\n"
                "    # placement -- and a roof's props stand within one footprint and are\n"
                "    # seen together or not at all, so the roof is the unit. With the\n"
                "    # placements baked into the vertices above, `pack_by_material`'s module\n"
                "    # rule applies (every part at identity), and it groups by part FAMILY\n"
                "    # and material: every `Hvac_*` part on the roof in `M_Hvac_<material>`\n"
                "    # becomes one mesh, every `VentStack_*` another -- about one mesh a\n"
                "    # species a roof, since each recipe paints one material. `merge_parts`\n"
                "    # False is the one-build control, as everywhere.\n"
                "    merge_stats = export.export_glb(base + \".glb\", coll,\n"
                "                                    merge_parts=opts[\"merge_parts\"],\n"
                "                                    weighted_normals=opts[\"weighted_normals\"])\n")
B_INDEX_OLD = ("    index = {\"tool_version\": TOOL_VERSION, \"building_id\": building_id,\n"
               "             \"theme\": theme, \"seed\": seed, \"space\": plan[\"space\"],\n"
               "             \"counts\": plan[\"counts\"], \"props_built\": built,\n"
               "             \"placements\": plan[\"placements\"], \"files\": files}\n"
               "    index_file = base + \".built.json\"\n")
B_INDEX_NEW = ("    index = {\"tool_version\": TOOL_VERSION, \"building_id\": building_id,\n"
               "             \"theme\": theme, \"seed\": seed, \"space\": plan[\"space\"],\n"
               "             \"counts\": plan[\"counts\"], \"props_built\": built,\n"
               "             \"placements\": plan[\"placements\"], \"files\": files,\n"
               "             # the rects each roof kept its props off (1.101.0)\n"
               "             \"forbidden\": plan.get(\"forbidden\", {})}\n"
               "    if merge_stats is not None:\n"
               "        index[\"merge\"] = merge_stats\n"
               "    index_file = base + \".built.json\"\n")
B_RET_OLD = ("    return {\"building_id\": building_id, \"theme\": theme, \"counts\": plan[\"counts\"],\n"
             "            \"props_built\": built, \"out_dir\": out_dir, \"files\": files,\n"
             "            \"index_file\": index_file}\n")
B_RET_NEW = ("    return {\"building_id\": building_id, \"theme\": theme, \"counts\": plan[\"counts\"],\n"
             "            \"props_built\": built, \"out_dir\": out_dir, \"files\": files,\n"
             "            \"index_file\": index_file, \"merge\": merge_stats}\n")

# --- zoo_cli.py -----------------------------------------------------------------------------
C_OPT_OLD = ("        options={\"save_blend\": not args.no_blend, \"clear_scene\": True,\n"
             "                 \"seed\": args.seed, \"density\": args.density})\n")
C_OPT_NEW = ("        options={\"save_blend\": not args.no_blend, \"clear_scene\": True,\n"
             "                 \"seed\": args.seed, \"density\": args.density,\n"
             "                 # the merge's one-build control, as on every other route\n"
             "                 \"merge_parts\": not args.no_merge_parts})\n")
C_PRINT_OLD = ("    print(f\"[zoo]   {res['props_built']} props ({summary})\")\n"
               "    print(f\"[zoo]   glb: {res['files']['glb']}   index: {res['index_file']}\")\n")
C_PRINT_NEW = ("    print(f\"[zoo]   {res['props_built']} props ({summary})\")\n"
               "    if res.get(\"merge\"):\n"
               "        m = res[\"merge\"]\n"
               "        print(f\"[zoo]   merged: {m.get('parts_in')} parts -> \"\n"
               "              f\"{m.get('meshes_out')} meshes, {m.get('triangles')} triangles\")\n"
               "    print(f\"[zoo]   glb: {res['files']['glb']}   index: {res['index_file']}\")\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.101.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.101.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.101.0.md")
    assert entry.startswith("## [1.101.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_roofprops.py.txt")
    assert "test_a_tank_needs_a_tall_roof" in test_text

    rp, r_eol, roof = _read(ROOF)
    assert "TANK_MIN_ROOF_M" not in roof, "already applied"
    roof = _once(roof, R_DOC_OLD, R_DOC_NEW, "the module docstring")
    roof = _once(roof, R_DEF_OLD, R_DEF_NEW, "the constants before roof_slots")
    roof = _once(roof, R_SLOT_OLD, R_SLOT_NEW, "roof_slots' dict")
    roof = _once(roof, R_FOOT_OLD, R_FOOT_NEW, "the helpers after _footprint")
    roof = _once(roof, R_SDOC_OLD, R_SDOC_NEW, "scatter's docstring")
    roof = _once(roof, R_INIT_OLD, R_INIT_NEW, "scatter's accumulators")
    roof = _once(roof, R_LOOP_OLD, R_LOOP_NEW, "scatter's loop")
    roof = _once(roof, R_RET_OLD, R_RET_NEW, "scatter's return")

    bp, b_eol, bld = _read(BUILD)
    bld = _once(bld, B_PLACE_OLD, B_PLACE_NEW, "the placement loop")
    bld = _once(bld, B_EXPORT_OLD, B_EXPORT_NEW, "the roof props export")
    bld = _once(bld, B_INDEX_OLD, B_INDEX_NEW, "the index")
    bld = _once(bld, B_RET_OLD, B_RET_NEW, "the return")

    cp, c_eol, cli = _read(CLI)
    cli = _once(cli, C_OPT_OLD, C_OPT_NEW, "the roof props options")
    cli = _once(cli, C_PRINT_OLD, C_PRINT_NEW, "the roof props summary")

    tp, t_eol, _tests = _read(TEST)

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(rp, r_eol, roof)
    _write(bp, b_eol, bld)
    _write(cp, c_eol, cli)
    _write(tp, t_eol, test_text)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.100.0 -> 1.101.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
