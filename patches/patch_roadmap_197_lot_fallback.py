"""Roadmap 197, 2026-10-13: Lot 0.120.2 fixed the refuted cell the door finding found in Lot -- one body paragraph
at the end of 197, its status untouched (the door decision is still the walker's). The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_197_lot_fallback.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
#: the roadmap as read before this was written; a different file was edited since, and is not patched blind
SHA16 = "804e4ace658d3d70"

#: the end of 197's body and the start of 198's status, which sits directly above 198's heading
ANCHOR = "\n\n*STATUS: CLOSED 2026-10-07 -- cold run 9193 (0 interventions, findings 64 -> 64"
NEW = ("\n\n**FOUND WHILE MEASURING THE DOORS, FIXED: Lot 0.120.2, 2026-10-13** (`docs/findings/door_widths/README.md`, "
       "`lot/CHANGELOG.md`). Lot carried the refuted cell as well: `site_cover._NAV_BAKE_FALLBACK` said `cell_size_m` "
       "0.15 against the contract's 0.1 -- the contract's own value when it was written, 2026-07-27, refuted two days "
       "later, refreshed in `lot._AGENT_DEFAULTS` the day after and not here -- and `LOT_COVER_PINCH` stated the "
       "fallback's 1.2 m over lanes `plan_cover` measured at the contract's 1.0 m, because `lot.py` hands it the "
       "contract's bake. The fallback is 0.1, `CoverPlan.passable_gap` carries the threshold the read-back used and "
       "the message states it, and `lot/tests/test_cover_fallback.py` holds both copies Lot carries equal to the "
       "contract. Built sites do not move: cold run 9284's club_block_014 seed_9080 Lot job, replayed from its "
       "`job.log`, builds 53 of 53 files identical before and after and to the cold run's own "
       "(`docs/findings/door_widths/cover_fallback_ab.py`), and none of the 261 Lot job logs on this disk carried a "
       "`LOT_COVER_PINCH`. It touches neither the doors nor the contract's `clearances.derivation` (at Deli Counter "
       "0.213.0 still the formula at 0.15): that decision is the walker's, as the status says.")


def _status_above(text, heading):
    """The status block directly above ``heading``, and nothing between them but a blank line."""
    h = text.find("\n\n" + heading)
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and s > 0, heading
    block = text[s + 2:h]
    assert "\n\n" not in block, (heading, "a paragraph sits between its status and its heading")
    return block


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA16, ("the roadmap changed since this was written", got)
    text = raw.decode("utf-8")
    assert "Lot 0.120.2" not in text, "already applied"
    assert not re.search(r"^\*\*\d", NEW.lstrip("\n"), re.M), "a body line starting **<digits> parses as an item"
    assert text.count(ANCHOR) == 1, ("198's status not found once", text.count(ANCHOR))
    at = text.find(ANCHOR)
    assert text.find("\n\n**197. ") < at < text.find("\n\n**198. "), "the anchor is not between 197 and 198"
    before_197, before_198 = _status_above(text, "**197. "), _status_above(text, "**198. ")
    text = text[:at] + NEW + text[at:]
    assert _status_above(text, "**197. ") == before_197 and _status_above(text, "**198. ") == before_198
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 197: Lot 0.120.2 in its body; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
