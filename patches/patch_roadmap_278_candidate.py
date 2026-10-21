"""Roadmap 278: Level Factory 0.228.0 refuses a candidate the mission's plan never builds. Copied from
`patch_roadmap_275_teller.py`'s checks: replaces 278's status block (the paragraph directly above its heading,
asserted to be the one this was written against) with a CLOSED one that keeps it after "Earlier status kept:". No item
is added. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_278_candidate.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_278 = "\n\n**278. Level Factory approves a candidate no job built.**"
STATUS_278_OLD = ("*STATUS: OPEN 2026-10-21 -- found by cold run 9362; the cold drive guards it since "
                  "(`tools/cold_drive/cold_drive.sh`), Level Factory does not.*")
STATUS_278_NEW = (
    "*STATUS: CLOSED 2026-10-21 -- SHIPPED AND PROVEN. Level Factory 0.228.0 (e71ea71): `approve candidate_selected` "
    "refuses a candidate outside the mission's plan -- its batch's seeds, `planner.derive_seeds(seed_base, "
    "candidate_count)` through `_plan_for`, known before any job runs -- names the planned ones and records nothing; a "
    "planned candidate not yet built is recorded with the warning as before, and a mission no batch holds keeps the "
    "warning. `tests/unit/test_candidate_guard.py`, two of its five failing on 0.227.0; the suite exit 0, 2,565 passed; "
    "against a copy of cold run 9362's workspace the real command refuses seed 9281 with nothing recorded and approves "
    "seed 9155 (`patches/lf_candidate_guard/approve_probe_9362.out.txt`). REFUTED, kept: this item was first written as "
    "if Level Factory took the unbuilt candidate unguarded. It warned at the approve step -- \"no "
    "bank_block_001.lot_assemble.candidate.seed_9281 yet; the selection is recorded and will resolve once that job runs\" "
    "(9362's `driver.log` line 17) -- by design: whether a candidate's job has run when it is selected is an ordering "
    "question its `_refuse_bad_candidate` leaves open on purpose. The gap was narrower than the item said, membership "
    "of the plan, which is not that question; the fix asks the plan, not the jobs. Earlier status kept: OPEN 2026-10-21 "
    "-- found by cold run 9362; the cold drive guards it since (`tools/cold_drive/cold_drive.sh`), Level Factory does "
    "not.*"
)


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if STATUS_278_NEW[:70] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_278) != 1:
        raise SystemExit("REFUSED: 278's heading is not there once; nothing written")
    h = text.find(HEADING_278)
    s = text.rindex("\n\n", 0, h) + 2
    if text[s:h] != STATUS_278_OLD:
        raise SystemExit("REFUSED: 278's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_278_NEW + text[h:]
    if text.count(STATUS_278_NEW + HEADING_278) != 1:
        raise SystemExit("REFUSED: 278's status no longer adjoins its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 278: CLOSED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
