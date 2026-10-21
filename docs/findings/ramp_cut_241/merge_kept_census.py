"""What a building merge drops that is not a mesh: in every building scene a level's presentation composes, the
nodes that are an Area3D or carry groups, counted under the top-level child that holds them -- the unit Level
Factory's `merge_buildings.gd` merges whole and then removes.

    python docs/findings/ramp_cut_241/merge_kept_census.py <presentation_compose out/presentation dir>

Reads the text scenes (`lot/<building>/site.tscn`); prints what it counted and stops.
"""
import collections
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
NODE = re.compile(r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]+)")?(.*)\]$')
for scene in sorted(root.glob("lot/*/site.tscn")):
    counts = collections.Counter()
    for line in scene.read_text(encoding="utf-8", errors="replace").splitlines():
        m = NODE.match(line)
        if not m:
            continue
        name, typ, parent, rest = m.group(1), m.group(2) or "", m.group(3), m.group(4)
        if parent is None:
            continue                       # the scene root
        top = name if parent == "." else parent.split("/")[0]
        if typ == "Area3D" or "groups=" in rest:
            groups = re.findall(r'groups=\[([^\]]*)\]', rest)
            counts[(top, typ or "instance", groups[0] if groups else "")] += 1
    if counts:
        print(scene.parent.name)
        for (top, typ, groups), n in sorted(counts.items()):
            print("   %-28s %3d %-10s %s" % (top, n, typ, groups))
