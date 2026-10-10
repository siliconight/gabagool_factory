"""Roadmap 228, steps A and B proven in cold run 9224, and C, D, E landing.

Replaces 228's status block and adds 9224's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_step_b.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- step A shipped: Lux 0.73.0's `LuxHorizonGlow`, a ring every "
    "preset tunes (sodium at night, a haze by day; energy 0 draws nothing), seen on cold run "
    "9221's walk copy at the menu's stations (an orange band over the wall at eye level; from the "
    "elevated cameras the whole sky above the roofline goes sodium, the walker's dial) and priced "
    "at Level Factory's fixed stations against two controls: +1.0 draw, p95 +0.19 ms median "
    "inside the controls' 0.23 ms spread, 8 of 53 headings over it, the worst +1.81 ms on the "
    "level's heaviest frame, fill rate where the sky fills the view "
    "(`docs/findings/horizon_glow/`). Next: step B, the fence at the plate's edge (Lot, Zoo), "
    "priced with the glow standing; then the rowhome kit and the tower (Zoo), the bands by "
    "recipe (Lot), composition and the beacon (Level Factory, Lux).*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- steps A and B PROVEN in cold run 9224 (restaurant_row_001, "
    "0 interventions, 0 retries, findings 74 to 74): Lux 0.73.0's glow and Lot 0.107.0's fence "
    "stand at the edge (`LOT_PERIMETER_FENCED: 6 run(s), 589.7 m`), the wall's 78 tiles are gone "
    "from the scene, and at every edge station the road ends at the chain-link against the dusk "
    "sky instead of at the pale wall (`docs/cold_runs/cold_9224/edge_before_after.png`). Priced "
    "against 9223's package at the fixed stations: -5 draws a heading median (-28 to +17), frame "
    "time inside the controls' 0.80 ms spread. Step C (Zoo 1.95.0's rowhome and water tower), D "
    "(Lot 0.108.0's bands by recipe) and E (Level Factory 0.174.0's MultiMesh composition) are "
    "landing; cold run 9225 proves and prices them.*\n"
)
BODY_ANCHOR = (
    "- **Two refutations while writing it, kept:** a LuxRoot added under a SceneTree script's "
    "`_initialize` is not ready until the next frame (the selftest's first run found no glow); "
    "and a mesh stores its vertex colours in 8 bits, so a read-back is within 1/255 of what was "
    "written, not within 1/1000.\n"
)
ADDED = (
    "\n**STEP B SHIPPED, Lot 0.107.0** (`patches/patch_lot_perimeter_fence.py`): "
    "`site_fences.plan_perimeter` lays one chain-link run a side 0.25 m inside the wall, split "
    "where a side is longer than Zoo's widest module (120 m), never on a mission marker, as "
    "cover slots the same kit build makes; the wall keeps its collision and shows nothing "
    "(`_box_node(visual=False)`, `_wall_seen`); the roads that leave the plate end at the fence "
    "as they ended at the wall, a gate module being a later refinement; `perimeter.fence` false "
    "keeps the wall. 6 tests, all failing on 0.106.0.\n"
    "\n"
    "**A AND B PROVEN, cold run 9224** (`docs/cold_runs/cold_9224/NOTES.md`): 0 interventions, "
    "findings 74 to 74; `LOT_PERIMETER_FENCED: 6 run(s), 589.7 m` (two of 97.75 m on the long "
    "edges, one of 99.37 m on the short); `site.tscn` names `perim_` 16 times against 324. "
    "Shot before and after at the edge stations through each package's entry scene: the pale "
    "wall at the end of every road is a chain-link against the dusk sky, and from the elevated "
    "cameras the fence's posts and fabric stand where the band stood with the glow above the "
    "roofline. Priced on copies of the two packages, 9223's as the control: -5 draws a heading "
    "median (28 headings fewer, 25 more; -28 where the wall's tiles were most of the view, +17 "
    "where the runs are), frame time -0.74 ms median against the controls' mean with the "
    "controls' own spread at 0.80 ms, so inside the noise; this level stands at about 2,900 "
    "draws a heading, heavier than club_block_014's 1,150.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: steps A and B proven in cold run 9224")


if __name__ == "__main__":
    main()
