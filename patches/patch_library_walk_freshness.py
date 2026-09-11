"""`library_walk.py` refuses to walk stale geometry (roadmap 65).

Anchored; asserts each target exactly once and refuses to write on a miss.
Run from the factory root:  python patches\\patch_library_walk_freshness.py
"""
import io
import sys

P = "tools/library_walk.py"


def main() -> int:
    t = io.open(P, encoding="utf-8", newline="").read()
    if "--allow-stale" in t:
        print("already applied")
        return 0
    edits = []

    edits.append((
        '    ap.add_argument("--timeout", type=int, default=1200)\n',
        '    ap.add_argument("--timeout", type=int, default=1200)\n'
        '    ap.add_argument("--allow-stale", action="store_true",\n'
        '                    help="walk a site whose building geometry is stale "\n'
        '                         "against its spec or builder anyway. Without "\n'
        '                         "this a stale site is REFUSED, not graded: a "\n'
        '                         "number taken on twenty-version-old geometry "\n'
        '                         "describes nothing (roadmap 65)")\n'))

    edits.append((
        '        proj, how = stage(name, spec, keep=args.keep)\n',
        '        # REFUSE STALE GEOMETRY RATHER THAN GRADE IT (roadmap 65).\n'
        '        # `check_freshness.py` detected this by content hash and was in\n'
        '        # `check_all.py` from the day it was written, and nobody ran it;\n'
        '        # every site-scale measurement for 24 days -- walks, nav-gate\n'
        '        # readings, Laser Tag runs -- was taken on geometry up to twenty\n'
        '        # Deli Counter versions old. The precedent is `build_freshness.py`,\n'
        '        # which refuses to grade a stale library. Same rule, one level up.\n'
        '        stale = stale_buildings(spec)\n'
        '        if stale and not args.allow_stale:\n'
        '            print(f"  {name}: REFUSED, {len(stale)} stale building(s) --")\n'
        '            for stem, state, detail in stale[:6]:\n'
        '                print(f"      {stem:<26} {state:<14} {detail}")\n'
        '            if len(stale) > 6:\n'
        '                print(f"      ... and {len(stale) - 6} more")\n'
        '            print("      rebuild: python tools/rebuild_buildings.py "\n'
        '                  "--blender <path>   (or --allow-stale to walk anyway)")\n'
        '            results.append({"mission": name, "stem": stem,\n'
        '                            "verdict": "REFUSED_STALE",\n'
        '                            "stale": [s[0] for s in stale]})\n'
        '            continue\n'
        '        proj, how = stage(name, spec, keep=args.keep)\n'))

    edits.append((
        'def stage(name, spec, keep=False):\n',
        'def stale_buildings(spec):\n'
        '    """[(stem, state, detail)] for every building this site walks whose\n'
        '    geometry no longer matches its spec or builder, per\n'
        '    `check_freshness.verify`. Empty when every .glb is fresh -- and empty\n'
        '    when the checker cannot run, which is reported rather than treated\n'
        '    as fresh."""\n'
        '    try:\n'
        '        import check_freshness as cf\n'
        '    except ImportError:\n'
        '        print("  (check_freshness not importable -- freshness NOT verified)")\n'
        '        return []\n'
        '    src_b = os.path.join(os.path.dirname(spec), "buildings")\n'
        '    if not os.path.isdir(src_b):\n'
        '        return []\n'
        '    bhash, bcount = cf.builder_hash(cf.builder_files())\n'
        '    out = []\n'
        '    for fn in sorted(os.listdir(src_b)):\n'
        '        if not fn.endswith(".glb"):\n'
        '            continue\n'
        '        glb = cf.pathlib.Path(src_b) / fn\n'
        '        state, detail = cf.verify(glb, bhash, bcount)\n'
        '        if state != "fresh":\n'
        '            out.append((glb.stem, state, detail))\n'
        '    return out\n'
        '\n'
        '\n'
        'def stage(name, spec, keep=False):\n'))

    for old, new in edits:
        n = t.count(old)
        if n != 1:
            print(f"ANCHOR MISS ({n}): {old[:70]!r}", file=sys.stderr)
            return 1
        t = t.replace(old, new, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
