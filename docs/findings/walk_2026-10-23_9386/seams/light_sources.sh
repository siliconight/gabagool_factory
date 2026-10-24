#!/usr/bin/env bash
# Finding 2: the walker's eye on 9389's walk copy, three arms in one session, the frames to _scratch/seam_src/<arm>/
# and the joint step of each through joints_in_frame.py (light_sources_9389.out.txt beside this):
#   shipped        -- nothing switched off (the control: it must reproduce the shipped frame's joint excess)
#   lightmap_only  -- every other source off: live, sun, ambient, probes, emission, sky, fog
#   no_lightmap    -- the lightmap off (look_shots.gd's SWITCHES: the lightmap cleared, its static lamps hidden)
cd /c/Projects/gabagool_studios/gabagool_factory || exit 9
F=docs/findings/walk_2026-10-23_9386/seams
W=_runs/walk_9389_restaurant_row_001
O=_scratch/seam_src
ST="seams:-8.0,1.6,-0.1,-6.0,2.07,-10.5"
rm -rf "${O:?}"
for arm in shipped lightmap_only no_lightmap; do
  case $arm in
    shipped) SW="" ;;
    lightmap_only) SW="live,sun,ambient,probes,emission,sky,fog" ;;
    no_lightmap) SW="lightmap" ;;
  esac
  python tools/look_shots.py $W --out $O/$arm --station "$ST" --switch-off "$SW" --json > $O.$arm.json 2> $O.$arm.err
  echo "$arm exit $?"
done
python $F/joints_in_frame.py $O/shipped/seams.png $O/lightmap_only/seams.png $O/no_lightmap/seams.png > $F/light_sources_9389.out.txt
grep -E "^==|^mean" $F/light_sources_9389.out.txt
