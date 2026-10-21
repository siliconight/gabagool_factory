"""Level Factory's suite in the proven 0.230.0 clone against a fresh 0.229.0 clone (1f6f047), both with
LF_LASERTAG_ROOT and LF_LOT_ROOT set to the factory's checkouts. Writes suite_clone_vs_base.out.txt beside this file.

The conftest replaces pytest's summary (docs/COMMANDS.md, trap 1), so each side is tallied from its progress characters
and its failures are named from `-rfE`'s short summary; a side whose named failures do not account for every F and E in
its progress refuses rather than reporting a comparison it could not make. 0.229.0 ran this comparison inline and did
not keep it; this is the kept version.

    python patches/lf_sight_contract/suite_vs_base.py <new scratch dir> <proven clone>
"""
import collections
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
root, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(FACTORY / "level_factory"), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "1f6f047"], check=True)
env = dict(os.environ, LF_LASERTAG_ROOT=str(FACTORY / "lasertag"), LF_LOT_ROOT=str(FACTORY / "lot"))


def suite(where, label):
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE"], cwd=where,
                       capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    progress = "".join(re.sub(r"\s*\[\s*\d+%\]$", "", l) for l in out.splitlines() if re.search(r"\[\s*\d+%\]$", l))
    tally = collections.Counter(progress)
    failed = sorted({m.group(1) for m in re.finditer(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})
    if len(failed) != tally["F"] + tally["E"]:
        raise SystemExit("REFUSED: %s's progress has %d F and %d E but %d failures are named; no comparison"
                         % (label, tally["F"], tally["E"], len(failed)))
    return r.returncode, len(progress), dict(tally), failed


new = suite(proven, "0.230.0")
old = suite(root, "0.229.0")
lines = ["== Level Factory's suite in the lf_sight_contract clone (0.230.0) against a fresh 0.229.0 clone (1f6f047), "
         "both with LF_LASERTAG_ROOT and LF_LOT_ROOT set to the factory's checkouts",
         "0.230.0: exit=%d %d %s" % new[:3], "0.229.0: exit=%d %d %s" % old[:3]]
only_new, only_old = sorted(set(new[3]) - set(old[3])), sorted(set(old[3]) - set(new[3]))
lines.append("failing only on 0.230.0: %d; only on 0.229.0: %d" % (len(only_new), len(only_old)))
lines += ["  only 0.230.0: " + n for n in only_new] + ["  only 0.229.0: " + n for n in only_old]
lines.append("the failures both share (each needs the factory tree beside the clone):")
lines += ["  " + n for n in sorted(set(new[3]) & set(old[3]))]
txt = "\n".join(lines) + "\n"
(HERE / "suite_clone_vs_base.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
