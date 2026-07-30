"""Copy pack assets to the paths the scene actually references.

MEASURED, by the engine check added minutes earlier -- the first time anything
asked Godot to open a site pack:

    ERROR: Resource file not found: res://buildings/warehouse_a02.glb
    ERROR: res://ballpark_block.tscn:683 - Parse Error: [ext_resource]
           referenced non-existent resource at: res://buildings/warehouse_a02.glb
    PACK LOADS IN GODOT = False

In the walk scene this shows as three holes in the ground you fall through. The
ground plate is cut out under each building because buildings supply their own
floors (self_flooring); the buildings then fail to load; the holes remain.

THE CAUSE. lot.write_godot_scene with portable=True emits asset paths RELATIVE to
the scene file, deliberately -- that relativity is what lets the pack folder sit
at any path inside a consumer's project:

    rel = os.path.join(glb_dir, src)          # "buildings/warehouse_a02.glb"
    prefix = "" if portable else "res://"
    f'[ext_resource type="PackedScene" path="{prefix}{rel}" ...'

package.py then copies the assets like this:

    shutil.copy2(p, os.path.join(pack_dir, os.path.basename(src)))

os.path.basename flattens "buildings/warehouse_a02.glb" to
"warehouse_a02.glb", so every asset lands one directory above where the scene
looks for it. The scene is right and the copy is wrong. Copying to `src` instead
of `basename(src)` puts each asset where its own reference points.

This has been true of every site pack ever produced. It survived because a pack
was judged by its manifest, its deterministic zip and its sha256 -- three things
that are all perfectly happy to describe a pack that cannot load. The sibling
packager (deli_counter/portable_building.py) has run a headless engine check since
it was written; the site packager never did.

A SECOND DEFECT in the same run, also from the engine:

    WARNING: A navigation mesh that uses a cell_size of 0.10000000149012 was
    assigned to a navigation map set to a larger cell_size of 0.25.
    This mismatch in cell size can cause rasterization errors with navigation
    mesh edges on the navigation map.

The mesh is baked at the contract's nav_bake grid (0.10 / 0.15) and Godot's
project-wide navigation map defaults to 0.25 / 0.25. Nothing set them, so the
runtime map rasterises the baked mesh on a coarser grid than it was built for --
the class of defect that puts navmesh edges in the wrong place, which is what half
of this pass has been about. The walkable host project now sets both from the same
contract the bake reads, and PACK_README tells a consumer to do the same, because
the pack cannot set project settings in someone else's project.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
PKG = ROOT / "lot" / "package.py"

# --- 1. the copy ------------------------------------------------------------

COPY_OLD = '''    for src, p in resolved.items():
        shutil.copy2(p, os.path.join(pack_dir, os.path.basename(src)))
'''

COPY_NEW = '''    for src, p in resolved.items():
        # Copy to the asset's OWN relative path, not its basename. The scene
        # emits `path="buildings/x.glb"` relative to itself (that relativity is
        # what lets this folder sit at any path in a consumer's project), and
        # basename() flattened it to "x.glb" -- one directory above where the
        # scene looks. Every site pack ever built failed to load for this reason,
        # and a manifest, a deterministic zip and a sha256 all describe such a
        # pack without complaint. Only the engine notices.
        rel = str(src).replace("\\\\", "/").lstrip("/")
        if os.path.isabs(str(src)) or ".." in rel.split("/"):
            # The scene would have emitted this same odd path, so flattening it
            # here would not save the pack -- say so rather than quietly
            # producing something that cannot load.
            print(f"[package] ASSET PATH NOT PACK-RELATIVE: {src!r}. The scene "
                  f"references it as written, so the pack will not resolve it. "
                  f"Use a path relative to the site spec, like "
                  f"buildings/<name>.glb.")
            rel = os.path.basename(str(src))
        dest = os.path.join(pack_dir, *rel.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(p, dest)
'''

# --- 2. the navigation grid in the host project ------------------------------

PROJ_OLD = '''config/name="{name} (site pack walk)"
run/main_scene="res://{scene}"
{features}
[debug]'''

PROJ_NEW = '''config/name="{name} (site pack walk)"
run/main_scene="res://{scene}"
{features}
[navigation]

; The baked navmesh in this pack uses the agent contract's nav_bake grid. Godot's
; project-wide navigation map defaults to 0.25/0.25, and the engine warns that a
; map coarser than the mesh it carries "can cause rasterization errors with
; navigation mesh edges" -- edges in the wrong place, which is the whole class of
; defect a walk test exists to catch. A consumer dropping this pack into their own
; project has to set these there; the pack cannot set them for you.
3d/default_cell_size={cell_size}
3d/default_cell_height={cell_height}

[debug]'''

FMT_OLD = '''        f.write(_WALK_PROJECT.format(name=name, scene=scene,
                                     features=_godot_features(godot)))'''

FMT_NEW = '''        nav = lot._agent()["nav_bake"]
        f.write(_WALK_PROJECT.format(
            name=name, scene=scene, features=_godot_features(godot),
            cell_size=float(nav["cell_size_m"]),
            cell_height=float(nav["cell_height_m"])))'''

# --- 3. tell the consumer ---------------------------------------------------

README_ANCHOR = '''Open `ballpark_block_walk.tscn` and press F6'''


def _readme_addition(src):
    """The README is generated per-site, so anchor on the sentence, not a name."""
    import re
    m = re.search(r'Open `\{[^`]*\}_walk\.tscn` and press F6[^\n]*\n', src)
    return m


NAV_NOTE = '''
Set these in your project settings, or the navmesh in this pack is rasterised on
a coarser grid than it was baked for (Godot warns about it; it puts navmesh edges
in the wrong place):

    navigation/3d/default_cell_size   = {cell_size}
    navigation/3d/default_cell_height = {cell_height}
'''


def main() -> int:
    if not PKG.exists():
        raise SystemExit(f"missing {PKG}. Nothing written.")
    src = PKG.read_text(encoding="utf-8")
    if "_WALK_PROJECT" not in src:
        raise SystemExit("package.py has no --walkable support yet. Run "
                         "patch_package_walkable.py first. NOTHING WRITTEN.")

    done = []
    if "ASSET PATH NOT PACK-RELATIVE" in src:
        done.append("package.py: assets already copied to their relative paths")
    else:
        if src.count(COPY_OLD) != 1:
            raise SystemExit(f"package.py: the asset copy loop appears "
                             f"{src.count(COPY_OLD)} time(s), expected exactly "
                             f"1. NOTHING WRITTEN.")
        src = src.replace(COPY_OLD, COPY_NEW)
        done.append("package.py: assets copied to the paths the scene "
                    "references, not flattened")

    if "3d/default_cell_size" in src:
        done.append("package.py: host project already sets the navigation grid")
    else:
        for label, old in (("the host project template", PROJ_OLD),
                           ("the template format call", FMT_OLD)):
            if src.count(old) != 1:
                raise SystemExit(f"package.py: {label} appears "
                                 f"{src.count(old)} time(s), expected exactly "
                                 f"1. NOTHING WRITTEN.")
        src = src.replace(PROJ_OLD, PROJ_NEW).replace(FMT_OLD, FMT_NEW)
        done.append("package.py: host project sets the navigation cell size and "
                    "height from the contract")

    backup = PKG.with_suffix(".py.pre_paths")
    if not backup.exists():
        shutil.copy2(PKG, backup)
    PKG.write_text(src, encoding="utf-8")
    py_compile.compile(str(PKG), doraise=True)
    for line in done:
        print(f"  {line}")
    print(f"  compiles; previous file kept at {backup.name}")

    print("\n  Repackage and let the engine judge it:\n")
    print("    cd lot")
    print("    python package.py specs\\ballpark_block\\ballpark_block_site.json "
          "--walkable \\")
    print('      --check "C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe"')
    print("\n  Expect `PACK LOADS IN GODOT = True` and 0 error lines. The three "
          "holes in\n  the ground are the buildings failing to load, so they "
          "should close with it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
