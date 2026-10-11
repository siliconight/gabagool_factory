#!/bin/bash
# Roadmap 202, install test 4: the certified package (factory-v1.36.0, the zip on GitHub Releases)
# unpacked fresh, and START_HERE.md's commands typed into cmd.exe there with the page's own
# `setup --venv` (docs/findings/stranger_install/install_test_venv.cmd) -- the first install test
# that makes the factory's Python from Blender's and downloads the three packages from PyPI, which
# waited for the walker's yes (2026-10-11). Nothing is packaged here: the zip is the released one.
#     bash docs/findings/stranger_install/install_test_4.sh
F=/c/Projects/gabagool_studios/gabagool_factory
ZIP='C:\Projects\gabagool_studios\gabagool_factory_package_factory-v1.36.0.zip'
DEST='C:\stranger_202_4\gabagool'
LOG=$F/_scratch/install_202_4
mkdir -p "$LOG"
cd "$F" || exit 1
echo "== unpack $(date +%H:%M:%S)  $ZIP"
powershell.exe -NoProfile -Command "if (Test-Path '$DEST') { Remove-Item -Recurse -Force '$DEST' }; New-Item -ItemType Directory -Path '$DEST' -Force | Out-Null; Expand-Archive -LiteralPath '$ZIP' -DestinationPath '$DEST' -Force" > "$LOG/unpack.txt" 2>&1
echo "unpack exit $?"
cd /c/stranger_202_4/gabagool || exit 3
ls | head -20 > "$LOG/unpacked_ls.txt"
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test_venv.cmd)" "$DEST" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== venv $(date +%H:%M:%S)"
ls /c/stranger_202_4/gabagool/.venv/Scripts 2>/dev/null | head -5
/c/stranger_202_4/gabagool/.venv/Scripts/python.exe -c "import sys, PIL, pygltflib, jsonschema; print(sys.version.split()[0], PIL.__version__, pygltflib.__version__, jsonschema.__version__)" 2>&1 | tail -1
echo "== done $(date +%H:%M:%S)"
