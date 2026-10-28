cd /c/Projects/gabagool_studios/gabagool_factory || exit 9
PY=.venv/Scripts/python.exe; CLI=level_factory/apps/cli/main.py
for m in off on; do $PY $CLI -C workspaces/zone-$m-02660-ws make _scratch/events_${m}_input/batch.json > _scratch/zone_${m}_02660_make.log 2>&1; echo "$m make=$?"; done
python _scratch/zone_check.py
