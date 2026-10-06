#!/usr/bin/env bash
# ONE cold run of a sweep, refused if anything is left from the run before,
# staged from the mission's own last cold run, driven, ended, one line out.
# Written for the breadth sweep of 2026-10-05/06 (cold runs 9166-9177,
# docs/findings/breadth_sweep_2026-10-06/), where it ran ten missions one at
# a time.
#
#   bash tools/cold_drive/sweep_one.sh <N> <FROM> <mission> <seed|auto>
#
# <FROM> is the mission's own last cold run: stage_batch.py copies its
# batch.json and briefs/ out of docs/cold_runs/cold_<FROM>. The driver's PREV
# is the newest workspace that still has a tools.local.json, because
# cold_drive.sh copies that file and stops without it -- the mission's own
# last workspace is usually long gone.
#
# One run per call, on purpose. A background task in the agent's harness is
# killed at two hours, and a kill mid-run leaves _runs/cold/ACTIVE and a
# half-built workspace; nine runs back to back take five.
#
# Refuses before staging when a run is still ACTIVE, when Godot or Blender is
# still running, or when C: has under 8 GB free (cold run 9163 died on a full
# disk).
set -u
N="$1"; FROM="$2"; M="$3"; SEED="$4"
cd /c/Projects/gabagool_studios/gabagool_factory
if [ -f _runs/cold/ACTIVE ]; then echo "REFUSED $N: a run is still ACTIVE"; exit 2; fi
if tasklist | grep -qiE "godot|blender"; then echo "REFUSED $N: Godot or Blender still running"; exit 2; fi
free=$(powershell -NoProfile -Command "[math]::Floor((Get-PSDrive C).Free/1GB)" | tr -d '\r')
if [ "${free:-0}" -lt 8 ]; then echo "REFUSED $N: C: has ${free:-?} GB free"; exit 2; fi
PREV_WS=$(ls -d workspaces/cold-*-ws 2>/dev/null | sed -E 's/.*cold-([0-9]+)-ws/\1/' | sort -n \
          | while read -r p; do [ "$p" != "$N" ] && [ -f "workspaces/cold-$p-ws/tools.local.json" ] && echo "$p"; done | tail -1)
[ -n "$PREV_WS" ] || { echo "REFUSED $N: no workspace with a tools.local.json to copy"; exit 2; }
python tools/cold_drive/stage_batch.py "$N" "$FROM" \
  "sweep: $M, seed $SEED, on Level Factory $(cat level_factory/VERSION); staged from cold run $FROM" \
  || { echo "REFUSED $N: staging failed"; exit 2; }
echo "$(date +%H:%M:%S) start $N $M (from $FROM, seed $SEED, tools from cold-$PREV_WS-ws, C: ${free} GB free)"
bash tools/cold_drive/cold_drive.sh "$N" "$PREV_WS" "$M" "$SEED" > "docs/cold_runs/cold_$N/driver.log" 2>&1
python tools/cold_run.py --end 2>&1 | grep -E "INTERVENTIONS" >> "docs/cold_runs/cold_$N/driver.log"
echo "$(date +%H:%M:%S) end $N $M: $(grep -E '^STOPPED|^DONE' "docs/cold_runs/cold_$N/driver.log" | tail -1) |$(grep -E 'INTERVENTIONS' "docs/cold_runs/cold_$N/driver.log" | tail -1)"
