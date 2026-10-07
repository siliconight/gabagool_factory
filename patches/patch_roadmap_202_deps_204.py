"""Roadmap: the walker's dependency bar on item 202 (a consumer installs Blender
and Godot, nothing else), measured; and item 204, the package's anchors.

    python patch_roadmap_202_deps_204.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_201_close_203.py left it
(1,250,643 bytes, LF, as read 2026-10-07): 202's status line, 202's OPEN
DECISIONS heading, and 203's last line (the file's end). Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_202_HEAD = ("*STATUS: OPEN 2026-10-07 -- measured, not started: a stranger's first hour with the factory "
                   "package would cost interventions before any level is built.")
STATUS_202_HEAD_NEW = ("*STATUS: OPEN 2026-10-07 -- measured, not started. The walker's bar: a consumer installs "
                       "Blender and Godot and nothing else. Today a stranger's first hour with the factory package "
                       "would cost interventions before any level is built.")

DECISIONS = "**OPEN DECISIONS (the walker's).**\n"
DEPS = r"""**THE BAR: BLENDER AND GODOT, NOTHING ELSE** (the walker, 2026-10-07: "My goal is for consumers of Gabagool Factory to only need Blender, Godot and then to be able to make great looking fun to play levels"). Measured the same day:
- **Blender already ships the interpreter.** Blender 5.1.1's bundled Python (`<blender>/5.1/python/bin/python.exe`) is 3.13.9 and carries numpy 2.3.4, pip 25.2, pytest 9.1.1 and requests. Level Factory asks for >= 3.11 and needs no third-party package at runtime; its CLI starts, and `verify-manifest` runs, under that interpreter unchanged.
- **Five packages are missing from it:** Pillow, pygltflib, jsonschema, PyYAML and cairosvg -- exactly the set the seven repos without a `pyproject.toml` import (Pillow in Deli Counter, Zoo, Lux, Pixelcoat, Patina and root tools; pygltflib in Deli Counter and Patina; jsonschema in Deli Counter and Patina; PyYAML and cairosvg in one Deli Counter file each). Each is a candidate to drop, to vendor (pygltflib, jsonschema and PyYAML are pure Python), or to install into Blender's own Python with its bundled pip at setup.
- **So the bar is two installs plus one discovery step:** find Blender and Godot (the resolution chain every tool already uses), run every factory tool on Blender's interpreter, and fill `tools.local.json` from that -- no separate Python, no hand-edited paths.
- **Not yet measured:** the suites of every repo under Blender's interpreter (pytest is there to run them), and which of the five packages sit on the level-making path rather than on developer tools.

"""

TAIL_203 = ("- Whether Laser Tag's route finding should be major below some completion short of zero is Laser Tag's "
            "call; the 8% case is the evidence for it.\n")

ADD = r"""
*STATUS: OPEN 2026-10-07 -- found reading cold run 9194's package: `gameplay_anchors.json`, the list the game layer receives, marks no objective as the score and names no anchor's building (5 objective anchors, 3 extractions, `objective: ""` and `source_building: ""` on all 64), and on that bank level its `deli_counter:*` anchors -- listed first -- are the mission's own generated shell, which a library lot never places, in that shell's local frame. The first two facts hold on 9189, 9191 and 9193's packages too.*

**204. The package does not say where the score is.** Found 2026-10-07 while framing cold run 9194's stair foot: `tools/look_shots.py` takes the first anchor of each type from the package's `gameplay_anchors.json`, and its "objective" camera stood at (4.5, -1.5, 2.25), near the spawn building, while the score's vault is at (-54, -3.9, -12).

**WHAT WAS MEASURED** (9194, `workspaces/cold-9194-ws/.level_factory/exports/LF_bank_block_001.portable-godot/gameplay_anchors.json`, 64 anchors):
- **Five objective anchors, none marked.** In order: `deli_counter:crack_vault` (4.5, -3.1, 2.25), `deli_counter:grab_drawers` (0, 0.5, 2.0), `lot:A_17` (18.6, 4.2, -10.0), `lot:A_24` (62, 0, 0), and the score's own vault, `lot:A_6` (-54, -3.9, -12.0), last. Every anchor carries `"objective": ""` and `"source_building": ""`.
- **The `deli_counter:*` anchors are a building that is not in the level.** crack_vault, grab_drawers and the crew spawn `deli_counter:A` (-2, 0, 14) are the generated shell `lf_bank_block_001_9054`'s `OBJECTIVE_CRACK_VAULT` (x 4.5, y -2.25, z -3.1, room `vault_room_east`), `OBJECTIVE_GRAB_DRAWERS` and `CREW_SPAWN_A` -- its local coordinates mapped to Godot with no site placement. The lot is library buildings (bank_branch_a04, casino_a03, strip_retail_a02); bank_branch_a04 has no `vault_room_east` and no `lobby`.
- **Three extractions, none marked.** `lot:EXIT` (6, 0, 13) first, by the spawn building; the site spec's extraction, b2's street point (52, 0, 13), is `lot:STREET_25`, last.
- **The earlier packages:** 9189 and 9193 (restaurant_row_001, 116 anchors, 9 objectives) and 9191 (deli_001, 171, 12) mark no objective and name no building either. Whether their `deli_counter:*` anchors are placed buildings' (deli_a01 is a Deli Counter building on that lot) or the unplaced shell's was not checked.

**WHY IT MATTERS.** The package is the deliverable, and the game layer is somebody else's code. Roadmap 201 made the score the brief's building for Lot, the walk scene and Laser Tag; the package still cannot tell its consumer which of five objectives that is, and on a library lot it offers objectives from a building that is not there, first.

**NEXT.**
- Read Level Factory's dispatch staging (`packages/staging/dispatch_inputs.py` and its caller) before deciding anything: where it takes Deli Counter anchors from on a library lot, and in which frame.
- Mark the score: the objective anchors of the site spec's `objective` building carry the objective, and the site spec's extraction is marked as such.
- Name each anchor's building (`source_building`).
- A test on a library-lot package: no anchor from a shell the lot does not place.
"""


def main():
    data = RM.read_bytes()
    assert len(data) == 1250643, "PIPELINE_ROADMAP.md is %d bytes, read at 1,250,643" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(STATUS_202_HEAD) == 1, text.count(STATUS_202_HEAD)
    assert text.count(DECISIONS) == 1, text.count(DECISIONS)
    assert text.endswith(TAIL_203) and text.count(TAIL_203) == 1, "the tail anchor is not the file's end"
    text = text.replace(STATUS_202_HEAD, STATUS_202_HEAD_NEW).replace(DECISIONS, DEPS + DECISIONS) + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 202 carries the dependency bar, 204 appended")


if __name__ == "__main__":
    main()
