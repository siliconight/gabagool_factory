"""Roadmap 212: Zoo 1.86.0 builds the responders' cruiser; what is left is
getting it into a level.

Anchored on 212's full status block and on its body's last bullet; each must
match exactly once, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

OLD_STATUS_TAIL = (
    "Open: the cruiser (the walker's comps first); `S_RESPONDER_ARC` firing where a site's roads lie to one "
    "side of the objective; and the getaway van closing every lane that has to pass it, which cost cold run "
    "9204 one arrival of three.*\n"
    "\n"
    "**212. Responders arrive on the way back.**"
)
NEW_STATUS_TAIL = (
    "Zoo 1.86.0 builds the cruiser the walker asked for, a 1990s Crown Victoria lettered DELCO COUNTY "
    "POLICE in two liveries: 0 coincident pairs at the genome's three corners and over 51 swept sizes, "
    "five meshes and 3,476 triangles a car, and `simple_car`'s own cars unchanged, 200 meshes hashed "
    "(`docs/findings/cruiser_build/`). Open: the cruiser into a level -- Lot's responder slot derived "
    "from it, the asset in the package for the gameplay layer to spawn, and a price; `S_RESPONDER_ARC` "
    "firing where a site's roads lie to one side of the objective; and the getaway van closing every lane "
    "that has to pass it, which cost cold run 9204 one arrival of three.*\n"
    "\n"
    "**212. Responders arrive on the way back.**"
)

OLD_TAIL = (
    "  - **The fix:** a lane that shifts across the carriageway round standing ground, as a driver does, with "
    "a test that fails on 9204's spec.\n"
    "\n"
    "*STATUS: CLOSED 2026-10-08 -- the stage ships live, brighter, and cycling."
)
NEW_TAIL = (
    "  - **The fix:** a lane that shifts across the carriageway round standing ground, as a driver does, with "
    "a test that fails on 9204's spec.\n"
    "\n"
    "**ZOO 1.86.0, DONE: THE CRUISER (2026-10-08)** (`patches/patch_zoo_cruiser.py`; the evidence in "
    "`docs/findings/cruiser_build/`).\n"
    "- **What the walker asked for.** \"I would think a classic 1990s Crown Victoria\", with five photographs; "
    "\"Delco County Police Dept. as a start?\"; and a photograph of the interior. The comps are "
    "`docs/reference/CRUISER_COMPS.md`, read for format only.\n"
    "- **What it is.** A species, `cruiser`, on `simple_car`'s sedan at a Crown Victoria's published "
    "proportions, its form pinned (four doors and a quarter glass, black steel wheels, a blue-grey cloth "
    "interior), with no jitter, and never drawn by `auto`.\n"
    "  - **The kit:** a light bar (red on the driver's side), a push bar, an A-pillar spotlight, a whip, and "
    "inside a partition and a radio console.\n"
    "  - **The livery:** one image on one material, `black_white` (the default) or `white_blue`. DELCO COUNTY "
    "POLICE, seals with unit 214, the motto WE'LL GET YOUSE. It is lettered where `simple_car` cut the doors, "
    "and the marks shrink together on a lower car (0.92 at the genome's lowest; refused under 0.8).\n"
    "  - **The slot:** 2.196 x 5.545 x 1.578 m by default: wide to the mirror heads, long from the push bar "
    "to the rear bumper, tall to the light bar's top.\n"
    "- **Measured.**\n"
    "  - Coincident faces: 0 pairs at the three corners on the census's third run, and 0 over 51 swept "
    "sizes in each livery.\n"
    "  - Five meshes, one a material, as the van has; 3,476 triangles at every size.\n"
    "  - `simple_car`'s own cars unchanged: 200 meshes, every vertex hashed against 1.85.0, 0 differ.\n"
    "- **Found on the way, each fixed at its source and kept in the finding.**\n"
    "  - The first build drew it as an SUV where a style decides details, with a hatchback's quarter glass "
    "(1.45 m doors). It is a sedan there now (`car_forms.SEDANS`): 1.67 m doors.\n"
    "  - The census's first run found 8-9 pairs a build in the kit, the partition through the headrests "
    "among them, and the lowest corner unable to letter its doors.\n"
    "  - The kit was a sixth mesh: named outside the car's part family, the export could not merge it.\n"
    "- **Not done.**\n"
    "  - **Lot's slot is still hand-set.** `site_responders.VEHICLE` is 2.0 x 5.4 x 1.5 m, \"not derived: "
    "Zoo has no cruiser species yet\" (`lot/site_responders.py:59`). Derived from the genome's default, "
    "the stop needs 0.196 m more width and 0.145 m more length, so stops that fit today may not. Its "
    "comment calls 2.0 m the width to the mirrors; the published 1.99-2.0 m it cites is the body's, and "
    "the cruiser's mirror heads stand 2.196 m apart.\n"
    "  - **The asset is not in a package.** Responders are the gameplay layer's to spawn, so the car has to "
    "ship beside `responder_arrivals.json` rather than stand in the scene.\n"
    "  - **Not priced in a frame.**\n"
    "  - **The livery is the walker's to choose.** Both are shown in the finding's frames.\n"
    "\n"
    "*STATUS: CLOSED 2026-10-08 -- the stage ships live, brighter, and cycling."
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    for label, old in (("status", OLD_STATUS_TAIL), ("tail", OLD_TAIL)):
        n = text.count(old)
        if n != 1:
            sys.exit(f"refusing: the {label} anchor matches {n} times")
    text = text.replace(OLD_STATUS_TAIL, NEW_STATUS_TAIL).replace(OLD_TAIL, NEW_TAIL)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 212 updated; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
