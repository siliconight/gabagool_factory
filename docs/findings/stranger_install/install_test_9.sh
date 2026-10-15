#!/bin/bash
# Roadmap 202, install test 9: package the factory at its current HEADs -- the set factory 1.40.0 would
# certify: Deli Counter 0.222.0, Laser Tag 0.32.0, Level Factory 0.211.1 (its certified table re-grounded to this
# set), Lot 0.123.0, Lux 0.77.0, Patina 0.31.0, Zoo 1.112.0, with Dispatch 0.5.2, Pipeline 0.6.0 and Pixelcoat 0.62.0
# as 1.39.0 had them -- unpack it fresh, and type START_HERE.md's commands into cmd.exe there with the page's own
# `setup --venv` and its PyPI download (install_test_venv.cmd, the walker's yes of 2026-10-11), as tests 6 to 8 did.
# It counts the doctor's `drift vs certified` lines in setup's log (0.211.1 re-grounded the table, so 0 is the
# claim) and times `make` and `walk` against test 8's 7.9 and 5.6 minutes.
#     bash docs/findings/stranger_install/install_test_9.sh
F=/c/Projects/gabagool_studios/gabagool_factory
DEST='C:\stranger_202_9\gabagool'
LOG=$F/_scratch/install_202_9
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
cd /c/stranger_202_9/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
/c/stranger_202_9/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -2
ls /c/stranger_202_9/gabagool/.venv/Lib/site-packages/sitecustomize.py 2>&1 | tail -1
echo "== sitecustomize errors"
for f in setup make walk; do echo "$f: $(grep -c 'Error in sitecustomize' "$LOG/$f.txt") of $(wc -l < "$LOG/$f.txt") lines"; done
echo "== the doctor's drift lines at setup"
echo "drift vs certified: $(grep -c 'drift vs certified' "$LOG/setup.txt")  WARN rows: $(grep -c 'WARN' "$LOG/setup.txt")"
echo "== the package after the walk"
E=/c/stranger_202_9/gabagool/levels/.level_factory/exports/LF_restaurant_row_001.portable-godot
echo "files: $(find "$E" -type f | wc -l)  bake.exr: $(ls "$E/bake.exr" 2>/dev/null | wc -l)  light_bake.json ok: $(python -c "import json,sys; print(json.load(open(sys.argv[1])).get('ok'))" "$E/light_bake.json" 2>&1 | tail -1)"
echo "merged modules dropped: $(grep -c "merged Empties' modules no file names" "$LOG/make.txt")  backdrop ground: $(grep -c 'BackdropGround' "$E/site_backdrop.tscn" 2>/dev/null)"
echo "== done $(date +%H:%M:%S)"
