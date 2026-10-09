"""Roadmap 212 CLOSED: responders can arrive, and the car they arrive in
ships (cold runs 9206-9209). `S_RESPONDER_ARC` moves to item 215, opened
here with the finding that the site audit reaches no report.

Anchored on 212's status line, the body's "Not built yet" line, and the
roadmap's last line; each must match exactly once, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

OLD_STATUS_HEAD = "*STATUS: NARROWED 2026-10-08 -- the arrivals are planned, kept clear and in the package."
OLD_STATUS_TAIL = ("Open: the cruiser itself in the package for the gameplay layer to spawn, and a price; "
                   "`S_RESPONDER_ARC` firing where a site's roads lie to one side of the objective.*\n")
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-08 -- responders can arrive, and the car they arrive in ships. Lot 0.99.0-0.101.0 "
    "plans an arrival per open road end, sized for Zoo 1.86.0's cruiser, its lane steered round the getaway van "
    "and reserved from every later planner; Level Factory 0.156.0-0.162.1 marks each stop as a `responder` anchor "
    "and ships `responder_arrivals.json` (v3) naming the car each brings. Cold runs 9206-9209 (club_block_014, 0 "
    "interventions each): three arrivals on every candidate, every stop walked by Lot's nav QA, the cruiser built "
    "by Zoo's site kit, in the package at 259,531 bytes, named for every arrival and stood nowhere, its import "
    "Dynamic so a spawned one samples the lightmap's probes (Godot 4.7 measured: `light_baking=3` gives gi_mode "
    "DYNAMIC). How many responders spawn, and when, is the gameplay layer's. `S_RESPONDER_ARC` is a question "
    "about road layout, and moves to item 215.*\n"
)

OLD_NOT_BUILT = "  - **Not built yet.** Then a price.\n"
NEW_NOT_BUILT = (
    "  - *Built, below: Lot 0.101.0, Level Factory 0.162.0 and 0.162.1.*\n"
    "\n"
    "**LOT 0.101.0, LEVEL FACTORY 0.162.0 AND 0.162.1, DONE: THE CAR IN THE PACKAGE (2026-10-08)** "
    "(`patches/patch_lot_responder_vehicle.py`, `patch_lf_responder_vehicle.py`, `patch_lf_bake_spawned.py`).\n"
    "- **Built, never stood.** Lot writes each arrival's car as `site_spec[\"responders\"]`, a list of its own, "
    "not cover. `write_site_slots` gives each a slot, so Zoo's site kit builds the cruiser.\n"
    "  - The themed assembly copies the module into `cover/` with its textures, declares none of it in "
    "`site.tscn`, and names it in `responders.json`.\n"
    "  - Level Factory gives each arrival `vehicle_scene`, checked present in the package.\n"
    "- **Cold run 9208** (`docs/cold_runs/cold_9208/NOTES.md`, its `check_vehicle.py` read in pipeline order):\n"
    "  - the kit built `prop_cruiser_delco_1997_01_w220_d554_h158`, `pass`;\n"
    "  - all three arrivals name it, and the scene stands nothing;\n"
    "  - the closure and GLB-reference scans are clean, 440 GLBs.\n"
    "- **Found by 9208: the bake had marked the car static.** Every GLB sidecar was set to Static Lightmaps.\n"
    "  - Measured on Godot 4.7: `light_baking=2` gives the car's five meshes gi_mode STATIC, `3` gives "
    "DYNAMIC.\n"
    "  - A static mesh outside the bake gets neither the lightmap nor the probes.\n"
    "  - Level Factory 0.162.1 sets a spawned car to 3. Cold run 9209: `light_baking=3`, no unwrap cache, "
    "\"1 spawned set dynamic\".\n"
    "- **The price.** 259,531 bytes of package: the GLB and its own 21,639-byte livery; its other eight "
    "textures were already shipped. Nothing a frame until spawned, then five draws and 3,476 triangles a car.\n"
)

TAIL = ("  4. procedural detail on that bake source.\n"
        "- **A.5 What does not change.** No subdivided mesh at runtime; a normal map is a texture in the part "
        "family's one material; triangles are counted on the game mesh.\n")
ITEM_215 = (
    "\n"
    "*STATUS: OPEN 2026-10-08 -- split out of item 212 at its close, not worked. On club_block_014 (cold run 9209) "
    "the site audit reports all three responder arrivals inside a 6-degree arc of the objective, and that finding "
    "-- with every other site-audit finding -- reaches no report: it is in Lot's job log only.*\n"
    "\n"
    "**215. `S_RESPONDER_ARC` fires where a site's roads lie to one side of the objective, and the site audit "
    "reaches no report.**\n"
    "\n"
    "**WHAT THE RULE ASKS.** No gap between responders' bearings from the objective wider than 150 degrees: three "
    "or more, spread round it, so \"pressure changes direction between waves\".\n"
    "\n"
    "**WHAT THE SITES GIVE IT.**\n"
    "- **Stops stand on roads, at open road ends.** Where the roads lie to one side of the objective, no stop can "
    "pass the rule.\n"
    "- **The measured arcs:**\n"
    "  - cold run 9198's seed_9256: every road point bears 215 to 18 degrees from the objective;\n"
    "  - cold run 9200: arcs of 20, 5 and 30 degrees;\n"
    "  - cold run 9209's club_block_014 seed_9181: 6 degrees.\n"
    "- **So the finding is about the road layout,** not the stops (item 212).\n"
    "\n"
    "**THE AUDIT REACHES NO REPORT.** Measured on cold run 9209's seed_9181:\n"
    "- **What Lot printed.** Its job log carries one MED (`S_RESPONDER_ARC`) and three INFO "
    "(`S_GETAWAY_AT_SPAWN`, `S_STREET_CROSS` twice).\n"
    "- **What the report carries.** Level Factory's validation report carries no `S_` code at all.\n"
    "- **What follows.** No cold run's findings diff has ever counted the site audit, so a finding it raises "
    "moves no number anyone reads.\n"
    "\n"
    "**NOT DECIDED HERE.**\n"
    "- **The rule's premise** (assault waves from different directions) is the gameplay layer's design.\n"
    "- **The factory's options:**\n"
    "  - leave the rule, which reports a true fact about the roads;\n"
    "  - let Lot open road ends on more sides of a heist;\n"
    "  - change the rule's severity.\n"
    "- **First, separately:** carry the site audit into the validation report, so whatever it says is counted.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    i = text.find(OLD_STATUS_HEAD)
    if text.count(OLD_STATUS_HEAD) != 1 or text.count(OLD_STATUS_TAIL) != 1:
        sys.exit("refusing: 212's status anchors do not match once")
    j = text.index(OLD_STATUS_TAIL, i) + len(OLD_STATUS_TAIL)
    if "\n" in text[i:j - 1]:
        sys.exit("refusing: 212's status line is not one line")
    text = text[:i] + NEW_STATUS + text[j:]
    if text.count(OLD_NOT_BUILT) != 1:
        sys.exit("refusing: the 'Not built yet' line matches %d times" % text.count(OLD_NOT_BUILT))
    text = text.replace(OLD_NOT_BUILT, NEW_NOT_BUILT)
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: item 214's last lines are not the end of the file")
    if "\n**215. " in text:
        sys.exit("refusing: an item 215 already exists")
    text += ITEM_215
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 212 closed, 215 opened; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
