"""Zoo 1.81.0: VERSION and CHANGELOG for the deli case.

    python patch_zoo_181_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

ENTRY = '''## [1.81.0] - the deli case: curved glass, a lit deck, the logs cut to the customer

### The one piece that says what the building is, built as a box

Deli Counter's corner deli has always stood a `deli_case_cover` in front of
its deli counter. No species answered to the name, so it built as a plain
box wearing glass. In cold run 9189's composed deli_a01 it was
`prop_delco_1997_03_w700_d110_h130_mglass`, a 7 m slab, in every deli in
every level. The walker's store references put "a hoagie/deli counter
further back" in the 1990s store; the corner deli is that counter as a
whole business.

### `deli_case`, a species of its own

The brief, by the authorship guide's three questions:
- **What it is for.** The family behind it slices to order and the case
  shows what there is. Whole logs lie on their sides with the cut end to the
  glass, so a customer can tell the provolone from the ham. Salads sit in
  steel pans in front, each with a white card and its price.
- **Who touches it.** Customers lean on the steel bumper and point through
  the glass. The staff reach in through the doors behind and wrap on the
  stainless top.
- **What it is made of.** A white enamel base with one accent band, a black
  kick, curved front glass in three facets, glass end panes, a fluorescent
  tube under the top's front edge, and the plastic parsley a deli lines its
  pans with.

**Planned in pure Python** (`core/deli_case_forms.py`), built by
`recipes/deli_case.py`, which carries no geometry of its own.
- **The deck** is one closed mesh, cut a bay at a time (`BAY`, 1.2 m). Each
  bay's top maps its own painted tile, to `TILES_MAX` (6): cards, parsley,
  sixth pans of eight salads, trays of sliced meat.
- **The pieces on the deck's back half** are six logs (provolone, genoa,
  capicola, ham, turkey, roast beef) and two blocks (American, swiss). Each
  cut face carries a painted cross-section and faces the glass.
- **The variant** chooses the accent band (deli red, walnut, Kelly green,
  navy) and the order of the pieces.

**Three submissions whatever the length**, the cooler wall's:
- painted metal, with each part's colour in the `Wear` vertex colour;
- the glass, see-through at 0.20;
- the glow: the deck, the tube and every piece on ONE backlit image,
  `M_DeliCase_<art>_Face`, which Lux's power cut takes. Its emission starts
  at 0.7, under the cooler's 1.0, because it is product under a tube rather
  than a backlit panel. To be judged on the walk.

**No word on the case but a price.** The cold cuts and salads are generic
names, in code only.

### Built

At Deli Counter's slot (5.815 x 1.1 x 1.3, the case as Deli Counter 0.199.0
trims it off its wall):
- Validation passes.
- 1,412 triangles against a budget of 2,400. The largest case in the genome
  (8.0 m) plans 1,872.
- One image: 361,596 bytes, 118,896 once written beside the GLB.
- `tools/coplanar_probe.py --species deli_case`: 0 coincident pairs.

**Four sets of shared planes were found on the way, each moved by 4 mm or
more:**
- the end panes against the glass and the rear rail;
- the rail's ends against the base's;
- the deck's bays, which met face to face until the deck became one mesh;
- the logs' flat bottom facets, 1.6-2.1 mm under the deck's top until they
  were sunk `LOG_SINK`.

### Tests

**`tests/test_deli_case.py`: 37 pure, 4 built.** The 4 built tests passed
inside Blender 5.1. None of them can be collected on 1.80.0, where the
module does not exist. They cover:
- the slot filled exactly with no shared plane, at both of Deli Counter's
  sizes and the genome's eight corners;
- the deck cut a bay at a time;
- the pieces behind the glass and under the top, each cut face looking at
  the customer;
- the glow mapping, deterministic art, and every price set;
- the variant, the genome and the recipe read as source;
- built: PASS and fit, three submissions with one lit material and the glass
  blended, and the same file every build.

**The species is registered** in:
- `test_genome.py`;
- `test_material_options_closed.py`, as painted;
- `test_theme_style_resolution.py`, whose count goes from 92 to 93;
- `test_coincident_faces.py`, whose census goes from 357 builds to 360
  after `tools/coplanar_census.py --species deli_case` ran in Blender 5.1.1:
  "3 builds, 0 with coincident pairs, 0 that did not build" (416 / 1,412 /
  1,872 tris). The first full suite failed on exactly that line, before the
  census was run.

**Unproven until it stands in a level.** Deli Counter must route
`deli_case_cover` to the species, and a cold run must show it.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = ZOO / "VERSION"
    assert v.read_bytes().strip() == b"1.80.0", v.read_bytes()
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [1.80.0] - the flat-top grill fits its slot"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(v.read_bytes().replace(b"1.80.0", b"1.81.0"))
    print("Zoo 1.81.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
