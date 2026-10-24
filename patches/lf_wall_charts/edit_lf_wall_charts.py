"""Level Factory 0.240.0 on a CLONE (<repo>): a wall's run is one lightmap chart, not one a module (the walker's walk
of cold run 9386, finding 2, and their call: "i think we want the look of baking but where we try to not get those
bands"). Anchored; refuses on a miss.

    python edit_lf_wall_charts.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("assets/godot/merge_buildings.gd", [
    ('''## Godot's import default for `meshes/lightmap_texel_size`, as `merge_empties.gd` has it.
const TEXEL_M := 0.2''',
     '''## Godot's import default for `meshes/lightmap_texel_size`, as `merge_empties.gd` has it.
const TEXEL_M := 0.2
## ONE CHART A WALL RUN (0.240.0). The walker, walking cold run 9386, of bands down a back room's walls -- and then:
## "i think we want the look of baking but where we try to not get those bands". Measured on cold run 9389's
## pharmacy (the factory's `docs/findings/walk_2026-10-23_9386/seams/`): `lightmap_unwrap` on a cell's mesh as built
## made a chart of every 2 m wall module, because modules merged side by side share no vertices; their charts landed
## apart in the lightmap, and the step across a module joint was twice the step mid-module. So the cell's mesh is
## unwrapped through a PROXY whose corners sharing a position and a normal are welded -- a wall's plane, run end to
## end, is one connected surface and one chart -- and the proxy's UV2 is carried back corner by corner
## (`_welded_unwrap`). Proved on that mesh before it shipped: 4 charts on the wall to 2 (its door splits it), every
## proxy corner within a micrometre of the corner it was carried to. Where the carry cannot be trusted -- the proxy's
## corners out of order, an attribute it does not carry -- the plain unwrap stands and the report counts it
## (`unwrapped_plain`). WELD_M and WELD_NORMAL are the keys' resolutions: a millimetre's tenth and a thousandth.
const WELD_M := 0.0001
const WELD_NORMAL := 0.001'''),
    ('''		if am.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) == OK:
			row["unwrapped"] = int(row["unwrapped"]) + 1
		var mesh_path: String = "%s/r%d.res" % [dir, k]''',
     '''		var welded: ArrayMesh = _welded_unwrap(am)
		if welded != null:
			if src != null:
				welded.surface_set_material(0, am.surface_get_material(0))
			am = welded
			row["unwrapped"] = int(row["unwrapped"]) + 1
		elif am.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) == OK:
			row["unwrapped"] = int(row["unwrapped"]) + 1
			row["unwrapped_plain"] = int(row.get("unwrapped_plain", 0)) + 1
		var mesh_path: String = "%s/r%d.res" % [dir, k]'''),
    ('''func _cannot_carry(n: Node, child: Node) -> String:''',
     '''## A one-surface mesh unwrapped for its lightmap through a WELDED PROXY (ONE CHART A WALL RUN, at `WELD_M`): its
## corners sharing a position and a normal made one vertex, the proxy unwrapped at `TEXEL_M`, its UV2 carried back to
## the original corners in order, then the corners indexed again. Null when the carry cannot be trusted -- more than one
## surface, an attribute this does not carry (bones, weights, custom), the proxy not unwrapping, or its output not
## keeping the corners' order and positions -- and the caller unwraps as before.
func _welded_unwrap(mesh: ArrayMesh) -> ArrayMesh:
	if mesh.get_surface_count() != 1:
		return null
	var arr: Array = mesh.surface_get_arrays(0)
	for a in [Mesh.ARRAY_BONES, Mesh.ARRAY_WEIGHTS, Mesh.ARRAY_CUSTOM0, Mesh.ARRAY_CUSTOM1, Mesh.ARRAY_CUSTOM2,
			Mesh.ARRAY_CUSTOM3]:
		if arr[a] != null:
			return null
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	if arr[Mesh.ARRAY_NORMAL] == null:
		return null
	var norms: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
	var idx: PackedInt32Array = PackedInt32Array()
	if arr[Mesh.ARRAY_INDEX] != null:
		idx = arr[Mesh.ARRAY_INDEX]
	else:
		for i in verts.size():
			idx.append(i)
	var key_of := {}
	var pv := PackedVector3Array()
	var pn := PackedVector3Array()
	var pidx := PackedInt32Array()
	for i in idx:
		var v: Vector3 = verts[i]
		var nv: Vector3 = norms[i]
		var key := "%d,%d,%d|%d,%d,%d" % [roundi(v.x / WELD_M), roundi(v.y / WELD_M), roundi(v.z / WELD_M),
			roundi(nv.x / WELD_NORMAL), roundi(nv.y / WELD_NORMAL), roundi(nv.z / WELD_NORMAL)]
		if not key_of.has(key):
			key_of[key] = pv.size()
			pv.append(v)
			pn.append(nv)
		pidx.append(int(key_of[key]))
	var proxy := ArrayMesh.new()
	var pa: Array = []
	pa.resize(Mesh.ARRAY_MAX)
	pa[Mesh.ARRAY_VERTEX] = pv
	pa[Mesh.ARRAY_NORMAL] = pn
	pa[Mesh.ARRAY_INDEX] = pidx
	proxy.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, pa)
	if proxy.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) != OK:
		return null
	var out: Array = proxy.surface_get_arrays(0)
	var ov: PackedVector3Array = out[Mesh.ARRAY_VERTEX]
	var ouv2: PackedVector2Array = out[Mesh.ARRAY_TEX_UV2]
	var oidx: PackedInt32Array = PackedInt32Array()
	if out[Mesh.ARRAY_INDEX] != null:
		oidx = out[Mesh.ARRAY_INDEX]
	else:
		for i in ov.size():
			oidx.append(i)
	if oidx.size() != idx.size():
		return null
	for c in idx.size():
		if (ov[oidx[c]] - verts[idx[c]]).length() > WELD_M:
			return null
	# every corner its own vertex -- the original's attributes and the proxy's UV2 -- then indexed again
	var ra: Array = []
	ra.resize(Mesh.ARRAY_MAX)
	var keep: Array = [Mesh.ARRAY_VERTEX, Mesh.ARRAY_NORMAL, Mesh.ARRAY_TANGENT, Mesh.ARRAY_COLOR, Mesh.ARRAY_TEX_UV]
	for a in keep:
		if arr[a] == null:
			continue
		var width: int = 4 if a == Mesh.ARRAY_TANGENT else 1
		var src = arr[a]
		var dst = src.duplicate()
		dst.resize(idx.size() * width)
		for c in idx.size():
			for w in width:
				dst[c * width + w] = src[idx[c] * width + w]
		ra[a] = dst
	var u2 := PackedVector2Array()
	u2.resize(idx.size())
	for c in idx.size():
		u2[c] = ouv2[oidx[c]]
	ra[Mesh.ARRAY_TEX_UV2] = u2
	var st := SurfaceTool.new()
	st.create_from_arrays(ra, Mesh.PRIMITIVE_TRIANGLES)
	st.index()
	return st.commit()


func _cannot_carry(n: Node, child: Node) -> String:'''),
])

TEST = """


def test_a_cell_s_mesh_is_unwrapped_through_a_welded_proxy():
    \"\"\"0.240.0, the walker's walk of cold run 9386, finding 2: a chart a 2 m module put bands down the walls. A
    cell's mesh is unwrapped through a proxy whose corners sharing a position and a normal are welded, its UV2 carried
    back in order and checked corner by corner; the plain unwrap is kept, and counted, where the carry cannot be
    trusted. FAILS ON 0.239.0.\"\"\"
    text = M.MERGE_SCRIPT.read_text(encoding="utf-8")
    body = _func(text, "_welded_unwrap")
    assert "proxy.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M)" in body
    assert "if (ov[oidx[c]] - verts[idx[c]]).length() > WELD_M:" in body and "return null" in body
    assert "Mesh.ARRAY_BONES" in body and "get_surface_count() != 1" in body
    assert "st.index()" in body
    assert re.search(r"^const WELD_M := 0\\.0001$", text, re.M)
    assert re.search(r"^const WELD_NORMAL := 0\\.001$", text, re.M)
    assert "var welded: ArrayMesh = _welded_unwrap(am)" in text
    assert 'row["unwrapped_plain"]' in text
"""
tp = R / "tests" / "unit" / "test_merge_buildings.py"
traw = tp.read_bytes()
assert b"\r\n" not in traw and traw.endswith(b"\n") and b"_welded_unwrap" not in traw
tp.write_bytes(traw.rstrip(b"\n") + b"\n" + TEST.encode("utf-8"))
print("merge_buildings: welded unwrap for a cell's mesh; test")
