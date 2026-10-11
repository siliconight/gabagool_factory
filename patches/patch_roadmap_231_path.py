"""Roadmap 231: the path for the markings, settled after reading the bake -- an OBJ per paint colour,
lightmapped through the import pass, the wear offset kept in explicit UVs.

Appends the note to 231's body. The anchor must match exactly once; nothing is written on a miss.
The generated index is regenerated afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_231_path.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

BODY_ANCHOR = "Owner: Lot, with Level Factory's perf census as the gate.\n"
BODY_ADDED = (
    "\n**THE PATH FOR THE MARKINGS, SETTLED 2026-10-12** (`docs/findings/street_draws/README.md`): a "
    "MultiMesh is not lightmapped -- `light_bake.py` bakes inline primitive meshes (`add_uv2`) and "
    "imported models (the sidecar's `meshes/light_baking`), and a `MultiMeshInstance3D` is neither -- so "
    "merged markings in that form would lose the baked lamp pools and read flat under every street "
    "lamp at night; an inline ArrayMesh needs Godot's packed vertex layout and its own UV2. The form "
    "that keeps the bake is the buildings': a model beside the scene, imported through the sidecar "
    "pass. Lot writes one OBJ per paint colour (every marking a quad; 9233's 125 markings, 227 tiled "
    "boxes and 125 materials become 2 meshes and 2 materials), one `MeshInstance3D` per colour with "
    "the one paint material mapping by UV1, and each quad's UVs carry what the per-marking material "
    "carried -- world position times the pack's tile scale plus `paint_offset`'s hash -- so the wear "
    "offset survives with no second step. The lightmap UV comes from the import: measured on Godot 4.7 "
    "with a one-quad OBJ imported headless, the `wavefront_obj` importer's params are "
    "`generate_lightmap_uv2=false` and `generate_lightmap_uv2_texel_size=0.2`, which Level Factory's "
    "`mark_imports` sets as it sets the GLBs' `meshes/light_baking` (a point release). The 8-light cap "
    "applies to the merged mesh as to a bigger tile, so the paired census gates both. Lot's tests that "
    "pin `mark_<n>_<kind>` nodes and per-marking materials move to the OBJ's quads and the one "
    "material; `site.markings.json` is unchanged. Owner: Lot 0.114.0 and Level Factory 0.177.1, a cold "
    "run on 9233's brief and the price against 9233's package.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "THE PATH FOR THE MARKINGS, SETTLED 2026-10-12" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 231: the markings' path settled")


if __name__ == "__main__":
    main()
