# Grocery store interiors: the walker's comps, and what each tool owes them

The walker, 2026-10-26, after walking seed 9205's supermarket ("far too dark in teh super market"):

> grocery store inside comps including lighting

> shiny floor, bright lights, isles, glowing freezer section, stacked high

> look up 1990s grocery store interior for more inspiration

Five photographs came with it. They were shown in chat and are not stored here. What follows was read off
them, and it covers format only. The chains, their banners ("ROLLBACK", "MADE IN USA", the price cards) and
every brand on the shelves are real, and none of them is reproduced. Store names and brands come from the
factory's invented-brand sources (`zoo/core/brands.py`); see the memory on fake Delco brands.

## WHAT THE COMPS AGREE ON

All five are high-key interiors. Nothing in them is in shadow, and the whole look is light and repetition.

- **Bright lights, in lines.** Long continuous runs of bare fluorescent strips hang from a white ceiling,
  either a dropped tile grid or the painted deck. They run the length of the store, about 2 to 3 m apart.
  Overhead you read one run, not separate fixtures. In the freezer comp the runs follow the aisle; in the
  general-merchandise comps they cross it. The ceiling is lit too, and it is the second-brightest surface in
  every frame.
- **A shiny floor.** The floor is pale vinyl tile (VCT), white to light grey, polished until it mirrors each
  fluorescent run as a streak down the aisle. In three of the five comps this is the most recognisable thing
  in the frame. A coloured accent stripe (red or maroon) runs along the main aisle like a racetrack and
  marks the department edge. One comp puts carpet under a single department (clothing), as an island.
- **Aisles.** Gondola runs stand about 1.8 to 2.1 m high, with endcaps facing the main aisle. Low tables
  and dump bins stand in the main aisle. Above each aisle hangs a sign with a number and categories, about
  3 m up. Department signs hang from the ceiling as big coloured boards, readable from across the store.
- **A glowing freezer section.** One whole aisle has glass-door reach-in freezers on both sides, lit from
  inside, with a fluorescent tube down every mullion. The cases are brighter than the floor in front of
  them, and the floor carries their reflection. The ceiling over the aisle can be dimmer, because the cases
  light the aisle.
- **Stacked high.** The shelves are full to the top, and product is faced forward so each shelf reads as a
  solid band of colour. Wall shelving goes higher than the gondolas. A perimeter band of colour (red, blue)
  runs above the wall shelving, under the ceiling. In the "stacked high" comp, every shelf is one product
  repeated across its width, with a big price card at eye height.

## WHAT THE PERIOD SOURCES ADD (1990s)

- **Flat, even fluorescent light was the norm.** It was the period's standard, and designers were already
  complaining that uniform tube lighting made everything look flat. That flatness is the 1990s look. The
  comps want the flat brightness, not a modern accent-lit store.
  ([Supermarket News](https://www.supermarketnews.com/fresh-produce/expert-proper-lighting-use-makes-fresh-products-shine))
- **Light levels by zone,** from a food-distribution lighting study:
  - non-perishable sales area: up to about 100 fc;
  - wall wash: about 180 fc;
  - front end (checkouts, under a ceiling dropped to about 10 ft): about 120 fc;
  - work areas: 50 to 80 fc;
  - storage: about 25 fc.

  So the stockroom is meant to be about a quarter as bright as the sales floor. Ours had it backwards (the
  sales floor at p50 3 against the back stock's 77, [`walk_2026-10-26_panel/` L4](../findings/walk_2026-10-26_panel/README.md)).
  ([ageconsearch.umn.edu](https://ageconsearch.umn.edu/record/27460/files/12010093.pdf))
- **Overlit was common.** An EPA/FMI design guide found aisle centres above 200 fc. It recommends fluorescent
  strip lighting as the general sales lighting.
  ([EPA/FMI](https://19january2021snapshot.epa.gov/sites/static/files/documents/Designing_for_Energy_Efficiency_2010FMI.pdf))
- **Freezer aisles can be lit by the cases alone.** One store's freezer aisle had no ceiling lighting at all,
  and the case lights lit the aisle.
  ([LSI, Tops Market](https://portal.lsicorp.com/wp-content/uploads/LSI-Flyer-ProjectSpotlight-Tops-Market.pdf))
- **The floor was VCT.** The industry's own trade press describes the standard supermarket floor as plain
  VCT, before the move to decorative floors.
  ([Progressive Grocer](https://progressivegrocer.com/floors-ceilings-enhance-supermarket-experience))
- **The local chains' interiors were not found.** No 1990s interior photographs of the Philadelphia chains
  (Acme, Pathmark, Genuardi's, Super Fresh) turned up. The one Delco note on record is that Genuardi's 2000
  decor package used a black ceiling. That is past the comps' period, so it is a variant at most.

## WHAT THE LIBRARY HAD, 2026-10-26 (`supermarket_a01`, Deli Counter 0.272.0)

| comp                      | the build                                                                                              | owner                                                 |
|---------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| bright lights, in lines   | 12 lamps for 1,056 m² (3 rows of 4, 11 m apart), held there by `lights._MAX_LAMPS_ROOM`                 | Deli Counter `lights.py`, priced in Lux                |
| shiny floor               | tile since 0.271.0, matte                                                                              | Pixelcoat / the tile material; Lux's room probe       |
| racetrack stripe          | none                                                                                                   | Deli Counter floors                                   |
| aisles                    | 5 gondola runs, 2.0 m (0.272.0)                                                                        | Deli Counter + Zoo `snack_gondola`                    |
| aisle signs               | none; Zoo `aisle_sign` exists (card shop)                                                              | Deli Counter routes, Zoo paints grocery words         |
| glowing freezer section   | none; Zoo `cooler_run` exists (convenience store, emissive, 3 draws a run)                              | Deli Counter places it                                |
| stacked high              | gondola product panels; wall run is the furnish's generic `shelf_run`, plus filing cabinets and vending | Deli Counter furnish; Zoo stock                       |

## The walker's link, 2026-10-26: guide.pinterest.com/design/old-supermarkets/

18 photographs, read from their alt text only: the fetch returns the page's words, not its images. These points
confirm the comps above:
- even linear fluorescent runs;
- polished tile;
- dense vertical stacking;
- long refrigerated walls anchoring aisles.

These add to them:
- **A produce section.** Baskets and tables of fruit and vegetables under a category sign.
- **Category and promo signage.** Ceiling banners and hanging boards; some neon over produce and drinks.
- **Exposed ceiling pipes or beams** in some stores, in place of a dropped tile grid.
- **Checkered black-and-white floors** in the smaller and older shops. The supermarkets' floors are pale.
