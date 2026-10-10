## 0.104.0 - a heap of filled garbage bags beside each dumpster

**Roadmap 219, the walker's note 11:** "need filled black garbage bags
stacked near the garbage bins". Zoo 1.93.0 draws the heap, `trash_bags`: a
row of filled bags on the ground and one or two thrown on top, mostly black,
in four heaps picked by a slot's `variant`.

**Now.** `site_dumpsters.plan_bags` stands one heap beside each dumpster
that `plan_dumpsters` stood.
- **Against the same wall,** `BAG_GAP` 0.1 m off one of the container's
  sides and `BAG_WALL_GAP` 0.15 m off the wall.
- **Turned,** so its width runs out from the wall: a row of bags lining the
  container's side. A full pad runs 0.935 m past each side of its
  container. The heap, 0.8 m deep and 0.1 m off, fits on it with 3.5 cm to
  spare. Face on, 1.4 m wide, it would not fit at all.
- **On its pad where the pad has room.** Of the two sides, one its pad
  covers comes first, and the building's id picks between equals. The record
  says which (`on_pad`), and so does its log line, `LOT_BAGS_PLACED`.
- **Clear of what the dumpster is clear of:**
  - a way in by `DOOR_CLEAR`, any other opening by `WINDOW_CLEAR`;
  - an entry's approach point;
  - the paths, walks and fields, and the road bands;
  - the neighbours, and what stands other than its own dumpster;
  - the markers and the plate's edge.
  It never passes the wall's end.
- **None rather than one in the way.** A dumpster with neither side clear
  is said (`LOT_BAGS_NO_ROOM`) and gets no bags.
- **After the pads,** so a heap stands on a pad rather than shrinking it.
  **Before the parking and the cover planner,** so both see it standing.
- **The slot asks for plastic** (`COVER_MATERIALS["trash_bags"]`), Zoo's one
  option, and for the heap's variant, as a dumpster's slot asks for its
  hauler. `site_furniture.SPECIES` carries the genome's default dims.

**Order of landing: Zoo 1.93.0 first.** A Zoo without the species builds
the slot's box and says so in `species_fallbacks`. That would be a grey box
beside every dumpster, the defect note 5 was about. So
`test_lot_knows_the_species_and_zoo_draws_it` fails when the sibling Zoo has
no `trash_bags` genome.

**Tests.** `tests/test_site_trash_bags.py`:
- the whole road: the dumpster, its pad, and a heap beside it, turned, on
  the pad, toward the wall's middle, with its front away from the
  container;
- the side its pad covers comes first;
- with no pad it still stands, and says it is off one;
- a walk, or what stands, keeps it off a side;
- a door or a window keeps it off a side, and with neither side clear none
  is stood and it is said;
- it never passes the wall's end;
- the same site stands the same bags;
- the slot asks for plastic and the variant, and the module stem carries
  the variant;
- Lot's dims and material are the genome's.

On 0.103.0 all nine fail: the file stops at collection, because
`site_dumpsters` has no `BAG_DIMS`.

**Replayed on cold run 9218's club_block_014 spec** (seed 9181, the
assemble alone): three dumpsters, three heaps, all three on their pads. The site's
slots differ from 0.103.0's by exactly those three, 170 to 173, and nothing
else on the site moved.

Suite: 729 passed (720 on 0.103.0), with Zoo 1.93.0 beside it.
