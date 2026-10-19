"""Roadmap 196 NARROWED again, 2026-10-19 (later the same day): 30 of 31 stores hold two cabinets, two different
machines, the partition behind each now usable -- Deli Counter 0.231.0 and 0.231.1, cold runs 9326 and 9327.

The status line is replaced whole, the earlier same-day NARROWED status kept after it verbatim; a paragraph goes
after the item's last body line (its LEFT paragraph, which this one answers). Anchored on both lines' sha256, the
heading two lines below the status and the next item's status two lines below the body's end. The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_196_partitions.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
STATUS_SHA = "d253bb0628ce4244b5e29d5204706a553fd24f59884ef2e70a99e50b53edbf97"
HEADING_PREFIX = "**196. Furnish stands wall pieces against walls that are not there.**"
OLD_PREFIX = "*STATUS: NARROWED 2026-10-19 -- "
BODY_END_SHA = "8cba59cb60589dda373fb0e4070b84a51b660b5d8c9ac6a0f6967c8129948d9a"

NEW = ("*STATUS: NARROWED 2026-10-19 -- 30 of the 31 stores hold their two cabinets, two different machines, seen and "
       "priced in levels. The short stores' refusals were traced rule by rule (`patches/dc_store_cabinets/"
       "why_rule.py`): the 0.9 m spread off other volumes and the metre-off-a-partition line rule, which refused "
       "every slot a partition wall offers -- the \"partition still unfurnished\" this item named. Deli Counter "
       "0.231.0 (50db4890, `patches/patch_dc_cabinet_partitions.py`): the cabinet may back onto the one partition "
       "behind it (`backs_on_partitions`, a call made 2026-10-19 and meant to be changed); simulated before "
       "writing and reproduced exactly -- fuel_stop_heist 0 -> 2, pharmacy_a01 1 -> 2, stop_n_go 1 -> 2, "
       "pawn_shop_a01 0 -> 1, nine of the fifteen displaced fillers back, poster boards +2. Deli Counter 0.231.1 "
       "(5f3c51c0): the cabinet is `distinct`, after cold run 9326 showed the six delis one machine twice. Cold "
       "runs 9326 and 9327 (urban_row_001, 0 interventions, findings 107): pharmacy_a01 two cabinets, deli_a01 two "
       "machines on its partition with its vending, file cabinet and poster board back; priced against 9325, +0.1 "
       "draws a heading on the mean and p95 -0.00 ms inside a 0.05 ms floor. Open: pawn_shop_a01 at one; every "
       "other wall piece still keeps a metre off every partition -- the dial is per piece, and only the cabinet "
       "has it. Earlier status kept: NARROWED 2026-10-19 -- ")

BODY = [
    "",
    "**PARTITIONS AND MACHINES, 2026-10-19** (`patches/patch_dc_cabinet_partitions.py` and `dc_cabinet_partitions/`; "
    "`patches/patch_dc_cabinet_variants.py` and `dc_cabinet_variants/`; `docs/cold_runs/cold_9326/`, `cold_9327/`). "
    "**The LEFT above, attributed** (`why_rule.py`, tracing which `return False` of `_seed_clear` each candidate "
    "reached, on 0.230.0's library): in the four short stores' selling rooms the 0.9 m spread refused 12 to 37 "
    "candidates and the metre-off-a-partition line rule 24 to 48, with 2 at a door's approach and 3 at a ladder. "
    "The line rule keeps a piece's centre a metre off every partition's line, so a cabinet backed against a "
    "partition, its centre about half a metre off it, never stood; the door rule is separate and stays. **The "
    "call, made 2026-10-19 and meant to be changed:** one dial on one piece -- `backs_on_partitions`, on for the "
    "store cabinet alone, exempts the one partition whose centreline is the room edge it backs onto; every other "
    "rule and every other piece are as they were. **Simulated before writing** (`partition_sim.py`: the same "
    "edits in a scratch copy, the library stripped and refurnished in memory) and **reproduced exactly** by the "
    "real migration: 26 specs; 30 of 31 stores at two; +5 file cabinets and +4 vending back, because a cabinet "
    "now finds a partition before it needs a filler's slot; poster boards +2. **Found in a level, fixed the same "
    "hour:** cold run 9326 stood deli_a01's two cabinets on its customer floor, both one machine -- a variant is "
    "the name's crc32 and both names drew it, as in all six delis -- so 0.231.1 makes the cabinet `distinct`, "
    "0.163.0's dial, which moves a variant and never a placement. **Seen** (`cold_9327/cabinets_before_after.png`): "
    "PIKE DRAW and LUCKY HOAGIE on deli_a01's partition, the doorway clear; pharmacy_a01's second cabinet on the "
    "partition that stood bare in 9325. **Priced** against 9325 (`cold_9327/price/`): +0.1 draws a heading on the "
    "mean, -4 to +6 at any heading, p95 inside the floor, textures +0.1 MiB. **Still open:** pawn_shop_a01's "
    "second cabinet (its shop floor is the spread rule's), and whether any other wall piece should back onto a "
    "partition -- a dial a piece, not a rule for all.",
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if _sha(l) == STATUS_SHA]
    assert len(hits) == 1, f"item 196's status found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(HEADING_PREFIX), "the status no longer adjoins 196's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    ends = [j for j, l in enumerate(lines) if _sha(l) == BODY_END_SHA]
    assert len(ends) == 1 and ends[0] > i, f"item 196's last body line found {len(ends)} times"
    j = ends[0]
    assert lines[j + 1] == "" and lines[j + 2].startswith("*STATUS:"), "item 196's body no longer ends there"
    for k in range(i + 3, j):
        assert not lines[k].startswith("*STATUS:"), "another status inside item 196 at line %d" % (k + 1)
    for block in BODY:
        assert not (block.startswith("**") and block[2:3].isdigit()), "a body line would parse as an item"
    lines[j + 1:j + 1] = BODY
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: NARROWED 2026-10-19 -- 30 of the 31") and lines[i].endswith("*")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 196 NARROWED (Deli Counter 0.231.0 / 0.231.1, cold runs 9326 and 9327); now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
