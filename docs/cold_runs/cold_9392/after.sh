#!/usr/bin/env bash
# Cold run 9392's proofs, after `cold_run.py --end` and the walk copy renamed to _runs/walk_9392_restaurant_row_001:
#   1. the door hardware's merge (Zoo 1.127.0): visible meshes under each Site child, 9391 against 9392
#      (docs/cold_runs/cold_9391/count_by_site_child.gd) -- each Empty was +2 in 9391 against 9389;
#   2. the bus stop zones (Lot 0.131.0): patches/lot_bus_zone/zone_check.py on the run's themed site, its base the
#      9391 job's out dir;
#   3. the office stair (Deli Counter 0.268.0 balustrades, 0.269.0 raking rail; Zoo 1.128.0, 1.129.0): frames from
#      the walker's view of finding 6 and two more, shipped light and the inspection light, 9391 against 9392;
# and writes each output beside this file.
F=/c/Projects/gabagool_studios/gabagool_factory
cd $F || exit 9
H=$F/docs/cold_runs/cold_9392
G=C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe
for r in 9391 9392; do
  W=_runs/walk_${r}_restaurant_row_001
  cp docs/cold_runs/cold_9391/count_by_site_child.gd "${W:?}/count_by_site_child.gd"
  timeout 300 $G --headless --path $W --script res://count_by_site_child.gd > $H/count_by_site_child_$r.out.txt 2>&1
  rm -f "${W:?}/count_by_site_child.gd"
done
python - <<'PY' > $H/count_by_site_child_diff.out.txt
import re
def rd(r):
    d = {}
    for l in open("docs/cold_runs/cold_9392/count_by_site_child_%s.out.txt" % r, encoding="utf-8", errors="replace"):
        m = re.match(r"CHILD (\S+) (\d+)", l)
        if m:
            d[m[1]] = int(m[2])
    return d
a, b = rd("9391"), rd("9392")
assert a and b, "a count is empty: not the probe's output"
print("totals 9391 %d 9392 %d" % (sum(a.values()), sum(b.values())))
for k in sorted(set(a) | set(b)):
    if a.get(k, 0) != b.get(k, 0):
        print("%+d %s (%d -> %d)" % (b.get(k, 0) - a.get(k, 0), k, a.get(k, 0), b.get(k, 0)))
PY
cat $H/count_by_site_child_diff.out.txt | head -40
J=workspaces/cold-9392-ws/.level_factory/jobs/restaurant_row_001.themed_site_assemble/out
B=workspaces/cold-9391-ws/.level_factory/jobs/restaurant_row_001.themed_site_assemble/out
python patches/lot_bus_zone/zone_check.py $B $J > $H/zone_check.out.txt 2>&1; echo "zone check exit $?"; cat $H/zone_check.out.txt
ST="--station walker6:55.7,5.2,-6.0,54.0,4.45,2.21 --station east6:59.5,5.2,-0.5,54.0,4.0,-0.5 --station above6:54.0,10.5,-6.5,54.0,3.6,-0.5"
for r in 9391 9392; do
  for mode in shipped inspect; do
    O=_scratch/stair92_${r}_$mode
    rm -rf "${O:?}"
    if [ $mode = inspect ]; then X="--inspect studio"; else X=""; fi
    python tools/look_shots.py _runs/walk_${r}_restaurant_row_001 --out $O $ST $X --json > $O.json 2> $O.err
    echo "$r $mode exit $?"
  done
done
python - <<'PY'
from PIL import Image, ImageDraw
st = ["walker6", "east6", "above6"]
sheet = Image.new("RGB", (3200, 450 * len(st)))
d = ImageDraw.Draw(sheet)
for i, s in enumerate(st):
    for j, (r, mode) in enumerate((("9391", "shipped"), ("9392", "shipped"), ("9391", "inspect"), ("9392", "inspect"))):
        name = ("INSPECT_studio_%s.png" % s) if mode == "inspect" else ("%s.png" % s)
        im = Image.open("_scratch/stair92_%s_%s/%s" % (r, mode, name)).convert("RGB").resize((800, 450))
        sheet.paste(im, (800 * j, 450 * i))
        d.text((800 * j + 8, 450 * i + 8), "%s %s %s" % (s, r, mode), fill=(255, 255, 0))
sheet.save("docs/cold_runs/cold_9392/stair_9391_vs_9392.webp", quality=80)
print("sheet written")
PY
