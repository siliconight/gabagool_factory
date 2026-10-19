@tool
extends EditorPlugin
## Roadmap 24's proof: open a shipped scene in the editor, let Lux's @tool scripts run as they would for anyone who
## opens the package, save it, and write what the editor held when it saved. `owner_probe.py` installs this into a
## COPY of a package, runs the editor headless, and diffs the saved scene against the shipped one -- the diff, not
## this census, is the measurement. A probe: it reports and quits.
##
## The waits follow Level Factory's light bake plugin (`assets/godot/light_bake_plugin.gd`): the editor's low
## processor mode is held off every frame, the open is asked once the first file scan is idle and again until it
## lands, and every wait is bounded on a clock.

const CONFIG := "res://owner_probe.json"
const OUT := "res://owner_probe_result.json"
const OPEN_LIMIT_MS := 600000

var _phase: int = 0
var _frames: int = 0
var _t0: int = 0
var _scene: String = ""
var _settle: int = 120


func _enter_tree() -> void:
	OS.low_processor_usage_mode = false
	var cfg: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
	if cfg is Dictionary:
		_scene = String((cfg as Dictionary).get("scene", ""))
		_settle = int((cfg as Dictionary).get("settle_frames", 120))
	set_process(true)


func _process(_delta: float) -> void:
	OS.low_processor_usage_mode = false
	_frames += 1
	match _phase:
		0:
			if _frames < 120 or EditorInterface.get_resource_filesystem().is_scanning():
				return
			if _scene == "" or not ResourceLoader.exists(_scene):
				_done({"ok": false, "error": "no scene to open: %s" % _scene})
				return
			EditorInterface.open_scene_from_path(_scene)
			_t0 = Time.get_ticks_msec()
			_phase = 1
			_frames = 0
		1:
			var root: Node = EditorInterface.get_edited_scene_root()
			if root == null or root.scene_file_path != _scene:
				if _frames % 300 == 0 and not EditorInterface.get_resource_filesystem().is_scanning():
					EditorInterface.open_scene_from_path(_scene)
				if Time.get_ticks_msec() - _t0 > OPEN_LIMIT_MS:
					_done({"ok": false, "error": "the scene did not open", "waited_ms": Time.get_ticks_msec() - _t0})
				return
			_phase = 2
			_frames = 0
		2:
			if _frames < _settle:
				return
			var root2: Node = EditorInterface.get_edited_scene_root()
			var census: Dictionary = {"nodes": 0, "owned": 0, "lux_owned": [], "world_environments": 0,
				"directional_lights": 0, "canvas_layers": 0}
			_census(root2, root2, census)
			EditorInterface.save_scene()
			_done({"ok": true, "scene": _scene, "settle_frames": _settle,
				"open_ms": Time.get_ticks_msec() - _t0, "census": census})


## Every node the edited root holds, how many a save would keep (owned by the root), and the Lux-made kinds the
## item names: WorldEnvironments, suns, canvas layers.
func _census(n: Node, root: Node, out: Dictionary) -> void:
	out["nodes"] = int(out["nodes"]) + 1
	if n == root or n.owner == root:
		out["owned"] = int(out["owned"]) + 1
		if String(n.name).begins_with("Lux") and (out["lux_owned"] as Array).size() < 60:
			(out["lux_owned"] as Array).append(str(root.get_path_to(n)))
	if n is WorldEnvironment:
		out["world_environments"] = int(out["world_environments"]) + 1
	if n is DirectionalLight3D:
		out["directional_lights"] = int(out["directional_lights"]) + 1
	if n is CanvasLayer:
		out["canvas_layers"] = int(out["canvas_layers"]) + 1
	for c in n.get_children():
		_census(c, root, out)


func _done(result: Dictionary) -> void:
	set_process(false)
	var f := FileAccess.open(OUT, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(result, " "))
		f.close()
	print("OWNER_PROBE ", JSON.stringify(result))
	var tree := EditorInterface.get_base_control().get_tree()
	tree.quit()
	await tree.process_frame
	await tree.process_frame
	OS.kill(OS.get_process_id())
