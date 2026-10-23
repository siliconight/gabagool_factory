extends Node
## Walk copy -- DEV ONLY ladder climb volumes.
## ----------------------------------------------------------------------------
## The walker, 2026-09-13, on a walk_export copy: "I can't get up this ladder,
## we have made successful ladders in the past." They had -- in Lot's own walk
## scene, whose `_ladder_volume_nodes` builds an Area3D in group "ladder" for
## each gameplay ladder marker, which is what `lot_player.gd` climbs. The
## exported PACKAGE carries only the markers (a Node3D `LADDER_n` in group
## "ladder" inside each building scene) because building the volume is the
## consumer's job, and `walk_export.py` never did it. So every ladder in every
## walk copy was scenery.
##
## This does Lot's half at runtime, in the walk copy only.
##
## THE PACKAGE'S OWN VOLUME FIRST (2026-10-23). Deli Counter's packages carry a
## climb Area3D for every ladder -- `Ladders/Ladder_<id>`, groups
## "ladder_area3d"/"dc_ladder", at the ladder's base, spanning the full climb
## plus a metre (`deli_counter/portable_building.py`) -- and the walk player
## climbs group "ladder", so it stood unused. Each is put in "ladder" here, and
## a marker with one at its base gets nothing more. The walker, cold run 9383:
## "im stuck trying to get up the ladder to the roof" -- deli_a03's roof ladder
## climbs 6.6 m and the volume this file built for it was 4.0 m tall; 17 roof
## ladders in the library could not be climbed in a walk copy
## (`docs/findings/walk_2026-10-23_deli/`).
##
## The fallback, for a ladder MARKER (a Node3D in group "ladder" that is not an
## Area3D) with no package volume at its base: a climb Area3D from the marker up
## to the nearest "hatch" marker directly above it, or 3.0 m when there is
## none. (This header said Deli Counter emits a hatch marker atop every roof and
## slab ladder; it emits one only for a hatch link -- which is why the fallback
## ran on a roof ladder at 3.0 m.) Sizing mirrors `lot._ladder_volume_nodes`: a
## 1.3 m square footprint so a building's rotation cannot turn the volume
## edge-on, and a 1 m dismount lip over the top. Never in the package; the
## package is content.

const DEFAULT_CLIMB := 3.0
const FOOTPRINT := 1.3
const DISMOUNT_LIP := 1.0
const HATCH_XZ_TOLERANCE := 1.0
## How near a package volume's origin must stand to a marker, across and up, to be that marker's ladder: both sit at
## the ladder's base anchor, so they coincide; a metre across and half a metre up allow for rounding.
const PACKAGE_XZ_TOLERANCE := 1.0
const PACKAGE_Y_TOLERANCE := 0.5


func _ready() -> void:
	call_deferred("_build")


func _build() -> void:
	var hatches: Array[Node3D] = []
	for h in get_tree().get_nodes_in_group("hatch"):
		if h is Node3D:
			hatches.append(h as Node3D)
	# the package's own volumes: climbable as they are
	var package_bases: Array[Vector3] = []
	var adopted := 0
	for v in get_tree().get_nodes_in_group("ladder_area3d"):
		if not (v is Area3D):
			continue
		package_bases.append((v as Area3D).global_position)
		if not v.is_in_group("ladder"):
			v.add_to_group("ladder")
			adopted += 1
	var made := 0
	for n in get_tree().get_nodes_in_group("ladder"):
		if n is Area3D or not (n is Node3D):
			continue
		var base: Vector3 = (n as Node3D).global_position
		if _has_package_volume(base, package_bases):
			continue
		var climb := _climb_height(base, hatches)
		var area := Area3D.new()
		area.name = "%s_climb" % n.name
		area.monitoring = true
		area.monitorable = true
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(FOOTPRINT, climb + DISMOUNT_LIP, FOOTPRINT)
		shape.shape = box
		shape.position = Vector3(0.0, (climb + DISMOUNT_LIP) * 0.5, 0.0)
		area.add_child(shape)
		add_child(area)
		area.global_position = base
		area.add_to_group("ladder")
		made += 1
	print("[walk_ladders] %d package ladder volume(s) adopted, %d fallback volume(s) built" % [adopted, made])


func _has_package_volume(base: Vector3, package_bases: Array[Vector3]) -> bool:
	for p in package_bases:
		var dx: float = p.x - base.x
		var dz: float = p.z - base.z
		if sqrt(dx * dx + dz * dz) <= PACKAGE_XZ_TOLERANCE and absf(p.y - base.y) <= PACKAGE_Y_TOLERANCE:
			return true
	return false


func _climb_height(base: Vector3, hatches: Array[Node3D]) -> float:
	var best := -1.0
	for h in hatches:
		var p: Vector3 = h.global_position
		var dx: float = p.x - base.x
		var dz: float = p.z - base.z
		if sqrt(dx * dx + dz * dz) > HATCH_XZ_TOLERANCE:
			continue
		var rise: float = p.y - base.y
		if rise > 0.5 and (best < 0.0 or rise < best):
			best = rise
	return best if best > 0.0 else DEFAULT_CLIMB
