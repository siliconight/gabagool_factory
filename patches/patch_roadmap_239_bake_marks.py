"""Roadmap 239: Level Factory 0.187.0 (the light bake's lightmap requests in the export's second
import pass), measured by re-exporting cold run 9252 and in cold run 9253, and the correction of
the refuted one-import plan's cause, kept beside it. Three anchors, each asserted once, nothing
written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_bake_marks.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "Open: the light bake's and the sidecar step's imports, the walk copy's (91 s in 9252), the Lux "
     "job's staging and the work done for a cache hit before the cache is asked, the Blender builds' "
     "reproducibility, and the grader's step (4x against the game's 1/60 s, the walker's call).*",
     "Then the export again: Level Factory 0.187.0 asks for the lightmap UVs in the sidecar step's "
     "second pass, so the bake no longer imports every model a third time; cold run 9253: the export "
     "284 -> 241 s, the drive 9.7 minutes, no shared-texture pin lost, the Empties merged one mesh a "
     "side per material (236 -> 148). Open: the walk copy's import (88 s in 9253), the sidecar step's "
     "two passes, the Lux job's staging and the work done for a cache hit before the cache is asked, "
     "the Blender builds' reproducibility, and the grader's step (4x against the game's 1/60 s, the "
     "walker's call).*"),
    ("item 1's left",
     "Left: the lightmap UVs could be asked for in the sidecar step's second pass (the bake's first "
     "import gone, and with it the race below), the bake's second import is worth reading, and the "
     "walk copy imports the package from scratch again",
     "**The lightmap UVs in the sidecar step's second pass: Level Factory 0.187.0** "
     "(`docs/findings/grader_speed/uv_second_pass_probe.py`): re-exporting 9252, the export 277.6 -> "
     "238.4 s, the bake's import of every model 55.0 -> 5.0 s, no pin lost where the control lost 74, "
     "the greybox census, the occluders and the closure verdict identical; cold run 9253, the export "
     "284 -> 241 s and the drive 10.3 -> 9.7 minutes, 0 interventions. The bake's second import was "
     "cut by 0.183.0. Left: the walk copy imports the package from scratch again"),
    ("the correction",
     "judged on the gate, the merge and the bake, not on sidecars.\n2. **The art l",
     "judged on the gate, the merge and the bake, not on sidecars. **CORRECTED, KEPT (cold run 9251's "
     "import log).** Two parts of the above were wrong. The worldskin needs a building's floor module "
     "imported before its base, not the texture packs first: a model's FIRST import cannot promise it "
     "(pass one left 105 slab meshes greybox) and the second pass can. And the 148 merged meshes were "
     "not a failure: models that carry their lightmap UV when the Empties merge make one mesh a side "
     "per material, as the merge was written to (`merged_materials.py`: the same 148 groups, split into "
     "up to four meshes before); the 3,320 users are that merge, seen by the bake. Only the greybox "
     "gate's failure was real, and it was the first import's.\n2. **The art l"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**The lightmap UVs in the sidecar step's second pass: Level Factory 0.187.0**" not in text, \
        "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's 0.187.0, cold run 9253 and the correction recorded; now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
