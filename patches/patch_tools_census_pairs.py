"""tools/mesh_light_census: count what the engine pairs, beside what reaches.

The walker, 2026-10-08: "make the perf light census bake-aware". This is the
root tool's half; Level Factory 0.159.0 (`patch_lf_census_pairs.py`) is the
perf harness's. Godot 4.7's culler never binds a light whose cull mask misses
a mesh's layers, nor a BAKE_STATIC light to a mesh that has a lightmap
(`servers/rendering/renderer_scene_cull.cpp`, `_scene_cull`). Since Level
Factory 0.131.0 bakes most of a package's lights, the reach count -- this
tool's only count, and roadmap 54's closing number -- over-reports exactly
on the lightmapped meshes. So:

  * the payload reads every LightmapGI's own users, and counts per mesh a
    PAIRED count beside the reach count: `paired_histogram`,
    `paired_over_8`, `paired_worst`, `paired_worst_path`, `lightmap_users`,
    and `paired` on each over-8 row;
  * the report prints both;
  * `--count paired` makes `--max-per-mesh` gate on the paired count. The
    default stays `reach`, the count every earlier verdict was given in.

Anchored edits (every anchor once; refuses on a miss; nothing is written until
both files matched). New file: `tools/test_mesh_light_census_pairs.py`, from
`tools_census_pairs/`.

    python patch_tools_census_pairs.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GD = ROOT / "tools" / "mesh_light_census.gd"
PY = ROOT / "tools" / "mesh_light_census.py"
SRC = pathlib.Path(__file__).resolve().parent / "tools_census_pairs"
NEW = {ROOT / "tools" / "test_mesh_light_census_pairs.py": SRC / "test_mesh_light_census_pairs.py"}

GD_EDITS = [
    ("## directly. Spot cones are ignored on purpose: range is a sphere here, so the\n"
     "## count is an upper bound on what the engine will bind. A mesh that passes\n"
     "## this cannot fail in the renderer.\n",
     "## directly. Spot cones are ignored on purpose: range is a sphere here, so the\n"
     "## count is an upper bound on what the engine will bind. A mesh that passes\n"
     "## this cannot fail in the renderer.\n"
     "##\n"
     "## AND WHAT THE ENGINE PAIRS, beside it (2026-10-08). Godot 4.7's culler\n"
     "## (servers/rendering/renderer_scene_cull.cpp, `_scene_cull`) never binds a\n"
     "## light whose cull mask misses the mesh's layers, nor a BAKE_STATIC light to\n"
     "## a mesh that has a lightmap -- the lightmap holds that light already. Level\n"
     "## Factory has baked most of a package's lights since 0.131.0, so the reach\n"
     "## count over-reports exactly on the lightmapped meshes. `paired_*` counts\n"
     "## with both rules; a mesh has a lightmap when a LightmapGI lists it as a\n"
     "## user, which is how the engine gives it one.\n"),
    ("\t\t\t\t\t\t\t\"range\": l.omni_range, \"kind\": \"omni\",\n",
     "\t\t\t\t\t\t\t\"range\": l.omni_range, \"kind\": \"omni\",\n"
     "\t\t\t\t\t\t\t\"static\": l.light_bake_mode == Light3D.BAKE_STATIC,\n"
     "\t\t\t\t\t\t\t\"mask\": l.light_cull_mask,\n"),
    ("\t\t\t\t\t\t\t\"range\": l.spot_range, \"kind\": \"spot\",\n",
     "\t\t\t\t\t\t\t\"range\": l.spot_range, \"kind\": \"spot\",\n"
     "\t\t\t\t\t\t\t\"static\": l.light_bake_mode == Light3D.BAKE_STATIC,\n"
     "\t\t\t\t\t\t\t\"mask\": l.light_cull_mask,\n"),
    ("\t\tif (n as Light3D).is_visible_in_tree():\n"
     "\t\t\tdirectional += 1\n",
     "\t\tif (n as Light3D).is_visible_in_tree():\n"
     "\t\t\tdirectional += 1\n"
     "\t# THE MESHES THAT HAVE A LIGHTMAP: every LightmapGI's own users, resolved\n"
     "\t# relative to it, the way LightmapGI resolves them. Keyed by instance id.\n"
     "\tvar users := {}\n"
     "\tfor n in scene.find_children(\"*\", \"LightmapGI\", true, false):\n"
     "\t\tvar lm: LightmapGI = n\n"
     "\t\tif lm.light_data == null:\n"
     "\t\t\tcontinue\n"
     "\t\tfor i in range(lm.light_data.get_user_count()):\n"
     "\t\t\tvar u: Node = lm.get_node_or_null(lm.light_data.get_user_path(i))\n"
     "\t\t\tif u != null:\n"
     "\t\t\t\tusers[u.get_instance_id()] = true\n"),
    ("\tvar worst_count := 0\n"
     "\tvar worst_path := \"\"\n",
     "\tvar worst_count := 0\n"
     "\tvar worst_path := \"\"\n"
     "\tvar paired_histogram := {}   # paired count -> mesh count\n"
     "\tvar paired_over := 0\n"
     "\tvar paired_worst := 0\n"
     "\tvar paired_worst_path := \"\"\n"),
    ("\t\tvar count := 0\n"
     "\t\tfor l in lights:\n"
     "\t\t\tif _sphere_touches_aabb(l[\"pos\"], l[\"range\"], aabb):\n"
     "\t\t\t\tcount += 1\n"
     "\t\thistogram[count] = int(histogram.get(count, 0)) + 1\n",
     "\t\tvar mapped: bool = users.has(mi.get_instance_id())\n"
     "\t\tvar count := 0\n"
     "\t\tvar paired := 0\n"
     "\t\tfor l in lights:\n"
     "\t\t\tif _sphere_touches_aabb(l[\"pos\"], l[\"range\"], aabb):\n"
     "\t\t\t\tcount += 1\n"
     "\t\t\t\tif (int(l[\"mask\"]) & mi.layers) != 0 and not (mapped and bool(l[\"static\"])):\n"
     "\t\t\t\t\tpaired += 1\n"
     "\t\thistogram[count] = int(histogram.get(count, 0)) + 1\n"
     "\t\tpaired_histogram[paired] = int(paired_histogram.get(paired, 0)) + 1\n"
     "\t\tif paired > 8:\n"
     "\t\t\tpaired_over += 1\n"
     "\t\tif paired > paired_worst:\n"
     "\t\t\tpaired_worst = paired\n"
     "\t\t\tpaired_worst_path = String(scene.get_path_to(mi))\n"),
    ("\t\t\t\t\"lights\": count,\n",
     "\t\t\t\t\"lights\": count,\n"
     "\t\t\t\t\"paired\": paired,\n"),
    ("\t\t\"worst_path\": worst_path,\n",
     "\t\t\"worst_path\": worst_path,\n"
     "\t\t\"paired_histogram\": paired_histogram,\n"
     "\t\t\"paired_over_8\": paired_over,\n"
     "\t\t\"paired_worst\": paired_worst,\n"
     "\t\t\"paired_worst_path\": paired_worst_path,\n"
     "\t\t\"lightmap_users\": users.size(),\n"),
]

PY_EDITS = [
    ("WHAT THE COUNT OVERSTATES. Spot cones are ignored (range as a sphere), and a\n"
     "light behind a wall still counts if its range crosses the mesh's AABB --\n"
     "both make the count an upper bound on what the engine will bind. A mesh\n"
     "that passes at 8 here cannot drop a light in the renderer; one that fails\n"
     "here may still render clean, and the fix for that is to look, not to trust.\n",
     "WHAT THE COUNT OVERSTATES. Spot cones are ignored (range as a sphere), and a\n"
     "light behind a wall still counts if its range crosses the mesh's AABB --\n"
     "both make the count an upper bound on what the engine will bind. A mesh\n"
     "that passes at 8 here cannot drop a light in the renderer; one that fails\n"
     "here may still render clean, and the fix for that is to look, not to trust.\n"
     "\n"
     "AND WHAT THE ENGINE PAIRS (2026-10-08). Beside the reach count, a PAIRED\n"
     "count applies the culler's own two rules (Godot 4.7,\n"
     "servers/rendering/renderer_scene_cull.cpp, `_scene_cull`): no light whose\n"
     "cull mask misses the mesh's layers, and no BAKE_STATIC light on a mesh that\n"
     "has a lightmap. Level Factory has baked most of a package's lights since\n"
     "0.131.0, so on a baked package the reach count over-reports exactly on the\n"
     "lightmapped meshes. `--count paired` makes `--max-per-mesh` gate on it; the\n"
     "default stays `reach`, the count every earlier verdict was given in.\n"),
    ("    print(\"    worst          %d   %s\" % (c[\"worst\"], c[\"worst_path\"]))\n",
     "    print(\"    worst          %d   %s\" % (c[\"worst\"], c[\"worst_path\"]))\n"
     "\n"
     "    ph = c.get(\"paired_histogram\")\n"
     "    print(\"\")\n"
     "    if ph is None:\n"
     "        print(\"  paired           not in this census (a payload from before the \"\n"
     "              \"paired count)\")\n"
     "    else:\n"
     "        print(\"  paired           what the engine binds: no light masked off the mesh, \"\n"
     "              \"no baked light on a lightmapped mesh (%d lightmap user(s))\"\n"
     "              % c.get(\"lightmap_users\", 0))\n"
     "        print(\"    <=8 lights     %d\" % _bucket(ph, 0, 8))\n"
     "        print(\"    over 8         %d\" % _bucket(ph, 9))\n"
     "        print(\"    worst          %d   %s\" % (c[\"paired_worst\"], c[\"paired_worst_path\"]))\n"),
    ("            print(\"    %3d  %-14s %s\" % (row[\"lights\"], size, row[\"path\"]))\n",
     "            print(\"    %3d  (%s paired)  %-14s %s\"\n"
     "                  % (row[\"lights\"], row.get(\"paired\", \"?\"), size, row[\"path\"]))\n"),
    ("    ap.add_argument(\"--json\", action=\"store_true\",\n",
     "    ap.add_argument(\"--count\", choices=(\"reach\", \"paired\"), default=\"reach\",\n"
     "                    help=\"which count --max-per-mesh gates on (default: \"\n"
     "                         \"%(default)s). `paired` leaves out what the engine \"\n"
     "                         \"never binds: masked-off lights and baked lights on \"\n"
     "                         \"lightmapped meshes\")\n"
     "    ap.add_argument(\"--json\", action=\"store_true\",\n"),
    ("    if a.max_per_mesh is not None and \"error\" not in c:\n",
     "    if a.max_per_mesh is not None and \"error\" not in c and a.count == \"paired\":\n"
     "        if \"paired_histogram\" not in c:\n"
     "            print(\"\")\n"
     "            print(\"[mesh_light_census] NOT MEASURED: --count paired, and this \"\n"
     "                  \"payload carries no paired count.\")\n"
     "            return 1\n"
     "        c = dict(c, worst=c[\"paired_worst\"], worst_path=c[\"paired_worst_path\"],\n"
     "                 histogram=c[\"paired_histogram\"])\n"
     "    if a.max_per_mesh is not None and \"error\" not in c:\n"),
]


def _stage(path, pairs):
    d = path.read_bytes()
    assert b"\r\n" not in d, (path.name, "CRLF; this patch writes LF")
    t = d.decode("utf-8")
    for old, new in pairs:
        n = t.count(old)
        assert n == 1, (path.name, n, old[:70])
        t = t.replace(old, new)
    return t.encode("utf-8")


def main():
    for dst in NEW:
        assert not dst.exists(), ("already applied", dst.name)
    staged = {GD: _stage(GD, GD_EDITS), PY: _stage(PY, PY_EDITS)}
    for dst, src in NEW.items():
        staged[dst] = src.read_bytes()
    # Every anchor in both files matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    print("applied: mesh_light_census counts what the engine pairs beside what reaches")


if __name__ == "__main__":
    main()
