#!/bin/bash
# Roadmap 202, install test 5: package the factory at its current HEADs (the set factory 1.37.0
# would certify), unpack it fresh, and type START_HERE.md's commands into cmd.exe there with the
# page's own `setup --venv` and its PyPI download (docs/findings/stranger_install/install_test_venv.cmd).
# Install test 4's one finding -- Blender's sitecustomize erroring in the venv -- is Level Factory
# 0.178.1's to have fixed: this test counts that error line in every log.
#     bash docs/findings/stranger_install/install_test_5.sh
F=/c/Projects/gabagool_studios/gabagool_factory
DEST='C:\stranger_202_5\gabagool'
LOG=$F/_scratch/install_202_5
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
cd /c/stranger_202_5/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
/c/stranger_202_5/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -2
ls /c/stranger_202_5/gabagool/.venv/Lib/site-packages/sitecustomize.py 2>&1 | tail -1
echo "== sitecustomize errors"
for f in setup make walk; do echo "$f: $(grep -c 'Error in sitecustomize' "$LOG/$f.txt") of $(wc -l < "$LOG/$f.txt") lines"; done
echo "== done $(date +%H:%M:%S)"
