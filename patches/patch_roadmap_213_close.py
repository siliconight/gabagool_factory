"""Roadmap 213 CLOSED: the stage ships live and brighter, proven in cold run 9205.

Anchored on the full status block and on the last line of the item's body;
each must match exactly once, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-08 -- decided, not built. The walker: \"Stage can be brighter, im ok with live or baked, "
    "whatever you think is the best\". The call is LIVE, and brighter. Live costs no draw calls and 0.11 to 0.17 ms at "
    "a view facing a stage, on frames of about 3 ms (`docs/findings/club_stage_live_price/`). With the four stage lamps "
    "live, no mesh is over the 8-lights-a-mesh cap: Level Factory 0.159.0's paired census reads 0 over, worst 6, the "
    "same as baked (`docs/findings/light_census_pairs/`). Next: the bake keeps a cycling stage rig live, Lux lights the "
    "stage brighter, and a cold run on club_block_014 shows both.*\n"
    "\n"
    "**213. The light bake freezes the club's stage show.**"
)
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-08 -- the stage ships live, brighter, and cycling. Lux 0.69.0 lights it at "
    "`CLUB_STAGE_LEVEL` 24, eight times the old level, and a cycling lamp bakes no bounce; Level Factory 0.160.0's "
    "bake leaves a cycling rig live. Cold run 9205 (club_block_014, 0 interventions): \"76 steady rig(s) baked, 13 "
    "failing and 2 cycling left live\", the two cycling being the two stages; the stage top reads 22.2 and the pole "
    "56.5 (luminance, 8-bit codes) against 9.5 and 2.5 as 9204 shipped, within 0.1 codes of the 8x hand copy the call "
    "was made from; the lamp housings' frozen first colours are gone, brightest pixel 640-644 to 9; paired census "
    "still 0 over 8, worst 6 (`docs/cold_runs/cold_9205/NOTES.md`). Not this item's: a lens that follows the lamp's "
    "colour, unbuilt and unpriced.*\n"
    "\n"
    "**213. The light bake freezes the club's stage show.**"
)

OLD_TAIL = (
    "- *As first written in the finding:* \"8 of the 9 largest differences are at stations within 17 m of a stage\". "
    "Retracted: ninth place is a tie at 0.075 ms between a near heading and a far one.\n"
)
NEW_TAIL = OLD_TAIL + (
    "\n"
    "**DONE: BUILT (2026-10-08).**\n"
    "- **Lux 0.69.0** (`patches/patch_lux_stage_live.py`, its tests first in `patch_lux_stage_live_tests.py`). "
    "`CLUB_STAGE_LEVEL` 3 to 24, chosen against live frames at 4x, 8x and 10x: 8x is the brightest thing in the room "
    "with nothing clipped, and 10x barely differs (`docs/findings/club_stage_live_price/`, \"How bright\"). A cycling "
    "stage rig's lamps get `light_indirect_energy = 0`, so no bake holds a show that moves. `club_light_selftest` case "
    "M: 3 checks fail on 0.68.2.\n"
    "- **Level Factory 0.160.0** (`patches/patch_lf_bake_cycling_live.py`). The trap above, answered on the bake's "
    "side: `mark_steady_rigs` maps each rig resource to the nodes that use it, and leaves it live when one of them "
    "cycles. On 9204's pre-bake scene, 78 baked and 13 failing live before; 76 baked, 13 failing and 2 cycling live "
    "after.\n"
    "\n"
    "**DONE: PROVEN (cold run 9205, 2026-10-08)** (`docs/cold_runs/cold_9205/NOTES.md`, its frames and "
    "`stage_measure.py` beside it).\n"
    "- **The package carries it.** 0 interventions. The two cycling rigs are the two stages, the only nodes carrying "
    "`cycle_period_s`; their resources carry no `bake_mode` (0, Realtime); their lamps are exactly eight times 9204's "
    "energy, with `light_indirect_energy` 0.0.\n"
    "- **It reads as the copy the call was made from.** At the close station the stage top is 22.2 against the 8x "
    "copy's 22.3, and the pole 56.5 against 56.5. As 9204 shipped they were 9.5 and 2.5.\n"
    "- **The frozen show was visible, and it is gone.** Above the main stage the two lamp housings read 640-644 and "
    "547-551 in every 9204 frame, whatever the live energy, in the colours the lamps start their cycle with. In 9205 "
    "they read 9 and 9. The frames this decision rests on carry those lit housings; the package does not.\n"
    "- **The census agrees.** Paired: 0 over 8, worst 6, as predicted. Ten of b0's meshes gain the live lamps, none "
    "past 5. By reach: 33 over 8, unmoved.\n"
    "- **Not settled.** Whose light 9204's dim wash was: the 8x copy kept 9204's bake and still matches 9205 on the "
    "stage top to 0.1 codes, and the stage lip's neon is the candidate, untested. And the resource is still named "
    "\"Stage Light (baked)\" on a live rig: the loader names every club rig so, and `lux_lighting.gd` ranks shadows by "
    "those names.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    for label, old in (("status", OLD_STATUS), ("tail", OLD_TAIL)):
        n = text.count(old)
        if n != 1:
            sys.exit(f"refusing: the {label} anchor matches {n} times")
    if not text.endswith(OLD_TAIL):
        sys.exit("refusing: item 213's last line is no longer the end of the file")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(OLD_TAIL, NEW_TAIL)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 213 CLOSED; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
