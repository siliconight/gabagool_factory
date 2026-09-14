"""Roadmap batch 63, 2026-09-14: cold runs 9051 and 9052 are two more zeros and
9052 is the first walked in rain (17); the rain walk's findings and what fixed
them go into item 155's ledger; the rain slice shipped (157); the cars shipped
(158); items 159 (interior furnishing) and 160 (the hero vault) are filed.

Anchored; each anchor must match exactly once; refuses to write on a miss.
Run from the factory root, then `python tools/roadmap_status.py --write` and
`--check`.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

EDITS = [
    ("item 17", """*STATUS: NARROWED 2026-09-13 (late night) -- 9044 THROUGH 9050 ARE SEVEN
MORE ZEROS, AND 9050 CARRIES THE WALKER'S SECOND ROUND.""",
     """*STATUS: NARROWED 2026-09-14 -- 9051 AND 9052 ARE TWO MORE ZEROS, AND 9052
IS THE FIRST PACKAGE WALKED IN THE RAIN. Both: 0 interventions, 0
unattributed, 0 retries, export exit 0 (docs/cold_runs/cold_905N/run.log).
9051 carried Deli Counter 0.127.0 (a one-storey switchback cuts one run);
9052 carried the new cars (Zoo 0.79.0, Lot 0.70.0) and rain (Lux 0.35.0, LF
0.83.0), with the bank brief's `weather` set to "rain" as the run's input.
The walker's rain walk produced fifteen findings in an hour, recorded in item
155; every one was found by a person, none by a gate. Previously: 9044
THROUGH 9050 ARE SEVEN MORE ZEROS, AND 9050 CARRIES THE WALKER'S SECOND
ROUND."""),
    ("item 155 status", """*STATUS: NARROWED 2026-09-13 (late night) -- EIGHTEEN OF THE ROUND'S
FINDINGS HAVE A SHIPPED FIX, SOME NOT YET SEEN IN GAME, AND THE
FRAMES OF THE FIX FOUND A NEW ONE.""",
     """*STATUS: NARROWED 2026-09-14 -- THE RAIN WALK (COLD RUN 9052) ADDED FIFTEEN
FINDINGS; ELEVEN HAVE A SHIPPED FIX, NONE YET WALKED. Listed under "THE RAIN
WALK" below. Open: the interior furnishing (item 159), the vault as a hero
piece (item 160), and two look decisions waiting on the walker (Lux's
per-channel quantiser under a calm wall, and the rain preset's film grain).
Previously: EIGHTEEN OF THE ROUND'S FINDINGS HAVE A SHIPPED FIX, SOME NOT YET
SEEN IN GAME, AND THE FRAMES OF THE FIX FOUND A NEW ONE."""),
    ("item 155 close", """**WHAT WOULD CLOSE THIS:** every entry above fixed or explicitly declined by
the walker, and a walk of a fresh cold package that raises none of them
again.""",
     """THE RAIN WALK (cold run 9052, walk copy `_runs/walk_9052_rain`).

34. **The one-storey switchback's open run** (entry 33; DC 0.127.0).
    `stairwell.hole_span`: a single-storey switchback cuts and reserves only the
    run its leg climbs in. 59 stairs in 53 specs. Seen in 9051's arena frame.
35. **Windows opaque** (Pixelcoat 0.40.0, Zoo 0.80.0, Lux 0.36.0, LF 0.84.0).
    `glass_delco` had no transparency block -- not a decision: Pixelcoat's own
    0.17.0 entry calls it orphaned content. Four owners: the grammar, a Zoo
    warning, Lux's window rigs drawing a panel in front of the glass, and a
    blended material casting an opaque shadow. Facade shells keep opaque
    `glass_facade` (DC 0.128.1 restored the lost tag).
36. **Far-wall moire on corrugated steel** (LF 0.85.0). Kit textures embedded
    uncompressed carried no mipmaps: 138 of 138 metal surfaces. A/B
    high-frequency energy 22.32 -> 12.58. The walker's articulation of it was
    interference; the mechanism is aliasing with the same arithmetic.
37. **"2 surfaces clashing" behind the teller line** (DC 0.128.0). My
    regression: 0.126.0's staff room added floor and ceiling skins over the
    lobby's. `floors.nested_room_voids`; also fixed `gs_corner_station`.
38. **"should we just fill in these gaps?"** beside the stairs (DC 0.128.0).
    Side guards fill the 0.4 m margin flush to the flight. The claim that this
    costs the navmesh nothing was REFUTED by the nav gate on `twin_a01` (0.9 m
    flights split into islands); flights under 1.1 m keep the slot.
39. **"a light inside of a vault?"** (DC 0.128.0). Solids reaching the ceiling
    band are keep-out rects for lamp rows; 2 bulbs in or at the vault -> 0.
40. **Waiting chairs z-fighting on the wall** (Zoo 0.81.0, DC 0.129.0). Backs
    coplanar with the wall face, 0.00 mm: DC placed wall pieces 0.12 m off the
    centreline of a 0.30 m wall, burying every one 3 cm. Library refurnished.
41. **"pathing here seems kind of random?"** (Lot 0.71.0, 0.72.1). Setback
    strips were bare asphalt with a door path's diagonal-reading sides; now
    paved frontage. The diagonal b1->b2 path was drawn MIRRORED -- slab writers
    passed `-angle`, and the step checker read Godot's transform as columns.
42. **Cargo container a flat box** (Zoo 0.82.0). 44 tris, no corrugation;
    now an ISO container with castings, rails, locking-bar doors, markings.
43. **Wall texture "circular blotches"** (Pixelcoat branch; Zoo 0.81.1 shipped
    the seam half). `worley_f1` cells at 8 cm; seams were 6 mm V-grooves from
    3 mm end bevels, not gaps. The calm drywall waits on the walker: it exposes
    teal/mauve banding from Lux's per-channel quantiser.
44. **White lumps on the sidewalk; "white boxes at the stop signs"** (Lot
    0.72.0, Patina 0.22.0, LF 0.86.0). Dressing sat at z 0 inside raised slabs
    (2,587 of 4,948 off their surface -> 0); the clutter build ran without
    skins and its textures were never saved; vertex colour was never on for
    any object. The stop-sign boxes are the placeholder fire hydrant (Zoo,
    branch in progress).

FOUND BY AGENTS, NOT FIXED: the hero vault's breached state is not
repeatable (shard vertex order changes per build); Lot 0.72.0 did not rebuild
9052's own scene byte for byte from today's inputs, and its walktest spine
differed (302 m against 405 m) -- unexplained.

**WHAT WOULD CLOSE THIS:** every entry above fixed or explicitly declined by
the walker, and a walk of a fresh cold package that raises none of them
again."""),
    ("item 157 status", """*STATUS: NARROWED 2026-09-13 (late night) -- THE OWNER IS LUX AND SLICE 1 IS
IN PROGRESS ON A BRANCH. Rain only; wetness and puddles are later slices.*""",
     """*STATUS: NARROWED 2026-09-14 -- SLICE 1 SHIPPED AND WAS WALKED: RAIN OUTSIDE,
DRY INSIDE. Lux 0.35.0 and LF 0.83.0; cold run 9052 walked it. Against rain
off, the two street shots rose 12,182 and 17,897 pixels and every under-roof
shot 0; at 9,000 drops viewport GPU cost was +0.016 to +0.07 ms (RTX 2060). Measured on Godot 4.7 Compatibility: particle
trails, sub-emitters and volumetric fog do not render; box and heightfield
collision work. Wet ground, puddles and a night rain preset remain.*"""),
    ("item 158 status", """*STATUS: NARROWED 2026-09-13 (late night) -- ZOO IS REBUILDING THE CAR ON A
BRANCH. Nothing merged.*""",
     """*STATUS: NARROWED 2026-09-14 -- SHIPPED AND WALKED IN 9052, NOT YET JUDGED.
Zoo 0.79.0: sedan, hatchback, SUV and coupe with separate see-through panes
(Godot readback: transparency on, alpha 0.38), interiors, arches, lamps, 0
coplanar pairs in 646 builds. Lot 0.70.0: 8 distinct car modules per street
instead of 1, and 19 of 42 cars that faced into traffic now face their lane.
LF 0.86.0 draws their wear shading for the first time. The walker has not
named them yet.*"""),
]

APPEND = """

*STATUS: OPEN 2026-09-14 -- ZOO SIDE SHIPPED; DELI COUNTER'S FURNISH REWRITE
NOT STARTED.*

**159. Rooms are a table-and-chair round robin.** The walker, in cold run
9052's `country_club_a01` basement: "need a lot more species for this room,
its just a bunch of chairs and tables with nothing on it, boring". The room is
`wine_cellar`, which matches no `_FURNITURE` keyword; 272 of 691 library rooms
hit that default. The plan, with the measurements, is
`docs/proposals/INTERIOR_FURNISHING.md`: whole-token room matching, a recipe
per room kind (anchors, wall run, clusters), a size palette, and items on
surfaces chosen by room kind. Zoo 0.84.0 shipped the pieces: carton_stack,
furnace (and water heater), dust_sheet, pool_table, booth_seat (and sofa), and
`_surface_stock` flavours office / bar / kitchen / vault / storage carried in
prop slots as `stock`, `variant`, `form`. Deli Counter must write those
fields, mirror them in `themed_tscn.module_stem`, route the new names in
`prop_species.PROP_SPECIES`, and replace the round robin.

**WHAT WOULD CLOSE THIS:** a cold package the walker walks room by room and
names each room's use from what is in it.


*STATUS: OPEN 2026-09-14 -- THE DOOR IS BUILT; THE ROOM AROUND IT IS IN
PROGRESS.*

**160. The bank vault is a box.** The walker: "the bank vault should absolutely
be a hero piece", with references of round riveted vault doors. The vault in
`bank_branch_a02/a03` and `bank_job` is a 5 x 5 x 3 m prop volume with no
species; no modular spec has a `vault` opening, so Zoo's `vault_door` had never
been built for a level. Zoo 0.83.0: a round door in a riveted surround with
wheel, bars, dial and hinges, in the four states DC's `vault_door` machine
names, with per-state collision. Deli Counter must size the vault slot to the
module (3.6 m for a 1.3 x 2.1 aperture, not the aperture's width), drop the
0.15 m sill, face the approach, keep the swing clear, and turn the box into a
vault room -- in bank_branch_a02 the box also stands in the wrong room for
its objective and loot.

**WHAT WOULD CLOSE THIS:** the walker opens a generated bank's vault and calls
it the hero piece.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings; refusing", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for label, old, _new in EDITS:
        n = text.count(old)
        if n != 1:
            print(f"anchor {label} matched {n} times; refusing", file=sys.stderr)
            return 1
    if "**159. " in text:
        print("item 159 already exists; refusing", file=sys.stderr)
        return 1
    for _label, old, new in EDITS:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + APPEND
    io.open(P, "wb").write(text.encode("utf-8"))
    print(f"{P}: batch 63 applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
