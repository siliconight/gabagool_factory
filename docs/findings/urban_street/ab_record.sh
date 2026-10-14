#!/bin/bash
# The first urban street against the strip it came from: two cold runs' packages, shot and priced side by side
# (factory roadmap 241, step 5 -- "priced and seen").
#
#     bash docs/findings/urban_street/ab_record.sh <N control> <mission control> <N subject> <mission subject>
#     bash docs/findings/urban_street/ab_record.sh 9285 restaurant_row_001 9287 urban_row_001
#
# 9287 ran restaurant_row_001's brief with `streetscape: urban` and nothing else changed; both picked seed_9104,
# and the near side's lots are the same buildings. So the control is 9285's package -- the rowhome terrace across
# the street -- and the subject 9287's -- the continuous mid-rise wall. The tools between the two runs moved no
# output on a strip brief: Level Factory 0.200.0 changes only an urban one (its suite holds the strip terrace),
# and Deli Counter 0.215.0 and 0.216.0 moved no built shell (their manifests).
#
# tools/recipe_run_record.sh's pattern with that control: the stations derived from the subject's drawn spec
# (tools/edge_stations.py, the road ends at the plate's edge, which look down the street), look_shots on both
# (its own spawn, objective, extraction and elevated cameras as well), a sheet control-beside-subject, and
# docs/findings/horizon_glow/price_glow.py (control, subject, control again) for draws, frame time and memory.
#
# Writes to docs/findings/urban_street/ab_<N subject>/: stations.txt, ab_sheet.png, price/ (perf_control_1.json, perf_glow.json
# -- the SUBJECT, the harness's name for it --, perf_control_2.json, price.txt). The frames go to
# _scratch/frames_urban_<N subject>/ and the copies to _scratch/price_urban_<N subject>/; delete the copies once
# the JSONs exist (each about 250 MB). Nothing else may run beside the price.
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
NC="$1"; MC="$2"; NS="$3"; MS="$4"
[ -n "$NS" ] && [ -n "$MS" ] || { echo "usage: ab_record.sh <N control> <mission> <N subject> <mission>"; exit 2; }
PKG_C="workspaces/cold-$NC-ws/.level_factory/exports/LF_$MC.portable-godot"
PKG_S="workspaces/cold-$NS-ws/.level_factory/exports/LF_$MS.portable-godot"
OUT="docs/findings/urban_street/ab_$NS"
FR="_scratch/frames_urban_$NS"
SCR="_scratch/price_urban_$NS"
for p in "$PKG_C" "$PKG_S"; do [ -f "$p/mission.tscn" ] || { echo "no package at $p"; exit 1; }; done
DRAWN=$(ls -t "workspaces/cold-$NS-ws/.level_factory/jobs/$MS.themed_site_assemble/"*/out/site.site.drawn.json 2>/dev/null | head -1)
[ -f "$DRAWN" ] || { echo "no drawn spec for $MS in cold-$NS-ws"; exit 1; }
echo "control: $PKG_C"; echo "subject: $PKG_S"; echo "drawn:   $DRAWN"
mkdir -p "$OUT/price" "$FR" "$SCR"
rm -rf "$SCR/control" "$SCR/subject"
cp -r "$PKG_C" "$SCR/control" || exit 1
cp -r "$PKG_S" "$SCR/subject" || exit 1
STATIONS=$(python tools/edge_stations.py "$DRAWN" 2> "$OUT/stations.txt") || exit 1
echo "$STATIONS" >> "$OUT/stations.txt"
[ -n "$STATIONS" ] || { echo "no edge station derived from $DRAWN"; exit 1; }
cat "$OUT/stations.txt"
for name in control subject; do
  timeout 900 python tools/look_shots.py "$SCR/$name" --scene mission.tscn --out "$FR/shots_$name" --json $STATIONS \
    > "$FR/shots_$name.json" 2> "$FR/shots_$name.err" < /dev/null
  echo "$name shots exit $?"
done
ARGS=()
for tok in $STATIONS; do
  case "$tok" in
    --station) ;;
    *) s="${tok%%:*}"; ARGS+=("control $s=$FR/shots_control/$s.png" "subject $s=$FR/shots_subject/$s.png") ;;
  esac
done
for s in spawn objective elev_N elev_S elev_E elev_W; do
  [ -f "$FR/shots_control/$s.png" ] && ARGS+=("control $s=$FR/shots_control/$s.png" "subject $s=$FR/shots_subject/$s.png")
done
python docs/findings/edge_menu/sheet.py "$OUT/ab_sheet.png" 2 "${ARGS[@]}" && echo "sheet: $OUT/ab_sheet.png"
python docs/findings/horizon_glow/price_glow.py "$SCR/control" "$SCR/subject" "$OUT/price" > "$OUT/price/price.txt" 2>&1
echo "price exit $?"
