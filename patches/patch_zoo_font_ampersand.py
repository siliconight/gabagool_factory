"""Zoo 1.80.0: the neon font copy carries Pixelcoat 0.61.0's `&`.

`neon_forms.FONT_5X7` is a literal copy of Pixelcoat's `signage._FONT`, and
`tests/test_club_species.py::test_the_font_copy_matches_pixelcoat_when_it_is_beside_this_repo`
holds them equal. Pixelcoat 0.61.0 added `&` for Zoo's own door names,
WOODER ICE & HOAGIES and SCRAPPLE & SONS DELI. The copy was not updated, and
the test has failed on every Zoo checkout since (45 glyphs against 44).

    python patch_zoo_font_ampersand.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
NF = ROOT / "zoo" / "zoo_keeper" / "core" / "neon_forms.py"

OLD = '''    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
}
GW, GH = 5, 7
'''
NEW = '''    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    # Pixelcoat 0.61.0's: WOODER ICE & HOAGIES and SCRAPPLE & SONS DELI
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
}
GW, GH = 5, 7
'''


def main():
    data = NF.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "anchor"
    NF.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("patched", NF.relative_to(ROOT))


if __name__ == "__main__":
    main()
