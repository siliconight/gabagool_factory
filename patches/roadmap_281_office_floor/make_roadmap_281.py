"""Write patches/patch_roadmap_281_office_floor.py: 281's status (the block above its heading, embedded exactly)
replaced with a CLOSED one that keeps it; item 283 appended after the last item. Refuses if the patch name is taken."""
import pathlib
import re

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_281_office_floor.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t


def status_of(n):
    m = list(re.finditer(r"(?m)^\*\*%d\. " % n, t))
    assert len(m) == 1, n
    h = m[0].start()
    s = t.rindex("\n\n", 0, h - 2) + 2
    block = t[s:h - 2]
    assert block.startswith("*STATUS: ") and block.endswith("*") and "\n" not in block, n
    heading = t[h - 2:t.index("\n", h)]
    assert t.count(heading) == 1, n
    return heading, block


H281, OLD281 = status_of(281)
heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", t)]
assert heads[-1] == 282 == max(heads), heads[-3:]

NEW281 = (
    "*STATUS: CLOSED 2026-10-21 -- Deli Counter 0.248.0 (88422d0b, `patches/patch_dc_office_floor.py`): "
    "`level_design.is_office_floor`, read in `_room_kind` after the strip club's, the card shop's and the video store's "
    "rules -- a building whose id says `office`, and a room the word table would make a shop floor by `floor` alone. "
    "Counted first: fifteen library rooms are shop floors by `floor` alone, the offices' two plainly wrong; the other "
    "thirteen (arenas', a brewery's, a depot's, a foundry's, a freight terminal's, the warehouses', a setback demo's, "
    "a supermarket's mezzanine) keep their kind. Refurnished: office's floor_1 from a service counter, three vending "
    "machines, two filing cabinets, four shelf runs, four cartons and four litter bins to four desks and their chairs, "
    "three shelf runs, six filing cabinets and five cartons; office_stepped's from five litter bins and nine cartons to "
    "six desks and their chairs and ten cartons; floor share 13.9 -> 13.9 % and 12.5 -> 13.6 %; no other room moved; "
    "four tests, two failing on 0.247.0 on behaviour. Cold run 9370 (restaurant_row_001 at seed 9003, 9369's level, "
    "Deli Counter the only tool moved): 0 interventions, findings 108 -> 108; frames of floor_1 before and after "
    "(`docs/findings/office_floor_281/`) -- the desks stand where the bins stood, their screens lit, and the bullpen, "
    "the control, does not move; the office's merged meshes 290 -> 302, every other building's the same. Earlier "
    "status kept: " + OLD281[len("*STATUS: "):])
ITEMS = (
    "*STATUS: OPEN 2026-10-21 -- measured closing roadmap 281; not started.*\n\n"
    "**283. The shelter pass and the combat audit ask a piece's storey two more ways.** Deli Counter 0.246.0 made "
    "furnish's count ask a volume's FOOT (`_room_volume_count`), because `abs(z - (floor + size_z / 2)) < sh` put a "
    "piece on the floor above or below exactly `sh` away and let float rounding decide. The same question is still "
    "asked twice more, differently. `level_design._room_has_cover` and `_room_has_shelter` -- which decide whether "
    "`seed_cover` stands shelter in a room -- keep that float window, and count a cover marker on ANY storey inside "
    "the room's plan. `combat_audit._cover_in_room` is wider still: `abs(z - floor) < sh` on a volume's CENTRE, which "
    "counts everything standing on the floor below (measured in memory: a 1 m crate on the ground floor counts as "
    "cover in the room over it), and its markers carry no storey test either. Asked by the foot and by a marker's own "
    "floor, the audit's findings over the 159 library specs gain seven COVER_ALL_LOW -- furnished rooms whose every "
    "piece is under the break height, which tall pieces on the floor below had been answering for "
    "(cbp_town_finale's home_plate_overlook, deli_a02's stairwell, final_stand's stair_core, freight_terminal_a02's "
    "gantry_control, pawn_shop_a02's upper_flat, primos_pizza's rear_hall, twin_a01's front_left_1) -- and lose none. "
    "The fight is the walker's first priority (2026-10-21: \"free navigation and fun gun fights\"), and these are the "
    "instruments that answer for it. **What would close it:** one storey test, a volume's foot and a marker's floor, "
    "asked by all four; the shelter pass re-run where a room has none by it, every room it fills attributed; the "
    "audit's seven read again; the presets' corpus test still clean.\n")

PATCH = '''"""Roadmap 281: an office building's open floor is an office (Deli Counter 0.248.0, cold run 9370) -- CLOSED; item 283,
found on the way. Copied from `patch_roadmap_148_corner_store_rows.py`'s checks: replaces 281's status block (the
paragraph directly above its heading, asserted to be the one this was written against) with one that keeps it after
"Earlier status kept:", and appends item 283 after the last item (asserted to be 282). The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_281_office_floor.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_281 = %r
STATUS_281_OLD = %r
STATUS_281_NEW = %r
ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**283. " in text or STATUS_281_NEW[:80] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_281) != 1:
        raise SystemExit("REFUSED: 281's heading is not there once; nothing written")
    h = text.find(HEADING_281)
    s = text.rindex("\\n\\n", 0, h) + 2
    if text[s:h] != STATUS_281_OLD:
        raise SystemExit("REFUSED: 281's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_281_NEW + text[h:]
    if text.count(STATUS_281_NEW + HEADING_281) != 1:
        raise SystemExit("REFUSED: 281's status no longer adjoins its heading; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 282 or heads[-1] != 282:
        raise SystemExit("REFUSED: the last item is not 282; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + "\\n" + ITEMS
    if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*283\\. ", text)) != 1:
        raise SystemExit("REFUSED: item 283's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 281: CLOSED, the earlier status kept; item 283 appended; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (H281, OLD281, NEW281, ITEMS)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
