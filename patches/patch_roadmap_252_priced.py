"""Roadmap 252 NARROWED: the backdrop's ground priced, and Level Factory 0.215.0 ships it unshaded. Replaces 252's
status block (asserted once). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_252_priced.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. Level Factory 0.211.0's ground under "
                   "the backdrop shipped as \"one draw\"")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- PRICED, and the cheap version ships. On cold run 9308's package against itself "
    "with the node removed, two controls, 53 headings (`docs/findings/walk_2026-10-14/`, \"The ground's price\"): "
    "the shaded ground as 0.211.0 shipped it costs +1 to +7 draws a heading (+2.5 on the mean) and at the heaviest "
    "heading +6 draws and +7.20 ms on the p95 against a 0.40 ms noise floor, nine of 53 headings beyond the "
    "controls' spread; the same plane unshaded costs +1 draw everywhere and at most +0.52 ms (+0.04 on the median, "
    "an 0.08 ms floor). At the walker's spot, from 26 m up and from the east elevation the two read the same in "
    "this evening level (`ground_frames/ground_sheet.png`). Level Factory 0.215.0 writes the ground unshaded, byte "
    "for byte the priced arm's material (`patches/patch_lf_ground_unshaded.py`, proven on a copy). Left: a cold run "
    "whose package carries `shading_mode = 0` on the ground and nothing else moved, which closes it; the look by "
    "day, unmeasured (9308 is evening; neither arm takes the baked sun); and the walker's call to spend the shaded "
    "ground on a level when runtime data says its frame can.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "252's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    text = text[:i] + STATUS_NEW + text[j:]
    head = "\n\n**252. The backdrop's ground was shipped unpriced.**"
    k = text.find(STATUS_NEW)
    assert text[k + len(STATUS_NEW):].startswith(head), "252's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 252: status replaced; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
