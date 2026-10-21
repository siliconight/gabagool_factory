"""Every value that moved in a built record against HEAD, its build-time keys (`*_utc`) set aside: one line a leaf,
`path: old -> new`. For attributing what a rebuild changed in a record beyond its build time.

    python patches/dc_ticket_queue/record_moves.py build/arena_a02.gameplay.json [...]

Paths are Deli Counter's; prints what moved and stops.
"""
import json
import subprocess
import sys

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if not k.endswith("_utc"):
                yield from leaves(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, "%s[%d]" % (path, i))
    else:
        yield path, o


for rel in sys.argv[1:]:
    old = json.loads(subprocess.run(["git", "-C", DC, "show", "HEAD:" + rel], capture_output=True, check=True).stdout)
    new = json.load(open(DC + "\\" + rel.replace("/", "\\"), encoding="utf-8"))
    a, b = dict(leaves(old)), dict(leaves(new))
    moved = [(k, a.get(k, "<absent>"), b.get(k, "<absent>")) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
    print("%s: %d values moved" % (rel, len(moved)))
    for k, x, y in moved:
        print("   %s: %r -> %r" % (k, x, y))
