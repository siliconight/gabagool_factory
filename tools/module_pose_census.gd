extends Node
## Is every placed module standing the way its slot says?
##
## Loaded as an autoload by tools/module_pose_census.py into a MIRROR of the
## project under test. Walks every MeshInstance3D whose ancestor chain names
## a slot (`ext_*`, `int_*`, `prop_*`, ...) and reports its WORLD AABB --
## vertical extent, horizontal extents, and the gap between its bottom and
## the nearest storey floor -- so "a wall panel spun in its own plane" or "a
## slab floating at mid-height" is a row in a table rather than a screenshot.
## Prints one fenced JSON block and quits.
##
## It reports and stops: which pose is right belongs to the slot manifest
## and the composer, not to this file.

const MARK_BEGIN := "<<<MODULE_POSE_JSON"
const MARK_END := "MODULE_POSE_JSON>>>"

var _frames := 0
var _settle := 5


func _ready() -> void:
	_settle = int(ProjectSettings.get_setting("module_pose/settle_frames", 5))


func _slot_name(node: Node) -> String:
	var n: Node = node
	while n != null:
		var s := String(n.name)
		if s.begins_with("ext_") or s.begins_with("int_") or s.begins_with("prop") \
				or s.contains("_seg") or s.contains("cover") or s.contains("Cover"):
			return s
		n = n.get_parent()
	return ""


func _process(_delta: float) -> void:
	_frames += 1
	if _frames < _settle:
		return
	set_process(false)
	var rows: Array = []
	_walk(get_tree().root, rows)
	print(MARK_BEGIN)
	print(JSON.stringify({"meshes": rows.size(), "rows": rows}))
	print(MARK_END)
	get_tree().quit(0)


func _walk(node: Node, out: Array) -> void:
	if node is MeshInstance3D and (node as MeshInstance3D).mesh != null and (node as MeshInstance3D).visible:
		var mi := node as MeshInstance3D
		var slot := _slot_name(mi)
		if slot != "":
			var box: AABB = mi.global_transform * mi.mesh.get_aabb()
			var b: Basis = mi.global_transform.basis
			out.append({
				"slot": slot, "mesh": String(mi.name),
				"path": String(mi.get_path()),
				"min": [box.position.x, box.position.y, box.position.z],
				"size": [box.size.x, box.size.y, box.size.z],
				# the basis columns: where the mesh's local X, Y and Z point in the world
				"local_x": [b.x.x, b.x.y, b.x.z],
				"local_y": [b.y.x, b.y.y, b.y.z],
				"local_z": [b.z.x, b.z.y, b.z.z],
			})
	for child in node.get_children():
		_walk(child, out)
