extends SceneTree
## Finding 2's cure, proved on the real mesh before it goes into Level Factory: one merged mesh unwrapped two ways --
## as the merge does it (`lightmap_unwrap` on the mesh as built) and through a WELDED PROXY (vertices sharing a position
## and a normal made one, unwrapped, its UV2 carried back corner by corner). For each, the lightmap islands lying on one
## plane of constant Z (building-local metres), and for the welded one whether every proxy corner's position matches
## the original corner it is carried to. Headless; saves nothing. Measurements only.
##
##     godot --headless --path <walk copy> --script res://welded_unwrap.gd -- <res path> <plane_z>

const TEXEL_M := 0.2
const TOL := 0.25


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var path: String = args[0]
	var plane_z: float = float(args[1])
	var src := load(path) as ArrayMesh
	if src == null or src.get_surface_count() != 1:
		print("REFUSED: %s is not a one-surface ArrayMesh" % path)
		quit(2)
		return
	var arr: Array = src.surface_get_arrays(0)
	# the mesh as the merge built it, before its unwrap: strip the UV2 it carries
	var bare := ArrayMesh.new()
	var a2: Array = arr.duplicate()
	a2[Mesh.ARRAY_TEX_UV2] = null
	bare.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, a2)
	var plain := bare.duplicate() as ArrayMesh
	var e1 := plain.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M)
	print("PLAIN unwrap %d  islands on plane: %d" % [e1, _islands(plain, plane_z)])
	var welded := _welded_unwrap(bare)
	if welded == null:
		print("WELDED refused (see above)")
	else:
		print("WELDED islands on plane: %d" % _islands(welded, plane_z))
	quit(0)


## The cure: a proxy of positions and normals with shared corners welded, unwrapped; its UV2 carried back to the
## original corners triangle by triangle. Null, and said, when the proxy's output does not keep the triangles' order.
func _welded_unwrap(mesh: ArrayMesh) -> ArrayMesh:
	var arr: Array = mesh.surface_get_arrays(0)
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var norms: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
	var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	if idx.size() == 0:
		for i in verts.size():
			idx.append(i)
	var key_of := {}
	var pv := PackedVector3Array()
	var pn := PackedVector3Array()
	var pidx := PackedInt32Array()
	for i in idx:
		var v: Vector3 = verts[i]
		var n: Vector3 = norms[i]
		var key := "%d,%d,%d|%d,%d,%d" % [roundi(v.x * 10000.0), roundi(v.y * 10000.0), roundi(v.z * 10000.0),
			roundi(n.x * 1000.0), roundi(n.y * 1000.0), roundi(n.z * 1000.0)]
		if not key_of.has(key):
			key_of[key] = pv.size()
			pv.append(v)
			pn.append(n)
		pidx.append(int(key_of[key]))
	var proxy := ArrayMesh.new()
	var pa: Array = []
	pa.resize(Mesh.ARRAY_MAX)
	pa[Mesh.ARRAY_VERTEX] = pv
	pa[Mesh.ARRAY_NORMAL] = pn
	pa[Mesh.ARRAY_INDEX] = pidx
	proxy.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, pa)
	if proxy.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) != OK:
		print("WELDED: the proxy did not unwrap")
		return null
	var out: Array = proxy.surface_get_arrays(0)
	var ov: PackedVector3Array = out[Mesh.ARRAY_VERTEX]
	var ouv2: PackedVector2Array = out[Mesh.ARRAY_TEX_UV2]
	var oidx: PackedInt32Array = out[Mesh.ARRAY_INDEX] if out[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	if oidx.size() == 0:
		for i in ov.size():
			oidx.append(i)
	print("WELDED proxy: %d corners in, %d out; %d vertices welded from %d" % [idx.size(), oidx.size(), pv.size(), idx.size()])
	if oidx.size() != idx.size():
		print("WELDED: the proxy's output has %d corners, not %d" % [oidx.size(), idx.size()])
		return null
	var worst := 0.0
	for c in idx.size():
		worst = maxf(worst, (ov[oidx[c]] - verts[idx[c]]).length())
	print("WELDED: worst corner mismatch %.6f m (triangle order kept when ~0)" % worst)
	if worst > 1e-4:
		return null
	# carried back: every corner its own vertex with the original's attributes and the proxy's UV2
	var res := ArrayMesh.new()
	var ra: Array = []
	ra.resize(Mesh.ARRAY_MAX)
	var rv := PackedVector3Array()
	var rn := PackedVector3Array()
	var ruv := PackedVector2Array()
	var ruv2 := PackedVector2Array()
	var uv: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV] if arr[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
	for c in idx.size():
		rv.append(verts[idx[c]])
		rn.append(norms[idx[c]])
		if uv.size() > 0:
			ruv.append(uv[idx[c]])
		ruv2.append(ouv2[oidx[c]])
	ra[Mesh.ARRAY_VERTEX] = rv
	ra[Mesh.ARRAY_NORMAL] = rn
	if ruv.size() > 0:
		ra[Mesh.ARRAY_TEX_UV] = ruv
	ra[Mesh.ARRAY_TEX_UV2] = ruv2
	res.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, ra)
	return res


func _islands(mesh: ArrayMesh, plane_z: float) -> int:
	var arr: Array = mesh.surface_get_arrays(0)
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var uv2: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV2]
	var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	if idx.size() == 0:
		for i in verts.size():
			idx.append(i)
	# islands by shared UV2 position among the plane's triangles (a chart is connected in UV2 space)
	var parent := {}
	var tri_keys: Array = []
	for t in range(0, idx.size(), 3):
		var a: Vector3 = verts[idx[t]]
		var b: Vector3 = verts[idx[t + 1]]
		var c: Vector3 = verts[idx[t + 2]]
		var n: Vector3 = (b - a).cross(c - a)
		if n.length() < 1e-9 or absf(n.normalized().z) < 0.95:
			continue
		if absf((a.z + b.z + c.z) / 3.0 - plane_z) > TOL:
			continue
		var ks: Array = []
		for j in 3:
			var u: Vector2 = uv2[idx[t + j]]
			var k := "%d,%d" % [roundi(u.x * 100000.0), roundi(u.y * 100000.0)]
			if not parent.has(k):
				parent[k] = k
			ks.append(k)
		_union(parent, ks[0], ks[1])
		_union(parent, ks[0], ks[2])
		tri_keys.append(ks[0])
	var roots := {}
	for k in tri_keys:
		roots[_find(parent, k)] = true
	return roots.size()


func _find(parent: Dictionary, k: String) -> String:
	var r: String = k
	while String(parent[r]) != r:
		r = String(parent[r])
	return r


func _union(parent: Dictionary, a: String, b: String) -> void:
	var ra := _find(parent, a)
	var rb := _find(parent, b)
	if ra != rb:
		parent[rb] = ra
