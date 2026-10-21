"""Deli Counter's suite in the proven 0.254.0 clone against a fresh 0.253.0 clone (ca7e45a8). Writes
suite_clone_vs_base.out.txt beside this file. Copied from `patches/dc_npc_body/suite_vs_base.py`, its
versions changed; that copied one that copied `patches/dc_marker_routes/suite_vs_base.py`, for Deli
Counter: its tests stand at the repository root and pytest's own summary line is kept, so each side is read from that
line and its failures named from `-rfE`'s short summary; a side whose named failures do not account for its summary's
failed and error counts refuses rather than reporting a comparison it could not make.

    python patches/dc_axonometric/suite_vs_base.py <new scratch dir> <proven clone>
"""
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
root, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(FACTORY / "deli_counter"), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "ca7e45a8"], check=True)


def suite(where, label):
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE"], cwd=where,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ))
    out = r.stdout + r.stderr
    summary = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed)", l) and " in " in l]
    if not summary:
        raise SystemExit("REFUSED: %s printed no pytest summary line; no comparison" % label)
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|errors?|xfailed|xpassed)", summary[-1])}
    failed = sorted({m.group(1) for m in re.finditer(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})
    want = counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0)
    if len(failed) != want:
        raise SystemExit("REFUSED: %s's summary counts %d failed or errored but %d are named; no comparison"
                         % (label, want, len(failed)))
    return r.returncode, summary[-1].strip("= "), failed


new = suite(proven, "0.254.0")
old = suite(root, "0.253.0")
lines = ["== Deli Counter's suite in the dc_axo clone (0.254.0) against a fresh 0.253.0 clone (ca7e45a8)",
         "0.254.0: exit=%d  %s" % new[:2], "0.253.0: exit=%d  %s" % old[:2]]
only_new, only_old = sorted(set(new[2]) - set(old[2])), sorted(set(old[2]) - set(new[2]))
lines.append("failing only on 0.254.0: %d; only on 0.253.0: %d" % (len(only_new), len(only_old)))
lines += ["  only 0.254.0: " + n for n in only_new] + ["  only 0.253.0: " + n for n in only_old]
lines.append("the failures both share:")
lines += ["  " + n for n in sorted(set(new[2]) & set(old[2]))]
txt = "\n".join(lines) + "\n"
(HERE / "suite_clone_vs_base.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
