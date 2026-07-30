"""Stop gdcheck.py depending on a PATH entry that pip warns it did not create.

MEASURED. `pip install gdtoolkit` succeeded and gdcheck.py still died:

    FileNotFoundError: [WinError 2] The system cannot find the file specified

because gdcheck.py runs

    subprocess.run(["gdparse", path], ...)

and pip had said, in the same output:

    WARNING: The scripts gd2py.exe, gdformat.exe, gdlint.exe, gdparse.exe and
    gdradon.exe are installed in '...\\pythoncore-3.14-64\\Scripts' which is not
    on PATH.

So the module is importable and the console shim is unreachable. Depending on a
console script means depending on a PATH entry that the install itself warns it
did not make -- and CLAUDE.md tells the reader to run this tool before any .gd
leaves the machine, so the instruction was unfollowable on a clean install.

TWO FIXES.

1. Invoke the module, not the shim: [sys.executable, "-m", "gdtoolkit.parser"].
   That resolves through the same interpreter running gdcheck, so it cannot
   disagree with it about which environment is in play, and PATH is irrelevant.
   Verified to give exit 0 on a valid file and 1 with the offending line on an
   invalid one, which is what the existing return-code check already expects.

2. Say what is wrong instead of raising. A missing checker made the patch that
   invoked it look like the thing that had broken -- a 40-line traceback in the
   middle of an otherwise clean run. gdcheck now reports that the parser is
   unavailable, names the install command, and returns 2 for "could not check",
   distinct from 1 for "checked and found problems". The hand-written trap lint
   still runs, because two of the three traps do not need a parser and a partial
   check beats none.

Asserts its target, refuses on a miss, idempotent, and demonstrates itself
against a deliberately broken file.
"""
import pathlib
import py_compile
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
GDCHECK = ROOT / "gdcheck.py"

OLD = '''    bad = 0
    for path in argv:
        problems = []
        r = subprocess.run(["gdparse", path], capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            problems.append((0, "gdparse: " + (tail[-1] if tail else "rejected")))
        problems += lint(path)
'''

NEW = '''    # Is the parser usable AT ALL? Asked once, before any file, because
    # "the parser is missing" and "this file is bad" are different answers and
    # inferring the first from a failed parse of the second gets it wrong. The
    # earlier version keyed on "No module named" appearing in stderr, which a
    # parser broken any other way does not say -- and it then reported the
    # breakage as a defect in the file being checked.
    parser_ok = False
    parser_why = ""
    try:
        probe = subprocess.run(
            [sys.executable, "-c", "import gdtoolkit.parser"],
            capture_output=True, text=True)
        parser_ok = probe.returncode == 0
        if not parser_ok:
            tail = (probe.stderr or "").strip().splitlines()
            parser_why = tail[-1] if tail else "import failed"
    except OSError as e:
        parser_why = f"{type(e).__name__}: {e}"
    if not parser_ok:
        print("THE GDSCRIPT GRAMMAR CHECK IS NOT RUNNING.")
        print(f"  {parser_why}")
        print(f"  install it with: {sys.executable} -m pip install gdtoolkit")
        print("  The hand-written trap checks below still run, but a file that "
              "passes\\n  only those has not been parsed. Do not read it as "
              "clean.\\n")

    bad = 0
    for path in argv:
        problems = []
        # Invoke the MODULE, not the `gdparse` console script. pip installs that
        # shim into a Scripts directory it warns may not be on PATH, and on a
        # clean install it was not -- so this raised FileNotFoundError with
        # gdtoolkit correctly installed, and the traceback made whatever ran
        # gdcheck look like the thing that was broken. Going through
        # sys.executable also guarantees the parser comes from the same
        # interpreter as this script rather than whichever one PATH finds first.
        if parser_ok:
            r = subprocess.run(
                [sys.executable, "-m", "gdtoolkit.parser", path],
                capture_output=True, text=True)
            if r.returncode != 0:
                tail = (r.stderr or r.stdout or "").strip().splitlines()
                problems.append((0, "gdparse: "
                                 + (tail[-1] if tail else "rejected")))
        problems += lint(path)
'''

TAIL_OLD = '''        else:
            print(f"{path}: parses, and none of the three known traps")
    return 1 if bad else 0
'''

TAIL_NEW = '''        elif parser_ok:
            print(f"{path}: parses, and none of the three known traps")
        else:
            print(f"{path}: none of the three known traps -- NOT PARSED")
    # 1 = checked and found problems. 2 = could not fully check. Distinct,
    # because a checker that could not run must not report what a clean file
    # reports.
    if bad:
        return 1
    return 0 if parser_ok else 2
'''


def main() -> int:
    if not GDCHECK.exists():
        raise SystemExit(f"missing {GDCHECK}. Nothing written.")
    src = GDCHECK.read_text(encoding="utf-8")
    if '"-m", "gdtoolkit.parser"' in src:
        print("gdcheck.py: already invokes the parser module")
    else:
        for label, old in (("the gdparse call", OLD), ("the return", TAIL_OLD)):
            if src.count(old) != 1:
                raise SystemExit(
                    f"gdcheck.py: {label} appears {src.count(old)} time(s), "
                    f"expected exactly 1. Read the file rather than forcing "
                    f"this. NOTHING WRITTEN.")
        src = src.replace(OLD, NEW).replace(TAIL_OLD, TAIL_NEW)
        backup = GDCHECK.with_suffix(".py.pre_invoke")
        if not backup.exists():
            shutil.copy2(GDCHECK, backup)
        GDCHECK.write_text(src, encoding="utf-8")
        py_compile.compile(str(GDCHECK), doraise=True)
        print("gdcheck.py: parser invoked as a module, missing parser reported "
              "not raised")
        print(f"gdcheck.py: compiles; previous file kept at {backup.name}")

    # demonstrate it: a real file, then a deliberately broken one
    real = ROOT / "lot" / "godot" / "addons" / "lot" / "lot_player.gd"
    print("\n=========== on the shipped player ===========")
    r = subprocess.run([sys.executable, str(GDCHECK), str(real)],
                       capture_output=True, text=True, cwd=str(ROOT))
    print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-600:])
    print(f"  exit {r.returncode}   (0 clean, 1 problems, 2 could not check)")

    with tempfile.TemporaryDirectory() as d:
        broken = pathlib.Path(d) / "broken.gd"
        broken.write_text('func f(\n\tvar s := "a" "b"\n', encoding="utf-8")
        print("\n=========== on a deliberately broken file ===========")
        r2 = subprocess.run([sys.executable, str(GDCHECK), str(broken)],
                            capture_output=True, text=True, cwd=str(ROOT))
        print((r2.stdout or "").rstrip() or (r2.stderr or "").rstrip()[-600:])
        print(f"  exit {r2.returncode}   (must be 1 -- a checker that cannot "
              f"fail is not a check)")
        if r2.returncode != 1:
            print("  WARNING: the broken file was not rejected. Do not trust "
                  "the clean result above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
