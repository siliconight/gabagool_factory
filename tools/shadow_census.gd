extends Node
## Which lights in the running scene cast shadows, by rig class.
##
## Loaded as an autoload by tools/shadow_census.py into a MIRROR of the
## project under test. After the scene settles, walks every Light3D and
## reports shadow_enabled by the class the shadow policy ranks on (roadmap
## 60), plus the LuxRoot's tier and budget if one is in the tree. Prints one
## fenced JSON block and quits.
##
## It reports and stops. Whether the budget is right for a machine is the
## quality-profile decision; this says what the package actually spends.

const MARK_BEGIN := "<<<SHADOW_CENSUS_JSON"
const MARK_END := "SHADOW_CENSUS_JSON>>>"

var _frames := 0
var _settle := 5


func _ready() -> void:
	_settle = int(ProjectSettings.get_setting("shadow_census/settle_frames", 5))


## The same reading LuxLighting.shadow_rank makes: the rig NODE's name, with
## the resource's rig_name appended -- signs and windows share a resource
## name, and the marker path names rigs `Spawned_<type>_<n>`.
func _class_of(light: Node3D) -> String:
	if light is DirectionalLight3D:
		return "sun"
	var rig_node := light.get_parent()
	if rig_node == null:
		return "other"
	var name := String(rig_node.name).to_lower()
	var r: Variant = rig_node.get(&"rig")
	if r != null and r.get(&"rig_name") != null:
		name += " " + String(r.get(&"rig_name")).to_lower()
	if name.contains("sign") or name.contains("pack") or name.contains("street"):
		return "exterior"
	if name.contains("window"):
		return "window"
	if name.contains("bulb") or name.contains("pendant"):
		return "bulb"
	if name.contains("fluorescent") or name.contains("ceiling"):
		return "fluorescent"
	return "other"


func _process(_delta: float) -> void:
	_frames += 1
	if _frames < _settle:
		return
	set_process(false)
	var lights: Array = []
	_walk(get_tree().root, lights)
	var by_class := {}
	var shadowed := 0
	for l in lights:
		var c := _class_of(l)
		if not by_class.has(c):
			by_class[c] = {"lights": 0, "shadowed": 0}
		by_class[c]["lights"] += 1
		if (l as Light3D).shadow_enabled:
			by_class[c]["shadowed"] += 1
			shadowed += 1
	var report := {"lights": lights.size(), "shadowed": shadowed,
		"by_class": by_class, "tier": -1, "budget": -1}
	for root in get_tree().get_nodes_in_group(&"lux_root"):
		report["tier"] = int(root.get(&"quality_tier"))
		var q: Variant = root.call(&"get_quality_profile")
		if q != null:
			report["budget"] = int(q.get(&"max_shadow_casters"))
		break
	print(MARK_BEGIN)
	print(JSON.stringify(report))
	print(MARK_END)
	get_tree().quit(0)


func _walk(node: Node, out: Array) -> void:
	if node is Light3D and (node as Light3D).visible:
		out.append(node)
	for child in node.get_children():
		_walk(child, out)
