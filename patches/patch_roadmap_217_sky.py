"""Roadmap 217: the sky in the bake, answered. The walker, 2026-10-09: "yes bake
the sky in" -- Level Factory 0.164.0 (`patch_lf_bake_sky.py`).

Two anchored edits, each matched exactly once: item 217's status line, whole,
and its walker's-call bullet on the sky. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

STATUS_OLD = (
    "*STATUS: NARROWED 2026-10-09 -- the instruments exist, and the street lamps are dark by day. "
    "Root tools `light_breakdown.py`, `light_check.py` and `lux_rebake.py` measure a level by source, "
    "by room and street against named floors, and at any slot by an exact re-bake. Lux 0.71.0 darkens "
    "poles and wall packs under the four day presets, proven in cold run 9214 (0 interventions): a hidden "
    "lamp is not baked (wall pack 002's wall 32.5, against 48.0 with the lamps forced on), and the lamps "
    "move the check's 23 stations by 0.2 or less. The walker's lighting spec, set against the code, found "
    "three gaps: the bake holds no sky, fluorescents scale with the slot, and Heavy Rain's shadowless sun "
    "lights rooms through their roofs, which is why 12 of 16 interior stations outshine its street "
    "(objective 67.8 to 39.9 with the sun off; the fluorescent boost at 1.0 moves rooms 0 to 11.8). The "
    "same level as a clear afternoon has 2. That shadow was refused on price in Lux 0.38.0; on it, the "
    "rooms fall 5.6 to 31.6 and 12 WARNs become 7, and the price predates the light bake and the merges. "
    "The sky in the bake lifts a clear afternoon's street +15.1 and +21.4 at no run-time cost. Open: the "
    "walker's calls on Heavy Rain's sun, the sky in the bake, and where the night boost lives; morning and "
    "noon presets.*\n"
)
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-09 -- the instruments exist, the street lamps are dark by day, and the sky "
    "is in the bake. Root tools `light_breakdown.py`, `light_check.py` and `lux_rebake.py` measure a level "
    "by source, by room and street against named floors, and at any slot by an exact re-bake. Lux 0.71.0 "
    "darkens poles and wall packs under the four day presets, proven in cold run 9214 (0 interventions): a "
    "hidden lamp is not baked (wall pack 002's wall 32.5, against 48.0 with the lamps forced on), and the "
    "lamps move the check's 23 stations by 0.2 or less. The walker's lighting spec, set against the code, "
    "found three gaps: the bake held no sky, fluorescents scale with the slot, and Heavy Rain's shadowless "
    "sun lights rooms through their roofs, which is why 12 of 16 interior stations outshine its street "
    "(objective 67.8 to 39.9 with the sun off; the fluorescent boost at 1.0 moves rooms 0 to 11.8). The "
    "same level as a clear afternoon has 2. That shadow was refused on price in Lux 0.38.0; on it, the "
    "rooms fall 5.6 to 31.6 and 12 WARNs become 7, and the price predates the light bake and the merges. "
    "Level Factory 0.164.0 bakes the sky at the walker's word (\"yes bake the sky in\"): re-baked, a clear "
    "afternoon's street rose +15.1 and +21.4, every room 1.2 or less at four slots, at no run-time cost; "
    "its cold run is next. Open: the walker's calls on Heavy Rain's sun and where the night boost lives; "
    "morning and noon presets.*\n"
)
CALL_OLD = (
    "- **The sky in the bake.** Level Factory's `environment_mode` 0 to 1 is one line. It is measured at "
    "four slots, it costs nothing at run time, and it does not touch the rooms. Recommended. The look is the "
    "call: shade on a clear afternoon goes from near black to blue-grey daylight.\n"
)
CALL_NEW = (
    "- **The sky in the bake: ANSWERED 2026-10-09,** \"yes bake the sky in\". Level Factory 0.164.0 "
    "(`patches/patch_lf_bake_sky.py`) bakes `environment_mode = 1`. `test_the_bake_takes_the_sky` fails on "
    "0.163.1. Not yet proven in a cold run. `tools/lux_rebake.py --bake-environment none` bakes as before, "
    "for a control.\n"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    for old in (STATUS_OLD, CALL_OLD):
        assert text.count(old) == 1, (text.count(old), old[:80])
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(CALL_OLD, CALL_NEW)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 217: the sky in the bake, answered")


if __name__ == "__main__":
    main()
