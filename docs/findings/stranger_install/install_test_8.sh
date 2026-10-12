#!/bin/bash
# Roadmap 202, install test 8: package the factory at its current HEADs (the set factory 1.39.0
# would certify: Deli Counter 0.209.1, Laser Tag 0.27.0, Level Factory 0.193.1, Lot 0.117.0, Zoo
# 1.103.0), unpack it fresh, and type START_HERE.md's commands into cmd.exe there with the page's
# own `setup --venv` and its PyPI download (docs/findings/stranger_install/install_test_venv.cmd),
# as install tests 6 and 7 did. It counts the doctor's `drift vs certified` lines in setup's log
# (Level Factory 0.193.1 re-grounded the table to this set, so 0 is the claim), reads the
# package's fixture layers as test 7 did, and its step stamps time `make` against test 7's 34.1
# minutes -- the cold-run speed work of roadmap 239 is in this set (Level Factory 0.179.0 to
# 0.193.1, Laser Tag 0.27.0, Lot 0.117.0, Zoo 1.103.0).
#     bash docs/findings/stranger_install/install_test_8.sh
F=/c/Projects/gabagool_studios/gabagool_factory
DEST='C:\stranger_202_8\gabagool'
LOG=$F/_scratch/install_202_8
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
cd /c/stranger_202_8/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
/c/stranger_202_8/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -2
ls /c/stranger_202_8/gabagool/.venv/Lib/site-packages/sitecustomize.py 2>&1 | tail -1
echo "== sitecustomize errors"
for f in setup make walk; do echo "$f: $(grep -c 'Error in sitecustomize' "$LOG/$f.txt") of $(wc -l < "$LOG/$f.txt") lines"; done
echo "== the doctor's drift lines at setup"
echo "drift vs certified: $(grep -c 'drift vs certified' "$LOG/setup.txt")  WARN rows: $(grep -c 'WARN' "$LOG/setup.txt")"
echo "== the package after the walk"
E=/c/stranger_202_8/gabagool/levels/.level_factory/exports/LF_restaurant_row_001.portable-godot
echo "files: $(find "$E" -type f | wc -l)  bake.exr: $(ls "$E/bake.exr" 2>/dev/null | wc -l)  light_bake.json ok: $(python -c "import json,sys; print(json.load(open(sys.argv[1])).get('ok'))" "$E/light_bake.json" 2>&1 | tail -1)"
echo "== the package's fixture layers"
for g in $(find "$E" -name "*_fixtures.glb" | sort); do python "$F/docs/findings/fixture_merge/layer_count.py" "$g" | sed "s#$E/##" | grep -v "^\[layer\]   " ; python "$F/docs/findings/fixture_merge/layer_count.py" "$g" | grep "Pendant_metal\|Pendant_Lens"; done
echo "== done $(date +%H:%M:%S)"
