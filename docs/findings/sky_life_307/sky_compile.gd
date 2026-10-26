extends SceneTree
# Opens a window, adds a walk copy's _walk.tscn, draws FRAMES frames and quits, so a shader that fails to compile
# says so on stdout. Then prints whether the sky-life materials' shaders report a valid RID. Measurements only.

const FRAMES := 30
var _n := 0

func _init() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())

func _process(_d: float) -> bool:
	_n += 1
	if _n == FRAMES:
		for n in ["SkyBirds", "SkyPlane"]:
			var g := root.get_node("_walk/" + n) as MultiMeshInstance3D
			var mat: ShaderMaterial = g.material_override
			print("%s shader rid valid %s, code %d chars" % [n, str(mat.shader.get_rid().is_valid()), mat.shader.code.length()])
		quit()
	return false
