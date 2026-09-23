"""Ladders: rusted outside, clean inside, with the value contrast kept.

The walker's call, 2026-09-23, with two reference photographs (recorded in
`docs/SET_DRESSING_REFERENCES.md`).

HOLD UNTIL THE COLD RUN ENDS. Written while cold run 9072 was in flight;
applying it mid-run would void the zero. `patches/` is not in the hashed set,
so writing it is free -- running it is not.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "assets" / "godot" / "zoo_worldskin.gd"

# ---------------------------------------------------------------- anchor 1
A1 = 'const SLAB_REVEAL_FAMILY: Array = ["floor_"]\n'

N1 = A1 + '''
## LADDERS -- rusted outside, clean inside (roadmap 169), and the walker's
## call with two reference photographs.
##
## WHAT SHIPS TODAY: nothing skins a ladder, so it arrives in Deli Counter's
## flat `gb_ladder` -- 38 surfaces and 22.82 m2 on cold run 9070's package.
## The `greybox_skin` gate counts them and does not refuse, because an absent
## capability is not a regression.
##
## THE FALLBACK IS YELLOW AND IT IS YELLOW ON PURPOSE, which is the whole
## difficulty here. `GREYBOX_PALETTE` gives `gb_ladder` (1.00, 0.90, 0.55) --
## luminance 0.897, the BRIGHTEST value on the site -- because "it is the
## smallest thing that has to be found". Skinning a ladder therefore SPENDS a
## legibility signal that palette deliberately bought, and a rusted ladder on
## a weathered wall is precisely the "amber and grey reading as one surface"
## failure the palette's own comment warns about.
##
## SO THE SIGNAL IS MOVED RATHER THAN SPENT. Deli Counter emits a ladder's
## rails and rungs as SEPARATE meshes (`ladder<n>_rail_*`, `ladder<n>_rung_*`,
## `deli_counter.py:2032`), so reference 2's actual read -- a matte near-black
## frame against bright galvanised treads -- is reproducible with no new
## geometry: the rails take the darkest metal the building owns and the rungs
## the lightest. The rungs stay the bright thing the eye is meant to find.
##
## OUTSIDE, BOTH HALVES TAKE THE RUST, per reference 1, where the rails and
## rungs are equally streaked and the ladder reads against grey concrete
## rather than against itself.
##
## THE SOURCE IS `prop_`, NOT A KIT FAMILY, AND THAT IS MEASURED. On 9070's
## package only 1 of 3 buildings owns metal in a kit family (freight_terminal
## 5 modules; deli_a03 and strip_club_a03 have NONE), while all three own it
## in `prop_` (27, 21 and 41 modules). Asking a building for a kit finish it
## may not own is exactly the `STAIR_KIND = "concrete"` mistake this file
## already records as REFUTED, and it would have refused on two buildings in
## three. `KIT_PREFIXES` excludes props because world-projecting a MOVABLE
## object makes its texture swim; that reason does not apply to borrowing a
## prop's material for a ladder bolted to a wall.
const LADDER_PREFIX: String = "ladder"
## `ladder<n>ext_*` is an exterior ladder: Deli Counter writes the mark from
## `Ladder.placement_mode` (`exterior_wall` / `platform`), the same way
## `stair<n>col_` and `stair<n>ramp_` carry their kind in the name. Measured
## across the spec library: 109 ladders are interior (52 explicit, 54 unset
## and taking the dataclass default, 3 `shaft`) against 3 exterior. The split
## is real and lopsided, and the lopsidedness is why the interior look is the
## one worth getting right.
const LADDER_EXTERIOR_MARK: String = "ext"
const LADDER_RAIL_MARK: String = "_rail_"
const LADDER_RUNG_MARK: String = "_rung_"
const LADDER_METAL_FAMILY: Array = ["prop_"]
## The theme's weathered steel. Its `baseColorFactor` is (1, 1, 1) because the
## rust is entirely in `metal_rusted_street_albedo` -- so it cannot be ranked
## by tint and is chosen BY NAME, and must be excluded from the darkest and
## lightest search below or its untinted 1.0 would always win "lightest".
const LADDER_RUST_MATERIAL: String = "M_Skin_metal_delco_1997"
## A material whose albedo factor is at or above this carries no tint to rank:
## its colour lives in its texture. Measured on 9070's package, the tinted
## metals run 0.015 to 0.789 and the only one at 1.0 is the rusted skin.
const LADDER_TINTLESS: float = 0.95
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''\t\t\tvar sl: Dictionary = _skin_slabs(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  slabs: %d surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(sl["slab_surfaces"]), int(sl["slab_meshes"]),
\t\t\t\t\tint(sl["unskinned_meshes"]), String(sl["note"])])
\t\t\treturn scene
'''

N2 = '''\t\t\tvar sl: Dictionary = _skin_slabs(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  slabs: %d surface(s) skinned on %d mesh(es), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(sl["slab_surfaces"]), int(sl["slab_meshes"]),
\t\t\t\t\tint(sl["unskinned_meshes"]), String(sl["note"])])
\t\t\tvar ld: Dictionary = _skin_ladders(scene, get_source_file().get_base_dir())
\t\t\tprint("[worldskin] %s  ladders: %d surface(s) skinned on %d mesh(es) (%d exterior), %d mesh(es) left flat%s"
\t\t\t\t% [base, int(ld["ladder_surfaces"]), int(ld["ladder_meshes"]),
\t\t\t\t\tint(ld["exterior_meshes"]), int(ld["unskinned_meshes"]),
\t\t\t\t\tString(ld["note"])])
\t\t\treturn scene
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''\tfor c in n.get_children():
\t\tvar sub: Array = _assign_slabs(c, mat)
\t\tfs += int(sub[0])
\t\tfm += int(sub[1])
\t\tseen += int(sub[2])
\t\tflat += int(sub[3])
\treturn [fs, fm, seen, flat]
'''

N3 = A3 + '''

## Every metal material the building's prop modules wear, with its tint.
##
## Returns [[material, name, luminance, rankable]], one row per DISTINCT
## material name. Scans the whole family rather than stopping at the first
## hit, because this pass needs the extremes of the range and not a
## representative -- which is the one way it differs from `_family_material`.
##
## Luminance is read off `albedo_color`, not parsed out of the name's hex
## suffix: the factor IS the tint (measured, 31 distinct metals spanning
## 0.015 to 0.789), and a name is a weaker source than the value it encodes.
func _metal_palette(art: String, dir: DirAccess) -> Array:
\tvar files: PackedStringArray = dir.get_files()
\tfiles.sort()
\tvar seen: Dictionary = {}
\tvar out: Array = []
\tfor f in files:
\t\tif not f.ends_with(".glb"):
\t\t\tcontinue
\t\tvar in_family: bool = false
\t\tfor fam in LADDER_METAL_FAMILY:
\t\t\tif f.begins_with(String(fam)):
\t\t\t\tin_family = true
\t\tif not in_family:
\t\t\tcontinue
\t\tvar ps: PackedScene = load(art.path_join(f)) as PackedScene
\t\tif ps == null:
\t\t\tcontinue
\t\tvar inst: Node = ps.instantiate()
\t\t_collect_metals(inst, seen, out)
\t\tinst.free()
\treturn out


func _collect_metals(n: Node, seen: Dictionary, out: Array) -> void:
\tvar mi: MeshInstance3D = n as MeshInstance3D
\tif mi != null and mi.mesh != null:
\t\tfor i in range(mi.mesh.get_surface_count()):
\t\t\tvar bm: BaseMaterial3D = mi.mesh.surface_get_material(i) as BaseMaterial3D
\t\t\tif bm == null or bm.albedo_texture == null:
\t\t\t\tcontinue
\t\t\tvar nm: String = String(bm.resource_name)
\t\t\tif not nm.contains("metal") or seen.has(nm):
\t\t\t\tcontinue
\t\t\tseen[nm] = true
\t\t\tvar c: Color = bm.albedo_color
\t\t\tvar lum: float = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
\t\t\tout.append([bm, nm, lum, lum < LADDER_TINTLESS])
\tfor c2 in n.get_children():
\t\t_collect_metals(c2, seen, out)


## A world-triplanar duplicate of `src`, named for the part it dresses.
## Same treatment `_family_material` gives its pick, and for the same reason:
## a greybox box carries no UVs, so the texture is projected from position.
func _ladder_material(src: BaseMaterial3D, part: String) -> Material:
\tvar dup: BaseMaterial3D = src.duplicate()
\tdup.resource_name = "M_Skin_ladder_%s" % part
\tif not dup.uv1_world_triplanar:
\t\tdup.uv1_triplanar = true
\t\tdup.uv1_world_triplanar = true
\treturn dup


## Skin the greybox base's ladders, for the reasons on `LADDER_PREFIX`.
##
## Refuses out loud like its two siblings: a base whose ladders this cannot
## dress ships them in the greybox yellow, and a `print` nobody reads is how
## the stair defect survived five days (roadmap 144).
##
## Returns {ladder_surfaces, ladder_meshes, exterior_meshes,
## unskinned_meshes, note}. `exterior_meshes` is COUNTED rather than inferred
## from the note, so a test can prove the exterior branch fired instead of
## trusting a sentence that would print either way.
func _skin_ladders(scene: Node, base_dir: String) -> Dictionary:
\tvar out: Dictionary = {"ladder_surfaces": 0, "ladder_meshes": 0,
\t\t"exterior_meshes": 0, "unskinned_meshes": 0, "note": ""}
\tvar present: Array = _assign_ladders(scene, null, null, null)
\tvar rungs_and_rails: int = int(present[2])
\tif rungs_and_rails == 0:
\t\tout["note"] = "; no visual ladder in this base, nothing to skin"
\t\treturn out
\tvar art: String = base_dir.path_join("art").path_join("zoo")
\tvar dir := DirAccess.open(art)
\tif dir == null:
\t\tout["unskinned_meshes"] = rungs_and_rails
\t\tout["note"] = "; NO art/zoo BESIDE THE BASE -- %d ladder mesh(es) left in the greybox material" % rungs_and_rails
\t\tpush_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
\t\treturn out
\tvar palette: Array = _metal_palette(art, dir)
\tif palette.is_empty():
\t\tout["unskinned_meshes"] = rungs_and_rails
\t\tout["note"] = ("; NO METAL MATERIAL UNDER art/zoo IN FAMILIES %s -- %d ladder mesh(es) left in the greybox material"
\t\t\t% [str(LADDER_METAL_FAMILY), rungs_and_rails])
\t\tpush_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
\t\treturn out

\tvar rust: BaseMaterial3D = null
\tvar darkest: BaseMaterial3D = null
\tvar lightest: BaseMaterial3D = null
\tvar dark_lum: float = 999.0
\tvar light_lum: float = -1.0
\tvar dark_name: String = ""
\tvar light_name: String = ""
\tvar rust_name: String = ""
\tfor row in palette:
\t\tvar bm: BaseMaterial3D = row[0]
\t\tvar nm: String = String(row[1])
\t\tvar lum: float = float(row[2])
\t\tif nm == LADDER_RUST_MATERIAL:
\t\t\trust = bm
\t\t\trust_name = nm
\t\tif not bool(row[3]):
\t\t\tcontinue
\t\tif lum < dark_lum:
\t\t\tdark_lum = lum
\t\t\tdarkest = bm
\t\t\tdark_name = nm
\t\tif lum > light_lum:
\t\t\tlight_lum = lum
\t\t\tlightest = bm
\t\t\tlight_name = nm
\t# One rankable metal is a ladder with no contrast in it, which is worse
\t# than the yellow it replaces -- the yellow at least reads. Say so.
\tif darkest == null or lightest == null or darkest == lightest:
\t\tout["unskinned_meshes"] = rungs_and_rails
\t\tout["note"] = ("; ONLY %d TINTED METAL(S) under art/zoo -- a ladder needs two for rail/rung contrast, %d mesh(es) left in the greybox material"
\t\t\t% [palette.size(), rungs_and_rails])
\t\tpush_error("[worldskin] %s%s" % [get_source_file(), String(out["note"])])
\t\treturn out
\t# Outside takes the rust on both halves (reference 1). With no rusted skin
\t# in this building's packs the exterior falls back to the interior pair,
\t# and the note says so rather than pretending.
\tvar ext: Material = null
\tif rust != null:
\t\text = _ladder_material(rust, "rust")
\tvar rail: Material = _ladder_material(darkest, "rail")
\tvar rung: Material = _ladder_material(lightest, "rung")
\tvar counts: Array = _assign_ladders(scene, rail, rung, ext)
\tout["ladder_surfaces"] = int(counts[0])
\tout["ladder_meshes"] = int(counts[1])
\tout["unskinned_meshes"] = int(counts[3])
\tout["exterior_meshes"] = int(counts[4])
\tout["note"] = ("; rail %s (%.3f), rung %s (%.3f)"
\t\t% [dark_name, dark_lum, light_name, light_lum])
\tif ext != null:
\t\tout["note"] += "; exterior %s" % rust_name
\telse:
\t\tout["note"] += "; NO %s in this building's packs, exterior ladders take the interior pair" % LADDER_RUST_MATERIAL
\treturn out


## A mesh named for a ladder that is DRAWN rather than collided with.
## `ladder<n>_plane-convcolonly` is Deli Counter's climb-face collider and
## Godot has already removed its visual by the time this runs; the `col` test
## is the same second line of defence the slab pass keeps.
func _is_visual_ladder(nm: String) -> bool:
\treturn nm.begins_with(LADDER_PREFIX) and not nm.contains("col")


## Assign rail/rung/exterior materials. A null trio counts instead of
## assigning, so the census and the work share one definition of a ladder
## mesh rather than two that can drift (see `_assign_stairs`).
##
## Returns [ladder_surfaces, ladder_meshes, ladder_seen, unskinned_meshes,
## exterior_meshes].
func _assign_ladders(n: Node, rail: Material, rung: Material,
\t\text: Material) -> Array:
\tvar fs: int = 0
\tvar fm: int = 0
\tvar seen: int = 0
\tvar flat: int = 0
\tvar ext_n: int = 0
\tvar mi: MeshInstance3D = n as MeshInstance3D
\tif mi != null and mi.mesh != null and _is_visual_ladder(String(mi.name)):
\t\tvar nm: String = String(mi.name)
\t\tvar is_rail: bool = nm.contains(LADDER_RAIL_MARK)
\t\tvar is_rung: bool = nm.contains(LADDER_RUNG_MARK)
\t\tif is_rail or is_rung:
\t\t\tseen += 1
\t\t\tvar pick: Material = rail if is_rail else rung
\t\t\t# `ladder<n>ext_` -- the mark sits on the index token, before the
\t\t\t# part, so it is tested on the whole name rather than a split.
\t\t\tif ext != null and nm.contains(LADDER_EXTERIOR_MARK + "_"):
\t\t\t\tpick = ext
\t\t\t\text_n += 1
\t\t\tif pick == null:
\t\t\t\tflat += 1
\t\t\telse:
\t\t\t\tfor i in range(mi.mesh.get_surface_count()):
\t\t\t\t\tmi.mesh.surface_set_material(i, pick)
\t\t\t\t\tfs += 1
\t\t\t\tfm += 1
\tfor c in n.get_children():
\t\tvar sub: Array = _assign_ladders(c, rail, rung, ext)
\t\tfs += int(sub[0])
\t\tfm += int(sub[1])
\t\tseen += int(sub[2])
\t\tflat += int(sub[3])
\t\text_n += int(sub[4])
\treturn [fs, fm, seen, flat, ext_n]
'''

EDITS = ((A1, N1), (A2, N2), (A3, N3))


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
