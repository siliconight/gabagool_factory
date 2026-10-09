"""Roadmap 216 OPEN: trees -- a sculpted trunk and a crown of branch cards, and
god rays under them. The walker's ask of 2026-10-09, with a CC0 reference
tree; filed and measured, not started.

Anchored on the roadmap's last line (item 215's last body line), which must
match exactly once and end the file, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

TAIL = ("- **The arc question is unchanged in substance and is now counted.** `S_RESPONDER_ARC` fires on every "
        "candidate of club_block_014, at 33, 6 and 16 degrees against the rule's 210. The options above stand.\n")
ITEM_216 = (
    "\n"
    "*STATUS: OPEN 2026-10-09 -- filed, not started. The walker's ask: better-looking trees, with a CC0 reference "
    "tree, the method it was made by, and god rays through canopies (`docs/reference/TREE_REFERENCE.md`). Zoo's six "
    "tree species are grown from a skeleton under faceted box leaf clusters: 2,220-3,564 triangles and 4 primitives "
    "each. The reference is a sculpted trunk under about 800 bent, alpha-tested branch cards: about 21,000 "
    "triangles in 3 materials with 2048 maps. Next: price an alpha-tested crown before building one.*\n"
    "\n"
    "**216. Trees: a sculpted trunk and a crown of branch cards, and god rays under them.** The walker, "
    "2026-10-09: \"On the roadmap, improving Trees\", with `one tree hill_gumroad.blend` (\"The cc0 tree to use as "
    "a reference for how to make better looking trees\"), a transcript of the video it comes from, and a note on "
    "god rays with a photograph.\n"
    "\n"
    "**THE REFERENCE** (measured: `docs/findings/trees_reference/`, read with Blender's auto-exec off; it holds "
    "no scripts). One 21 m stylized hill tree.\n"
    "- **The trunk:** one connected mesh of 7,030 triangles, roots to main limbs, with its Multires sculpt "
    "beside it. A 2048 colour map and a 2048 normal map, opaque.\n"
    "- **The crown:** 12 large branch cards (100 triangles each) and about 800 small leafy ones in three variants "
    "(about 28 each). The placed cards are bent, not flat. Each material has a 2048 colour map with alpha and a "
    "2048 normal map, alpha-tested and two-sided.\n"
    "- **The binary is not tracked** (75 MB). It is in `_archive/reference/`, and the note carries its sha256. "
    "`docs/FILING.md` has a new row for reference assets too large to track.\n"
    "\n"
    "**THE METHOD** (the video, in this repo's words, in the note): a trunk from a skeleton under a Skin modifier "
    "and a subdivision, applied, thinned by dissolving every second loop, sculpted and baked. That is the "
    "standard's Addendum A.2 and A.3 in use. A crown of cards, each a 3D branch baked onto a plane, cut to its "
    "outline, bent, its origin at the branch base. Cards are merged to cut draw calls, and the wind is on the "
    "cards.\n"
    "\n"
    "**ZOO TODAY** (`zoo/zoo_keeper/recipes/street_tree.py`, `core/tree_forms.py`).\n"
    "- **How a tree is grown.** Species angles, a tapered six-sided trunk and leader, box twigs, a faceted box "
    "\"leaf cluster\" at every tip: the low-poly retro read the walker kept on 2026-09-13.\n"
    "- **What it costs:** 2,220 to 3,564 triangles, 4 primitives and 203 to 320 KB, on 3 to 5 m slots.\n"
    "- **Wind exists:** a `Sway` UV layer on the crown (Zoo 1.56.0).\n"
    "- **Cards were tried.** `params.crown = \"cards\"` keeps 0.69.2's four crossed cutout planes, judged not ready "
    "on cold run 9032.\n"
    "- **At night in a level**, a trunk under a few square green masses "
    "(`docs/findings/weighted_normals/level_extraction_pair.png`).\n"
    "\n"
    "**THE WORK, by owner.**\n"
    "- **Zoo, the trunk.** The skeleton Zoo already grows, under a Skin modifier with a radius per vertex: one "
    "connected trunk instead of intersecting cylinders. Bark rides as a baked normal map, which is Addendum A.4's "
    "trial 3, the procedural bake source. The tree may be its first use.\n"
    "- **Zoo, the crown.**\n"
    "  - A branch generator per species: twigs and leaves as 3D geometry, baked into one card atlas of colour, "
    "alpha and normal. One atlas per species, shared by every tree of it.\n"
    "  - Cards bent and placed at the skeleton's tips, their origins at the branch bases, and merged by material "
    "per tree. Target: the same 4 primitives.\n"
    "  - The `Sway` layer written on the cards.\n"
    "- **Lux, god rays.** Fake shafts: additive quads or cones under a canopy, angled along the sun.\n"
    "  - Lux's streetlight cone (`lux_light_cone.gdshader`: a flat alpha gradient, faded as the camera walks "
    "under it) is the same kind of object.\n"
    "  - Daylight slots with a low sun only (morning, afternoon, evening); never midnight.\n"
    "  - Volumetric fog does not render on GL Compatibility (Lux measured it), and screen-space shafts are the "
    "post-process class CLAUDE.md defers.\n"
    "\n"
    "**PRICE FIRST: alpha-tested cards are the costliest surface this renderer draws.**\n"
    "- **The house measurement.** Cold run 9185 priced the fence fabric alpha-tested against blended. Alpha test "
    "cost +3.3 draws a view, consistent with a shadow pass, and +1.05 to +1.59 ms where the fence filled the view. "
    "Blended was cheaper, and casts no shadow.\n"
    "- **For a crown, neither is free.**\n"
    "  - Blended cards cannot sort against each other, and a tree without a shadow reads wrong.\n"
    "  - Alpha-tested cards pay the shadow pass, and the discard and overdraw under the crown, where a player on "
    "the sidewalk stands.\n"
    "- **Triangles** would go up about 7x a tree. That is not the budget (CLAUDE.md, draw calls are), but it trips "
    "the genome's regression detector. A budget class (item 214's \"hero\") makes the jump a stated exception.\n"
    "- **So the first step is a price, not a tree:** one species' crown of cards, alpha-tested and blended, on a "
    "street of them, at fixed stations against a control.\n"
    "\n"
    "**NOT DECIDED HERE.**\n"
    "- **Ingesting the reference as it is.** Possible: Zoo's ingest keeps authored normals since 1.87.0. But it is "
    "one 21 m hill tree, not a Delco street tree, and the deliverable is the generator. The reference is a brief, "
    "not a part.\n"
    "- **The look.** Whether the retro read the walker kept on 2026-09-13 gives way to the reference's is the "
    "walker's call. Their 2026-10-02 call, that realism replaces the retro look, points that way.\n"
    "- **Which species first.** `red_maple`, the default form, unless the walker says otherwise.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: 215's last line is not the end of the file")
    if "\n**216. " in text:
        sys.exit("refusing: an item 216 already exists")
    text += ITEM_216
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 216 opened; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
