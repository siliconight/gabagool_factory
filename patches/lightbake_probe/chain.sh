#!/usr/bin/env bash
# The light-bake probe end to end on a fresh build of the walker's lot:
# rebuild, walk copy, real-time pole survey, UV2 import, unattended bake,
# back to GL Compatibility, frames baked against unbaked, and the price on
# the fixed-station harness (raw packages, the unbaked one twice).
#   bash chain.sh <tag>
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
T=${1:-v2}
P=$R/patches/lightbake_probe
OUT="C:/Projects/gabagool_studios/gabagool_factory/docs/findings/light_bake/$T"
WS=workspaces/moving-ws
M=gas_block_001
cd "$R" || exit 3
mkdir -p "$R/docs/findings/light_bake/$T"
step() { echo "== $1 $(date +%T)"; }

step rebuild
python -m level_factory -C "$WS" run $M 2>&1 | grep -E "candidates:|blockers open|Traceback" | tail -2
python -m level_factory -C "$WS" run $M --art --gameplay 2>&1 | grep -E "blockers open|Traceback" | tail -2
python -m level_factory -C "$WS" export $M --mode portable-godot 2>&1 | grep -E "^exported|Traceback|refus" | tail -2
W=$R/_runs/walk_export_bake_$T
rm -rf "$W"
python tools/walk_export.py "$R/$WS/.level_factory" $M --out "$W" 2>&1 | tail -1
test -f "$W/_walk.tscn" || { echo "no walk copy"; exit 5; }
"$G" --headless --import --path "$W" >/dev/null 2>&1

step "real-time pole survey"
cp "$R/patches/lux_streetlight_hang/probes/pole_survey_probe.gd" "$W/_survey.gd"
(cd "$W" && timeout 900 "$G" --path . --script _survey.gd 2>&1 | grep -E "^SURVEY (alive|dead)|SCRIPT ERROR")
rm -f "$W/_survey.gd" "$W/_survey.gd.uid"

step "uv2 import"
U=$R/_runs/lightbake_probe_$T
python "$P/prepare.py" "$W" "$U" | grep -E "static lightmaps|kept dynamic:|add_uv2"
timeout 1800 "$G" --headless --import --path "$U" > "$U/import.log" 2>&1
echo "import errors: $(grep -c ERROR "$U/import.log")"

step bake
E=$R/_runs/lightbake_editor_$T
python "$P/prepare_bake.py" "$U" "$E" 0
python "$P/run_bake.py" "$E" 1800

step compat
C=$R/_runs/lightbake_compat_$T
python "$P/prepare_compat.py" "$E" "$C" || exit 6
timeout 900 "$G" --headless --import --path "$C" > "$C/compat_import.log" 2>&1
echo "compat import errors: $(grep -c ERROR "$C/compat_import.log")"

step frames
for pair in "$U:unbaked" "$C:baked"; do
  d=${pair%%:*}; t=${pair##*:}
  cp "$P/lit_shots.gd" "$d/_lit.gd"
  (cd "$d" && timeout 600 "$G" --path . --script _lit.gd -- "$OUT" "$t" 2>&1 | grep -E "^LIT|SCRIPT ERROR" | sed "s/^/$t /")
  rm -f "$d/_lit.gd" "$d/_lit.gd.uid"
done

step price
RU=$R/_runs/lightbake_raw_unbaked_$T
RB=$R/_runs/lightbake_raw_baked_$T
rm -rf "$RU" "$RB"
cp -r "$W" "$RU"
(cd "$RU" && rm -rf .godot _walk.tscn _walk_flashlight.gd _walk_flashlight.gd.uid _walk_ladders.gd _walk_ladders.gd.uid \
   _walk_player.gd _walk_player.gd.uid debug_overlay.gd debug_overlay.gd.uid \
   && sed -i 's#^run/main_scene="res://_walk.tscn"#run/main_scene="res://mission.tscn"#' project.godot)
python "$P/prepare_compat.py" "$E" "$RB" --raw
rm -rf "$RB/.godot"
cd "$R/_runs/perf_inner" || exit 7
for t in "bake_${T}_unbaked:$RU" "bake_${T}_baked:$RB" "bake_${T}_unbaked2:$RU"; do
  tag=${t%%:*}; pkg=${t#*:}
  echo "-- $tag"
  python run.py "$tag" "$pkg" 2>&1 | grep -E "^import|^perf|CANNOT" | head -3
done
python "$R/patches/lux_streetlight_hang/perf_table.py" "bake_${T}_unbaked.json" "bake_${T}_baked.json" "bake_${T}_unbaked2.json"
cp bake_${T}_*.json "$R/docs/findings/light_bake/$T/" 2>/dev/null
step done
