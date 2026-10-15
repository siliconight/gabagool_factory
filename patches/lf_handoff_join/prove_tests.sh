#!/bin/bash
# Prove patch_lf_handoff_join.py (0.215.1) on a throwaway copy of level_factory at its HEAD (56fd144, 0.215.0):
# the new test fails before and the file's tests pass after, the composed text printed around the join. Then apply
# it to the real repo with its result pending and run the full suite with a tally. Stops at the first step that
# fails. Removes only the throwaway copy it made, by its literal path.
F=/c/Projects/gabagool_studios/gabagool_factory
S="$1"
C="$S/lf_copy3"
TALLY='import re,sys;from collections import Counter;L=open(sys.argv[1],encoding="utf-8",errors="replace").read().splitlines();c="".join(re.sub(r"\s*\[\s*\d+%\]$","",l) for l in L if re.search(r"\[\s*\d+%\]$",l));d=dict(Counter(c));print(len(c),d)'
rm -rf "$S/lf_copy3" && mkdir -p "$C"
git -C "$F/level_factory" archive HEAD | tar -x -C "$C" || exit 2
echo "copy at $(git -C "$F/level_factory" rev-parse --short HEAD), VERSION $(cat "$C/VERSION")"
echo "== apply 0.215.1 to the copy, then run its tests against 0.215.0's export.py (the new test and the call-site test must fail)"
LF_ROOT="$C" python "$F/patches/patch_lf_handoff_join.py" --results-pending || exit 3
git -C "$F/level_factory" show HEAD:packages/exporting/export.py > "$C/packages/exporting/export.py"
(cd "$C" && python -m pytest -q tests/unit/test_layers_shown.py > "$S/prove_run3.txt" 2>&1; echo "control: exit $?")
python -c "$TALLY" "$S/prove_run3.txt"; grep -E "^FAILED" "$S/prove_run3.txt" | cut -c1-150
echo "== the patched module (must pass)"
git -C "$F/level_factory" show HEAD:packages/exporting/export.py > "$C/packages/exporting/export.py"
git -C "$F/level_factory" show HEAD:tests/unit/test_layers_shown.py > "$C/tests/unit/test_layers_shown.py"
printf '0.215.0' > "$C/VERSION"
python - "$C" <<'EOF'
import pathlib, sys
cl = pathlib.Path(sys.argv[1]) / "CHANGELOG.md"
text = cl.read_text(encoding="utf-8")
cl.write_text(text[text.index("## [0.215.0] - The backdrop's ground is unshaded"):], encoding="utf-8")
EOF
LF_ROOT="$C" python "$F/patches/patch_lf_handoff_join.py" --results-pending || exit 4
(cd "$C" && python -m pytest -q tests/unit/test_layers_shown.py > "$S/prove_run3.txt" 2>&1; echo "patched: exit $?")
python -c "$TALLY" "$S/prove_run3.txt"; grep -E "^FAILED" "$S/prove_run3.txt" | cut -c1-150
(cd "$C" && python -c "import sys; sys.path.insert(0,'.'); import packages.exporting.export as E; t=E.handoff_text({'art','gameplay','light'}, E.MODE_PORTABLE); i=t.index('WHAT THIS PACKAGE'); print(repr(t[i-40:i+30])); print('ends:', repr(t[-24:]))")
rm -rf "$S/lf_copy3" "$S/prove_run3.txt"
echo "== apply 0.215.1 to the real repo and run the suite ($(date +%H:%M:%S))"
python "$F/patches/patch_lf_handoff_join.py" --results-pending || exit 5
git -C "$F/level_factory" status --short
cd "$F/level_factory" || exit 6
s=$(date +%s)
python -m pytest -q > "$F/_scratch/lf_0215_1_suite.txt" 2>&1
e=$?
echo "suite exit=$e wall=$(( $(date +%s) - s ))s"
python -c "$TALLY" "$F/_scratch/lf_0215_1_suite.txt"
grep -E "^FAILED|^ERROR" "$F/_scratch/lf_0215_1_suite.txt" | head -5
echo "done ($(date +%H:%M:%S))"
