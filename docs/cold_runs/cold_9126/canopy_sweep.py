"""Price a brighter canopy: scale the four canopy washes' baked energy in a
walk copy, shoot fixed forecourt stations, read the pad and the pumps.

The washes' energy is BAKED into presentation/lux.applied.tscn at export --
on each rig resource (`rig_name = &"Canopy Wash (baked)"`, `energy = ...`) and
on its SpotLight3D (`light_energy = ...`) -- and Lux's `energy_for` is linear
in the level, so k x CANOPY_WASH_LEVEL is k x those numbers. k = 1 is shot
twice: the control. The scene is restored byte for byte at the end.

The scene is CRLF. Patterns are matched on an LF copy and the file is written
back in its own endings: the first pass matched the rigs NOWHERE in the CRLF
text while the lights matched, and the 8-line guard below stopped it.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WALK = ROOT / "_runs" / "walk_export_club_block_014"
SCENE = WALK / "presentation" / "lux.applied.tscn"
HERE = ROOT / "_runs" / "canopy_sweep"
STATIONS = [
    "01_street_approach:120,1.7,10,90,2.5,10",
    "03_lane:110,1.6,13,94,1.3,13",
    "04_pump_face:103,1.45,12.4,103,1.15,16",
    "05_pump_back:103,1.45,19.6,103,1.15,16",
    "07_pad:100,1.7,13,94,0.0,13",
]
REGIONS = {"04_pump_face": (690, 355, 910, 610), "05_pump_back": (690, 355, 910, 600),
           "07_pad": (0, 300, 1600, 900)}
NL, CRNL = chr(10), chr(13) + chr(10)

orig = SCENE.read_bytes()
CRLF = CRNL.encode() in orig
text = orig.decode("utf-8").replace(CRNL, NL)

RIG = re.compile(r'(rig_name = &"Canopy Wash \(baked\)"\nlight_color = [^\n]*\nenergy = )([0-9.eE+-]+)')
LIGHT = re.compile(r'(parent="LuxClub/b\d+_canopy_roof_wash_\d+"[^\n]*\n(?:[^\n\[]*\n)*?light_energy = )([0-9.eE+-]+)')


def scaled(k):
    """The scene with every canopy wash's energy x k."""
    out = RIG.sub(lambda m: m.group(1) + repr(float(m.group(2)) * k), text)
    return LIGHT.sub(lambda m: m.group(1) + repr(float(m.group(2)) * k), out)


def write(body):
    SCENE.write_bytes((body.replace(NL, CRNL) if CRLF else body).encode("utf-8"))


def lum(px):
    r, g, b = px
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def read(png, rect):
    from PIL import Image
    im = Image.open(png).convert("RGB")
    x0, y0, x1, y1 = rect
    v = sorted(lum(im.getpixel((x, y))) for y in range(y0, y1, 2) for x in range(x0, x1, 2))
    n = len(v)
    return {"p50": round(v[n // 2], 1), "mean": round(sum(v) / n, 1),
            "clip_pct": round(100.0 * sum(1 for x in v if x >= 250) / n, 2)}


rows = {}
try:
    probe = scaled(2.0)
    changed = sum(1 for a, b in zip(text.split(NL), probe.split(NL)) if a != b)
    print("lines scaled per run:", changed, flush=True)
    assert changed == 8, changed          # four rigs, four lights
    for tag, k in (("k1", 1.0), ("k1_control", 1.0), ("k2", 2.0), ("k3", 3.0), ("k4", 4.0)):
        write(scaled(k))
        out = HERE / ("shots_" + tag)
        if out.exists():
            shutil.rmtree(out)
        cmd = [sys.executable, str(ROOT / "tools" / "look_shots.py"), str(WALK), "--out", str(out), "--json"]
        for st in STATIONS:
            cmd += ["--station", st]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        assert r.returncode == 0, r.stderr[-600:]
        frames = {s["name"]: round(s["mean"], 1) for s in json.loads(r.stdout)["shots"]
                  if s["name"][0].isdigit()}
        rows[tag] = {"k": k, "frames": frames,
                     **{n: read(out / (n + ".png"), rect) for n, rect in REGIONS.items()}}
        print(tag, json.dumps(rows[tag]), flush=True)
finally:
    SCENE.write_bytes(orig)
    assert SCENE.read_bytes() == orig
(HERE / "sweep.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
