"""Roadmap 241, 2026-10-13: the near side's two residues fixed and proven -- Lot 0.122.0 and cold run 9290 (the
starved candidate), Level Factory 0.203.0 and cold run 9291 (the spent deal). The status stays NARROWED; its Left
clause loses the two, and one body paragraph is added after the near side's. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check`.

Cold run 9291's result is read from its own driver log and the patch refuses until the run has ended, so the
status names the count the run reported rather than one typed from memory.

    python patches/patch_roadmap_241_residues.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

LEFT_OLD = ("Left: the walker's eye on 9287's and 9289's frames (`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`); one "
            "candidate's enemy spawns starved by the near block and the far wall together (`LOT_ENEMY_SPAWN_UNPLACEABLE`, "
            "by elimination, the mechanism not traced); a fresh deal when a room's only fitting block is spent; heights "
            "by cause;")
BODY_ANCHOR = "And a 6.70 m room stayed open because the deal had spent its one narrow block.\n\n"


def _result(n):
    log = (ROOT / "docs" / "cold_runs" / f"cold_{n}" / "driver.log").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"INTERVENTIONS: (\d+)\s+\(journal (\d+), unattributed files (\d+)\)", log)
    assert m and "DONE" in log, f"cold run {n} has not ended"
    return f"{m.group(1)} interventions"


def _texts(r9290, r9291):
    left_new = (
        "The near side's two residues fixed and proven: Lot 0.122.0 (030901f) lets enemies stand where the fences "
        "leave a row open -- the near block's band had starved seed_9205 of all six "
        "(`docs/findings/urban_street/spawn_filters.py`) -- and cold run 9290 (" + r9290 + ") graded all three "
        "candidates PASS 90; Level Factory 0.203.0 (c132c30) deals afresh where a design fits and the bag's "
        "remainder does not, and cold run 9291 (" + r9291 + ") stood a block in every near-side room, each left "
        "with less than the narrowest design's 6.6 m. Left: the walker's eye on 9287's and 9289's frames "
        "(`ab_9287/ab_sheet.png`, `ab_9289/ab_sheet.png`); heights by cause;")
    body = (
        BODY_ANCHOR +
        "**THE NEAR SIDE'S TWO RESIDUES, 2026-10-13** (`docs/findings/urban_street/spawn_filters.py`, "
        "`near_blocks.py`; `patches/patch_lot_open_rows.py`, `patch_lf_near_fresh_deal.py`; `docs/cold_runs/cold_9290/`, "
        "`cold_9291/`). **The starved candidate, traced.** Lot keeps enemies out of the band behind every Empty row's "
        "front line, across the plate's whole width (`site_fences.shut_bands`, Lot 0.97.3), and `plan_fences` leaves "
        "a row open, unfenced, when a mission marker stands behind it. A near-side block is a row of its own: on "
        "seed_9205 its band was the mission's own half of the plate, the far row's band everything but the street, "
        "and the street inside the opening range, so all six enemies were dropped; on seed_9104 all six stood in the "
        "street; on seed_9003 the band covered the street and the crew's route. The fences had left all three rows "
        "open -- of the 276 `lot_assemble` job logs on this disk, the only three with a row left open. Lot 0.122.0 "
        "makes enemy placement ask the fences' question (`site_fences.markers_behind`); the strip's ten replayed "
        "jobs move 0 of 420 files. Cold run 9290 (" + r9290 + "): every candidate graded, PASS 90 each, seed_9205 "
        "standing all six; the fights moved with the enemies, now between the buildings near the route -- the first "
        "enemy shot at 1.93 to 2.65 s, `INSTANT_CONTACT` on all three, PASS 100 -> 90 on two -- recorded, not tuned, "
        "enemy placement being provisional. **The spent deal.** `empties.infill` left a room open whenever what was "
        "left in the bag was too wide for it; on a test street of three rooms and three designs, 0.202.0 left 58 of "
        "120 rooms with a design's width or more empty over forty seeds. Level Factory 0.203.0 deals afresh behind "
        "the remainder where a design fits. Cold run 9291 (" + r9291 + "): seed_9104 and seed_9205 each stand a "
        "second 6.6 m block in the 6.70 m room between b1 and b2; every near-side room on the three candidates holds "
        "a block, each left with less than 6.6 m.\n\n")
    return left_new, body


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE NEAR SIDE'S TWO RESIDUES" not in text, "already applied"
    for old in (LEFT_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert s < text.find(LEFT_OLD) < h, "the Left clause is not 241's status"
    left_new, body = _texts(_result(9290), _result(9291))
    for line in body.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(LEFT_OLD, left_new).replace(BODY_ANCHOR, body)
    h = text.find("\n\n**241. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241: the near side's two residues; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
