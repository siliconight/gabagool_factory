"""Roadmap 222 NARROWED: the streetlight shadow selftest's cap control passes again, 7 runs of 7.

Replaces 222's status block and adds the measurement to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_222_probes.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- Lux's windowed `streetlight_shadow_selftest` fails its on-axis "
    "control on 0.71.0 and 0.72.0 alike, run alone with the GPU idle: the cap 5 mm under an "
    "on-axis lamp leaves the pool at 0.447 against 0.459 unshadowed, where the control wants "
    "under a tenth. 0.71.0's record (2026-10-09) has the test passing. Cause not established.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- it does not fail now: seven runs from 04:30 the same "
    "night, six on a copy of Lux 0.72.0 and one in the repo, all read the cap control at 0.001 "
    "against 0.459 and PASS, on the same binary and driver (`docs/findings/"
    "streetlight_shadow_control/`). Two probes over a bare shaft show the control's own setting "
    "(5 mm, bias 0.03) blacks the pool on its first read after the shadow is switched on. What "
    "differed during the two failing runs is not known; next time it fails, keep the frame and "
    "the window's state.*\n"
)

BODY_ANCHOR = (
    "Until it is settled, this test's PLACED result -- the pool keeps 0.8 of itself -- stands on a "
    "control that cannot currently fail the way it is meant to: the slab control still proves "
    "shadows draw, but not that the cap's 5 mm can be seen.\n"
)
PROOF = (
    "\n**MEASURED, 2026-10-10 from 04:30** (`docs/findings/streetlight_shadow_control/`).\n"
    "- **The selftest, unchanged, seven times:** five in a row and one more on a working-tree "
    "copy of Lux 0.72.0, and one in the Lux repo, clean before and after. Every run printed "
    "`placed 0.453 unshadowed 0.459 on the axis at the lens 0.001 under a slab 0.000` and "
    "PASS, with Godot 4.7 stable and NVIDIA 616.56.\n"
    "- **`shadow_gap_probe.gd`:** the selftest's lamp from Lux's own loader over a bare 0.06 m "
    "shaft, its cap 5 mm to 30 cm under the lamp, at biases 0 to 0.10. At 5 mm and bias 0.03, "
    "the control's own setting, the pool reads 0.001. At 10 and 30 cm the pool is partly lit at "
    "every bias (0.185, 0.419), as the narrowing cone says it should be. At bias 0.00 and gaps "
    "of 2 cm or less no shadow is drawn at all (0.447), and at the pole's 0.10 a 5 mm cap lets "
    "0.081 through, which is why the control runs at 0.03.\n"
    "- **`shadow_gap_probe2.gd`, refuting a staleness reading.** The control is the selftest's "
    "first read after `shadow_enabled = true`, so the probe read twice at each setting. Bias "
    "0.03 is black on its first read after switching on, and bias 0.00's lost shadow is lost "
    "on both reads. The bias decides, not the order.\n"
    "\n"
    "So the control can fail the way it is meant to, and today it passes. Why it read 0.447 "
    "twice earlier that night, on unchanged code, is not established. Not recorded then, and "
    "worth keeping the next time: the frame, and whether the window was covered, minimised or "
    "on a sleeping display.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for name, anchor in (("status", OLD_STATUS), ("body", BODY_ANCHOR)):
        n = text.count(anchor)
        assert n == 1, (name, "anchor matches", n, "times")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_ANCHOR, BODY_ANCHOR + PROOF)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**222. "), "222's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 222: NARROWED, the control passes again")


if __name__ == "__main__":
    main()
