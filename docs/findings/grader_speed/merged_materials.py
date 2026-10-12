"""How many merged meshes each Empty's side carries per material, in one package or two.

The Empties' merge (`level_factory/assets/godot/merge_empties.gd`) keys a group on the side, the
material's name, its uv1 flags and the surface format, and saves each group as
`lot/<empty>/merged/<side>_<n>.res`. This reads the material's name out of each saved mesh (the
first string in the resource that has a capital and an underscore and is not a path or a class)
and counts meshes per (empty, side, material). For two packages it prints the rows that differ.
It measures and prints.

    python docs/findings/grader_speed/merged_materials.py <package> [<package>]
"""
import collections
import glob
import os
import re
import sys


def material(path):
    raw = open(path, "rb").read()
    for s in re.findall(rb"[ -~]{4,}", raw):
        s = s.decode("latin-1")
        if s.startswith(("res://", "local://", "uid://")) or "Material3D" in s or "ArrayMesh" in s:
            continue
        if re.search(r"[A-Z]", s) and "_" in s:
            return s
    return "?"


def census(pkg):
    out = collections.Counter()
    for p in glob.glob(os.path.join(pkg, "lot", "*", "merged", "*.res")):
        empty = os.path.basename(os.path.dirname(os.path.dirname(p)))
        out[(empty, os.path.basename(p)[0], material(p))] += 1
    return out


def main():
    pkgs = sys.argv[1:]
    cs = [census(p) for p in pkgs]
    for p, c in zip(pkgs, cs):
        print("%s: %d merged meshes, %d (empty, side, material) groups, at most %d meshes in one"
              % (p, sum(c.values()), len(c), max(c.values()) if c else 0))
    if len(cs) == 2:
        a, b = cs
        rows = sorted(k for k in set(a) | set(b) if a.get(k, 0) != b.get(k, 0))
        print("groups whose mesh count differs: %d of %d" % (len(rows), len(set(a) | set(b))))
        for k in rows[:40]:
            print("   %-20s %s %-42s %d -> %d" % (k[0], k[1], k[2], a.get(k, 0), b.get(k, 0)))


if __name__ == "__main__":
    main()
