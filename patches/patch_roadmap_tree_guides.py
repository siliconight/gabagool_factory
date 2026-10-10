"""Roadmaps 216 and 228: the walker's two Pennsylvania tree guides filed; step G named for the backdrop.

Replaces 216's and 228's status blocks and adds a paragraph to each body. Each anchor must match
exactly once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_tree_guides.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S216_OLD = (
    "*STATUS: OPEN 2026-10-09 -- filed, not started. The walker's ask: better-looking trees, with a "
    "CC0 reference tree, the method it was made by, and god rays through canopies "
    "(`docs/reference/TREE_REFERENCE.md`). Zoo's six tree species are grown from a skeleton under "
    "faceted box leaf clusters: 2,220-3,564 triangles and 4 primitives each. The reference is a "
    "sculpted trunk under about 800 bent, alpha-tested branch cards: about 21,000 triangles in 3 "
    "materials with 2048 maps. Next: price an alpha-tested crown before building one.*\n"
)
S216_NEW = (
    "*STATUS: OPEN 2026-10-10 -- filed, not started; the method is now written down. The walker's "
    "ask: better-looking trees, with a CC0 reference tree, the method it was made by, and god rays "
    "through canopies (`docs/reference/TREE_REFERENCE.md`), and on 2026-10-10 two companion guides "
    "(`docs/reference/PA_NATIVE_TREES_PHILLY_DELCO.md`, `docs/reference/BLENDER_SCRIPTING_PA_TREES.md`): "
    "35 Pennsylvania species with their silhouettes, habitats and weighted palettes, and the "
    "pipeline a recognisable tree is built by (a skeleton graph before geometry, tapered tubes with "
    "transported frames, foliage sockets on fine branches, space colonisation inside overlapping "
    "crown lobes, LODs that keep the species' masses, a Godot export checklist). Zoo's six tree "
    "species are grown from a skeleton under faceted box leaf clusters: 2,220-3,564 triangles and "
    "4 primitives each. Next: price an alpha-tested crown before building one, then the guide's "
    "first milestone, three leaf-off skeletons (white oak, tuliptree, sycamore) that read as "
    "different trees in black silhouette.*\n"
)
B216_ANCHOR = (
    "- **Which species first.** `red_maple`, the default form, unless the walker says otherwise.\n"
)
B216_ADDED = (
    "\n**THE GUIDES, 2026-10-10.** The walker: \"do these docs help with making trees look more "
    "realistic?\" They do, in two ways. For the STREET tree, the scripting guide is the pipeline "
    "this item needs: a branch graph with ids, attachment positions and radii before any mesh; tubes "
    "with a transported frame (no frame flips); sockets for foliage on living fine growth; "
    "authored major limbs with procedural twigs, or space colonisation inside several overlapping "
    "crown lobes with no-growth volumes for buildings; bark UVs by length and circumference; two "
    "materials; LODs that remove invisible twigs and merge foliage units but keep the sycamore's "
    "pale limbs and the elm's vase; a glTF handoff checklist. Its budgets (6k-20k triangles a "
    "gameplay tree, 1k-6k mid, a few hundred to 1.5k far) are authored starts to be priced here. "
    "The species guide gives the library plan: twelve recognisably different species first (white "
    "oak, northern red oak, tuliptree, red maple, beech, sycamore, silver maple, black cherry, "
    "black walnut, dogwood, sassafras, redcedar), forest, edge and open-grown forms of each, and "
    "placement by habitat patch before species (a 1990s setting has no emerald-ash-borer dead "
    "ash). Both say their numbers are authored starting values, not measurements: fills for "
    "blanks, never overrides. The BACKDROP tree's share of them is roadmap 228's step G.\n"
)

S228_OLD_TAIL = (
    "shows the walker the trees and prices them; the borough's seven modules are priced by 9229.*\n"
)
S228_NEW_TAIL = (
    "shows the walker the trees and prices them; the borough's seven modules are priced by 9229. "
    "STEP G, from the walker's tree guides of 2026-10-10 (`docs/reference/PA_NATIVE_TREES_PHILLY_DELCO.md`, "
    "`BLENDER_SCRIPTING_PA_TREES.md`): the backdrop's three invented forms become the guide's "
    "species silhouettes (crown-start and width as shares of height, limb counts and angles: an "
    "open white oak, a red maple, a tuliptree with a leader, an elm's vase, a pin oak's three "
    "limb zones, a sycamore with pale upper wood, a redcedar column), forest forms far and open "
    "forms near, the belt's mix by recipe from the guide's weighted palettes, and per-instance "
    "colour for the sycamore's wood and the season; not started.*\n"
)
B228_ANCHOR = (
    "are about twelve more MultiMeshes than three; the parkland re-run measures it against "
    "9227's +14 draws.\n"
)
B228_ADDED = (
    "\n**STEP G, named 2026-10-10: the guide's species instead of invented forms.** The walker's "
    "tree guides (roadmap 216) carry what the backdrop tree lacks: species silhouettes as numbers. "
    "`tree_form` decides oak / maple / elm by the slot's h / w with rows I made up; the scripting "
    "guide's table gives, for mature forms, crown-start over height (C/H) and width over height "
    "(W/H) with the limb architecture that matters: white oak open C/H 0.18-0.35, W/H 0.80-1.20, "
    "5-9 heavy scaffolds at 45-78 degrees from vertical; northern red oak 0.28-0.50 and 0.60-0.90, "
    "ascending; red maple 0.30-0.50 and 0.55-0.85, rounded, ascending limbs; tuliptree forest "
    "0.55-0.75 and 0.30-0.55, a persistent leader; American elm 0.25-0.45 and 0.75-1.15, limbs "
    "ascending then arching out, fine drooping tips; pin oak with lower limbs at 95-115 degrees, "
    "middle 65-90, upper 25-55; sycamore 0.25-0.50 and 0.65-1.00, few large divisions and pale "
    "upper wood; redcedar 0.05-0.25 and 0.30-0.60, a column. In cones and lobes every one of "
    "these is a row of shares like `TREE_FORM_ROWS`, and a Lot piece names the species in its "
    "stem the way `pole_flyers` names its form. The species guide's growth-context table makes "
    "the far belt forest-grown (long clear trunk, small high crown) and the near belt open-grown "
    "(broad crown, low limbs), and its weighted palettes give each recipe its mix: a hospital's "
    "parkland an upland woodland far (tuliptree 25, white oak 20, red oak 20, beech 15, red maple "
    "10, pignut hickory 10) with open oaks and maples near; the roadside and the yards the "
    "old-field edge (black cherry 30, sassafras 25, redcedar 20, walnut 15, red maple 10). The "
    "sycamore's pale limbs and early-autumn crowns are per-instance colour on the two materials, "
    "never a material each (the draw-call rule). Two structural variants a species before seeds, "
    "as the guide says: eight modules a belt is still under thirty-two draws. The guides' numbers "
    "are authored starts, not measurements; the walker's eye on 9230's frames judges the current "
    "forms first.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for old in (S216_OLD, B216_ANCHOR, S228_OLD_TAIL, B228_ANCHOR):
        assert text.count(old) == 1, (text.count(old), old[:60])
    text = text.replace(B216_ANCHOR, B216_ANCHOR + B216_ADDED).replace(S216_OLD, S216_NEW)
    text = text.replace(B228_ANCHOR, B228_ANCHOR + B228_ADDED).replace(S228_OLD_TAIL, S228_NEW_TAIL)
    i = text.index(S216_NEW)
    assert text[i + len(S216_NEW):].startswith("\n**216. "), "216's status left its heading"
    j = text.index(S228_NEW_TAIL)
    assert text[j + len(S228_NEW_TAIL):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmaps 216 and 228: the tree guides filed, step G named")


if __name__ == "__main__":
    main()
