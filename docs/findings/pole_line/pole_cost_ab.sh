#!/bin/bash
# Attribute the pole line's +170 draws a heading (poles_price.sh, 9261 -> 9262) with arms of both
# runs' packages, one Level Factory station pass each, against the two runs as built (the price's
# perf_control_*.json for 9261 and perf_glow.json for 9262, the same harness on the same copies).
# Draw counts repeat exactly between passes (the controls' spread is 0), so one pass attributes
# draws; frame time it does not. Arms by pole_cost_arms.py on copies of the price's imported copies
# (_scratch/price_poles/{control,subject}), which poles_price.sh leaves for this:
#   9262_poles_hidden    the 11 poles hidden
#   9262_shadows_off     Lux's shadow_caster_budget = 0 (every positional light unshadowed)
#   9261_shadows_off     the same on the lamps' level
#   9262_budget_8        the budget at the Medium tier's 8
#   9262_budget_4        the budget at the Low and Compatibility tiers' 4
#   9262_rigfade_30      every street light's shadow cut beyond 30 m of the camera (Godot's
#                        distance_fade_shadow), the light itself kept, set in the vendored rig
# An arm whose report exists is not run again.
#
# REFUTED, KEPT: perf_9262_shadow_enabled_edit_REFUTED.json, the first shadows arm, which edited
# the lights' `shadow_enabled` in the scene; Lux's runtime policy sets it, so it measured nothing
# (pole_cost_arms.py says how); and perf_9262_fade_30_scene_edit_REFUTED.json, the same fade
# written on the scene's street lights, which the rig frees and rebuilds at runtime.
#
#     bash docs/findings/pole_line/pole_cost_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/findings/pole_line/price_9261_9262"
for spec in subject:poles_hidden:9262_poles_hidden subject:shadows_off:9262_shadows_off \
            control:shadows_off:9261_shadows_off subject:budget_8:9262_budget_8 \
            subject:budget_4:9262_budget_4 subject:rigfade_30:9262_rigfade_30; do
  src="_scratch/price_poles/${spec%%:*}"; rest="${spec#*:}"; arm="${rest%%:*}"; name="${rest#*:}"
  [ -f "$OUT/perf_$name.json" ] && { echo "$name measured before"; continue; }
  [ -f "$src/mission.tscn" ] || { echo "no imported copy at $src (run poles_price.sh)"; exit 1; }
  rm -rf "_scratch/pole_arm_$name"
  cp -r "$src" "_scratch/pole_arm_$name" || exit 1
  python docs/findings/pole_line/pole_cost_arms.py "_scratch/pole_arm_$name" "$arm" || exit 1
  timeout 1800 python level_factory/tools/perf_stations_run.py "_scratch/pole_arm_$name" \
    --json "$OUT/perf_$name.json" > "$OUT/perf_$name.log" 2>&1 < /dev/null
  echo "$name pass exit $? ($( [ -f "$OUT/perf_$name.json" ] && echo measured || echo NOT MEASURED ))"
  rm -rf "_scratch/pole_arm_$name"
done
python - "$OUT" <<'PY'
import json, statistics as st, sys
out = sys.argv[1]
def tab(name):
    d = json.load(open("%s/perf_%s.json" % (out, name), encoding="utf-8"))
    if d.get("schema") != "level_factory.perf_stations.v1" or not d.get("complete"):
        raise SystemExit("UNKNOWN SHAPE: %s" % name)
    return {(r["station"], h["yaw"]): int(h["draws"]) for r in d["rows"] for h in r["headings"]}
c1, c2 = tab("control_1"), tab("control_2")
if set(c1) != set(c2) or any(c1[k] != c2[k] for k in c1):
    raise SystemExit("THE 9261 PASSES DISAGREE ON DRAWS: one pass cannot attribute")
runs = {"9261 as built": c1, "9262 as built": tab("glow")}
for n in ("9262_poles_hidden", "9262_shadows_off", "9261_shadows_off", "9262_budget_8", "9262_budget_4",
          "9262_rigfade_30"):
    runs[n.replace("_", " ", 1)] = tab(n)
keys = sorted(c1, key=str)
for n, t in runs.items():
    if set(t) != set(c1):
        raise SystemExit("STATIONS DIFFER: %s" % n)
def line(label, a, b):
    d = [a[k] - b[k] for k in keys]
    print("%-46s mean %+7.1f  median %+6.0f  min %+5.0f  max %+5.0f"
          % (label, st.mean(d), st.median(d), min(d), max(d)))
print("draws a heading over 53 headings")
line("9262 as built - 9261 as built", runs["9262 as built"], runs["9261 as built"])
line("9262 as built - 9262 poles hidden (the poles)", runs["9262 as built"], runs["9262 poles_hidden"])
line("9262 as built - 9262 shadows off (its shadows)", runs["9262 as built"], runs["9262 shadows_off"])
line("9261 as built - 9261 shadows off (its shadows)", runs["9261 as built"], runs["9261 shadows_off"])
line("9262 shadows off - 9261 shadows off (the rest)", runs["9262 shadows_off"], runs["9261 shadows_off"])
print("the levers, against 9262 as built and against 9261 as built")
for n in ("9262 budget_8", "9262 budget_4", "9262 rigfade_30"):
    line("9262 as built - %s (saved)" % n, runs["9262 as built"], runs[n])
    line("%s - 9261 as built" % n, runs[n], runs["9261 as built"])
PY
