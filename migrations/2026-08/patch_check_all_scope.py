"""check_all's gdscript row never ran. Two defects, and they are not the same one.

MEASURED, not inferred. 446 .gd files in the tree, 70,029 characters of argv,
against a Windows command-line ceiling of 32,767. check_all.py:91 builds ONE
argv of [python, gdcheck.py] + every path and hands it to subprocess.run, so
CreateProcess refused and raised WinError 206 -- "the filename or extension is
too long". There is no long filename. There are 446 short ones. That message
names the wrong thing so precisely that it read as a missing file, and the row
printed NOT CHECKED next to three checks that were clean.

DEFECT 1, SCOPE. Of the 446, 342 are in rockay-ws:

    342  rockay-ws          77% of the run
     37  lux
     36  lasertag
      9  deli_counter
      9  lot
      5  level_factory
      3  patina
      2  pixelcoat
      2  zoo
      1  navmesh_solid_probe.gd

CLAUDE.md is explicit that rockay-ws is evidence -- read it, do not edit it. So
three quarters of this check was spending its time raising findings on files
nobody is allowed to act on, and a reader who followed one would be patching a
file that is not the file. That is the same shape as the *.pre_* backups that
went into history last night, and it wants the same answer: exclude by reason.

The two exclusion reasons are kept apart in SKIP_PARTS rather than merged into
one tuple of strings, because they would want different answers if either
changed. Generated output is skipped because a finding there points at a copy.
Evidence is skipped because it is not ours to fix. Someone adding a directory
needs to know which of those they are claiming.

DEFECT 2, THE UNBOUNDED ARGV, WHICH THE SCOPE FIX DOES NOT REPAIR. Dropping
rockay-ws leaves 104 files, roughly 16k of argv, comfortably under the ceiling
today. Stopping there would pin correctness to a file count nobody is watching,
and this repo has now been bitten three times by a constant that was right at
one setting and wrong at the next -- WP_RADIUS at one bake grid, the *.pre_*
suffix list, GATE_SEVERITY's missing level. So the invocation is batched against
a budget DERIVED from the ceiling, and the class of failure is gone rather than
postponed.

WORST WINS across batches, on the three-way convention check_all already
enforces: any batch that could not check makes the whole row "could not check",
any batch with findings makes it "found", and a clean batch never upgrades a
dirty one. A naive "last exit code" would have let a clean final batch report
success over an earlier failure, which is the exact defect check_all exists to
prevent at the top level.

WHAT THIS DOES NOT CHANGE. gdcheck.py spawns one gdtoolkit.parser subprocess per
file. That is correct for its documented use -- a handful of files before they
go to a machine that runs Godot -- and at 104 files it is slow rather than
wrong. Left alone deliberately; if it becomes the bottleneck it is a change to
gdcheck, not to the thing that calls it.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CA = ROOT / "check_all.py"

DOC_OLD = '''    gdscript     gdcheck.py           every .gd in the tree: grammar plus the
                                      three traps a grammar cannot see
'''

DOC_NEW = '''    gdscript     gdcheck.py           every .gd this repo owns: grammar plus
                                      the three traps a grammar cannot see.
                                      rockay-ws is skipped -- it is evidence
                                      rather than source, and it holds 342 of
                                      the tree's 446 .gd files
'''

FILES_OLD = '''def gd_files():
    """Every .gd in the tree, minus scratch and editor backups."""
    out = []
    for p in ROOT.rglob("*.gd"):
        s = str(p)
        if any(part in s for part in ("_bridge", "__pycache__", "_scratch_archive",
                                      os.sep + "dist" + os.sep,
                                      os.sep + "_runs" + os.sep, ".godot")):
            continue
        out.append(str(p))
    return sorted(out)
'''

FILES_NEW = '''#: Skipped, for two DIFFERENT reasons, kept apart because they would want
#: different answers if either changed:
#:
#:   generated  _bridge, __pycache__, _scratch_archive, dist, _runs, .godot.
#:              Build output and staging copies. A finding here points at a
#:              copy, and the next reader patches a file that is not the file.
#:   evidence   rockay-ws. A mission workspace -- CLAUDE.md says read it, do
#:              not edit it. It holds 342 of the tree's 446 .gd files, so
#:              including it spent three quarters of this check raising
#:              findings nobody is permitted to act on.
#:
#: Anyone adding an entry has to say which of the two they are claiming.
SKIP_GENERATED = ("_bridge", "__pycache__", "_scratch_archive",
                  os.sep + "dist" + os.sep, os.sep + "_runs" + os.sep, ".godot")
SKIP_EVIDENCE = (os.sep + "rockay-ws" + os.sep,)

#: Windows refuses a command line over 32767 characters, and CreateProcess then
#: raises WinError 206 -- "the filename or extension is too long". Measured at
#: 70,029 characters across 446 files, so the gdscript check never launched at
#: all and printed NOT CHECKED beside three checks that had run. The budget is
#: derived from the ceiling rather than chosen as a file count, because a count
#: that is right today goes wrong the next time paths lengthen or a repo joins.
ARGV_CEILING = 32767
ARGV_BUDGET = ARGV_CEILING - 768   # room for the interpreter path and quoting


def gd_files():
    """Every .gd this repo owns -- see SKIP_GENERATED and SKIP_EVIDENCE."""
    out = []
    for p in ROOT.rglob("*.gd"):
        s = str(p)
        if any(part in s for part in SKIP_GENERATED + SKIP_EVIDENCE):
            continue
        out.append(str(p))
    return sorted(out)


def batched(base, files):
    """`files` split so no single command line approaches ARGV_CEILING.

    Returns a list of file-lists to append to `base`, never empty, so a caller
    can loop over it unconditionally.
    """
    room = ARGV_BUDGET - sum(len(x) + 1 for x in base)
    groups, cur, used = [], [], 0
    for f in files:
        if cur and used + len(f) + 1 > room:
            groups.append(cur)
            cur, used = [], 0
        cur.append(f)
        used += len(f) + 1
    if cur:
        groups.append(cur)
    return groups or [[]]
'''

RUN_OLD = '''    argv = [sys.executable, str(path)]
    for a in args:
        if a == "@gd":
            files = gd_files()
            if not files:
                return "cannot", None, "no .gd files found to check"
            argv += files
        else:
            argv.append(a)
    try:
        r = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
    except OSError as e:
        return "cannot", None, f"{type(e).__name__}: {e}"
    out = (r.stdout or "") + (r.stderr or "")
    tail = [l.strip() for l in out.splitlines() if l.strip()]
    if r.returncode == 0:
        state = "ok"
    elif r.returncode == 2:
        state = "cannot"
    else:
        state = "found"
'''

RUN_NEW = '''    base = [sys.executable, str(path)]
    plain = [a for a in args if a != "@gd"]
    if "@gd" in args:
        files = gd_files()
        if not files:
            return "cannot", None, "no .gd files found to check"
        groups = batched(base + plain, files)
    else:
        groups = [[]]

    outs, codes = [], []
    for g in groups:
        try:
            r = subprocess.run(base + plain + g, capture_output=True,
                               text=True, cwd=str(ROOT))
        except OSError as e:
            return "cannot", None, f"{type(e).__name__}: {e}"
        outs.append((r.stdout or "") + (r.stderr or ""))
        codes.append(r.returncode)
    out = "".join(outs)
    tail = [l.strip() for l in out.splitlines() if l.strip()]
    # Worst wins. A batch that could not check makes the whole row "could not
    # check"; a batch with findings makes it "found"; and a clean batch never
    # upgrades a dirty one. Reading only the last exit code would let a clean
    # final batch report success over an earlier failure, which is precisely
    # the substitution this runner exists to stop at the top level.
    if 2 in codes:
        state, code = "cannot", 2
    elif any(c != 0 for c in codes):
        state, code = "found", next(c for c in codes if c != 0)
    else:
        state, code = "ok", 0
    if len(groups) > 1:
        tail.append(f"checked in {len(groups)} batches "
                    f"({sum(len(g) for g in groups)} files)")
'''

RET_OLD = '''    return state, r.returncode, (summary or (tail[-1] if tail else ""))
'''

RET_NEW = '''    return state, code, (summary or (tail[-1] if tail else ""))
'''

VERBOSE_OLD = '''        if args.verbose:
            print(f"\\n=========== {key} ===========")
            r = subprocess.run([sys.executable, str(ROOT / script)]
                               + ([] if argv != ["@gd"] else gd_files()),
                               cwd=str(ROOT))
'''

VERBOSE_NEW = '''        if args.verbose:
            print(f"\\n=========== {key} ===========")
            # Batched here too. This path had the same unbounded argv and would
            # have failed the same way, quietly, since its result was discarded.
            _base = [sys.executable, str(ROOT / script)]
            _groups = batched(_base, gd_files()) if argv == ["@gd"] else [[]]
            for _g in _groups:
                subprocess.run(_base + _g, cwd=str(ROOT))
'''


def _swap(src, old, new, label, done):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. NOTHING WRITTEN.")
    done.append(label)
    return src.replace(old, new)


def main() -> int:
    if not CA.exists():
        raise SystemExit(f"missing {CA}. Nothing written.")
    src = CA.read_text(encoding="utf-8")
    if "ARGV_CEILING" in src:
        print("check_all.py: already scoped and batched")
        return 0
    if "def gd_files():" not in src:
        raise SystemExit("check_all.py has no gd_files() -- this is not the "
                         "file this patch was written against. NOTHING WRITTEN.")
    done = []
    src = _swap(src, DOC_OLD, DOC_NEW,
                "check_all.py: the docstring says rockay-ws is skipped", done)
    src = _swap(src, FILES_OLD, FILES_NEW,
                "check_all.py: SKIP_GENERATED / SKIP_EVIDENCE, and batched()",
                done)
    src = _swap(src, RUN_OLD, RUN_NEW,
                "check_all.py: run() batches the invocation, worst code wins",
                done)
    src = _swap(src, RET_OLD, RET_NEW,
                "check_all.py: run() returns the combined code", done)
    src = _swap(src, VERBOSE_OLD, VERBOSE_NEW,
                "check_all.py: --verbose batches too", done)

    backup = CA.with_suffix(".py.pre_scope")
    if not backup.exists():
        shutil.copy2(CA, backup)
    CA.write_text(src, encoding="utf-8")
    py_compile.compile(str(CA), doraise=True)
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Expected next run: gdscript goes from NOT CHECKED to a real "
          "result over 104\n  files rather than 446. It will take a minute or "
          "two -- gdcheck spawns one\n  parser process per file, which is fine "
          "for its documented use and merely\n  slow here.\n")
    print("    python check_all.py")
    print("\n  If it reports FINDINGS, read them before assuming they are new. "
          "These 104\n  files have never actually been through this check, so "
          "anything it raises is\n  pre-existing rather than caused by tonight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
