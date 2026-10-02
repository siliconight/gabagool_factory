"""Level Factory 0.126.0: a brief may ask for a video store.

Deli Counter 0.171.0 registers the `video_store` preset; the adapter's copy
of that list has to learn it or a brief is refused at graybox (cold runs
9055 and 9056, the strip club's). `tests/unit/test_dc_preset_registry.py`
failed the moment Deli Counter's registry grew -- "missing here:
['video_store']" -- which is what it is for.

Aliases: a brief is as likely to say `video_rental` or `vhs_store`, and the
keyword fallback only fires when the archetype CONTAINS a preset's name.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

LF = pathlib.Path(__file__).resolve().parents[1] / "level_factory"


def _edit(rel, pairs):
    p = LF / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    b = s.encode("utf-8")
    p.write_bytes(b.replace(b"\n", b"\r\n") if crlf else b)
    print("patched", rel)


ADAPTER = [
    ('''    "strip_club", "suburban_safehouse", "twin", "warehouse",
}''', '''    "strip_club", "suburban_safehouse", "twin", "video_store", "warehouse",
}'''),
    ('''    "comic_shop": "card_shop", "collectibles_shop": "card_shop",
}''', '''    "comic_shop": "card_shop", "collectibles_shop": "card_shop",
    # The video store (Deli Counter 0.171.0). `video_store_*` resolves on
    # the keyword rule; these contain no preset's name and would raise.
    "video_rental": "video_store", "video_rental_store": "video_store",
    "vhs_store": "video_store", "vhs_rental": "video_store",
    "movie_rental": "video_store",
}'''),
]

TEST = [
    ('''def test_this_check_can_actually_find_deli_counter():''', '''def test_the_video_store_preset_resolves():
    """Deli Counter 0.171.0's `video_store`, and the names a brief reaches
    for that contain no preset's name."""
    assert _preset_for("video_store") == "video_store"
    for alias in ("video_rental", "video_rental_store", "vhs_store", "vhs_rental",
                  "movie_rental"):
        assert _preset_for(alias) == "video_store", alias


def test_this_check_can_actually_find_deli_counter():'''),
]


def main():
    _edit("adapters/deli_counter/__init__.py", ADAPTER)
    _edit("tests/unit/test_dc_preset_registry.py", TEST)


if __name__ == "__main__":
    main()
