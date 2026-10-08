"""Roadmap: 207 NARROWED -- Lot 0.99.1 carries a stage light's aim with its
club, and cold run 9204 built all 44 club rigs where 9197 built 42; whether
the stages read lit is not measured, and the attempt that tried is retracted.
213 filed: the light bake freezes the club's stage show.

    python patch_roadmap_207_213.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_204_close.py left it once
its index was regenerated (1,309,501 bytes, LF, as read 2026-10-08): 207's
status line by its unique prefix, directly above its heading; 207's two NEXT
bullets; the file's last line, after which 213 goes. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S207_PREFIX = "*STATUS: OPEN 2026-10-08 -- cause measured, not fixed: Lot's `merge_lights` carries"
S207_NEW = (
    "*STATUS: NARROWED 2026-10-08 -- the refusal is fixed: Lot 0.99.1 carries a light anchor's `target` into "
    "site space with its `pos` (and refuses any numeric triple it has not classed), so cold run 9204 "
    "(club_block_014, 0 interventions) built 44 of 44 club rigs where 9197 built 42, `LUX_CLUB_REFUSED` is "
    "gone, and the stages throw 4.28 and 5.23 m in the shipped manifests. Not shown: the stages lit in a frame. "
    "The club's frames are dark, and the on/off test that tried was invalid -- the stage rig rebuilds its lamps "
    "from its resource at load, and the light bake bakes it -- so it is retracted, not counted. The bake also "
    "freezes the stage's colour cycle (item 213).*\n")

OLD_NEXT = (
    "- Lot: `merge_lights` carries `target` through `_place_point` with `pos`, and a test proves a placed stage "
    "light's throw is the building's own, at a turned and offset placement.\n"
    "- Then a cold run with a club: `LUX_CLUB_REFUSED` gone, 44 of 44 club rigs, and the stages lit in a frame.\n")
NEW_NEXT = (
    "- Lot: `merge_lights` carries `target` through `_place_point` with `pos`, and a test proves a placed stage "
    "light's throw is the building's own, at a turned and offset placement. *Done, below.*\n"
    "- Then a cold run with a club: `LUX_CLUB_REFUSED` gone, 44 of 44 club rigs, and the stages lit in a frame. "
    "*The first two done, below; the third not shown.*\n"
    "\n"
    "**DONE: LOT 0.99.1 (2026-10-08)** (`patches/patch_lot_light_targets.py`).\n"
    "- **Every point, not only `pos`.** `_LIGHT_POINTS` (`pos`, `target`) are placed with the building, and "
    "`_LIGHT_NOT_POINTS` (`size`, `color`) are kept: `size` is an extent in the light's own frame, which Lux "
    "turns with `rot_y`. Any other numeric triple is refused rather than shipped in the building's frame -- the "
    "rule `_ladder_to_site` keeps.\n"
    "- **Surveyed first.** 131 building light manifests on disk, 2,609 anchors. The only numeric triples are "
    "`pos`, `size` and `target`, and `target` is on 7 anchors, every one a `stage_light`.\n"
    "- **The tests** (`tests/test_light_targets.py`, against Deli Counter's strip_club_a01 build) hold each "
    "stage's throw to the building's own at three placements, two of them turned; 5 of 6 fail on 0.99.0.\n"
    "- **Cold run 9204** (club_block_014 from 9167's brief, 0 interventions; `docs/cold_runs/cold_9204/NOTES.md`). "
    "Lux's log: \"Baked 44 club rig(s) from 44 club anchor(s)\". b0's stages aim at (-62, -7, 1.68) and "
    "(-67, 5, 1.68), 4.28 and 5.23 m from their lamps, in both the candidate's and the themed site's manifests.\n"
    "\n"
    "**THE STAGES IN A FRAME -- NOT SHOWN, AND THE ATTEMPT RETRACTED.**\n"
    "- **What was shot.** `tools/look_shots.py` on 9204's walk copy, three given stations: the main stage from "
    "12 m, from 8 m and higher, and the VIP stage. The frames are a dark club -- posters, the lit back bar, a "
    "round stage with a red rim -- with no visible pool on either stage, at mean luminance 1.1-3.4.\n"
    "- **The test that followed, and why it is void.** It zeroed the four stage spots' `light_energy` in a "
    "copy, then raised their `spot_range` to 16 m. Neither moved a pixel beyond the control (on against on: "
    "maximum deltas 17, 25 and 237; on against off: 16, 26 and 237). But `lux_stage_light_rig.gd`'s "
    "`_rebuild()` frees every saved `Light3D` child at load and makes the lamps again from the rig's resource, "
    "so the edited values never ran. The resource reads `bake_mode = 1`, \"Stage Light (baked)\", so the "
    "stage's light is in the lightmap, where no scene edit reaches it. A null result from a dial that was not "
    "the dial refutes nothing. *As first read:* \"the stage spotlights make no measurable difference\", then "
    "\"its range is the limit\" -- both retracted.\n"
    "- **What would answer it:** an export with the stage rigs removed before the bake, against one with them, "
    "at the same stations -- or a station inside a stage's own cone.\n")

OLD_TAIL = "- **Price** the cruiser the way the van was priced.\n"
NEW_TAIL = OLD_TAIL + (
    "\n"
    "*STATUS: OPEN 2026-10-08 -- found, the walker's call: Level Factory's light bake marks every Lux rig whose "
    "resource carries no `failing_kind` as baked (`bake_mode = 1`), and a baked rig stops cycling "
    "(`lux_stage_light_rig.gd`, `_cycles()`). Lux's club stage rig cycles colour every 4 s by design but is not "
    "a failing fixture, so every club package ships its stage show frozen on one colour. Seen first in cold run "
    "9204, the first package whose stage rigs were built at all (item 207). Keep the cycling stages live and "
    "price them, or bake them frozen and say so.*\n"
    "\n"
    "**213. The light bake freezes the club's stage show.** Found 2026-10-08 checking cold run 9204's club for "
    "item 207.\n"
    "\n"
    "**WHAT WAS READ.**\n"
    "- **The bake's rule.** `level_factory/packages/exporting/light_bake.py`: \"every Lux rig in the "
    "presentation scene whose resource carries no `failing_kind` gets `bake_mode = 1`. A failing fixture (a "
    "stuttering tube, a cycling pole, a wavering bulb) stays live.\"\n"
    "- **The stage rig.** `lux_stage_light_rig.gd` cycles its lamps' colours -- \"each colour holds for 75% of "
    "`cycle_period_s`\" -- and changes nothing else, so a lamp's pairing with meshes never changes while it "
    "cycles. Its `_cycles()` returns false when `rig.bake_mode == 1`.\n"
    "- **In cold run 9204's package**, the stage rigs carry `cycle_period_s = 4.0`, seven colours, and a "
    "resource reading `bake_mode = 1`, \"Stage Light (baked)\". The stage lip's resource reads \"Neon (baked)\". "
    "The bake reported 78 rigs baked and 13 failing left live.\n"
    "\n"
    "**WHY IT IS THE WALKER'S CALL.** A colour cycle is unsteady light, and baking it freezes the look Lux "
    "built. Keeping it live costs four dynamic spot lights in a club, each one more light against the "
    "8-lights-a-mesh cap on the stage and floor. CLAUDE.md asks for that tradeoff to be shown rather than "
    "settled silently, and today it is settled silently.\n"
    "\n"
    "**NEXT.**\n"
    "- Price the four stage spots live against baked, the way the van was priced, with a station inside a "
    "stage's cone.\n"
    "- The walker chooses: live, or baked and frozen with the choice recorded.\n"
    "- If live: the bake keeps a rig with `cycle_period_s > 0` live, as it keeps a failing one, with a test that "
    "fails while it bakes one.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:50])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1309501, "PIPELINE_ROADMAP.md is %d bytes, read at 1,309,501" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD_NEXT) == 1, "NEXT found %d times" % text.count(OLD_NEXT)
    assert text.count(OLD_TAIL) == 1 and text.endswith(OLD_TAIL), "the file does not end on 212's last bullet"
    text = _replace_status(text, S207_PREFIX, S207_NEW, "**207. ")
    text = text.replace(OLD_NEXT, NEW_NEXT)
    text = text[:-len(OLD_TAIL)] + NEW_TAIL
    RM.write_bytes(text.encode("utf-8"))
    print("207 narrowed, 213 filed; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
