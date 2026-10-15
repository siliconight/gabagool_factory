"""Roadmap 56 CLOSED: answered by Level Factory 0.87.0 and re-measured 2026-10-15
(`docs/findings/open_items_remeasure/`). Replaces 56's four-line status block (asserted once). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_56_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("*STATUS: OPEN 2026-08-23 -- MEASURED at discovery, unworked. Found by item\n54's closing instrument on "
              "its first honest run and recorded here the same\nday, because \"the roadmap already knew\" (item 39's "
              "epitaph) is only true of\nfindings that get written down*")
HEADING = ("\n\n**56. The global light budget is derived from scene text, and the running\nlevel has twice as many "
           "lights as the number it was given.**")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- the cap counts what runs, since Level Factory 0.87.0, re-measured "
    "(`docs/findings/open_items_remeasure/`). The Lux driver counts every Light3D in the running tree after its "
    "last bake and writes `lux.quality.json[\"lights_in_tree\"]`, and `package_light_budget` writes "
    "`max_renderable_lights` as the larger of the scene-text count and that census (0.87.0's entry cites this "
    "item); `test_project_godot_agreement.py` pins the cap to the package's count and the preview's project to "
    "the export's. Cold runs 9308, 9313 and 9314 each record 239 (205 fixture, 19 daylight, 14 club) and write "
    "239; the applied scene declares 238, the spawner's rigs packed into it; the perf harness's own census of "
    "9308's running tree, an instrument the driver does not share, counts 238 positional lights -- inside the "
    "cap, where this item's package held 272 against 136. The check it asked for holds by construction, the cap "
    "never below the driver's count, with the harness as the independent reading; nothing refuses an export on "
    "the comparison, because the only light that could exceed the cap at run time is one the gameplay layer "
    "spawns, outside the package by contract.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD)
    assert i >= 0 and text.count(STATUS_OLD) == 1, "56's status block not found once"
    k = i + len(STATUS_OLD)
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "56's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 56 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
