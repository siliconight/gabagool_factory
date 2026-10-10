"""Trial a den's light on a copy of a walk project: re-bake, then measure.

    python den_fill_trial.py <walk project> <work dir> <share> <tinted|white> [wash_level]

Copies the walk project to <work>/src and edits the COPY:
- <share> > 0: its Lux loader fills a den's rooms at <share> of the preset's room fill -- a tinted
  room's fill in its probe's own colour when `tinted`. <share> 0 leaves dens unfilled, as shipped.
- [wash_level] (default 12, as shipped): every `Club Wash (baked)` rig stored in
  `presentation/lux.applied.tscn` has its energy scaled by wash_level / 12.

THE WASH LEVEL IS NOT READ AT BAKE TIME. Lux computes each wash's energy when it composes the
presentation and stores it in the scene. The first wash trial set the loader's `CLUB_WASH_LEVEL`
to 36, and the club came back unchanged to the decimal: the knob was not the dial.

Re-bakes the copy to <work>/baked with tools/lux_rebake.py, runs tools/light_check.py on it at its
own slot, and prints the bake's fill line and every DEN row. Nothing outside <work> is written;
the repo's Lux is not touched.
"""
import os
import re
import shutil
import subprocess
import sys

FACTORY = r"C:\Projects\gabagool_studios\gabagool_factory"
walk, work, share, mode = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
wash = float(sys.argv[5]) if len(sys.argv) > 5 else 12.0
assert mode in ("tinted", "white"), mode
src, baked = os.path.join(work, "src"), os.path.join(work, "baked")
for d in (src, baked):
    if os.path.exists(d):
        shutil.rmtree(d)
shutil.copytree(walk, src)

# ---- the den fill, in the copy's own loader --------------------------------------------------
loader = os.path.join(src, "runtime", "lux", "runtime", "lux_light_loader.gd")
t = open(loader, "rb").read().decode("utf-8")
crlf = "\r\n" in t
t = t.replace("\r\n", "\n")


def swap(old, new):
    global t
    assert t.count(old) == 1, (old[:60], t.count(old))
    t = t.replace(old, new)


if share > 0.0:
    swap("\t\tif not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR) \\\n"
         "\t\t\t\tor dens.has(_probe_building(p)):\n"
         "\t\t\tcontinue\n",
         "\t\tvar den: bool = dens.has(_probe_building(p))\n"
         "\t\tvar tinted: bool = not p.ambient_color.is_equal_approx(ROOM_AMBIENT_DERIVED_COLOR)\n"
         "\t\tif tinted and not den:\n"
         "\t\t\tcontinue\n")
    nx = "\t\tvar nx := maxi(1, ceili(room.x / BAKE_FILL_CELL_M))\n"
    swap(nx, "\t\tif den:\n\t\t\tshare = %r\n" % share + nx)
    if mode == "tinted":
        att = "\t\t\t\tomni.omni_attenuation = 0.0\n"
        swap(att, att + "\t\t\t\tif den and tinted:\n\t\t\t\t\tomni.light_color = p.ambient_color\n")
open(loader, "wb").write((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))

# ---- the club washes, in the copy's stored rigs ----------------------------------------------
scene = os.path.join(src, "presentation", "lux.applied.tscn")
s = open(scene, "rb").read().decode("utf-8")
WASH_RE = re.compile(r'(rig_name = &"Club Wash \(baked\)"\n(?:[^\n\[]*\n)*?)energy = ([0-9.eE+-]+)')
count = [0]


def _scale(m):
    count[0] += 1
    return m.group(1) + "energy = %r" % (float(m.group(2)) * wash / 12.0)


s = WASH_RE.sub(_scale, s)
assert count[0] > 0, "no Club Wash (baked) rig found"
open(scene, "wb").write(s.encode("utf-8"))
print("trial: den fill share", share, mode, "| %d club washes x %.2f" % (count[0], wash / 12.0))

# ---- re-bake and measure ---------------------------------------------------------------------
r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "lux_rebake.py"), src, baked],
                   capture_output=True, text=True)
print("rebake exit", r.returncode)
for ln in r.stdout.splitlines():
    if "room fill" in ln:
        print("  rebake:", ln.strip()[:220])
if r.returncode:
    print(r.stderr[-1500:])
    sys.exit(2)
shutil.rmtree(src)
r = subprocess.run([sys.executable, os.path.join(FACTORY, "tools", "light_check.py"), baked,
                    "--slots", "own", "--out", os.path.join(work, "light")],
                   capture_output=True, text=True)
for ln in r.stdout.splitlines():
    if " DEN " in ln:
        print(ln)
