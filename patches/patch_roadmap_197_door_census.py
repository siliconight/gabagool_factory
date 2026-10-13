"""Roadmap 197, 2026-10-13: the door clause measured across the library -- `docs/findings/door_widths/`, a decision
for the walker with three options. 197's status gains the census in its "Left" sentence. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_197_door_census.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("so whether the doors widen or the clearance is re-derived is a decision, and a re-derivation moves every "
       "aisle and landing built from it.*")
NEW = ("so whether the doors widen or the clearance is re-derived is a decision, and a re-derivation moves every "
       "aisle and landing built from it. Measured across the library on 2026-10-13 (`docs/findings/door_widths/`): "
       "200 enterable doors under 1.25 m in 32 of 132 buildings, 13 at 1.0, 74 at 1.1 and 113 at 1.2 -- 47 of "
       "those width-less, built at Deli Counter's own 1.2 m default -- and none under the formula's 1.00; the "
       "decision, with its three options, is the walker's.*")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "docs/findings/door_widths/" not in text, "already applied"
    assert text.count(OLD) == 1, ("197's clause not found once", text.count(OLD))
    text = text.replace(OLD, NEW)
    h = text.find("\n\n**197. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and NEW in text[s:h], "197's status does not sit directly above its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 197: the census in its status; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
