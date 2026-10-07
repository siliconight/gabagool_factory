"""Lux 0.68.2's release: VERSION and the CHANGELOG entry.

    python patch_lux_0682_release.py

Anchored on VERSION (b'Lux 0.68.1', no newline) and on CHANGELOG.md's head
as Lux 0.68.1 left it (LF).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LUX = ROOT / "lux"

HEAD = "# Changelog\n\n## [0.68.1]"
ENTRY = """# Changelog

## [0.68.2] - a den of sin is a building, not a room

The walker, 2026-10-07: "the 'dens of sin' buildings that we can keep a bit
dark".

**0.68.0's fill skipped only a TINTED probe** -- a strip club's floor -- and
filled every other room in the same building. On club_block_014 at night
(Delco Night), re-baked through Level Factory 0.151.0 with 0.68.1 vendored,
strip_club_a02's back rooms became the brightest room in the level.

**A building with any tinted probe now keeps every room unfilled**
(`_probe_building`). Which building a probe stands in is Lot's contract:
`merge_lights` ids every anchor `<building>/<id>` (lot.py), and Lux names a
room probe after its anchor's room with "/" made "_". So
`b0_back_rooms_ambient` is building b0, in every package read, single
buildings included. A probe whose name carries no building stands alone:
only its own tint counts, which is 0.68.1's rule.

Mean luma of 255 a room, club_block_014 at night:

    room                               shipped   0.68.1   0.68.2
    strip_club_a02  main floor            2.8       2.8      2.8
                    back rooms           19.5      52.3     19.5
                    cellar hall           1.2       8.7      1.2
                    count room            1.0       7.0      1.0
    bank_tower_a02  teller band           9.7      40.0     40.0
                    upper ring           10.6      46.7     46.7
    freight_terminal_a01 cross dock       1.1      11.1     11.1
    fills laid                             --       171      135

The club is back to the dark it was built with, room for room. Its two
neighbours keep their floor unchanged.

`tools/bake_fill_selftest.gd` adds a club building whose back room keeps no
fill and an ordinary one beside it that keeps its own. The prefix-less
probes are the control that a probe naming no building stands alone. On
0.68.1 it fails 1: the club's back room took 2 fills.

## [0.68.1]"""


def main():
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.68.1", repr(v)
    c = (LUX / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.count(HEAD) == 1, text.count(HEAD)
    (LUX / "VERSION").write_bytes(b"Lux 0.68.2")
    (LUX / "CHANGELOG.md").write_bytes(text.replace(HEAD, ENTRY, 1).encode("utf-8"))
    print("Lux 0.68.2: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
