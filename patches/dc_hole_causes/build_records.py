"""After `build.py --all`: which tracked build records changed in more than their build time, by spec, all of them. A
probe: it reads `git diff -U0` of deli_counter/build/ against HEAD, prints and stops. (patches/dc_lint_out_of_the_build/
build_time_only.py asks the same question as a pass/fail gate and prints only its first 20.)

    python patches/dc_hole_causes/build_records.py
"""
import collections
import re
import subprocess
from pathlib import Path

DC = Path(__file__).resolve().parents[2] / "deli_counter"


def git(*args):
    return subprocess.run(["git", "-C", str(DC)] + list(args), capture_output=True, text=True, check=True).stdout


names = git("diff", "--name-only", "--", "build").split()
untracked = git("ls-files", "--others", "--exclude-standard", "--", "build").split()
moved = collections.defaultdict(list)
for n in names:
    body = [ln for ln in git("diff", "-U0", "--", n).splitlines()
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    if [ln for ln in body if not re.match(r'^[+-]\s*"built_utc": "[^"]+",?$', ln)]:
        spec, kind = Path(n).name.split(".", 1)
        moved[spec].append(kind)
print("tracked build records changed: %d; beyond built_utc: %d, in %d spec(s); untracked new under build/: %d"
      % (len(names), sum(len(v) for v in moved.values()), len(moved), len(untracked)))
for spec in sorted(moved):
    print("  %-26s %s" % (spec, ", ".join(sorted(moved[spec]))))
for n in untracked:
    print("  NEW:", n)
