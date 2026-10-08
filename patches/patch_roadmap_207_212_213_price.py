"""Roadmap: 207 CLOSED -- the club's stage lamps land on the stage and the pole
in a frame; 213 priced -- live costs no draw calls and 0.11-0.17 ms at a view
facing a stage, and the stage does not read lit at Lux's energy either way;
212 gains the getaway van closing a responder lane (cold run 9204).

    python patch_roadmap_207_212_213_price.py

Anchored on PIPELINE_ROADMAP.md as commit 7a76506 left it (1,314,530 bytes,
LF, as read 2026-10-08): the status lines of 207, 212 and 213 by their unique
prefixes, each directly above its heading; 207's third NEXT bullet's note and
its last bullet; 212's last NEXT bullet; 213's three NEXT bullets. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S207_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the refusal is fixed: Lot 0.99.1 carries"
S207_NEW = (
    "*STATUS: CLOSED 2026-10-08 -- Lot 0.99.1 carries a light anchor's `target` into site space with its `pos` "
    "(and refuses any numeric triple it has not classed), so cold run 9204 (club_block_014, 0 interventions) "
    "built 44 of 44 club rigs where 9197 built 42, `LUX_CLUB_REFUSED` is gone, the stages throw 4.28 and 5.23 m, "
    "and the lamps land on the stage and the pole in a frame: with the stage rigs' resources set live at Lux's own "
    "energy, 0.46% of the close frame moves by more than 8 codes, against 0.00% for a second launch of the "
    "shipped package (`docs/findings/club_stage_live_price/`). At that energy the stage does not read lit, baked "
    "or live; that question, with the frozen colour cycle, is item 213's.*\n")

OLD_207_NOTE = "*The first two done, below; the third not shown.*"
NEW_207_NOTE = ("*All three done, below. The third is shown as the lamps landing on the stage and the pole; "
                "whether the stage reads lit is item 213's.*")

OLD_207_LAST = (
    "- *As first filed:* \"Read why Lux refuses a stage anchor ... Then decide whether the stage is lit by its "
    "hardware (the markerless fixtures) and the refusal is correct, or a rig is missing.\" The refusal is correct; "
    "the anchor is wrong. The walker's standing call still applies: dens of sin are dark buildings, but a stage is "
    "where a club's light goes.\n")
NEW_207_LAST = OLD_207_LAST + (
    "\n"
    "**THE STAGES IN A FRAME -- SHOWN (2026-10-08)** (`docs/findings/club_stage_live_price/`).\n"
    "- **The dial that works.** `make_live_copy.py` sets the stage rigs' resources live (`bake_mode = 1` to 0), "
    "the value `_rebuild()` reads. On the raw package it reproduces the hand-made copy the price ran on, byte for "
    "byte.\n"
    "- **The lamps land.** At the main stage from 8 m (`main_stage_close`), a live copy at Lux's energy moves "
    "0.46% of the frame by more than 8 codes (largest 221), against 0.00% (largest 25) for a second launch of the "
    "shipped package; at ten times Lux's energy, 1.06%. The frames show the pole lit and a brighter pool on the "
    "stage.\n"
    "- **The stage does not read lit at Lux's energy, baked or live.** As shipped it is a dim red-brown wash; "
    "live adds a lit pole and a slightly brighter pool. Whose light the shipped wash is -- the stage lamps', "
    "baked, or the stage lip's orange neon, baked, reaching 2.5 m -- is not separated. Item 213 carries it.\n")

S212_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the arrivals are planned, kept clear and in the package."
OLD_212_OPEN = ("Open: the cruiser (the walker's comps first), and `S_RESPONDER_ARC` firing where a site's roads "
                "lie to one side of the objective.*")
NEW_212_OPEN = ("Open: the cruiser (the walker's comps first); `S_RESPONDER_ARC` firing where a site's roads lie "
                "to one side of the objective; and the getaway van closing every lane that has to pass it, which "
                "cost cold run 9204 one arrival of three.*")

OLD_212_LAST = "- **Price** the cruiser the way the van was priced.\n"
NEW_212_LAST = OLD_212_LAST + (
    "- **Lot: let the lane steer round the van.** Cold run 9204's club_block_014 lost one arrival of three to "
    "the getaway van (`docs/findings/responder_entry_no_stop/`, which replays Lot's planner on the job's inputs "
    "and reproduces its record).\n"
    "  - **The van overhangs its bay, by design.** Its body is 2.30 m and stands 0.20 m off the kerb, so in a "
    "2.2 m parking lane the body overhangs 0.30 m and the mirrors 0.45 m.\n"
    "  - **The lane cannot pass it.** The planner's lane is a 3.0 m box at the lane's centre, in a 2.8 m "
    "driving half. It overlaps the van by 0.55 m, and the cruiser alone would by 0.05 m. So every lane that has "
    "to pass the van is refused, and every stop short of it is within `CAMP_RADIUS` of the crew.\n"
    "  - **It recurs** wherever an open road end's inbound lane runs along the van's kerb toward it. "
    "`LOT_RESPONDER_ENTRY_NO_STOP` counted it twice on 9204, once from the candidate's assemble and once from "
    "the themed site's: one road end.\n"
    "  - **The fix:** a lane that shifts across the carriageway round standing ground, as a driver does, with "
    "a test that fails on 9204's spec.\n")

S213_PREFIX = "*STATUS: OPEN 2026-10-08 -- found, the walker's call: Level Factory's light bake marks"
S213_NEW = (
    "*STATUS: OPEN 2026-10-08 -- priced, the walker's call: Level Factory's light bake bakes every Lux rig whose "
    "resource carries no `failing_kind`, and a baked rig stops cycling, so every club package ships its stage "
    "show frozen on one colour (seen first in cold run 9204). Keeping the stage rigs live costs no draw calls and "
    "0.11 to 0.17 ms at a view facing a stage, on frames of about 3 ms, in two runs against two controls; beyond "
    "50 m of a stage it does not measure (`docs/findings/club_stage_live_price/`). At Lux's energy the stage does "
    "not read lit, baked or live. The calls: live and cycling, or baked and frozen; and whether the stage should "
    "be brighter.*\n")

OLD_213_NEXT = (
    "- Price the four stage spots live against baked, the way the van was priced, with a station inside a stage's "
    "cone.\n"
    "- The walker chooses: live, or baked and frozen with the choice recorded.\n"
    "- If live: the bake keeps a rig with `cycle_period_s > 0` live, as it keeps a failing one, with a test that "
    "fails while it bakes one.\n")
NEW_213_NEXT = (
    "- Price the four stage spots live against baked, the way the van was priced, with a station inside a stage's "
    "cone. *Done, below -- from the two stations whose headings face a stage, not from inside a cone.*\n"
    "- The walker chooses: live, or baked and frozen with the choice recorded. And, separately, whether the stage "
    "should read brighter than Lux's solve: at that energy it does not read lit either way.\n"
    "- If live: the bake keeps a rig with `cycle_period_s > 0` live, as it keeps a failing one, with a test that "
    "fails while it bakes one. The stage then loses whatever part of its baked wash is the stage lamps'.\n"
    "\n"
    "**DONE: THE PRICE (2026-10-08)** (`docs/findings/club_stage_live_price/`).\n"
    "- **How.** Four runs of Level Factory's fixed-station harness: cold run 9204's package as shipped, a copy "
    "with the two stage rigs' resources live at Lux's energy, the shipped package again, and the live copy "
    "again. 53 station headings, GL Compatibility, RTX 2060, 1280x720.\n"
    "- **Draw calls: none.** Live against shipped is 0 at every heading; unshadowed lamps add no pass. The one "
    "exception is -160 at `attacker_spawn_8` yaw 0 in the repeat. That heading draws 871 or 711 from pass to "
    "pass in all four runs, the controls included.\n"
    "- **Level-wide: nothing measurable.** The median frame moved +0.014 and +0.001 ms against the controls' "
    "mean. The controls differ from each other by +0.021.\n"
    "- **Facing a stage: 0.11 to 0.17 ms**, on frames of 2.7 and 3.1 ms.\n"
    "  - `patrol_point_18` yaw 0, the main stage 5.9 m ahead: +0.143 and +0.160 ms (control -0.027).\n"
    "  - `defender_spawn_15` yaw 270, the VIP stage 5.1 m ahead: +0.170 and +0.113 ms (control +0.032).\n"
    "  - The 24 headings within 17 m of a stage moved +0.047 and +0.022 ms on average; the 29 beyond 50 m, "
    "+0.006 and -0.011.\n"
    "- **Not measured: the 8-lights-a-mesh cap.** The harness's light census counts every positional light by "
    "its reach, baked or live. So it reads the same in all four runs (33 of 3,954 meshes over 8), and cannot say "
    "whether the live lamps put a stage mesh over the lights the renderer pairs with it.\n"
    "- **The look.** At Lux's energy, live adds a lit pole and a slightly brighter pool to the shipped dim wash; "
    "the frames are beside the price. Ten times Lux's energy gives a magenta pool -- a dial turned to see the "
    "light land, not a proposal.\n"
    "- *As first written in the finding:* \"8 of the 9 largest differences are at stations within 17 m of a "
    "stage\". Retracted: ninth place is a tie at 0.075 ms between a near heading and a far one.\n")


def _status_line(lines, prefix, heading):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:50])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    return i


def main():
    data = RM.read_bytes()
    assert len(data) == 1314530, "PIPELINE_ROADMAP.md is %d bytes, read at 1,314,530" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, what in ((OLD_207_NOTE, "207's NEXT note"), (OLD_207_LAST, "207's last bullet"),
                      (OLD_212_LAST, "212's last NEXT bullet"), (OLD_213_NEXT, "213's NEXT")):
        assert text.count(old) == 1, "%s found %d times" % (what, text.count(old))
    assert text.endswith(OLD_213_NEXT), "the file does not end on 213's NEXT"

    lines = text.split("\n")
    i = _status_line(lines, S207_PREFIX, "**207. ")
    lines[i] = S207_NEW.rstrip("\n")
    i = _status_line(lines, S212_PREFIX, "**212. ")
    assert lines[i].count(OLD_212_OPEN) == 1 and lines[i].endswith(OLD_212_OPEN), "212's Open clause"
    lines[i] = lines[i][:-len(OLD_212_OPEN)] + NEW_212_OPEN
    i = _status_line(lines, S213_PREFIX, "**213. ")
    lines[i] = S213_NEW.rstrip("\n")
    text = "\n".join(lines)

    text = text.replace(OLD_207_NOTE, NEW_207_NOTE)
    text = text.replace(OLD_207_LAST, NEW_207_LAST)
    text = text.replace(OLD_212_LAST, NEW_212_LAST)
    text = text[:-len(OLD_213_NEXT)] + NEW_213_NEXT
    RM.write_bytes(text.encode("utf-8"))
    print("207 closed, 212 and 213 updated; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
