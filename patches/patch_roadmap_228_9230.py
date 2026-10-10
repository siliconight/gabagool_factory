"""Roadmap 228: step F (the tree redraw) proven, seen and priced in cold run 9230.

Replaces the step-F part of 228's status block and adds 9230's record to its body. Each anchor
must match exactly once; nothing is written on a miss. The generated index is regenerated
afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_9230.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "STEP F IS LANDED, not yet seen in a level: Zoo 1.97.0 (`patches/patch_zoo_backdrop_3.py`), "
    "a trunk that flares and forks into three limbs under ten overlapping lobes, the form by the "
    "slot's proportions (a low oak, a round maple, a narrow elm), 548 triangles, census clean, "
    "rendered in `docs/findings/backdrop_kit/tree_forms_1_97_0.png`; Lot 0.110.0 "
    "(`patches/patch_lot_tree_belt.py`), six dims two a form, the belt in clusters of 4 to 9 with "
    "5 to 18 m of daylight between, 6 m off the fence. The two tally lines are fixed (Lot 0.109.1, "
    "Level Factory 0.175.1). A parkland re-run (county_hospital_001 from 9227) shows the walker "
    "the trees and prices them; the borough's seven modules are PRICED by cold run 9229"
)
NEW_STATUS = (
    "STEP F IS PROVEN, SEEN AND PRICED in cold run 9230 (county_hospital_001 rebuilt from 9227 "
    "on the same seed, 0 interventions, 0 retries; `docs/cold_runs/cold_9230/`): Zoo 1.97.0 "
    "(`patches/patch_zoo_backdrop_3.py`), a trunk that flares and forks into three limbs under "
    "ten overlapping lobes, the form by the slot's proportions (a low oak, a round maple, a "
    "narrow elm), 548 triangles; Lot 0.110.0 (`patches/patch_lot_tree_belt.py`), six dims two a "
    "form, the belt in clusters of 4 to 9 with 5 to 18 m of daylight between, 6 m off the fence. "
    "Lot laid 185 trees where 9227 laid 273, Level Factory shipped `185 instances of 6 module(s) "
    "on their sides, 24 draw calls` (9227: 3 modules, 12). Seen: the road ends under trees that "
    "fork, the glow between their limbs; from the elevated views a wood in clumps with the fence "
    "showing between them and a broad crown twice its neighbours' height, where 9227's ranks of "
    "balls on sticks closed every edge; up close, one crown filling `elev_E`, the lobes read as "
    "faceted boulders. Priced against the package's own backdrop-off copy: +22 draws a heading "
    "median (+4 to +36; 9227's twelve MultiMeshes cost +14) and p95 +0.10 ms median on a 2.03 ms "
    "frame, over the controls' 0.03 ms spread on 23 of 25 headings, the first parkland frame cost "
    "the harness can see, in the band 9228's roadside read (+0.20); the lever, one module a form "
    "with the size as instance scale, is recorded and not taken. The walker's eye on 9230's "
    "sheet is the next call: whether the near band wants a minimum distance from an elevated "
    "station, and whether the lobes want the guides' card method before the forms become species. "
    "The two tally lines are fixed (Lot 0.109.1, Level Factory 0.175.1); the borough's seven "
    "modules are PRICED by cold run 9229"
)
BODY_ANCHOR = (
    "Cold run 9230 (the hospital's parkland, from 9227) is running with Zoo 1.97.0's tree and Lot "
    "0.110.0's clustered belt.\n"
)
BODY_NEW = (
    "Cold run 9230 (the hospital's parkland, from 9227) ran with Zoo 1.97.0's tree and Lot "
    "0.110.0's clustered belt, below.\n"
    "\n"
    "**STEP F PROVEN, cold run 9230** (`docs/cold_runs/cold_9230/NOTES.md`): county_hospital_001 "
    "rebuilt on the landed set at 0 interventions, 0 retries, the seed 9227 picked (9107), so its "
    "sheet is 9227's sheet of the same level with the new trees. Lot: `LOT_BACKDROP_PLACED: recipe "
    "parkland, 185 piece(s) (backdrop_tree 185) by side (N 58, S 56, E 36, W 35), 6 module(s), 0 "
    "water tower(s)` (9227: 273 in 3), the six dims two a form: oaks 8 x 8 x 8 (37) and 11 x 11 x "
    "12 (27), maples 5 x 5 x 7 (27) and 7 x 7 x 10 (32), elms 4 x 4 x 9 (24) and 6 x 6 x 13 (38); "
    "Zoo's site kit built all six PASS; Level Factory shipped `185 instances of 6 module(s) on "
    "their sides, 24 draw calls` (9227: 12). Seen (`edge_before_after.png`, the same three road "
    "ends and four elevated views as 9227, night and rain): down road 0 to the east edge the road "
    "ends under trees that fork, a trunk, two or three limbs, lobes at different heights, the glow "
    "showing between the limbs, where 9227's ended under balls on sticks; from the north a cluster "
    "of five with a broad oak-form crown twice its neighbours' height and the fence and glow "
    "showing between the clusters, where 9227's ranks closed the edge; from the south the densest "
    "stretch, flat broad crowns against tall narrow ones; from the west one tree alone before the "
    "fence. For the walker's eye: from the east one near crown still fills the foreground (the "
    "belt's inner edge at 6 m now, 2.5 in 9227) and up close its lobes read as a pile of faceted "
    "boulders rather than foliage. Priced against the package's own backdrop-off copy, heading by "
    "heading against the controls' mean (`price_vs_mean.py`): +22 draws a heading median (+4 to "
    "+36) and p95 +0.10 ms median (+0.01 to +0.44) on a 2.03 ms frame, over the controls' 0.03 ms "
    "spread on 23 of 25 headings; 9227's twelve MultiMeshes cost +14 draws and no frame time, "
    "9230's twenty-four cost +22 and a tenth of a millisecond, the cost following the submissions "
    "(six modules on four sides) and not the trees (two thirds the instances). The harness's flip "
    "at `attacker_spawn_0` fell the same way in all three runs, so the median is clean; the "
    "controls' own worst disagreement (0.44 ms) equals the subject's worst, so the worst heading "
    "proves nothing. The lever if the tenth matters on the low-end target: one module a form with "
    "the slot's size as instance scale, three modules and twelve draws as 9227, at the cost of the "
    "six dims' varied proportions; recorded, not taken. Two calls for the walker: a minimum "
    "distance from an elevated station for the near band, and the guides' alpha-card method for "
    "the lobes (step G) before the forms become species. Not proven: the parkland by day, the "
    "player's eye at the fence, the price on the low-end target.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert text.count(NEW_STATUS) == 0 and "STEP F PROVEN, cold run 9230" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_NEW).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: step F proven, seen and priced in cold run 9230")


if __name__ == "__main__":
    main()
