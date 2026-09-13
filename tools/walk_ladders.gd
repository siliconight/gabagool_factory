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
## This does Lot's half at runtime, in the walk copy only: for every ladder
## MARKER (a Node3D in group "ladder" that is not already an Area3D) it adds a
## climb Area3D. The height runs from the marker, which sits at the ladder's
## base, up to the nearest "hatch" marker directly above it -- Deli Counter
## emits one at the top of every roof and slab ladder -- or 3.0 m when there is
## none. Sizing mirrors `lot._ladder_volume_nodes`: a 1.3 m square footprint so
## a building's rotation cannot turn the volume edge-on, and a 1 m dismount lip
## over the top. Never in the package; the package is content.

const DEFAULT_CLIMB := 3.0
const FOOTPRINT := 1.3
const DISMOUNT_LIP := 1.0
const HATCH_XZ_TOLERANCE := 1.0


func _ready() -> void:
	call_deferred("_build")


func _build() -> void:
	var hatches: Array[Node3D] = []
	for h in get_tree().get_nodes_in_group("hatch"):
		if h is Node3D:
			hatches.append(h as Node3D)
	var made := 0
	for n in get_tree().get_nodes_in_group("ladder"):
		if n is Area3D or not (n is Node3D):
			continue
		var base: Vector3 = (n as Node3D).global_position
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
	print("[walk_ladders] %d ladder climb volume(s)" % made)


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
