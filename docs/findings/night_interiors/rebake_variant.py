"""Re-bake a scratch copy of a walk export, optionally with a lighting change.

    python rebake_variant.py <walk_copy> <dest> <variant> [--godot EXE]

variant:
  control   -- no change: proves a re-bake reproduces the shipped lightmap
  nowindows -- the level's own bake without Lux's window lights (`LuxDaylight`)
  clear2cm  -- every fluorescent-rig lamp at mount 0.0, which sits on the
               bottom of its own bulb (Bare Bulb, Counter Accent), hung 2 cm
               lower. NOT the wall pack: its streetlight rig already hangs
               the lamp LAMP_HANG_M (0.10) under the anchor.

The copy's entry is pointed back at the presentation scene and its old bake
files removed, because Level Factory's `light_bake.bake` refuses (and on a
refusal deletes the bake files of) a package already retargeted at
bake.tscn. Then `bake()` runs exactly as the export runs it. Frames: none
here; measure with night_interior_census.py afterwards.
"""
import os
import re
import shutil
import sys
from pathlib import Path

FACTORY = Path(r"C:\Projects\gabagool_studios\gabagool_factory")
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import light_bake   # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
ON_HARDWARE = ("Bare Bulb (baked)", "Counter Accent (incandescent)")
CLEAR = -0.02


def clear_lamps(pres: Path) -> int:
    text = pres.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^\[)", text, flags=re.M)
    n = 0
    for i, b in enumerate(blocks):
        if not b.startswith('[sub_resource type="Resource"'):
            continue
        m = re.search(r'^rig_name = &"([^"]+)"', b, re.M)
        if not m or m.group(1) not in ON_HARDWARE:
            continue
        new, k = re.subn(r"^mount_height = 0\.0$", "mount_height = %s" % CLEAR, b, flags=re.M)
        if k != 1:
            raise SystemExit("rig %r has no 'mount_height = 0.0' line" % m.group(1))
        blocks[i] = new
        n += 1
    pres.write_text("".join(blocks), encoding="utf-8", newline="\n")
    return n


FILL_PREFIX = "LuxBakeFill_"


def room_probes(pres: Path) -> list:
    """Every interior ReflectionProbe in the presentation scene, in the site
    frame (Godot metres, y up): ``{name, center, size, color, energy}``.
    Refuses a probe whose parent carries a transform -- the frame would be
    wrong and nothing here composes it."""
    text = pres.read_text(encoding="utf-8")
    parents_with_xf = set(re.findall(r'^\[node name="([^"]+)" type="Node3D" parent="\."[^\]]*\]\ntransform', text, re.M))
    out = []
    # the body: lines up to the next header. `[^\[\n]`, not `[^\[]` -- the
    # latter matches a blank line's newline and runs on through every node
    # after it (the first dry run read 1 probe, carrying the file's LAST
    # transform and size).
    for m in re.finditer(r'^\[node name="([^"]+)" type="ReflectionProbe" parent="([^"]+)"[^\]]*\]\n((?:[^\[\n].*\n|\n)*)', text, re.M):
        name, parent, body = m.group(1), m.group(2), m.group(3)
        if parent in parents_with_xf:
            raise SystemExit("probe %s sits under a transformed parent %s" % (name, parent))
        kv = dict(re.findall(r"^(\w+) = (.+)$", body, re.M))
        if kv.get("interior") != "true":
            continue
        xf = [float(v) for v in re.search(r"Transform3D\(([^)]*)\)", kv["transform"]).group(1).split(",")]
        size = [float(v) for v in re.search(r"Vector3\(([^)]*)\)", kv["size"]).group(1).split(",")]
        col = [float(v) for v in re.search(r"Color\(([^)]*)\)", kv.get("ambient_color", "Color(1, 1, 1, 1)")).group(1).split(",")]
        out.append({"name": name, "center": xf[9:12], "size": size, "color": col[:3],
                    "energy": float(kv.get("ambient_color_energy", "1.0"))})
    return out


#: Lux's ROOM_AMBIENT_MARGIN: a probe is its room's box plus this a side.
PROBE_MARGIN = 0.1
#: v2: a fill at a person's head height over the floor, under every ceiling
#: fixture (a bulb hangs at 2.6 m in a 3.2 m storey, a tube at 2.65+).
FILL_HEIGHT = 1.7
#: v2: one fill per cell this wide at most, the room's energy split between
#: them, so a fill that does land inside a piece loses one cell, not a room.
FILL_CELL = 6.0
#: v4: a local fill's reach, in cells
LOCAL_REACH = 1.5


def bulb_points(pres: Path) -> list:
    """Site positions of every rig whose resource is a Bare Bulb: the rooms
    Deli Counter lights with pendants (the walker, 2026-09-28: "keep
    pendants moody"). Rig nodes under a transform-free container only."""
    text = pres.read_text(encoding="utf-8")
    bulb_res = set()
    for m in re.finditer(r'^\[sub_resource type="Resource" id="([^"]+)"\]\n((?:[^\[\n].*\n|\n)*)', text, re.M):
        if re.search(r'^rig_name = &"Bare Bulb', m.group(2), re.M):
            bulb_res.add(m.group(1))
    out = []
    for m in re.finditer(r'^\[node name="[^"]+" type="Node3D" parent="LuxFixtureLights"[^\]]*\]\n((?:[^\[\n].*\n|\n)*)', text, re.M):
        body = m.group(1)
        r = re.search(r'^rig = SubResource\("([^"]+)"\)', body, re.M)
        t = re.search(r"^transform = Transform3D\(([^)]*)\)", body, re.M)
        if r and t and r.group(1) in bulb_res:
            v = [float(x) for x in t.group(1).split(",")]
            out.append((v[9], v[10], v[11]))
    return out


def is_moody(probe: dict, bulbs: list) -> bool:
    (cx, cy, cz), (sx, sy, sz) = probe["center"], probe["size"]
    return any(abs(x - cx) <= sx / 2 and abs(y - cy) <= sy / 2 and abs(z - cz) <= sz / 2 for x, y, z in bulbs)


def fill_nodes(probes: list, energy: float, layout: str = "grid", moody=None, moody_share: float = 1.0) -> str:
    """Bake-only omnis for every UNTINTED room probe (a tinted probe is a
    club room, dark by design), flat falloff (attenuation 0) out past the
    far corner, static so the lightmapper takes them.

    layout "centre" (v1) -- ONE fill at the room's centre, a quarter of its
    height above the probe's middle. REFUTED, kept: in a 3.2 m storey that
    is 2.3 m, the height a bare bulb hangs at, and the room's centre is where
    the middle bulb of a row hangs -- deli_a01's deli counter fill stood at
    (-71.5, 2.3, -2.51), exactly its centre bulb's anchor, inside the glass.
    The four deli basement rooms and the deli counter came out unchanged.

    layout "grid" (v2) -- one fill per FILL_CELL cell at FILL_HEIGHT over the
    floor, the room's `energy` split evenly between them, each reaching the
    whole room. Works where v1 did not, and leaves a big room dark: a floor
    point is lit mostly by the fills near it, so a fixed room energy split
    n ways falls as 1/size (office lobby, 34 x 12 m: 4.7 -> 10.1).

    layout "local" (v4) -- the same cells, but `energy` is EACH fill's, and
    each reaches only LOCAL_REACH cells, flat inside it: a floor point sees
    the fills near it whatever the room's size. Under a fill against the
    point between four, about 1.3x."""
    lines = []
    for p in probes:
        if any(abs(c - 1.0) > 1e-6 for c in p["color"]):
            continue
        cx, cy, cz = p["center"]
        sx, sy, sz = p["size"]
        room_energy = energy * (moody_share if moody and p["name"] in moody else 1.0)
        if layout == "centre":
            reach = 0.5 * (sx * sx + sy * sy + sz * sz) ** 0.5 * 1.1
            points = [((cx, cy + 0.25 * sy, cz), reach, room_energy)]
        else:
            rx, rz = sx - 2 * PROBE_MARGIN, sz - 2 * PROBE_MARGIN
            floor = cy - sy / 2.0 + PROBE_MARGIN
            nx, nz = max(1, int(-(-rx // FILL_CELL))), max(1, int(-(-rz // FILL_CELL)))
            points = []
            for i in range(nx):
                for k in range(nz):
                    px = cx - rx / 2.0 + rx * (i + 0.5) / nx
                    pz = cz - rz / 2.0 + rz * (k + 0.5) / nz
                    far = max(((px - x) ** 2 + (pz - z) ** 2) ** 0.5
                              for x in (cx - rx / 2, cx + rx / 2) for z in (cz - rz / 2, cz + rz / 2))
                    if layout == "local":
                        reach = LOCAL_REACH * FILL_CELL
                        points.append(((px, floor + FILL_HEIGHT, pz), reach, room_energy))
                    else:
                        reach = (far * far + (sy - FILL_HEIGHT) ** 2) ** 0.5 * 1.2
                        points.append(((px, floor + FILL_HEIGHT, pz), reach, room_energy / (nx * nz)))
        for j, (pos, reach, e) in enumerate(points):
            lines += ['', '[node name="%s%s_%d" type="OmniLight3D" parent="."]' % (FILL_PREFIX, p["name"], j),
                      "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %.4f, %.4f, %.4f)" % pos,
                      "light_energy = %.5f" % e,
                      "light_bake_mode = 1",
                      "omni_range = %.3f" % reach,
                      "omni_attenuation = 0.0"]
    return "\n".join(lines) + "\n"


def strip_daylight(pres: Path) -> int:
    """Remove Lux's window lights (the `LuxDaylight` container and every node
    under it) from the presentation scene: what a level's windows add, by
    their absence. Returns the nodes removed."""
    text = pres.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^\[)", text, flags=re.M)
    keep = [b for b in blocks if not (b.startswith('[node name="LuxDaylight"')
                                      or re.match(r'\[node [^\]]*parent="LuxDaylight', b))]
    pres.write_text("".join(keep), encoding="utf-8", newline="\n")
    return len(blocks) - len(keep)


def strip_fills(scene: Path) -> int:
    text = scene.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^\[)", text, flags=re.M)
    keep = [b for b in blocks if not b.startswith('[node name="%s' % FILL_PREFIX)]
    scene.write_text("".join(keep), encoding="utf-8", newline="\n")
    return len(blocks) - len(keep)


def main(argv):
    src, dest, variant = Path(argv[0]), Path(argv[1]), argv[2]
    godot = argv[argv.index("--godot") + 1] if "--godot" in argv else GODOT
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    for f in light_bake.BAKE_FILES:
        (dest / f).unlink(missing_ok=True)
    entry = dest / "mission.tscn"
    t = entry.read_text(encoding="utf-8")
    old, new = "load('res://bake.tscn')", "load('res://%s')" % light_bake.PRESENTATION
    if t.count(old) == 1:
        entry.write_text(t.replace(old, new), encoding="utf-8", newline="\n")
    elif t.count(new) != 1:
        # the unbaked copy (`proj_unbaked`) already points at the scene: the
        # only 9190 source left once cold run 9192's walk step overwrote
        # `_runs/walk_export_restaurant_row_001` with its own copy
        raise SystemExit("mission.tscn loads neither bake.tscn nor the presentation scene once")
    fill = None
    layout = "centre"
    moody_share = 1.0
    if variant.startswith("filllocal"):
        # filllocal0.025 -> 0.025 EACH fill, 6 m cells, reach 1.5 cells, half in a bulb-lit room (v4)
        fill, layout, moody_share = float(variant[9:]), "local", 0.5
    elif variant.startswith("fillmoody"):
        # fillmoody0.08 -> 0.08 a room, half of it in a bulb-lit room, 8 m cells (v3)
        fill, layout, moody_share = float(variant[9:]), "grid", 0.5
        global FILL_CELL
        FILL_CELL = 8.0
    elif variant.startswith("fillgrid"):
        fill, layout = float(variant[8:]), "grid"     # fillgrid0.08 -> 0.08, v2
    elif variant.startswith("fill"):
        fill = float(variant[4:])          # fill0.08 -> 0.08, v1 (refuted)
    if variant == "clear2cm" or fill is not None:
        print("lamps hung clear of their hardware:", clear_lamps(dest / light_bake.PRESENTATION))
    elif variant == "nowindows":
        # the level's own bake (whatever its Lux lays) without its window lights
        print("window light nodes removed:", strip_daylight(dest / light_bake.PRESENTATION))
    elif variant != "control":
        raise SystemExit("unknown variant " + variant)
    if fill is not None:
        probes = room_probes(dest / light_bake.PRESENTATION)
        moody = None
        if moody_share != 1.0:
            bulbs = bulb_points(dest / light_bake.PRESENTATION)
            moody = {p["name"] for p in probes if is_moody(p, bulbs)}
            print("bulb rigs: %d; bulb-lit rooms (fill x %s): %s" % (len(bulbs), moody_share, sorted(moody)))
        extra = fill_nodes(probes, fill, layout, moody, moody_share)
        print("room probes: %d, fills: %d (%s layout), %s a room" % (len(probes), extra.count("OmniLight3D"),
                                                                    layout, fill))
        base = light_bake.bake_scene_text
        light_bake.bake_scene_text = lambda: base() + extra
    report = light_bake.bake(dest, godot)
    print("ok:", report.get("ok"), "reason:", report.get("reason"), "editor_s:", report.get("editor_s"),
          "rigs:", report.get("rigs"), "users:", (report.get("result") or {}).get("users"))
    if fill is not None and report.get("ok"):
        print("fills stripped from the shipped bake.tscn:", strip_fills(dest / light_bake.BAKE_SCENE))


if __name__ == "__main__":
    main(sys.argv[1:])
