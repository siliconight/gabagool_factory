"""Write patches/patch_roadmap_288_reserved_routes.py: 288's status (the block above its heading, embedded exactly)
replaced with a NARROWED one that keeps it. Copied from make_roadmap_283.py's status half. Refuses if the name is
taken."""
import pathlib
import re

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_288_reserved_routes.py"
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


H288, OLD288 = status_of(288)
NEW288 = (
    "*STATUS: NARROWED 2026-10-21 -- the corner stores' floors done. Deli Counter 0.250.0 (f0ab57ca, "
    "`patches/patch_dc_reserved_routes.py`) reserves a corner store's routes before its rows are laid: "
    "`protected_routes`, square routes between a floor's doors and markers on the floor as furnish finds it "
    "(`unfurnished`), a greedy spanner at the guide's 10 %, corridors half `two_abreast_width()` (1.90 m) wide, kept "
    "clear by furnish's rows, floor pieces, clusters and chairs where `reserves_routes` says (a shop floor that stands "
    "rows); down a row each island on the writer's centimetre. Over the fourteen corner-store specs, every room of "
    "them: routes over 10 % 20 in 13 rooms -> 4 in 3, none on a corner floor (the four in back offices and back halls, "
    "which reserve nothing; a corner floor's worst 1.096); narrowed to single file 70 -> 54; two abreast after "
    "furnishing 129 -> 145; the floors' share 19.2-23.1 -> 17.2-22.1 %, inside the walker's band; no other room moved. "
    "Refuted and kept, each measured (`patches/dc_reserved_routes/`): diagonal routes (they cut the rows into "
    "scattered gondolas), a spanning tree (10 pairs over 10 % against 4), the aisle as the corridor (62 narrowed "
    "against 54), the fixtures pass asked (two stores lost both video poker cabinets), the rows a centimetre wider "
    "(off a room's own aisles). Cold run 9371 (restaurant_row_001 at seed 9003, Deli Counter the only tool moved): 0 "
    "interventions, findings 108 -> 108; from deli_a03's west door 9370 faces a wall of gondola fronts and 9371 looks "
    "down a lane two abreast to the kitchen door, 26.0 % of that frame moved, the controls 0.0 to 0.4 % "
    "(`docs/findings/reserved_routes_288/`). LEFT: the census's AUTHORED arm measures a store's rows against an empty "
    "floor, where the guide's 10 % is a flag on dressing over the functional build -- an arm that keeps furnish's "
    "functional pieces (anchors, rows) and strips only its dressing (clusters, small floor pieces) is the census's "
    "next step; then the reservation for the kinds the census names next, each measured before and after -- the "
    "office (14 of 324 routes over 10 %, 25 narrowed), the vault (6 and 42 of 146), the small objective rooms whose "
    "door-to-marker routes grow 20 to 30 %; the eleven authored cases; the census's limits named where they bite. "
    "Earlier status kept: " + OLD288[len("*STATUS: "):])

PATCH = '''"""Roadmap 288: the corner stores' floors reserve their routes (Deli Counter 0.250.0, cold run 9371) -- NARROWED.
Copied from `patch_roadmap_283_storey_shelter.py`'s status half: replaces 288's status block (the paragraph directly
above its heading, asserted to be the one this was written against) with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_288_reserved_routes.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_288 = %r
STATUS_288_OLD = %r
STATUS_288_NEW = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if STATUS_288_NEW[:80] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_288) != 1:
        raise SystemExit("REFUSED: 288's heading is not there once; nothing written")
    h = text.find(HEADING_288)
    s = text.rindex("\\n\\n", 0, h) + 2
    if text[s:h] != STATUS_288_OLD:
        raise SystemExit("REFUSED: 288's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_288_NEW + text[h:]
    if text.count(STATUS_288_NEW + HEADING_288) != 1:
        raise SystemExit("REFUSED: 288's status no longer adjoins its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 288: NARROWED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (H288, OLD288, NEW288)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
