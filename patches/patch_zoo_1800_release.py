"""Zoo 1.80.0: VERSION and CHANGELOG for `patch_zoo_grill_fits_its_slot.py`
and `patch_zoo_font_ampersand.py`.

    python patch_zoo_1800_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

ENTRY = '''## [1.80.0] - the flat-top grill fits its slot, and the neon font has Pixelcoat's ampersand

### The grill measured 35 mm deeper than its slot

**Cold runs 9132, 9179 and 9185** each logged `ZOO_PARTIAL_BUILD` for one
module: `prop_flat_top_grill_delco_1997_04_w120_d90_h105_mmetal`.
- `fit_depth` measured 0.935 m against an exact 0.900 m. Every other check
  passed.
- The resolver fell back to base: a grey stand-in in every deli kitchen that
  draws the grill, deli_a01's included.

**The recipe built the cabinet at the full slot depth** and hung the knobs off
its front: 0.03 m cylinders centred 0.02 m before the face, standing 0.035 m
proud. 0.900 + 0.035 = 0.935, exactly what was measured.

**`core/flat_top_grill_forms.py`** is the grill in numbers, with no bpy, as
the fence's and the roller grill's forms are.
- The cabinet and everything on it stand `KNOB_PROUD` shallower than the slot
  and set back by half of it, so the knobs end on the slot's front face.
- The module's extents are exactly (width, depth, height) at any genome
  dimension.
- `recipes/flat_top_grill.py` draws the parts the layout returns and carries
  no geometry of its own.

**Built** (`zoo_cli --species flat_top_grill`): validation pass. The plan
asked for depth 0.9078 and the module measures 0.908. Before this release it
would have measured 0.943.

### The neon font copy carries `&`

`neon_forms.FONT_5X7` is a literal copy of Pixelcoat's `signage._FONT`.
Pixelcoat 0.61.0 added `&` for Zoo's own door names, WOODER ICE & HOAGIES and
SCRAPPLE & SONS DELI. The copy was not updated, and
`test_the_font_copy_matches_pixelcoat_when_it_is_beside_this_repo` failed on
every checkout since, 45 glyphs against 44. The copy now carries the same
rows.

### Tests

**`tests/test_flat_top_grill_forms.py`, 3:**
- the extents are exactly the slot, at four sizes and two to four knobs;
- the knobs end on the front face;
- the recipe builds from the layout (read as source).

All three fail on 1.79.0, where the module does not exist.

**Suite:** 3,346 passed, 382 skipped, 1 xfailed. That is 1.79.0's 3,343, these
3, and the font mirror passing again.

'''


def main():
    v = ZOO / "VERSION"
    assert v.read_bytes() == b"1.79.0", v.read_bytes()
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [1.79.0] - a door box can wear"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"1.80.0")
    print("Zoo 1.80.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
