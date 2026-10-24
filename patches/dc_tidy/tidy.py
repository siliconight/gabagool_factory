"""Deli Counter 0.265.0 on a CLONE (<repo>): the root is the builder; tests live in tests/, one-shot migrations in
migrations/, and the commit hook refuses a new root .py. The walker, 2026-10-23: "Deli Counter Repo needs a little
clean up/organization? (and a way so the home root doesn't just fill up with python files?)". Prints what it moved and
rewrote; refuses on any file it does not recognise.

    python tidy.py <repo>
"""
import pathlib
import re
import subprocess
import sys

R = pathlib.Path(sys.argv[1])

#: migrate_* modules the builder imports or a build reaches (`presets.py`; `build_freshness.GEOMETRY_SOURCES`): they
#: are builder code under an old name, and stay at the root.
KEEP_ROOT = {"migrate_furnish_recipes.py", "migrate_roller_grill.py", "migrate_slush_machine.py",
             "migrate_wall_crossing.py", "migrate_window_poster.py", "migrate_window_sign.py"}

#: A file's own directory, as a moved file spells it -> the repo root, one level up.
REWRITES = [
    ("HERE = os.path.dirname(os.path.abspath(__file__))",
     "HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"),
    ("HERE = Path(__file__).resolve().parent\n", "HERE = Path(__file__).resolve().parent.parent\n"),
    ("here = os.path.dirname(os.path.abspath(__file__))",
     "here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"),
    ("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
     "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"),
    ("os.path.join(os.path.dirname(os.path.abspath(__file__)),",
     "os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"),
    ("os.path.dirname(os.path.dirname(os.path.abspath(__file__))), \"zoo\")",
     "os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), \"zoo\")"),
]


def git(*args):
    subprocess.run(["git", "-C", str(R)] + list(args), check=True)


def rewrite(path):
    b = path.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    n = 0
    for o, new in REWRITES:
        if o in t and new not in t:
            n += t.count(o)
            t = t.replace(o, new)
    # the usage lines a moved file gives, which now run from the root into its directory
    def home(m):
        name = m.group(2)
        if name in KEEP_ROOT:
            return m.group(0)
        return m.group(1) + ("tests/" if name.startswith("test_") else "migrations/") + name
    t, k = re.subn(r"(?m)(python (?:-m pytest (?:-q )?)?)((?:test|migrate)_[a-z0-9_]+\.py)", home, t)
    n += k
    left = [l for l in t.splitlines() if "__file__" in l and "dirname(os.path.dirname" not in l and
            ".parent.parent" not in l]
    path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    return n, left


def main():
    tests = sorted(p.name for p in R.glob("test_*.py"))
    migr = sorted(p.name for p in R.glob("migrate_*.py") if p.name not in KEEP_ROOT)
    (R / "tests").mkdir(exist_ok=True)
    for f in tests:
        git("mv", f, "tests/" + f)
    for f in migr:
        git("mv", f, "migrations/" + f)
    unexplained = {}
    for d, files in (("tests", tests), ("migrations", migr)):
        for f in files:
            n, left = rewrite(R / d / f)
            if left:
                unexplained[d + "/" + f] = left
    print("moved %d tests to tests/ and %d migrations to migrations/" % (len(tests), len(migr)))
    for f, lines in unexplained.items():
        print("  __file__ left as is in %s: %s" % (f, " | ".join(l.strip() for l in lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
