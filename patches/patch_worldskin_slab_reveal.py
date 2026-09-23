"""Skin the greybox slab, so a hole cut through it is not lined with greybox.

Anchored: every anchor must match exactly once or this refuses to write, and
the before/after text is recorded here so the file can be rebuilt from a clean
ancestor plus the patches that followed it.

Target read in this session: level_factory/assets/godot/zoo_worldskin.gd,
42,515 bytes, LF only (900 newlines, 0 CRLF), matching the figure the listing
reported.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "assets" / "godot" / "zoo_worldskin.gd"

# ---------------------------------------------------------------- anchor 1
A1 = 'const STAIR_GUARD_PREFIX: String = "stair_guard_"\n'

N1 = A1 + '''
## The greybox slab's CUT EDGE, which theming never reaches (roadmap 168).
##
## Walked 2026-09-23: on a ladder, looking down reads grey and untextured and
## the real floor appears on the way down; the walker reported the same on the
## stairs independently. Measured on cold run 9070's package before a line of
## this was written, because four cheaper explanations were on the table and
## every one of them is wrong:
##
##  * NOT draw distance. Every mesh in that column reports
##    `visibility_range_begin/end = 0`, `lod_bias = 1.0` and no distance fade.
##    Nothing in the scene changes with camera distance at all.
##  * NOT occlusion culling. Two package copies differing only in
##    `use_occlusion_culling` in `project.godot` drew identical counts at four
##    eye heights (52/38/82/12).
##  * NOT z-fighting. The themed floor's top and the slab's top are 20 mm
##    apart and a 24-bit buffer separates about 0.03 mm at that range. The
##    coplanar pair is the floor's UNDERSIDE against the slab's top, which
##    backface culling never draws.
##  * NOT a gap in the floor. Themed floor area equals slab area to 0.1 m2
##    (3192.0 against 3192.0), and the ladder hole is cut through BOTH to the
##    same rectangle -- slab x 53.45..54.55 z 21.9..23.2, themed floor the
##    same to the raster's own 5 cm cell.
##
## What is left is the only untextured surface in the column. Theming skins a
## slab's TOP (as a floor) and its BOTTOM (as a ceiling) and never touches the
## faces that a hole cut through it CREATES. `deli_counter._slab_holes_cut`
## boolean-subtracts the opening and the new interior faces inherit the slab's
## flat `gb_floor`. A slab is `floor_thick` deep, so a 1.10 x 1.30 m ladder
## hole is ringed by 1.44 m2 of bare greybox -- the same area as the opening it
## surrounds, which is why it fills the view from anywhere but straight down.
## 8 of 344 slabs in that package are cut, carrying 10.44 m2 between them:
## every ladder shaft and every stairwell.
##
## THE WHOLE SLAB IS SKINNED, NOT THE COLLAR. The buried top and bottom cost
## nothing to dress -- it is one mesh with one material either way, so the
## submission count does not move -- and picking the interior faces out of a
## boolean result would mean trusting normals that the cut generated.
##
## A BOOLEAN'S NEW FACES CARRY NO USABLE UVs, which is the same problem
## `_skin_stairs` was written for and takes the same answer: world triplanar
## projects from position and needs none.
const SLAB_PREFIX: String = "slab_"
## Deli Counter's collision slabs are `slab_col_<story>`; its visual ones are
## `slab_<story>` and `slab_<story>_t<j>_<i>`. One spelling of the test, shared
## with the stair pass's shape rather than written a second way.
const SLAB_COLLISION_MARK: String = "col"
## A REVEAL TAKES THE FAMILY OF THE SURFACE IT MEETS. The collar's top edge
## abuts the themed floor plane, so sharing that family makes the one seam a
## walker actually sees continuous. The wall family was considered and left:
## it would match a seam that is not there. Same value as
## `STAIR_FLIGHT_FAMILY` and written out rather than aliased to it, so the two
## can diverge later without one silently moving the other.
const SLAB_REVEAL_FAMILY: Array = ["floor_"]
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''\t\tif base.begins_with(BASE_PREFIX):
\t\t\tvar n: Dictionary = _skin_stairs(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  stairs: %d flight surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(n["flight_surfaces"]), int(n["flight_meshes"]),
\t\t\t\t\tint(n["unskinned_meshes"]), String(n["note"])])
\t\t\treturn scene
'''

N2 = '''\t\tif base.begins_with(BASE_PREFIX):
\t\t\tvar n: Dictionary = _skin_stairs(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  stairs: %d flight surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(n["flight_surfaces"]), int(n["flight_meshes"]),
\t\t\t\t\tint(n["unskinned_meshes"]), String(n["note"])])
\t\t\tvar sl: Dictionary = _skin_slabs(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  slabs: %d surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(sl["slab_surfaces"]), int(sl["slab_meshes"]),
\t\t\t\t\tint(sl["unskinned_meshes"]), String(sl["note"])])
\t\t\treturn scene
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''\tfor c in n.get_children():
\t\tvar sub: Array = _assign_stairs(c, flight_mat)
\t\tfs += int(sub[0])
\t\tfm += int(sub[1])
\t\tseen += int(sub[2])
\t\tguards += int(sub[3])
\t\tflat += int(sub[4])
\treturn [fs, fm, seen, guards, flat]
'''

N3 = A3 + '''

## Skin the greybox base's floor slabs, for the reasons written on
## `SLAB_PREFIX` above.
##
## Mirrors `_skin_stairs` deliberately, including refusing OUT LOUD: a base
## whose slabs this cannot dress ships bare grey around every ladder and
## stairwell in it, which is exactly the failure that reached the walker and
## exactly the kind that a `print` nobody reads does not stop.
##
## Returns {slab_surfaces, slab_meshes, unskinned_meshes, note}.
func _skin_slabs(scene: Node, base_dir: String) -> Dictionary:
\tvar out: Dictionary = {"slab_surfaces": 0, "slab_meshes": 0,
\t\t"unskinned_meshes": 0, "note": ""}
\t# The census and the work use ONE definition of a visual slab mesh: a null
\t# material counts instead of assigning (see `_assign_stairs`).
\tvar present: Array = _assign_slabs(scene, null)
\tvar slabs: int = int(present[2])
\tif slabs == 0:
\t\tout["note"] = "; no visual slab in this base, nothing to skin"
\t\treturn out
\tvar art: String = base_dir.path_join("art").path_join("zoo")
\tvar dir := DirAccess.open(art)
\tif dir == null:
\t\tout["unskinned_meshes"] = slabs
\t\tout["note"] = "; NO art/zoo BESIDE THE BASE -- %d slab mesh(es) left in the greybox material" % slabs
\t\tpush_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
\t\treturn out
\tvar reveal: Array = _family_material(art, dir, SLAB_REVEAL_FAMILY, "slab_reveal")
\tif reveal.is_empty():
\t\tout["unskinned_meshes"] = slabs
\t\t# `%` binds tighter than `+`, so the formatted piece is built whole
\t\t# before it is joined (the trap `tools/gdcheck.py` exists to catch).
\t\tout["note"] = ("; NO MODULE UNDER art/zoo IN FAMILIES %s -- %d slab mesh(es) left in the greybox material"
\t\t\t% [str(SLAB_REVEAL_FAMILY), slabs])
\t\tpush_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
\t\treturn out
\tvar counts: Array = _assign_slabs(scene, reveal[0] as Material)
\tout["slab_surfaces"] = int(counts[0])
\tout["slab_meshes"] = int(counts[1])
\tout["unskinned_meshes"] = int(counts[3])
\tout["note"] = "; reveal from %s" % String(reveal[1])
\treturn out


## A mesh named for a floor slab that is DRAWN rather than collided with.
func _is_visual_slab(nm: String) -> bool:
\treturn nm.begins_with(SLAB_PREFIX) and not nm.contains(SLAB_COLLISION_MARK)


## Assign the reveal material. A null `mat` counts the meshes it would have
## dressed as unskinned instead of assigning, so the census `_skin_slabs`
## takes before it goes looking for a pack and the work it does afterwards
## share one definition rather than two that can drift.
##
## Returns [slab_surfaces, slab_meshes, slab_seen, unskinned_meshes].
func _assign_slabs(n: Node, mat: Material) -> Array:
\tvar fs: int = 0
\tvar fm: int = 0
\tvar seen: int = 0
\tvar flat: int = 0
\tvar mi: MeshInstance3D = n as MeshInstance3D
\tif mi != null and mi.mesh != null and _is_visual_slab(String(mi.name)):
\t\tseen += 1
\t\tif mat == null:
\t\t\tflat += 1
\t\telse:
\t\t\tfor i in range(mi.mesh.get_surface_count()):
\t\t\t\tmi.mesh.surface_set_material(i, mat)
\t\t\t\tfs += 1
\t\t\tfm += 1
\tfor c in n.get_children():
\t\tvar sub: Array = _assign_slabs(c, mat)
\t\tfs += int(sub[0])
\t\tfm += int(sub[1])
\t\tseen += int(sub[2])
\t\tflat += int(sub[3])
\treturn [fs, fm, seen, flat]
'''

# ------------------------------------------------- anchors 4 and 5 (naming)
# `part` now names the whole surface rather than a half of a stair, because a
# second caller arrived. Nothing reads these names: grepped across the repo,
# the only other hits are copies of this file inside built packages.
A4 = '\t\t\tdup.resource_name = "M_Skin_stair_%s" % part\n'
N4 = '\t\t\tdup.resource_name = "M_Skin_%s" % part\n'

A5 = '\tvar flight: Array = _family_material(art, dir, STAIR_FLIGHT_FAMILY, "flight")\n'
N5 = '\tvar flight: Array = _family_material(art, dir, STAIR_FLIGHT_FAMILY, "stair_flight")\n'

EDITS = ((A1, N1), (A2, N2), (A3, N3), (A4, N4), (A5, N5))


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
    print(f"{TARGET.name}: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
