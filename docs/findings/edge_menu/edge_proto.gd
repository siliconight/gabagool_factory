extends Node3D
## A MOCKUP, NOT PIPELINE OUTPUT (roadmap 219 notes 8 and 12): what could stand at the plate's
## edge and beyond it, for the walker to choose from. Built at run time from EDGE_OPTION, a comma
## list of parts:
##   wall_dark  the perimeter's flat pale material swapped for dark concrete block, with a cap
##   glow       a ring 380 m out: a sodium sky-glow at the horizon over dark land
##   houses     rows of rowhome blocks beyond the wall, 2-3 storeys, a few windows lit
##   houses_far the same rows from 38 m out only, behind a tree belt
##   trees      a belt of tree crowns beyond the wall
##   tower      a water tower 90 m beyond the north edge, a red lamp on top
##   fence      the wall's tiles hidden, its collision kept, and Zoo's 14.9 m chain-link
##              run tiled just inside it (42 modules here; one long run a side in a tool)
## Empty, it builds nothing, so the same copy is its own control.
## Frame: Godot, x east, y up, z = -plan y, metres. The plate is x -102..102, z -51..51.

const X0 := -102.0
const X1 := 102.0
const Z0 := -51.0
const Z1 := 51.0
const SEED := 9181
const WALL_H := 3.0

var _rng := RandomNumberGenerator.new()
var _counts := {}


func _ready() -> void:
	call_deferred("_build")


func _build() -> void:
	var opt: String = OS.get_environment("EDGE_OPTION")
	if opt == "":
		print("[edge_proto] EDGE_OPTION empty: nothing built")
		return
	var parts: PackedStringArray = opt.split(",")
	_rng.seed = SEED
	if parts.has("wall_dark"):
		_wall_dark()
	if parts.has("fence"):
		_fence()
	if parts.has("glow"):
		add_child(_glow_ring())
		_counts["glow"] = 1
	if parts.has("houses"):
		_houses(false)
	elif parts.has("houses_far"):
		_houses(true)
	if parts.has("trees"):
		_trees()
	if parts.has("tower"):
		_water_tower(Vector3(-40.0, 0.0, Z0 - 90.0))
	print("[edge_proto] built ", opt, " ", _counts)


# --- the wall ------------------------------------------------------------------------------------

func _wall_dark() -> void:
	var block := StandardMaterial3D.new()
	block.albedo_texture = load("res://skins/concrete_delco_albedo.png") as Texture2D
	block.albedo_color = Color(0.36, 0.35, 0.34)
	block.uv1_triplanar = true
	block.uv1_scale = Vector3(0.5, 0.5, 0.5)
	block.roughness = 0.95
	var walls: Array[Node] = get_tree().root.find_children("perim_*", "StaticBody3D", true, false)
	var tiles := 0
	for w in walls:
		for c in w.get_children():
			var mi := c as MeshInstance3D
			if mi != null:
				mi.material_override = block
				tiles += 1
	# a concrete cap along each wall's top: one MultiMesh, four instances
	var cap := BoxMesh.new()
	cap.size = Vector3(1.0, 1.0, 1.0)
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = cap
	mm.instance_count = 4
	var lx := X1 - X0 + 0.5
	var lz := Z1 - Z0 + 0.5
	mm.set_instance_transform(0, _box_xf(Vector3(0.0, WALL_H + 0.08, Z0), Vector3(lx, 0.16, 0.5)))
	mm.set_instance_transform(1, _box_xf(Vector3(0.0, WALL_H + 0.08, Z1), Vector3(lx, 0.16, 0.5)))
	mm.set_instance_transform(2, _box_xf(Vector3(X0, WALL_H + 0.08, 0.0), Vector3(0.5, 0.16, lz)))
	mm.set_instance_transform(3, _box_xf(Vector3(X1, WALL_H + 0.08, 0.0), Vector3(0.5, 0.16, lz)))
	var capmat := StandardMaterial3D.new()
	capmat.albedo_color = Color(0.42, 0.41, 0.40)
	capmat.roughness = 0.9
	add_child(_mmi("WallCaps", mm, capmat))
	_counts["wall_tiles"] = tiles
	_counts["wall_bodies"] = walls.size()


# --- the fence --------------------------------------------------------------------------------

func _fence() -> void:
	var scene := load("res://cover/prop_chain_link_fence_delco_1997_01_w1490_d6_h183.glb") as PackedScene
	if scene == null:
		push_warning("[edge_proto] no 14.9 m chain-link module in this package")
		return
	var mod := 14.9
	var h := 1.83
	var walls: Array[Node] = get_tree().root.find_children("perim_*", "StaticBody3D", true, false)
	for w in walls:
		for c in w.get_children():
			var mi := c as MeshInstance3D
			if mi != null:
				mi.visible = false
	var n := 0
	for side: String in ["N", "S", "E", "W"]:
		var length: float = (X1 - X0) if (side == "N" or side == "S") else (Z1 - Z0)
		var count: int = int(ceil(length / mod))
		for i: int in range(count):
			var along: float = minf(-length * 0.5 + mod * (float(i) + 0.5), length * 0.5 - mod * 0.5)
			var inst := scene.instantiate() as Node3D
			if side == "N":
				inst.position = Vector3(along, h * 0.5, Z0 + 0.25)
			elif side == "S":
				inst.position = Vector3(along, h * 0.5, Z1 - 0.25)
			elif side == "E":
				inst.position = Vector3(X1 - 0.25, h * 0.5, along)
				inst.rotation = Vector3(0.0, PI * 0.5, 0.0)
			else:
				inst.position = Vector3(X0 + 0.25, h * 0.5, along)
				inst.rotation = Vector3(0.0, PI * 0.5, 0.0)
			add_child(inst)
			n += 1
	_counts["fence_modules"] = n
	_counts["wall_bodies_hidden"] = walls.size()


# --- the sky-glow --------------------------------------------------------------------------------

func _glow_ring() -> MeshInstance3D:
	# rings of vertices at these heights, 380 m out, coloured top to foot: nothing high up, a
	# sodium glow at the horizon (eye height 1.7), dark land under it
	# A city's sky-glow climbs 10 to 20 degrees: from 26 m a 3.2 m wall already covers the first 3.2
	# of them, so a glow that fades out by 4 degrees is hidden by the wall it stands behind. RETRACTED,
	# kept: the first ring peaked at the horizon and was gone by 25 m up (3.8 degrees), and no frame
	# showed it.
	var heights := PackedFloat32Array([-20.0, -1.0, 1.7, 30.0, 70.0, 140.0])
	var cols := PackedColorArray([
		Color(0.03, 0.03, 0.035, 1.0), Color(0.05, 0.045, 0.05, 1.0),
		Color(0.78, 0.47, 0.26, 0.34), Color(0.70, 0.42, 0.24, 0.24),
		Color(0.55, 0.34, 0.22, 0.08), Color(0.50, 0.30, 0.20, 0.0)])
	var seg := 64
	var radius := 380.0
	var nh: int = heights.size()
	var verts := PackedVector3Array()
	var vcols := PackedColorArray()
	var idx := PackedInt32Array()
	for i in range(seg + 1):
		var a: float = TAU * float(i) / float(seg)
		for j in range(nh):
			verts.append(Vector3(cos(a) * radius, heights[j], sin(a) * radius))
			vcols.append(cols[j])
	for i in range(seg):
		for j in range(nh - 1):
			var a0: int = i * nh + j
			var b0: int = (i + 1) * nh + j
			idx.append_array(PackedInt32Array([a0, b0, a0 + 1, b0, b0 + 1, a0 + 1]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_COLOR] = vcols
	arrays[Mesh.ARRAY_INDEX] = idx
	var ring := ArrayMesh.new()
	ring.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.vertex_color_use_as_albedo = true
	mat.disable_receive_shadows = true
	# the glow IS the haze: Delco Night's fog (density 0.006) leaves a tenth of anything 380 m out
	mat.disable_fog = true
	var mi := MeshInstance3D.new()
	mi.name = "GlowRing"
	mi.mesh = ring
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	return mi


# --- the houses beyond the wall ------------------------------------------------------------------

func _houses(far_only: bool) -> void:
	var body := BoxMesh.new()
	body.size = Vector3(1.0, 1.0, 1.0)
	var roof := PrismMesh.new()
	roof.size = Vector3(1.0, 1.0, 1.0)
	var pane := QuadMesh.new()
	pane.size = Vector2(0.9, 1.3)
	var lamp := SphereMesh.new()
	lamp.radius = 0.35
	lamp.height = 0.7
	lamp.radial_segments = 8
	lamp.rings = 4
	var brick := StandardMaterial3D.new()
	brick.vertex_color_use_as_albedo = true
	brick.roughness = 0.95
	var lit := StandardMaterial3D.new()
	lit.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	lit.vertex_color_use_as_albedo = true
	var n_houses := 0
	var n_windows := 0
	for side: String in ["N", "S", "E", "W"]:
		var bodies: Array[Transform3D] = []
		var body_cols: Array[Color] = []
		var roofs: Array[Transform3D] = []
		var roof_cols: Array[Color] = []
		var panes: Array[Transform3D] = []
		var pane_cols: Array[Color] = []
		var lamps: Array[Transform3D] = []
		for band: Vector2 in [Vector2(4.0, 14.0), Vector2(38.0, 49.0), Vector2(80.0, 92.0)]:
			if far_only and band.x < 10.0:
				continue
			var span := _side_span(side, band.y)
			var t := span.x
			while t < span.y:
				if _rng.randf() < 0.07:
					t += _rng.randf_range(8.0, 14.0)          # a cross street
					continue
				var w := _rng.randf_range(5.0, 7.5)
				var depth := band.y - band.x
				var h := _rng.randf_range(6.5, 10.0)
				var d_mid := (band.x + band.y) * 0.5
				var c := _place(side, t + w * 0.5, d_mid)
				var size := _sized(side, w, h, depth)
				bodies.append(_box_xf(c + Vector3(0.0, h * 0.5, 0.0), size))
				var k := _rng.randf_range(0.06, 0.12)
				body_cols.append(Color(k * 1.25, k * 0.8, k * 0.7))
				if _rng.randf() < 0.3:
					var rh := _rng.randf_range(2.0, 3.0)
					roofs.append(_roof_xf(side, c + Vector3(0.0, h + rh * 0.5, 0.0), w, rh, depth))
					roof_cols.append(Color(k * 0.6, k * 0.6, k * 0.65))
				# windows on the face toward the plate, only the lit ones drawn
				var storeys: int = int(h / 3.0)
				for s: int in range(storeys):
					for j: int in range(2):
						if _rng.randf() < 0.2:
							var along: float = t + w * (0.3 + 0.4 * float(j))
							var face := _place(side, along, band.x - 0.02)
							face.y = 1.6 + 3.0 * float(s)
							panes.append(_pane_xf(side, face))
							if _rng.randf() < 0.2:
								pane_cols.append(Color(0.55, 0.65, 0.95))      # a TV
							else:
								pane_cols.append(Color(1.0, 0.78, 0.48))
				n_houses += 1
				t += w + (0.0 if _rng.randf() < 0.8 else _rng.randf_range(1.0, 3.0))
			# a street of lamps in front of the band, except the first: it backs onto the wall
			if band.x > 10.0:
				var u := span.x
				while u < span.y:
					var p := _place(side, u, band.x - 6.0)
					p.y = 6.0
					lamps.append(Transform3D(Basis(), p))
					u += _rng.randf_range(26.0, 34.0)
		add_child(_mmi("Houses_" + side, _mm(body, bodies, body_cols), brick))
		if not roofs.is_empty():
			add_child(_mmi("Roofs_" + side, _mm(roof, roofs, roof_cols), brick))
		if not panes.is_empty():
			add_child(_mmi("Windows_" + side, _mm(pane, panes, pane_cols), lit))
			n_windows += panes.size()
		if not lamps.is_empty():
			var lc: Array[Color] = []
			for _i in range(lamps.size()):
				lc.append(Color(1.0, 0.62, 0.30))
			add_child(_mmi("Lamps_" + side, _mm(lamp, lamps, lc), lit))
	_counts["houses"] = n_houses
	_counts["lit_windows"] = n_windows


# --- the tree belt -------------------------------------------------------------------------------

func _trees() -> void:
	var crown := SphereMesh.new()
	crown.radius = 1.0
	crown.height = 2.0
	crown.radial_segments = 10
	crown.rings = 5
	var trunk := BoxMesh.new()
	trunk.size = Vector3(1.0, 1.0, 1.0)
	var leaf := StandardMaterial3D.new()
	leaf.vertex_color_use_as_albedo = true
	leaf.roughness = 1.0
	var n := 0
	for side: String in ["N", "S", "E", "W"]:
		var crowns: Array[Transform3D] = []
		var crown_cols: Array[Color] = []
		var trunks: Array[Transform3D] = []
		var trunk_cols: Array[Color] = []
		var span := _side_span(side, 40.0)
		var t := span.x
		while t < span.y:
			var d := _rng.randf_range(2.5, 38.0)
			var r := _rng.randf_range(2.6, 5.0)
			var stem := _rng.randf_range(2.5, 5.0)
			var p := _place(side, t, d)
			var sq := _rng.randf_range(0.85, 1.35)
			crowns.append(Transform3D(Basis().scaled(Vector3(r, r * sq, r)), p + Vector3(0.0, stem + r * sq * 0.85, 0.0)))
			var k := _rng.randf_range(0.6, 1.0)
			crown_cols.append(Color(0.05 * k, 0.085 * k, 0.05 * k))
			trunks.append(_box_xf(p + Vector3(0.0, stem * 0.5 + 0.5, 0.0), Vector3(0.35, stem + 1.0, 0.35)))
			trunk_cols.append(Color(0.07, 0.055, 0.045))
			n += 1
			t += _rng.randf_range(1.2, 3.2)
		add_child(_mmi("Crowns_" + side, _mm(crown, crowns, crown_cols), leaf))
		add_child(_mmi("Trunks_" + side, _mm(trunk, trunks, trunk_cols), leaf))
	_counts["trees"] = n


# --- the landmark --------------------------------------------------------------------------------

func _water_tower(at: Vector3) -> void:
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.20, 0.24, 0.24)
	steel.roughness = 0.6
	var tank := CylinderMesh.new()
	tank.top_radius = 7.0
	tank.bottom_radius = 7.0
	tank.height = 8.0
	tank.radial_segments = 24
	var cone := CylinderMesh.new()
	cone.top_radius = 0.4
	cone.bottom_radius = 7.4
	cone.height = 3.0
	cone.radial_segments = 24
	var leg := BoxMesh.new()
	leg.size = Vector3(0.6, 28.0, 0.6)
	var root := Node3D.new()
	root.name = "WaterTower"
	root.position = at
	add_child(root)
	root.add_child(_mesh("Tank", tank, steel, Vector3(0.0, 32.0, 0.0)))
	root.add_child(_mesh("Cone", cone, steel, Vector3(0.0, 37.5, 0.0)))
	for i: int in range(4):
		var a: float = TAU * (float(i) + 0.5) / 4.0
		root.add_child(_mesh("Leg" + str(i), leg, steel, Vector3(cos(a) * 5.0, 14.0, sin(a) * 5.0)))
	var red := StandardMaterial3D.new()
	red.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	red.albedo_color = Color(1.0, 0.12, 0.08)
	red.disable_fog = true
	var bulb := SphereMesh.new()
	bulb.radius = 0.6
	bulb.height = 1.2
	root.add_child(_mesh("Beacon", bulb, red, Vector3(0.0, 39.6, 0.0)))
	_counts["tower_meshes"] = 7         # the tank, its cone, four legs and the lamp


# --- helpers -------------------------------------------------------------------------------------

## The span along a side, metres, wide enough to fill the corners at this depth.
func _side_span(side: String, depth: float) -> Vector2:
	if side == "N" or side == "S":
		return Vector2(X0 - depth - 20.0, X1 + depth + 20.0)
	return Vector2(Z0 + 2.0, Z1 - 2.0)


## A point `along` the side and `out` metres beyond its wall, on the ground.
func _place(side: String, along: float, out: float) -> Vector3:
	if side == "N":
		return Vector3(along, 0.0, Z0 - out)
	if side == "S":
		return Vector3(along, 0.0, Z1 + out)
	if side == "E":
		return Vector3(X1 + out, 0.0, along)
	return Vector3(X0 - out, 0.0, along)


func _sized(side: String, w: float, h: float, depth: float) -> Vector3:
	if side == "N" or side == "S":
		return Vector3(w, h, depth)
	return Vector3(depth, h, w)


func _box_xf(centre: Vector3, size: Vector3) -> Transform3D:
	return Transform3D(Basis().scaled(size), centre)


## A gable roof whose ridge runs along the side, so its slopes face the plate and away.
## PrismMesh's triangle is in its own xy and its ridge runs along its z: scale it in that frame
## (x across the ridge = the house's depth, z along it = the house's width), then turn it.
func _roof_xf(side: String, centre: Vector3, w: float, rh: float, depth: float) -> Transform3D:
	var local := Basis.from_scale(Vector3(depth, rh, w))
	if side == "N" or side == "S":
		return Transform3D(Basis(Vector3.UP, PI * 0.5) * local, centre)
	return Transform3D(local, centre)


## A window pane on the face toward the plate.
func _pane_xf(side: String, at: Vector3) -> Transform3D:
	var yaw := 0.0
	if side == "N":
		yaw = 0.0
	elif side == "S":
		yaw = PI
	elif side == "E":
		yaw = PI * 0.5
	else:
		yaw = -PI * 0.5
	return Transform3D(Basis(Vector3.UP, yaw), at)


func _mm(mesh: Mesh, xfs: Array[Transform3D], cols: Array[Color]) -> MultiMesh:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = not cols.is_empty()
	mm.mesh = mesh
	mm.instance_count = xfs.size()
	for i in range(xfs.size()):
		mm.set_instance_transform(i, xfs[i])
		if mm.use_colors:
			mm.set_instance_color(i, cols[i])
	return mm


func _mmi(nm: String, mm: MultiMesh, mat: Material) -> MultiMeshInstance3D:
	var mmi := MultiMeshInstance3D.new()
	mmi.name = nm
	mmi.multimesh = mm
	mmi.material_override = mat
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mmi.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	return mmi


func _mesh(nm: String, mesh: Mesh, mat: Material, at: Vector3) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = nm
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = at
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	return mi
