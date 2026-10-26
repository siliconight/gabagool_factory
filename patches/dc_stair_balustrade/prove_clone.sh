#!/usr/bin/env bash
# The 0.268.0 clone: build every spec, nav gate every spec, the suite (junitxml). Outputs to patches/dc_stair_balustrade/.
F=/c/Projects/gabagool_studios/gabagool_factory
C=$F/_scratch/dc_bal
P=$F/patches/dc_stair_balustrade
cd $C || exit 9
python build.py --all > $P/build_all.out.txt 2>&1; rc=$?; tail -3 $P/build_all.out.txt > $P/build_all_clone.tail.txt; rm -f $P/build_all.out.txt; echo "build exit $rc"
python nav_gate.py --all > $P/navgate_all.out.txt 2>&1; echo "nav gate exit $?"; tail -1 $P/navgate_all.out.txt
python -m pytest -q -p no:cacheprovider --junitxml=../suite_0268.xml > $P/suite.out.txt 2>&1; echo "suite exit $?"
python - <<'PY'
import xml.etree.ElementTree as ET
r=ET.parse("../suite_0268.xml").getroot(); s=r if r.tag=="testsuite" else r[0]
print("tests %s failures %s errors %s skipped %s" % tuple(s.get(x) for x in ("tests","failures","errors","skipped")))
for tc in s.iter("testcase"):
    if tc.find("failure") is not None or tc.find("error") is not None: print(" FAIL",tc.get("classname"),tc.get("name"))
PY
