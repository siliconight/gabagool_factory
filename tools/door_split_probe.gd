extends Node
## Door-split probe: wall meshes whose extent TERMINATES inside a doorway's
## aperture in a RUNNING scene -- the built-output half of roadmap 59.
##
## WHY BUILT OUTPUT. layout_lint L18 judges SPEC-authored openings, and the
## library now lints clean -- yet the sighting that opened item 59 (a
## partition's WallEnd standing mid-aperture, lot_demo_001, 2026-08-23) is
## provably not in specs/: zero interior-host findings library-wide. So its
## aperture is emitted downstream of the spec (slot grammar, themed kit,
## greybox segmenting), and only an instrument that reads the tree the level
## actually runs can see it. Same doctrine as mesh_light_census: ask the
## running scene directly.
##
## WHAT IT MEASURES. The composed scene names doorway FRAME pieces, not
## apertures: each opening node carries a Doorway_Jamb_L and Doorway_Jamb_R
## (the first run of this probe matched any *Doorway* mesh and measured 102
## walls sitting FLUSH against jambs -- correct construction read as
## defects; that run is why this version exists). So the aperture is
## DERIVED: for every parent node with a jamb pair, the clear gap between
## the jambs' inner faces is the opening. A visible mesh that is
## WALL-SHAPED relative to it -- thin along the gap axis, long along the
## depth axis, reaching the doorway's plane, overlapping its height -- whose
## thin extent sits strictly INSIDE the clear gap is a wall ending inside a
## doorway: one opening, two squeeze-past channels.
##
## WHAT IT CANNOT SEE, stated: an opening with no jamb pair is invisible
## (the naming is the sensor), and a wall ending flush AT a jamb face is
## correct construction, not reported. It reports measurements and stops;
## whether a finding is generated or authored belongs in the reply, argued
## from the paths it prints.

const MARK_BEGIN := "<<<DOOR_SPLIT_PROBE_JSON"
const MARK_END := "DOOR_SPLIT_PROBE_JSON>>>"

const LEAF_MARGIN := 0.3   # layout_lint.LEAF_MARGIN, the same rule's number
const THIN_MAX := 0.8      # a wall is thin across the aperture's width axis
const LONG_MIN := 0.8      # ...and long along the depth axis
const HEIGHT_MIN := 0.3    # must share this much vertical extent with the door
const DEPTH_PAD := 0.6     # how far past the frame a meeting wall may sit


func _ready() -> void:
	var frames: int = int(ProjectSettings.get_setting(
		"door_split_probe/settle_frames", 5))
	for _i in range(frames):
		await get_tree().process_frame

	var scene: Node = get_tree().current_scene
	if scene == null:
		_emit({"error": "current_scene is null"})
		return

	var jambs_by_parent := {}
	var meshes: Array = []
	for n in scene.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if mi.mesh == null or not mi.is_visible_in_tree():
			continue
		var aabb: AABB = mi.global_transform * mi.get_aabb()
		var rec := {"node": mi, "aabb": aabb,
					"path": String(scene.get_path_to(mi))}
		if String(mi.name).contains("Doorway_Jamb"):
			var par: Node = mi.get_parent()
			if not jambs_by_parent.has(par):
				jambs_by_parent[par] = []
			jambs_by_parent[par].append(rec)
		if not String(mi.name).contains("Doorway"):
			meshes.append(rec)   # jambs/headers/leaves are frame, not walls

	# Derive one aperture per jamb PAIR: the clear gap between inner faces.
	var apertures: Array = []
	for par in jambs_by_parent:
		var js: Array = jambs_by_parent[par]
		if js.size() < 2:
			continue
		var a0: AABB = js[0]["aabb"]
		var a1: AABB = js[1]["aabb"]
		# Gap axis = the horizontal axis along which the two jambs stand
		# apart; the other horizontal axis is the wall-thickness (depth).
		var dx: float = absf(a1.get_center().x - a0.get_center().x)
		var dz: float = absf(a1.get_center().z - a0.get_center().z)
		var wa := 0 if dx >= dz else 2
		var pa := 2 if wa == 0 else 0
		var lo_j: AABB = a0 if a0.get_center()[wa] <= a1.get_center()[wa] else a1
		var hi_j: AABB = a1 if lo_j == a0 else a0
		var gap_lo: float = lo_j.position[wa] + lo_j.size[wa]
		var gap_hi: float = hi_j.position[wa]
		if gap_hi - gap_lo < 0.4:
			continue   # jambs touching or crossing: not a walkable aperture
		apertures.append({
			"node": par,
			"path": String(scene.get_path_to(par)),
			"wa": wa, "pa": pa,
			"gap_lo": gap_lo, "gap_hi": gap_hi,
			"y_lo": minf(a0.position.y, a1.position.y),
			"y_hi": maxf(a0.position.y + a0.size.y, a1.position.y + a1.size.y),
			"depth_lo": minf(a0.position[pa], a1.position[pa]) - DEPTH_PAD,
			"depth_hi": maxf(a0.position[pa] + a0.size[pa],
							a1.position[pa] + a1.size[pa]) + DEPTH_PAD,
			"center": Vector3((a0.get_center() + a1.get_center()) / 2.0),
		})

	var findings: Array = []
	var groups := {}
	for d in apertures:
		var wa: int = d["wa"]
		var pa: int = d["pa"]
		var par: Node = d["node"]
		for m in meshes:
			if par.is_ancestor_of(m["node"]):
				continue   # the opening's own frame/leaf hardware
			var ma: AABB = m["aabb"]
			var ylo: float = maxf(ma.position.y, d["y_lo"])
			var yhi: float = minf(ma.position.y + ma.size.y, d["y_hi"])
			if yhi - ylo < HEIGHT_MIN:
				continue
			if ma.size[wa] > THIN_MAX or ma.size[pa] < LONG_MIN:
				continue
			if (ma.position[pa] > d["depth_hi"]
					or ma.position[pa] + ma.size[pa] < d["depth_lo"]):
				continue
			# Thin extent strictly INSIDE the clear gap: a wall end standing
			# in the doorway. Flush-at-jamb (the first run's 102 false
			# positives) sits outside the gap and never enters.
			var mlo: float = ma.position[wa]
			var mhi: float = mlo + ma.size[wa]
			if mlo < d["gap_lo"] + 0.02 or mhi > d["gap_hi"] - 0.02:
				continue
			var center: float = (d["gap_lo"] + d["gap_hi"]) / 2.0
			var c3: Vector3 = d["center"]
			findings.append({
				"doorway": d["path"],
				"doorway_pos": [snappedf(c3.x, 0.1), snappedf(c3.y, 0.1),
								snappedf(c3.z, 0.1)],
				"span_width": snappedf(d["gap_hi"] - d["gap_lo"], 0.01),
				"mesh": m["path"],
				"offset_from_center": snappedf((mlo + mhi) / 2.0 - center, 0.01),
			})
			var parts: PackedStringArray = String(m["path"]).split("/")
			var key: String = parts[0]
			for i in range(1, mini(3, parts.size())):
				key += "/" + parts[i]
			groups[key] = int(groups.get(key, 0)) + 1

	_emit({
		"scene": String(scene.name),
		"settle_frames": frames,
		"engine": String(Engine.get_version_info().get("string", "")),
		"doorways": apertures.size(),
		"meshes_considered": meshes.size(),
		"split_doorways": findings.size(),
		"findings": findings,
		"offender_groups": groups,
	})


func _emit(report: Dictionary) -> void:
	print(MARK_BEGIN)
	print(JSON.stringify(report, "  "))
	print(MARK_END)
	get_tree().quit()
