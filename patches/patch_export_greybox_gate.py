"""Wire the greybox-skin gate into the exporter, between the GLB reference
gate and the closure verdict.

Anchored: every anchor must match exactly once or this refuses to write.

WHY HERE. Above the closure verdict, for the same reason `glb_refs` is: the
scan file must be inside the package the verdict describes and inside the
manifest that lists it. Below the occluder bake, because the census reads the
IMPORTED scene and the bake is what guarantees an import cache exists.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "packages" / "exporting" / "export.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''class ExportWarmupError(RuntimeError):
'''

N1 = '''class ExportGreyboxSkinError(RuntimeError):
    """A themed package still draws greybox where theming claims to reach.

    Every other gate here measures traversal correctness or resource closure.
    This one measures whether the result reads as DESIGNED, which is the gap
    CLAUDE.md names: of the three problems found by actually playing a
    generated level, one was caught by an instrument and two by a person
    looking at the screen. The defect it was built from -- a bare `gb_floor`
    collar lining every ladder shaft and stairwell, 10.44 m2 over 8 openings
    on cold run 9070's package -- was found on a ladder, by the walker.

    Refuses on SLABS only; see `packages.exporting.greybox_skin` for the
    census that set that threshold and for what it deliberately only
    reports."""


class ExportWarmupError(RuntimeError):
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''    # 4.9 Resource-closure VERDICT'''

N2 = '''    # 4.87 DOES THIS THEMED PACKAGE STILL DRAW GREYBOX? See
    # `packages.exporting.greybox_skin`, which owns the verdict, and
    # `assets/godot/greybox_census.gd`, which owns the measurement.
    #
    # IN THE ENGINE, not over the GLBs: `zoo_worldskin.gd` is an import
    # post-processor, so a shipped GLB keeps its `gb_*` materials by design
    # and a glTF-level check would refuse every package ever built.
    #
    # ABOVE THE CLOSURE VERDICT, so `greybox_skin_scan.json` is inside the
    # package the verdict describes and inside the manifest that lists it --
    # the same reasoning as the GLB reference gate above, and the same
    # consequence: it must NOT be added to `_WRITTEN_AFTER_VERDICT`.
    #
    # ENFORCED ONLY WITH A GODOT TO RUN IT, matching the occluder bake. A
    # build with no engine cannot take this census, and a census not taken
    # must say so rather than read as a clean package.
    from packages.exporting import greybox_skin
    if godot_executable:
        try:
            gb_report = greybox_skin.measure(export_dir, godot_executable)
            print("[export] greybox skin: " + greybox_skin.summary(gb_report))
            greybox_skin.assert_skinned(export_dir, gb_report)
        except greybox_skin.GreyboxCensusError as exc:
            raise ExportGreyboxSkinError(
                "the greybox census failed and this build had a Godot to run "
                "it with: %s\\n  a package that cannot be measured must not "
                "be shipped claiming it was" % exc) from exc
        except greybox_skin.GreyboxSkinError as exc:
            raise ExportGreyboxSkinError(str(exc)) from exc
    else:
        print("[export] greybox skin: no Godot in this build, so the census "
              "was not taken and nothing is certified about it")

    # 4.9 Resource-closure VERDICT'''

EDITS = ((A1, N1), (A2, N2))


def main() -> None:
    data = TARGET.read_bytes()
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
