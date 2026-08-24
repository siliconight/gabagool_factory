extends Node
## One question, asked of the RUNNING tree: do the LuxEmit_* fixture markers
## carry their glTF-extras payload as node metadata?
##
## Written 2026-08-24, when the census showed every fluorescent at the
## no-drop range fallback while the fixtures GLB demonstrably carried
## `lux_drop` in every marker's extras (verified with pygltflib on the same
## build). Between the file and the spawner stands exactly one step --
## Godot's import of node extras into metadata -- and `marker_type`'s
## name-parse fallback has masked that step's health forever: the TYPE
## working proves nothing, because the type is also in the node name.
##
## Prints one fenced JSON block and quits. Reports, never judges.

const MARK_BEGIN := "<<<MARKER_META_JSON"
const MARK_END := "MARKER_META_JSON>>>"


func _ready() -> void:
	for _i in range(5):
		await get_tree().process_frame
	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return

	var markers: Array = []
	_collect(scene, markers)
	var with_meta := 0
	var with_drop := 0
	var samples: Array = []
	for mk in markers:
		var keys: Array = []
		for k in (mk as Node).get_meta_list():
			keys.append(String(k))
		if not keys.is_empty():
			with_meta += 1
		var has_drop: bool = (mk as Node).has_meta(&"lux_drop")
		if has_drop:
			with_drop += 1
		if samples.size() < 8:
			samples.append({
				"name": String(mk.name),
				"meta_keys": keys,
				"lux_drop": (mk as Node).get_meta(&"lux_drop", null),
			})
	_emit({
		"scene": String(scene.name),
		"markers_found": markers.size(),
		"markers_with_any_meta": with_meta,
		"markers_with_lux_drop": with_drop,
		"samples": samples,
	})


func _collect(node: Node, out: Array) -> void:
	if node is Node3D and String(node.name).begins_with("LuxEmit"):
		out.append(node)
	for c in node.get_children():
		_collect(c, out)


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()
