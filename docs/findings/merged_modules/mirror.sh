#!/bin/bash
# Level Factory 0.210.0's `drop_merged_modules` on two copies of cold run 9305's package, before it ships (roadmap
# 249). Copy `a` is the package as 9305 shipped it, the control; copy `b` has the drop run on it with the export's
# own merge report (`merge_empties.json`). Then, each written beside this script:
#
#   mirror_drop.out.json      what the drop removed and kept, and the bytes
#   mirror_closure.out.txt    Level Factory's own closure scan of each copy: what it resolves, misses or misroots
#   mirror_import.out.txt     a first `--import` of each copy, the way a consumer's editor opens a package, timed
#                             -- ONE RUN EACH, a then b, so a measurement and not a price
#   mirror_frames.out.txt     look_shots on a, on b and on a again at the walk-up and corner stations and its
#                             own: each frame's pixels differing by more than 24 levels, a against a again (THE
#                             CONTROL: Lux's grain and the failing fixtures move from shot to shot) and a against b
#
# REFUTED AND KEPT: the first run compared a with b alone and counted a pixel differing by any amount, so every
# frame read 70-93 % of its pixels different (`mirror_frames_nocontrol.out.txt`, with that run's import timing in
# `mirror_import_run1.out.txt`). Grain alone does that; with no control the number could not tell noise from change.
#
# The copies are removed after. Run with Level Factory at 0.210.0 and nothing else running.
#
#     bash docs/findings/merged_modules/mirror.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/findings/merged_modules"
SCR="_scratch/mirror_249"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
SRC="workspaces/cold-9305-ws/.level_factory/exports/LF_urban_row_001.portable-godot"
[ -f "$SRC/mission.tscn" ] || { echo "no package at $SRC"; exit 1; }
grep -q "def drop_merged_modules" level_factory/packages/exporting/merge_empties.py \
  || { echo "level_factory has no drop_merged_modules: apply the patch first"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR"
cp -r "$SRC" "$SCR/a" || exit 1
cp -r "$SRC" "$SCR/b" || exit 1
python "$OUT/mirror_steps.py" drop "$SCR/b" "$OUT/mirror_drop.out.json" || exit 1
python "$OUT/mirror_steps.py" closure "$SCR/a" "$SCR/b" > "$OUT/mirror_closure.out.txt" || exit 1
cat "$OUT/mirror_closure.out.txt"
python "$OUT/mirror_steps.py" import "$G" "$SCR/a" "$SCR/b" > "$OUT/mirror_import.out.txt" || exit 1
cat "$OUT/mirror_import.out.txt"
ST="$(python docs/findings/fire_escape/walkup_stations.py 9305 urban_row_001 seed_9104 2>/dev/null) $(python docs/findings/urban_street/corner_stations.py 9305 urban_row_001 seed_9104 2>/dev/null)"
for c in a b a2; do
  src="$SCR/$c"; [ "$c" = "a2" ] && src="$SCR/a"
  timeout 900 python tools/look_shots.py "$src" --scene mission.tscn --out "$SCR/frames_$c" --json $ST \
    > "$SCR/frames_$c.json" 2> "$SCR/frames_$c.err" < /dev/null
  echo "shots $c exit $?"
done
python "$OUT/mirror_steps.py" frames "$SCR/frames_a" "$SCR/frames_a2" "$SCR/frames_b" > "$OUT/mirror_frames.out.txt"
cat "$OUT/mirror_frames.out.txt"
rm -rf "$SCR"
