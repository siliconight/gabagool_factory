#!/usr/bin/env bash
# Lot 0.124.0 (patches/patch_lot_isolated_finding.py): the proof, output in prove_tests.out.txt.
#   1. the new tests against 0.123.0's tree (git archive of HEAD + the test): they cannot pass there;
#   2. the patch applied;
#   3. the Lot suite.
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
T=$(mktemp -d)
echo "== 1. lot HEAD ($(git -C $R/lot log -1 --format=%h)) + tests/test_isolated_finding.py"
(cd "$T" && git -C $R/lot archive HEAD | tar -x) || exit 1
cp $R/lot/tests/test_isolated_finding.py "$T/tests/"
(cd "$T" && python -m pytest -q tests/test_isolated_finding.py -p no:cacheprovider 2>&1 | grep -E "passed|failed|error|Error" | tail -3)
rm -rf "$T"
echo "== 2. apply"
python $R/patches/patch_lot_isolated_finding.py || exit 1
echo "== 3. lot suite"
(cd $R/lot && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3)
echo "== done"
