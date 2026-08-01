"""Six tools stop assuming they live in the tree they check.

MEASURED. A grep across every root .py for `__file__`, `rglob`, `glob(` and
`iterdir` found six that derive the tree they scan from their own location:

    check_all.py          ROOT.rglob("*.gd")           -- 104 files today
    check_freshness.py    DC.glob("*.py"), SITES.glob("*/buildings/*.glb")
    check_stair_pitch.py  SITES.glob("*/buildings/*.glb")
    check_steps.py        LOT, RUNS, SPECS, CONTRACT off ROOT
    library_walk.py       LOT, RUNS, REGISTRY off HERE
    rebuild_buildings.py  SITES, DC, DC_SPECS off ROOT

Move any of them into tools/ as-is and it scans tools/. check_all would report
`gdscript  clean  0` over four files instead of 104 -- narrower coverage, same
green. That is the exact failure this whole guardrails pass has been about, and
a tidy is a stupid way to reintroduce it.

WHAT CHANGES. Each file asks factory_paths.factory_root() instead of assuming
`__file__`'s parent. The two that also need their own directory -- check_all.py
shells out to sibling checkers, rebuild_buildings.py imports check_freshness --
get SCRIPT_DIR as a separate name, because those two questions had the same
answer only while nothing had moved.

WHAT DOES NOT CHANGE. Every downstream name (ROOT, HERE, SITES, DC, LOT, RUNS,
SPECS, CONTRACT, REGISTRY) keeps its meaning and its type -- check_steps.py and
library_walk.py use os.path.join, so they still get str. Nothing below the
header is touched in any of the six.

RUN THIS BEFORE MOVING ANYTHING. The tools stay at the root through this patch,
so `python check_all.py` must report exactly what it reported before -- 104
files on the gdscript row. If it does not, the move would have been worse.

Asserts every target, refuses on a miss, idempotent, byte-compiles all six.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")

SHIM = '''sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from factory_paths import factory_root                        # noqa: E402
'''

EDITS = {
    "check_all.py": [(
        "ROOT = pathlib.Path(__file__).resolve().parent\n",
        '''SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from factory_paths import factory_root                        # noqa: E402

#: TWO QUESTIONS, not one. SCRIPT_DIR finds the sibling checkers this script
#: shells out to; ROOT is the tree those checkers are pointed at. They were the
#: same directory while everything sat at the factory root, and stop being the
#: same the moment anything moves -- at which point gd_files() would scan the
#: tools directory, find a handful of .gd files instead of 104, and still print
#: `clean`.
ROOT = factory_root()
''')],

    "check_freshness.py": [(
        '''import os
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent
''',
        '''import os
import pathlib
import sys
import time

''' + SHIM + '''
#: The tree being checked, found by walking up to factory.manifest.json rather
#: than assuming this file sits in it.
ROOT = factory_root()
''')],

    "check_stair_pitch.py": [(
        '''import os
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parent
''',
        '''import os
import pathlib
import struct
import sys

''' + SHIM + '''
ROOT = factory_root()
''')],

    "check_steps.py": [(
        "ROOT = os.path.dirname(os.path.abspath(__file__))\n",
        '''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factory_paths import factory_root                        # noqa: E402

#: str, not Path -- everything below joins with os.path.join.
ROOT = str(factory_root())
''')],

    "library_walk.py": [(
        "HERE = os.path.dirname(os.path.abspath(__file__))\n",
        '''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factory_paths import factory_root                        # noqa: E402

#: HERE meant "the directory this file is in", which was the factory root only
#: because nothing had moved. It means the factory now. str, not Path, because
#: everything below joins with os.path.join.
HERE = str(factory_root())
''')],

    "rebuild_buildings.py": [(
        '''sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    import check_freshness as _fresh
except ImportError:
    _fresh = None

ROOT = pathlib.Path(__file__).resolve().parent
''',
        '''SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import check_freshness as _fresh
except ImportError:
    _fresh = None
from factory_paths import factory_root                        # noqa: E402

#: SCRIPT_DIR above finds check_freshness beside this file; ROOT is the tree
#: being rebuilt. Same distinction check_all.py now makes, same reason.
ROOT = factory_root()
''')],
}


def main() -> int:
    if not (ROOT / "factory_paths.py").is_file():
        raise SystemExit(
            "factory_paths.py is not at the factory root yet. Put it there\n"
            "first -- every edit below imports it. NOTHING WRITTEN.")
    if not (ROOT / "factory.manifest.json").is_file():
        raise SystemExit("no factory.manifest.json at the root -- that is the\n"
                         "marker factory_root() walks up to. NOTHING WRITTEN.")

    plan, done, already = [], [], []
    for name, edits in EDITS.items():
        p = ROOT / name
        if not p.exists():
            raise SystemExit(f"missing {p}. NOTHING WRITTEN.")
        src = p.read_text(encoding="utf-8")
        if "factory_root()" in src:
            already.append(name)
            continue
        for old, new in edits:
            n = src.count(old)
            if n != 1:
                raise SystemExit(
                    f"{name}: anchor appears {n} time(s), expected exactly 1.\n"
                    f"  The file is not what this patch was written against.\n"
                    f"  NOTHING WRITTEN -- no other file has been touched either.")
            src = src.replace(old, new)
        plan.append((p, src))

    # Nothing is written until every file has been checked, so a late mismatch
    # cannot leave half the toolchain converted and half not.
    for p, src in plan:
        backup = p.with_suffix(".py.pre_root")
        if not backup.exists():
            shutil.copy2(p, backup)
        p.write_text(src, encoding="utf-8")
        py_compile.compile(str(p), doraise=True)
        done.append(p.name)

    for n in already:
        print(f"  {n}: already asks factory_root()")
    for n in done:
        print(f"  {n}: root derived from factory.manifest.json, not from __file__")
    if done:
        print(f"\n  {len(done)} file(s) rewritten and byte-compiled; previous "
              f"copies kept as *.pre_root")
    print("\n  NOTHING MOVED. Everything is still at the root, so this run must "
          "produce\n  the SAME result as before -- 104 files on the gdscript "
          "row:\n")
    print("    python check_all.py")
    print("\n  If that number changed, the root-finder is wrong and the move "
          "would have\n  been worse. If it held, the tools are relocatable and "
          "the move is safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
