"""Write patches/patch_roadmap_148_corner_store_rows.py: 148's status (the block above its heading, embedded exactly)
replaced with a NARROWED one that keeps it; a paragraph appended to 148's body after its last (embedded exactly); items
281 and 282 appended after the last item. Refuses if the patch name is taken. PRICE is read from a file the price step
writes, so the status carries the measured sentence."""
import pathlib
import re
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_148_corner_store_rows.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t
PRICE = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip()
assert PRICE and "\n" not in PRICE


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


H148, OLD148 = status_of(148)
h149 = re.search(r"(?m)^\*\*149\. ", t).start()
s149 = t.rindex("\n\n", 0, h149 - 2) + 2
h148 = re.search(r"(?m)^\*\*148\. ", t).start()
body = t[h148:s149 - 2]
LAST148 = "\n\n" + body.split("\n\n")[-1]
assert t.count(LAST148) == 1
heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", t)]
assert heads[-1] == 280 == max(heads), heads[-3:]

NEW148 = (
    "*STATUS: NARROWED 2026-10-21 -- THE CORNER STORES STAND AISLES: Deli Counter 0.247.0 (e1cbd7e1, "
    "`patches/patch_dc_corner_store_rows.py`) lays a corner store's selling floor -- a deli's market aisles, a "
    "convenience store's or a gas station's sales floor -- in rows of Zoo's `snack_gondola`, 1.40 to 1.45 m tall "
    "(cover a body crouches behind, never shelter), down the room's long axis or along its own aisles at their depth "
    "and on their line, the contract's 1.25 m aisle from every wall's face, until a quarter of the floor stands under "
    "furniture or nothing more clears; a deli is a store to the gondola migration, so its two authored aisle shelves "
    "are snack gondolas too. 14 library floors stand 126 gondolas and go from 5.4-13.4 % of their floor under "
    "furniture to 19.2-23.1 %; no other room moved. Under it, Deli Counter 0.246.0 (d94c6c0f, "
    "`patches/patch_dc_room_count.py`): a room counted a piece standing on the floor above or below it whenever "
    "float rounding put it inside a window -- 740 volumes in 195 rooms of 55 specs -- and furnished one piece fewer "
    "for each; refurnished, 109 rooms of 44 specs go 1,034 -> 1,432 pieces. Cold runs 9368 (the control: Deli "
    "Counter 0.245.0 from a clone; 9367 stopped at its shell leg without the clone's navgate manifests) and 9369 "
    "(shipped), restaurant_row_001 at seed 9003, the review's level: 0 interventions each, findings 108 -> 108; "
    "deli_a03's market aisles 5.7 -> 19.7 % (frames in both lights, `docs/findings/denser_rooms_148/`). " + PRICE +
    " REFUTED, kept: more pieces -- furnish's target without its 160 to 400 m2 plateau writes 63 % more across the "
    "library and moves the market aisles 5.7 -> 6.8 %. Left: the review's other rooms by the same rows where their "
    "kind has them -- a stockroom's racks, a bullpen's desk pairs or cubicle banks, a kitchen's prep islands; an "
    "office's floor_1 furnishing as a shop floor (281); the card shop island's aisle (282); a clock, a ceiling vent, "
    "a smoke detector, a light switch and an exit sign, which no species draws, and the no-collision dressing layer; "
    "and whether a room reads as inhabited, the walker's eye -- the market aisles' frames are the question. Earlier "
    "status kept: " + OLD148[len("*STATUS: "):])
BODY148 = (
    "\n\n**THE CORNER STORES' AISLES, 2026-10-21** (Deli Counter 0.246.0 and 0.247.0; `patches/dc_room_count/`, "
    "`patches/dc_corner_store_rows/`, `docs/findings/denser_rooms_148/`). Measured first: furnish's target is one "
    "piece per 16 m2 to ten, then one per 40 m2 to thirty, so every room between 160 and 400 m2 -- the band all seven "
    "of the review's frames were in -- wants ten, and the floor under furniture was 3.7 to 16.1 % in those rooms, "
    "most of the office's an authored cubicle bank. REFUTED, kept: more pieces (`plateau_dry_run.py`). What a room is "
    "known by stands in rows, and nothing in furnish laid any. REFUTED, kept: the rows' first grid stood an aisle off "
    "the room's bounds -- a wall's centre line -- and refused every slot beside a wall, 1.07 m from the face; an even "
    "grid stood its columns 1.1 m off deli_a03's own aisles; the square gas station floors ran the rows across their "
    "10 m aisles. A defect underneath, shipped first on its own: the first 1.45 m gondola counted in deli_a03's "
    "apartment upstairs and cost it nine pieces.")
ITEMS = (
    "*STATUS: OPEN 2026-10-21 -- found in cold run 9369's frames (roadmap 148); not started.*\n\n"
    "**281. A room's kind reads its words without its building: an office's floor_1 furnishes as a shop floor.** "
    "`level_design._room_kind` reads a room's id through `_ROOM_KINDS` in order, and `floor` is a shop-floor word "
    "(\"a shop floor is shelving and stock\"), so the office's and office_stepped's 816 m2 `floor_1` -- the open office "
    "floor of the storey above the bullpen -- is furnished by the shop floor's recipe. Measured on Deli Counter "
    "0.247.0: the office's holds a service counter, three vending machines, two filing cabinets, four shelf runs, four "
    "cartons and four litter bins; office_stepped's five litter bins and nine cartons. 0.246.0's count fix let the "
    "office's reach its target, 5 -> 18 pieces, and cold run 9369's frame of it shows litter bins standing mid-floor "
    "among carton stacks "
    "(`docs/findings/denser_rooms_148/rooms_9368_9369_lit.jpg`). The strip club, the card shop and the video store "
    "are already read by their building first (`is_strip_club_room`, `is_card_shop_room`, `video_store_room_kind`); "
    "an office building's `floor_N` is that shape again. **What would close it:** the rooms whose kind comes from a "
    "bare `floor` counted across the library by building; the office's read as offices (desks, which 148's rows "
    "would lay in pairs); the refurnish attributed; a frame of floor_1 before and after.\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured building Deli Counter 0.247.0's rows (roadmap 148); not started.*\n\n"
    "**282. The card shop's island stands its aisle off the room's bound, not the wall's face.** "
    "`level_design._island_slots` keeps a single island `island_aisle_width` (1.25 m) from the room's BOUNDS, and a "
    "bound is a wall's centre line: the floor between the island and the wall's face is half a wall short. Measured "
    "on card_shop_a01: its twin `pack_wall_island` stands 1.12 m from a partition's face -- under the aisle its own "
    "docstring claims, over the contract's 1.10 m corridor minimum. Deli Counter 0.247.0's rows measure from the "
    "faces (`_row_slots`) and left this alone, because moving it refurnishes a room the walker has passed. **What "
    "would close it:** `_island_slots` asked from the faces; card_shop_a01's refurnish attributed; every island in the "
    "library an aisle from every face, by a test that re-derives the gap.\n")

PATCH = '''"""Roadmap 148: the corner stores stand aisles (Deli Counter 0.246.0 and 0.247.0, cold runs 9367 to 9369); items 281
and 282, found on the way. Copied from `patch_roadmap_267_container.py`'s checks: replaces 148's status block (the
paragraph directly above its heading, asserted to be the one this was written against) with one that keeps it after
"Earlier status kept:", appends a paragraph to 148's body after its last (asserted whole), and appends items 281 and
282 after the last item (asserted to be 280). The index is NOT touched here: run `python tools/roadmap_status.py
--write` then `--check` after it.

    python patches/patch_roadmap_148_corner_store_rows.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_148 = %r
STATUS_148_OLD = %r
STATUS_148_NEW = %r
BODY_148_LAST = %r
BODY_148_ADD = %r
ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**281. " in text or STATUS_148_NEW[:80] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_148) != 1:
        raise SystemExit("REFUSED: 148's heading is not there once; nothing written")
    h = text.find(HEADING_148)
    s = text.rindex("\\n\\n", 0, h) + 2
    if text[s:h] != STATUS_148_OLD:
        raise SystemExit("REFUSED: 148's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_148_NEW + text[h:]
    if text.count(STATUS_148_NEW + HEADING_148) != 1:
        raise SystemExit("REFUSED: 148's status no longer adjoins its heading; nothing written")
    if text.count(BODY_148_LAST) != 1:
        raise SystemExit("REFUSED: 148's last paragraph is not there once; nothing written")
    b = text.index(BODY_148_LAST) + len(BODY_148_LAST)
    if text.find(HEADING_148) > b or not text.startswith("\\n\\n*STATUS: ", b) or text.find("\\n\\n**149. ", b) < 0:
        raise SystemExit("REFUSED: 148's last paragraph is not where 148 ends; nothing written")
    text = text[:b] + BODY_148_ADD + text[b:]
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 280 or heads[-1] != 280:
        raise SystemExit("REFUSED: the last item is not 280; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + "\\n" + ITEMS
    for n in (281, 282):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 148: NARROWED, the earlier status kept, a body paragraph added; items 281 and 282 appended; "
          "now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (H148, OLD148, NEW148, LAST148, BODY148, ITEMS)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
