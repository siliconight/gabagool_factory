"""Write patches/patch_roadmap_289_sight_contract.py: 289's status (the block above its heading, embedded exactly)
replaced with a NARROWED one that keeps it, and item 292 appended after 291. Copied from make_roadmap_288.py's status
half and `patch_roadmap_guides_2026_10_21.py`'s append half. Refuses if the name is taken."""
import pathlib
import re

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_289_sight_contract.py"
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


H289, OLD289 = status_of(289)
NEW289 = (
    "*STATUS: NARROWED 2026-10-21 -- the advisory's heights done; left, the contract's note. Level Factory 0.229.0 "
    "(1f6f047, `patches/patch_lf_sight_crossing.py`) moved `sightlines.py`'s eye 1.4 -> 1.6 and its crossing 1.2 -> "
    "1.3, and held the module's heights to Laser Tag's files with the check Lot's copies answer to "
    "(`lasertag_contract.check_sight_drift`), a test failing on 0.228.0 on behaviour. That left them literals beside a "
    "comment naming the contract, which the walker's rule forbids, so Level Factory 0.230.0 (16ba543, "
    "`patches/patch_lf_sight_contract.py`) draws the advisory's lines from the body the run fields: the adapter hands "
    "`tactical.advise_scene` an `Engagement` carrying the heights the run's scenario carries -- Laser Tag's own, under "
    "the contract's body and the job's scenario, the one precedence `run` writes (`_run_scenario`, `_run_engagement`) "
    "-- and `sightlines` takes a `Sight`, its constants the fallback; `LT_SIGHT_ONE_EYE` (INFO) says when a run's crew "
    "and enemy sight from two heights, which one eye cannot model. Its nine tests, a 92 m street with a 1.4 m crate "
    "through `advise_configuration`: on 0.229.0 three fail on behaviour (a contract's 2.05 m character and a brief's "
    "taller body leave the crate called cover; the one-eye note never given), two on the new names, four guards pass; "
    "the suite 2,591 collected, 2,576 passed, exit 0. Cold runs 9372 (0.229.0) and 9373 (0.230.0), restaurant_row_001 "
    "at seed 9003: 0 interventions each, findings 108 -> 108 -> 108, the same by code, candidate and message; the "
    "advisory ran in every Laser Tag job (`LT_OPENING_STANDOFF` 3, `LT_STOREY_UNSEEN` 3, `LT_MARKER_OFF_FLOOR` 1) and "
    "drew no open sightline under either crossing, so the level cannot show the move; 9373's three staged scenarios "
    "byte for byte 9372's (`patches/lf_sight_contract/cold_compare.out.txt`). LEFT: the contract's `sightlines` note "
    "still says \"Lot still carries 1.2\", which Lot does not; it rides Deli Counter's next change. Filed beside it, "
    "292. Earlier status kept: " + OLD289[len("*STATUS: "):])

ITEM292 = (
    "*STATUS: OPEN 2026-10-21 -- found shipping Level Factory 0.230.0 (roadmap 289); not started.*\n\n"
    "**292. The contract's body reaches the crew in a run and not the enemy.** "
    "`level_factory/adapters/laser_tag/__init__.py`'s `_FIELDS` writes `characters.player`'s radius, height, eye, "
    "walk speed, step-up and chest from `deli_counter/agent_contract.json` into the run's scenario (roadmap 123), and "
    "nothing more: `enemy_eye_height_m` is written from `_STOCK_SCENARIO`'s 1.6 whatever the contract states. The "
    "contract states it twice -- its NPCs share the player's metrics until a distinct class ships "
    "(`characters.npc_standard`), and `sightlines.enemy_sight_height_m` is 1.6 -- and the seam reads neither. A studio "
    "stating a 2.05 m character with a 1.85 m eye and a 1.15 m chest gets a crew sighting from 1.85 m against enemies "
    "sighting from 1.6, so the evaluator's lines cross at 1.42 m (`Engagement.cover_break_height`) where the crew's "
    "body alone crosses at 1.5; Level Factory 0.230.0's `LT_SIGHT_ONE_EYE` says so in the advisory. Laser Tag exposes "
    "the enemy's eye and no enemy radius or height (`LT_TestScenario.gd`), so the enemy's body size follows nothing. "
    "**What would close it:** which of the contract's two statements governs the enemy's eye settled in the contract, "
    "the other derived from it or removed; the seam writing the enemy's eye from it, with a test like roadmap 123's "
    "that one stated body moves both sides; the enemy's body size, if the evaluation is to follow it, one bounded "
    "Laser Tag change (the walker's rule for Laser Tag).\n")

PATCH = '''"""Roadmap 289: the sightline advisory sights from the body the run fields (Level Factory 0.229.0 and 0.230.0, cold
runs 9372 and 9373) -- NARROWED; and 292 filed, the contract's body reaching the crew and not the enemy. Copied from
`patch_roadmap_288_reserved_routes.py`'s status half and `patch_roadmap_guides_2026_10_21.py`'s append half: replaces
289's status block (the paragraph directly above its heading, asserted to be the one this was written against) with
one that keeps it after "Earlier status kept:", and appends 292 after the last item (asserted to be 291). The index is
NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_289_sight_contract.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_289 = %r
STATUS_289_OLD = %r
STATUS_289_NEW = %r
ITEM_292 = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if STATUS_289_NEW[:80] in text or "\\n**292. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_289) != 1:
        raise SystemExit("REFUSED: 289's heading is not there once; nothing written")
    h = text.find(HEADING_289)
    s = text.rindex("\\n\\n", 0, h) + 2
    if text[s:h] != STATUS_289_OLD:
        raise SystemExit("REFUSED: 289's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_289_NEW + text[h:]
    if text.count(STATUS_289_NEW + HEADING_289) != 1:
        raise SystemExit("REFUSED: 289's status no longer adjoins its heading; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 291 or heads[-1] != 291:
        raise SystemExit("REFUSED: the last item is not 291; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + "\\n" + ITEM_292
    if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*292\\. ", text)) != 1:
        raise SystemExit("REFUSED: item 292's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 289: NARROWED, the earlier status kept; 292 appended; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (H289, OLD289, NEW289, ITEM292)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
