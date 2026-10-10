#!/bin/bash
# Roadmap 202, install test 2: package the factory at its current HEADs, unpack it fresh, and type
# START_HERE.md's commands into cmd.exe there (docs/findings/stranger_install/install_test.cmd).
F=/c/Projects/gabagool_studios/gabagool_factory
LOG=$F/_scratch/install_202b
mkdir -p "$LOG"
cd "$F" || exit 1
echo "== package $(date +%H:%M:%S)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/make_factory_package.ps1 > "$LOG/package.txt" 2>&1
echo "package exit $?"
ZIP=$(grep -o "package: .*\.zip" "$LOG/package.txt" | sed 's/^package: //')
echo "zip: $ZIP"
[ -n "$ZIP" ] || exit 2
echo "== unpack $(date +%H:%M:%S)"
powershell.exe -NoProfile -Command "New-Item -ItemType Directory -Path 'C:\stranger_202b\gabagool' -Force | Out-Null; Expand-Archive -LiteralPath '$ZIP' -DestinationPath 'C:\stranger_202b\gabagool'" > "$LOG/unpack.txt" 2>&1
echo "unpack exit $?"
cd /c/stranger_202b/gabagool || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w $F/docs/findings/stranger_install/install_test.cmd)" "C:\\stranger_202b\\gabagool" "$(cygpath -w $LOG)" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
echo "== done $(date +%H:%M:%S)"
