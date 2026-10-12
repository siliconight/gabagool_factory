"""What the street lights' shadow options look like on a body that moves (roadmap 240, the pole line's
price; the walker, 2026-10-12: "What do you think? What helps us learn?").

    python docs/findings/pole_line/shadow_options.py            # the frames and the sheet
    python docs/findings/pole_line/shadow_options.py --price    # and one station pass an arm (draws)

A steady street light is baked: its shadows on the street are in the lightmap, and its shadow map at
runtime shades only what is not -- a body. So the options are compared on bodies: two grey capsules the
crew body's size (0.35 m radius, 1.8 m tall), standing in the road 0.7 m off the lens line of two
STEADY lights of cold run 9264's package -- pole 22 (shadowed as built, and the first to lose its map
at a budget of 4: Lux hands the twelve out by rank and then by name, the lane's two lamps and poles 20
and 21 first) and pole 24, 60 m from the far camera. Four arms of the same copy:

  built     as the package runs: twelve shadow maps, the street lights first
  budget4   `LuxRoot.shadow_caster_budget = 4` (the Low and Compatibility tiers' figure)
  budget0   no shadow map at all
  fade30    every steady street light faded out WHOLE past 30 m from the camera (Godot's
            `distance_fade_begin` 30, `_length` 5, its shadow with it), set in the rig vendored into
            the copy, where `_rebuild()` builds the lamps at runtime; a cycling light, a wall pack and a
            canopy wash keep theirs

Stations (Godot frame: x, height, -plan y): `near` stands 6.7 m from the pole-22 body; `far` looks east
down the road at the pole-24 body 60 m off, and the sheet adds that body enlarged three times. The
copies are made under `_scratch/shadow_options/` and removed; the frames stay under
`_scratch/frames_shadow_options/`. It measures and stops.
"""
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = F / "workspaces" / "cold-9264-ws" / ".level_factory" / "exports" / "LF_restaurant_row_001.portable-godot"
SCR = F / "_scratch" / "shadow_options"
FR = F / "_scratch" / "frames_shadow_options"
OUT = F / "docs" / "findings" / "pole_line"
ARMS = ("built", "budget4", "budget0", "fade30")
BODIES = {"body_pole22": (-15.1, 0.9, 24.4), "body_pole24": (48.3, 0.9, 24.4)}
STATIONS = ["--station", "near:-9.1,1.6,21.4,-15.1,0.6,24.4",
            "--station", "far:-12.0,1.7,22.0,48.3,1.5,24.4"]

BODY_SUBS = ('[sub_resource type="CapsuleMesh" id="Body_probe_mesh"]\n'
             "radius = 0.35\n"
             "height = 1.8\n\n"
             '[sub_resource type="StandardMaterial3D" id="Body_probe_mat"]\n'
             "albedo_color = Color(0.55, 0.55, 0.55, 1)\n"
             "roughness = 0.8\n\n")
RIG_ANCHOR = "\t\tlamp.shadow_enabled = r.shadows_enabled\n"
RIG_FADE = (RIG_ANCHOR
            + "\t\tif String(r.rig_name).contains(\"Streetlight\") and r.failing_kind == LuxFailing.NONE:\n"
            + "\t\t\tlamp.distance_fade_enabled = true\n"
            + "\t\t\tlamp.distance_fade_begin = 30.0\n"
            + "\t\t\tlamp.distance_fade_length = 5.0\n"
            + "\t\t\tlamp.distance_fade_shadow = 30.0\n")


def _bodies(copy):
    scene = copy / "presentation" / "lux.applied.tscn"
    text = scene.read_text(encoding="utf-8")
    first = text.find("\n[node ")
    if first < 0 or "Body_probe_mesh" in text:
        sys.exit("UNKNOWN SHAPE: %s" % scene)
    nodes = ""
    for name, (x, y, z) in BODIES.items():
        nodes += ('\n[node name="%s" type="MeshInstance3D" parent="."]\n'
                  "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %g, %g, %g)\n"
                  'mesh = SubResource("Body_probe_mesh")\n'
                  'material_override = SubResource("Body_probe_mat")\n'
                  "gi_mode = 2\n" % (name, x, y, z))
    text = text[:first + 1] + BODY_SUBS + text[first + 1:].rstrip("\n") + "\n" + nodes
    scene.write_text(text, encoding="utf-8", newline="\n")


def _budget(copy, n):
    scene = copy / "presentation" / "lux.applied.tscn"
    text = scene.read_text(encoding="utf-8")
    ids = re.findall(r'^\[ext_resource type="Script"[^\]]*path="[^"]*/lux_root\.gd" id="([^"]+)"\]', text, re.M)
    anchor = '\nscript = ExtResource("%s")' % ids[0] if len(ids) == 1 else None
    if anchor is None or text.count(anchor) != 1:
        sys.exit("UNKNOWN SHAPE: LuxRoot in %s" % scene)
    scene.write_text(text.replace(anchor, anchor + "\nshadow_caster_budget = %d" % n), encoding="utf-8",
                     newline="\n")


def _fade(copy):
    rig = copy / "runtime" / "lux" / "runtime" / "rigs" / "lux_streetlight_rig.gd"
    raw = rig.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(RIG_ANCHOR) != 1:
        sys.exit("UNKNOWN SHAPE: the rig's shadow line in %s" % rig)
    rig.write_bytes(text.replace(RIG_ANCHOR, RIG_FADE).replace("\n", eol).encode("utf-8"))


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    FR.mkdir(parents=True, exist_ok=True)
    for arm in ARMS:
        copy = SCR / arm
        shutil.copytree(PKG, copy)
        _bodies(copy)
        if arm == "budget4":
            _budget(copy, 4)
        elif arm == "budget0":
            _budget(copy, 0)
        elif arm == "fade30":
            _fade(copy)
        shots = FR / ("shots_" + arm)
        with open(FR / ("shots_%s.json" % arm), "w") as out, open(FR / ("shots_%s.err" % arm), "w") as err:
            rc = subprocess.run([sys.executable, str(F / "tools" / "look_shots.py"), str(copy), "--scene",
                                 "mission.tscn", "--out", str(shots), "--json"] + STATIONS,
                                stdout=out, stderr=err, stdin=subprocess.DEVNULL, timeout=1200).returncode
        print("%-8s shots exit %d" % (arm, rc), flush=True)
        if "--price" in sys.argv:
            rep = OUT / "shadow_options" / ("perf_%s.json" % arm)
            rep.parent.mkdir(parents=True, exist_ok=True)
            rc = subprocess.run([sys.executable, str(F / "level_factory" / "tools" / "perf_stations_run.py"),
                                 str(copy), "--json", str(rep)], capture_output=True, text=True,
                                stdin=subprocess.DEVNULL, timeout=1800).returncode
            print("%-8s price pass exit %d (%s)" % (arm, rc, "measured" if rep.exists() else "NOT MEASURED"),
                  flush=True)
        shutil.rmtree(copy)
    shutil.rmtree(SCR, ignore_errors=True)
    from PIL import Image
    for arm in ARMS:   # the far body enlarged: 48.3 m east in the far frame's middle
        im = Image.open(FR / ("shots_" + arm) / "far.png")
        w, h = im.size
        crop = im.crop((w // 2 - 160, h // 2 - 70, w // 2 + 160, h // 2 + 110))
        crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST).save(FR / ("shots_" + arm) / "far_body.png")
    args = []
    for station in ("near", "far", "far_body"):
        for arm in ARMS:
            args.append("%s %s=%s" % (arm, station, FR / ("shots_" + arm) / (station + ".png")))
    subprocess.run([sys.executable, str(F / "docs" / "findings" / "edge_menu" / "sheet.py"),
                    str(OUT / "shadow_options.png"), "4"] + args, check=True)
    print("sheet: docs/findings/pole_line/shadow_options.png")


if __name__ == "__main__":
    main()
