extends SceneTree
## Cold run 9265: which sun does a package run? (Lux 0.76.0, factory roadmap 243)
##
##     godot --headless --path <an imported copy of a package> -s res://sun_state.gd
##
## Loads the package's main scene the way the game does, lets Lux bind its lightmaps (deferred from
## LuxRoot's ready), and prints the LuxSun's bake mode, shadow and visibility, how many LightmapGI
## nodes carry data, and LuxRoot's baked_lighting() and fixtures_powered(): at frame 5, at frame 35,
## with the power cut (`set_fixtures_powered(false)`), and with it back. Also whether the vendored
## `lux_lighting.gd` carries `_apply_sun_mode`, which only 0.76.0 does.
##
## Run on 9264's package too, as the control: a 0.75.0 package must read "dynamic, shadowed" with its
## lightmap shown, or this cannot see the difference it is asked about. Headless draws nothing: this
## reads state, not light. It measures and stops.

const LIGHTING_SRC := "res://runtime/lux/runtime/lux_lighting.gd"


func _initialize() -> void:
	_main.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _find(node: Node, out: Dictionary) -> void:
	if node is DirectionalLight3D and String(node.name) == "LuxSun":
		out["sun"] = node
	if node is LightmapGI:
		out["lightmaps"].append(node)
	if node.has_method("set_fixtures_powered") and node.has_method("baked_lighting") \
			and node.has_method("fixtures_powered") and not out.has("lux"):
		out["lux"] = node
	for child in node.get_children():
		_find(child, out)


func _report(label: String) -> void:
	var out: Dictionary = {"lightmaps": []}
	_find(root, out)
	var with_data: int = 0
	for lm in out["lightmaps"]:
		if (lm as LightmapGI).light_data != null:
			with_data += 1
	var sun_text: String = "NO LuxSun"
	if out.has("sun"):
		var sun: DirectionalLight3D = out["sun"]
		sun_text = "%s, %s, visible %s" % [
			"static" if sun.light_bake_mode == Light3D.BAKE_STATIC else (
				"dynamic" if sun.light_bake_mode == Light3D.BAKE_DYNAMIC else "disabled"),
			"shadowed" if sun.shadow_enabled else "unshadowed", str(sun.visible)]
	var lux_text: String = "NO LuxRoot"
	if out.has("lux"):
		lux_text = "baked_lighting %s, fixtures_powered %s" % [
			str(out["lux"].baked_lighting()), str(out["lux"].fixtures_powered())]
	var lm_text: String = "lightmaps with data %d of %d" % [with_data, out["lightmaps"].size()]
	print("%-12s sun %s; %s; %s" % [label, sun_text, lm_text, lux_text])


func _main() -> void:
	var src: String = FileAccess.get_file_as_string(LIGHTING_SRC)
	print("vendored lux_lighting.gd: %d bytes, carries _apply_sun_mode: %s" % [
		src.length(), str(src.contains("func _apply_sun_mode"))])
	var path: String = str(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		print("could not load the main scene %s" % path)
		_exit(2)
		return
	root.add_child(packed.instantiate())
	for i in 5:
		await process_frame
	_report("frame 5")
	for i in 30:
		await process_frame
	_report("frame 35")
	var probe: Dictionary = {"lightmaps": []}
	_find(root, probe)
	if not probe.has("lux"):
		print("no LuxRoot to cut the power on")
		_exit(2)
		return
	probe["lux"].set_fixtures_powered(false)
	await process_frame
	_report("power cut")
	probe["lux"].set_fixtures_powered(true)
	await process_frame
	_report("power back")
	_exit(0)
