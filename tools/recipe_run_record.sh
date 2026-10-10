#!/bin/bash
# Record a recipe cold run's edge (roadmap 228): the run's package against itself with the backdrop
# off, at the edge stations derived from its drawn spec, shot and priced.
#
#     bash tools/recipe_run_record.sh <N> <mission>
#
# A recipe run (9226 yards, 9227 parkland, 9228 roadside) has no earlier run of its level to compare
# against, so the control is the package itself with `<site>_backdrop.tscn` not loaded
# (tools/backdrop_off.py): every other draw identical, the same bake.tscn. The stations come from
# the themed drawn spec (tools/edge_stations.py), one a road end that reaches the plate's edge,
# and look_shots adds its own elevated cameras over the plate.
#
# Writes to docs/cold_runs/cold_<N>/: stations.txt (what was derived and the arguments),
# edge_before_after.png (control left, subject right, a row a station, the elevated views after),
# price/ (perf_control_1.json, perf_glow.json -- the SUBJECT, the harness's name for it --,
# perf_control_2.json and price.txt). The frames and look_shots' json/err go to _scratch/frames_<N>/
# and the package copies to _scratch/price_<N>/; delete the copies once the JSONs exist (each is
# about 250 MB; forty-two of them filled the disk once).
F=$(cd "$(dirname "$0")/.." && pwd)
cd "$F" || exit 1
N="$1"; M="$2"
[ -n "$N" ] && [ -n "$M" ] || { echo "usage: recipe_run_record.sh <N> <mission>"; exit 2; }
WS="workspaces/cold-$N-ws"
PKG="$WS/.level_factory/exports/LF_$M.portable-godot"
OUT="docs/cold_runs/cold_$N"
FR="_scratch/frames_$N"
SCR="_scratch/price_$N"
[ -f "$PKG/mission.tscn" ] || { echo "no package at $PKG"; exit 1; }
DRAWN=$(ls -t "$WS/.level_factory/jobs/$M.themed_site_assemble/"*/out/site.site.drawn.json 2>/dev/null | head -1)
[ -f "$DRAWN" ] || { echo "no drawn spec under $WS/.level_factory/jobs/$M.themed_site_assemble"; exit 1; }
echo "package: $PKG"
echo "drawn:   $DRAWN"
mkdir -p "$OUT/price" "$FR" "$SCR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$PKG" "$SCR/subject" || exit 1
cp -r "$PKG" "$SCR/control" || exit 1
python tools/backdrop_off.py "$SCR/control" || exit 1
STATIONS=$(python tools/edge_stations.py "$DRAWN" 2> "$OUT/stations.txt") || exit 1
echo "$STATIONS" >> "$OUT/stations.txt"
[ -n "$STATIONS" ] || { echo "no edge station derived from $DRAWN"; exit 1; }
cat "$OUT/stations.txt"
for name in control subject; do
  timeout 900 python tools/look_shots.py "$SCR/$name" --scene mission.tscn --out "$FR/shots_$name" --json $STATIONS \
    > "$FR/shots_$name.json" 2> "$FR/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
# the sheet: control beside subject, a row a station, then the elevated views
ARGS=()
for tok in $STATIONS; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("control $s=$FR/shots_control/$s.png" "subject $s=$FR/shots_subject/$s.png") ;;
  esac
done
for s in elev_N elev_S elev_E elev_W; do
  ARGS+=("control $s=$FR/shots_control/$s.png" "subject $s=$FR/shots_subject/$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/edge_before_after.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/edge_before_after.png"
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
tail -8 "$OUT/price/price.txt"
