"""Every file that left or joined a package between two exports (roadmap 249's proof in the cold runs).

    python docs/findings/merged_modules/package_files.py <package A> <package B>

Walks both packages, `.godot/` aside, and prints the files only A has and the files only B has, the kit
modules under an Empty's `art/zoo/` -- each `.glb` with its `.glb.import` and `.unwrap_cache` -- counted
apart from the rest, which are listed by path. Prints what it measured and stops.
"""
import os
import sys


def files(root):
    out = set()
    for dp, _dn, fn in os.walk(root):
        if ".godot" in os.path.relpath(dp, root).split(os.sep):
            continue
        for f in fn:
            out.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    return out


def main(a, b):
    if not (os.path.isdir(a) and os.path.isdir(b)):
        raise SystemExit("not two package folders: %s, %s" % (a, b))
    fa, fb = files(a), files(b)
    gone, new = fa - fb, fb - fa
    modules = {f for f in gone if "/art/zoo/" in f and f.endswith((".glb", ".glb.import", ".unwrap_cache"))}
    glbs = {f for f in modules if f.endswith(".glb")}
    rest = sorted(gone - modules)
    print("A %s: %d files" % (a, len(fa)))
    print("B %s: %d files" % (b, len(fb)))
    print("only in A: %d -- %d kit modules' files under art/zoo/ (%d .glb), %d other"
          % (len(gone), len(modules), len(glbs), len(rest)))
    for f in rest:
        print("   - " + f)
    print("only in B: %d" % len(new))
    for f in sorted(new):
        print("   + " + f)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
