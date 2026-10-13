# Philly street comps: what a street is made of, and what the factory does not make yet

The walker, 2026-10-11, with three photographs: "some really good comps that
you need to learn from". Shown in chat and not stored here; one carries
another party's watermark. Read for what a generator can learn -- the parts,
where they stand and why -- never copied. Each element is mapped to the tool
that would own it and to what exists today (checked the same day against
Zoo's species list, Deli Counter's presets and Lot).

## What the three photographs show

**1. A corner at a wide avenue, winter, overcast** (shot from a parked car).
- A WOODEN UTILITY POLE carries everything at the corner: a cobra-head
  streetlight on a long arm, the green street-name sign, a traffic signal
  for the side street mounted low on the pole, equipment boxes, and a web of
  OVERHEAD WIRES crossing the frame in every direction.
- A vacant lot fenced with grey corrugated metal panels; a low commercial
  building with a painted band beside it.
- The ground in front: broken asphalt and gravel, a pothole, paper and
  plastic litter collected along the lot's edge -- not spread evenly.
- A rounded concrete kerb at the corner, a striped crosswalk, parked cars.
- Behind: three brick public-housing towers, about twelve storeys, small
  regular windows, flat roofs with penthouses; two-storey infill homes with
  small gabled porches; bare trees.

**2. A neighbourhood from a tall building, golden hour.**
- To the horizon, rowhouse blocks in a grid. Their roofs are FLAT and most
  are SILVER or WHITE coated, some black tar; rear ells step the roofline
  down at the back; chimneys, hatches, a few skylights.
- In front, a commercial corridor: two- and three-storey buildings, a shop
  at grade and windows above, every front its own colour and material, a
  sign band and awnings per shop (blue, red), corner stores at the ends.
- In the middle distance a ballfield as open ground, institutional
  buildings, and on the horizon smokestacks and a water tower.
- Low sun from the side, long shadows across the roofs.

**3. A rowhouse street on a summer day, a block party.**
- A narrow one-way street between two continuous rows, three storeys, red
  brick beside grey parged (stuccoed) fronts.
- STOOPS: three or four steps up to each door, with iron railings; the
  first floor stands above the sidewalk.
- SATELLITE DISHES mounted on the FRONTS at the second floor, on many houses.
- Cobra-head streetlights on poles at the kerb; wires overhead.
- Pop-up canopy tents (blue, green), folding lawn chairs, toys, chalk on the
  asphalt, kids riding in the street, trash cans and bags, parked cars on one
  side, a van at the far end.

## Which tool owns each element, and what exists

| element | today | owner of the change |
|---|---|---|
| wooden utility poles, overhead wires along the block and across the street | **absent**: no pole or wire species; `streetlight` stands on its own pole | Zoo (a `utility_pole` species, wire spans generated as thin meshes), Lot (a pole line along the kerb, spans across at junctions) |
| cobra-heads, street-name signs and signals ON the utility pole | `streetlight`, `sign_post`, `traffic_signal`, `stop_sign` exist as separate poles | Lot (mount them on the pole line where one stands), Zoo (arm variants) |
| stoops with railings, a raised first floor | stoops only on the twin preset; the rowhome Empty's door is at grade | Deli Counter (`empty_rowhome`: a raised first floor and a stoop volume -- a rise is gameplay geometry, so the contract's step limits decide its form), Zoo (a stoop with railings) |
| satellite dishes on the fronts | `satellite_dish` exists, placed on Empty roofs only | Patina (facade anchors at the second floor), Deli Counter (which houses) |
| silver-coated flat roofs, some tar; rear ells | the rowhome roof is `concrete`; no ells | Pixelcoat (a silver roof-coating pack and a tar one), Deli Counter (a rear ell in the rowhome massing) |
| a mixed-use corridor: shop at grade, homes above, colour and sign per front | shops and homes are separate buildings | Deli Counter (a mixed-use preset), Lot (a corridor row), Pixelcoat and Zoo (sign bands, awnings), the invented brands rule |
| litter collected where it collects: lot edges, gutters, fence lines | `litter_scrap`, `trash_bags`, `litter_bin` exist; Layer 3 dressing places clutter | Lot (dressing anchors by cause: kerb lines, fence bases, lot edges) |
| broken and patched asphalt, potholes | road paint and plain asphalt | Pixelcoat (roadmap 237 tier A: patching, cracks, as pack layers) |
| a vacant lot behind corrugated metal | `chain_link_fence` exists; vacant lots are queued (land-use guide) | Lot (vacant lot parcels), Zoo (corrugated and plywood fence kinds) |
| a block party: canopies, lawn chairs, toys, chalk | `folding_chair` exists; no canopy tent | Lot (a street-use state for a residential street by day, like the five times of day), Zoo (a canopy species); people are the gameplay layer's |
| brick public-housing towers, smokestacks, a water tower, a ballfield | the edge recipes carry rowhomes, a water tower, warehouses, trees (roadmap 228, the walker's E) | Lot and Zoo (a tower massing and stacks in the backdrop recipes, by level) |
| flat overcast light | five times of day; rain is a weather | Lux (an overcast sky beside clear) |

## The first three to build, by what reads as this place and is absent

1. **The pole line and its wires.** In two of the three photographs the
   overhead network is the strongest single line in the frame, and the
   factory has none of it. A street's poles, wires, lamps and signs are one
   system: lamps and signs belong ON the poles. Cheap if built right: wire
   spans merged one mesh per street per material, no shadow casting.
2. **The rowhouse front: stoop, railings, a dish on the front.** Every
   residential frame in the set has them, and a stoop is also cover and a
   height step for gameplay, so the contract decides its riser.
3. **The silver roofs.** The aerial frame is mostly silver and white roofs;
   ours are concrete-grey. A pack and a material choice -- and since roof
   props arrived, players see roofs. GROUNDED 2026-10-12 at the walker's
   asking (`ROWHOUSE_ROOFS.md`): "silver" is an aluminum coating over a tar
   membrane, and white roofs are mostly after Philadelphia's 2010 cool-roof
   law; the walker's call, tar now (Deli Counter 0.210.0) and the coating
   when a 1990s source says how common it was.

Each is a level-creation change (the walker's priority, 2026-10-11) and each
is a generator rule, never a placement in a workspace.
