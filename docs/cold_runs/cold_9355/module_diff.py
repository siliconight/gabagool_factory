"""What changed between two walk copies of one level, module by module: every GLB and every image under each, by
name and by hash -- added, removed, and changed in place. Run to attribute a price before reading it.

    python docs/cold_runs/cold_9355/module_diff.py <walk copy A> <walk copy B>

A walk copy is the package plus a player; the package's files are the same bytes in it. Prints what it counted.
"""
import hashlib
import pathlib
import sys

a, b = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
KINDS = (".glb", ".png", ".jpg", ".exr", ".tscn", ".lmbake", ".res", ".tres")


def files(root):
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in KINDS and ".godot" not in p.parts:
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    return out


fa, fb = files(a), files(b)
added = sorted(set(fb) - set(fa))
removed = sorted(set(fa) - set(fb))
changed = sorted(k for k in set(fa) & set(fb) if fa[k] != fb[k])
print("A %d files, B %d; same %d" % (len(fa), len(fb), len(set(fa) & set(fb)) - len(changed)))
for title, names in (("added in B", added), ("removed in B", removed), ("changed in place", changed)):
    print("%s: %d" % (title, len(names)))
    for n in names:
        print("   ", n)
