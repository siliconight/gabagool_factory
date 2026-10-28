cd /c/Projects/gabagool_studios/gabagool_factory || exit 9
PY=.venv/Scripts/python.exe; CLI=level_factory/apps/cli/main.py
for m in off on; do $PY $CLI -C workspaces/events-$m-02651-ws make _scratch/events_${m}_input/batch.json > _scratch/events_${m}_02651_make.log 2>&1; echo "$m make=$?"; done
python - <<'PY'
import json
def ids(ws):
    d = json.load(open("workspaces/%s/.level_factory/exports/LF_bank_block_001.portable-godot/gameplay_anchors.json" % ws, encoding="utf-8"))
    return {a["shell_id"]: a for a in d["anchors"]}
base, off, on = ids("template-bank_block-0264-ws"), ids("events-off-02651-ws"), ids("events-on-02651-ws")
plain_on = {k: v for k, v in on.items() if v["anchor_type"] != "trigger"}
print("0.264.0 off:", len(base), " 0.265.1 off:", len(off), " 0.265.1 on:", len(on), "triggers", len(on) - len(plain_on))
print("off ids == 0.264.0 ids:", set(off) == set(base), " on's other ids == 0.264.0 ids:", set(plain_on) == set(base))
print("off records == 0.264.0 records:", all(off[k] == base[k] for k in base if k in off))
PY
