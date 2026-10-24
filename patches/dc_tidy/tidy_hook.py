"""Deli Counter 0.265.0, second step on the CLONE (<repo>) after tidy.py: tests/conftest.py, check.py's paths, and the
guard that keeps the root the builder's -- root_modules.txt and check.py's step that holds the root to it. Anchored;
refuses on a miss.

    python tidy_hook.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


(R / "tests" / "conftest.py").write_text('''"""The tests live in tests/ and the builder at the repo's root (0.265.0): put the root, and migrations/ for the
one-shots some tests read, on the import path, as the root's own directory was when the tests stood beside it."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "migrations"), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
''', encoding="utf-8", newline="\n")

builder = sorted(p.name for p in R.glob("*.py"))
(R / "root_modules.txt").write_text(
    "# THE ROOT IS THE BUILDER (0.265.0): every .py at this repo's root, one a line, and nothing else.\n"
    "# check.py fails on a root .py not named here and on a name here with no file. A test goes in tests/, a\n"
    "# one-shot migration in migrations/, a probe or instrument in the factory's tools/ or docs/findings/. A new\n"
    "# builder module is added here on purpose, in the change that adds it.\n"
    + "".join(n + "\n" for n in builder), encoding="utf-8", newline="\n")

edit("check.py", [
    ("""BLENDER_ONLY = [
    ("test_failing_fixtures.py",""",
     """BLENDER_ONLY = [
    ("tests/test_failing_fixtures.py","""),
    ("""AFTER_NAV_GATE = ["test_navgate_population.py"]""",
     """AFTER_NAV_GATE = ["tests/test_navgate_population.py"]


def root_is_the_builder():
    \"\"\"Every .py at the root is named in `root_modules.txt` and every name there is a file (0.265.0). The walker:
    "a way so the home root doesn't just fill up with python files". Returns the problems, none when clean.\"\"\"
    listed = [l.strip() for l in open(os.path.join(HERE, "root_modules.txt"), encoding="utf-8")
              if l.strip() and not l.startswith("#")]
    have = sorted(f for f in os.listdir(HERE) if f.endswith(".py"))
    out = ["%s stands at the root and is not in root_modules.txt: a test goes in tests/, a one-shot in "
           "migrations/, an instrument in the factory's tools/ -- or, a builder module, add it there" % f
           for f in have if f not in listed]
    out += ["root_modules.txt names %s, which is not at the root" % f for f in listed if f not in have]
    return out"""),
    ("""def main():
    rc = 0
    print("== unit suites (everything that runs without Blender) ==")""",
     """def main():
    rc = 0
    print("== the root is the builder (root_modules.txt) ==")
    problems = root_is_the_builder()
    for p in problems:
        print("   " + p)
    rc |= 1 if problems else 0
    print("== unit suites (everything that runs without Blender) ==")"""),
])
edit("tests/test_check_order.py", [
    ('POPULATION = "test_navgate_population.py"',
     'POPULATION = "tests/test_navgate_population.py"'),
])
print("conftest, root_modules.txt (%d modules), check.py, test_check_order" % len(builder))
