"""Roadmap 227: how deep below a workspace the files a level writes reach, by kind.

    python docs/findings/long_paths/depth.py <workspace> [<workspace> ...]

For each workspace, the deepest file of each kind, in characters below the workspace root, and the
same path absolute. The kinds are where Godot writes under any `.godot` folder (`editor`, its UI
state; `imported`, what a level loads) and everything else. Windows refuses a path longer than 260
characters unless `LongPathsEnabled` is 1, so the absolute figure is the one that matters on a given
machine, and the figure below the workspace is the one a doctor could add to any workspace's own
depth. Counts every path past 260 too, and names the longest single file or folder name, which
is what Linux limits (255). It prints what it measured and stops.
"""
import os
import sys

LIMIT = 260


def kind(rel):
    parts = rel.replace("/", os.sep).split(os.sep)
    if ".godot" in parts:
        nxt = parts[parts.index(".godot") + 1] if parts.index(".godot") + 1 < len(parts) else ""
        return "godot " + nxt if nxt in ("editor", "imported") else "godot other"
    return "everything else"


def main(roots):
    for root in roots:
        root = os.path.abspath(root)
        if not os.path.isdir(root):
            raise SystemExit("%s: not a folder" % root)
        deepest = {}
        files = over = 0
        longest = (0, "")
        for dp, dn, fn in os.walk(root):
            for name in dn + fn:
                if len(name) > longest[0]:
                    longest = (len(name), name)
            for f in fn:
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, root)
                files += 1
                if len(p) > LIMIT:
                    over += 1
                k = kind(rel)
                if len(rel) > deepest.get(k, (0, ""))[0]:
                    deepest[k] = (len(rel), rel)
        if not files:
            raise SystemExit("%s: no files under it" % root)
        print("%s (%d characters; %d files, %d of them past %d absolute)" % (root, len(root), files, over, LIMIT))
        for k, (n, rel) in sorted(deepest.items(), key=lambda kv: -kv[1][0]):
            print("  %-16s %3d below, %3d absolute: %s" % (k, n, n + len(root) + 1, rel))
        print("  longest name     %3d: %s" % longest)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
