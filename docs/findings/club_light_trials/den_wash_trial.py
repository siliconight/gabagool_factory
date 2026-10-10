"""Trial wall washes in a den's rooms on a copy of a walk project: re-bake, measure, frame.

    python den_wash_trial.py <walk project> <work dir> <wall level> [--fill SHARE] [--rooms tinted|all]
                             [--pitch M] [--inset M] [--aim-h M] [--angle DEG] [--keep]

THE QUESTION (roadmap 219 note 1). The club is lit in pools with black between them, and a room
station looks mostly at the black (`README.md` here: a den fill at half share reaches a median of
3, the washes x3 a median of 1). The comps light the WALLS. This lays, in the copy only, a row of
wall washers along every wall of every den room: bake-only spots like Lux's room fills, laid
before the bake and freed before the save, so the level carries nothing at run time.

Each washer:
- hangs `--inset` (0.8 m) in from its wall, 0.25 m under the ceiling, every `--pitch` (3.0 m)
  along it, the wall's washers spaced evenly;
- aims at the wall `--aim-h` (1.0 m) over the floor, a cone `--angle` (50 deg) half-angle, rim
  0.5, range 4.0 m, attenuation 2;
- takes the colour of the nearest club wash in its room, or the room's own tint when it has none;
- carries the energy that puts `<wall level>` x Lux's REFERENCE_POOL (0.684, a tuned club wash's
  floor value) on the wall at the aim point, solved from Lux's own closed form:
      value(d) = energy * (1 - (d / R)^4)^2 / d^2 * cos(incidence)
  so the level means the same thing in Lux's unit as every other club level.
`<wall level>` 0 lays none: the control, which must reproduce the shipped numbers.

`--fill SHARE` also fills the den rooms at SHARE of the preset's room fill, white, the way
`den_fill_trial.py` does. `--rooms all` washes a den's untinted back rooms too.

Writes under <work>: `baked/` (the re-baked copy, deleted unless --keep), `light/` (light_check's
report), `shots/` (look_shots at the club's two stations, PNG + JSON). Prints the trial's
parameters, the bake's fill line, every DEN row and each station's frame and centre figures. The
repo's Lux is not touched.

FRAME AND UNITS: Godot metres, Y up. Luma 0-255 after the grade.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

FACTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REFERENCE_POOL = 0.684
STATIONS = ["club_main:-72.2,1.6,7.0,-51.8,1.0,7.0", "club_vip:-74.2,1.6,-5.0,-59.8,1.0,-5.0",
            "club_bar:-60.0,1.6,2.0,-62.0,1.2,13.0"]

ap = argparse.ArgumentParser()
ap.add_argument("walk")
ap.add_argument("work")
ap.add_argument("level", type=float)
ap.add_argument("--fill", type=float, default=0.0)
ap.add_argument("--rooms", choices=("tinted", "all"), default="tinted")
ap.add_argument("--pitch", type=float, default=3.0)
ap.add_argument("--inset", type=float, default=0.8)
ap.add_argument("--aim-h", type=float, default=1.0)
ap.add_argument("--angle", type=float, default=50.0)
ap.add_argument("--drop", type=float, default=0.25)
ap.add_argument("--range", type=float, default=4.0)
ap.add_argument("--keep", action="store_true")
args = ap.parse_args()

src, baked = os.path.join(args.work, "src"), os.path.join(args.work, "baked")
for d in (src, baked):
    if os.path.exists(d):
        shutil.rmtree(d)
shutil.copytree(args.walk, src)

loader = os.path.join(src, "runtime", "lux", "runtime", "lux_light_loader.gd")
raw = open(loader, "rb").read()
crlf = raw.count(b"\r\n")
assert crlf == 0 or crlf == raw.count(b"\n"), "mixed line endings in the copy's loader"
t = raw.decode("utf-8").replace("\r\n", "\n")


def swap(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


# ---- the den fill, as den_fill_trial.py lays it (white) --------------------------------------
if args.fill > 0.0:
    swap("\t\tif not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR) \\\n"
         "\t\t\t\tor dens.has(_probe_building(p)):\n"
         "\t\t\tcontinue\n",
         "\t\tvar den: bool = dens.has(_probe_building(p))\n"
         "\t\tvar tinted: bool = not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR)\n"
         "\t\tif tinted and not den:\n"
         "\t\t\tcontinue\n")
    nx = "\t\tvar nx := maxi(1, ceili(room.x / BAKE_FILL_CELL_M))\n"
    swap(nx, "\t\tif den:\n\t\t\tshare = %r\n" % args.fill + nx)

# ---- the wall washers, laid in the fill's container so the bake frees them ------------------
WASHERS = """\
	# TRIAL (docs/findings/club_light_trials/den_wash_trial.py): den wall washers
	var trial_level: float = %(level)r
	if trial_level > 0.0:
		var washes: Array = []
		for n in scene_root.find_children("*", "Node3D", true, false):
			if n is LuxFluorescentRig and (n as LuxFluorescentRig).rig != null \\
					and String((n as LuxFluorescentRig).rig.rig_name).begins_with("Club Wash"):
				washes.append([(n as Node3D).global_position, (n as LuxFluorescentRig).rig.light_color])
		var laid: int = 0
		var last_energy: float = 0.0
		for p in probes:
			if not dens.has(_probe_building(p)):
				continue
			var tinted_room: bool = not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR)
			if not tinted_room and not %(all_rooms)s:
				continue
			var room := p.size - Vector3.ONE * 2.0 * ROOM_AMBIENT_MARGIN
			if room.x <= 0.0 or room.y <= 0.0 or room.z <= 0.0:
				continue
			var xf := p.global_transform
			var inv := xf.affine_inverse()
			var inset: float = %(inset)r
			var head: float = room.y * 0.5 - %(drop)r
			var aim_y: float = -room.y * 0.5 + %(aim_h)r
			var rng: float = %(range)r
			var dx: float = inset
			var dy: float = head - aim_y
			var d: float = sqrt(dx * dx + dy * dy)
			var cos_i: float = dy / d
			var win: float = 1.0 - pow(d / rng, 4.0)
			var energy_w: float = trial_level * %(pool)r * d * d / (win * win * cos_i)
			last_energy = energy_w
			if container == null:
				container = Node3D.new()
				container.name = BAKE_FILL_CONTAINER
				scene_root.add_child(container)
				container.owner = owner_node
			for side in 4:
				var on_x: bool = side < 2
				var sgn: float = 1.0 if side %% 2 == 0 else -1.0
				var length: float = room.z if on_x else room.x
				var half_depth: float = (room.x if on_x else room.z) * 0.5
				var count: int = maxi(1, int(round(length / %(pitch)r)))
				for i in count:
					var along: float = length * ((float(i) + 0.5) / float(count) - 0.5)
					var at := Vector3(along, head, sgn * (half_depth - inset))
					var aim := Vector3(along, aim_y, sgn * half_depth)
					if on_x:
						at = Vector3(sgn * (half_depth - inset), head, along)
						aim = Vector3(sgn * half_depth, aim_y, along)
					var gpos: Vector3 = xf * at
					var gaim: Vector3 = xf * aim
					var col: Color = p.ambient_color
					var best: float = INF
					for w in washes:
						var wp: Vector3 = w[0]
						var lw: Vector3 = inv * wp
						if absf(lw.x) > p.size.x * 0.5 or absf(lw.z) > p.size.z * 0.5:
							continue
						var dd: float = Vector2(wp.x - gpos.x, wp.z - gpos.z).length()
						if dd < best:
							best = dd
							col = w[1]
					var spot := SpotLight3D.new()
					spot.name = "%%s_washer_%%d_%%d" %% [String(p.name), side, i]
					spot.light_color = col
					spot.light_energy = energy_w
					spot.light_bake_mode = Light3D.BAKE_STATIC
					spot.spot_range = rng
					spot.spot_attenuation = 2.0
					spot.spot_angle = %(angle)r
					spot.spot_angle_attenuation = 0.5
					container.add_child(spot)
					spot.owner = owner_node
					spot.global_position = gpos
					spot.look_at(gaim, Vector3.UP)
					laid += 1
		print("TRIAL den washers laid: %%d, the last room's at energy %%.3f" %% [laid, last_energy])
	return container


## The site building a room probe stands in."""
params = dict(level=args.level, all_rooms="true" if args.rooms == "all" else "false",
              inset=args.inset, drop=args.drop, aim_h=args.aim_h, range=args.range,
              pool=REFERENCE_POOL, pitch=args.pitch, angle=args.angle)
swap("\treturn container\n\n\n## The site building a room probe stands in.", WASHERS % params)
open(loader, "wb").write((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))

# the energy the GDScript will solve, printed here so the reader sees it before the bake
head_minus_aim = (3.3 * 0.5 - args.drop) - (-3.3 * 0.5 + args.aim_h)
d = (args.inset ** 2 + head_minus_aim ** 2) ** 0.5
win = 1.0 - (d / args.range) ** 4
e = args.level * REFERENCE_POOL * d * d / (win * win * (head_minus_aim / d)) if args.level > 0 else 0.0
print("trial: wall level %.2f x %.3f, fill %.2f, rooms %s, pitch %.1f, inset %.2f, aim %.2f m, "
      "angle %.0f; on a 3.3 m room each washer %.2f (d %.2f m)"
      % (args.level, REFERENCE_POOL, args.fill, args.rooms, args.pitch, args.inset, args.aim_h,
         args.angle, e, d))

chk = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "gdcheck.py"), loader],
                     capture_output=True, text=True)
if chk.returncode:
    print(chk.stdout[-2000:], chk.stderr[-2000:])
    sys.exit("gdcheck refused the edited loader")

r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "lux_rebake.py"), src, baked],
                   capture_output=True, text=True)
print("rebake exit", r.returncode)
for ln in (r.stdout + r.stderr).splitlines():
    if "room fill" in ln or "TRIAL" in ln:
        print("  rebake:", ln.strip()[:240])
if r.returncode:
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit(2)
shutil.rmtree(src)

r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "light_check.py"), baked,
                    "--slots", "own", "--out", os.path.join(args.work, "light")],
                   capture_output=True, text=True)
for ln in r.stdout.splitlines():
    if " DEN " in ln:
        print(ln)

shots = os.path.join(args.work, "shots")
cmd = [sys.executable, os.path.join(FACTORY, "tools", "look_shots.py"), baked, "--out", shots]
for s in STATIONS:
    cmd += ["--station", s]
r = subprocess.run(cmd, capture_output=True, text=True)
try:
    with open(shots + ".json", encoding="utf-8") as fh:
        man = json.load(fh)
except (OSError, ValueError):
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit("look_shots wrote no manifest")
if "error" in man or not man.get("shots"):
    sys.exit("look_shots: %s" % man.get("error", "no shots"))


def under(png, limit=10):
    """Share of the frame's pixels with Rec.709 luma under `limit`, from the PNG as shot."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    n = lo = 0
    for rr, gg, bb in im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata():
        n += 1
        if 0.2126 * rr + 0.7152 * gg + 0.0722 * bb < limit:
            lo += 1
    return 100.0 * lo / n


for s in man["shots"]:
    if s["name"].startswith("club_"):
        c = s["centre"]
        print("  %-10s frame mean %6.2f p50 %3d, %4.1f%% under 10 | centre mean %6.2f p50 %3d"
              % (s["name"], s["mean"], s["p50"], under(s["png"]), c["mean"], c["p50"]))
if not args.keep:
    shutil.rmtree(baked)
