"""Which meshes' face roles Patina 0.31.0 changes on the shells whose replay moved only the styled GLB (roadmap 248).

    python docs/findings/patina_props/glb_only_roles.py > docs/findings/patina_props/glb_only_roles.out.txt

Imports the factory's Patina repo (0.31.0 or later). For each shell `replay.py` found moving its `.patina.glb` and not its
dressing, loads Deli Counter's GLB the CLI's way, classifies it twice -- its slots.json's props unnamed, as 0.30.0
read every shell, and named -- and prints how many meshes' roles changed, whether each is a prop or structure,
and how many faces left which role. Prints what it measured and stops.
"""
import sys
from collections import Counter
from pathlib import Path

F = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "patina"))
from patina import gltf_io, slots, surfaces  # noqa: E402

BUILD = F / "deli_counter" / "build"
SHELLS = ("07_police_station", "bank", "bank_branch_a02", "bank_branch_a03", "bank_job", "final_stand",
          "parking_garage", "parking_garage_a01", "parking_garage_a02", "pvp_station_ref", "harbor_score")

for name in SHELLS:
    roles = {}
    props = frozenset()
    for how in ("unnamed", "named"):
        sc = gltf_io.load_glb(str(BUILD / (name + ".glb")))
        m = slots.load(sc)
        if m is None:
            raise SystemExit("UNKNOWN SHAPE: no slots.json beside " + name)
        props = m.prop_ids()
        sc.bake_visual_transforms()
        up = slots.detect_up_axis(sc)
        surfaces.classify(sc, up, props=props if how == "named" else frozenset())
        roles[how] = {x.name: Counter(r.value for p in x.primitives for r in p.face_roles) for x in sc.visual_meshes()}
    changed = [n for n in roles["named"] if roles["named"][n] != roles["unnamed"][n]]
    kinds = Counter(("prop" if n in props else "structure") for n in changed)
    left, joined = Counter(), Counter()
    for n in changed:
        for r in set(roles["unnamed"][n]) | set(roles["named"][n]):
            d = roles["unnamed"][n].get(r, 0) - roles["named"][n].get(r, 0)
            if d > 0:
                left[r] += d
            elif d < 0:
                joined[r] -= d
    print("%-20s meshes whose roles changed: %3d %s; faces leaving a role %s, joining %s; e.g. %s"
          % (name, len(changed), dict(kinds), dict(left), dict(joined), changed[:3]))
