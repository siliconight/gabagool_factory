"""Roadmap: 211 CLOSED (Lot 0.98.2, its census and cold run 9200); 212
NARROWED (phase 1, Lot 0.99.0, proven by cold run 9200); 204's cause found
for the site-level markers (Level Factory's Dispatch staging reads none).

    python patch_roadmap_211_212_204.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_phase2.py left it once
its index was regenerated (1,300,117 bytes, LF, as read 2026-10-08): each
status line by its unique prefix, directly above its heading; 211's last NEXT
bullet; 212's "NEXT, in order." heading and its first two bullets; 204's last
measured bullet and its first NEXT bullet. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S204_PREFIX = "*STATUS: OPEN 2026-10-07 -- found reading cold run 9194's package:"
S204_NEW = (
    "*STATUS: OPEN 2026-10-08 -- cause found for the site-level markers: Level Factory's Dispatch staging "
    "(`packages/staging/dispatch_inputs.py`) turns Lot's `markers`, `objectives` and `loot` into anchors and "
    "never reads `site_markers`, so the getaway van's crew spawn and extraction, and Lot 0.99.0's responder "
    "arrivals, never reach the package; with no `player_start` from Lot, `ensure_mission_anchors` synthesizes "
    "one at the centroid of every Lot anchor and tags every untagged extraction as the mission's. As filed "
    "2026-10-07 from cold run 9194's package: `gameplay_anchors.json` marks no objective as the score, names no "
    "anchor's building, and lists first the `deli_counter:*` anchors of the mission's own generated shell, which "
    "a library lot never places, in that shell's local frame.*\n")

S211_PREFIX = "*STATUS: OPEN 2026-10-08 -- found, not fixed: Lot's `site_audit._cover_rects`"
S211_NEW = (
    "*STATUS: CLOSED 2026-10-08 -- Lot 0.98.2 reads `size[2]` as plan y. Audited both ways over the 115 site "
    "specs on disk (112 with cover): 18 `S_NAKED_ANCHOR` as shipped and 0 that the fix moves, while a "
    "constructed site flips both ways (`tests/test_audit_cover_depth.py`, 3 of 3 fail on 0.98.1); cold run 9200 "
    "(0 interventions) has no `S_NAKED_ANCHOR` in its logs or 9199's. 0.98.1's two overstatements are corrected "
    "in the same release.*\n")

S212_PREFIX = "*STATUS: OPEN 2026-10-08 -- the walker's design, not started: responders arrive after the job"
S212_NEW = (
    "*STATUS: NARROWED 2026-10-08 -- phase 1 proven: Lot 0.99.0 plans an arrival per open road end -- the "
    "inbound keep-right lane, and a stop a 1990s cruiser fits with its doors open, nearest the crew's way back "
    "and outside the audit's camping line -- reserves both from the parking and the cover, reads the reservation "
    "back after every planner, and writes each as a `responder_spawn` site marker. Cold run 9200 (0 "
    "interventions): three arrivals on each of three candidates, nothing standing in any lane or stop, and the "
    "nav QA walked a bot from every stop to the nearest crew point, 5.8-22.5 m. Open: the package carries none "
    "of it (item 204, cause found), the cruiser (the walker's comps first), and `S_RESPONDER_ARC` fires on every "
    "candidate because their roads lie to one side of the objective.*\n")

OLD_211_TAIL = (
    "- In the same release, correct 0.98.1's two overstatements: its changelog's \"two checks\" (it is one), and "
    "`place_enemies`' single-file account of the one-leg spread, which cold run 9199's seed_9256 contradicts "
    "(item 206).\n")
NEW_211_TAIL = OLD_211_TAIL + (
    "\n"
    "**DONE, LOT 0.98.2 (2026-10-08)**, all three, recorded in `patches/patch_lot_audit_cover_depth.py`:\n"
    "- `_cover_rects` reads the third number as plan y.\n"
    "- The census, `patches/lot_audit_cover_depth/census_naked_anchor.py`, audited every drawn site in the "
    "workspaces and every spec under `lot/specs/` both ways. Of 18 `S_NAKED_ANCHOR` as shipped, it found none "
    "that moves; a constructed site flips, so it could have seen one. The error had moved no verdict on any "
    "site on disk.\n"
    "- The changelog corrects \"two checks\" to one, and `place_enemies`' comment now says the single-file "
    "account held on two sites of three.\n"
    "- Cold run 9200's Lot logs carry no `S_NAKED_ANCHOR`, as 9199's did not.\n")

OLD_212_NEXT = (
    "**NEXT, in order.**\n"
    "- **Lot: arrival routes.** For a heist, two or three, each made of four parts:\n")
NEW_212_NEXT = (
    "**PHASE 1, DONE: LOT 0.99.0 (2026-10-08).** `site_responders`, recorded in "
    "`patches/patch_lot_responder_arrivals.py`:\n"
    "- **An arrival per open road end**, up to three, spread by bearing. Each has:\n"
    "  - the inbound keep-right lane;\n"
    "  - a stop where a 2.0 x 5.4 m cruiser fits with a 1.0 m door's room each side, at the lane's station "
    "nearest the crew's way back (objective to extraction);\n"
    "  - and refuses a stop within `site_audit.CAMP_RADIUS` of the van, in a junction, or less than 10.8 m in "
    "from the road's end, as well as anything already standing and the other arrivals' stops and lanes.\n"
    "- **Reserved and read back.** The stops and lanes reach `plan_parking` as standing ground and "
    "`plan_cover` as the new placement-only `keep_out`. After every planner, `LOT_RESPONDER_BLOCKED` names "
    "anything standing in one.\n"
    "- **Written as `responder_spawn` site markers,** with the rest under `arrival`. The audit judges them, "
    "and Lot's nav QA spawns a bot at each.\n"
    "- **Cold run 9200** (0 interventions; `docs/cold_runs/cold_9200/NOTES.md`): three arrivals on each of "
    "three candidates, and no `LOT_RESPONDER_*` finding. Every arrival's bot reached the nearest crew point on "
    "the baked navmesh, 5.8-22.5 m.\n"
    "- **What the reservation moved.**\n"
    "  - seed_9054: a parked car out of a stop, which is the bake's 4 fewer users.\n"
    "  - seed_9256: a 4.7 m SUV swapped for a 4.3 m sedan beside a stop.\n"
    "  - seed_9155: a cargo container out of the road 1 lane. The cover planner broke the same line with one "
    "car beside the lane, and that fight went from 0 crew deaths in 25 runs to 6.\n"
    "  A clear lane is street the cover planner can no longer stand a truck in.\n"
    "- **`S_RESPONDER_ARC` fires on all three,** at 20, 5 and 30 degree arcs. Every stop is on a road, and "
    "these roads all lie to one side of each objective.\n"
    "- **Unproven:**\n"
    "  - a route from each stop to the van itself on every site -- the nav QA proves the nearest crew point;\n"
    "  - the package;\n"
    "  - anything a player sees, since there is no vehicle.\n"
    "\n"
    "**NEXT, in order.**\n"
    "- **Lot: arrival routes** -- *done, phase 1 above.* As filed: for a heist, two or three, each made of four "
    "parts:\n")

OLD_212_PACKAGE = (
    "- **The package** marks them, with the pose and the routes, so the game layer can find them (item 204).\n")
NEW_212_PACKAGE = (
    "- **The package** marks them, with the pose and the routes, so the game layer can find them (item 204, "
    "whose cause is now found: Level Factory's Dispatch staging reads no site markers).\n")

OLD_204_MEASURED = (
    "The walk scene and Laser Tag stand the crew at the van; a game layer reading the package would not know "
    "where it is. Whether Dispatch's Lot input carries the markers was not checked.\n")
NEW_204_MEASURED = OLD_204_MEASURED + (
    "- **THE CAUSE, for the site-level markers (read 2026-10-08).** Two things in "
    "`level_factory/packages/staging/dispatch_inputs.py`:\n"
    "  - **`_iter_records` never reads `site_markers`.** It yields Lot's gameplay `markers`, `objectives` and "
    "`loot`, and nothing else, so no site-level marker becomes an anchor: not the van's crew spawn, not its "
    "extraction, and not Lot 0.99.0's responder arrivals. It is the shape of the `ladders` line that was "
    "missing there in cold run 9076.\n"
    "  - **`ensure_mission_anchors` covers the gap.** With no `player_start` among Lot's anchors, it "
    "synthesizes one at the centroid of every Lot anchor: that is `lot:mission_start`, (-7.03, 0, 0.68) on "
    "9198. With extractions present but none tagged, it tags every one of them, so the mission's extraction "
    "is every building's street point and never the van.\n")

OLD_204_NEXT = (
    "- Read Level Factory's dispatch staging (`packages/staging/dispatch_inputs.py` and its caller) before "
    "deciding anything: where it takes Deli Counter anchors from on a library lot, and in which frame.\n")
NEW_204_NEXT = (
    "- *Done 2026-10-08, for the site-level markers (the cause above):* read Level Factory's dispatch staging "
    "(`packages/staging/dispatch_inputs.py` and its caller) before deciding anything. Still to read: where it "
    "takes Deli Counter anchors from on a library lot, and in which frame.\n"
    "- **Pass Lot's `site_markers` through:**\n"
    "  - `crew_spawn` as the mission's `player_start`, tagged `mission_start`;\n"
    "  - the getaway van's `extraction` as the mission's extraction, tagged `extraction`;\n"
    "  - `responder_spawn` as an `ai_spawn` tagged `responder`.\n"
    "  Carry each arrival's entry, lane and stop pose somewhere the game layer can read them: a Dispatch "
    "anchor holds only a position, a facing and tags.\n")


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
    assert len(data) == 1300117, "PIPELINE_ROADMAP.md is %d bytes, read at 1,300,117" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    pairs = ((OLD_211_TAIL, NEW_211_TAIL), (OLD_212_NEXT, NEW_212_NEXT), (OLD_212_PACKAGE, NEW_212_PACKAGE),
             (OLD_204_MEASURED, NEW_204_MEASURED), (OLD_204_NEXT, NEW_204_NEXT))
    for old, _new in pairs:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    text = _replace_status(text, S204_PREFIX, S204_NEW, "**204. ")
    text = _replace_status(text, S211_PREFIX, S211_NEW, "**211. ")
    text = _replace_status(text, S212_PREFIX, S212_NEW, "**212. ")
    for old, new in pairs:
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("204 cause, 211 closed, 212 phase 1; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
