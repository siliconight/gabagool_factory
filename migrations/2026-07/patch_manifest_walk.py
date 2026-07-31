"""The pack manifest lists a flat directory. The pack is no longer flat.

MEASURED, immediately after patch_pack_paths.py:

    File "lot/package.py", line 433, in build_pack
      manifest["files"][fn] = {"sha256": _sha256(full),
    PermissionError: [Errno 13] Permission denied:
      '...\\lot\\dist\\ballpark_block_pack\\buildings'

The manifest is built with

    for fn in sorted(os.listdir(pack_dir)):
        full = os.path.join(pack_dir, fn)
        manifest["files"][fn] = {"sha256": _sha256(full), ...}

os.listdir returns names, not files, and every name used to be a file because the
pack was flat. Copying assets to their real relative paths introduced a
`buildings/` directory, and open(directory, "rb") is PermissionError on Windows.

MY DEFECT, and worth naming precisely: the previous patch changed the pack's shape
and I checked that the copy produced the right layout without checking what else
read that layout. A directory listing that assumes every entry is a file is the
same class of assumption as a byte count that assumes no CRLF -- correct until the
thing underneath it changes shape.

THE FIX. Walk the tree and record POSIX-style relative paths, so the manifest
describes the pack as the scene addresses it: "buildings/warehouse_a02.glb", not
"warehouse_a02.glb". That also makes the manifest agree with the deterministic zip,
which has always stored nested paths, and it stays correct for any future nesting
rather than for exactly one level of it.

Skips pack.manifest.json itself, as the flat version did by writing it afterwards,
and keeps the sort so the manifest remains byte-stable for identical inputs.

Asserts its target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
PKG = ROOT / "lot" / "package.py"

OLD = '''    for fn in sorted(os.listdir(pack_dir)):
        full = os.path.join(pack_dir, fn)
        manifest["files"][fn] = {"sha256": _sha256(full),
                                 "bytes": os.path.getsize(full)}
'''

NEW = '''    # WALK the pack, do not list it. os.listdir returns names, and every name
    # used to be a file only because the pack was flat -- assets are now copied
    # to their own relative paths, so `buildings/` is a directory and
    # open(directory, "rb") is PermissionError on Windows.
    #
    # Recording POSIX relative paths also makes the manifest describe the pack as
    # the SCENE addresses it ("buildings/warehouse_a02.glb"), agree with the
    # deterministic zip, which has always stored nested paths, and stay correct
    # for any depth rather than for exactly one level.
    for root, dirs, files in os.walk(pack_dir):
        dirs.sort()
        for fn in sorted(files):
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, pack_dir).replace(os.sep, "/")
            if rel == "pack.manifest.json":
                continue        # written below; cannot hash itself
            manifest["files"][rel] = {"sha256": _sha256(full),
                                      "bytes": os.path.getsize(full)}
'''


def main() -> int:
    if not PKG.exists():
        raise SystemExit(f"missing {PKG}. Nothing written.")
    src = PKG.read_text(encoding="utf-8")
    if "for root, dirs, files in os.walk(pack_dir):" in src:
        print("package.py: manifest already walks the pack")
        return 0
    if src.count(OLD) != 1:
        raise SystemExit(f"package.py: the manifest loop appears "
                         f"{src.count(OLD)} time(s), expected exactly 1. "
                         f"NOTHING WRITTEN.")
    backup = PKG.with_suffix(".py.pre_manifest")
    if not backup.exists():
        shutil.copy2(PKG, backup)
    PKG.write_text(src.replace(OLD, NEW), encoding="utf-8")
    py_compile.compile(str(PKG), doraise=True)
    print("  package.py: manifest walks the pack and records relative paths")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  A stale pack folder from the failed run is probably sitting in "
          "lot/dist.\n  package.py removes it at the start of a build, so just "
          "re-run:\n")
    print("    cd lot")
    print("    python package.py specs\\ballpark_block\\ballpark_block_site.json "
          "--walkable \\")
    print('      --check "C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
