"""Lot's suite in the proven 0.127.0 clone against a fresh clone of the factory's lot at its HEAD (0.126.1), against
Deli Counter's shipped contract. A clone outside the factory has no sibling checkouts, so the tests that read a built
Deli Counter shell fail on both sides alike; the comparison is which failures differ. Copied from
`patches/lot_npc_fallback/suite_vs_base.py`, one contract instead of two. Writes suite_clone_vs_base.out.txt here.

    python patches/lot_bus_flag/suite_vs_base.py <new scratch dir> <proven clone>
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
subprocess.run(["git", "clone", "-q", str(FACTORY / "lot"), str(root)], check=True)
shipped = FACTORY / "deli_counter" / "agent_contract.json"


def suite(where):
    env = dict(os.environ, DC_AGENT_CONTRACT=str(shipped))
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf"], cwd=where,
                       capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    tail = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed)", l)][-1:]
    failed = sorted({m.group(1) for m in re.finditer(r"^FAILED (\S+)", out, re.M)})
    assert tail, "no pass/fail line: the suite did not finish\n" + out[-2000:]
    return tail[0], failed


lines = []
base_tail, base_failed = suite(root)
new_tail, new_failed = suite(proven)
lines.append("base (lot HEAD): %s" % base_tail)
lines.append("clone (0.127.0): %s" % new_tail)
lines.append("failing in the clone only: %s" % (sorted(set(new_failed) - set(base_failed)) or "none"))
lines.append("failing in the base only: %s" % (sorted(set(base_failed) - set(new_failed)) or "none"))
lines.append("failing on both: %d" % len(set(base_failed) & set(new_failed)))
(HERE / "suite_clone_vs_base.out.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(lines))
