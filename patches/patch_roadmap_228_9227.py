"""Roadmap 228: the parkland recipe proven in cold run 9227.

Replaces 228's status block and adds 9227's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_9227.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS_TAIL = (
    "(`docs/cold_runs/cold_9226/`); 9227 (parkland) and 9228 (roadside) run next. The walker's: "
    "the near band 4 m past the fence reads as a dark wall of windows down the main road at dusk "
    "(9225), and a container's near-white roof reads as a pale slab over the roofline from an "
    "elevated view (9226).*\n"
)
NEW_STATUS_TAIL = (
    "(`docs/cold_runs/cold_9226/`). Cold run 9227 (county_hospital_001, 0 interventions) proved "
    "`parkland`: 273 trees in three modules, 12 draws, ranks of crowns over the hospital's "
    "roofline from every elevated view and a line of trees at the road's end, +14 draws a "
    "heading median and no frame time (`docs/cold_runs/cold_9227/`); 9228 (roadside) runs "
    "next. The walker's: the near band 4 m past the fence reads as a dark wall of windows down "
    "the main road at dusk (9225); a container's near-white roof reads as a pale slab over the "
    "roofline from an elevated view (9226); and on 9227's parkland, \"those trees in the "
    "distance are a little lazy imo (giant lolipops vs. trees)\": step F, the backdrop tree "
    "redrawn with a real silhouette, forked limbs under a lobed crown, a conifer and a bare "
    "form, laid in clusters rather than ranks, priced as the rest were.*\n"
)
BODY_ANCHOR = (
    "A darker, dirtier "
    "roof in Zoo, or the near band stood further off at a yard, are the two answers.\n"
)
ADDED = (
    "\n**PARKLAND PROVEN, cold run 9227** (`docs/cold_runs/cold_9227/NOTES.md`): 0 interventions, "
    "0 retries; `surroundings_of` decided `parkland` from `county_hospital`; Lot laid 273 "
    "`backdrop_tree` slots in three sizes (87 at 5 x 5 x 7 m, 103 at 7 x 7 x 10, 83 at 9 x 9 x "
    "13), Zoo's site kit built the three modules PASS, Level Factory shipped `273 instances of 3 "
    "module(s) on their sides, 12 draw calls`. Seen in heavy rain at night: the strongest of the "
    "three recipes, ranks of faceted crowns standing over and behind the roofline from every "
    "elevated view, 7 to 13 m tall against the 2-storey hospital, and the road ending under a line "
    "of trees instead of the bare glow band. Priced against the package's own backdrop-off copy: "
    "+14 draws a heading median (+4 to +18), p95 median -0.01 ms inside the controls' 0.16 ms "
    "spread; the report's +484 draws at one heading is the harness's own occlusion flip "
    "(`split_perturbed`: the control's two passes there read 699 and 1,165), not the trees.\n"
    "- **The walker's verdict, 2026-10-10:** \"those trees in the distance are a little lazy imo "
    "(giant lolipops vs. trees)\". The species is a trunk box under one twelve-by-six faceted "
    "sphere at three sizes (Zoo 1.96.0, 132 triangles), and from above the belt reads as a row "
    "of the same lollipop.\n"
    "- **Step F, the backdrop tree redrawn** (Zoo, then Lot's belt): a silhouette that reads as a "
    "tree at 20 to 90 m, which is a trunk that flares at the foot and forks into two to four "
    "limbs, a crown of several overlapping lobes at different heights with an irregular outline "
    "and daylight under it, in three or four forms (a broad oak-like crown, a tall vase-shaped "
    "elm, a layered conifer, a bare winter tree of limbs alone) at a backdrop budget of a few "
    "hundred triangles, bark and vegetation still two materials and one MultiMesh a module a "
    "side; the belt laid in clusters with gaps between them and the forms mixed, not ranks of "
    "one tree; the near belt further off the fence on a small plate. Priced at the same "
    "stations against 9227's package: the parkland costs 14 draws a heading today, and a "
    "500-triangle tree in five modules is still under twenty.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS_TAIL) == 1, text.count(OLD_STATUS_TAIL)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS_TAIL, NEW_STATUS_TAIL)
    i = text.index(NEW_STATUS_TAIL)
    assert text[i + len(NEW_STATUS_TAIL):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: the parkland recipe proven in cold run 9227")


if __name__ == "__main__":
    main()
