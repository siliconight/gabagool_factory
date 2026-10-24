extends SceneTree
## PRICE INSTRUMENT, NOT SHIPPED. Gives a package copy's merged desk screens the CRT pass's darkening overlay, as an
## export with Level Factory's `_is_crt_face` taking `StockScreen` would carry it (finding 5 of the walker's walk of
## cold run 9386). Desk screens live in LF's MERGED lit meshes (`lot/<id>/merged/*.res`, `LitR_*`), which a GLB
## re-import never reaches, so the overlay is hung here on the merged meshes' screen material and saved.
##
## The shader is read from this package's own `zoo_worldskin.gd` (its MOTION_SHADER block), and its parameters are the
## values `_motion_material` sets, copied from Level Factory 0.238.0's constants: ROLL_PERIOD_S 5.0 (1 / 0.2 Hz),
## ROLL_BAND_FRAC 21/262.5, ROLL_DEPTH 0.10, ROLL_UP -1, FLICKER_DEPTH 0.035, FLICKER_HZ 1.3 and 2.1, NOISE_DEPTH 0.04,
## NOISE_HZ 12, SCREEN_PROUD_M 0.002, picture_pixels the albedo texture's size. Prints what it changed and stops.
##
##     godot --headless --path <package copy> --script res://screen_overlay_prep.gd

func _initialize() -> void:
	var src: String = FileAccess.get_file_as_string("res://zoo_worldskin.gd")
	var a: int = src.find("const MOTION_SHADER: String = \"\"\"")
	var start: int = src.find("\"\"\"", a) + 3
	var stop: int = src.find("\"\"\"", start)
	if a < 0 or stop < 0:
		print("[prep] REFUSED: no MOTION_SHADER block in res://zoo_worldskin.gd")
		quit(2)
		return
	var shader := Shader.new()
	shader.code = src.substr(start, stop - start)
	var given := {}
	var meshes := 0
	var root := DirAccess.open("res://lot")
	for b in root.get_directories():
		var d := DirAccess.open("res://lot/%s/merged" % b)
		if d == null:
			continue
		for f in d.get_files():
			if not f.ends_with(".res"):
				continue
			var path := "res://lot/%s/merged/%s" % [b, f]
			var m := load(path) as ArrayMesh
			if m == null:
				continue
			var changed := false
			for s in m.get_surface_count():
				var bm := m.surface_get_material(s) as BaseMaterial3D
				if bm == null:
					continue
				var nm := String(bm.resource_name)
				if not (nm.begins_with("M_") and nm.ends_with("_Face") and nm.contains("StockScreen")):
					continue
				if bm.next_pass == null:
					var sm := ShaderMaterial.new()
					sm.shader = shader
					sm.resource_name = nm + "_motion"
					var px := Vector2(224.0, 168.0)
					if bm.albedo_texture != null:
						px = Vector2(float(bm.albedo_texture.get_width()), float(bm.albedo_texture.get_height()))
					sm.set_shader_parameter("picture_pixels", px)
					sm.set_shader_parameter("roll_period_s", 5.0)
					sm.set_shader_parameter("roll_band_frac", 21.0 / 262.5)
					sm.set_shader_parameter("roll_depth", 0.10)
					sm.set_shader_parameter("roll_dir", -1.0)
					sm.set_shader_parameter("flicker_depth", 0.035)
					sm.set_shader_parameter("flicker_hz_a", 1.3)
					sm.set_shader_parameter("flicker_hz_b", 2.1)
					sm.set_shader_parameter("noise_depth", 0.04)
					sm.set_shader_parameter("noise_hz", 12.0)
					sm.set_shader_parameter("proud_m", 0.002)
					bm.next_pass = sm
					# a material kept in a file of its own is saved there, or the mesh's save drops the change
					if bm.resource_path != "" and not bm.resource_path.contains("::"):
						print("[prep] %s saved %s" % [bm.resource_path, ResourceSaver.save(bm, bm.resource_path)])
				given[nm] = true
				changed = true
			if changed:
				meshes += 1
				var err := ResourceSaver.save(m, path)
				print("[prep] %s saved %s" % [path, err])
	print("[prep] %d merged mesh(es) given the overlay, materials %s" % [meshes, given.keys()])
	quit(0 if meshes > 0 else 2)
