"""Re-export every building the library walks, in place.

`library_walk.py` stages a site by copying `lot/specs/<site>/buildings/` into a
throwaway project, so the .glb sitting in each site folder IS the geometry that
gets walked. A fix in `deli_counter.py` reaches a site only after that .glb is
rebuilt through Blender, and nothing else in the toolchain does it.

That matters right now because two changes have to arrive together:

  * patch_ramp_foot.py lands a flight's collision ramp flush on the floor at its
    foot, instead of half a step proud of it.
  * agent_max_climb_m dropped 0.5 -> 0.15, so the navmesh stops routing bodies
    over risers a capsule cannot walk.

Apply the second without the first and a stale building's 0.26 m ramp foot is
now too tall for the bake, which disconnects its staircase from below. The
result reads as "the climb change broke this site" when what actually happened
is the building was never rebuilt. Re-export first, then sweep, so a red site
means a real defect.

Each .glb is matched to `deli_counter/specs/<stem>.json` by filename. A .glb with
no matching spec is REPORTED, not skipped silently -- it came from somewhere this
does not know about, and pretending otherwise is how stale geometry survives a
rebuild.

Buildings shared by several sites are built once and copied to the rest.

    python rebuild_buildings.py --dry-run
    python rebuild_buildings.py --blender "C:\\blender\\blender.exe"
"""
import argparse
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
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    import check_freshness as _fresh
except ImportError:
    _fresh = None
from factory_paths import factory_root                        # noqa: E402

#: SCRIPT_DIR above finds check_freshness beside this file; ROOT is the tree
#: being rebuilt. Same distinction check_all.py now makes, same reason.
ROOT = factory_root()
SITES = ROOT / "lot" / "specs"
DC = ROOT / "deli_counter"
DC_SPECS = DC / "specs"


def find_blender(explicit=None):
    """Same order build.py uses, plus the path this project actually has."""
    if explicit:
        return explicit
    if os.environ.get("BLENDER"):
        return os.environ["BLENDER"]
    found = shutil.which("blender")
    if found:
        return found
    for guess in (r"C:\blender\blender.exe",
                  r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
                  r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
                  r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"):
        if os.path.exists(guess):
            return guess
    return None


def targets():
    """{stem: [every .glb path in the library that stem feeds]}."""
    out = {}
    for glb in sorted(SITES.glob("*/buildings/*.glb")):
        out.setdefault(glb.stem, []).append(glb)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--blender", help="path to blender.exe")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be rebuilt and stop")
    ap.add_argument("--only", nargs="*", default=None,
                    help="rebuild only these building stems")
    args = ap.parse_args()

    found = targets()
    if args.only:
        found = {k: v for k, v in found.items() if k in set(args.only)}
    if not found:
        print(f"no .glb under {SITES}/*/buildings/ -- wrong root?")
        return 1

    have, missing = {}, {}
    for stem, paths in sorted(found.items()):
        spec = DC_SPECS / f"{stem}.json"
        (have if spec.exists() else missing)[stem] = (spec, paths)

    print(f"  {len(found)} distinct building(s) across "
          f"{sum(len(v) for v in found.values())} site slot(s)")
    if _fresh is None:
        print("  NO STAMPS WILL BE WRITTEN -- check_freshness.py is not "
              "importable, so\n  nothing will be able to verify these exports "
              "afterwards.")
        bhash, bcount = None, 0
    else:
        bhash, bcount = _fresh.builder_hash()
        print(f"  builder: {bcount} deli_counter source file(s), combined "
              f"{bhash[:16]}")
    print()
    for stem, (spec, paths) in have.items():
        ages = {p: time.strftime("%Y-%m-%d %H:%M",
                                 time.localtime(p.stat().st_mtime))
                for p in paths}
        where = ", ".join(f"{p.parent.parent.name} ({ages[p]})" for p in paths)
        print(f"  build  {stem:<26} -> {where}")
    for stem, (spec, paths) in missing.items():
        print(f"  NO SPEC {stem:<25} -> {', '.join(p.parent.parent.name for p in paths)}")
    if missing:
        print(f"\n  {len(missing)} building(s) have no deli_counter spec and "
              f"CANNOT be rebuilt here.\n  They keep whatever geometry they "
              f"already have; if a site of theirs fails the\n  sweep, that is "
              f"the first thing to suspect.")

    if args.dry_run:
        print("\n  --dry-run: nothing built")
        return 0

    blender = find_blender(args.blender)
    if not blender:
        print("\nBlender not found. Pass --blender or set $env:BLENDER.")
        return 1
    print(f"\n  blender: {blender}\n")

    built = failed = copied = stamped = 0
    for stem, (spec, paths) in have.items():
        first = paths[0]
        before = first.stat().st_size
        cmd = [sys.executable, str(DC / "build.py"), str(spec),
               "--blender", blender, "--out", str(first)]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(DC))
        if r.returncode != 0 or not first.exists():
            failed += 1
            print(f"  FAIL   {stem}")
            tail = (r.stderr or r.stdout or "").rstrip().splitlines()[-6:]
            for ln in tail:
                print(f"           {ln[:150]}")
            continue
        built += 1
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

    print(f"\n  built {built}, copied {copied}, stamped {stamped}, "
          f"failed {failed}, no-spec {len(missing)}")
    if bhash is not None:
        print(f"  verify any time with: python check_freshness.py")
    if missing:
        print(f"  the {len(missing)} building(s) with no spec stay UNSTAMPED and "
              f"cannot be verified")
    if failed:
        print("  a failed building keeps its old geometry -- do NOT read the "
              "sweep as clean")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
