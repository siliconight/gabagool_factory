"""Level Factory 0.143.0: the Empties, merged one mesh a side per material
(roadmap 182). See `lf_empty_merge/CHANGELOG_0.143.0.md`.

Adds:
  packages/exporting/merge_empties.py   which scenes, the run, the report check
  assets/godot/merge_empties.gd         the merge itself
Anchored edits (every anchor once; refuses on a miss):
  packages/exporting/export.py   ExportMergeError; the merge, after the
                                 occluder bake and before the light bake
Copies the test; CHANGELOG and VERSION.

    python patch_lf_empty_merge.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_empty_merge"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


ERR_OLD = '''class ExportOccluderError(RuntimeError):
    """The package's occluders could not be measured, or the culling flag and
    the occluders that shipped do not agree."""
'''
ERR_NEW = '''class ExportOccluderError(RuntimeError):
    """The package's occluders could not be measured, or the culling flag and
    the occluders that shipped do not agree."""


class ExportMergeError(RuntimeError):
    """The Empties' merge ran and its report could not be believed (0.143.0,
    roadmap 182): `packages/exporting/merge_empties.check` says which."""
'''

STEP_OLD = '''        print("[export] WARNING no occluders in this package: %s" % exc)
        print("[export]   occlusion culling stays OFF in project.godot; "
              "the package is consistent and buys nothing from the culler")

    # THE LIGHT BAKE (0.131.0), opt-in.'''
STEP_NEW = '''        print("[export] WARNING no occluders in this package: %s" % exc)
        print("[export]   occlusion culling stays OFF in project.godot; "
              "the package is consistent and buys nothing from the culler")

    # THE EMPTIES, MERGED ONE MESH A SIDE PER MATERIAL (0.143.0, roadmap 182).
    # After the occluder bake, whose boxes were measured on the modules and are
    # world-space, so they stay true of the merged geometry; before the light
    # bake, whose users are node paths -- the merged meshes are the users, and
    # arrive unwrapped. Needs the import cache, as both do. Without a Godot the
    # package keeps its per-module Empties: consistent, and merely slower.
    # With one, a merge whose report cannot be believed fails the build, as
    # the occluder bake does.
    from packages.exporting.merge_empties import MergeError
    from packages.exporting.merge_empties import merge as _merge_empties
    if godot_executable:
        try:
            mreport = _merge_empties(export_dir, godot_executable)
        except MergeError as exc:
            drop_cache(export_dir)
            raise ExportMergeError(
                "the Empties' merge failed and this build had a Godot to run "
                "it with: %s\\n  report: %s" % (exc, export_dir / "merge_empties.json"))
        rows = mreport.get("scenes") or []
        if rows:
            print("[export] Empties merged: %d scene(s), %d mesh(es) of %d surface(s) "
                  "-> %d merged mesh(es), %d collider(s) kept"
                  % (len(rows), sum(r["meshes_in"] for r in rows),
                     sum(r["surfaces_in"] for r in rows),
                     sum(r["merged"] for r in rows), sum(r["colliders"] for r in rows)))

    # THE LIGHT BAKE (0.131.0), opt-in.'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.142.0"
    for new in (LF / "packages" / "exporting" / "merge_empties.py",
                LF / "assets" / "godot" / "merge_empties.gd"):
        assert not new.exists(), new
    shutil.copyfile(SRC / "merge_empties.py", LF / "packages" / "exporting" / "merge_empties.py")
    shutil.copyfile(SRC / "merge_empties.gd", LF / "assets" / "godot" / "merge_empties.gd")
    _edit(LF / "packages" / "exporting" / "export.py", [(ERR_OLD, ERR_NEW), (STEP_OLD, STEP_NEW)])
    shutil.copyfile(SRC / "test_merge_empties.py", LF / "tests" / "unit" / "test_merge_empties.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.143.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.143.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.143.0")


if __name__ == "__main__":
    main()
