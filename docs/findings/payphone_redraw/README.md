# The payphone, redrawn: a coin phone in three enclosures, one draw (Zoo 1.88.0, roadmap 210)

**Question.** Roadmap 210 is the walker's 1990s payphone, "pay with quarters
... on a metal cord" (2026-10-08). On 2026-10-09, looking at the 1.87.0
frames, the walker noted it "doesn't have a phone or appropriate decals". The
modern low-poly standard's second worked example is a payphone, and its brief
is the target:
- readable instructions and brand;
- a low-sided cable;
- a real coin-return recess;
- 1,500 to 2,500 triangles;
- one opaque material where practical.

What had to be shown:
- that the redraw builds clean at every size and form;
- what it costs;
- how it looks against the old one.

**Frame and units.** Metres, Z up, the caller at -Y. Coincident faces are
read with the coplanar probe's defaults: within 2 mm, overlapping by 1 mm2.

**What was built.** Zoo 1.88.0, `patches/patch_zoo_payphone.py`.
- `core/payphone_forms.py` plans every face as a tile in one atlas, the
  dumpster's way.
- `recipes/payphone.py` builds it with `_card_atlas.build_art`.
- Comps: `docs/reference/PAYPHONE_COMPS.md`, format only. The phone company,
  YOUSETEL, is invented.

## What was there

1.86.0 and 1.87.0's payphone:
- a half-booth of boxes: a post, a back panel, a hood, a face plate, a coin
  box, a handset on a hook;
- 308 triangles, three materials, three draws;
- no keypad, no coin slot, no cord, nothing printed;
- the coincident-face census pinned it at 2 pairs
  (`zoo/tests/test_coincident_faces.py`, `RESIDUE`).

## What it is now

**The instrument,** at its real size, 0.19 x 0.11 x 0.50 m, its foot 1.0 m
up wherever the slot allows. On it:
- twelve keys proud of a printed face, each key's front showing its own
  digit;
- the coin slot in a raised bezel;
- the coin-return recess: a real hole, four walls and a dark back 30 mm in;
- the vault door with its lock;
- the instruction card;
- the hook-switch cradle, with the handset hung in it.

**The cord:** one swept tube of ribbed stainless, from the handset's foot,
looped below the instrument and back into its side. Its rings are turned by
parallel transport, so it does not twist.

**The forms** (`params.form`; `auto` is the booth):

| form | what stands |
|---|---|
| `booth` | a post; back panel, sides and roof; a header reading PHONE and YOUSETEL; a shelf |
| `pedestal` | the shroud on its post; no header, no shelf; the handset glyph stamped on each side |
| `wall` | no post; a line conduit to the ground; a phone book on two rings under the shelf |

**The art,** one image:
- the header;
- the card ("LOCAL CALL 25 CENTS", the three steps, "EMERGENCY 911 NO
  COIN");
- the key legends;
- three stickers in the shop's hand: a bandit sign, a pager's number, CALL
  YA MOM;
- graffiti tags and outdoor wear.

The stickers sit on the back panel's face, cut into a grid, so each samples
its own 800 px/m tile.

## Measured

**Coincident faces: 0, at every form and size.**
- `tests/test_payphone.py`: `prims.coincident_pairs` over 27 sizes and 3
  forms.
- `form_census.py`: the census's own probe on the built meshes, 3 forms at
  the genome's 3 corners, 9 builds. Output `form_census.txt`.
- `tools/coplanar_census.py --species payphone` (the default form only): 0
  at all three corners.
- The payphone leaves `RESIDUE`, whose total goes from 2,997 pairs to 2,995.

**Retracted, kept above the fix: the first Blender census found 6 pairs.**
- **Where:** 1 at the min and the max corner of every form, and 0 at the
  default. Opposite faces 2.0 mm apart, 3.2 to 3.6 cm2.
- **What it was.** The vault lock's inner cap. The lock began 2 mm proud of
  the face, exactly on the probe's window, and float32 decided which side
  of it each size fell. The pure check runs in float64 and missed it.
- **The fix.** The lock starts 4 mm inside the body (the INSET rule).
- **And the suite now checks at 3 mm,** not the probe's 2: the old lock
  fails there, 1 pair at the booth's min corner.

**Every build passes Zoo's validation** (`build_check.py`, output
`build_check.txt`). Each is one object, `Payphone_Art`, and one material:

| | min corner | default slot | max corner |
|---|---|---|---|
| booth | 994 tris | 1,046 tris | 1,046 tris |
| pedestal | 980 | 1,032 | 1,032 |
| wall | 1,046 | 1,098 | 1,098 |

These are the visual triangles. The GLB adds the collision proxy's 48.

**The cost against the old one:**

| | 1.87.0 | 1.88.0, a default booth |
|---|---|---|
| draws | 3 | 1 |
| materials | 3 | 1 |
| triangles | 308 | 1,046 |
| GLB bytes | 21,716 | 76,928 |
| texture | shared skins | one atlas, 256 x 1,243 px, 137,458 bytes |

- **The standard's targets.** The triangles are under its 1,500 to 2,500.
- **The atlas** is about 1.2 times the area of its 512 x 512 target at the
  default slot, and 256 x 868 to 335 x 1,871 over the corners. Zoo's shared
  packer stacks narrow tiles; it was kept as it is rather than bent for one
  species.

## The frames

`render_frames.py`. `tools/preview_specimen.py` renders each species at the
default slot, Cycles, with the tool's own sun, world and camera. A caller's
view is 1.1 m out, eye at 1.6 m, aimed at the instrument.

| frame | what it shows |
|---|---|
| `before_after.png` | 1.87.0's half-booth beside 1.88.0's booth |
| `forms.png` | booth, pedestal and wall |
| `close_before_after.png` | a caller's view of each |

- **In the caller's view, everything reads:** the card, the twelve
  digits, "25 CENTS" by the slot, COIN RETURN over its recess, the vault,
  the stickers, and the cord hanging below the shelf.
- **Retracted, kept: the first pedestal frame.** It stood the handset glyph
  upright, a grip between two cups, and from outside it read as a capital
  I. The glyph is now the one everybody reads, a grip across the top with
  a cup turned down at each end.

## Not settled

- **Which form stands where is Lot's half.** Today Lot stands one payphone
  at each bus stop, with no form, so `auto` makes it a booth.
  - The comps put wall units by store doors and pedestals at corners, on
    city and urban streets.
  - Which themes those are is the walker's call.
- **Indoors.** Deli Counter stands payphones in the airport terminal and
  the funeral home, and `auto` makes those booths too. A wall unit would
  suit a lobby, and asking for it is Deli Counter's change.
- **The graffiti tags** are a looping marker stroke, the shape of a name
  nobody can read. Whether they read as tags is for the walker's eye.
- **The A/B/C review** the standard asks for, with construction and
  materials separated, was not split. The frames compare the old with the
  whole redraw.

## Records beside this README

- **Instruments:** `build_check.py`, `form_census.py`, `render_frames.py`.
- **Outputs, on the real tree after the release:** `build_check.txt` and
  `form_census.txt`.
- **The retracted first census:** `form_census_run1_lock.txt`, the vault
  lock's 6 pairs.
- **The frames:** `before_after.png`, `forms.png` and
  `close_before_after.png`.
- **The retracted pedestal:** `forms_run1_pictogram_I.png`, its upright glyph
  reading as an I.
