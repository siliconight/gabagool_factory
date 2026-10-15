"""Roadmap 80 CLOSED, re-measured 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces 80's ten-line
status block (asserted once, from its first line to the line ending the block's `*`). The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_80_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-08-29 -- DELI COUNTER'S GUARANTEE SURVIVES THE ART PASS;\n"
HEADING = ("\n\n**80. Deli Counter's one-mesh-in-VRAM discipline is not carried any further\nthan the export, and the "
           "two pieces that would carry it are both dead code.**")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- its first two moves shipped and the third it placed last, re-measured "
    "(`docs/findings/open_items_remeasure/`). World-space UVs ship on every kit module: `zoo_worldskin.gd` is the "
    "modules' import script, applied at import and baked into the .scn, run by the package since Level Factory "
    "0.57.0 and in all 13 building folders of cold run 9314's package; `walk_themed.py` and its runtime flag are "
    "gone. MultiMesh carries the dressing and the backdrop: `dressing_scene` is called by `dressing_layer.py` and "
    "`backdrop_layer.py`, 4,439 instances of 4 meshes in 4 draws and 297 backdrop instances in 25 on 9314. The "
    "walls were not MultiMeshed -- the light-budget tension this item named -- and went the other way: Level "
    "Factory 0.143.0 (roadmap 182) merges an Empty's modules one mesh a side per material, 686 draws and 0.88 ms "
    "on cold run 9162's level against a 816-draw ceiling, trading the shared datablock for submissions by the "
    "measured rule that draw calls are the budget; the mission's buildings keep their instanced modules, and the "
    "per-mesh budget is read by what the renderer pairs (147's record). `instances.json` is still read by "
    "nothing, which this item placed third once the other two existed; the per-instance channel is roadmap "
    "76's question.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "80's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("NOBODY HAS PUT A FRAME TIME ON IT*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "80's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 80 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
