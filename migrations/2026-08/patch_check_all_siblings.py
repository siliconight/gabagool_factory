"""check_all finds its checkers beside itself, not in the tree it checks.

MY OWN GAP, caught by writing the baseline down. patch_factory_root.py gave
check_all.py a SCRIPT_DIR and then never used it: run() still resolves each
checker as `ROOT / script`, and so does the --verbose path. While everything sat
at the factory root those were the same directory, which is exactly why the bug
was invisible -- the same coincidence the whole pass exists to break.

Move the checkers into tools/ without this and check_all looks for
<factory>/check_freshness.py, does not find it, and reports NOT CHECKED with
exit 2. Loud rather than silent, so it would not have lied. It would just have
been broken, on the commit whose entire purpose was to not break anything.

Two call sites, one idea: a checker is a SIBLING, the tree is the SUBJECT.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CA = ROOT / "check_all.py"

RUN_OLD = '''    path = ROOT / script
    if not path.exists():
        return "cannot", None, f"{script} is not at the factory root"
'''

RUN_NEW = '''    # SIBLING, not subject. ROOT is the tree being checked; the checkers live
    # beside this file. Identical answers until something moved.
    path = SCRIPT_DIR / script
    if not path.exists():
        return "cannot", None, (f"{script} is not beside check_all.py "
                                f"(looked in {SCRIPT_DIR})")
'''

VERB_OLD = '''            _base = [sys.executable, str(ROOT / script)]
'''

VERB_NEW = '''            _base = [sys.executable, str(SCRIPT_DIR / script)]
'''


def main() -> int:
    if not CA.exists():
        raise SystemExit(f"missing {CA}. Nothing written.")
    src = CA.read_text(encoding="utf-8")
    if "SCRIPT_DIR / script" in src:
        print("check_all.py: already resolves checkers as siblings")
        return 0
    if "SCRIPT_DIR" not in src:
        raise SystemExit("check_all.py has no SCRIPT_DIR -- run "
                         "patch_factory_root.py first. NOTHING WRITTEN.")
    done = []
    for old, new, label in ((RUN_OLD, RUN_NEW, "run() resolves the checker beside this file"),
                            (VERB_OLD, VERB_NEW, "--verbose does the same")):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: target appears {n} time(s), expected 1. "
                             f"NOTHING WRITTEN.")
        src = src.replace(old, new)
        done.append(label)

    backup = CA.with_suffix(".py.pre_siblings")
    if not backup.exists():
        shutil.copy2(CA, backup)
    CA.write_text(src, encoding="utf-8")
    py_compile.compile(str(CA), doraise=True)
    print("applied:")
    for d in done:
        print(f"  check_all.py: {d}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Still nothing moved, so this must STILL report four clean rows "
          "and 104\n  files. Same baseline, one more edit under it:\n")
    print("    python check_all.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
