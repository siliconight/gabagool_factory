"""An occluder must not cap an opening it cannot actually block.

WALKED 2026-09-23, on cold run 9072's package. The walker turned occlusion off
and a basement stairwell appeared that had not been visible with it on, along
with walls that came and went over 0.7 m of movement. Measured A/B, in a
window (headless returns 0 for every rendering counter -- the first attempt at
this measurement produced 0 objects at every station with the flag both ways):

    station      yaw   ON        OFF       culled
    A x3.4       180   940 obj   940 obj      0
    B x4.1       180   469 obj   930 obj    461
    C x6.8        90   220 obj  2430 obj   2210
    D stair       90   894 obj  2532 obj   1638

THE CAUSE IS THE PROXY, and it is the defect CLAUDE.md names as recurring: a
cheap observable standing in for an expensive truth with nothing recording the
substitution. `_run` classifies `wall_ roof_ floor_ ceiling_` as solid, takes
the node's AABB, shrinks it 2 cm and emits that box. The AABB stands in for
"what this module blocks". For a floor plate with a stairwell cut through it
the AABB is the whole room and the mesh is not:

    floor_main_floor   x -65.98..-30.02   y 0.00..0.02   z -10.98..1.98

A 36 x 13 m horizontal box, 2 cm thick, spanning the stair opening. Stand on
that floor, look down the stair, and everything below is behind the box.

THE THRESHOLD IS DERIVED, not chosen, and both bounds were measured on that
package before this was written:

    smallest opening the pipeline cuts    1.10 x 1.30 m ladder hole = 1.43 m2
    measured deficit of every solid       0.000000 m2, over 381 modules
    measured deficit of the 11 holed      12.74 .. 36.00 m2

0.25 m2 sits 5.7x below the smallest real opening and infinitely above a noise
floor that is exactly zero. A RATIO would have been the wrong instrument: that
same 1.43 m2 hole in a 36 x 13 m floor is 0.3% of the area, so any tolerant
ratio misses precisely the case this was built for. Absolute area is
scale-free.

WHAT THIS COSTS AND WHAT THE EXPENSIVE VERSION WOULD BUY. 11 of 392 occluders
are dropped (2.8%), all horizontal plates, which occlude less than the 355
walls that do the real work. The expensive version emits the plate's actual
faces as an `ArrayOccluder3D` so the solid 97% of a holed floor still occludes;
it costs triangles in the occlusion rasteriser and is worth measuring when
there is a reason to. Recorded rather than closed.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "assets" / "godot" / "bake_occluders.gd"

# ---------------------------------------------------------------- anchor 1
A1 = '''var _counts := {
	"solid": 0, "porous": 0, "glass": 0, "filler": 0, "other": 0,
	"no_bounds": 0, "too_small": 0,
}
'''

N1 = '''#: An occluder must be a SUBSET of opaque geometry. A module whose mesh
#: leaves more than this much of its own bounding box uncovered, on the axis
#: it is thinnest in, has an opening in it and its box would cap that opening.
#:
#: DERIVED, and both bounds measured on cold run 9072's package before this
#: number was written. The smallest opening this pipeline cuts is a ladder
#: hole, `ladder_geom.through_hole` at 1.10 x 1.30 m = 1.43 m2. The measured
#: deficit of every module WITHOUT an opening was 0.000000 m2, over 381 of
#: them; the 11 with one measured 12.74 to 36.00 m2. So this sits 5.7x below
#: the smallest real opening and infinitely above the noise.
#:
#: AREA, NOT A RATIO, and that is the whole point. A 1.43 m2 hole in a
#: 36 x 13 m room floor is 0.3% of its area -- a ratio tolerant enough to
#: survive any mesh would miss exactly the case this exists for. Absolute
#: area does not care how big the room is.
const HOLE_MIN_M2 := 0.25

var _counts := {
	"solid": 0, "porous": 0, "glass": 0, "filler": 0, "other": 0,
	"no_bounds": 0, "too_small": 0, "holed": 0,
}
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''func _r(v: float) -> float:
	return snappedf(v, pow(10.0, -ROUND_DP))
'''

N2 = '''## How much of its own bounding box the module's mesh leaves uncovered, in m2,
## on `axis` (0=X, 1=Y, 2=Z). Sums the projected area of every face pointing
## along +axis and subtracts it from the box's cross-section there.
##
## Faces pointing the OTHER way are not counted: a plate has a top and a
## bottom and counting both would read 2.0 and hide a hole in either.
func _uncovered_m2(n: Node3D, box: AABB, axis: int) -> float:
	var inv: Transform3D = n.global_transform.affine_inverse()
	var nodes: Array = []
	_walk(n, nodes)
	var area: float = 0.0
	for x in nodes:
		var mi: MeshInstance3D = x as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = inv * mi.global_transform
		for s in range(mi.mesh.get_surface_count()):
			var arr: Array = mi.mesh.surface_get_arrays(s)
			if arr.is_empty():
				continue
			var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
			var nt: int = idx.size() / 3 if idx.size() > 0 else v.size() / 3
			for t in range(nt):
				var p0: Vector3
				var p1: Vector3
				var p2: Vector3
				if idx.size() > 0:
					p0 = xf * v[idx[t * 3]]
					p1 = xf * v[idx[t * 3 + 1]]
					p2 = xf * v[idx[t * 3 + 2]]
				else:
					p0 = xf * v[t * 3]
					p1 = xf * v[t * 3 + 1]
					p2 = xf * v[t * 3 + 2]
				var nrm: Vector3 = (p1 - p0).cross(p2 - p0)
				var comp: float = nrm.y
				if axis == 0:
					comp = nrm.x
				elif axis == 2:
					comp = nrm.z
				if comp > 0.0:
					area += comp * 0.5
	var cross: float = box.size.x * box.size.z
	if axis == 0:
		cross = box.size.y * box.size.z
	elif axis == 2:
		cross = box.size.x * box.size.y
	return cross - area


## The axis the module is thinnest in -- the one its box would occlude across.
func _thin_axis(box: AABB) -> int:
	if box.size.y <= box.size.x and box.size.y <= box.size.z:
		return 1
	if box.size.z <= box.size.x and box.size.z <= box.size.y:
		return 2
	return 0


func _r(v: float) -> float:
	return snappedf(v, pow(10.0, -ROUND_DP))
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''		if maxf(box.size.x, maxf(box.size.y, box.size.z)) < MIN_EXTENT_M:
			_counts["too_small"] = int(_counts["too_small"]) + 1
			continue
'''

N3 = '''		if maxf(box.size.x, maxf(box.size.y, box.size.z)) < MIN_EXTENT_M:
			_counts["too_small"] = int(_counts["too_small"]) + 1
			continue
		# THE BOX IS NOT THE MESH when the mesh has an opening cut in it, and
		# an occluder over an opening caps what can be seen through it. See
		# `HOLE_MIN_M2` for the measurement that set the bound and for the
		# basement this shipped without.
		var axis: int = _thin_axis(box)
		var uncovered: float = _uncovered_m2(n, box, axis)
		if uncovered > HOLE_MIN_M2:
			_counts["holed"] = int(_counts["holed"]) + 1
			continue
'''

# ---------------------------------------------------------------- anchor 4
A4 = '''	print("[occluders] measured=%d solid=%d porous=%d glass=%d filler=%d other=%d"
		% [rows.size(), int(_counts["solid"]), int(_counts["porous"]),
		   int(_counts["glass"]), int(_counts["filler"]), int(_counts["other"])])
'''

N4 = '''	print("[occluders] measured=%d solid=%d porous=%d glass=%d filler=%d other=%d holed=%d"
		% [rows.size(), int(_counts["solid"]), int(_counts["porous"]),
		   int(_counts["glass"]), int(_counts["filler"]), int(_counts["other"]),
		   int(_counts["holed"])])
'''

EDITS = ((A1, N1), (A2, N2), (A3, N3), (A4, N4))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
