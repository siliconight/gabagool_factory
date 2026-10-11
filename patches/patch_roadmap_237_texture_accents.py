"""Roadmap 237: a second pass of texture accents -- where it lives in the DAG, in three tiers, and
what it must not be. Filed from the walker's guide, 2026-10-11
(`docs/reference/BLENDER_SECOND_PASS_TEXTURE_ACCENTS_GUIDE.md`). Appends the item after 236
(asserting the roadmap still ends with 236's body); nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_237_texture_accents.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL_236 = ("smoke's overdraw grows with screen area; a fire's light is a live light under the "
            "eight-lights-per-mesh cap.\n")

STATUS_237 = (
    "*STATUS: OPEN 2026-10-11 -- PLACED, NOT STARTED. The walker's guide is filed "
    "(`docs/reference/BLENDER_SECOND_PASS_TEXTURE_ACCENTS_GUIDE.md`) and its place in the DAG is "
    "decided below: tier A in Pixelcoat's pack recipes (`pixelcoat_build`), tier B as cause-driven "
    "vertex masks written by the tool that knows the cause and read by the shared material "
    "(`zoo_*_build`; the `Wear` channel already reaches Godot on both material paths), tier C the "
    "guide's full pass and bake for hero uniques at library time. Never runtime decals (GL "
    "Compatibility has none), never a unique texture an instance, never Patina's greybox pass. Behind "
    "roadmap 181 and the level-creation queue (the walker, 2026-10-11: levels before look work); tier "
    "A first.*")

ITEM_237 = """

**237. A second pass of texture accents: where it lives in the DAG, and what it must not be.** The walker's guide (2026-10-11, `docs/reference/BLENDER_SECOND_PASS_TEXTURE_ACCENTS_GUIDE.md`): an optional Blender pass over an ACCEPTED base material that adds selected emphasis -- local pigment variation, a directional fade, a repaint patch or stripe, contact polish, chipped paint showing primer and substrate, runoff and ground grime, fine grain -- every effect behind an explicit permission mask (`final = permission x placement x breakup x strength`), 70-90 % of a surface left alone, the base material preserved as a data-block, the stack baked to base colour / normal / ORM for export. Its placement rule is the authorship guide's: a mark needs a cause (`hand_contact`, `kick_zone`, `water_origin`, `ground_contact`, `repair_patch`, `protected_surface`), and noise only shapes a region a cause already chose.

**WHERE IT LIVES, grounded in what the tools do today.** The base coat in this factory is a Pixelcoat pack -- albedo, normal, roughness, optional emissive and height, a wet variant -- resolved by Zoo at build into ONE material per (kind, theme) shared by every part of that kind in a building (`zoo_keeper/bpylayer/materials.py`), with each part carrying a `Wear` corner attribute that the material multiplies into albedo on both the flat and the skinned path (measured; `tools/wear_probe.py`). The guide's pass therefore splits into three tiers, each at a different stage:

- **Tier A -- texture-space layers, shared, free at runtime: Pixelcoat (`pixelcoat_build`).** The guide's broad pigment variation (7.1), fine paint grain and pores (7.7), brick / plaster / concrete and wood rules (7.9, 7.10) are tileable layers over a pack's albedo and roughness (and height where the pack carries one), per kind and theme, in the pack recipe -- `recipe.cavity_grime` is the one float of this that exists. One material a kind as now; no draw, no texture memory beyond the pack. First, because it is the cheapest and reaches every wall.
- **Tier B -- placement masks, cause-driven, generated: Zoo's builds (`zoo_kit_build`, `zoo_dressing_build`, `zoo_fixtures_build`, `zoo_roof_props_build`), with the cause supplied by whoever knows it.** The guide paints its masks; this factory derives them, because the cause is already in the generator: a recipe knows its handle, feet, pipe and sill (Zoo), a slot knows its door's kick zone and threshold (Deli Counter), site furniture knows its ground contact and the street's wet (Lot). Written into the part's vertex colour -- `Wear` today, one scalar; COLOR_0 carries four channels, so wear, dirt, fade and permission fit one attribute -- and read by the SHARED material: no new material, no new draw, no texture, which is the rule CLAUDE.md states for every variation (instance data, a vertex channel, an atlas UV). **B1**, with what ships: the albedo multiply places darkening, dirt and a tinted fade by vertex. **B2**, to price: chips, primer and substrate (7.4) and runoff shape (7.6) need `vertex mask x pack breakup texture`, which a StandardMaterial3D cannot express -- a shader the export's worldskin installs once per imported GLB (`assets/godot/zoo_worldskin.gd`, the CRT's `next_pass` precedent, priced the CRT's way) rather than a material a placement. Low-poly parts carry few vertices, so a vertex mask is a gradient across a box: the breakup lives in the texture, the region in the vertices, exactly the guide's split.
- **Tier C -- hero uniques: the guide's full pass and bake, as a Zoo species option, once per species at LIBRARY time, never per level.** The getaway van, a storefront's door, the objective's safe: things that exist once in a level and are read up close. The §18 recipe JSON is the contract (`surface_accents_recipe_v1`: masks, group inputs, bake size, the validation rules), the bake is Cycles in Blender (a 1,024 x 2,048 set is minutes and about 32 MiB raw for three maps; Godot's import compresses), and one or two a level is the budget until runtime data says otherwise.

**WHAT IT MUST NOT BE.** Not runtime decals: Godot 4.7 lists them for Forward+ and Mobile, and this game ships on GL Compatibility (the guide says so itself, G02). Not a unique baked texture per instance across a level: that is a material a placement, Deli Counter's one-mesh-in-VRAM discipline undone, and tens of megabytes a door. Not a Patina pass: Patina's posterised textures and decal pass dress the GREYBOX for the PS1 path, and the shipped surfaces of a themed level are Zoo's modules in Pixelcoat's packs. And not applied before the base is accepted: the guide's first rule and the walker's eye on a run's frames are the same gate -- an accent pass does not disguise a missing base colour design, a bad UV or a flat pack.

**WHAT WOULD CLOSE IT.** Tier A shipped in one pack family (brick or painted metal) and priced against the pack it replaces -- the same draws by construction, judged on frames at the fixed stations; tier B1 on one species with a cause (a door's kick zone and handle, from Deli Counter's slot), seen in a cold run; tier B2 priced as the CRT pass was, on and off, several stations, a no-change control; tier C on the van, its texture bytes recorded. The guide's acceptance table (§17) is the look check; `tools/wear_probe.py` is the instrument that says whether a mask reached the package at all."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**237. " not in text and "PLACED, NOT STARTED. The walker's guide is filed" not in text, "already applied"
    assert text.endswith(TAIL_236), ("the roadmap does not end with 236's body", text[-160:])
    assert text.count("\n\n**236. ") == 1, "236 not found once"
    text = text.rstrip("\n") + "\n\n" + STATUS_237 + ITEM_237 + "\n"
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 237 appended after 236; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
