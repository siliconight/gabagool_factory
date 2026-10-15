#!/usr/bin/env bash
# Roof hatch (patches/patch_roof_hatch.py: Zoo 1.113.0 + Deli Counter 0.224.0): the proof, output in
# prove_tests.out.txt.
#   1. the new Deli Counter test against 0.223.0's tree (git archive of HEAD + the test): it cannot pass there;
#   2. the Zoo suite (pure; the Blender census is census.log beside this file);
#   3. the Deli Counter suite.
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
T=$(mktemp -d)
echo "== 1. deli_counter HEAD ($(git -C $R/deli_counter log -1 --format=%h)) + test_roof_hatch.py"
(cd "$T" && git -C $R/deli_counter archive HEAD | tar -x) || exit 1
cp $R/deli_counter/test_roof_hatch.py "$T/"
(cd "$T" && python -m pytest -q test_roof_hatch.py -p no:cacheprovider 2>&1 | grep -E "passed|failed|error|Error" | tail -3)
rm -rf "$T"
echo "== 2. zoo suite"
(cd $R/zoo && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3)
echo "== 3. deli_counter suite"
(cd $R/deli_counter && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3)
echo "== done"
