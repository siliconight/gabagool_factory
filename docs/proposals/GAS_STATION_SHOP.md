# The gas station and its convenience store

PROPOSED. Nothing here is built. The walker asked for it during the 2026-09-26
walk of cold run 9080's package (`docs/walks/WALK_9080_DRIP.md`), with
references, and this records what was MEASURED about the current one beside
what was asked for, so the gap is a list rather than an impression.

## What is there now, measured

`lot/gas_station_a02/site.tscn`, cold run 9080's package.

**The forecourt is built and completely unlit.**

    canopy_roof     world (92, 10)   22.0 x 13.0 m   soffit at y 4.90
    canopy_col x6   world x 87 / 97,  z 2 / 10 / 18   4.90 m tall
    pump_island x3  world (92, 4) (92, 10) (92, 16)   1.60 x 8.00
    pump x6

    Lux fixture holders within 45 m : 20
      7 pendant, 10 fluorescent, 1 sign box, 2 wall pack
      their world x range : 58.7 .. 81.3   -- all on the SHOP
      the canopy spans    : 81.0 .. 103.0  -- none over it

Zoo has `pendant_fixture`, `fluorescent_fixture`, `club_fixture` and
`sign_box`, and **no species that goes on a canopy soffit**. Lux lit what it was
given; it was not given a canopy. This is not a Lux defect.

**The shop is nearly empty.** The building has six rooms -- `sales_floor`,
`food_service`, `stockroom`, `walk_in_cooler`, `back_hall`, `manager_office` --
and the whole building carries **19 dressing props**:

    cartons x5   table_work x4   counter_service x2   grill x2
    vending x1   shelf_run x1    table_dining x1      litter_bin x1
    pallets x1   counter_kitchen x1

A 1990s convenience store is dense. Nineteen props in a six-room building is
the reason it reads as a shell with furniture in it.

## What the references show

The walker's set, 2026-09-26: a Wawa interior (green and purple walls, coffee
island, checkerboard tile band, service counter under a lit valance), a 1990s
store interior (fluorescent ceiling grid, packed gondolas, magazine wall,
floor displays), a lit storefront at night (window band, promo boards, stacked
cases outside), a corner-store exterior, and a coffee counter of glass carafes
on burners with orange decaf handles.

Three things carry the read, in order:

1. **The canopy is the light source.** In every forecourt reference the soffit
   is a grid of recessed fixtures and the fascia band glows. The tarmac is lit
   by the canopy, not by street lighting.
2. **The window band is the second light source**, and it is what makes a shop
   read as open at night.
3. **Density inside.** Product on every shelf, cigarettes overhead behind the
   counter, coffee, impulse racks at the till, cooler doors along one wall.

## The asked-for list, as given

Walker, 2026-09-26: "the building adjacent to the pumps/canopy, we would
categorize as the gas station convenient store. Should have products, coffee,"
and then "cigarettes,". The list is open; this file is where it accumulates.

    products    -- gondola shelving with stock on every shelf
    coffee      -- the carafe counter: burners, glass pots, condiment rail
    cigarettes  -- the overhead rack behind the service counter
    gum         -- the impulse rack at the till
    snacks      -- crisps, candy, the racks that face the queue

AND THE PERIOD IS SPECIFIC. The walker's last reference is a Philadelphia Daily
News piece, "The LAND of MILK and HOAGIES", photographing Wawa's CEO at a NEW
cappuccino bar -- syrup bottles in a row, stacked cups above, a dedicated bar
counter. That is the 1990s convenience store growing a coffee programme, dated
to the decade this theme is set in, and it says the coffee station should read
as a BAR with syrups and cup stacks rather than as a pot on a warmer.

## Two more references, and one of them dates the whole thing

**The period is exact, and the reference says so.** Wawa's own fact sheet:
"began opening stores with gasoline operations in 1996 in an effort to provide
customers with a total one-stop shopping experience". A 1997 Delco forecourt
with a convenience store attached is not a liberty -- it is the year the format
arrived. The same sheet gives the shape of the offer: built-to-order hoagies,
brewed coffee, a hot breakfast sandwich, burgers and fries, and "more than
6,000 items including groceries, tobacco and candy".

**The cooler is a dense wall of labelled product.** The walker's close-up: a
glass-door reach-in, wire dividers holding each row straight, and a blue price
rail under every shelf carrying a printed tag per facing. The rail is what
makes it read as a shop rather than as bottles on a board, and it is a strip of
texture rather than geometry.

**The pumps are mechanical, and that is the period tell.** The walker's
close-up: three grades in separate colour-coded bodies (silver, red, gold),
each with a MECHANICAL PRICE WHEEL showing dollars-per-gallon to the
nine-tenths -- 1.55, 1.45 9/10, 1.65 9/10 -- above a smaller wheel for the
sale. Coiled black hose, nozzle in a holster on the face, a stencilled
"UNLEADED GASOLINE" plate, grade buttons along the front, and a yellow bollard
at the island end. A digital seven-segment display would date the whole
forecourt wrong by a decade, and the 9/10 fraction is the detail that reads as
1997 at a glance.

Zoo's `pump` species exists; whether it carries wheels, a holstered nozzle, a
coiled hose and per-grade colour has not been checked against this reference.

**THE BRANDS ARE INVENTED.** These references are Wawa, and nothing shipped
carries a real mark. The rule is already the repo's: invented Delco-slang
brands on every branded surface, PG-13 crass, no real trademarks -- the strip
club takes its vibe from a real place and not its name, and the same applies
here. Reference the format, the density and the light; name it something else.

## What Zoo already has, and what it does not

Checked against `zoo/zoo_keeper/recipes/`, 2026-09-26.

**Exists and is reusable**: `shelving`, `_shelf_stock` and `_surface_stock`
(stock layout, pure Python and unit-tested), `display_case`, `counter`,
`cash_register`, `vending_machine`, `cigarette_machine` (a floor-standing
machine with "two rows of packs behind the front"), `carton_stack`,
`pallet_stack`, `flat_top_grill`, `aisle_sign`, `poster`, `fluorescent_fixture`,
`sign_box`, `newspaper_box`, `litter_bin`, `condiment_bottle`, `soda_cup`.

**Does not exist**, and each is a species the gap protocol says Zoo grows:

    canopy_fixture     recessed soffit light hardware + the fascia band
    price_pylon        the roadside sign with price digits
    coffee_counter     burner row, glass carafes, condiment rail
    cigarette_overhead the rack above and behind the service counter
    cooler_run         the glass-door reach-in wall facing the sales floor
    impulse_rack       the candy and gum rack at the till

`cigarette_machine` is NOT the cigarette rack. It is a standalone vending
machine; what the reference shows is a lit overhead rack behind the counter,
which is a different object in a different place.

## The light budget, which decides the canopy

`max_lights_per_object` is 8 on GL Compatibility and more than that reaching one
mesh is a shape this repo has already refused. A real canopy has 12-20 recessed
fixtures and every one of them would reach the same forecourt ground mesh -- the
surface that fills the frame when a player stands under it.

So the canopy cannot be a literal fixture grid without measurement. Three
options were put to the walker with the tradeoff stated rather than decided:

* **emissive soffit + 2-4 real lights** -- the fixtures are bright emissive
  panels in the soffit geometry, costing no light and no extra draw call beyond
  the mesh, with a few wide spots doing the pooled illumination on the tarmac;
* **emissive only** -- cheapest, and the forecourt stays dark underfoot;
* **a real fixture grid** -- truest, over the 8-light rule, and unmeasurable
  until it is built.

All three need the same new species. Only the Lux side differs.
