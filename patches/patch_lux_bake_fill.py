"""Lux 0.68.0: the rooms' floor, put back in the bake.

    python patch_lux_bake_fill.py

A lightmapped surface takes its light from the lightmap alone, so the room
probes' ambient floor (0.38.0) stopped reaching any wall or floor when Level
Factory started baking, and a corner no lamp reaches baked to black.
`LuxLightLoader.add_bake_fills` lays bake-only fills over every untinted room
probe for a bake to bake and free; `LuxPreset.bake_room_fill` is their
energy. `docs/findings/night_interiors/` has the measurements.

Anchored on, as read 2026-10-07 (both LF):
  lux/addons/lux/resources/lux_preset.gd       23,092 bytes
  lux/addons/lux/runtime/lux_light_loader.gd   88,643 bytes (Lux 0.67.0)
Every anchor must match once; nothing is written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRESET = ROOT / "lux" / "addons" / "lux" / "resources" / "lux_preset.gd"
LOADER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_light_loader.gd"

PRESET_OLD = "@export_range(0.0, 16.0) var fluorescent_energy_scale: float = 1.0\n"
PRESET_NEW = (
    "@export_range(0.0, 16.0) var fluorescent_energy_scale: float = 1.0\n"
    "## THE ROOMS' FLOOR IN A BAKED LEVEL (0.68.0): the energy of each bake-only\n"
    "## fill `LuxLightLoader.add_bake_fills` lays -- the light a room's corners\n"
    "## get that no lamp reaches, which a room probe's ambient gave them until\n"
    "## the light bake made every wall and floor take its light from the\n"
    "## lightmap alone. MEASURED on cold run 9190's restaurant row (Blue Hour),\n"
    "## re-baked, mean luma of 255 over 16 fluorescent rooms and 8 bulb-lit ones:\n"
    "##\n"
    "##     no floor (Lux 0.67.0)     15.7    9.6\n"
    "##     0.025                     39.1   22.8\n"
    "##     the level lit live, before the bake  24.3  17.5\n"
    "##\n"
    "## (`docs/findings/night_interiors/`). A preset that wants darker rooms\n"
    "## lowers it, and 0.0 bakes no floor. A room lit by bare bulbs takes\n"
    "## BAKE_FILL_BULB_SHARE of it. Chosen by eye from the frames, not derived:\n"
    "## the walker's \"enough light to signify the surroundings\" (2026-10-07).\n"
    "## Per time of day is the next step -- a level is set at one of five times\n"
    "## and its preset is the place each one's light lives.\n"
    "@export_range(0.0, 0.2, 0.005) var bake_room_fill: float = 0.025\n"
)

LOADER_OLD = "\treturn probe\n\n\n## Read `path`, replace any previous bake, and spawn a rig per anchor under a\n"
LOADER_NEW = (
    "\treturn probe\n"
    "\n"
    "\n"
    "## THE ROOMS' FLOOR, IN THE BAKE (0.68.0). A lightmapped surface takes its\n"
    "## light from the lightmap alone, so once Level Factory baked (0.131.0, on by\n"
    "## default since 0.144.0) a room probe's ambient -- the floor\n"
    "## ROOM_AMBIENT_DERIVED_ENERGY was put there to be -- reached no wall and no\n"
    "## floor: raised five-fold on cold run 9190's level it moved nothing, and a\n"
    "## corner no lamp reaches baked to black. The bake is baked with the\n"
    "## environment off, which is right for a sealed room and leaves it nothing.\n"
    "##\n"
    "## `add_bake_fills` puts the floor back as light that exists only while the\n"
    "## lightmapper runs: static omnis over every UNTINTED room probe (a tinted\n"
    "## probe is a club room, dark by design -- the walker's dens of sin), which a\n"
    "## bake lays before it bakes and frees before it saves. The container has no\n"
    "## owner, so even a save that forgot to free it cannot keep it, and a level\n"
    "## carries no fill at runtime: nothing to draw, nothing to price. Dynamic\n"
    "## objects see it through the lightmap's own probes.\n"
    "##\n"
    "## FOUR LAYOUTS WERE BAKED ON THAT LEVEL; THE FIRST THREE ARE KEPT HERE AS\n"
    "## REFUTATIONS. Mean luma of 255, 16 fluorescent rooms / 8 bulb-lit rooms:\n"
    "##\n"
    "##     no floor                                     15.7   9.6   85 s\n"
    "##     1 fill a room, centre, 2.3 m, 0.08           32.9  19.4   86 s\n"
    "##     6 m cells, 1.7 m, 0.08 a room split          32.0  28.1  172 s\n"
    "##     8 m cells, the same, bulb rooms half         32.0  18.7  132 s\n"
    "##     6 m cells, 1.7 m, 0.025 each, 9 m, half      39.1  22.8   94 s\n"
    "##\n"
    "## (the last column is the bake's time in the editor). The centre fill hung\n"
    "## a quarter of the storey over the middle -- 2.3 m, where a bare bulb hangs,\n"
    "## at the room's centre, where a row's middle bulb hangs: deli_a01's deli\n"
    "## counter fill stood exactly on its centre bulb's anchor, inside the glass,\n"
    "## and four rooms did not move. A room's energy split between its cells, each\n"
    "## reaching the whole room, left a big room dark: a floor point is lit by the\n"
    "## fills near it, so the split falls as 1/size (the office lobby, 34 x 12 m,\n"
    "## 10.0). A fixed energy a fill, each reaching 1.5 cells and flat inside it,\n"
    "## lights a floor the same whatever the room's size -- about 1.3x under a\n"
    "## fill against the point between four -- and bakes nearly as fast as none.\n"
    "const BAKE_FILL_CONTAINER := \"LuxBakeFill\"\n"
    "## A person's head height over the room's floor: under every ceiling fixture\n"
    "## (a bulb hangs 0.6 m under a 3.2 m storey's ceiling, a tube 0.25 under its\n"
    "## lens). A low room takes 0.6 of its height instead.\n"
    "const BAKE_FILL_HEIGHT_M := 1.7\n"
    "## One fill per cell this wide at most, the room's cells equal.\n"
    "const BAKE_FILL_CELL_M := 6.0\n"
    "## Each fill reaches this many cells, flat inside it (attenuation 0).\n"
    "const BAKE_FILL_REACH_CELLS := 1.5\n"
    "## A room a bare bulb lights keeps this share of the floor: \"keep pendants\n"
    "## moody\" (the walker, 2026-09-28). 22.8 against the fluorescent rooms'\n"
    "## 39.1 on the level above.\n"
    "const BAKE_FILL_BULB_SHARE := 0.5\n"
    "\n"
    "\n"
    "## Lay the bake-only room fills under `scene_root` and return their\n"
    "## container, or null when nothing asks for one. Clears an earlier call's\n"
    "## fill first, always. `energy` is each fill's; negative reads the scene's\n"
    "## LuxRoot preset (`bake_fill_energy`). For a light bake to call before it\n"
    "## bakes and to free before it saves; `scene_root` must be in the tree.\n"
    "static func add_bake_fills(scene_root: Node, energy: float = -1.0) -> Node3D:\n"
    "\tif scene_root == null or not scene_root.is_inside_tree():\n"
    "\t\treturn null\n"
    "\tvar old := scene_root.get_node_or_null(NodePath(BAKE_FILL_CONTAINER))\n"
    "\tif old != null:\n"
    "\t\told.free()\n"
    "\tif energy < 0.0:\n"
    "\t\tenergy = bake_fill_energy(scene_root)\n"
    "\tif energy <= 0.0:\n"
    "\t\treturn null\n"
    "\t# the rooms a bare bulb lights, by where their rigs hang\n"
    "\tvar bulbs: Array[Vector3] = []\n"
    "\tfor n in scene_root.find_children(\"*\", \"Node3D\", true, false):\n"
    "\t\tif n is LuxFluorescentRig and (n as LuxFluorescentRig).rig != null \\\n"
    "\t\t\t\tand String((n as LuxFluorescentRig).rig.rig_name).begins_with(\"Bare Bulb\"):\n"
    "\t\t\tbulbs.append((n as Node3D).global_position)\n"
    "\tvar container: Node3D = null\n"
    "\tfor n in scene_root.find_children(\"*\", \"ReflectionProbe\", true, false):\n"
    "\t\tvar p := n as ReflectionProbe\n"
    "\t\tif not p.interior or p.ambient_mode != ReflectionProbe.AMBIENT_COLOR \\\n"
    "\t\t\t\tor not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR):\n"
    "\t\t\tcontinue\n"
    "\t\tvar room := p.size - Vector3.ONE * 2.0 * ROOM_AMBIENT_MARGIN\n"
    "\t\tif room.x <= 0.0 or room.y <= 0.0 or room.z <= 0.0:\n"
    "\t\t\tcontinue\n"
    "\t\tvar xf := p.global_transform\n"
    "\t\tvar inv := xf.affine_inverse()\n"
    "\t\tvar share := 1.0\n"
    "\t\tfor b in bulbs:\n"
    "\t\t\tvar l: Vector3 = inv * b\n"
    "\t\t\tif absf(l.x) <= p.size.x * 0.5 and absf(l.y) <= p.size.y * 0.5 \\\n"
    "\t\t\t\t\tand absf(l.z) <= p.size.z * 0.5:\n"
    "\t\t\t\tshare = BAKE_FILL_BULB_SHARE\n"
    "\t\t\t\tbreak\n"
    "\t\tvar nx := maxi(1, ceili(room.x / BAKE_FILL_CELL_M))\n"
    "\t\tvar nz := maxi(1, ceili(room.z / BAKE_FILL_CELL_M))\n"
    "\t\tvar y := -room.y * 0.5 + minf(BAKE_FILL_HEIGHT_M, room.y * 0.6)\n"
    "\t\tif container == null:\n"
    "\t\t\tcontainer = Node3D.new()\n"
    "\t\t\tcontainer.name = BAKE_FILL_CONTAINER\n"
    "\t\t\tscene_root.add_child(container)\n"
    "\t\tfor i in nx:\n"
    "\t\t\tfor k in nz:\n"
    "\t\t\t\tvar local := Vector3(room.x * ((i + 0.5) / float(nx) - 0.5), y,\n"
    "\t\t\t\t\troom.z * ((k + 0.5) / float(nz) - 0.5))\n"
    "\t\t\t\tvar omni := OmniLight3D.new()\n"
    "\t\t\t\tomni.name = \"%s_%d\" % [String(p.name), i * nz + k]\n"
    "\t\t\t\tomni.light_energy = energy * share\n"
    "\t\t\t\tomni.light_bake_mode = Light3D.BAKE_STATIC\n"
    "\t\t\t\tomni.omni_range = BAKE_FILL_REACH_CELLS * BAKE_FILL_CELL_M\n"
    "\t\t\t\tomni.omni_attenuation = 0.0\n"
    "\t\t\t\tcontainer.add_child(omni)\n"
    "\t\t\t\tomni.global_position = xf * local\n"
    "\treturn container\n"
    "\n"
    "\n"
    "## The `bake_room_fill` of the preset the scene's LuxRoot starts with (its\n"
    "## `local_override`, else its `active_preset`), or 0.0 when the scene has no\n"
    "## LuxRoot or its preset predates the field (0.68.0).\n"
    "static func bake_fill_energy(scene_root: Node) -> float:\n"
    "\tif scene_root == null or not scene_root.is_inside_tree():\n"
    "\t\treturn 0.0\n"
    "\tfor n in scene_root.get_tree().get_nodes_in_group(&\"lux_root\"):\n"
    "\t\tif n != scene_root and not scene_root.is_ancestor_of(n):\n"
    "\t\t\tcontinue\n"
    "\t\tvar preset: Variant = n.get(\"local_override\")\n"
    "\t\tif preset == null:\n"
    "\t\t\tpreset = n.get(\"active_preset\")\n"
    "\t\tif preset is Resource and \"bake_room_fill\" in preset:\n"
    "\t\t\treturn float(preset.get(\"bake_room_fill\"))\n"
    "\treturn 0.0\n"
    "\n"
    "\n"
    "## Read `path`, replace any previous bake, and spawn a rig per anchor under a\n"
)


def main():
    staged = []
    for path, size, old, new in ((PRESET, 23092, PRESET_OLD, PRESET_NEW), (LOADER, 88643, LOADER_OLD, LOADER_NEW)):
        data = path.read_bytes()
        assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
        assert b"\r\n" not in data, "%s has CRLF; it was LF" % path.name
        text = data.decode("utf-8")
        assert text.count(old) == 1, "%s: anchor found %d times" % (path.name, text.count(old))
        staged.append((path, data, text.replace(old, new)))
    for path, data, text in staged:
        path.write_bytes(text.encode("utf-8"))
        print("%s: %d -> %d bytes" % (path.name, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
