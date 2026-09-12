"""Roadmap batch 41, 2026-09-12: cover as species slots in a cold package --
22 gets its first status (INSERT above the heading), 17 records cold runs
9018-9021 (REPLACE, old kept), 18 the pivot claim nobody measured (REPLACE,
old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

INSERT_22 = ("""**22. Outdoor props have no swap contract, so cover stays boxes forever.**""",
"""*STATUS: NARROWED 2026-09-12 (late night) -- THE SITE HAS A SLOT MANIFEST
AND ITS COVER IS BUILT BY ZOO AND STANDS IN THE PACKAGE WITH COLLISION;
THE SPECIES ARE STILL BOXES. The walker, on 9017's frames: "the green boxes
should be larger props with collision to offer cover between buildings to
force creative traversal." Built in one day, four cold runs: Lot 0.59.x
places cover as SPECIES pieces -- a box truck (2.4 x 6.0 x 2.8), a cargo
container (2.44 x 6.06 x 2.59), a car (1.75 x 4.3 x 1.45), the Zoo
genomes' own defaults -- turned so the length lies across the sightline
each breaks, quantised to 0/90 so the axis-aligned break and pinch
arithmetic measure the piece and not its bounding box, the table walked
per piece so a street gets a truck, a container, a car, and each piece the
largest that fits its lane; `assemble` writes `<site>.slots.json` in Deli
Counter's manifest shape, one prop slot per piece. LF 0.77.x fans out a
`zoo_kit_build` for archetype `site` over it and the themed site names
the build directory; Lot stands each module where its box stood, centre
for centre, by the stem it mirrors from Deli Counter and Zoo, with the
module's own collision, and keeps the box under `LOT_COVER_MODULE_MISSING`
when a module is not there. Zoo 0.66.x minted `box_truck` and
`cargo_container` beside the existing `simple_car`. IN A PACKAGE: cold run
9021 (item 17) stands a box truck and a container on the lot, both `pass`
in the site kit, both in the assembly and in Lux's applied scene, no open
sightline, no pinch, no blocker. WHAT THE FOUR RUNS TAUGHT, each a rule
now: the marker clearance was measured from a piece's centre, which left a
3 m cube 1.5 m clear of a spawn and a 6 m container nothing -- Laser
Tag's preflight refused 9018 ("Enemy_2 is sealed off", the container's
end 0.25 m from it), and the export gate held (Lot 0.59.1: clearance from
the edge); the modules were referenced by absolute path and the Lux
stage's copy of the scene lost them (9019: three built, none in the
level; Lot 0.59.2: copied beside the scene, like the skins); the kit index
said "pivot: center" for modules built base-up, so a centre-placed truck
stood 1.4 m in the air (9019, measured off the GLB; Zoo 0.66.1 re-centres
on build and fails `fit_pivot`; 0.66.2 leaves clutter, built base-up on
purpose, alone after 9020 failed all four species on it). WHAT REMAINS:
the truck and the container are boxes at the right proportions (the
recipes are where the cab, the wheels and the doors go); the car has a
recipe and reads as one; the density is Lot's sightline budget, two or
three pieces a site, which is cover and not yet a lot that reads as parked
in; and the thing the references warned about (`docs/SET_DRESSING_
REFERENCES.md`) is now live -- a prop's silhouette leaving the box it was
graded in is an affordance change no gate measures. Previously OPEN,
inferred: no status had ever been written for this item.*

**22. Outdoor props have no swap contract, so cover stays boxes forever.**""")

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (late night) -- THREE RUNS FOR THE GROUND
SKIN: 9015 SHIPPED UNLIT OVER A BLOCKER, 9016 WAS REFUSED AT EXPORT BY THE
GATE THAT RUN TAUGHT, 9017 IS THE ZERO WITH THE SKIN IN THE PACKAGE.""",
"""*STATUS: NARROWED 2026-09-13 (small hours) -- FOUR RUNS FOR THE SPECIES
COVER: 9018 REFUSED AT EXPORT ON A SEALED SPAWN, 9019 A ZERO THAT LOST ITS
MODULES ONE STAGE ON, 9020 A ZERO WITH THE CLUTTER BUILD RED, 9021 THE
ZERO WITH A TRUCK AND A CONTAINER ON THE LOT. All the bank brief. 9018,
on Zoo 0.66.0 / Lot 0.59.0 / LF 0.77.0: the site kit built the truck and
the container from Lot's manifest, Lot stood both, and Laser Tag's
preflight refused two candidates -- "Enemy_2 is sealed off from the crew
spawn", the container's end 0.25 m from the marker -- so the export
refused the mission: the first cover defect stopped before it shipped
(item 22). 9019, on Lot 0.59.1: 0 interventions, export exit 0, three
species built and placed in Lot's scene, and NONE in the level: absolute
module paths, the Lux stage's copy of the scene lost them, and the frames
showed the street bare; not counted a zero. 9020, on Lot 0.59.2 / Zoo
0.66.1: 0 interventions, export exit 0, the truck in the package, centred,
in both scenes -- and `zoo_clutter_build` red, every clutter species
failing the new pivot check it was never meant for; the export shipped
undressed and said so. 9021, on Zoo 0.66.2: 0 interventions, 0 retries, 0
unattributed changes, every tool repo clean at --begin, all stages
succeeded, 0 blockers, export exit 0, 14 minutes (14:00 -> 14:14); a box
truck and a cargo container on the lot, no open sightline, no pinch, the
dressing back (2,387 pieces, none inside a footprint). The thirteenth
zero. Logs and journals: `docs/cold_runs/cold_9018/` .. `cold_9021/`;
walk copy `_runs/walk_export_bank_block_001` is 9020's. Previously: THREE
RUNS FOR THE GROUND
SKIN: 9015 SHIPPED UNLIT OVER A BLOCKER, 9016 WAS REFUSED AT EXPORT BY THE
GATE THAT RUN TAUGHT, 9017 IS THE ZERO WITH THE SKIN IN THE PACKAGE."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (late night) -- THE THIRD SHAPE A THIRD TIME
IN ONE DAY, AND THE LAST PLACE IT COULD HIDE WAS THE EXPORT.""",
"""*STATUS: NARROWED 2026-09-13 (small hours) -- A FOURTH SHAPE: A CLAIM
REPEATED AS A MEASUREMENT. Zoo's kit index carries `"pivot": "center"` on
every module row, and Deli Counter and Lot place a module's origin at its
slot's centre on the strength of it. The field was the PLAN's claim
copied through; nothing measured where a built module's bounds sat.
Measured 2026-09-12 off cold run 9019's site kit: the minted placeholders
z 0 .. h and `simple_car` z 0.01 .. 1.45 under that claim, a truck placed
by it 1.4 m in the air. The building props were centred (the teller line
-1.2 .. 1.2), which is why nothing had ever shown it. Zoo 0.66.1:
`gather_facts` reports the bounds' centre, `fit_pivot` fails a module off
it, `build_module` re-centres what a recipe returns; 0.66.2 scopes it to
slot-fit modules after the check failed every clutter species, which are
built base-up to sit on a surface. THE RULE FOR THE SCORE: a manifest
field that names a property of the artefact is a claim until an
instrument reads it off the artefact; the index now carries both, and
they are compared. Previously: THE THIRD SHAPE A THIRD TIME
IN ONE DAY, AND THE LAST PLACE IT COULD HIDE WAS THE EXPORT."""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    head, new = INSERT_22
    if text.count("\n" + head) != 1:
        print("22 heading not unique; refusing", file=sys.stderr)
        return 1
    if "**22. " in text and text[text.index("\n" + head) - 300:text.index("\n" + head)].count("*STATUS: NARROWED 2026-09-12 (late night) -- THE SITE HAS"):
        print("22 already has this status", file=sys.stderr)
        return 1
    for old, _ in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    text = text.replace("\n" + head, "\n" + new, 1)
    for old, rep in R:
        text = text.replace(old, rep, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 22 given a status, 17, 18 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
