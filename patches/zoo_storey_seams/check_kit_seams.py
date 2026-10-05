"""Rebuild one building's kit with the Zoo checked out now, as cold run 9156's
`zoo_kit_build` job did, and report every wall-family module's chamfer
vertices near its top and bottom planes.

    python check_kit_seams.py <out_dir> [<building>]

A run module's top and bottom are joints (Zoo >= 1.70.0): a vertex within
1 cm of the top or bottom plane but not ON it (more than 0.1 mm away) is a
chamfer cut along a seam. Prints, per module GLB, the count of such vertices
on its visual meshes, with 9156's shipped module beside it as the control.
"""
import json
import pathlib
import struct
import subprocess
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WS = F / "workspaces" / "cold-9156-ws" / ".level_factory" / "jobs"
BLENDER = r"C:\blender\blender.exe"
sys.path.insert(0, str(F / "patches" / "zoo_cover_merge"))
import glb_geometry as G  # noqa: E402

out = pathlib.Path(sys.argv[1])
bid = sys.argv[2] if len(sys.argv) > 2 else "gs_empty_rowhome_d"
dst = out / bid
dst.mkdir(parents=True, exist_ok=True)
cmd = [BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
       "--build-kit", str(F / "deli_counter" / "build" / f"{bid}.slots.json"), "--out", str(dst),
       "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
       "--theme", "delco_1997", "--seed", "9080", "--no-blend"]
r = subprocess.run(cmd, cwd=str(F / "zoo"), capture_output=True, text=True, timeout=1800)
print(f"kit build exit {r.returncode}")
if r.returncode != 0:
    print(r.stdout[-1500:]); print(r.stderr[-1500:]); sys.exit(1)


def seam_vertices(path):
    g, binb = G.load(str(path))
    bad = 0
    total = 0
    for n in g["nodes"]:
        if "mesh" not in n or "colonly" in n.get("name", ""):
            continue
        for prim in g["meshes"][n["mesh"]]["primitives"]:
            P = G.accessor(g, binb, prim["attributes"]["POSITION"])
            ys = [p[1] for p in P]          # glTF Y-up: a module's height axis
            lo, hi = min(ys), max(ys)
            for y in ys:
                total += 1
                for plane in (lo, hi):
                    if 1e-4 < abs(y - plane) < 0.01:
                        bad += 1
    return bad, total


shipped = WS / f"gas_block_001.zoo_kit_build.{bid}" / "1" / "out"
for glb in sorted(dst.glob("*.glb")):
    if not glb.name.startswith(("wall", "window", "doorway", "breach")):
        continue
    now_bad, now_total = seam_vertices(glb)
    old = shipped / glb.name
    old_txt = "-"
    if old.is_file():
        ob, ot = seam_vertices(old)
        old_txt = f"{ob} of {ot}"
    print(f"{glb.name:60s} vertices in a seam chamfer: 1.70.0 {now_bad} of {now_total}   9156 (1.69.0) {old_txt}")
