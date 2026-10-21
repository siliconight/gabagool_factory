"""Lot's suite in the proven 0.126.1 clone against a fresh 0.126.0 clone (49dcf8d), each run twice: against Deli
Counter's shipped contract (0.252.0) and against the 0.253.0 clone's, named by DC_AGENT_CONTRACT. A clone outside the
factory has no sibling checkouts, so the tests that read a built Deli Counter shell fail on both sides alike; the
comparison is which failures differ. Writes suite_clone_vs_base.out.txt beside this file.

    python patches/lot_npc_fallback/suite_vs_base.py <new scratch dir> <proven clone> <0.253.0 contract>
"""
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
root, proven, new_contract = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
assert not root.exists(), "the scratch dir must be new"
assert new_contract.is_file(), new_contract
subprocess.run(["git", "clone", "-q", str(FACTORY / "lot"), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "49dcf8d"], check=True)
shipped = FACTORY / "deli_counter" / "agent_contract.json"


def suite(where, contract):
    env = dict(os.environ, DC_AGENT_CONTRACT=str(contract))
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf"], cwd=where,
                       capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    tail = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed)", l)][-1:]
    failed = sorted({m.group(1) for m in re.finditer(r"^FAILED (\S+)", out, re.M)})
    return r.returncode, (tail or ["(no summary)"])[0].strip(), failed


lines = ["== Lot's suite in the lot_npc clone (0.126.1) against a fresh 0.126.0 clone (49dcf8d), neither beside the "
         "factory's other repos"]
for label, contract in (("Deli Counter 0.252.0's contract (the factory's)", shipped),
                        ("Deli Counter 0.253.0's contract (the dc_eye clone)", new_contract)):
    new, old = suite(proven, contract), suite(root, contract)
    lines += ["-- " + label, "  0.126.1: exit=%d %s" % new[:2], "  0.126.0: exit=%d %s" % old[:2]]
    only_new, only_old = sorted(set(new[2]) - set(old[2])), sorted(set(old[2]) - set(new[2]))
    lines.append("  failing only on 0.126.1: %d; only on 0.126.0: %d; on both: %d"
                 % (len(only_new), len(only_old), len(set(new[2]) & set(old[2]))))
    lines += ["    only 0.126.1: " + n for n in only_new] + ["    only 0.126.0: " + n for n in only_old]
txt = "\n".join(lines) + "\n"
(HERE / "suite_clone_vs_base.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
