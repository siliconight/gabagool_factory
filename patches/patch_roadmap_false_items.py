"""Roadmap: three body lines written 2026-10-10 parsed as items 1 and 2; reword them.

`tools/roadmap_status.py` reads any line that starts `**<digits>. ` as an item heading
(`_ITEM`). Three step lines written into items 224 and 225 that night started that way, so the
generated index carried a second item 1 (twice) and a second item 2, and the count line read 229
items for 226. Each is reworded so it no longer starts with a number; the words are unchanged.
Each anchor must match exactly once; nothing is written on a miss.

    python patches/patch_roadmap_false_items.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

REWORDS = [
    ("**1. MEASURED 2026-10-10: the quality does not move them** ",
     "**Step 1, MEASURED 2026-10-10: the quality does not move them** "),
    ("**1. DONE, Level Factory 0.172.0** ",
     "**Step 1 DONE, Level Factory 0.172.0** "),
    ("**2. ANSWERED, read off 9222's package:** ",
     "**Step 2 ANSWERED, read off 9222's package:** "),
]


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for old, new in REWORDS:
        n = text.count("\n" + old)
        assert n == 1, (old, "matches at a line start", n, "times")
        text = text.replace("\n" + old, "\n" + new)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap: 3 step lines reworded so they no longer parse as items")


if __name__ == "__main__":
    main()
