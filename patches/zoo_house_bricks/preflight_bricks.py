"""Pre-flight for a house's own brick: one rowhome's kit, built by the Zoo checked
out now from Deli Counter's freshly built slots, against a delco_1997 skin
library built by the Pixelcoat checked out now.

    python preflight_bricks.py <skins_dir> <out_dir> [<building> ...]

Prints, per building, Zoo's own "[zoo] skin:" lines for the brick kinds (the
pack each kind resolved to, or the flat fallback) and every wall-family
module's stem and the materials its GLB carries. A brown house's walls must
be `_mbrick_brown` modules in `M_Skin_brick_brown_delco_1997`.
"""
import json
import pathlib
import struct
import subprocess
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
BLENDER = r"C:\blender\blender.exe"

skins, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for bid in sys.argv[3:] or ["gs_empty_rowhome_c"]:
    dst = out / bid
    dst.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([BLENDER, "--background", "--python", str(F / "zoo" / "tools" / "zoo_cli.py"), "--",
                        "--build-kit", str(F / "deli_counter" / "build" / f"{bid}.slots.json"),
                        "--out", str(dst), "--skins", str(skins), "--theme", "delco_1997",
                        "--seed", "9080", "--no-blend"],
                       cwd=str(F / "zoo"), capture_output=True, text=True, timeout=1800)
    print(f"== {bid}: kit exit {r.returncode}")
    for line in sorted({l for l in r.stdout.splitlines() if l.startswith("[zoo] skin:") and "brick" in l}):
        print("  " + line[:150])
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])
        continue
    for p in sorted(dst.glob("*.glb")):
        if not p.name.startswith(("wall", "window", "doorway")):
            continue
        b = p.read_bytes()
        g = json.loads(b[20:20 + struct.unpack_from("<I", b, 12)[0]])
        print(f"  {p.name:62s} {sorted({m.get('name') for m in g.get('materials', [])})}")
