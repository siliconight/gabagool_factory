"""One arm of the sodium-pool question: the slice's walk copy, its streetlights given a longer BAKE range and a scaled
energy, re-baked with Level Factory's own bake, and shot from the street.

    python docs/findings/sodium_pools/arm.py <walk project> <tag> --bake-range R --energy-x K

The arm is a COPY under `_scratch/sodium_pools/<tag>` (the source is only read). Two edits to the copy, both what a Lux
change would make, so the frame is the frame that change would ship:

* its vendored `lux_light_loader.gd` `stretch_bake_ranges` lends a `LuxStreetlightRig`'s `bake_range` as it already
  lends a fluorescent row's (Lux 0.80.0) -- the lamp's live range is untouched, so no dynamic object pays for it;
* every `Streetlight (baked)` rig in `presentation/lux.applied.tscn` takes `bake_range = R` (0 leaves it out) and its
  energy times K.

Then `tools/lux_rebake.py` bakes it and `tools/look_shots.py` shoots the slice's street stations
(`docs/findings/slice_look/shoot_street.py`'s), in the level's light. Prints what it changed and each frame's mean
and median; the frames are the evidence.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import look_shots  # noqa: E402

ST = ["ave_east:-120.0,1.7,30.6,60.0,4.0,30.6",
      "ave_west:110.0,1.7,30.6,-90.0,4.0,30.6",
      "sidewalk_east:-45.0,1.7,25.5,40.0,2.0,23.5",
      "gas_front:-86.0,1.7,33.0,-86.0,3.0,0.0",
      "bank_oblique:8.0,1.7,32.0,-18.0,5.0,18.0",
      "card_front:25.0,1.7,31.0,25.0,3.5,18.0",
      "road_down:-35.0,1.7,31.5,-70.0,0.0,31.5"]

STRETCH_OLD = """		if not (n is LuxFluorescentRig):
			continue
		var rig: LuxLightRig = (n as LuxFluorescentRig).rig
"""
STRETCH_NEW = """		if not (n is LuxFluorescentRig or n is LuxStreetlightRig):
			continue
		var rig: LuxLightRig = n.get("rig") as LuxLightRig
"""
RIG = re.compile(r'(\[sub_resource type="Resource" id="[^"]+"\]\nscript = ExtResource\("[^"]+"\)\n'
                 r'(?:bake_mode = \d\n)?rig_name = &"Streetlight \(baked\)"\n(?:[a-z_]+ = [^\n]*\n)*?)'
                 r'energy = ([0-9.e+-]+)\nlight_range = ([0-9.]+)\n')


def _read(p: Path):
    """A file's text with LF endings, and whether it was CRLF -- a vendored copy can be either, and must stay what
    it was."""
    d = p.read_bytes()
    crlf = d.count(b"\r\n")
    assert crlf in (0, d.count(b"\n")), f"{p}: mixed endings"
    return d.decode("utf-8").replace("\r\n", "\n"), crlf > 0


def _write(p: Path, text: str, crlf: bool) -> None:
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("tag")
    ap.add_argument("--bake-range", type=float, default=0.0)
    ap.add_argument("--energy-x", type=float, default=1.0)
    ap.add_argument("--spot-angle", type=float, default=0.0)
    ap.add_argument("--skin", action="append", default=[],
                    help="NAME=SRC: replace skins/NAME in the copy with SRC (a re-minted Pixelcoat map)")
    a = ap.parse_args()
    base = ROOT / "_scratch" / "sodium_pools"
    src = base / (a.tag + "_src")
    dst = base / a.tag
    for p in (src, dst):
        if p.exists():
            print(f"REFUSED: {p} exists")
            return 1
    base.mkdir(parents=True, exist_ok=True)
    shutil.copytree(a.project, src, ignore=shutil.ignore_patterns(".godot"))
    loader = src / "runtime" / "lux" / "runtime" / "lux_light_loader.gd"
    t, crlf = _read(loader)
    if t.count(STRETCH_NEW) == 1:
        print(f"{a.tag}: the copy's Lux lends a street lamp its bake range already (>= 0.82.0)")
    else:
        assert t.count(STRETCH_OLD) == 1, "stretch_bake_ranges is neither the 0.80.0 nor the 0.82.0 text"
        _write(loader, t.replace(STRETCH_OLD, STRETCH_NEW), crlf)
    for sk in a.skin:
        name, s_src = sk.split("=", 1)
        target = src / "skins" / name
        assert target.is_file(), f"no skins/{name} in the copy"
        shutil.copyfile(s_src, target)
        print(f"{a.tag}: skins/{name} <- {s_src}")
    if a.spot_angle > 0.0:
        # the rig rebuilds its lamps on load with a fixed 55 degree cone; a streetlight's alone takes the arm's
        rig_gd = src / "runtime" / "lux" / "runtime" / "rigs" / "lux_streetlight_rig.gd"
        g, g_crlf = _read(rig_gd)
        old = "\t\tlamp.spot_angle = 55.0\n"
        assert g.count(old) == 1, "the rig's cone is not the fixed 55.0"
        new = ('\t\tlamp.spot_angle = %r if String(r.rig_name).begins_with("Streetlight") else 55.0\n'
               % a.spot_angle)
        _write(rig_gd, g.replace(old, new), g_crlf)
    scene = src / "presentation" / "lux.applied.tscn"
    s, s_crlf = _read(scene)
    n = 0

    def edit(m):
        nonlocal n
        n += 1
        e = float(m.group(2)) * a.energy_x
        tail = f"energy = {e!r}\nlight_range = {m.group(3)}\n"
        if a.bake_range > 0.0:
            tail += f"bake_range = {a.bake_range!r}\n"
        return m.group(1) + tail

    s = RIG.sub(edit, s)
    print(f"{a.tag}: {n} streetlight rig(s), bake_range {a.bake_range}, energy x {a.energy_x}")
    if n == 0:
        print("REFUSED: no streetlight rig matched")
        return 1
    _write(scene, s, s_crlf)
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "lux_rebake.py"), str(src), str(dst)])
    shutil.rmtree(src)
    if r.returncode != 0:
        print(f"rebake exit {r.returncode}")
        return 1
    got = look_shots.shoot(str(dst), str(base / ("frames_" + a.tag)), stations=ST, timeout=1200)
    for sh in got.get("shots", []):
        if sh["name"] in [x.split(":")[0] for x in ST]:
            print(a.tag, sh["name"], round(sh["mean"], 1), sh["p50"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
