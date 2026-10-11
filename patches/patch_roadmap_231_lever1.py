"""Roadmap 231: the first lever landed, proven and priced (cold run 9236), its own gate tripped and
answered, the second lever landed with it (Lot 0.115.0, Level Factory 0.178.0), cold run 9237 to
price it. Replaces 231's status block (asserted once) and appends two body paragraphs after the
item's last paragraph (the path note). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_231_lever1.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-10-11 -- measured, not started. Cold run 9233 priced a street for the first time:"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- the first lever is LANDED, PROVEN and PRICED, and it tripped its own "
    "gate; the second is landed with the answer and in flight. Lot 0.114.0 ships a site's road paint as one "
    "OBJ mesh per paint colour beside the scene (each quad's UVs carrying the per-marking wear offset, one "
    "MeshInstance3D and one material a colour, lightmapped through the wavefront sidecar Level Factory "
    "0.177.1 asks for `generate_lightmap_uv2`); cold runs 9234 and 9235 stopped at the export's closure gate "
    "at 0 interventions because first the Lot adapter (0.177.2) and then the export's assembly step "
    "(0.177.3) dropped the new sibling file kind; cold run 9236 (restaurant_row_001 on 9233's brief, 0 "
    "interventions, closure clean, both meshes among the 474 models lightmapped) priced it against 9233's "
    "package at the fixed stations: the site scene's pool from 795 box meshes and 178 materials to 568 and "
    "55 (`tools/draw_census.py`: the 227 per-marking boxes and 125 materials become two meshes and two "
    "materials), -107 draws and -0.36 ms p95 a heading median against the controls' mean on a 6.14 ms frame "
    "(noise floor 0.08 ms; 39 of 53 headings faster beyond it, 4 slower by at most 0.41; the worst headings "
    "-1.0 to -1.2 ms, player_start_19 yaw 90 from 19.0 to 17.9 ms) -- the second street's +107 draws given "
    "back whole and two thirds of its +0.55 ms. The same seven stations shot in both packages "
    "(`docs/cold_runs/cold_9236/paint.png`) read alike bar for bar, the wear in the same places. BUT the "
    "paired-light census read each level-wide paint mesh under 21 live lights against the engine's cap of 8 "
    "(a mesh whose box is the plate reaches the failing tube behind every storefront), so Lot 0.115.0 cuts "
    "the paint into 32 m cells a colour (`PAINT_CELL_M`, the colour's one material shared) and takes the "
    "second lever with it: `mesh_tile(site_spec)` reads the spec's `render` and cuts the plate families to "
    "`MESH_TILE_BAKED` (32 m) where Level Factory 0.178.0 says the lights bake (`render.lights_baked`, the "
    "export's own default in one constant; `export --no-bake-lights` says so out loud). Cold run 9237 prices "
    "both against 9236's package; the gate is the paired census on its package, no mesh over 8 live lights. "
    "Owner: Lot, with Level Factory's perf census as the gate.*")

BODY_TAIL = ("Owner: Lot 0.114.0 and Level Factory 0.177.1, a cold run on 9233's brief and the price "
             "against 9233's package.")
BODY_ADD = """

**LEVER 1 LANDED, PROVEN AND PRICED, 2026-10-11** (`docs/cold_runs/cold_9236/NOTES.md`; the two stops before it in `cold_9234/` and `cold_9235/`). Lot 0.114.0 (`patches/patch_lot_marks_obj.py`): `_marking_meshes` writes the road's paint and the fields' bay lines as quads in one OBJ a paint colour beside the scene, `v` at the paint's top face, `vt` = world xz over the pack's tile plus `paint_offset`'s hash of the marking, two faces a quad, `cull_mode = 2`, no collision; the scene declares each as a Mesh ext_resource and stands it with one material (`_mat_sub(..., triplanar=False)`, UV1 at scale 1). Six decimals in the file: four turned a 0.3 m bay tick's direction by 4.5e-4 on a diagonal road and failed eight tests. Level Factory 0.177.1 (`patches/patch_lf_obj_lightmap.py`): `light_bake.mark_imports` sets `generate_lightmap_uv2=true` on every `*.obj.import` and the bake re-imports before baking, so the meshes bake like models. Then two runs to ship a new file kind beside Lot's scene, each stopped by the closure gate at 0 interventions and each the shape of cold run 9016's skins: 0.177.2, the Lot adapter's suffix list (`collect_outputs` published .tscn/.json/.csv/.glb/.gd/.png); 0.177.3, the export's assembly step, which copies the scene and three named sibling DIRECTORIES (`skins/`, `cover/`, `signs/` -- "THE LIST IS THE CONTRACT") and the meshes are sibling files. A new kind beside Lot's scene needs a line in both lists, and nothing before the closure gate notices a Mesh ext_resource that resolves to nothing -- the bake then fails with "bake.tscn did not open". Cold run 9236 priced it (above): -107 draws and -0.36 ms p95 a heading median, the worst headings -1.0 to -1.2 ms, the pool's 227 marking boxes and 125 materials gone and nothing else in the pool moved; fourteen frames at seven stations in both packages read alike, the wear in the same places (`paint.png`, `tools/paint_stations.py`). And the paired census, read off the same perf reports: the two paint meshes at 21 live lights each against the cap of 8, beside the horizon glow's 235 and one roof's 10 that 9233's package already carried. A mesh whose box is the whole plate pairs with every live light on the level; the engine binds the first 8.

**LEVER 2 LANDED WITH THE ANSWER, 2026-10-11, NOT YET MEASURED** (Lot 0.115.0, `patches/patch_lot_mesh_tile.py`; Level Factory 0.178.0, `patches/patch_lf_render_in_site_spec.py`; both proven on clones of the landed set, 788 and 2,214 passed). The paint is cut into cells: one mesh a colour a `PAINT_CELL_M` (32 m) square by each marking's centre, the colour's one material shared, so each piece pairs with the lights within its reach and culls as a piece. The plate tile follows the bake: `mesh_tile(site_spec)` reads the spec's `render` -- `mesh_tile_m` names the tile outright, else `lights_baked` true takes `MESH_TILE_BAKED` (32 m), else `MESH_TILE` (8 m) and a spec that says nothing draws byte for byte as before -- and `_outdoor_nodes` cuts the plate families (ground, paths, courtyards, fields, yards, perimeter, street slabs, frontages) to it; covers and blockers keep the 8 m law, being under it. Lot cannot know what the export will do, so the export's own default says it: `BAKE_LIGHTS_CLI_DEFAULT` in `export.py`, read by `main.py`'s `--bake-lights` and written by `_write_site_spec` as `render.lights_baked` into both the greybox and the themed spec; `export --no-bake-lights` says out loud that the site was drawn for a bake it did not get. On the kerb probe the boxes go 999 to 307 under the baked tile with every shape and material unchanged. The caller-less `_yaw_quad_node` and the `uv_offset` only it passed to `_mat_sub` are gone. Cold run 9237 (staged, 9233's brief) prices both against 9236's package and reads the paired census on its package: the gate is no mesh over 8 live lights; the number moves if the census says so. Zoo's `PLATE_TILE` and Deli Counter's `SLAB_TILE` are the same law indoors and have not moved; each is its own decision, after this one is measured."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF count means something changed"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "231's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    assert text.count(BODY_TAIL) == 1, ("231's last paragraph not found once", text.count(BODY_TAIL))
    assert "LEVER 1 LANDED, PROVEN AND PRICED" not in text, "already applied"
    new = text[:i] + STATUS_NEW + text[j:]
    k = new.find(BODY_TAIL) + len(BODY_TAIL)
    assert new[k:].strip() == "", "231 is no longer the last item: re-anchor the body addition"
    new = new[:k] + BODY_ADD + "\n"
    # the status block must still adjoin its heading
    assert "\n\n**231. " in new[new.find(STATUS_NEW):new.find(STATUS_NEW) + len(STATUS_NEW) + 40]
    RM.write_bytes(new.encode("utf-8"))
    print("roadmap 231: status replaced, two paragraphs appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
