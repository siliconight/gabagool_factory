"""Pixelcoat 0.60.0: VERSION, the wheel fallback, and the CHANGELOG entry for
`patch_pixelcoat_brand_and_fabric.py`.

    python patch_pixelcoat_brand_release.py
"""
import pathlib

PX = pathlib.Path(__file__).resolve().parent.parent / "pixelcoat"

HEAD = "# Changelog\n\n"
ENTRY = '''## [0.60.0] - FLAPPAHS is cream on green, and the chain-link fabric blends

**FLAPPAHS is cream on green.** The walker, 2026-10-06, choosing between
the band's cream on red and the pylon's cream on green: "We can do the green
and cream".
- Zoo draws the pylon, the pumps and the door box in
  `price_pylon_forms.COLOURWAYS[0]`.
- The band now draws in the same three colours, in both level themes: panel
  `#184e34`, border `#e2ce96`, text `#f6eed6`.
- `tests/test_flappahs_signs.py::test_the_brand_is_cream_on_green_as_zoo_draws_it`
  reads Zoo's tuple as source, so the band and the pylon cannot drift apart.
- `marks/flappahs_green.svg` is the goose mark with its five red fills and
  the swoosh's red stroke in the brand green. `flappahs_red.svg` stays, as
  the art the brand was named with (2026-09-26). Nothing renders a mark; it
  is reference art.

**The chain-link fabric blends its texture** (`chain_link_galvanized`:
`transparency.alpha_mode` is now `blend_texture`, which Zoo 1.78.0 honours).
- Tested at 0.5, the fabric vanished at distance (cold run 9183, roadmap
  188). It is about a quarter wire, so its smaller mips fall under the
  cutoff.
- Rendered on cold run 9184's walk copy against three other fixes, from an
  alley 20 m away and along a 16.8 m run:
  - cut at 0.2: the far fabric turns into a solid dark wall;
  - alpha hash: the whole run goes solid dark under GL Compatibility;
  - a second, distant card: the run's far end still goes bare, because a
    visibility range switches a whole node;
  - blended: the same crisp wire near, and a faint screen far.
- The cutout alpha itself is unchanged.

**Tests:**
- `test_chain_link.py::test_the_fabric_is_a_cutout_that_blends_mostly_open`
  (renamed from the scissor test).
- The FLAPPAHS mirror, one per level theme.
- All three fail on 0.59.0's profiles.

**Suite:** 647 passed (0.59.0's 645 and the two mirrors), run after the
version bump.

'''

FALLBACK_OLD = '_FALLBACK = "0.59.0"\n'
FALLBACK_NEW = '_FALLBACK = "0.60.0"\n'


def main():
    version = PX / "VERSION"
    changelog = PX / "CHANGELOG.md"
    vpy = PX / "pixelcoat" / "version.py"
    v = version.read_bytes()
    assert v == b"Pixelcoat 0.59.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(HEAD + "## [0.59.0] - "), text[:60]
    vt = vpy.read_bytes().decode("utf-8")
    assert vt.count(FALLBACK_OLD) == 1, "the fallback"
    version.write_bytes(b"Pixelcoat 0.60.0")
    vpy.write_bytes(vt.replace(FALLBACK_OLD, FALLBACK_NEW).encode("utf-8"))
    changelog.write_bytes((HEAD + ENTRY + text[len(HEAD):]).encode("utf-8"))
    print("Pixelcoat 0.60.0: VERSION, _FALLBACK and CHANGELOG")


if __name__ == "__main__":
    main()
