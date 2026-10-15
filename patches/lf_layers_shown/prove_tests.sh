#!/bin/bash
# Prove patch_lf_layers_shown.py (0.213.0) and patch_lf_venv_pins.py (0.214.0) on a throwaway copy of
# level_factory at its HEAD (775cac8, 0.212.0), LF_ROOT pointing at the copy; the real repo untouched.
# Each new test is run before its patch (must fail) and after (must pass); each patch's anchors assert.
# Level Factory's conftest prints no pass/fail summary (COMMANDS.md trap 1), so every run is read by its
# exit code and a tally of the progress characters; failures are listed by name.
F=/c/Projects/gabagool_studios/gabagool_factory
S="$1"
C="$S/lf_copy"
TALLY='import re,sys;from collections import Counter;L=open(sys.argv[1],encoding="utf-8",errors="replace").read().splitlines();c="".join(re.sub(r"\s*\[\s*\d+%\]$","",l) for l in L if re.search(r"\[\s*\d+%\]$",l));print("tally",len(c),dict(Counter(c)))'
run_tests() {   # run_tests <label> <test files...>: exit code, tally, FAILED lines
  local label="$1"; shift
  (cd "$C" && python -m pytest -q "$@" > "$S/prove_run.txt" 2>&1; echo "$label: exit $?")
  python -c "$TALLY" "$S/prove_run.txt"
  grep -E "^FAILED|^ERROR" "$S/prove_run.txt" | cut -c1-150
}
rm -rf "$C" && mkdir -p "$C"
git -C "$F/level_factory" archive HEAD | tar -x -C "$C" || exit 2
echo "copy at $(git -C "$F/level_factory" rev-parse --short HEAD), VERSION $(cat "$C/VERSION")"
echo "== 0.213.0's tests on the unpatched copy (must fail)"
cp "$F/patches/lf_layers_shown/test_layers_shown.py.txt" "$C/tests/unit/test_layers_shown.py"
run_tests "unpatched, 0.213.0's tests" tests/unit/test_layers_shown.py
rm "$C/tests/unit/test_layers_shown.py"
echo "== apply 0.213.0"
LF_ROOT="$C" python "$F/patches/patch_lf_layers_shown.py" --results-pending || exit 3
(cd "$C" && python -c "import sys; sys.path.insert(0,'.'); import packages.exporting.export as E; print('export.py imports; helpers:', callable(E.output_layers_record), callable(E.handoff_layers_text))") || exit 4
echo "== 0.213.0's tests on the patched copy (must pass), with the label, planner and manifest tests beside them"
run_tests "patched 0.213.0" tests/unit/test_layers_shown.py tests/unit/test_light_layer.py tests/unit/test_planner_graph.py tests/unit/test_manifest_lists_what_ships.py
echo "== a HANDOFF paragraph and a log line, as the export would write them for a lit full-stack package"
(cd "$C" && python -c "import sys; sys.path.insert(0,'.'); import packages.exporting.export as E; print(E.handoff_layers_text({'art','gameplay','light'}, E.MODE_PORTABLE)); r=E.output_layers_record({'art','gameplay','light'}); print(r)")
echo "== apply 0.214.0 on top"
LF_ROOT="$C" python "$F/patches/patch_lf_venv_pins.py" --results-pending || exit 5
echo "== 0.214.0's tests on the patched copy (must pass)"
run_tests "patched 0.214.0" tests/unit/test_setup_venv.py
echo "== the same tests against 0.213.0's interpreter.py and setup command (the restated test and the two new ones must fail, nothing else)"
git -C "$F/level_factory" show HEAD:packages/tools/interpreter.py > "$C/packages/tools/interpreter.py"
git -C "$F/level_factory" show HEAD:apps/cli/commands/__init__.py > "$C/apps/cli/commands/__init__.py"
run_tests "control" tests/unit/test_setup_venv.py
echo "== heads"
head -1 "$C/CHANGELOG.md"; cat "$C/VERSION"; echo
rm -rf "$C" "$S/prove_run.txt"
echo "copy removed"
