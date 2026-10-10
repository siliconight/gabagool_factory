"""Roadmap 221, step 3: price the per-side merge, Patina 0.29.2's dressing against 0.30.0's.

    python docs/findings/patina_cover_normals/price_merge.py <before copy> <after copy> <out dir>
    python docs/findings/patina_cover_normals/price_merge.py --compare <out dir>

Runs Level Factory's fixed-station harness (`level_factory/tools/perf_stations_run.py`) on the
BEFORE copy, the AFTER copy, and the BEFORE copy again: the two befores are the control, and
their spread is the noise floor. The copies must come from the same Level Factory version, so
the harness stands at the same stations (each package's `gameplay_anchors.json`); a heading
missing from one run stops the comparison. Headings are compared by (station, yaw).

It prints draw calls and p95 frame time, each against the controls' mean, as a mean over
headings and for the worst heading; it says what it measured and stops.
"""
import json
import statistics as st
import subprocess
import sys
from pathlib import Path

F = Path(__file__).resolve().parents[3]
HARNESS = F / "level_factory" / "tools" / "perf_stations_run.py"


def _rows(doc):
    if doc.get("schema") != "level_factory.perf_stations.v1" or not doc.get("complete"):
        raise SystemExit("UNKNOWN SHAPE: schema %r, complete %r" % (doc.get("schema"), doc.get("complete")))
    out = {}
    for row in doc.get("rows") or []:
        for h in row.get("headings") or []:
            if "draws" not in h or "ms_p95" not in h:
                raise SystemExit("UNKNOWN SHAPE: a heading without draws or ms_p95")
            out[(row.get("station"), h.get("yaw"))] = (int(h["draws"]), float(h["ms_p95"]))
    if not out:
        raise SystemExit("UNKNOWN SHAPE: no headings")
    return out


def _compare(out):
    runs = {n: _rows(json.loads((out / f"perf_{n}.json").read_text(encoding="utf-8")))
            for n in ("before_1", "after", "before_2")}
    keys = set(runs["before_1"])
    for n, r in runs.items():
        if set(r) != keys:
            print(f"STATIONS DIFFER: {n}")
            return 2
    order = sorted(keys, key=str)
    b1, b2, a = runs["before_1"], runs["before_2"], runs["after"]
    c_d = {k: st.mean((b1[k][0], b2[k][0])) for k in order}
    c_m = {k: st.mean((b1[k][1], b2[k][1])) for k in order}
    print("controls' spread, median over %d headings: p95 %.2f ms, draws %.1f"
          % (len(order), st.median(abs(b1[k][1] - b2[k][1]) for k in order),
             st.median(abs(b1[k][0] - b2[k][0]) for k in order)))
    for name, r in runs.items():
        dd = [r[k][0] - c_d[k] for k in order]
        dm = [r[k][1] - c_m[k] for k in order]
        print("%-9s draws %+7.1f mean, %+5.0f worst heading;  p95 %+6.2f ms median, %+6.2f mean"
              % (name, st.mean(dd), min(dd, key=lambda v: -abs(v)), st.median(dm), st.mean(dm)))
    return 0


def main():
    if sys.argv[1] == "--compare":
        return _compare(Path(sys.argv[2]))
    before, after, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    for name, pkg in (("before_1", before), ("after", after), ("before_2", before)):
        dest = out / f"perf_{name}.json"
        proc = subprocess.run([sys.executable, str(HARNESS), str(pkg), "--json", str(dest)],
                              capture_output=True, text=True, timeout=1800)
        if not dest.exists():
            print("NOT MEASURED: %s (exit %d)" % (name, proc.returncode))
            for line in (proc.stdout or "").splitlines()[-8:]:
                print(line)
            return 2
        print("measured", name)
    return _compare(out)


if __name__ == "__main__":
    sys.exit(main())
