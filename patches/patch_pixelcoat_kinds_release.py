"""Pixelcoat 0.59.0: VERSION, the wheel fallback, and the CHANGELOG entry
for `patch_pixelcoat_zoo_kinds.py`.

`pixelcoat/version.py`'s `_FALLBACK` is pinned to VERSION by
`tests/test_version_is_single_sourced.py`. 0.58.0 bumped VERSION and left
`_FALLBACK` at 0.57.0, because its suite ran BEFORE its release patch. This
one bumps both, and the suite runs after.

    python patch_pixelcoat_kinds_release.py
"""
import pathlib

PX = pathlib.Path(__file__).resolve().parent.parent / "pixelcoat"

HEAD = "# Changelog\n\n"
ENTRY = '''## [0.59.0] - the kinds Zoo knows are the kinds Zoo knows

**`cli.main._ZOO_KINDS` is a copy of Zoo's `skins.KNOWN_KINDS`, and it had
drifted.** Measured 2026-10-06, both read as source:
- Zoo knew 38 kinds and this listed 36.
- `wood_panel` and `slatwall`, in Zoo since its 0.95.0 card shop, were
  missing here. So `_warn_unknown_kind` told whoever built those packs they
  would reach no mesh, and they did reach one.
- The test standing guard,
  `test_the_new_kinds_are_not_claimed_as_kinds_zoo_knows`, asserted the two
  were ABSENT, "until Zoo grows them". It never read Zoo, so it went on
  passing after Zoo grew them.

**Now:**
- `_ZOO_KINDS` lists `wood_panel`, `slatwall`, and `chain_link`, the fence
  fabric this repo profiled in 0.56.0. Zoo 1.77.0's `chain_link_fence` wears
  it.
- The guard is a mirror,
  `test_card_shop_surfaces.test_the_kinds_zoo_knows_are_the_kinds_zoo_knows`:
  - it finds a Zoo checkout by walking up from the test;
  - it reads `KNOWN_KINDS` with `ast`;
  - it asserts the two sets are equal, and names what is missing on each
    side;
  - it skips only when no Zoo checkout exists.
- On 0.58.0's list it fails: missing here, `chain_link`, `slatwall`,
  `wood_panel`.

**And 0.58.0's wheel fallback.**
- `pixelcoat/version.py`'s `_FALLBACK` stayed at 0.57.0 when 0.58.0 bumped
  VERSION. `test_version_is_single_sourced` failed on 0.58.0 as committed.
- That suite had run before the release patch, so it never saw the bump.
- `_FALLBACK` is now 0.59.0, beside VERSION, and this release's suite ran
  after both.

**Suite:** 645 passed, run after the version bump.

'''

FALLBACK_OLD = '_FALLBACK = "0.57.0"\n'
FALLBACK_NEW = '_FALLBACK = "0.59.0"\n'


def main():
    assert "SUITE_LINE" not in ENTRY, "fill in SUITE_LINE before applying"
    version = PX / "VERSION"
    changelog = PX / "CHANGELOG.md"
    vpy = PX / "pixelcoat" / "version.py"
    v = version.read_bytes()
    assert v == b"Pixelcoat 0.58.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(HEAD + "## [0.58.0] - "), text[:60]
    vt = vpy.read_bytes()
    assert b"\r\n" not in vt
    vt = vt.decode("utf-8")
    assert vt.count(FALLBACK_OLD) == 1, "the fallback"
    version.write_bytes(b"Pixelcoat 0.59.0")
    vpy.write_bytes(vt.replace(FALLBACK_OLD, FALLBACK_NEW).encode("utf-8"))
    changelog.write_bytes((HEAD + ENTRY + text[len(HEAD):]).encode("utf-8"))
    print("Pixelcoat 0.59.0: VERSION, _FALLBACK and CHANGELOG")


if __name__ == "__main__":
    main()
