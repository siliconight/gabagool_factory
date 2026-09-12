"""Roadmap batch 39, 2026-09-12: item 152 filed (APPEND) -- the surface
dressing reads as texture defects, measured, with the layer stack the
walker asked for. Asserts the item is not already present.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

APPEND = """
*STATUS: OPEN 2026-09-12 (night) -- RAISED BY THE WALKER ON THE 9012 AND
9014 FRAMES, MEASURED, NOTHING BUILT; THE BUILD ORDER IS IN THE ITEM*

**152. The surface dressing reads as defects in the texture, not as things
on a surface -- and the layer stack under it has two layers missing and
one that never leaves the tool.** The walker, 2026-09-12, on the bank
frames: "it looks like unintentional defects on the texture ... consider
how we can leverage opacity/transparency to add it like layers to the
dominant floor, wall, ceiling ... it might be a sign that we need more
layers/nuance/realism." MEASURED on cold run 9014's package
(`bank_block_001.surface_dressing.json`, the clutter GLBs, `site_base.glb`,
`look_shots` outdoors at eye height and kneeling): (a) WHAT THE PIECES ARE:
four species, `pebble` / `rubble_frag` / `litter_scrap` / `weed_tuft`,
2,708 instances, 2,610 of them micro-band -- median heights 0.057, 0.051,
0.020 and 0.070 m -- every one a flat single-colour material with no
texture (pebble and rubble 0.56 grey, litter 0.72, weed 0.32/0.40/0.22),
72 to 192 triangles. At 1.7 m eye height a 5 cm stone at 8 m is about six
pixels of lit light-grey; that is a speck, and a speck on a surface reads
as a fault in the surface. (b) WHAT THEY SIT ON: the exterior ground plate
(`gb_floor`) is one untextured grey, 0.52, no image, no Pixelcoat skin --
the clutter is the only texture the outdoor ground has, so every piece is
a mark on a blank. The interior floors are skinned; the exterior ground is
not (item 45 has said "large playable surfaces are visually flat" since
2026-08-14 with nothing built). (c) WHERE THEY ARE: 2,284 of 2,708 in the
perimeter strips at 0.34 per m2 (`very_high`), 360 across 7,285 m2 of open
ground at 0.05 per m2, 35 at every wall base combined, 29 on the paths.
The guide's density readings put the most where the walker is least, and
the seam it calls `high` got thirty-five pieces on three buildings; the
kneeling frame at the plate edge is a drift of white flecks against a
flat wall. (d) NO GROUNDING: `shadow_policy: contact` is a word in the
manifest; nothing reads it, the MultiMesh nodes carry no shadow or AO
setting, and the pieces float bright on the plate with no contact
darkening. (e) THE HONESTY RULE IS WHY THEY ARE SMALL AND THAT IS
CORRECT: on traversed ground a piece may not exceed 0.117 m
(`unassisted_step_max`), so the walkable world can only ever carry
micro-band clutter -- the lever for "reads as a thing" is not size, it is
material, grounding and the layers beneath. (f) THE TRANSPARENT LAYER
EXISTS AND NEVER SHIPS: Patina's `decals.py` generates posterised RGBA
stamps (stains, scuffs, streaks, water stains, paint chips) and places them
per theme spec over classified faces -- exactly the walker's "opacity as
layers on the dominant floor, wall, ceiling" -- and (1) the `delco_1997`
theme the briefs use declares `"decals": []` (only the gas-station builtin
carries specs: water_stain 6 per 100 m2 on wall/ceiling, paint_chip 5),
so 9014's bank manifest says `decals: {"instances": []}`; and (2) the
placements are instantiated by the Patina Godot addon at runtime, which a
portable package cannot carry, and LF's export has no decal path at all
(`grep decal packages/exporting`: nothing). Built, unspecified for the
theme, and undeliverable. THE STACK, AS IT SHOULD READ, bottom to top,
each with an owner: L0 base skin (Pixelcoat; exists for buildings, ABSENT
for the ground plate); L1 large-scale variation -- wall-base dirt bands,
tile wear gradients, the depth guide's macro breakup (Patina's
vertex-colour banding does this for buildings; nothing for ground); L2
DECALS, projected alpha stamps on floors, walls, ceilings (Patina, built;
needs theme specs and an export path -- Godot `Decal` is a core node, so
the composed `.tscn` can carry them with the PNGs beside it, no addon);
L3 clutter (Zoo + Patina, exists; needs a skin, grounding, and a density
table that follows the walker); L4 interior set dressing (item 148,
nothing). The walker's instinct is the contract's own order: SURFACE_
DRESSING.md 3b says coverage first, cutouts second, translucency when the
material calls for it -- a stain is translucent because a stain is. THE
BUILD ORDER, cheapest gain first: (1) skin the ground plate (Lot/LF hand
the plate a Pixelcoat surface -- asphalt, sidewalk, packed dirt by zone
family -- item 45's first concrete step); (2) decals to the package: a
`decals` block in the delco_1997 theme, `presentation_compose` emitting
`Decal` nodes from Patina's placements with the stamps as package PNGs,
one deletable `PatinaDecals` node per building, and the same for the
ground through `patina_surface_dressing` (stains under wall bases, tyre
streaks on paths); (3) clutter that is not a speck: Pixelcoat-skinned
clutter materials instead of flat colour, base colours taken from the
surface under them (a pebble on asphalt is asphalt-dark), a sink of a few
millimetres and a contact-shadow disc or vertex-darkened base so each
piece is anchored, and the density table turned round -- wall bases and
path edges high, perimeter medium -- with the honesty rule untouched;
(4) the low band where nobody walks: boards, bags, a crate, a bollard, a
planter (0.1-0.7 m) in perimeter and wall-base zones only, where the
capsule never goes, so the layer has a silhouette and not only grain.
**WHAT WOULD CLOSE THIS:** a cold package whose outdoor ground carries a
skin, a decal layer and clutter that a frame at eye height shows as
objects on a surface rather than noise in it -- judged by the walker, and
counted by the census of what each layer put where.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if "\n**152. " in text:
        print("item 152 already present", file=sys.stderr)
        return 1
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 152 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
