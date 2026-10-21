"""The combat audit over the library of two Deli Counter checkouts (argv: before, after): `combat_audit.py --all --json`
run in each with its own modules, then every finding compared by spec, code and message over the specs git tracks.
The `lf_` specs Level Factory writes into a working tree, and git ignores, are left out: the factory's checkout held
299 of them beside the 132 tracked when this was written, and a clone holds none, so counting them compares two
different libraries. A finding that is not ``[severity, code, message]`` refuses. Writes audit_compare.out.txt.

    python patches/dc_marker_routes/audit_compare.py <before checkout> <after checkout>
"""
import collections
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sides = []
for dc in sys.argv[1:3]:
    r = subprocess.run([sys.executable, "-B", "combat_audit.py", "--all", "--json"], cwd=dc, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit("REFUSED: combat_audit exited %d in %s: %s" % (r.returncode, dc, r.stderr[-500:]))
    rows = [e for e in json.loads(r.stdout) if not e["name"].startswith("lf_")]
    for e in rows:
        for x in e["findings"]:
            if not (isinstance(x, list) and len(x) == 3):
                sys.exit("REFUSED: a finding in %s is not [severity, code, message]: %r" % (e["name"], x))
    sides.append(rows)
a, b = sides
if [e["name"] for e in a] != [e["name"] for e in b]:
    sys.exit("REFUSED: the two checkouts audit different specs")
fa = collections.Counter((e["name"], x[1], x[2]) for e in a for x in e["findings"])
fb = collections.Counter((e["name"], x[1], x[2]) for e in b for x in e["findings"])
ca = collections.Counter(k[1] for k in fa.elements())
cb = collections.Counter(k[1] for k in fb.elements())
lines = ["== combat_audit.py --all over the %d tracked specs: %s -> %s" % (len(a), sys.argv[1], sys.argv[2]), "codes:"]
lines += ["  %-18s %4d -> %4d" % (c, ca[c], cb[c]) for c in sorted(set(ca) | set(cb))]
gone, new = fa - fb, fb - fa
lines.append("findings only before: %d; only after: %d" % (sum(gone.values()), sum(new.values())))
lines += ["  - %s %s %s" % (k[0], k[1], k[2][:160]) for k in sorted(gone.elements())]
lines += ["  + %s %s %s" % (k[0], k[1], k[2][:160]) for k in sorted(new.elements())]
txt = "\n".join(lines) + "\n"
(HERE / "audit_compare.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
