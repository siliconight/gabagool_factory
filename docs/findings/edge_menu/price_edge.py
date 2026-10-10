"""Price each edge option with Level Factory's fixed-station harness, against two controls.

    python docs/findings/edge_menu/price_edge.py <walk copy with edge_proto installed> <out dir>
    python docs/findings/edge_menu/price_edge.py --compare <out dir>     # re-read the kept reports

Runs `level_factory/tools/perf_stations_run.py` once per option, in this order:
control, C, B, D, A, F, control. `EDGE_OPTION` picks the parts, and the harness's Godot inherits
it. Each report is kept as `<out dir>/perf_<name>.json`. It prints, per option, over every
station and heading the harness stood at:
  - draw calls: mean and worst;
  - p95 frame time: the median over headings;
  - each against the mean of the two controls.
The controls' spread is the noise floor: a difference inside it is not a difference.

A report in a shape this does not know stops the run (schema `level_factory.perf_stations.v1`,
`complete` true, rows with headings). Headings are compared by (station, yaw), not by position.
RETRACTED, kept: the first version compared the lists in order and refused the run, because the
harness may list a station's headings in another order from one run to the next. It measures
and prints; what the numbers mean belongs in the README.
"""
import json
import os
import statistics as st
import subprocess
import sys
from pathlib import Path

F = Path(__file__).resolve().parents[3]
HARNESS = F / "level_factory" / "tools" / "perf_stations_run.py"
RUNS = (("control_1", ""), ("C", "wall_dark,glow"), ("B", "wall_dark,glow,trees"),
        ("D", "fence,glow,trees"), ("A", "wall_dark,glow,houses,tower"),
        ("F", "fence,glow,trees,houses_far,tower"), ("control_2", ""))


def _headings(doc):
    if doc.get("schema") != "level_factory.perf_stations.v1" or not doc.get("complete"):
        raise SystemExit("UNKNOWN SHAPE: schema %r, complete %r" % (doc.get("schema"), doc.get("complete")))
    out = []
    for row in doc.get("rows") or []:
        for h in row.get("headings") or []:
            if "draws" not in h or "ms_p95" not in h:
                raise SystemExit("UNKNOWN SHAPE: a heading without draws or ms_p95: %r" % sorted(h))
            out.append((row.get("station"), h.get("yaw"), int(h["draws"]), float(h["ms_p95"])))
    if not out:
        raise SystemExit("UNKNOWN SHAPE: no headings")
    return out


def _compare(got):
    """Print each option against the two controls' mean, heading by heading (station, yaw)."""
    tables = {n: {(s, y): (d, m) for s, y, d, m in rows} for n, rows in got.items()}
    keys = set(tables["control_1"])
    for name, tab in tables.items():
        if set(tab) != keys:
            print("STATIONS DIFFER: %s stood at %d headings control_1 did not, and missed %d"
                  % (name, len(set(tab) - keys), len(keys - set(tab))))
            return 2
    order = sorted(keys, key=str)
    c1, c2 = tables["control_1"], tables["control_2"]
    c_draws = {k: st.mean((c1[k][0], c2[k][0])) for k in order}
    c_ms = {k: st.mean((c1[k][1], c2[k][1])) for k in order}
    noise = st.median(abs(c1[k][1] - c2[k][1]) for k in order)
    dnoise = st.median(abs(c1[k][0] - c2[k][0]) for k in order)
    print("controls' spread, median over %d headings: p95 %.2f ms, draws %.1f (the noise floor)"
          % (len(order), noise, dnoise))
    print("%-9s %12s %12s %16s" % ("option", "draws +mean", "draws +max", "p95 +median ms"))
    for name, tab in tables.items():
        dd = [tab[k][0] - c_draws[k] for k in order]
        dm = [tab[k][1] - c_ms[k] for k in order]
        print("%-9s %12.1f %12.0f %16.2f" % (name, st.mean(dd), max(dd), st.median(dm)))
    return 0


def main():
    if sys.argv[1] == "--compare":
        out = Path(sys.argv[2])
        got = {name: _headings(json.loads((out / ("perf_%s.json" % name)).read_text(encoding="utf-8")))
               for name, _opt in RUNS}
        return _compare(got)
    pkg, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    got = {}
    for name, opt in RUNS:
        dest = out / ("perf_%s.json" % name)
        env = dict(os.environ, EDGE_OPTION=opt)
        proc = subprocess.run([sys.executable, str(HARNESS), str(pkg), "--json", str(dest)],
                              env=env, capture_output=True, text=True, timeout=1800)
        if not dest.exists():
            print("NOT MEASURED: %s (exit %d)" % (name, proc.returncode))
            for line in (proc.stdout or "").splitlines()[-8:]:
                print(line)
            return 2
        got[name] = _headings(json.loads(dest.read_text(encoding="utf-8")))
        h = got[name]
        print("measured %-9s %3d headings  draws mean %.0f worst %d  p95 median %.2f ms"
              % (name, len(h), st.mean(x[2] for x in h), max(x[2] for x in h),
                 st.median(x[3] for x in h)))
    return _compare(got)


if __name__ == "__main__":
    sys.exit(main())
