## 0.123.0 - an urban street plants a city block's trees: one every 30 ft

**Factory roadmap 241, the urban street.** The comps show "street trees in pits along both sidewalks". Lot already
planted a tree in a grate on both sidewalks, but halfway between lamps 25 m apart (`TREE_OFFSET`). That is a
Delco strip's spacing: cold run 9292's 173 m through road stood five trees on one kerb and six on the other.

- **Read at source** (the factory root's `docs/reference/STREET_TREES.md`). Philadelphia's own siting guidelines,
  PHS / TreeVitalize's "Property Owner Request to Plant a Street Tree in Philadelphia" (2010), set:
  - 15 to 30 ft between trees, by mature size;
  - 30 ft from a street corner;
  - 15 ft from a pole or a hydrant;
  - 5 ft from a drain;
  - none in front of a doorway.
- **`site_furniture.urban_tree_stations(road, kerb)`.**
  - Each band is split at its road crossings, and each run kept `URBAN_TREE_CORNER` (30 ft, 9.144 m) clear of a
    crossing's dropped kerb and `LAMP_START` of the road's ends.
  - Each run is planted every `URBAN_TREE_SPACING` (30 ft, 9.144 m), its row centred, so a block's trees stand
    evenly from corner to corner.
  - The five species Lot plants are shade trees, so the range's upper end.
- **`plan_furniture(..., urban=False)`** plants by those stations when ``urban``. Each tree still steps clear of
  every cut, piece, marker and shop band, as before. A strip plants the lamps' stations exactly as it did.
- **`assemble` asks** `site_spec["streetscape"] == "urban"`, which Level Factory 0.205.0 writes for an urban
  brief. A spec without the key is a strip.
- **Carried, a message:** `LOT_DESTINATION_ABOVE_FLOOR` ended "Laser Tag cannot path to it either way and
  reports TRAVERSAL with 0% completion". The factory's roadmap 245 census refuted that: the walk test walked to
  the objective on 95 of the 96 candidates carrying the finding. It now says Lot cannot tell offline which, and
  that the walk test answers it.
- **Not enforced, written down** in `STREET_TREES.md`:
  - The 15 ft from a pole: the pole line is planned after the trees and steps clear of each crown.
  - A door path's hydrant, which a dense row may leave no room for.
  - Curb side: the form plants between the curb and the sidewalk, and Lot keeps the band's outer half.
- **The result:** on the test street (`tests/test_urban_street_trees.py`'s block: a 180 m through road and two side streets), trees 20 -> 49, the through road's 12 -> 33, and every other piece as the strip stands it -- 12 poles, 2 hydrants, 3 bus shelters, 60 meters and the rest; a real urban level's are the factory's cold run 9294's
- **Strip levels:** the picked `lot_assemble` jobs of cold runs 9278 to 9287 replayed on 0.122.0 and on 0.123.0 (the factory's `docs/findings/urban_street/lot_replay.py`): 10 jobs, 420 files, 0 differ -- none of their specs says urban
- **`tests/test_urban_street_trees.py`** has 4 checks. All 4 fail on 0.122.0. The suite: `python -m pytest -q`: 844 passed (0.122.0's 840 and the 4 here).
