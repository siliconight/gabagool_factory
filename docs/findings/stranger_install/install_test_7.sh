#!/bin/bash
# Roadmap 202, install test 7: package the factory at its current HEADs (the set factory 1.38.0
# would certify: Deli Counter 0.208.0, Level Factory 0.178.6, Lot 0.116.0, Lux 0.75.0, Zoo
# 1.100.0), unpack it fresh, and type START_HERE.md's commands into cmd.exe there with the page's
# own `setup --venv` and its PyPI download (docs/findings/stranger_install/install_test_venv.cmd),
# as install test 6 did. Beside test 6's checks it counts the doctor's `drift vs certified` lines
# in setup's log (Level Factory 0.178.4 re-grounded the table to this set, so 0 is the claim) and
# reads the package's fixture layers (Zoo 1.100.0 merges a fixture's same-material parts: the
# deli's pendants' metal should be one mesh a pendant).
#     bash docs/findings/stranger_install/install_test_7.sh
F=/c/Projects/gabagool_studios/gabagool_factory
DEST='C:\stranger_202_7\gabagool'
LOG=$F/_scratch/install_202_7
mkdir -p "$LOG"
cd "$F" || exit 1
echo "== package $(date +%H:%M:%S)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/make_factory_package.ps1 > "$LOG/package.txt" 2>&1
echo "package exit $?"
ZIP=$(grep -o "package: .*\.zip" "$LOG/package.txt" | sed 's/^package: //')
echo "zip: $ZIP"
[ -n "$ZIP" ] || exit 2
echo "== unpack $(date +%H:%M:%S)"
powershell.exe -NoProfile -Command "if (Test-Path '$DEST') { Remove-Item -Recurse -Force '$DEST' }; New-Item -ItemType Directory -Path '$DEST' -Force | Out-Null; Expand-Archive -LiteralPath '$ZIP' -DestinationPath '$DEST' -Force" > "$LOG/unpack.txt" 2>&1
echo "unpack exit $?"
cd /c/stranger_202_7/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
/c/stranger_202_7/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -2
ls /c/stranger_202_7/gabagool/.venv/Lib/site-packages/sitecustomize.py 2>&1 | tail -1
echo "== sitecustomize errors"
for f in setup make walk; do echo "$f: $(grep -c 'Error in sitecustomize' "$LOG/$f.txt") of $(wc -l < "$LOG/$f.txt") lines"; done
echo "== the doctor's drift lines at setup"
echo "drift vs certified: $(grep -c 'drift vs certified' "$LOG/setup.txt")  WARN rows: $(grep -c 'WARN' "$LOG/setup.txt")"
echo "== the package after the walk"
E=/c/stranger_202_7/gabagool/levels/.level_factory/exports/LF_restaurant_row_001.portable-godot
echo "files: $(find "$E" -type f | wc -l)  bake.exr: $(ls "$E/bake.exr" 2>/dev/null | wc -l)  light_bake.json ok: $(python -c "import json,sys; print(json.load(open(sys.argv[1])).get('ok'))" "$E/light_bake.json" 2>&1 | tail -1)"
echo "== the package's fixture layers"
for g in $(find "$E" -name "*_fixtures.glb" | sort); do python "$F/docs/findings/fixture_merge/layer_count.py" "$g" | sed "s#$E/##" | grep -v "^\[layer\]   " ; python "$F/docs/findings/fixture_merge/layer_count.py" "$g" | grep "Pendant_metal\|Pendant_Lens"; done
echo "== done $(date +%H:%M:%S)"
