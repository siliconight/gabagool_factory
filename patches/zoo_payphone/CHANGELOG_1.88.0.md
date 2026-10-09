## [1.88.0] - the payphone, redrawn: a coin phone you can read, on its armoured cord, in three enclosures

### What the walker asked for

- **2026-10-08, roadmap 210:** "In the 90s you would pay with quarters, and
  the phone is not wireless, it's on a metal cord", with three photographs
  read for format only (`docs/reference/PAYPHONE_COMPS.md`).
- **2026-10-09, on 1.87.0's frames:** the payphone "doesn't have a phone or
  appropriate decals".
- **The modern low-poly standard's second worked example** is a payphone. Its
  brief: readable text, a low-sided cable, a real coin-return recess, 1,500 to
  2,500 triangles, and one opaque material where practical.

### What was there

A half-booth of boxes: 308 triangles, three materials and three draws. No
keypad, no coin slot, no cord, nothing printed. The coincident-face census
pinned it at 2 pairs.

### What it is now

`core/payphone_forms.py` plans it in pure Python, the dumpster's way: every
face is a prim naming a tile in one atlas. `recipes/payphone.py` builds it
with `_card_atlas.build_art`. **One object, one material, one draw.**

**The instrument,** at its real size, 0.19 x 0.11 x 0.50 m, its foot 1.0 m
up wherever the slot allows. On it:
- twelve keys proud of a printed face, each key's front showing its own
  digit;
- the coin slot in a raised bezel;
- the coin-return recess: a real hole, four walls and a dark back 30 mm in;
- the vault door with its lock;
- the instruction card;
- the hook-switch cradle, with the handset hung in it.

**The cord:** `payphone_forms.tube`, one swept tube with its rings turned by
parallel transport, so it does not twist. Ribbed stainless, from the
handset's foot, looped below the instrument and back into its side.

**The forms,** `params.form` (`auto` is the booth):
- **booth:** a post; back panel, sides and roof; a header reading PHONE and
  YOUSETEL; a shelf.
- **pedestal:** the shroud on its post; no header, no shelf; the handset glyph
  stamped on each side.
- **wall:** no post; a line conduit to the ground; a phone book on two rings
  under the shelf.

**The art:**
- the header and the card;
- the key legends;
- three stickers in the shop's hand: a bandit sign, a pager's number, CALL YA
  MOM;
- graffiti tags and outdoor wear.

YOUSETEL ("YOUSE TALK. WE TOLL.") is invented. Its line rides only a header
0.66 m or wider, measured to set there; a narrower header carries the name
alone, by the plan's word, not by a dropped line. The stickers sit on the back
panel's face, cut into a grid, so each samples its own 800 px/m tile. A
sticker that does not fit is left off by the plan: the narrowest booth keeps
one of three.

### Measured (`docs/findings/payphone_redraw/`)

**Coincident faces: 0, at every form and size.** In pure Python (27 sizes, 3
forms), and in Blender with the census's own probe (3 forms at 3 corners).
- **The first Blender census found 6 pairs:** the vault lock's inner cap, 2.0
  mm in front of the face. That is on the probe's window, and float32 decided
  which side each size fell.
- **The fix.** The lock now starts inside the body.
- **The suite checks at 3 mm,** where the old lock fails.
- **The payphone leaves `test_coincident_faces.RESIDUE`:** 2,997 pairs to
  2,995.

**Triangles:** 980 to 1,098 over the forms and corners; 1,046 as a booth at
the default slot. Before: 308.

**The cost of a default booth:** 1 draw (3 before). 76,928 bytes of GLB and a
137,458-byte atlas of 256 x 1,243 px; the old GLB was 21,716 bytes.
- **Against the standard:** the triangles are under its range. The atlas is
  about 1.2 times its 512 x 512 area. Zoo's shared packer stacks narrow tiles
  and was not bent for one species.

**Every build passes validation:** 9 builds, 3 forms at 3 corners.

### Tests

`tests/test_payphone.py`, 22, 3 of them Blender-gated:
- every form fills its slot with no shared plane at 27 sizes;
- the check sees a shared plane;
- every flat face points out;
- one atlas, one material;
- every line of every tile sets, in every form at every size;
- the company's line rides only a header wide enough;
- the names are invented: the factory's denylists, the 1990s telephone
  companies and payphone makers, and the fictional 555-01xx exchange;
- the shroud is painted the genome's colour, and the recipe passes it in;
- the coin return is a real recess;
- twelve keys each show their own legend;
- the cord runs from the handset into the instrument, clear of the shelf and
  inside the slot;
- the narrowest booth keeps the one sticker that fits;
- the instrument stands at a caller's height.

On 1.87.0 the file fails at its import.

`tests/test_coincident_faces.py`: the payphone's `RESIDUE` row is gone, its
total is 2,995, and the xfail reads its species count off the table.

`tests/test_recipe_reads_its_genome.py` now skips the payphone ("builds no
materials"): an atlas recipe makes no material for it to read. The colour
test above takes its place.

**Suite:** 4,045 passed (4,027 + 19 - 1), 398 skipped, 1 xfailed, `python -m
pytest -q`. The -1 is that genome test; the skips are +3 Blender-gated, +1
that genome test, and -1 the payphone's residue case.

