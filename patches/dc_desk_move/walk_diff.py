"""What cold run 9376's export carries that 9375's does not, and the reverse: the two walk copies
(`_runs/walk_9375_restaurant_row_001`, `_runs/walk_9376_restaurant_row_001`, each its run's export with a player in
it), file by file -- every file only one side has, and every file both have whose bytes differ, `.godot/` and
`*.import` set aside -- then, for each building scene that differs (`lot/<id>/site.tscn`), its nodes on each side by
kind: merged meshes (`MergedR_<n>`), lit faces kept a mesh of their own (`LitR_<n>`), kit collision bodies, and the
rest. Cold run 9374's notes read the desk 0.252.0 took away the same way. Prints measurements only; writes
walk_diff.out.txt beside this file.

    python patches/dc_desk_move/walk_diff.py
"""
import collections
import hashlib
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
A = F / "_runs" / "walk_9375_restaurant_row_001"
B = F / "_runs" / "walk_9376_restaurant_row_001"
assert A.is_dir() and B.is_dir(), (A, B)


def files(root):
    out = {}
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if rel.startswith(".godot/") or rel.endswith(".import"):
                continue
            out[rel] = p
    return out


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


fa, fb = files(A), files(B)
lines = ["== the walk copies of cold runs 9375 and 9376: %d files against %d (.godot/ and *.import set aside)"
         % (len(fa), len(fb))]
only_a, only_b = sorted(set(fa) - set(fb)), sorted(set(fb) - set(fa))
lines.append("only in 9375: %d" % len(only_a))
lines += ["  " + n for n in only_a[:40]]
lines.append("only in 9376: %d" % len(only_b))
lines += ["  " + n for n in only_b[:40]]
differ = sorted(n for n in set(fa) & set(fb) if fa[n].stat().st_size != fb[n].stat().st_size or sha(fa[n]) != sha(fb[n]))
lines.append("in both, bytes differ: %d" % len(differ))
lines += ["  " + n for n in differ[:60]]
NODE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)"', re.M)


def kinds(text):
    c = collections.Counter()
    for name, typ in NODE.findall(text):
        if name.startswith("MergedR_"):
            c["merged mesh (MergedR_)"] += 1
        elif name.startswith("LitR_"):
            c["lit face (LitR_)"] += 1
        elif typ in ("StaticBody3D", "CollisionShape3D"):
            c[typ] += 1
        else:
            c["other " + typ] += 1
    return c


UID = re.compile(r" unique_id=\d+")
# ...and a node the engine names itself, `@StaticBody3D@723`, takes its number from a counter the whole merge run
# shares, so two bodies more in one building renumber every one after it (pharmacy_a01's, after office's, by two)
AUTO = re.compile(r"@(\w+)@\d+")
for n in differ:
    if not re.fullmatch(r"lot/[^/]+/site\.tscn", n):
        continue
    ta, tb = fa[n].read_text(encoding="utf-8"), fb[n].read_text(encoding="utf-8")
    ka, kb = kinds(ta), kinds(tb)
    # Godot gives every node a fresh `unique_id` each time it saves a scene, so a scene re-saved with nothing moved
    # differs on every node line; asked again with those set aside
    same = UID.sub("", ta) == UID.sub("", tb)
    renamed = not same and AUTO.sub(r"@\1@#", UID.sub("", ta)) == AUTO.sub(r"@\1@#", UID.sub("", tb))
    lines.append("%s: %d nodes -> %d; %s" % (
        n, sum(ka.values()), sum(kb.values()),
        "the same but for node unique_ids" if same else
        "the same but for node unique_ids and the engine's own @-numbered names" if renamed else "CONTENT DIFFERS"))
    for k in sorted(set(ka) | set(kb)):
        if ka[k] != kb[k]:
            lines.append("    %-28s %4d -> %4d" % (k, ka[k], kb[k]))
txt = "\n".join(lines) + "\n"
(HERE / "walk_diff.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
