extends Node
## How much Layer 3 surface dressing is actually standing in the running scene?
##
## Loaded as an autoload by tools/dressing_census.py into a MIRROR of the
## project under test. Walks the tree after the scene has settled, finds every
## MultiMeshInstance3D, and reports per node: instance_count, visible
## instance count, whether the mesh resolved, and the world AABB of the
## instances. Prints one fenced JSON block and quits.
##
## It reports and stops. Whether 1,094 pebbles is the right number for a
## site is item 18's question; this answers only whether the package the
## export wrote is the package the engine runs.

const MARK_BEGIN := "<<<DRESSING_CENSUS_JSON"
const MARK_END := "DRESSING_CENSUS_JSON>>>"

var _frames := 0
var _settle := 5


func _ready() -> void:
	_settle = int(ProjectSettings.get_setting("dressing_census/settle_frames", 5))


func _process(_delta: float) -> void:
	_frames += 1
	if _frames < _settle:
		return
	set_process(false)
	var nodes: Array = []
	_walk(get_tree().root, nodes)
	var report := {"multimesh_nodes": nodes.size(), "instances": 0,
		"visible_instances": 0, "nodes": []}
	for n in nodes:
		var mmi := n as MultiMeshInstance3D
		var mm: MultiMesh = mmi.multimesh
		var entry := {"path": String(mmi.get_path()), "instance_count": 0,
			"visible_instance_count": 0, "mesh": false, "aabb_position": [],
			"aabb_size": []}
		if mm != null:
			entry["instance_count"] = mm.instance_count
			var vis: int = mm.visible_instance_count
			if vis < 0:
				vis = mm.instance_count
			entry["visible_instance_count"] = vis
			entry["mesh"] = mm.mesh != null
			# Both get_aabb() forms are the render server's and read empty
			# headless. The instance ORIGINS are in the buffer -- 12 floats
			# per instance, row-major, origin at 3, 7 and 11 -- so the box
			# is taken from those, in world space through the node's own
			# transform. Origins, not mesh extents: a pebble's extent is
			# centimetres and the question is where the scatter is.
			var buf: PackedFloat32Array = mm.buffer
			var lo := Vector3.INF
			var hi := -Vector3.INF
			var i := 0
			while i + 11 < buf.size():
				var o := mmi.global_transform * Vector3(buf[i + 3], buf[i + 7], buf[i + 11])
				lo = lo.min(o)
				hi = hi.max(o)
				i += 12
			if buf.size() >= 12:
				entry["aabb_position"] = [lo.x, lo.y, lo.z]
				entry["aabb_size"] = [hi.x - lo.x, hi.y - lo.y, hi.z - lo.z]
			report["instances"] += mm.instance_count
			report["visible_instances"] += vis
		report["nodes"].append(entry)
	print(MARK_BEGIN)
	print(JSON.stringify(report))
	print(MARK_END)
	get_tree().quit(0)


func _walk(node: Node, out: Array) -> void:
	if node is MultiMeshInstance3D:
		out.append(node)
	for child in node.get_children():
		_walk(child, out)
