#!/usr/bin/env bash
# Patina 0.32.0 (patches/patch_patina_godot_half_gone.py): the proof, in order, output in prove_tests.out.txt.
#   1. the drift the test pins, read off the unpatched tree (version.py against VERSION);
#   2. the patch applied;
#   3. the new test alone, then the whole suite;
#   4. the test proven to fail without the fix: version.py flipped back to 0.30.0, the test run, flipped forward.
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
P=$R/patina
cd "$P" || exit 1
echo "== 1. unpatched tree: module version against VERSION"
python -c "import patina; print('patina.__version__ =', patina.__version__)"
echo "VERSION file = $(cat VERSION)"
echo "== 2. apply"
python "$R/patches/patch_patina_godot_half_gone.py" || exit 1
git status --short | head -20
echo "== 3a. the new test alone"
python -m pytest -q tests/test_version_file.py -p no:cacheprovider 2>&1 | tail -3
echo "== 3b. the whole suite"
python -m pytest -q -p no:cacheprovider 2>&1 | tail -4
echo "== 4. without the fix: version.py back to 0.30.0, the test, then forward again"
python - <<'EOF'
import pathlib
p = pathlib.Path("patina/version.py")
t = p.read_text(encoding="utf-8")
assert t.count('__version__ = "0.32.0"') == 1
p.write_text(t.replace('__version__ = "0.32.0"', '__version__ = "0.30.0"'), encoding="utf-8", newline="\n")
EOF
python -m pytest -q tests/test_version_file.py -p no:cacheprovider 2>&1 | tail -3
python - <<'EOF'
import pathlib
p = pathlib.Path("patina/version.py")
t = p.read_text(encoding="utf-8")
assert t.count('__version__ = "0.30.0"') == 1
p.write_text(t.replace('__version__ = "0.30.0"', '__version__ = "0.32.0"'), encoding="utf-8", newline="\n")
EOF
grep -n "__version__ = " patina/version.py
echo "== done"
