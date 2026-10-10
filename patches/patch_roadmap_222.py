"""Roadmap 222: a Lux selftest's control fails on an unchanged Lux.

Item 222 is appended after 221, the file's last item, its status directly above its heading,
refused if a 222 exists. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"
LAST = "3. then price the merge before and after, at stations that face one side of a building.\n"

ITEM_222 = (
    "\n"
    "*STATUS: OPEN 2026-10-10 -- Lux's windowed `streetlight_shadow_selftest` fails its on-axis "
    "control on 0.71.0 and 0.72.0 alike, run alone with the GPU idle: the cap 5 mm under an "
    "on-axis lamp leaves the pool at 0.447 against 0.459 unshadowed, where the control wants under "
    "a tenth. 0.71.0's record (2026-10-09) has the test passing. Cause not established.*\n"
    "\n"
    "**222. A shadow control that stopped seeing its shadow.** `lux/tools/"
    "streetlight_shadow_selftest.gd` holds the streetlight's lamp beside its pole (Lux 0.65.0). Its "
    "two controls prove the instrument sees a shadow at all:\n"
    "- **a slab a metre under the lamp blacks the pool.** It still does: 0.000.\n"
    "- **the lamp on the pole's axis, at the lens point, is blacked by the shaft's cap.** It is run "
    "at the engine's bias 0.03, because at the pole's 0.1 the 5 mm cap is swallowed by the bias.\n"
    "\n"
    "Measured 2026-10-10, ground under the pole 9 m off, the test's own figures: placed 0.453, "
    "unshadowed 0.459, on the axis at the lens 0.447, under a slab 0.000. The same numbers came back "
    "on Lux 0.71.0 HEAD and on 0.72.0's draft, the GPU idle both times. 0.71.0's changelog says all "
    "20 selftests passed when it shipped, this one windowed among them.\n"
    "\n"
    "So the code under test did not change, and the result did. Not yet looked at: the NVIDIA driver "
    "(look_shots' manifests read 616.56 tonight), the window's state when the test opens it, and "
    "whether the pole the test builds still matches the Zoo streetlight it was written against. "
    "Until it is settled, this test's PLACED result -- the pool keeps 0.8 of itself -- stands on a "
    "control that cannot currently fail the way it is meant to: the slab control still proves "
    "shadows draw, but not that the cap's 5 mm can be seen.\n"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**222." not in text, "item 222 exists"
    assert text.endswith(LAST) and text.count(LAST) == 1, "221 does not end the file"
    ROADMAP.write_bytes((text + ITEM_222).encode("utf-8"))
    print("roadmap 222 filed")


if __name__ == "__main__":
    main()
