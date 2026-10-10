## 0.103.0 - a parked box truck wears one of Zoo's four fleets

**Roadmap 219, the walker's note 5:** "i dont know what this giant grey
box is". It was `box_truck`, parked by `site_cover` across a lane as cover.
Zoo 1.92.0 draws it as a 1990s cab-over delivery truck in four invented
Delco fleets, picked by a slot's `variant` (`module_variants: 4`).

**What was missing here.** Lot has carried a cover record's `variant` into
the site's slot, and asked for the variant's module (`_n<v>`) before the
plain one, since 0.90.0, for the dumpster's hauler. It never gave a cover
piece a variant. So every truck on a lot would have been the first fleet.

**Now.**
- `site_cover.COVER_VARIANTS` names how many looks a cover species comes
  in: `box_truck` 4. Every other species has one look and no variant.
- `cover_variant(species, spot)` picks a look from the species and where it
  stands. A lot's trucks differ, and a re-run of one site stands the same
  truck in the same place.
- `Cover.variant` holds it. Both records carry it only when it is not 0, as
  a dumpster's does, so a record written before 0.103.0 reads the same.
- **Order of landing.** A Zoo that cannot draw a variant still builds the
  plain module, and `cover_module_refs` falls back to it. So this release
  and Zoo 1.92.0 need not land in the same instant.

**Tests.** `tests/test_cover_variants.py`:
- a truck has four looks, and nothing else has one;
- a truck keeps its look where it stands, and trucks differ: all four
  appear over a 13 x 9 grid of spots;
- the plan gives its truck the look its spot picks;
- the record carries a look only when it is not the plain one;
- the slot and the module stem ask for the look.

On 0.102.2 four of the five fail: `site_cover` has no `COVER_VARIANTS`.
The fifth walks 0.90.0's road from the record to the slot, and passes on
both.

Suite: 720 passed (715 on 0.102.2).
