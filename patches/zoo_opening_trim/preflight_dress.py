"""Pre-flight: one real building's dressing WITH its window fixtures AND its
stone lintels and sills (Patina 0.27.0), built by
the Zoo checked out now, before a cold run spends 33 minutes finding out.

    python preflight_dress.py <out_dir> [<building> ...]

For each building: Deli Counter's freshly built `build/<b>.slots.json` gives
the window fixtures through Patina's own `framing.window_fixture_orders`; they
are appended to cold run 9155's Patina manifest for that building (the orders
a Patina 0.26.0 run would add -- they are exempt from its keep-out, so the
filter would keep them all), and `zoo_cli.py --dress` builds the result under
Blender with 9155's skins, theme and seed. Prints the fixture counts, Zoo's
merge line, and the GLB's meshes and materials.
"""
import json
import pathlib
import struct
import subprocess
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WS = F / "workspaces" / "cold-9155-ws" / ".level_factory" / "jobs"
BLENDER = r"C:\blender\blender.exe"
sys.path.insert(0, str(F / "patina"))
from patina import framing, slots, trim  # noqa: E402


def glb_summary(path):
    b = path.read_bytes()
    clen = struct.unpack_from("<I", b, 12)[0]
    g = json.loads(b[20:20 + clen])
    mats = [m.get("name") for m in g.get("materials", [])]
    nodes = [n for n in g.get("nodes", []) if "mesh" in n]
    prims = sum(len(g["meshes"][n["mesh"]]["primitives"]) for n in nodes)
    return len(nodes), prims, mats, sorted(n.get("name") for n in nodes)


out = pathlib.Path(sys.argv[1])
for bid in sys.argv[2:] or ["gs_empty_rowhome_f"]:
    raw = json.loads((F / "deli_counter" / "build" / f"{bid}.slots.json").read_text(encoding="utf-8"))
    wins = [s for s in raw["slots"] if s.get("role") == "window"]
    _m, _r = slots.parse(raw), trim.build_sheet(size=64, seed=1999)[1]
    fx = framing.window_fixture_orders(_m, _r, seed=9080) + framing.opening_trim_orders(_m, _r, seed=9080)
    src = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
    man = json.loads(src.read_text(encoding="utf-8"))
    man["orders"] = list(man["orders"]) + fx
    dst = out / bid
    dst.mkdir(parents=True, exist_ok=True)
    mpath = dst / f"{bid}.preflight.dressing.json"
    mpath.write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"== {bid}: {len(wins)} windows -- bars {sum(1 for s in wins if s.get('bars'))}, "
          f"ac {sum(1 for s in wins if s.get('ac'))}; fixture orders "
          f"{sorted((o['cover'], o['slot_id']) for o in fx)}")
    cmd = [BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
           "--dress", str(mpath), "--out", str(dst),
           "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
           "--theme", "delco_1997", "--seed", "9080", "--no-blend"]
    r = subprocess.run(cmd, cwd=str(F / "zoo"), capture_output=True, text=True, timeout=1200)
    print(f"  zoo exit {r.returncode}")
    for line in r.stdout.splitlines():
        if line.startswith("[zoo]") and ("covers" in line or "merged" in line or "refused" in line):
            print("  " + line)
    if r.returncode != 0:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
        continue
    n, p, mats, names = glb_summary(dst / f"{bid}_dressing.glb")
    print(f"  glb: {n} mesh nodes, {p} primitives; materials {mats}")
    print(f"  nodes: {names}")
