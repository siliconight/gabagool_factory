# Cold run 9222 -- 0 interventions, 0 retries; the deli's band and door box in Blue Highway, smooth, at the art's own 6:1

restaurant_row_001, evening and clear, seed auto, staged from 9185's batch
and brief. It proves roadmap 223. A dealt business's sign pack is now:
- lettered smooth in Blue Highway Condensed at its band's 6:1 (Pixelcoat
  0.62.0);
- sampled as the pack asks, both on the band (Lot) and on the door box (Zoo
  1.94.0), and fitted to the door box at its own shape;
- carried with its manifest to the package (Lot 0.105.0);
- imported compressed with mips (Level Factory 0.166.0).

Tool versions hashed at `--begin` (`_runs/cold/cold_9222/before.json`):

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.166.0 |
| Lot | 0.105.0 |
| Lux | 0.72.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.94.0 |

Against 9221, the four releases of 223 are what moved.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9104**, as in 9185.
  - The buildings are deli_a01, office and rail_station_a02, with 12
    Empties.
  - The other two candidates each had 1 major finding. All three completed
    their routes.
- **The shell leg:** 0 blockers of 52. **The art leg:** 0 blockers of 74.
- **Findings, 65 to 74 against 9185.** Eight of the ten tools moved between
  the two runs, so the difference is NOT attributed to 223:

  | tool | 9185 | 9222 |
  |---|---|---|
  | Deli Counter | 0.188.0 | 0.205.0 |
  | Laser Tag | 0.23.2 | 0.25.0 |
  | Level Factory | 0.148.0 | 0.166.0 |
  | Lot | 0.97.1 | 0.105.0 |
  | Lux | 0.66.0 | 0.72.0 |
  | Patina | 0.29.1 | 0.30.0 |
  | Pixelcoat | 0.61.0 | 0.62.0 |
  | Zoo | 1.79.0 | 1.94.0 |
  - The new codes come from checks added since 9185: `S_GETAWAY_AT_SPAWN`
    4, `S_RESPONDER_ARC` 4, `S_STREET_CROSS` 6.
  - `PRESENTATION_ZFIGHT`'s 1 to 3 is Deli Counter's gate reporting per
    building since 0.198.0. That is 2, 2 and 1 coplanar pairs, of which "0
    can be seen".
- **The bake:** 479 models and 4,259 users, 100.5 s in the editor.
- **The deal:** `[site] 1 shop sign(s): b0=scrapple_sons_deli`, the same
  business 9185 dealt deli_a01. The office and the rail station take no band
  (Level Factory 0.147.0's `NO_BAND` and family rules).

## The chain, read off the walk copy

Read from `_runs/walk_export_restaurant_row_001`, which is the package plus
the walk wrapper:

| link | 223 asked for | 9222 |
|---|---|---|
| Pixelcoat 0.62.0 | smooth type, at 6:1, sampled linear, with mips | albedo and emissive 1,536 x 256. The pack's `import_hints`: `interpolation` "linear", `generate_mipmaps` true. `tool_version` 0.62.0 |
| Lot 0.105.0 | the pack's manifest travels | `signs/sign_scrapple_sons_deli.pack.json` beside its maps |
| Lot (from 0.97) | the band samples as the pack asks | band material `Mat_sign_b0` has no `texture_filter`, so it uses Godot's filtered default. 9185's carried `texture_filter = 2`, nearest |
| Level Factory 0.166.0 | the sign maps import compressed, with mips | `sign_scrapple_sons_deli_albedo.png.import`: `compress/mode=2`, `mipmaps/generate=true` |
| Zoo 1.94.0 | the door box samples as asked | `M_SignBox_sign_scrapple_sons_deli_Face` in `lot/deli_a01/art/fixtures/deli_a01_fixtures.glb`: magFilter 9729 (LINEAR), minFilter 9987 (LINEAR_MIPMAP_LINEAR), clamped both ways |
| Zoo 1.94.0 | the door box keeps the art's shape | face 2.05 x 0.60 m. UV u 0 to 1, v -0.378 to 1.378. The art lies on the face at **6.0:1**, its own 1,536:256. The surplus height clamps to the art's edge rows |

**The band.**
- It is a 9 x 1.5 m box, 6:1, centred at Godot (-58, 3.6, 13.16), with its
  face toward +z.
- 9185's band was the same box. The pack it wore was 4:1, so its letters were
  stretched 1.5 times across (`docs/findings/street_band_type/`).

## Frames (evening, the level's own light)

`tools/look_shots.py` on the walk copy, at two stations.

**`band_evening.png`: band, from (-58, 1.7, 23).**
- The band reads SCRAPPLE & SONS DELI in Blue Highway Condensed. Its edges
  are smooth and its letters stand at their own width.
- The door box shows at the left of the frame, wearing the same name.

**`door_box_evening.png`: door, from (-68.5, 1.7, 17.5).** The door box
reads the same name, unstretched, with the art's red field above and below
the lettering.

**Observed and not changed: two calls for the walker.**
- **A lamp pole stands in front of the band and hides the E of SCRAPPLE.**
  - The lamp is Lot's sidewalk lighting, and the band is also Lot's.
  - Neither placement knows about the other. That is a rule Lot does not
    have yet: keep a pole out of a band's sightline from the street.
- **The door box reads brighter than the band.**
  - The box's face emits its albedo at Zoo's strength.
  - The band's emission multiplier is 0.65.
  - Whether the two should match is taste.

A third station, from (-63, 1.7, 27), stood behind something at eye height
that crossed the whole frame. It is not used here, and what it was was not
looked into.

## Roadmap

223 is CLOSED by this run.
