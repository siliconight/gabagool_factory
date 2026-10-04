#!/usr/bin/env bash
# Does the enemy rule (site_fields.ENEMY_CLEAR) answer gas_block_001's new
# Laser Tag findings? Rebuild the brief with it and set the encounter figures
# beside the build without fields (yards-after) and the build with fields but
# without the rule (fields-after). Writes nothing to a tool repo.
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
cd "$R" || exit 3
m=gas_block_001
ws=$R/workspaces/fields2-after-$m-ws
rm -rf "$ws"
python -m level_factory init "$ws" --name "fields with the enemy rule" >/dev/null 2>&1 || { echo "init failed"; exit 4; }
cp "$R/workspaces/cold-9140-ws/tools.local.json" "$ws/tools.local.json"
python -m level_factory -C "$ws" batch create "$R/docs/cold_runs/cold_9140/batch.json" 2>&1 | tail -1
python -m level_factory -C "$ws" plan $m >/dev/null 2>&1 || { echo "plan failed"; exit 4; }
python -m level_factory -C "$ws" run $m 2>&1 | grep -E "candidates:|blockers open"
python - <<'PY'
import collections, json
m = "gas_block_001"
builds = (("no fields", "yards-after"), ("fields, no rule", "fields-after"), ("fields + rule", "fields2-after"))
for s in ("9080", "9181", "9282"):
    print("seed", s)
    for label, pre in builds:
        ws = f"workspaces/{pre}-{m}-ws/.level_factory"
        r = json.load(open(f"{ws}/jobs/{m}.laser_tag_evaluate.candidate.seed_{s}/out/lasertag.report.json", encoding="utf-8"))["summary"]
        g = json.load(open(f"{ws}/jobs/{m}.lot_assemble.candidate.seed_{s}/out/site.site.gameplay.json", encoding="utf-8"))
        fp = g.get("field_plan") or {}
        print("  %-16s field cars %2d  kerb cars %2d  survival %6.2f s  first enemy shot %5.2f s  first crew shot %5.2f s  route %.2f" % (
            label, len(fp.get("cars") or []), len((g.get("parking_plan") or {}).get("placed") or []),
            r["avg_player_survival_seconds"], r["avg_time_to_first_enemy_shot"], r["avg_time_to_first_player_shot"],
            r["route_progress_rate"]))
for label, pre in builds:
    d = json.load(open(f"workspaces/{pre}-{m}-ws/.level_factory/validation/{m}.json", encoding="utf-8"))
    c = collections.Counter((i["code"], (i.get("candidate_id") or "")[-4:]) for i in d["issues"] if i["code"].startswith("LT_"))
    print(label, len(d["issues"]), "issues; Laser Tag:", dict(sorted(c.items())))
PY
