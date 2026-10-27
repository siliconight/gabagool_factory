"""Edit a Lux clone for 0.80.0: a baked fluorescent row can bake with a longer range than it claims live -- a row's
`bake_reach` (the marker's `lux_bake_reach`) derives the rig's `bake_range`, and `stretch_bake_ranges` /
`restore_bake_ranges` lend it to the lamps only while a lightmap bakes. Run from the clone's root. Asserts every anchor
once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("addons/lux/resources/lux_light_rig.gd", [
('''@export_enum("Realtime (engine default)", "Static (baked)", "Dynamic (indirect only)")
var bake_mode: int = 0
''',
'''@export_enum("Realtime (engine default)", "Static (baked)", "Dynamic (indirect only)")
var bake_mode: int = 0
## The range a STATIC lamp bakes with, when that is longer than the
## `light_range` it claims live (0.80.0); 0 bakes at `light_range`. A lamp's
## range is also the realtime claim it makes on every dynamic object it
## reaches, so the live range stays short and the lightmap is lent this one
## only while it bakes (`LuxLightLoader.stretch_bake_ranges`). 0 is not
## saved, so a scene with no such row is byte-identical.
@export_range(0.0, 60.0) var bake_range: float = 0.0
'''),
])

edit("addons/lux/runtime/lux_fixture_spawner.gd", [
('''		# `lux_reach` (Zoo >= 1.21.0) the same way: a row facing a
		# storefront carries it and nothing else does (0.56.0).
		var rig := LuxLightLoader.rig_for_anchor({"type": t,
			"id": "Spawned_" + String(mk.name).trim_prefix(MARKER_PREFIX).trim_prefix("_"),
			"drop": float(marker_payload(mk, "lux_drop", 0.0)),
			"reach": float(marker_payload(mk, "lux_reach", 0.0))})''',
'''		# `lux_reach` (Zoo >= 1.21.0) the same way: a row facing a
		# storefront carries it and nothing else does (0.56.0). And
		# `lux_bake_reach` (Zoo >= 1.134.0), the floor a baked row must
		# reach in the lightmap (0.80.0).
		var rig := LuxLightLoader.rig_for_anchor({"type": t,
			"id": "Spawned_" + String(mk.name).trim_prefix(MARKER_PREFIX).trim_prefix("_"),
			"drop": float(marker_payload(mk, "lux_drop", 0.0)),
			"reach": float(marker_payload(mk, "lux_reach", 0.0)),
			"bake_reach": float(marker_payload(mk, "lux_bake_reach", 0.0))})'''),
])

edit("addons/lux/runtime/lux_light_loader.gd", [
('''			var drop := float(a.get("drop", 0.0))
			r.light_range = fluorescent_range(drop, float(a.get("reach", 0.0)))
''',
'''			var drop := float(a.get("drop", 0.0))
			r.light_range = fluorescent_range(drop, float(a.get("reach", 0.0)))
			# AND WHAT IT BAKES WITH (0.80.0): a row that carries `bake_reach`
			# lends the lightmap a longer range than it claims live
			# (`fluorescent_bake_range`, `stretch_bake_ranges`).
			var bake_reach := float(a.get("bake_reach", 0.0))
			if bake_reach > 0.0:
				r.bake_range = fluorescent_bake_range(drop, bake_reach, r.light_range)
'''),
('''## The fluorescent row's range rule (see its branch), as a function so the''',
'''## THE RANGE A BAKED ROW LENDS ITS LIGHTMAP (0.80.0): `hypot(drop,
## bake_reach) + 0.75`, never under the live ``light_range``, and NOT under
## `fluorescent_range`'s clamp -- that clamp prices the realtime claim each
## lamp makes on every mesh it reaches, which a static lamp's lightmap does
## not make. Deli Counter (>= 0.279.0) stamps `bake_reach` as a row's lamp
## spacing, so the light reaches the floor under the next lamp along.
##
## MEASURED on the walker's Restaurant Row level (seed 9205), the supermarket's
## 50 rows at 4.85 m live, re-baked with the range scaled
## (the factory's docs/findings/black_gondola_ends/range_arm.py): the frame
## toward the coolers 38.5 -> 61.5 mean at x 1.6, the gondolas' black end
## (1, 1, 7) -> (34, 32, 25). This rule gives 7.61 m there (drop 4.1, spacing
## 5.5), x 1.57.
static func fluorescent_bake_range(drop: float, bake_reach: float, live: float) -> float:
	if drop <= 0.0 or bake_reach <= 0.0:
		return 0.0
	return maxf(sqrt(drop * drop + bake_reach * bake_reach) + 0.75, live)


## Lend every static fluorescent lamp under ``scene_root`` its rig's
## `bake_range`, for a lightmap bake (0.80.0). Returns what to give back --
## ``[[lamp, live range], ...]`` -- for `restore_bake_ranges`, which the
## baker calls before it saves: the saved scene keeps the live range, and a
## loaded rig rebuilds its lamps from `light_range` in any case. A rig that
## is not static, or carries no `bake_range`, is untouched.
static func stretch_bake_ranges(scene_root: Node) -> Array:
	var lent: Array = []
	if scene_root == null:
		return lent
	for n in scene_root.find_children("*", "Node3D", true, false):
		if not (n is LuxFluorescentRig):
			continue
		var rig: LuxLightRig = (n as LuxFluorescentRig).rig
		if rig == null or rig.bake_mode != 1 or rig.bake_range <= rig.light_range:
			continue
		for c in n.get_children():
			if c is SpotLight3D:
				lent.append([c, (c as SpotLight3D).spot_range])
				(c as SpotLight3D).spot_range = rig.bake_range
			elif c is OmniLight3D:
				lent.append([c, (c as OmniLight3D).omni_range])
				(c as OmniLight3D).omni_range = rig.bake_range
	return lent


## Give back what `stretch_bake_ranges` lent. Returns how many lamps.
static func restore_bake_ranges(lent: Array) -> int:
	var n := 0
	for e in lent:
		var l: Variant = e[0]
		if not is_instance_valid(l):
			continue
		if l is SpotLight3D:
			(l as SpotLight3D).spot_range = float(e[1])
		elif l is OmniLight3D:
			(l as OmniLight3D).omni_range = float(e[1])
		n += 1
	return n


## The fluorescent row's range rule (see its branch), as a function so the'''),
])
