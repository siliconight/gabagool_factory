"""Pre-flight for the front doors: one rowhome's kit and dressing, built by the
Zoo checked out now from Deli Counter's freshly built slots, before a cold run.

    python preflight_doors.py <out_dir> [<building>]

1. The kit, as cold run 9157's `zoo_kit_build` job ran it: prints every
   doorway module's stem and its leaf's material. The front door's stem must
   carry `_e<finish>` and its leaf a painted metal tinted for it; the back
   door's must not.
2. The dressing, as 9157's `zoo_dressing_build` ran it, with this
   Patina's window fixtures, stone trim and door fixtures appended to 9157's
   manifest (all exempt from the keep-out): prints Zoo's merge line and the
   GLB's meshes and materials. A security door is iron, so on a side with
   bars it joins their mesh.
"""
import json
import pathlib
import struct
import subprocess
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WS = F / "workspaces" / "cold-9157-ws" / ".level_factory" / "jobs"
BLENDER = r"C:\blender\blender.exe"
sys.path.insert(0, str(F / "patina"))
from patina import framing, slots, trim  # noqa: E402


def glb(path):
    b = path.read_bytes()
    clen = struct.unpack_from("<I", b, 12)[0]
    return json.loads(b[20:20 + clen])


def run(cmd):
    r = subprocess.run(cmd, cwd=str(F / "zoo"), capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])
    return r


out = pathlib.Path(sys.argv[1])
bid = sys.argv[2] if len(sys.argv) > 2 else "gs_empty_rowhome_a"
slots_json = F / "deli_counter" / "build" / f"{bid}.slots.json"
raw = json.loads(slots_json.read_text(encoding="utf-8"))
doors = [(s["slot_id"], s.get("door"), s.get("security_door")) for s in raw["slots"] if s["role"] == "doorway"]
print(f"== {bid}: doorway slots {doors}")

kit = out / bid / "kit"
kit.mkdir(parents=True, exist_ok=True)
r = run([BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
         "--build-kit", str(slots_json), "--out", str(kit),
         "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
         "--theme", "delco_1997", "--seed", "9080", "--no-blend"])
print(f"kit exit {r.returncode}")
for p in sorted(kit.glob("doorway*.glb")):
    g = glb(p)
    mats = [m.get("name") for m in g.get("materials", [])]
    leaf = [mats[pr["material"]] for n in g["nodes"] if "Leaf" in n.get("name", "") and "mesh" in n
            for pr in g["meshes"][n["mesh"]]["primitives"] if "material" in pr]
    print(f"  {p.name:60s} leaf {leaf}")

m, r_ = slots.parse(raw), trim.build_sheet(size=64, seed=1999)[1]
fx = (framing.window_fixture_orders(m, r_, seed=9080) + framing.opening_trim_orders(m, r_, seed=9080)
      + framing.door_fixture_orders(m, r_, seed=9080))
src = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
man = json.loads(src.read_text(encoding="utf-8"))
man["orders"] = [o for o in man["orders"] if o["cover"] not in
                 ("window_bars", "ac_unit", "lintel", "window_sill", "security_door")] + fx
dres = out / bid / "dress"
dres.mkdir(parents=True, exist_ok=True)
mpath = dres / f"{bid}.preflight.dressing.json"
mpath.write_text(json.dumps(man, indent=1), encoding="utf-8")
r = run([BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
         "--dress", str(mpath), "--out", str(dres),
         "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
         "--theme", "delco_1997", "--seed", "9080", "--no-blend"])
print(f"dress exit {r.returncode}")
for line in r.stdout.splitlines():
    if line.startswith("[zoo]") and ("covers (" in line or "merged" in line):
        print("  " + line)
g = glb(dres / f"{bid}_dressing.glb")
print(f"  materials {[m.get('name') for m in g.get('materials', [])]}")
print(f"  nodes {sorted(n.get('name') for n in g['nodes'] if 'mesh' in n)}")
