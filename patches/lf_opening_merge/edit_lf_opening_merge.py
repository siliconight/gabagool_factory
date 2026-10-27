"""Edit a Level Factory clone for 0.258.0: an opening's surround merges with its wall; its glass stays its own
instance's mesh. Run from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


GD = "assets/godot/merge_buildings.gd"
edit(GD, [
("""##   * an opening, `*_open<n>`: a window's pane may be glass, which Godot sorts per mesh;
""", ""),
("""## 0.223.0 left every module with a lit face whole; a fixture still is.
""", """## 0.223.0 left every module with a lit face whole; a fixture still is.
## AN OPENING'S SURROUND MERGES WITH ITS WALL, AND ITS GLASS STAYS ITS OWN INSTANCE'S (0.258.0). Until 0.258.0 every
## `*_open<n>` slot was left whole because "a window's pane may be glass, which Godot sorts per mesh" -- so every
## doorway, window and breach panel kept its own mesh and its own lightmap chart beside a merged wall, and the walker,
## on seed 9205's first windowed walk, saw it as seams: "lot of seams visible on these doors", "highly visible seams
## and pieces here", "not consistent: textures" (the factory's `docs/findings/walk_2026-10-26_panel/`, L5-L7). The
## reason was a pane's, not a surround's: now a TRANSPARENT surface (`_glass`) goes into one mesh of its own,
## `GlassR_<n>`, where its instance stood -- sorted as it always was -- and the rest of the slot merges with its unit.
## A slot carrying `interactive_id` -- a door that opens, a breachable panel, a window that breaks -- still stays whole.
"""),
("""func _cell(px: float, py: float) -> String:""",
"""## A surface Godot draws transparent: sorted per mesh, so it keeps its own (0.258.0).
func _glass(mat: Material) -> bool:
	var bm: BaseMaterial3D = mat as BaseMaterial3D
	return bm != null and bm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED


func _cell(px: float, py: float) -> String:"""),
("""	if child.has_meta("interactive_id") or name.find("_open") >= 0:
		return false""",
"""	if child.has_meta("interactive_id"):
		return false"""),
("""		"unwrapped": 0, "colliders": 0, "units": {}, "lit_surfaces": 0, "lit_meshes": 0, "kept_carrying": [],
		"error": null}""",
"""		"unwrapped": 0, "colliders": 0, "units": {}, "lit_surfaces": 0, "lit_meshes": 0, "glass_surfaces": 0,
		"glass_meshes": 0, "kept_carrying": [], "error": null}"""),
("""	# one entry a lit instance: its lit surfaces, each [SurfaceTool, material], in its own mesh (0.224.0)
	var lit: Array = []""",
"""	# one entry a lit instance: its lit surfaces, each [SurfaceTool, material], in its own mesh (0.224.0)
	var lit: Array = []
	# ...and a glazed one: its transparent surfaces, the same way (0.258.0)
	var glazed: Array = []"""),
("""			var mine: Dictionary = {}
			for s in range(mi.mesh.get_surface_count()):""",
"""			var mine: Dictionary = {}
			var panes: Dictionary = {}
			for s in range(mi.mesh.get_surface_count()):"""),
("""					row["lit_surfaces"] = int(row["lit_surfaces"]) + 1
					continue""",
"""					row["lit_surfaces"] = int(row["lit_surfaces"]) + 1
					continue
				if _glass(mat):
					var gk: String = mat.resource_name if mat.resource_name != "" else "<glass %d>" % s
					if not panes.has(gk):
						panes[gk] = [SurfaceTool.new(), mat]
					((panes[gk] as Array)[0] as SurfaceTool).append_from(mi.mesh, s, xf)
					row["glass_surfaces"] = int(row["glass_surfaces"]) + 1
					continue"""),
("""			if not mine.is_empty():
				lit.append(mine)""",
"""			if not mine.is_empty():
				lit.append(mine)
			if not panes.is_empty():
				glazed.append(panes)"""),
("""	row["lit_meshes"] = li""",
"""	row["lit_meshes"] = li
	# THE PANES, one mesh an instance where it stood (0.258.0), the lit faces' way
	var gi: int = 0
	for panes in glazed:
		var gam := ArrayMesh.new()
		var gnames: Array = (panes as Dictionary).keys()
		gnames.sort()
		for gk in gnames:
			var gpair: Array = (panes as Dictionary)[gk]
			(gpair[0] as SurfaceTool).commit(gam)
			gam.surface_set_material(gam.get_surface_count() - 1, (gpair[1] as Material).duplicate(true) as Material)
		if gam.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) == OK:
			row["unwrapped"] = int(row["unwrapped"]) + 1
		var gpath: String = "%s/g%d.res" % [dir, gi]
		var gerr: int = ResourceSaver.save(gam, gpath)
		if gerr != OK:
			scene.queue_free()
			row["error"] = "cannot save %s (%d)" % [gpath, gerr]
			return row
		var gout := MeshInstance3D.new()
		gout.name = "GlassR_%d" % gi
		gout.mesh = load(gpath) as ArrayMesh
		gout.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		scene.add_child(gout)
		gout.owner = scene
		gi += 1
	row["glass_meshes"] = gi"""),
("""			var fmt: String = ("%d slots, %d meshes, %d surfaces -> %d merged, %d lit surfaces in %d meshes of "
				+ "their own (%d unwrapped), %d colliders kept; %d slots kept whole, holding what it cannot carry")
			said = fmt % [row["slots_merged"], row["meshes_in"], row["surfaces_in"], row["merged"],
				row["lit_surfaces"], row["lit_meshes"], row["unwrapped"], row["colliders"],
				(row["kept_carrying"] as Array).size()]""",
"""			var fmt: String = ("%d slots, %d meshes, %d surfaces -> %d merged, %d lit surfaces in %d meshes of "
				+ "their own, %d glass surfaces in %d (%d unwrapped), %d colliders kept; %d slots kept whole, "
				+ "holding what it cannot carry")
			said = fmt % [row["slots_merged"], row["meshes_in"], row["surfaces_in"], row["merged"],
				row["lit_surfaces"], row["lit_meshes"], row["glass_surfaces"], row["glass_meshes"],
				row["unwrapped"], row["colliders"], (row["kept_carrying"] as Array).size()]"""),
])

edit("packages/exporting/merge_buildings.py", [
("""                  "lit_surfaces", "lit_meshes"):""", """                  "lit_surfaces", "lit_meshes", "glass_surfaces", "glass_meshes"):"""),
("""        # every mesh it made is unwrapped: the merged groups and the lit instances both (0.224.0)
        if r["unwrapped"] != r["merged"] + r["lit_meshes"]:
            raise MergeError(f"{scene}: {r['unwrapped']} of {r['merged'] + r['lit_meshes']} meshes unwrapped \"""",
"""        # every mesh it made is unwrapped: the merged groups, the lit instances and the glazed ones (0.224.0, 0.258.0)
        made = r["merged"] + r["lit_meshes"] + r["glass_meshes"]
        if r["unwrapped"] != made:
            raise MergeError(f"{scene}: {r['unwrapped']} of {made} meshes unwrapped \""""),
("""        if (r["lit_meshes"] > 0) != (r["lit_surfaces"] > 0) or r["lit_meshes"] > r["lit_surfaces"]:
            raise MergeError(f"{scene}: {r['lit_surfaces']} lit surfaces in {r['lit_meshes']} meshes")""",
"""        if (r["lit_meshes"] > 0) != (r["lit_surfaces"] > 0) or r["lit_meshes"] > r["lit_surfaces"]:
            raise MergeError(f"{scene}: {r['lit_surfaces']} lit surfaces in {r['lit_meshes']} meshes")
        if (r["glass_meshes"] > 0) != (r["glass_surfaces"] > 0) or r["glass_meshes"] > r["glass_surfaces"]:
            raise MergeError(f"{scene}: {r['glass_surfaces']} glass surfaces in {r['glass_meshes']} meshes")"""),
])
