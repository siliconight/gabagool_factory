"""Roadmap 228: the roadside recipe proven in cold run 9228; the three recipes closed, step F open.

Replaces 228's status block and adds 9228's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_9228.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS_TAIL = (
    "heading median and no frame time (`docs/cold_runs/cold_9227/`); 9228 (roadside) runs "
    "next. The walker's: the near band 4 m past the fence reads as a dark wall of windows down "
    "the main road at dusk (9225); a container's near-white roof reads as a pale slab over the "
    "roofline from an elevated view (9226); and on 9227's parkland, \"those trees in the "
    "distance are a little lazy imo (giant lolipops vs. trees)\": step F, the backdrop tree "
    "redrawn with a real silhouette, forked limbs under a lobed crown, a conifer and a bare "
    "form, laid in clusters rather than ranks, priced as the rest were.*\n"
)
NEW_STATUS_TAIL = (
    "heading median and no frame time (`docs/cold_runs/cold_9227/`). Cold run 9228 "
    "(gas_stop_001, 0 interventions) proved `roadside`: 245 trees in a thin belt and 13 far "
    "warehouses, 258 instances in 21 draws, +25 draws a heading median and p95 +0.20 ms median, "
    "twice the controls' 0.09 ms spread on a 4.8 ms frame, the first recipe with a frame cost the "
    "harness can see (`docs/cold_runs/cold_9228/`). Every "
    "recipe is proven at 0 interventions: borough (9225), yards (9226), parkland (9227), "
    "roadside (9228). The walker's: the near band 4 m past the fence reads as a dark wall of "
    "windows down the main road at dusk (9225); a container's near-white roof reads as a pale "
    "slab over the roofline from an elevated view (9226); and on 9227's parkland, \"those trees "
    "in the distance are a little lazy imo (giant lolipops vs. trees)\", which 9228's clear "
    "night shows plainer still. STEP F IS DRAFTED, not landed: Zoo 1.97.0 "
    "(`patches/patch_zoo_backdrop_3.py`, a forking trunk under seven lobes in three forms by the "
    "slot's proportions, 27 pure tests) and Lot 0.110.0 (`patches/patch_lot_tree_belt.py`, six "
    "dims two a form, clusters of 4 to 9 with 5 to 18 m of daylight between, the belt 6 m off "
    "the fence); the renders and the next parkland run judge them.*\n"
)
BODY_ANCHOR = (
    "(the authorship guide's call). And the near belt starts 2.5 m off the fence, so from an "
    "elevated view on a small plate a crown fills the foreground larger than the building.\n"
)
BODY_ANCHOR_2 = (
    "stations against 9227's package: the parkland costs 14 draws a heading today, and a "
    "500-triangle tree in five modules is still under twenty.\n"
)
ADDED = (
    "\n**ROADSIDE PROVEN, cold run 9228** (`docs/cold_runs/cold_9228/NOTES.md`): 0 interventions, "
    "0 retries; `surroundings_of` decided `roadside` from `gas_station` on a `strip`; Lot laid "
    "245 `backdrop_tree` (102 at 5 x 5 x 7 m, 73 at 7 x 7 x 10, 70 at 9 x 9 x 13) in the thin "
    "belt and 13 `backdrop_warehouse` in the far band, Zoo's site kit built all six modules PASS, "
    "Level Factory shipped `258 instances of 6 module(s) on their sides, 21 draw calls` round a "
    "240 x 120 m plate (the fence 8 runs, 753.7 m). Seen on a clear night: the road's lamps end "
    "against a line of crowns instead of an empty horizon; from the elevated views ranks of round "
    "crowns stand directly behind the storefront row and the near belt's 9 m crowns loom in the "
    "foreground, the plainest frame yet of the walker's verdict. Priced against the package's own "
    "backdrop-off copy: +25 draws a heading median (0 to +36), p95 median +0.20 ms against a "
    "controls' spread of 0.09 ms and no pass flip, worst heading +0.73 ms: a fifth of a "
    "millisecond on the heaviest level of the three (1,230 draws, 4.8 ms a frame), the first "
    "recipe the harness can see; the tree redraw keeps the draw count and is priced here next.\n"
    "- **The three recipes and the borough are all proven at 0 interventions** (9225 to 9228), "
    "each priced within its controls' spread, the draws a heading +14 to +43. What stands past "
    "the edge now differs by level, as the walker asked; what the trees look like is step F.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert "PRICE_9228" not in NEW_STATUS_TAIL + ADDED, "fill the price before applying"
    assert text.count(OLD_STATUS_TAIL) == 1, text.count(OLD_STATUS_TAIL)
    assert text.count(BODY_ANCHOR_2) == 1, text.count(BODY_ANCHOR_2)
    text = text.replace(BODY_ANCHOR_2, BODY_ANCHOR_2 + ADDED).replace(OLD_STATUS_TAIL, NEW_STATUS_TAIL)
    i = text.index(NEW_STATUS_TAIL)
    assert text[i + len(NEW_STATUS_TAIL):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: the roadside recipe proven in cold run 9228; step F drafted")


if __name__ == "__main__":
    main()
