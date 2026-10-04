"""Deli Counter 0.175.1: the nav baseline check runs after the nav gate.

`check.py` ran `test_navgate_population.py` in its first pytest sweep, before
`nav_gate.py --all` wrote the `build/*.navgate.json` that test reads, so a new
unjudged shell passed on the commit that added it (0.174.0's six Empties did,
and 0.175.0's hook refused for them). See
`dc_navgate_order/CHANGELOG_0.175.1.md`.

Anchored edits to `check.py` (every anchor once; refuses on a miss). Copies
`dc_navgate_order/test_check_order.py`; CHANGELOG and VERSION. No geometry
source changes, so no rebuild (`build_freshness.GEOMETRY_SOURCES`).

    python patch_dc_navgate_order.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_navgate_order"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


LIST_OLD = '''     "imports bmesh -- needs a real Blender interpreter, not plain python"),
]
'''
LIST_NEW = '''     "imports bmesh -- needs a real Blender interpreter, not plain python"),
]

# Test files that READ WHAT THE NAV GATE WRITES. They run straight after
# `nav_gate.py --all`, never in the first sweep: there, a shell built for the
# commit being checked has no `build/<name>.navgate.json` yet, so it is never
# compared and a new unjudged shell passes on the commit that adds it.
# Measured 2026-10-04: 0.174.0 added six rowhome Empties and committed clean,
# and 0.175.0's hook refused for them -- their nav results were first written
# during that hook. A test that opens build/*.navgate.json belongs here.
AFTER_NAV_GATE = ["test_navgate_population.py"]
'''

SWEEP_OLD = '''            skipped.append((f, why))
    rc |= run(args)
'''
SWEEP_NEW = '''            skipped.append((f, why))
    args += ["--ignore=" + f for f in AFTER_NAV_GATE]
    rc |= run(args)
'''

NAV_OLD = '''    rc |= run(["nav_gate.py", "--all"])
'''
NAV_NEW = '''    rc |= run(["nav_gate.py", "--all"])
    print("== nav results against their baseline (reads what the gate just wrote) ==")
    rc |= run(["-m", "pytest", "-q"] + AFTER_NAV_GATE)
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.175.0"
    _edit(DC / "check.py", [(LIST_OLD, LIST_NEW), (SWEEP_OLD, SWEEP_NEW), (NAV_OLD, NAV_NEW)])
    shutil.copyfile(SRC / "test_check_order.py", DC / "test_check_order.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.175.1.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.175.1", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.175.1")


if __name__ == "__main__":
    main()
