"""Every layout_lint finding (lint_spec: fails and warns) for the named specs, against the Deli Counter checkout given first.

    python full_lint.py <deli_counter> <out.json> spec_a,spec_b,...

Prints nothing; writes {spec: {fails, warns}}. Run on 0.233.0 and on 0.234.0 and diff: lint_0233.json, lint_0234.json.
"""
import glob, json, os, sys
DC = sys.argv[1]; sys.path.insert(0, DC); os.chdir(DC)
import layout_lint
names = sys.argv[3].split(",")
out = {}
for n in names:
    d = json.load(open(os.path.join("specs", n + ".json"), encoding="utf-8"))
    _x, fails, warns = layout_lint.lint_spec(d, n)
    out[n] = {"fails": fails, "warns": warns}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
