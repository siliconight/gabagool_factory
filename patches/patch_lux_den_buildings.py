"""Lux 0.68.2: a den of sin is a building, not a room.

    python patch_lux_den_buildings.py [<loader path>]

The walker, 2026-10-07: "the 'dens of sin' buildings that we can keep a bit
dark". 0.68.0's fill skipped a TINTED probe -- a strip club's floor -- and
filled every other room in the same building: on club_block_014 at night,
strip_club_a02's back rooms went 19.5 -> 52.3 (the brightest room in the
level), its cellar hall 1.2 -> 8.7 and its count room 1.0 -> 7.0, while its
main floor stayed 2.8. A building with any tinted probe now keeps every room
unfilled.

Which building a probe is in: Lot's `merge_lights` ids every anchor
`<building>/<id>` (lot.py: `wa["id"] = f"{bid}/{a.get('id', 'light')}"`)
and Lux names a room probe after its anchor's room with "/" made "_", so
`b0_back_rooms_ambient` is building b0 -- in every package read, single
buildings included (`b0_customer_floor_ambient`). A probe without the prefix
stands alone: only its own tint counts, which is 0.68.1's rule.

Anchored on `lux/addons/lux/runtime/lux_light_loader.gd` as 0.68.1 left it
(95,641 bytes, LF) by default; a path argument patches another copy of the
same text (a vendored scratch copy, whose size is not checked). Every anchor
must match once; nothing is written on a miss.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_light_loader.gd"

EDITS = [
    ("## A room a bare bulb lights keeps this share of the floor: \"keep pendants\n",
     "## DENS OF SIN ARE BUILDINGS, NOT ROOMS (0.68.2). The walker, 2026-10-07: \"the\n"
     "## 'dens of sin' buildings that we can keep a bit dark\". 0.68.0 skipped only\n"
     "## the tinted probe -- a strip club's floor -- and filled the rest of the\n"
     "## building: on club_block_014 at night strip_club_a02's back rooms went\n"
     "## 19.5 -> 52.3, the brightest room in the level, while its floor stayed 2.8.\n"
     "## A building with ANY tinted probe now keeps every room unfilled.\n"
     "## `_probe_building` says which building a probe is in.\n"
     "##\n"
     "## A room a bare bulb lights keeps this share of the floor: \"keep pendants\n"),
    ("\tvar container: Node3D = null\n\tfor n in scene_root.find_children(\"*\", \"ReflectionProbe\", true, false):\n"
     "\t\tvar p := n as ReflectionProbe\n"
     "\t\tif not p.interior or p.ambient_mode != ReflectionProbe.AMBIENT_COLOR \\\n"
     "\t\t\t\tor not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR):\n"
     "\t\t\tcontinue\n",
     "\t# the room probes, and the buildings any tinted one makes a den\n"
     "\tvar probes: Array[ReflectionProbe] = []\n"
     "\tvar dens := {}\n"
     "\tfor n in scene_root.find_children(\"*\", \"ReflectionProbe\", true, false):\n"
     "\t\tvar rp := n as ReflectionProbe\n"
     "\t\tif not rp.interior or rp.ambient_mode != ReflectionProbe.AMBIENT_COLOR:\n"
     "\t\t\tcontinue\n"
     "\t\tprobes.append(rp)\n"
     "\t\tif not rp.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR):\n"
     "\t\t\tdens[_probe_building(rp)] = true\n"
     "\tvar container: Node3D = null\n"
     "\tfor p in probes:\n"
     "\t\tif not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR) \\\n"
     "\t\t\t\tor dens.has(_probe_building(p)):\n"
     "\t\t\tcontinue\n"),
    ("## The `bake_room_fill` of the preset the scene's LuxRoot starts with (its\n",
     "## The site building a room probe stands in. Lot's `merge_lights` ids every\n"
     "## anchor `<building>/<id>` (lot.py) and a probe is named after its anchor's\n"
     "## room with \"/\" made \"_\", so `b2_banking_hall_ambient` is building b2. A\n"
     "## name without that prefix is a building of its own.\n"
     "static func _probe_building(p: ReflectionProbe) -> String:\n"
     "\tvar m := RegEx.create_from_string(\"^(b[0-9]+)_\").search(String(p.name))\n"
     "\treturn m.get_string(1) if m != null else \"probe:\" + String(p.name)\n"
     "\n"
     "\n"
     "## The `bake_room_fill` of the preset the scene's LuxRoot starts with (its\n"),
]


def main(argv):
    path = pathlib.Path(argv[0]) if argv else LOADER
    data = path.read_bytes()
    if path == LOADER:
        assert len(data) == 95641, "loader is %d bytes, read at 95,641" % len(data)
        assert b"\r\n" not in data
    text = data.decode("utf-8").replace("\r\n", "\n")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("%s: %d -> %d bytes" % (path, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main(sys.argv[1:])
