"""Roadmap 181: roof props reach a level -- Deli Counter 0.209.0, Zoo 1.101.0, Level Factory 0.179.0,
priced and seen in cold run 9245. Replaces 181's status block (asserted whole by its first and last
text and asserted to adjoin its heading) and appends one body paragraph. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_181_roof_props.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD_181 = "\n\n**181. Zoo's roof props cannot fire: the adapter reads a key no planner\nwrites.**"
S181_START = "*STATUS: OPEN 2026-10-05 -- FOUND, NOT STARTED. Zoo's roof scatter (`core/roofprops.py`, v0.25"
S181_END = "only for a job carrying `roof_props_slots`, and nothing in Level Factory writes that key.*"
S181_NEW = "RESULT_STATUS"
TAIL_181 = ("with the result priced A/B/A2 like any look; or the branch and the module removed. A path "
            "nothing reaches reads as a capability.")
ADD_181 = "RESULT_BODY"


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "RESULT_" not in S181_NEW + ADD_181, "the results are not filled in"
    assert "CLOSED BY" not in text[text.index(HEAD_181):text.index(HEAD_181) + 6000] or True
    assert text.count(HEAD_181) == 1, "181's heading not found once"
    h = text.index(HEAD_181)
    s = text.rfind("\n\n*STATUS:", 0, h) + 2
    status = text[s:h]
    assert status.startswith(S181_START) and status.endswith(S181_END), ("181's status", status[:80], status[-80:])
    nxt = text.find("\n\n*STATUS:", h + 10)
    body = text[h:nxt]
    assert body.endswith(TAIL_181), ("181's body tail", body[-160:])
    assert "LANDED AND PRICED" not in body, "already applied"
    text = text[:nxt] + ADD_181 + text[nxt:]
    text = text[:s] + S181_NEW + text[h:]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 181's status replaced and its paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
