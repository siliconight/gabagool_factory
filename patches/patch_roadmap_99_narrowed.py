"""Roadmap 99 NARROWED, re-measured 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces 99's status block
(asserted once, from its first line to the line ending the block's `*`). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_99_narrowed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-09-05 -- MEASURED, NOT FIXED. NINE PIXELCOAT PROFILES,\nFOUR ZOO STYLES"
HEADING = "\n\n**99. A theme has to exist in two repos, and only two do.**"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- the ceiling moved from two themes to four, re-measured "
    "(`docs/findings/open_items_remeasure/`). Pixelcoat carries 13 profiles, `center_city` and `industrial_flats` "
    "among them -- the cheapest of the three moves this item named -- so the themes that exist on both sides are "
    "rockay (128 of 133 species), center_city (126), industrial_flats (126) and delco (119). The shared vocabulary "
    "exists as a rule: `packages/tools/themes.zoo_style_for` resolves a brief's theme to a Zoo style by name and "
    "then by the name minus its trailing qualifier (`delco_1997` -> `delco`, Zoo 0.57.0's fallback), which is "
    "why every level builds under a theme Zoo's list does not carry. Left: the doctor still prints both lists and "
    "the partial styles rather than the intersection, and the briefs still ask for one theme -- 298 of 301 "
    "cold-run briefs on disk say `delco_1997`, 3 say `delco`, and none has asked for the two that became askable.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "99's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "99's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 99 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
