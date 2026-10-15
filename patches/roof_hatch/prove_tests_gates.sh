#!/usr/bin/env bash
# Roof hatch, second cut (patches/patch_roof_hatch_gates.py: Zoo 1.113.1 + Deli Counter 0.224.1): both suites,
# output in prove_tests_gates.out.txt. The census is census_1131.log beside this file. The new circulation test
# cannot pass on 0.224.0's tree: `circulation.excused_own_furniture` does not exist there.
set -u
R=/c/Projects/gabagool_studios/gabagool_factory
T=$(mktemp -d)
echo "== 1. deli_counter HEAD ($(git -C $R/deli_counter log -1 --format=%h)) + the new circulation tests"
(cd "$T" && git -C $R/deli_counter archive HEAD | tar -x) || exit 1
cp $R/deli_counter/test_circulation.py "$T/"
(cd "$T" && python -m pytest -q test_circulation.py -p no:cacheprovider 2>&1 | grep -E "passed|failed|error|Error" | tail -3)
rm -rf "$T"
echo "== 2. zoo suite"
(cd $R/zoo && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3)
echo "== 3. deli_counter suite"
(cd $R/deli_counter && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3)
echo "== done"
