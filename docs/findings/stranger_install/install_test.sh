#!/bin/bash
# Roadmap 202's install test N: package the factory at its current HEADs, unpack it into a folder
# that has never held a factory, and type START_HERE.md's commands into cmd.exe there
# (install_test.cmd, beside this). Logs go to _scratch/install_202_<N>/; the folder it unpacks
# into, C:\stranger_202_<N>\gabagool, is the test's own and is removed after its record is filed.
#
#     bash docs/findings/stranger_install/install_test.sh <N>
#
# install_test_2.sh is this, written for test 2 alone, and kept as it ran.
N="$1"
[ -n "$N" ] || { echo "usage: install_test.sh <N>"; exit 2; }
F=$(cd "$(dirname "$0")/../../.." && pwd)
LOG=$F/_scratch/install_202_$N
DEST_WIN="C:\\stranger_202_$N\\gabagool"
mkdir -p "$LOG"
cd "$F" || exit 1
[ ! -e "/c/stranger_202_$N" ] || { echo "C:\\stranger_202_$N already exists: not a fresh folder"; exit 2; }
echo "== package $(date +%H:%M:%S)"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/make_factory_package.ps1 > "$LOG/package.txt" 2>&1
echo "package exit $?"
ZIP=$(grep -o "package: .*\.zip" "$LOG/package.txt" | sed 's/^package: //')
echo "zip: $ZIP"
[ -n "$ZIP" ] || exit 2
echo "== unpack $(date +%H:%M:%S)"
powershell.exe -NoProfile -Command "New-Item -ItemType Directory -Path '$DEST_WIN' -Force | Out-Null; Expand-Archive -LiteralPath '$ZIP' -DestinationPath '$DEST_WIN'" > "$LOG/unpack.txt" 2>&1
echo "unpack exit $?"
cd "/c/stranger_202_$N/gabagool" || exit 3
echo "== test $(date +%H:%M:%S)"
cmd.exe //c "$(cygpath -w "$F/docs/findings/stranger_install/install_test.cmd")" "$DEST_WIN" "$(cygpath -w "$LOG")" > "$LOG/steps.txt" 2>&1
echo "test exit $?"
cat "$LOG/steps.txt"
# What a stranger's first doctor says. Cold run 9223's notes named one of its two WARNs and the
# other, a grounded-table drift, would have shipped in the package: every row that is not PASS is
# printed here, and a setup.txt with no doctor rows is a shape this cannot read.
echo "== the doctor's rows in setup.txt that are not PASS"
ROWS=$(grep -a -E '^ *\[[A-Z_]+ *\] ' "$LOG/setup.txt" | tr -d '\r')
if [ -z "$ROWS" ]; then
  echo "setup.txt holds no doctor rows: nothing read"
  exit 4
fi
echo "$ROWS" | grep -v -E '^ *\[PASS +\] ' || echo "  none: every row PASS"
echo "== done $(date +%H:%M:%S)"
