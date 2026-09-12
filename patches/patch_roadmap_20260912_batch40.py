"""Roadmap batch 40, 2026-09-12: the ground plate skin (152 step 1, 45's
first concrete step), cold runs 9015-9017 (17 REPLACE, old kept), and the
export gate on open blockers (18 REPLACE, old kept). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

R.append(("""*STATUS: NARROWED 2026-09-12 (night) -- COLD RUNS 9013 AND 9014 SCORED
ZERO ON THE BANK BRIEF; 9013 IS THE PACKAGE THAT PROVED DC 0.120.0 WRONG
AND 9014 IS THE ONE WITH THE REMAINDERS ALONG THEIR WALLS BY THE ENGINE'S
READING AND NO OUTDOOR CLUTTER ON ANY FLOOR.""",
"""*STATUS: NARROWED 2026-09-12 (late night) -- THREE RUNS FOR THE GROUND
SKIN: 9015 SHIPPED UNLIT OVER A BLOCKER, 9016 WAS REFUSED AT EXPORT BY THE
GATE THAT RUN TAUGHT, 9017 IS THE ZERO WITH THE SKIN IN THE PACKAGE. All
three the bank brief. 9015, on Pixelcoat 0.30.0 / Lot 0.57.1 / LF 0.75.0:
0 interventions, all stages reported succeeded, export exit 0, 19 minutes
-- and NOT A ZERO: Lot referenced the ground maps by absolute path, Godot
has no importer for a png outside a project, the Lux stage failed to parse
the assembly ("No loader found for resource ... expected type:
Texture2D"), exited 2, was filed as a blocking `JOB_TOOL_EXIT`, and the
export shipped the mission anyway -- a package with no lighting, whose
every frame off the walk copy was black (item 18). Fixed twice: Lot 0.58.0
copies the maps to `skins/` beside its scene and references them as
siblings; LF 0.76.0 refuses an export with open blockers. 9016, on those:
0 interventions, the Lux stage failed again ("Resource file not found:
res://skins/asphalt_delco_albedo.png") because the Lot adapter published
`.tscn/.json/.csv/.glb/.gd` and not the pngs Lot had just written -- and
the export REFUSED, naming the blocker: the first time that gate closed on
a real run, one stage after the cause. LF 0.76.1 publishes `.png`. 9017,
on Pixelcoat 0.30.0 / Lot 0.58.0 / LF 0.76.1: 0 interventions, 0 retries,
0 unattributed changes, every tool repo clean at --begin, all stages
succeeded, Lux exit 0, 0 blockers, export exit 0, 16 minutes (11:59 ->
12:16); lot `bank_tower_a02` / funeral_home_a01 / setback_demo; the
package carries `skins/` with four maps and their sidecars, referenced
from the assembly and from Lux's applied scene; the walk copy, imported
and shot: the plate wears the asphalt grammar and the path the sidewalk
grammar, world-projected at 3 m and 2 m, and the clutter sits ON a
surface (item 152). The twelfth zero, and two runs that were not and say
so. Logs and journals: `docs/cold_runs/cold_9015/` .. `cold_9017/`; walk
copy `_runs/walk_export_bank_block_001` is 9017's. Previously: COLD RUNS
9013 AND 9014 SCORED
ZERO ON THE BANK BRIEF; 9013 IS THE PACKAGE THAT PROVED DC 0.120.0 WRONG
AND 9014 IS THE ONE WITH THE REMAINDERS ALONG THEIR WALLS BY THE ENGINE'S
READING AND NO OUTDOOR CLUTTER ON ANY FLOOR."""))

R.append(("""*STATUS: NARROWED 2026-09-12 (night) -- THE FIX BELOW WAS HALF WRONG AND
THE ENGINE CAUGHT IT IN THE NEXT COLD RUN; THE HALF THAT STANDS IS THE
FIT.""",
"""*STATUS: NARROWED 2026-09-12 (late night) -- THE THIRD SHAPE A THIRD TIME
IN ONE DAY, AND THE LAST PLACE IT COULD HIDE WAS THE EXPORT. Cold run
9015: the Lux stage exited 2, the scheduler filed `JOB_TOOL_EXIT` as a
BLOCKING finding in the mission's validation file, and `export` shipped
the mission -- a package with no lighting, walked black. The finding
existed, was marked blocking, and nothing that ships read it; the same
shape as the placement gate (morning) and the pose census (afternoon),
one gate further down. LF 0.76.0: `export` reads the mission's open
blockers from the file `validate` reads and refuses with them named,
before the functional-lock check -- minus the Layer 3 chain
(`lot_site_surfaces`, `zoo_clutter_build`, `patina_surface_dressing`),
whose absence the package already reports in `dressing_layer.json`; a
package without its lighting reports nothing. Cold run 9016 was the first
refusal on a real run. WHAT THE BLACK FRAME ALSO TAUGHT: a whole frame at
mean brightness 15 with a flat grey sky is a scene that did not load, not
a dark texture, and the first hypothesis (the walk copy's import cache)
was wrong -- the Lux job's log named the cause in one line. The
instrument score's rule for this: when a frame is uniformly wrong, read
the stage logs before the frame. Previously: THE FIX BELOW WAS HALF WRONG AND
THE ENGINE CAUGHT IT IN THE NEXT COLD RUN; THE HALF THAT STANDS IS THE
FIT."""))

R.append(("""*STATUS: OPEN 2026-08-14 -- specified by `Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is the same boundary approached from the other side*""",
"""*STATUS: NARROWED 2026-09-12 (late night) -- THE FIRST CONCRETE STEP IS
IN A COLD PACKAGE: THE GROUND PLATE WEARS THE THEME'S SKIN. Until cold run
9017 the exterior ground in every package was one untextured grey
(`gb_floor`, 0.52, no image) -- the largest playable surface in the level
and the flattest. Pixelcoat 0.30.0 mints `asphalt` and `sidewalk` kinds;
LF 0.75.0's themed site spec names a pack per outdoor family (ground ->
asphalt, path -> sidewalk, courtyard -> concrete); Lot 0.58.0 reads the
pack and writes the maps as world-projected materials at the pack's
`meters_per_tile`, copied beside the scene. Measured on 9017's walk copy:
the plate and the path are textured, the clutter sits on a surface. WHAT
THE FRAMES SAY NEXT, which is this item's real question: the asphalt
grammar reads as cracked paving cells at roughly half a metre, not as
asphalt, and the sidewalk as a white mosaic -- the same cell family the
walls wear. The plumbing is done; the grammar is the surface, and a large
surface needs the depth guide's macro layer under the tile period before
it needs anything on top. Previously: OPEN 2026-08-14 -- specified by
`Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is the same
boundary approached from the other side*"""))

R.append(("""*STATUS: OPEN 2026-09-12 (night) -- RAISED BY THE WALKER ON THE 9012 AND
9014 FRAMES, MEASURED, NOTHING BUILT; THE BUILD ORDER IS IN THE ITEM*""",
"""*STATUS: NARROWED 2026-09-12 (late night) -- STEP 1 OF THE BUILD ORDER IS
IN A COLD PACKAGE (9017): THE GROUND PLATE AND THE PATHS WEAR PIXELCOAT
SKINS, AND THE CLUTTER SITS ON A SURFACE. Pixelcoat 0.30.0 (the kinds),
Lot 0.58.0 (`ground_skins`, maps beside the scene, `LOT_GROUND_SKIN_
MISSING` when a pack cannot be read), LF 0.75.0-0.76.1 (the spec names
the packs, the adapter publishes them, the export copies them). Three
cold runs to land it, two of them not zeros and recorded on 17 -- the
absolute-path and the unpublished-png failures were both the same lesson:
a scene's textures are its siblings, and every stage that loads the scene
copies siblings. The walker's references are digested in
`docs/SET_DRESSING_REFERENCES.md` (nine pages, two with rules, the
Reddit thread pasted in by hand, Klafke's modular rules), each mapped to
the layer and owner here. WHAT REMAINS: steps 2-4 of the build order --
decals to the package, clutter that is anchored and coloured by the
surface under it with the density table turned round, the low band where
nobody walks -- and, from the 9017 frames, the grammars themselves: the
asphalt reads as paving cells and the sidewalk as a white mosaic (item
45). Previously: OPEN 2026-09-12 (night) -- RAISED BY THE WALKER ON THE
9012 AND
9014 FRAMES, MEASURED, NOTHING BUILT; THE BUILD ORDER IS IN THE ITEM*"""))


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 18, 45, 152 updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
