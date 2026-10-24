#!/usr/bin/env bash
# The 0.267.0 clone from nothing: a fresh clone of deli_counter, the edit, both migrations (pallets first, which
# refurnishes the specs it splits, then the safes' paint), each migration's re-run, then build every spec, nav gate
# every spec, the suite (junitxml). Outputs to patches/dc_pallets_safes/.
# The first proof (dc_pal3, migrations without the refurnish) failed four fixed-point-of-furnish tests on the six
# delis the pile stands in: suite_draft1.out.txt. The second (dc_pal4, refurnished, the pile counted as six stacks)
# emptied those stockrooms of five pieces each: furniture_kept.py, run now on every proof. The third (dc_pal5) gave
# the stacks a `pile` key, which the spec loader refuses: migrations_draft3.out.txt, suite_draft3.out.txt.
F=/c/Projects/gabagool_studios/gabagool_factory
C=$F/_scratch/dc_pal6
P=$F/patches/dc_pallets_safes
rm -rf "${C:?}"
git clone -q $F/deli_counter $C || exit 9
python $P/edit_dc_pallets_safes.py $C > $P/edit.out.txt 2>&1 || { echo "EDIT FAILED"; cat $P/edit.out.txt; exit 1; }
cd $C || exit 9
{ python migrations/migrate_pallet_pile.py && python migrations/migrate_safe_paint.py && \
  python migrations/migrate_pallet_pile.py --check && python migrations/migrate_safe_paint.py --check; } > $P/migrations.out.txt 2>&1
echo "migrations exit $?"; cat $P/migrations.out.txt
python $P/furniture_kept.py $C > $P/furniture_kept.out.txt 2>&1; echo "furniture kept exit $?"; tail -1 $P/furniture_kept.out.txt
python build.py --all > $P/build_all.out.txt 2>&1; rc=$?; tail -3 $P/build_all.out.txt > $P/build_all_clone.tail.txt; rm -f $P/build_all.out.txt; echo "build exit $rc"
python nav_gate.py --all > $P/navgate_all.out.txt 2>&1; echo "nav gate exit $?"; tail -1 $P/navgate_all.out.txt
python -m pytest -q -p no:cacheprovider --junitxml=../suite_0267.xml > $P/suite.out.txt 2>&1; echo "suite exit $?"
python - <<'PY'
import xml.etree.ElementTree as ET
r=ET.parse("../suite_0267.xml").getroot(); s=r if r.tag=="testsuite" else r[0]
print("tests %s failures %s errors %s skipped %s" % tuple(s.get(x) for x in ("tests","failures","errors","skipped")))
for tc in s.iter("testcase"):
    if tc.find("failure") is not None or tc.find("error") is not None: print(" FAIL",tc.get("classname"),tc.get("name"))
PY
git status -s | grep -v "^ M build/" | grep -c . ; git status -s -- specs | wc -l
