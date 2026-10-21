"""Write patches/patch_roadmap_283_storey_shelter.py: 283's status (the block above its heading, embedded exactly)
replaced with a CLOSED one that keeps it; item 284 appended after the last item. Copied from make_roadmap_281.py.
Refuses if the patch name is taken.

    python make_roadmap_283.py <dc hash> <build sentence> <suite sentence>
"""
import pathlib
import re
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_283_storey_shelter.py"
assert not dest.exists(), "name taken"
DC, BUILD, SUITE = sys.argv[1], sys.argv[2], sys.argv[3]
assert re.fullmatch(r"[0-9a-f]{8}", DC), DC
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


H283, OLD283 = status_of(283)
heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", t)]
assert heads[-1] == 283 == max(heads), heads[-3:]

NEW283 = (
    "*STATUS: CLOSED 2026-10-21 -- Deli Counter 0.249.0 (" + DC + ", `patches/patch_dc_storey_shelter.py`): "
    "`level_design.stands_on_storey` and `marker_on_storey`, one storey test asked by all four -- furnish's count, "
    "`_room_has_cover`, `_room_has_shelter`, `combat_audit._cover_in_room` -- and COVER_ALL_LOW's tallest asked on its "
    "room's storey. Attributing every room the shelter pass then filled found the defect behind this one: nothing ran "
    "the pass over the library (`enrich` runs in `presets.make`, `build.py` builds a spec as it stands, the shelter "
    "test asked presets alone), so `migrate_shelter.py` runs it and a test keeps the library its fixed point. Eleven "
    "shelter pieces in eleven combat rooms of nine specs, each attributed (`patches/dc_storey_shelter/`): three "
    "sheltered only by something on another storey (final_stand's stair_core, rowhouse_raid's kitchen, twin_a01's "
    "front_left_1), three by furnish's own tall pieces until a refurnish moved them (rail_station_a02's vault_approach "
    "at 0.204.0, rowhouse_raid's basement_vault at 0.234.0, warehouse_a01's back_corridor at 0.131.0), five never "
    "sheltered in any committed version; the pass falls back to the smallest piece where a room's own fits nowhere "
    "(the rowhome preset's back_0, which only the leak had sheltered). The audit over the library: COVER_ALL_LOW 12 -> "
    "8, KILLBOX, C_NAKED_ROOM and H_NO_HOLDOUT 0 -> 0; of the seven it newly sees four are filled and three stay; the "
    "eight left each attributed -- seven with no clear spot at any of 36 candidates, one under the seeding area. Only "
    "the eleven rooms move, and three lose life to the re-draw (cbp's club_ring_overlook 27 -> 15 pieces, its tables "
    "drawing 3 chairs where they drew 15: item 284). Nine tests, six failing on 0.248.0 on behaviour; the presets' "
    "corpus tests clean; " + BUILD + "; " + SUITE + ". No cold run: the level the last runs built "
    "(restaurant_row_001 at seed 9003 -- deli_a03, pharmacy_a01, office) draws none of the nine specs, and a run that "
    "cannot move proves nothing; the first package that draws one shows it. Earlier status kept: "
    + OLD283[len("*STATUS: "):])
ITEMS = (
    "*STATUS: OPEN 2026-10-21 -- measured shipping roadmap 283; not started.*\n\n"
    "**284. A dining table draws none to four chairs, and one in five stands with none.** `level_design`'s "
    "`table_dining` seats `(\"table\", 0, 4)`: `_seats` draws `rng.randint(0, 4)` chairs and clearance refuses some, "
    "so how many chairs a table has is chance. Measured on Deli Counter 0.249.0's library: 255 dining tables, 51 with "
    "no chair (20 %), 67 with one, 64 two, 43 three, 30 four; the chairless ones in 31 specs (cbp_town_finale's five; "
    "apartment_walkup_a01's, courthouse_a02's, final_stand's, landmark_hall_a01's and museum_a01's three each). The "
    "draw is also the most fragile thing in a room: a piece placed before the tables re-draws every table after it, "
    "and 0.249.0's one shelter crate took cbp's club_ring_overlook from 15 chairs at 9 tables to 3 at 8. The guide the "
    "walker filed on 2026-10-21 (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) reads both "
    "sides of it: a table with no chair is a cluster missing its reason (section 8, \"what belongs together\"), and "
    "loose half-metre chairs are the incidental obstacles navigation pays for (sections 12 and 15, \"players stare at "
    "the floor\"). Both point the same way: a table's chairs belong to it, mostly tucked to it. **What would close "
    "it:** every dining table seats at least one, its chairs drawn from the table's own stream so that an upstream "
    "piece does not re-draw them, and tucked within a seat's depth of the table unless pulled out on purpose; the "
    "library refurnished and attributed, the nav gate and the audit read before the look.\n")

PATCH = '''"""Roadmap 283: a room holds what stands on its storey, and the shelter pass runs over the library (Deli Counter
0.249.0) -- CLOSED; item 284, found on the way. Copied from `patch_roadmap_281_office_floor.py`'s checks: replaces
283's status block (the paragraph directly above its heading, asserted to be the one this was written against) with
one that keeps it after "Earlier status kept:", and appends item 284 after the last item (asserted to be 283). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_283_storey_shelter.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_283 = %r
STATUS_283_OLD = %r
STATUS_283_NEW = %r
ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**284. " in text or STATUS_283_NEW[:80] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_283) != 1:
        raise SystemExit("REFUSED: 283's heading is not there once; nothing written")
    h = text.find(HEADING_283)
    s = text.rindex("\\n\\n", 0, h) + 2
    if text[s:h] != STATUS_283_OLD:
        raise SystemExit("REFUSED: 283's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_283_NEW + text[h:]
    if text.count(STATUS_283_NEW + HEADING_283) != 1:
        raise SystemExit("REFUSED: 283's status no longer adjoins its heading; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 283 or heads[-1] != 283:
        raise SystemExit("REFUSED: the last item is not 283; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + "\\n" + ITEMS
    if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*284\\. ", text)) != 1:
        raise SystemExit("REFUSED: item 284's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 283: CLOSED, the earlier status kept; item 284 appended; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (H283, OLD283, NEW283, ITEMS)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
