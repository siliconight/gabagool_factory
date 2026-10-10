# Cold run 9219 -- 0 interventions, 0 retries; the box truck and the litter bin, drawn, on the walked level

club_block_014, seed 9181 at night: the level the walker walked on
2026-10-09 (cold run 9213). It is staged from 9218's batch and brief, and
proves roadmap 219 note 5, "i dont know what this giant grey box is":

| what | fix |
|---|---|
| `box_truck`, a 1990s cab-over in four invented fleets | Zoo 1.92.0 |
| `litter_bin`, a municipal street bin | Zoo 1.92.0 |
| each parked truck's fleet, from where it stands | Lot 0.103.0 |

Tool versions hashed at `--begin` (`_runs/cold/cold_9219/before.json`):
Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, Level Factory
0.165.0, Lot 0.103.0, Lux 0.72.0, Patina 0.29.2, Pipeline 0.6.0, Pixelcoat
0.61.0, Zoo 1.92.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9181,** as 9213, 9217 and 9218 picked it. It carries
  strip_club_a01, funeral_home_a03, airport_terminal_a02 and the 12 empty
  rowhomes.
- **The shell leg:** 0 blockers of 51 findings. **The art leg:** 0 blockers
  of 71.
- **Findings 71 to 71.**

## What the site asked Zoo for

From the assemble's `site.slots.json`:
- **one box truck:** `cover_154`, 2.4 x 6.0 x 2.8 at plan (-39.904, 3.663),
  yaw 0, **variant 2**. Lot 0.103.0's `cover_variant` picked it from where
  the truck stands, and it ships as
  `prop_box_truck_delco_1997_01_w240_d600_h280_n2.glb`: NANA'S BASEMENT
  SELF STORAGE.
- **one litter bin:** `cover_23` on the sidewalk at plan (34.7, -16.6),
  shipping as `prop_litter_bin_delco_1997_01_w60_d60_h100.glb`.
- **Two more drawn bins** reached the package from the buildings' own prop
  slots: `..._04_w50_d50_h85_mmetal` and `..._04_w60_d60_h100_mmetal`. Both
  are the same species and the same recipe.

**The bake** (`export.log`): 433 models and 1,528 primitive meshes
lightmapped, 3,894 users against 9218's 3,890. That is the truck's five
materials against the old box's one, 91.5 s in the editor.

## In the frames

`tools/look_shots.py` on the walk copy at midnight, at given stations
(`truck_and_bin.png`). Luma is of 255.

**The litter bin reads at once:** green steel slats, the lid's mouth, and
the placard, LITTER over KEEP DELCO CLASSY-ISH. Mean 34.9 from 1.7 m.

**The box truck reads as a truck:** the cab-over's flat face, the grille,
the headlamps and amber markers, the box standing taller behind the cab, and
the wheels. Mean 7.2 from its front corner. **Its livery does not read at
midnight.** The box's sides face away from the moon, and in its shadow they
are lit by nothing but the bake's bounce. The face's median is 2.

**That bounce is blotched** (`box_side_bake.png`):
- after an 8 px blur, the face's luma runs from p5 1 to p95 6;
- **the control:** with the lightmap switched off (`--switch-off
  lightmap`), the face is black all over. So the blotches are the bake's,
  not the truck's art;
- Blender's render of the same fleet, built after the run from Zoo
  1.92.0's truck code (7,918 tris), shows a clean white box with faint
  grime (`box_truck_v2_blender.png`).

That is a finding about the bake on a large pale face lit only by bounce,
not about the truck. It is filed as roadmap item 224.

**The edge of the world is the brightest thing in the truck's frames.**
Behind the truck, the `perim_*` wall shows as a pale flat band across the
horizon. That is roadmap 219 note 8, and it is the next menu.
