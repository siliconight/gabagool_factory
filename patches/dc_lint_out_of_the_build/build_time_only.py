"""After `build.py --all`: did every tracked build record change its build time alone? A checker: it reads
`git diff -U0` of deli_counter/build/ and FAILS on any changed line that is not a `built_utc` line, or on a change it
cannot read as one; it prints the counts and stops.

    python patches/dc_lint_out_of_the_build/build_time_only.py              # the working tree against HEAD
    python patches/dc_lint_out_of_the_build/build_time_only.py <commit>     # that commit against its parent

The second form is the control: on a rebuild that moved geometry it must fail, because each manifest carries
`outputs_sha256_16`, the output GLB's digest, and a moved shell changes it.
"""
import re
import subprocess
import sys
from pathlib import Path

DC = Path(__file__).resolve().parents[2] / "deli_counter"
REV = sys.argv[1:2]
RANGE = ([REV[0] + "^", REV[0]] if REV else [])
names = subprocess.run(["git", "-C", str(DC), "diff", "--name-only"] + RANGE + ["--", "build"], capture_output=True,
                       text=True, check=True).stdout.split()
untracked = [] if REV else subprocess.run(["git", "-C", str(DC), "ls-files", "--others", "--exclude-standard", "--",
                                            "build"], capture_output=True, text=True, check=True).stdout.split()
bad = []
for n in names:
    diff = subprocess.run(["git", "-C", str(DC), "diff", "-U0"] + RANGE + ["--", n], capture_output=True, text=True,
                          check=True).stdout.splitlines()
    body = [ln for ln in diff if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    other = [ln for ln in body if not re.match(r'^[+-]\s*"built_utc": "[^"]+",?$', ln)]
    if not body or other or sum(ln.startswith("+") for ln in body) != 1:
        bad.append((n, other[:3] or body[:3]))
print("%s: tracked build records changed: %d; untracked new under build/: %d; changed in more than built_utc: %d"
      % ("commit " + REV[0] if REV else "working tree", len(names), len(untracked), len(bad)))
for n, lines in bad[:20]:
    print("  NOT build time alone:", n, lines)
for n in untracked[:20]:
    print("  NEW:", n)
sys.exit(1 if bad or untracked else 0)
