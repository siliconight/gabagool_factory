# The slice's look: gaps and fixes, newest first

Judged by `RUBRIC.md`. The slice is `docs/vertical_slice/` (Delco Ave: a gas station, a bank and the library's draw).

## 2026-10-29 -- slice 1, the first build, judged

**What was built.** `workspaces/slice-1-ws`, Level Factory 0.268.0's `D01_delco_avenue` from its clone, Deli Counter
0.292.0's flush parapet from its clone, everything else at HEAD: seed 9003, candidate seed 9104 picked; the lot drew
gas_station_a02, bank_branch_a02, card_shop_a01 and train_yard_a01 (`docs/vertical_slice/`). Frames:
`frames/s1_level`, `frames/s1_inspect` (look_shots' derived cameras), `frames/s1_street_*` (`shoot_street.py`).
**Retracted, kept:** the first street stations stood at Godot z 0, behind every building; the avenue is at z 30.6
(the candidate's `site.markings.json`). Those frames were the buildings' backs and are re-shot. The re-shoot from the avenue (`frames/s1_street_*`, stations re-derived): mean brightness 22-40 of 255 in the
level's light, 57-84 under the studio light.

**The gaps, ranked by the rubric** (a defect before a missing detail; then share of frame x frames x cost):

1. **The open ground reads generated -- MEASURED.** `scatter_probe.py` on the surface-dressing manifest: 4,547 of
   6,111 pieces lay on 41,051 m2 of open ground (11.1 per 100 m2, Clark-Evans R 0.77, flat out to 10+ m from any
   edge), the wall bases where a street's debris collects held 64 (a near-grid, R 2.48), and weeds and rubble were
   drawn in equal shares in the middle of the asphalt. Owner: Patina's planner. FIX IN FLIGHT (below).
2. **The evening is black.** At the brief's `evening`, facades, ground and the far side go to near-black (several
   street frames under 5 of 255 mean); only the canopy, a few windows and the sky read. Legibility is a defect by the
   rubric, but the time of day and its mood are the walker's: **left for the walker**, with the studio-lit frames
   beside them to show what is there.
3. **Blank walls.** The bank's flank and the card shop's back are 20-30 m planes with one or two openings. Owner:
   Zoo / Deli Counter (facade layering). Next after the debris.
4. **Texture scale.** The gas station's stone reads at about twice real size. Owner: Pixelcoat. To measure.
5. **The white gutter line under the parapet.** FIX IN FLIGHT (below).
7. **The street trees read as generated -- seen from the corrected stations.** In seven of nine street frames a
   tree stands in the foreground or mid-ground as a silhouette of flat plates on a bare trunk. Of everything on the
   avenue it is the single most "computer made" shape, and it is in nearly every view. Owner: Zoo (the street
   tree species). Ranked second after the debris, before the facades, because of how many frames it is in; a
   redraw is a large change and is planned, not rushed.
6. **A train yard on Delco Ave.** The seeded draw's fourth building; plausible as "random", odd beside a bank.
   **Left for the walker** (a candidate pick, or a fabric list for D01).

## Fixes in flight, to be proven on slice 2

- **Debris gathers at edges** (Patina 0.34.0, `_scratch/patina-scupper`): on open ground (`ground` in a
  `play_space`) a candidate survives with probability max(0.06, exp(-d / 2.5 m)), d the distance to the nearest
  building, wall base or kerb; weeds and rubble only within 2 m of one; `very_high` zones (Lot's perimeter) and
  gameplay paths untouched. Re-planned on slice 1's own inputs: open ground 4,547 -> 811 pieces (11.1 -> 2.0 per
  100 m2), plate-wide R 0.72 -> 0.51; within 2 m of an edge 605 -> 413, beyond 10 m 1,585 -> 92.
  Tests: tests/test_debris_edges.py; suite 408 passed, 11 skipped.
- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, `_scratch/zoo-scupper`): a scupper, conductor head
  and downspout instead, on buildings that are not Empties.

## 2026-10-29 -- what the walker's comps show that our levels do not

The walker sent three comps of 2000s-era shooter levels (a desert city street from above, a ruined downtown
intersection at sunset, a civic bank on a plaza from above) and asked, "without copying these comps, what can you
see in these maps/levels that we aren't achieving today?" Read against seed 9082's bank block (the frames in
`docs/findings/parapet_flush/`), the gaps, as principles and not as things to copy, each with the tool that owns it:

1. **Massing that steps and overhangs** (Deli Counter). Their buildings are not extruded footprints: storeys set
   back, upper floors overhang the street, bays and balconies project, rooftops carry penthouses, stair towers,
   tanks and masts, and neighbours differ in height. Ours are boxes of similar height with flat tops; the skyline is
   one line.
2. **Facades in several planes** (Zoo). Deep reveals, shutters, awnings over each opening, cornices and string
   courses, pilasters and columns, recessed entries with steps -- every facade has three or four depths that throw
   shadow. Ours are one plane with holes in it, now with frames and sills.
3. **Weathering that tells where water runs** (Pixelcoat, Patina). Darker bases, streaks under sills and copings,
   patched render, stains, rust bleeding from metal -- value variation across one wall that follows cause. Ours are a
   uniform skin per wall.
4. **Light with a direction and a colour** (Lux). A low warm sun against cool shadow, long cast shadows, and
   atmospheric haze that pushes distance back in layers. Our level light is overcast or night: soft, even, grey.
   (The slice's time of day and weather are the walker's call; the brief says evening, clear.)
5. **Colour contrast by accent** (Pixelcoat, Zoo, Lot). A restrained base -- tan stone, grey concrete -- against a
   few saturated accents: a red truck, red paving, a lit sign, warning stripes, banners. Ours is close to one value
   everywhere with few accents beyond the signs.
6. **A ground plane with hierarchy** (Lot). Kerbs with gutters, paving bands at a frontage, a plaza in a different
   material, cracks, patches, manholes, stains and markings. Ours is road, sidewalk, lot.
7. **Clutter in groups that tell a story** (Lot, Zoo). Roadwork barricades with cones around a hole, wrecks pushed
   against a fence, a security perimeter of vans -- props clustered around a cause, not one every N metres.
8. **An overhead layer** (Lot). Wires across the street, hanging signals and lamps, banners: the top third of the
   street frame is full. Ours carries the pole line on one side and little across.
9. **A hero piece per view** (Zoo, Lot). Each frame has one thing it is about -- a neon blade sign, a columned bank
   portico on steps, a beacon mast, a palm -- larger, brighter or more detailed than its surroundings.
10. **Roofscapes worth seeing from above** (Zoo, Patina). Copings, tar patches, skylights, plant, parapets that
    differ by building -- because these levels are seen from rooftops. Ours are flat plates with a few units.
11. **An architectural language per building type** (Deli Counter, Zoo). The bank reads as a bank from 50 m:
    rusticated stone base, arched windows, columns and pediment, a name band. Ours reads as a box with a sign.

**Proposed order** (biggest change to the frame first, cheapest first among equals, every step priced):
weathering and value variation (3), facade layering on the common walls (2), the ground plane (6), clustered
dressing (7), the hero piece -- the bank's portico and the gas station's canopy (9, 11), massing and roofscape
(1, 10), the overhead layer (8). Light (4) and colour (5) touch the walker's taste and are proposed, not changed
alone.

## Fixes in flight

- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, clones `_scratch/patina-scupper`,
  `_scratch/zoo-scupper`): a non-Empty building's roof drains through a scupper in its parapet into a conductor head
  and a downspout; the white gutter line 1.4 m below the bank's top goes. Empties keep their gutters (the walker's
  call, 2026-10-04) -- **left for the walker**: should a rowhome with a parapet drain through it too?
