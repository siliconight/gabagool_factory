"""Zoo 1.77.0: VERSION and the CHANGELOG entry for the `chain_link_fence`
species and the `chain_link` kind (branch `fence_species`, cherry-picked).

    python patch_zoo_fence_release.py
"""
import pathlib

ZOO = pathlib.Path(__file__).resolve().parent.parent / "zoo"

ENTRY = '''## [1.77.0] - a chain-link fence

**The walker, 2026-10-04,** on the fenced vacant lot in
`docs/findings/backdrop_mock/` at the factory root: "I like the idea of a
fence between playable areas and non playable areas, thats good feedback to
the player". Pixelcoat 0.56.0 made the fabric, and this release makes the
fence. Lot 0.97.0 stands it.

**`chain_link_fence`**, a run of commercial chain-link fence
(`core.chain_link_fence_forms` is the plan; ASTM F1043 framework):
- **Line posts** no more than 10 ft (3.05 m) apart, 1-7/8 in OD.
- **Terminal posts** at each end, 2-3/8 in OD. A terminal's outer face is the
  run's end and its top is the run's top.
- **A top rail**, 1-5/8 in OD, carried by the line posts' loop caps.
- **The fabric**, hung 2 in above grade and tied to the rail, with a tension
  wire along its bottom edge. The wire is drawn at twice its 4.5 mm, as the
  antenna's tubes are.
- Width is the run's length, 1 to 120 m. Depth is exactly a terminal post's
  diameter. Height is the fabric's, 4 to 8 ft; 6 ft is the default.

**Two submissions, whatever the length:**
- **The steel**: posts, rail and wire, one mesh in `metal_bare`, galvanised
  grey.
- **The fabric**: one card the run's length in `chain_link`, Pixelcoat's
  alpha-cut tile, read from both sides. On the flat path, with no skin
  library, it is a grey panel: the greybox reading of a fence, which is a
  wall.

**Collision** is the slot's box: a wall nobody walks through and everybody
sees through.

**`chain_link` joins the kind vocabulary** (`skins.KNOWN_KINDS`,
`materials.ROUGHNESS` at 0.28 and `METALLIC` at 0.90, like `metal_bare`).

**Seen.** `tools/preview_specimen.py` built the default run against cold run
9181's Pixelcoat library:
- 196 triangles, status PASS.
- Both packs resolved: `metal_bare_delco_1997` tinted, and
  `chain_link_delco_1997`.
- At a standing eye height of 1.6 m and 3 m away, the frame shows the
  diamonds, the pack's rust at the knuckles, a round line post, the rail and
  the wire.

**The census caught the first cut** (`tools/coplanar_census.py`, the three
genome corners). Each build had three coincident pairs, all the tension wire
against the fabric card:
- the wire's flat underside 0.6 mm above the card's, along the whole run
  (357 cm2 at 9 m);
- its two end caps flush with the card's two ends.

The wire now runs ON the fabric's bottom edge, woven through it as a real one
is, and ends a quarter of a terminal post inside each terminal. The census
reads 3 builds and 0 with coincident pairs (132, 196 and 1,380 triangles).
`CENSUS_BUILDS` is 357.

**`BARE`** (`test_material_options_closed`) lists the fence, because its
steel is galvanised.

**Tests** (`tests/test_chain_link_fence.py`), 16:
- the species is discovered, validates, and plans at its dims;
- no span is longer than 10 ft and the ends are terminals, at seven
  widths from 1 to 120 m;
- the fewest posts that keep the spans short;
- the fabric hangs from the rail to just above grade, at three
  heights, with the wire on its edge;
- the wire ends inside the terminals;
- the fabric stays inside the slot;
- `chain_link` is a kind the skin library resolves.

The file cannot be collected on 1.76.0.

**Suite:** 3,338 passed, 382 skipped, 1 xfailed. That is 1.76.0's
3,316, these 16, and 6 the genome-wide sweeps run on the new species.

'''


def main():
    for token in ("TESTS_LINE", "SUITE_LINE"):
        assert token not in ENTRY, f"fill in {token} before applying"
    version = ZOO / "VERSION"
    changelog = ZOO / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"1.76.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [1.76.0] - "), c[:60]
    version.write_bytes(b"1.77.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Zoo 1.77.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
