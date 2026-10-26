#!/usr/bin/env bash
# Roadmap 224's next two levers on a WALL (the walker's walk of cold run 9386, finding 2: "textures have visible seams
# and it doesn't look as continous as it could be"; the office's back-room wall mottled in blotches a metre or two
# across): cold run 9391's walk copy re-baked three ways by tools/lux_rebake.py -- the control (Level Factory's own
# bake, as shipped), --texel-scale 2, --denoiser off -- then each shot from the walker's eye and square on the
# bookshelf wall. Copies to _scratch/rebake_<arm>; frames to _scratch/rebake_shots/<arm>; logs beside this file.
# Bake seconds here are INDICATIVE: another job shared the machine (2026-10-25).
F=/c/Projects/gabagool_studios/gabagool_factory
cd $F || exit 9
H=$F/docs/findings/bake_quality
SRC=_runs/walk_9391_restaurant_row_001
for arm in ctrl tex2 nodn; do
  case $arm in
    ctrl) OPT="" ;;
    tex2) OPT="--texel-scale 2" ;;
    nodn) OPT="--denoiser off" ;;
  esac
  D=_scratch/rebake_$arm
  rm -rf "${D:?}"
  python tools/lux_rebake.py $SRC $D $OPT > $H/wall_rebake_$arm.out.txt 2>&1
  echo "$arm rebake exit $?"
  O=_scratch/rebake_shots/$arm
  rm -rf "${O:?}"
  python tools/look_shots.py $D --out $O --station "walker:-8.0,1.6,-0.1,0.4,2.07,-6.34" \
      --station "shelf:-6.7,1.7,-2.5,-6.7,2.3,-6.34" --json > $H/wall_shots_$arm.json 2> $H/wall_shots_$arm.err
  echo "$arm shots exit $?"
  python - "$D" "$arm" <<'PY'
import json, os, sys
d, arm = sys.argv[1], sys.argv[2]
j = json.load(open(os.path.join(d, "light_bake.json"), encoding="utf-8"))
keys = [k for k in j if any(s in k for s in ("ms", "size", "texel", "quality", "denois", "lightmap", "bytes"))]
print(arm, {k: j[k] for k in keys})
print(arm, "bake.exr bytes", os.path.getsize(os.path.join(d, "bake.exr")) if os.path.exists(os.path.join(d, "bake.exr")) else None)
PY
done
