"""Roadmap 250, 2026-10-14 19:30: the walk's finding 5 traced -- the deli family's basement partition stops 7 m short
of the outside wall at both ends, authored so since Deli Counter 0.80.0 (`docs/findings/walk_2026-10-14/README.md`,
`partition_gaps.py`).

- 250's status: finding 5 named as traced.
- 250's Left: 5's trace and what fixes it, in place of "not yet traced".

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_250_basement.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S_OLD = "Open: 5, the deli's basement partitions' openings; 6,"
S_NEW = ("Open: 5, traced -- the deli family's basement partition stops 7 m short of the outside wall at both ends, "
         "the vault open to the utility room; 6,")
L_OLD = "**Left:** 5, not yet traced; 6,"
L_NEW = (
    "**Left:** 5, traced (`docs/findings/walk_2026-10-14/`, `partition_gaps.py`): every deli's wall along X at y 1.0 "
    "divides rooms that meet across the basement's full 38 m, x -19..19, and is built -12..12 -- 7.00 m open at each "
    "end, `basement_corridor` into `cold_storage` and `utility_room` into `basement_vault`, the objective room "
    "marked `fortifiable`, beside the 1.4 m `vault_side_breach` meant to be its way in. Authored so in Deli Counter "
    "0.80.0 (f54ebfee), whose other basement partition overshot and was clamped by 0.83.3; nothing extended this "
    "one. The census: 59 open stretches over 1 m in 31 of 446 specs, the delis' among them, others reading as "
    "designed openness (garage decks, warehouse aisles). Deli Counter's to fix -- the partition to the walls, and a "
    "check refusing a partition that stops short of where its rooms meet unless the spec names the gap -- through "
    "the graders, as both move the fights; the walker's call first whether the basement was meant open. 6,")


def _span(text, number):
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for old in (S_OLD, L_OLD):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 250)
    assert s < text.find(S_OLD) < h, "250's status is not where it was read"
    assert h < text.find(L_OLD) < e, "250's Left is not in 250"
    for block in (S_NEW, L_NEW):
        for line in block.splitlines():
            assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(S_OLD, S_NEW).replace(L_OLD, L_NEW)
    s, h, e = _span(text, 250)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-14 -- THE WALKER'S WALK"), "250's status moved"
    assert "\n\n" not in text[s + 2:h], "a blank line inside 250's status"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 250: finding 5 traced; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
