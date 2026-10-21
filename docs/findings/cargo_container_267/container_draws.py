"""The freight terminal's merged meshes by material, in one package: how many carry each of the container module's
materials, and which other pre-merge modules of the building wear those materials too. Reads the package's
lot/freight_terminal_a01/merged/*.res (Level Factory's building merge writes one material to each) and the
presentation job's pre-merge art/zoo GLBs. Prints what it counted and stops.

    python docs/findings/cargo_container_267/container_draws.py <package dir> <presentation_compose out/presentation>
"""
import collections, glob, json, os, re, struct, sys
pkg, pres = sys.argv[1], sys.argv[2]
CC = "prop_cargo_container_delco_1997_06_w240_d600_h260.glb"

def glb_mats(p):
    raw = open(p, "rb").read()
    n = struct.unpack_from("<I", raw, 12)[0]
    g = json.loads(raw[20:20 + n])
    return {m.get("name") for m in g.get("materials", [])}

zoo = os.path.join(pres, "lot", "freight_terminal_a01", "art", "zoo")
cmats = glb_mats(os.path.join(zoo, CC))
others = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(zoo, "*.glb"))):
    if os.path.basename(p) == CC:
        continue
    for m in glb_mats(p) & cmats:
        others[m].append(os.path.basename(p))
per_mat = collections.Counter()
for p in sorted(glob.glob(os.path.join(pkg, "lot", "freight_terminal_a01", "merged", "*.res"))):
    b = open(p, "rb").read()
    names = set(s.decode() for s in re.findall(rb"M_[A-Za-z0-9_]{3,80}", b))
    for m in names:
        per_mat[m] += 1
print("container materials:", len(cmats))
total = 0
for m in sorted(cmats):
    total += per_mat[m]
    print("  %-44s merged meshes %d   also worn by %s" % (m, per_mat[m], others.get(m, [])[:4] or "nothing else"))
print("merged meshes carrying a container material:", total, "of", sum(1 for _ in glob.glob(os.path.join(pkg, "lot", "freight_terminal_a01", "merged", "*.res"))))
