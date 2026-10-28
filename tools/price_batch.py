"""Price a batch: the control, the subject, the control again -- then the verdict and its action.

    python tools/price_batch.py --control <workspace> --subject <workspace> --mission <id> --out <finding dir> \
        --prefix <perf_x_>

Draw calls and frame time at fixed stations (Level Factory's `tools/perf_stations_run.py`, the stations the package's
own anchors give) for two builds of one mission, in one session with nothing else running (`docs/COMMANDS.md`):
control_a, subject, control_b. The controls are the same bytes, so their difference is the instrument's floor; the
reports land in ``<out>/<prefix><arm>.json`` and `tools/price_verdict.py` reads them and prints PASS, WATCH or FAIL
with its action (`docs/SHIPPING_A_CHANGE.md` section 5). Prints what it measured and stops.

THE CONTROL IS IMPORTED ONCE (2026-10-28). Timed on the bank's vault-rows price: each arm copied in 2-4 s, imported
headless in 66-67 s and ran the harness in 44-45 s, so import was 60% of a 6-minute price -- and the second control's
import re-imported the same bytes. Control_b now runs the harness again on control_a's imported copy, which keeps
the A-subject-A order in time (the reason for the second control: prices drift within a session as well as between
them). Every phase is timed and printed. NOT YET SHOWN: that a second harness run on an already-run copy reads as a
fresh import would. CLAUDE.md's draw-call measurement found a second lap no faster, so a large effect is not
expected -- but if there is one, the controls disagree more, the floor the verdict judges frame time against widens,
and a real frame-time cost could PASS. (Draws are counted, not timed, and are unaffected.) So the first prices run
this way must hold their floor against the separately imported ones -- 0.416-0.971 ms on the bank's five prices of
2026-10-28 -- and a floor past that range means re-importing control_b, not trusting the verdict.

Each copy is deleted once measured (a package is about 250 MB).
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import time

FACTORY = pathlib.Path(__file__).resolve().parents[1]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--control", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--mission", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--godot", default=GODOT)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    work = FACTORY / "_scratch" / ("price_" + args.prefix.strip("_")) / "perf"
    pkg = "LF_%s.portable-godot" % args.mission

    def package(ws):
        p = pathlib.Path(ws) / ".level_factory" / "exports" / pkg
        if not p.is_dir():
            raise SystemExit("no package at %s" % p)
        return p

    def prepare(tag, src):
        dst = work / tag
        t0 = time.monotonic()
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        shutil.rmtree(dst / ".godot", ignore_errors=True)
        t1 = time.monotonic()
        r = subprocess.run([args.godot, "--headless", "--path", str(dst), "--import"], capture_output=True, text=True,
                           timeout=1800)
        print("%s: copy %.0f s, import %.0f s (exit %d)" % (tag, t1 - t0, time.monotonic() - t1, r.returncode),
              flush=True)
        return dst

    def harness(tag, dst):
        t0 = time.monotonic()
        r = subprocess.run([sys.executable, str(FACTORY / "level_factory" / "tools" / "perf_stations_run.py"),
                            str(dst), "--json", str(out / ("%s%s.json" % (args.prefix, tag)))],
                           capture_output=True, text=True, timeout=3600, cwd=str(FACTORY / "level_factory"))
        print("%s: harness %.0f s (exit %d)" % (tag, time.monotonic() - t0, r.returncode), flush=True)
        if r.returncode not in (0, 1):
            print(r.stderr[-800:], flush=True)
            raise SystemExit("the harness failed on %s" % tag)

    start = time.monotonic()
    control = prepare("control", package(args.control))
    harness("control_a", control)
    subject = prepare("subject", package(args.subject))
    harness("subject", subject)
    shutil.rmtree(subject, ignore_errors=True)
    harness("control_b", control)
    shutil.rmtree(control, ignore_errors=True)
    print("price: %.0f s" % (time.monotonic() - start), flush=True)
    return subprocess.run([sys.executable, str(FACTORY / "tools" / "price_verdict.py"), "--dir", str(out),
                           "--prefix", args.prefix, "--json", str(out / ("%sverdict.json" % args.prefix))]).returncode


if __name__ == "__main__":
    sys.exit(main())
