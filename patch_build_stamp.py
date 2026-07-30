"""Make rebuild_buildings.py record what each export was built from.

check_freshness.py can only verify a .glb against a stamp, and a stamp is only
honest if it is written at the moment of export. Writing it any other time records
a claim instead of checking one. So the exporter writes it.

Three edits to rebuild_buildings.py:

1. After a successful build, stamp the .glb: the SHA-256 of the spec that fed it,
   of the deli_counter sources that produced it, and of the .glb itself.
2. Stamp every duplicate too. Buildings shared across sites are built once and
   copied, and the existing sidecar copy loop skips `.glb` -- it would copy the
   first site's stamp verbatim, which happens to be correct here since the bytes
   are identical, but relying on that is how a wrong stamp survives. Written
   explicitly per path instead.
3. Report the builder hash up front, so a run says what it is building WITH and
   not only what it is building.

The stamp is a tracked artifact, not a sidecar to ignore. `lot/.gitignore`
excludes the five sidecars Lot never reads (manifest, slots, navigation,
validation, combat_audit); this one is evidence that the committed geometry
matches the committed spec, which is exactly the thing that was unverifiable.

Asserts every target, refuses on a miss, idempotent.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
REBUILD = ROOT / "rebuild_buildings.py"

IMPORT_OLD = '''import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import time
'''

IMPORT_NEW = '''import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import time

# check_freshness owns the stamp format so there is ONE definition of what a
# build is built from. Importing it here rather than restating the hash rule is
# the point: two copies of "which files count as the builder" would drift, and a
# drifted second copy is the recurring defect of this toolchain.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    import check_freshness as _fresh
except ImportError:
    _fresh = None
'''

HEADER_OLD = '''    print(f"  {len(found)} distinct building(s) across "
          f"{sum(len(v) for v in found.values())} site slot(s)\\n")
'''

HEADER_NEW = '''    print(f"  {len(found)} distinct building(s) across "
          f"{sum(len(v) for v in found.values())} site slot(s)")
    if _fresh is None:
        print("  NO STAMPS WILL BE WRITTEN -- check_freshness.py is not "
              "importable, so\\n  nothing will be able to verify these exports "
              "afterwards.")
        bhash, bcount = None, 0
    else:
        bhash, bcount = _fresh.builder_hash()
        print(f"  builder: {bcount} deli_counter source file(s), combined "
              f"{bhash[:16]}")
    print()
'''

STAMP_OLD = '''        built += 1
        after = first.stat().st_size
        print(f"  ok     {stem:<26} {before} -> {after} bytes")
        for dup in paths[1:]:
            shutil.copy2(first, dup)
            copied += 1
            print(f"           also -> {dup.parent.parent.name}")
            for side in first.parent.glob(f"{stem}.*"):
                if side.suffix == ".glb":
                    continue
                shutil.copy2(side, dup.parent / side.name)
'''

STAMP_NEW = '''        built += 1
        after = first.stat().st_size
        print(f"  ok     {stem:<26} {before} -> {after} bytes")
        for dup in paths[1:]:
            shutil.copy2(first, dup)
            copied += 1
            print(f"           also -> {dup.parent.parent.name}")
            for side in first.parent.glob(f"{stem}.*"):
                if side.suffix == ".glb":
                    continue
                shutil.copy2(side, dup.parent / side.name)
        # Stamp what this was built FROM, now, while it is true. Written per
        # path rather than copied with the other sidecars: the bytes are
        # identical so a copy would be correct here, and depending on that is
        # how a stamp that no longer describes its .glb survives a refactor.
        if bhash is not None:
            for p in paths:
                _fresh.write_stamp(p, spec, bhash, bcount)
            stamped += len(paths)
'''

TALLY_OLD = '''    built = failed = copied = 0
'''

TALLY_NEW = '''    built = failed = copied = stamped = 0
'''

FOOT_OLD = '''    print(f"\\n  built {built}, copied {copied}, failed {failed}, "
          f"no-spec {len(missing)}")
'''

FOOT_NEW = '''    print(f"\\n  built {built}, copied {copied}, stamped {stamped}, "
          f"failed {failed}, no-spec {len(missing)}")
    if bhash is not None:
        print(f"  verify any time with: python check_freshness.py")
    if missing:
        print(f"  the {len(missing)} building(s) with no spec stay UNSTAMPED and "
              f"cannot be verified")
'''


def main() -> int:
    if not REBUILD.exists():
        raise SystemExit(f"missing {REBUILD}. Nothing written.")
    src = REBUILD.read_text(encoding="utf-8")
    if "_fresh.write_stamp(" in src:
        print("rebuild_buildings.py: already stamps its exports")
        return 0

    edits = (("imports check_freshness", IMPORT_OLD, IMPORT_NEW),
             ("reports the builder hash up front", HEADER_OLD, HEADER_NEW),
             ("counts stamps", TALLY_OLD, TALLY_NEW),
             ("stamps each export and each duplicate", STAMP_OLD, STAMP_NEW),
             ("reports the stamp count", FOOT_OLD, FOOT_NEW))
    for label, old, new in edits:
        if src.count(old) != 1:
            raise SystemExit(
                f"rebuild_buildings.py: the target for '{label}' appears "
                f"{src.count(old)} time(s), expected exactly 1. Read the file "
                f"rather than forcing this. NOTHING WRITTEN.")
    for label, old, new in edits:
        src = src.replace(old, new)

    backup = REBUILD.with_suffix(".py.pre_stamp")
    if not backup.exists():
        shutil.copy2(REBUILD, backup)
    REBUILD.write_text(src, encoding="utf-8")
    py_compile.compile(str(REBUILD), doraise=True)
    for label, _o, _n in edits:
        print(f"  rebuild_buildings.py: {label}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Nothing is stamped until the next rebuild, so check_freshness.py "
          "will\n  report every building UNSTAMPED until then -- which is the "
          "honest state:\n  nothing on disk currently proves the geometry "
          "matches its spec.\n")
    print("  If you have NOT changed deli_counter since the last rebuild, the "
          "library\n  is in fact current and a baseline is legitimate:\n")
    print("    python check_freshness.py --stamp")
    print("\n  Otherwise rebuild, which stamps as it goes:\n")
    print('    python rebuild_buildings.py --blender "C:\\blender\\blender.exe"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
