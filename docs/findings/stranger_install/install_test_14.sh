#!/bin/bash
# Roadmap 202, install test 14: package the factory at its current HEADs -- the set factory 1.42.1 would certify:
# 1.42.0's set with the tools' licences and Level Factory's grounded table caught up -- Deli Counter 0.286.1,
# Dispatch 0.5.4, Laser Tag 0.32.1, Level Factory 0.262.1 (`contracts.GROUNDED` re-grounded, eight rows), Lot
# 0.135.0, Lux 0.80.0, Patina 0.32.1, Pipeline 0.6.1, Pixelcoat 0.63.0, Zoo 1.142.0 -- unpack it fresh, and type
# START_HERE.md's commands into cmd.exe there with the page's own `setup --venv` and its PyPI download
# (install_test_venv.cmd), as tests 6 to 13 did. Copied from install_test_13.sh; its names changed. The claim:
# setup's doctor reads 0 `drift vs certified` lines, where test 13 read 5 because 1.42.0 was certified without
# re-grounding; make picks seed 9205 again and ships it; the walk climbs deli_a01's two ladders and the shot bot
# frames five stations.
#     bash docs/findings/stranger_install/install_test_14.sh
F=/c/Projects/gabagool_studios/gabagool_factory
DEST='C:\stranger_202_14\gabagool'
LOG=$F/_scratch/install_202_14
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
cd /c/stranger_202_14/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
/c/stranger_202_14/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -2
ls /c/stranger_202_14/gabagool/.venv/Lib/site-packages/sitecustomize.py 2>&1 | tail -1
echo "== sitecustomize errors"
for f in setup make walk; do echo "$f: $(grep -c 'Error in sitecustomize' "$LOG/$f.txt") of $(wc -l < "$LOG/$f.txt") lines"; done
echo "== the doctor's drift lines at setup"
echo "drift vs certified: $(grep -c 'drift vs certified' "$LOG/setup.txt")  WARN rows: $(grep -c 'WARN' "$LOG/setup.txt")"
echo "== the package after the walk"
E=/c/stranger_202_14/gabagool/levels/.level_factory/exports/LF_restaurant_row_001.portable-godot
echo "files: $(find "$E" -type f | wc -l)  bake.exr: $(ls "$E/bake.exr" 2>/dev/null | wc -l)  light_bake.json ok: $(python -c "import json,sys; print(json.load(open(sys.argv[1])).get('ok'))" "$E/light_bake.json" 2>&1 | tail -1)"
echo "merged modules dropped: $(grep -c "merged Empties' modules no file names" "$LOG/make.txt")  backdrop ground: $(grep -c 'BackdropGround' "$E/site_backdrop.tscn" 2>/dev/null)"
echo "== what the buildings' merge kept"
grep "buildings merged" "$LOG/make.txt"
for s in "$E"/lot/*/site.tscn; do echo "$(basename "$(dirname "$s")"): ladder_area3d $(grep -c 'ladder_area3d' "$s"), dc_marker $(grep -c 'dc_marker' "$s")"; done | grep -v ": ladder_area3d 0, dc_marker 0"
grep "walk bot\|shot bot\|stations" "$LOG/walk.txt"
echo "== done $(date +%H:%M:%S)"
