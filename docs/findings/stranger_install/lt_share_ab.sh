#!/bin/bash
# Install test 9 against 8: Laser Tag's share of the findings went 20 -> 17, every row that moved an unpicked
# candidate's (seed_9205: LT_MAP_ENEMY_STUCK, LT_MAP_INSTANT_CONTACT and LT_MAP_PLAYER_STUCK gone,
# LT_MAP_OVEREXPOSED new; seed_9104: LT_MAP_PLAYER_STUCK gone). Between the tests BOTH moved: every evaluated
# scene (the three jobs' fingerprints' scene_hash all differ) and the grader (Laser Tag 0.27.0 -> 0.32.0). This
# separates them, two by two for each seed: each test's staged project as its job ran it (the controls, which
# must read their own job's report) and with the other test's addon swapped in. Each arm is the job's own
# command line (its job.log's first line), one at a time; a job took 36 s. It measures and prints.
#
# EVERY ARM GETS LEVEL FACTORY'S IMPORT PASS (`godot --headless --path <project> --import`, as
# `packages/staging/godot_project.py` runs it after staging), controls included, so a control that still
# reads its own job also shows the pass moves nothing. THE FIRST RUN HAD NONE, and its swapped arm broke:
# Laser Tag 0.32.0 on test 8's project read BROKEN 20, 0 % of the route walked and no shot fired, every run
# logging "Trying to assign value of type 'Node' to a variable of type 'LT_EnemyMovement.gd'". The project's
# global_script_class_cache.cfg came from 0.27.0's scan and lacks LT_Steering (0.31.0), and `-s` honours only
# the class types an import scan registered (that file's comment, "verified on hardware"). The instrument
# failing, not a reading; the first run's arms are kept in `_scratch/install_202_9/lt_ab.first/`.
#
#     bash docs/findings/stranger_install/lt_share_ab.sh [seed ...]      (default: 9205 9104)
#     python docs/findings/stranger_install/lt_share_ab.py               (the comparison, from the arms' reports)
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64.exe"
X="$F/_scratch/install_202_9/lt_ab"
SEEDS="${*:-9205 9104}"
declare -A COMMIT=([27]=f5f47ad [32]=a277dd9)
declare -A TEST_V=([8]=27 [9]=32)
rm -rf "$X" && mkdir -p "$X"
for v in 27 32; do
  got=$(git -C "$F/lasertag" show "${COMMIT[$v]}:VERSION" | tr -d '\r')
  [ "$got" = "Laser Tag 0.$v.0" ] || { echo "${COMMIT[$v]} is '$got', not 0.$v.0"; exit 2; }
  mkdir -p "$X/a$v" && git -C "$F/lasertag" archive "${COMMIT[$v]}" addons/laser_tag_tool | tar -x -C "$X/a$v" || exit 3
done
addon_is() {   # addon_is <project> <version>: 0 differences but Godot's .uid files
  diff -rq "$X/a$2/addons/laser_tag_tool" "$1/addons/laser_tag_tool" | grep -vc '\.uid'
}
for s in $SEEDS; do
  JOB="restaurant_row_001.laser_tag_evaluate.candidate.seed_$s"
  for t in 8 9; do
    src="/c/stranger_202_$t/gabagool/levels/.level_factory/staging/$JOB"
    [ -d "$src" ] || { echo "test $t's staged project for seed_$s is missing"; exit 4; }
    n=$(addon_is "$src" "${TEST_V[$t]}")
    [ "$n" = 0 ] || { echo "test $t's staged addon is not 0.${TEST_V[$t]}.0 ($n differences)"; exit 5; }
    for v in 27 32; do
      arm="s${s}_t${t}_v$v"
      cp -r "$src" "$X/p_$arm"
      if [ "$v" != "${TEST_V[$t]}" ]; then
        d="$X/p_$arm/addons/laser_tag_tool"
        (cd "$d" && find . -type f ! -name "*.uid") | while read -r f; do
          [ -f "$X/a$v/addons/laser_tag_tool/$f" ] || rm -f "$d/$f" "$d/$f.uid"
        done
        cp -r "$X/a$v/addons/laser_tag_tool/." "$d/"
      fi
      n=$(addon_is "$X/p_$arm" "$v")
      [ "$n" = 0 ] || { echo "$arm: the addon is not 0.$v.0 ($n differences)"; exit 6; }
      timeout 300 "$G" --headless --path "$(cygpath -w "$X/p_$arm")" --import < /dev/null > "$X/import_$arm.log" 2>&1
      echo "$arm: import exit $?, classes $(grep -c '"class": &' "$X/p_$arm/.godot/global_script_class_cache.cfg"), LT_Steering $(grep -c '"class": &"LT_Steering"' "$X/p_$arm/.godot/global_script_class_cache.cfg")"
      st=$(date +%s.%N)
      timeout 600 "$G" --headless --fixed-fps 60 --path "$(cygpath -w "$X/p_$arm")" \
        -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- --bake-nav --map res://level.tscn \
        --scenario res://mission_scenario.tres --runs 25 --seed "$s" --output "$(cygpath -w "$X/r_$arm.json")" \
        < /dev/null > "$X/run_$arm.log" 2>&1
      echo "$arm: exit $?, wall $(python -c "print(round($(date +%s.%N) - $st, 1))") s"
    done
  done
done
tasklist 2>/dev/null | grep -i godot && echo "a Godot process is still running" || echo "no Godot process left"
