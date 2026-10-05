"""Pre-flight for an Empty's roof fixtures, before a cold run spends 33 minutes.

    python preflight_roof.py <run> <patina dir> <zoo dir> <out dir> [<building> ...]

For each building, from cold run <run>'s own outputs and Deli Counter's
current `build/<b>.slots.json`:

1. The roof slot is given what Deli Counter 0.185.0 writes on it -- `antenna`
   / `dish` from `presets.EMPTY_ROWHOMES`, and `front` from the wall holding
   the front door, by `roofs.front_facing` over the preset's own spec. Those
   functions are imported from the Deli Counter beside <patina dir>, so a
   patched scratch copy is the one tested.
2. The Patina at <patina dir> orders the fixtures (`roof_fixture_orders`);
   they are appended to the run's Patina manifest for the building. They are
   exempt from its keep-out, so its filter would keep them all.
3. The Zoo at <zoo dir> builds that manifest under Blender with the run's
   skins, theme and seed (`zoo_cli.py --dress`).
4. `render_roof.py` renders the shell and the covers from across the street
   and from above, under Blender's workbench.

Prints the orders, Zoo's merge lines, and the GLB's meshes and materials
before and after, so a new mesh or material is visible as a number.
"""
import importlib
import json
import pathlib
import struct
import subprocess
import sys
import types

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
BLENDER = r"C:\blender\blender.exe"
HERE = pathlib.Path(__file__).resolve().parent

run, patina_dir, zoo_dir, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]), \
    pathlib.Path(sys.argv[4])
WS = F / "workspaces" / f"cold-{run}-ws" / ".level_factory" / "jobs"
DC = patina_dir.parent / "deli_counter"
sys.path.insert(0, str(patina_dir))
sys.path.insert(0, str(DC))
from patina import framing, slots, trim  # noqa: E402

presets = importlib.import_module("presets")
roofs = importlib.import_module("roofs")
spec_types = importlib.import_module("spec_types")
assert pathlib.Path(framing.__file__).resolve().is_relative_to(patina_dir.resolve()), framing.__file__
assert pathlib.Path(roofs.__file__).resolve().is_relative_to(DC.resolve()), roofs.__file__


def glb_summary(path):
    b = path.read_bytes()
    clen = struct.unpack_from("<I", b, 12)[0]
    g = json.loads(b[20:20 + clen])
    mats = [m.get("name") for m in g.get("materials", [])]
    nodes = [n for n in g.get("nodes", []) if "mesh" in n]
    prims = sum(len(g["meshes"][n["mesh"]]["primitives"]) for n in nodes)
    return len(nodes), prims, mats, sorted(n.get("name") for n in nodes)


def front_of(name):
    """The facing `roofs.front_facing` reads off the preset's own spec."""
    spec = presets.empty_rowhome(name=name, **presets.EMPTY_ROWHOMES[name])
    walls = [spec_types.ExtWall(wall=w["wall"], story=w["story"],
                                openings=[spec_types.Opening(kind=o["kind"], tag=o.get("tag"))
                                          for o in w["openings"]])
             for w in spec["ext_walls"]]
    return roofs.front_facing(types.SimpleNamespace(ext_walls=walls))


out.mkdir(parents=True, exist_ok=True)
for bid in sys.argv[5:] or ["gs_empty_rowhome_b"]:
    args = presets.EMPTY_ROWHOMES[bid]
    raw = json.loads((F / "deli_counter" / "build" / f"{bid}.slots.json").read_text(encoding="utf-8"))
    (roof,) = [s for s in raw["slots"] if s.get("role") == "roof"]
    if args.get("antenna"):
        roof["antenna"] = True
    if args.get("dish"):
        roof["dish"] = True
    roof["front"] = front_of(bid)
    fx = framing.roof_fixture_orders(slots.parse(raw), trim.build_sheet(size=64, seed=1999)[1], seed=9080)
    src = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
    man = json.loads(src.read_text(encoding="utf-8"))
    base_glb = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}_dressing.glb"
    man["orders"] = list(man["orders"]) + fx
    dst = out / bid
    dst.mkdir(parents=True, exist_ok=True)
    mpath = dst / f"{bid}.preflight.dressing.json"
    mpath.write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"== {bid}: front {roof['front']}; antenna {bool(args.get('antenna'))}, "
          f"dish {bool(args.get('dish'))}")
    for o in fx:
        print(f"  order {o['cover']}: pos {o['pos']} size2 {o['size2']} tangent {o['tangent']}")
    cmd = [BLENDER, "--background", "--python", str(zoo_dir / "tools" / "zoo_cli.py"), "--",
           "--dress", str(mpath), "--out", str(dst),
           "--skins", str(WS / "gas_block_001.pixelcoat_build" / "out"),
           "--theme", "delco_1997", "--seed", "9080", "--no-blend"]
    r = subprocess.run(cmd, cwd=str(zoo_dir), capture_output=True, text=True, timeout=1200)
    print(f"  zoo exit {r.returncode}")
    for line in r.stdout.splitlines():
        if line.startswith("[zoo]") and ("covers" in line or "merge" in line or "refused" in line):
            print("  " + line)
    if r.returncode != 0:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
        continue
    glb = dst / f"{bid}_dressing.glb"
    for label, path in (("before", base_glb), ("after", glb)):
        if path.exists():
            n, p, mats, names = glb_summary(path)
            print(f"  {label}: {n} mesh nodes, {p} primitives; materials {mats}")
            print(f"    nodes {names}")
    shell = F / "deli_counter" / "build" / f"{bid}.glb"
    rr = subprocess.run([BLENDER, "--background", "--python", str(HERE / "render_roof.py"), "--",
                         str(shell), str(glb), str(dst / f"{bid}_roof")],
                        capture_output=True, text=True, timeout=600)
    print(f"  render exit {rr.returncode}: " + " ".join(
        line for line in rr.stdout.splitlines() if line.startswith("[render]")))
    if rr.returncode != 0:
        print(rr.stderr[-1200:])
