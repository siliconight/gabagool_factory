"""Pixelcoat 0.61.0, second half: Zoo's names render, and legibility is
measured, not counted.

Running the suite after `patch_pixelcoat_one_name_list.py` failed two
theme-sign tests, each on a real constraint the new names met:

  * `test_every_sign_renders_with_the_built_in_font`: the bitmap fallback has
    no `&`, and WOODER ICE & HOAGIES and SCRAPPLE & SONS DELI need one (the
    TTF has it; the fallback is what renders when the TTF cannot be found,
    and a missing glyph renders as a silent space). `&` joins `_FONT`.
  * `test_the_theme_names_a_street_of_businesses`: a name was capped at 20
    characters, and DOWN THE SHORE BREWING is 22.
    - The cap stood in for legibility. Measured with `fit_scale` on the
      band's 128 x 512 canvas: the brewery fits at scale 5, the same scale
      SCRAPPLE SUPERMARKET (20) always passed at; 20-character names land at
      5 to 7.
    - The test now asserts the scale -- at least 5 -- instead of the count.

    python patch_pixelcoat_one_list_fit.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PX = ROOT / "pixelcoat"

EDITS = {
    PX / "pixelcoat/core/signage.py": [
        ('''    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
}
''',
         '''    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    # 0.61.0: WOODER ICE & HOAGIES and SCRAPPLE & SONS DELI, Zoo's door names
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
}
'''),
    ],
    PX / "tests/test_theme_signs.py": [
        ('''        assert s["text"] == s["text"].upper()
        assert len(s["text"]) <= 20, s["text"]
''',
         '''        assert s["text"] == s["text"].upper()
        # LEGIBLE, MEASURED (0.61.0). This was `len(text) <= 20`, a count
        # standing in for legibility; DOWN THE SHORE BREWING (22, Zoo's door
        # list) fits the band's 128 x 512 canvas at scale 5, the scale
        # SCRAPPLE SUPERMARKET (20) always passed at.
        assert sgn.fit_scale(s["text"], (128, 512)) >= 5, s["text"]
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
