#!/usr/bin/env bash
# The 0.266.0 clone: build every spec, nav gate every spec, the suite (junitxml). Outputs to patches/dc_bins_on_walls/.
cd /c/Projects/gabagool_studios/gabagool_factory/_scratch/dc_bins_d || exit 9
P=/c/Projects/gabagool_studios/gabagool_factory/patches/dc_bins_on_walls
python build.py --all > $P/build_all.out.txt 2>&1; echo "build exit $?"
python nav_gate.py --all > $P/navgate_all.out.txt 2>&1; echo "nav gate exit $?"
python -m pytest -q -p no:cacheprovider --junitxml=../suite_0266.xml > $P/suite.out.txt 2>&1; echo "suite exit $?"
python - <<'PY'
import xml.etree.ElementTree as ET
r=ET.parse("../suite_0266.xml").getroot(); s=r if r.tag=="testsuite" else r[0]
print("tests %s failures %s errors %s skipped %s" % tuple(s.get(x) for x in ("tests","failures","errors","skipped")))
for tc in s.iter("testcase"):
    if tc.find("failure") is not None or tc.find("error") is not None: print(" FAIL",tc.get("classname"),tc.get("name"))
PY
