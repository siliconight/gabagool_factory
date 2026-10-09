## [1.89.0] - the payphone lit: a backlit header, a hood lamp's diffuser, and the lamp's marker

### What the walker asked for

- **Cold run 9212** stood 1.88.0's booth at a bus stop, and at midnight it
  read as a silhouette: its roof shaded the instrument, and no light reached
  the card, the keys or the stickers.
- **The proposal:** a backlit header and a hood lamp, at one more draw a
  payphone. **The walker, 2026-10-09:** "yes light it".

### What it is now

**Two atlases, two draws.** The paint atlas is 1.88.0's. The second is LIT,
built by `_card_atlas.build_art(lit=(GLOW_EMISSION, GLOW_ALBEDO))`, the
ATM's way, so its material is `_Face` and Lux's power cut takes it. On it:
- **the header's face** (the booth and the wall unit): PHONE and YOUSETEL
  glow;
- **the diffuser:** a box hung 14 mm under the roof, its top 4 mm into it,
  0.07 m deep, across the booth between the side panels, 30 mm in from each.
  Its face is a lit tube behind a ribbed panel, and its rim is painted.

**Where the diffuser hangs: just behind the header,** 10 mm off its back
face. A pedestal has no header, so it hangs just behind the roof's front
edge. A real booth's tube sits there, backlighting the sign and lighting the
instrument below it.

**This was measured, not chosen** (`docs/findings/payphone_light/`). A lamp
was stood live in cold run 9212's package, at the default slot:

| where the lamp hangs | the card, per unit of energy | the back panel's top |
|---|---|---|
| mid-hood | 0.27 | 11.4 |
| behind the header | 0.42 | 5.9 |

So behind the header the hot spot halves, and the card takes half again.

**The lamp's marker,** `LuxEmit_payphone_hood`:
- it hangs 30 mm under the diffuser's face, in free air: a lamp inside closed
  hardware bakes to nothing (Lux 0.65.0's pole, 0.67.0's bulbs);
- it carries `lux_type` (`payphone_hood`) and `lux_drop`, its height above
  the ground, 2.211 m at the default slot. Lux's `payphone_hood` row
  (Lux 0.70.0) solves the lamp's range and energy from it.
- **How the payload rides.** A recipe may now return `marker_props` beside
  `attachments`. `bpylayer.markers.add_marker(..., props=)` sets them as the
  empty's custom properties, and the glTF export (`export_extras=True`)
  writes them as the node's extras. That is where
  `LuxFixtureSpawner.marker_payload` reads them, as it does the fixture
  pass's.
- Both of `bpylayer.build`'s call sites pass them. A recipe that returns
  none builds as before.

### Measured

**Every build passes Zoo's validation** (`docs/findings/payphone_light/
build_check.py`, output `build_check.txt`). It builds each form at the
genome's min corner, the default slot and its max corner, and reads every
one back: two objects, two materials (the lit one `_Face`), and the marker
with its payload.

| at the default slot | paint tris | lit tris | GLB bytes (1.88.0) | atlases, px |
|---|---|---|---|---|
| booth | 1,052 | 4 | 79,620 (76,928) | 256 x 1,182 and 289 x 121 |
| pedestal | 1,040 | 2 | 78,296 (75,612) | 256 x 1,362 and 289 x 60 |
| wall | 1,104 | 4 | 83,504 (80,816) | 256 x 1,326 and 289 x 121 |

- **The paint atlas shrank** when the header's tile left it: the booth's
  256 x 1,243 is now 256 x 1,182.
- **The marker, read back from the GLB** at the default slot: glTF
  (0, 1.061, 0.177), `lux_drop` 2.211. At the min corner `lux_drop` is
  1.521, and at the max 3.131.
- **Coincident faces: 0** over the 9 builds, 990 to 1,108 visual triangles,
  by 1.88.0's census (`docs/findings/payphone_redraw/form_census.py`, output
  `docs/findings/payphone_light/form_census.txt`).

### Tests

`tests/test_payphone.py`:
- **two atlases:** the lit one holds exactly the header's face and the
  diffuser's, and the pedestal only the diffuser's;
- **the lamp in free air,** at all 27 sizes and 3 forms: under its
  diffuser, behind the header, in front of the instrument and above it, and
  inside no part;
- **its payload;**
- **the recipe hands it on,** and both build call sites pass it;
- **the built GLB** (Blender-gated): two objects, two materials, one
  `_Face`, the marker with its extras, re-centred with the geometry.

On 1.88.0 four fail:
- the genome's parts;
- the lit atlas, `{paint}` where `{paint, glow}` is asked;
- the lamp, `KeyError: 'lens'`;
- the recipe's hand-off.

**The suites:**
- **Zoo:** 4,047 passed, 398 skipped, 1 xfailed. 1.88.0's figures were
  4,045, 398 and 1; the difference is the two new pure tests.
- **Under Blender:** 79 passed. That is the payphone's 24, with the roller
  grill's and the ATM's; the grill is the other recipe whose marker goes
  through `add_marker`.

### Endings

`core/payphone_forms.py` and `tests/test_payphone.py` were CRLF in the
working tree and LF in git's index: 1.88.0's patch copied them from CRLF
sources. They are LF now, the index's form.
