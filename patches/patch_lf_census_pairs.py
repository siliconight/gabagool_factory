"""Level Factory 0.159.0: the light census counts what the renderer pairs,
beside what reaches. The walker, 2026-10-08: "make the perf light census
bake-aware".

Anchored edits (every anchor once; refuses on a miss; nothing is written until
every anchor in every file matched):
- `tools/perf_stations.gd`:
  - `_surface_dist` and `_reach` become static, so the census can be called
    from a test's own scene;
  - `_light_census` becomes static, keeps its reach count in the top-level
    fields, and adds `paired`: the lights the renderer pairs (`_pairs`), with
    the lightmap users read off every LightmapGI (`_lightmap_users`);
  - the harness's last line prints both counts.
- `tools/perf_stations_run.py`: prints both counts, and says when a report
  carries no paired count.
New file from `lf_census_pairs/`: `tests/unit/test_perf_census_pairs.py`.
CHANGELOG and VERSION from `lf_census_pairs/CHANGELOG_0.159.0.md`.

    python patch_lf_census_pairs.py
    LF_ROOT=<copy> python patch_lf_census_pairs.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_census_pairs"
CHANGELOG_HEAD = ("## [0.158.0] - The package names the score and its buildings, and only "
                  "buildings that are there\n")

HEADER_OLD = (
    "## Cold run 9088: 34 of 4,625 meshes over the cap of 8, worst a 47 m roof\n"
    "## reached by 47 lights.\n")
HEADER_NEW = (
    "## Cold run 9088: 34 of 4,625 meshes over the cap of 8, worst a 47 m roof\n"
    "## reached by 47 lights. Two counts since 0.159.0, BY REACH and PAIRED --\n"
    "## `_light_census` says why the second is the one the cap is spent on.\n")

CENSUS_OLD = (
    "func _light_census(nodes: Array, cap: int) -> Dictionary:\n"
    "\tvar lights: Array = []\n"
    "\tvar meshes: Array = []\n"
    "\tfor n in nodes:\n"
    "\t\tvar l: Light3D = n as Light3D\n"
    "\t\tif l != null:\n"
    "\t\t\tif not (l is DirectionalLight3D):\n"
    "\t\t\t\tlights.append(l)\n"
    "\t\t\tcontinue\n"
    "\t\tvar mi: MeshInstance3D = n as MeshInstance3D\n"
    "\t\tif mi != null and mi.visible and mi.mesh != null:\n"
    "\t\t\tmeshes.append(mi)\n"
    "\tvar over: int = 0\n"
    "\tvar worst: int = 0\n"
    "\tvar worst_name: String = \"-\"\n"
    "\t# WHICH MESHES, not only how many. Cold run 9125 moved one light and the\n"
    "\t# count went 43 -> 44, and nothing could say which mesh had crossed: the\n"
    "\t# report kept the count and the single worst name, and names repeat\n"
    "\t# (`Prop_Panel`). Every mesh over the cap by its node PATH, worst first,\n"
    "\t# at most OVER_LIST_MAX, and a flag that says when the list was cut.\n"
    "\tvar over_list: Array = []\n"
    "\tfor m in meshes:\n"
    "\t\tvar mi2: MeshInstance3D = m as MeshInstance3D\n"
    "\t\tvar n_reach: int = 0\n"
    "\t\tfor o in lights:\n"
    "\t\t\tvar ol: Light3D = o as Light3D\n"
    "\t\t\tif _surface_dist(mi2, ol.global_position) <= _reach(ol):\n"
    "\t\t\t\tn_reach += 1\n"
    "\t\tif n_reach > cap:\n"
    "\t\t\tover += 1\n"
    "\t\t\tover_list.append({\"mesh\": String(mi2.get_path()), \"lights\": n_reach})\n"
    "\t\tif n_reach > worst:\n"
    "\t\t\tworst = n_reach\n"
    "\t\t\tworst_name = String(mi2.name)\n"
    "\tover_list.sort_custom(func(a, b): return int(a[\"lights\"]) > int(b[\"lights\"]) "
    "\t\tor (int(a[\"lights\"]) == int(b[\"lights\"]) and String(a[\"mesh\"]) < String(b[\"mesh\"])))\n"
    "\tvar truncated: bool = over_list.size() > OVER_LIST_MAX\n"
    "\tif truncated:\n"
    "\t\tover_list = over_list.slice(0, OVER_LIST_MAX)\n"
    "\treturn {\"cap\": cap, \"lights\": lights.size(), \"meshes\": meshes.size(),\n"
    "\t\t\"over_cap\": over, \"worst\": worst, \"worst_mesh\": worst_name,\n"
    "\t\t\"over_list\": over_list, \"over_list_truncated\": truncated}\n")
CENSUS_NEW = (
    "## THE MESHES THAT HAVE A LIGHTMAP (0.159.0): every LightmapGI's own users,\n"
    "## resolved the way LightmapGI resolves them, relative to itself. A mesh gets\n"
    "## a lightmap in the renderer only by being one -- `gi_mode` static on a mesh\n"
    "## the bake skipped is not -- so this list, not a mesh's flags, is what the\n"
    "## pairing rule reads. Keyed by instance id.\n"
    "static func _lightmap_users(nodes: Array) -> Dictionary:\n"
    "\tvar users: Dictionary = {}\n"
    "\tfor n in nodes:\n"
    "\t\tvar lm: LightmapGI = n as LightmapGI\n"
    "\t\tif lm == null or lm.light_data == null:\n"
    "\t\t\tcontinue\n"
    "\t\tvar data: LightmapGIData = lm.light_data\n"
    "\t\tfor i in range(data.get_user_count()):\n"
    "\t\t\tvar u: Node = lm.get_node_or_null(data.get_user_path(i))\n"
    "\t\t\tif u != null:\n"
    "\t\t\t\tusers[u.get_instance_id()] = true\n"
    "\treturn users\n"
    "\n"
    "\n"
    "## WHETHER THE RENDERER PAIRS `l` WITH `mi`, given that the light reaches it.\n"
    "## Godot 4.7, servers/rendering/renderer_scene_cull.cpp, `_scene_cull`, where a\n"
    "## mesh's lights are rebuilt (FLAG_GEOM_LIGHTING_DIRTY): a light whose cull\n"
    "## mask misses the mesh's layers is skipped, and so is a BAKE_STATIC light on\n"
    "## a mesh that has a lightmap -- that light is in the lightmap already. A\n"
    "## hidden light is not in the scenario's pairing at all.\n"
    "static func _pairs(l: Light3D, mi: MeshInstance3D, mapped: bool) -> bool:\n"
    "\tif not l.is_visible_in_tree():\n"
    "\t\treturn false\n"
    "\tif (l.light_cull_mask & mi.layers) == 0:\n"
    "\t\treturn false\n"
    "\treturn not (mapped and l.light_bake_mode == Light3D.BAKE_STATIC)\n"
    "\n"
    "\n"
    "## TWO COUNTS (0.159.0).\n"
    "##   BY REACH, the top-level fields as they always were: every positional\n"
    "##   light whose range reaches a mesh's box, baked or live.\n"
    "##   PAIRED, under `paired`: of those, the ones the renderer binds (`_pairs`).\n"
    "## Since the light bake (0.131.0) most Lux rigs are BAKE_STATIC, and the\n"
    "## renderer never binds one to a lightmapped mesh, so the reach count stopped\n"
    "## being what the cap is spent on: cold run 9204's package read \"33 of 3,954\n"
    "## meshes over 8, worst 31\" with its club's stage lamps baked and with them\n"
    "## live (docs/findings/club_stage_live_price/ at the factory root). Both\n"
    "## counts take a light's range against the mesh's box -- spot cones as\n"
    "## spheres -- so both are upper bounds on what the renderer binds.\n"
    "static func _light_census(nodes: Array, cap: int) -> Dictionary:\n"
    "\tvar lights: Array = []\n"
    "\tvar meshes: Array = []\n"
    "\tfor n in nodes:\n"
    "\t\tvar l: Light3D = n as Light3D\n"
    "\t\tif l != null:\n"
    "\t\t\tif not (l is DirectionalLight3D):\n"
    "\t\t\t\tlights.append(l)\n"
    "\t\t\tcontinue\n"
    "\t\tvar mi: MeshInstance3D = n as MeshInstance3D\n"
    "\t\tif mi != null and mi.visible and mi.mesh != null:\n"
    "\t\t\tmeshes.append(mi)\n"
    "\tvar users: Dictionary = _lightmap_users(nodes)\n"
    "\tvar n_static: int = 0\n"
    "\tfor o in lights:\n"
    "\t\tif (o as Light3D).light_bake_mode == Light3D.BAKE_STATIC:\n"
    "\t\t\tn_static += 1\n"
    "\t# WHICH MESHES, not only how many. Cold run 9125 moved one light and the\n"
    "\t# count went 43 -> 44, and nothing could say which mesh had crossed: the\n"
    "\t# report kept the count and the single worst name, and names repeat\n"
    "\t# (`Prop_Panel`). Every mesh over the cap by its node PATH, worst first,\n"
    "\t# at most OVER_LIST_MAX, and a flag that says when the list was cut.\n"
    "\t# AND HOW MANY IN ALL, not only over the cap: `pairs` is every\n"
    "\t# (light, mesh) the count holds and `histogram` how many meshes hold how\n"
    "\t# many, so a change that moves lights under the cap still shows.\n"
    "\tvar reach: Dictionary = {\"over\": 0, \"worst\": 0, \"worst_mesh\": \"-\", \"list\": [],\n"
    "\t\t\"pairs\": 0, \"hist\": {}}\n"
    "\tvar paired: Dictionary = {\"over\": 0, \"worst\": 0, \"worst_mesh\": \"-\", \"list\": [],\n"
    "\t\t\"pairs\": 0, \"hist\": {}}\n"
    "\tfor m in meshes:\n"
    "\t\tvar mi2: MeshInstance3D = m as MeshInstance3D\n"
    "\t\tvar mapped: bool = users.has(mi2.get_instance_id())\n"
    "\t\tvar n_reach: int = 0\n"
    "\t\tvar n_paired: int = 0\n"
    "\t\tfor o in lights:\n"
    "\t\t\tvar ol: Light3D = o as Light3D\n"
    "\t\t\tif _surface_dist(mi2, ol.global_position) <= _reach(ol):\n"
    "\t\t\t\tn_reach += 1\n"
    "\t\t\t\tif _pairs(ol, mi2, mapped):\n"
    "\t\t\t\t\tn_paired += 1\n"
    "\t\tvar path: String = String(mi2.get_path())\n"
    "\t\t_tally(reach, n_reach, cap, {\"mesh\": path, \"lights\": n_reach}, mi2)\n"
    "\t\t_tally(paired, n_paired, cap,\n"
    "\t\t\t{\"mesh\": path, \"lights\": n_paired, \"by_reach\": n_reach}, mi2)\n"
    "\tvar out: Dictionary = {\"cap\": cap, \"lights\": lights.size(),\n"
    "\t\t\"meshes\": meshes.size(), \"basis\": \"reach\"}\n"
    "\tout.merge(_close(reach))\n"
    "\tvar p: Dictionary = _close(paired)\n"
    "\tp[\"basis\"] = \"paired\"\n"
    "\tp[\"lightmap_users\"] = users.size()\n"
    "\tp[\"lights_static\"] = n_static\n"
    "\tout[\"paired\"] = p\n"
    "\treturn out\n"
    "\n"
    "\n"
    "static func _tally(t: Dictionary, n: int, cap: int, row: Dictionary,\n"
    "\t\tmi: MeshInstance3D) -> void:\n"
    "\tt[\"pairs\"] = int(t[\"pairs\"]) + n\n"
    "\tvar h: Dictionary = t[\"hist\"]\n"
    "\th[n] = int(h.get(n, 0)) + 1\n"
    "\tif n > cap:\n"
    "\t\tt[\"over\"] = int(t[\"over\"]) + 1\n"
    "\t\t(t[\"list\"] as Array).append(row)\n"
    "\tif n > int(t[\"worst\"]):\n"
    "\t\tt[\"worst\"] = n\n"
    "\t\tt[\"worst_mesh\"] = String(mi.name)\n"
    "\n"
    "\n"
    "static func _close(t: Dictionary) -> Dictionary:\n"
    "\tvar lst: Array = t[\"list\"]\n"
    "\tlst.sort_custom(func(a, b): return int(a[\"lights\"]) > int(b[\"lights\"]) or "
    "(int(a[\"lights\"]) == int(b[\"lights\"]) and String(a[\"mesh\"]) < String(b[\"mesh\"])))\n"
    "\tvar truncated: bool = lst.size() > OVER_LIST_MAX\n"
    "\tif truncated:\n"
    "\t\tlst = lst.slice(0, OVER_LIST_MAX)\n"
    "\treturn {\"over_cap\": t[\"over\"], \"worst\": t[\"worst\"], \"worst_mesh\": t[\"worst_mesh\"],\n"
    "\t\t\"over_list\": lst, \"over_list_truncated\": truncated,\n"
    "\t\t\"pairs\": t[\"pairs\"], \"histogram\": t[\"hist\"]}\n")

PRINT_OLD = (
    "\tprint(\"[perf] lights per object: cap %d, %d of %d mesh(es) over it, worst %d (%s)\"\n"
    "\t\t% [census[\"cap\"], census[\"over_cap\"], census[\"meshes\"],\n"
    "\t\t\tcensus[\"worst\"], census[\"worst_mesh\"]])\n")
PRINT_NEW = (
    "\t# BOTH COUNTS (0.159.0): by reach, as this line always printed it, and\n"
    "\t# paired -- what the renderer binds, the one the cap is spent on.\n"
    "\tvar pc: Dictionary = census[\"paired\"]\n"
    "\tprint(\"[perf] lights per object: cap %d; by reach %d of %d mesh(es) over it, worst %d (%s); "
    "paired %d over it, worst %d (%s)\"\n"
    "\t\t% [census[\"cap\"], census[\"over_cap\"], census[\"meshes\"],\n"
    "\t\t\tcensus[\"worst\"], census[\"worst_mesh\"],\n"
    "\t\t\tpc[\"over_cap\"], pc[\"worst\"], pc[\"worst_mesh\"]])\n")

RUN_OLD = (
    "        print(\"  lights per object: cap %s, %s of %s mesh(es) over it, \"\n"
    "              \"worst %s (%s)\"\n"
    "              % (census.get(\"cap\"), census.get(\"over_cap\"),\n"
    "                 census.get(\"meshes\"), census.get(\"worst\"),\n"
    "                 census.get(\"worst_mesh\")))\n"
    "        # WHICH MESHES (0.125.0): the probe lists every mesh over the cap\n"
    "        # by node path, worst first; a report from before it has no list\n"
    "        for o in (census.get(\"over_list\") or [])[:OVER_PRINT]:\n"
    "            print(\"    %3s lights  %s\" % (o.get(\"lights\"), o.get(\"mesh\")))\n"
    "        if census.get(\"over_list_truncated\"):\n"
    "            print(\"    (list cut at the probe's limit; `over_cap` is the full count)\")\n")
RUN_NEW = (
    "        print(\"  lights per object, by reach: cap %s, %s of %s mesh(es) over it, \"\n"
    "              \"worst %s (%s); %s light-mesh pair(s)\"\n"
    "              % (census.get(\"cap\"), census.get(\"over_cap\"),\n"
    "                 census.get(\"meshes\"), census.get(\"worst\"),\n"
    "                 census.get(\"worst_mesh\"), census.get(\"pairs\", \"?\")))\n"
    "        # WHICH MESHES (0.125.0): the probe lists every mesh over the cap\n"
    "        # by node path, worst first; a report from before it has no list\n"
    "        for o in (census.get(\"over_list\") or [])[:OVER_PRINT]:\n"
    "            print(\"    %3s lights  %s\" % (o.get(\"lights\"), o.get(\"mesh\")))\n"
    "        if census.get(\"over_list_truncated\"):\n"
    "            print(\"    (list cut at the probe's limit; `over_cap` is the full count)\")\n"
    "        # PAIRED (0.159.0): what the renderer binds -- by reach less the\n"
    "        # baked lights on lightmapped meshes, the lights masked off a\n"
    "        # mesh's layers and the hidden ones. The cap is spent on this one.\n"
    "        paired = census.get(\"paired\")\n"
    "        if paired:\n"
    "            print(\"  lights per object, paired: %s of %s mesh(es) over the cap, \"\n"
    "                  \"worst %s (%s); %s light-mesh pair(s); %s lightmap user(s), \"\n"
    "                  \"%s of %s light(s) baked\"\n"
    "                  % (paired.get(\"over_cap\"), census.get(\"meshes\"),\n"
    "                     paired.get(\"worst\"), paired.get(\"worst_mesh\"),\n"
    "                     paired.get(\"pairs\", \"?\"), paired.get(\"lightmap_users\"),\n"
    "                     paired.get(\"lights_static\"), census.get(\"lights\")))\n"
    "            for o in (paired.get(\"over_list\") or [])[:OVER_PRINT]:\n"
    "                print(\"    %3s lights  (%s by reach)  %s\"\n"
    "                      % (o.get(\"lights\"), o.get(\"by_reach\"), o.get(\"mesh\")))\n"
    "            if paired.get(\"over_list_truncated\"):\n"
    "                print(\"    (list cut at the probe's limit; `over_cap` is the full count)\")\n"
    "        else:\n"
    "            print(\"  lights per object, paired: no paired count in this report \"\n"
    "                  \"(a probe from before 0.159.0)\")\n")

EDITS = {
    "tools/perf_stations.gd": [
        (HEADER_OLD, HEADER_NEW),
        ("func _surface_dist(mi: MeshInstance3D, p: Vector3) -> float:\n",
         "static func _surface_dist(mi: MeshInstance3D, p: Vector3) -> float:\n"),
        ("func _reach(l: Light3D) -> float:\n",
         "static func _reach(l: Light3D) -> float:\n"),
        (CENSUS_OLD, CENSUS_NEW),
        (PRINT_OLD, PRINT_NEW),
    ],
    "tools/perf_stations_run.py": [
        (RUN_OLD, RUN_NEW),
    ],
}
NEW = {"tests/unit/test_perf_census_pairs.py": "test_perf_census_pairs.py"}


def stage(root):
    """{path: bytes} for every edited and new file under ``root``, or raise.
    Nothing is written here: every anchor in every file must match first."""
    staged = {}
    for rel in NEW:
        assert not (root / rel).exists(), ("already applied", rel)
    for name, edits in EDITS.items():
        p = root / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    for rel, src in NEW.items():
        staged[root / rel] = (SRC / src).read_bytes()
    return staged


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.158.0", repr(v)
    staged = stage(LF)
    entry = (SRC / "CHANGELOG_0.159.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.159.0")
    print("Level Factory 0.158.0 -> 0.159.0")


if __name__ == "__main__":
    main()
