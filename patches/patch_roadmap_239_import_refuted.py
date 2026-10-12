"""Roadmap 239: the one-import plan, measured, applied to a real export, and REFUTED -- the light bake's
re-import of every model is load-bearing (the worldskin skins the models there). Adds the refutation
to 239's import item; one anchor asserted once, nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_import_refuted.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = ("Level Factory 0.182.0 applies them again after the last import and refuses a package that still "
       "lacks one.\n2. **The art leg")
NEW = ("Level Factory 0.182.0 applies them again after the last import and refuses a package that still "
       "lacks one. **REFUTED, KEPT: one import with the models' final settings as defaults.** Timed on "
       "stripped copies of cold run 9251's package, embedded images and lightmap UVs as the first pass's "
       "model defaults took the export's imports from 121.6 to 53.6 s with the sidecars it would ship "
       "unchanged; applied to a real re-export it FAILED the greybox-skin gate (105 slab surfaces left "
       "greybox, the Empties merged to 148 meshes instead of 236). The light bake's re-import of every "
       "model is where `zoo_worldskin.gd` skins them with the packs already imported -- load-bearing, and "
       "not visible in a sidecar (`patches/patch_lf_import_once.py` refuses to run). One import needs a "
       "worldskin that finds its packs without the textures imported first, judged on the gate, the merge "
       "and the bake, not on sidecars.\n2. **The art leg")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "REFUTED, KEPT: one import with the models' final settings" not in text, "already applied"
    assert text.count(OLD) == 1, ("239's import item", text.count(OLD))
    RM.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("roadmap: 239's refuted import plan recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
