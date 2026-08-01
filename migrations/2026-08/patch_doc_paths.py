"""Three documented commands, and one printed one, learn where the tools moved.

FOUND BY THE MOVE'S OWN GUARD, which separates an invocation from a mention:

    CLAUDE.md:204        python gdcheck.py navmesh_solid_probe.gd
    docs/CLEANUP.md:29   powershell ... -File factory_clean.ps1
    docs/CLEANUP.md:32   powershell ... -File factory_clean.ps1 -Apply

Each runs a file by path, so each sends a reader to somewhere that will not
exist after the move. The nineteen prose mentions in the same four files go
stale rather than broken and are left alone here -- fixing a sentence is a
documentation pass, fixing a command is a prerequisite.

AND ONE THE GUARD COULD NOT SEE. check_all.py's NOT_RUN block prints

    walk sweep   python library_walk.py --timeout 1800

The guard skips pairs where both files move, correctly -- nothing breaks,
check_all still finds its siblings. But that string is printed to a person
standing at the factory root, and after the move `python library_walk.py` finds
nothing there. A tool whose own output tells you to run a command that fails is
the small end of the same defect this whole pass has been chasing.

`python lot\\package.py` and `cd lot && python -m pytest` in the same block stay
correct -- lot/ is not moving.

Asserts every target, refuses on a miss, idempotent.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")

CLAUDE_OLD = """`gdcheck.py` at the factory root runs `gdparse` plus the traps a grammar cannot
see. Run it on every `.gd` before pushing to a machine that will load it:

    pip install gdtoolkit
    python gdcheck.py navmesh_solid_probe.gd
"""

CLAUDE_NEW = """`tools/gdcheck.py` runs `gdparse` plus the traps a grammar cannot see. Run it on
every `.gd` before pushing to a machine that will load it:

    pip install gdtoolkit
    python tools\\gdcheck.py tools\\navmesh_solid_probe.gd
"""

CLEANUP_OLD = "-File factory_clean.ps1"
CLEANUP_NEW = "-File scripts\\factory_clean.ps1"

CA_OLD = '''    ("walk sweep", "python library_walk.py --timeout 1800",
'''
CA_NEW = '''    ("walk sweep", "python tools\\\\library_walk.py --timeout 1800",
'''


def main() -> int:
    claude = ROOT / "CLAUDE.md"
    cleanup = ROOT / "docs" / "CLEANUP.md"
    ca = ROOT / "check_all.py"
    if not ca.exists():
        ca = ROOT / "tools" / "check_all.py"

    for p in (claude, cleanup, ca):
        if not p.exists():
            raise SystemExit(f"missing {p}. NOTHING WRITTEN.")

    plan, done, already = [], [], []

    src = claude.read_text(encoding="utf-8")
    if "tools\\gdcheck.py" in src:
        already.append("CLAUDE.md")
    else:
        n = src.count(CLAUDE_OLD)
        if n != 1:
            raise SystemExit(f"CLAUDE.md: the gdcheck block appears {n} time(s), "
                             f"expected 1. NOTHING WRITTEN.")
        plan.append((claude, src.replace(CLAUDE_OLD, CLAUDE_NEW), "CLAUDE.md"))

    src = cleanup.read_text(encoding="utf-8")
    if CLEANUP_NEW in src:
        already.append("docs/CLEANUP.md")
    else:
        n = src.count(CLEANUP_OLD)
        if n != 2:
            raise SystemExit(f"docs/CLEANUP.md: `{CLEANUP_OLD}` appears {n} "
                             f"time(s), expected 2. NOTHING WRITTEN.")
        # Replacing the shared prefix handles both lines; the ` -Apply` on the
        # second sits outside the match, so it survives untouched.
        plan.append((cleanup, src.replace(CLEANUP_OLD, CLEANUP_NEW),
                     "docs/CLEANUP.md"))

    src = ca.read_text(encoding="utf-8")
    if "tools\\\\library_walk.py" in src:
        already.append(ca.name)
    else:
        n = src.count(CA_OLD)
        if n != 1:
            raise SystemExit(f"{ca}: the walk-sweep line appears {n} time(s), "
                             f"expected 1. NOTHING WRITTEN.")
        plan.append((ca, src.replace(CA_OLD, CA_NEW), str(ca.relative_to(ROOT))))

    for p, text, label in plan:
        backup = p.with_suffix(p.suffix + ".pre_docpaths")
        if not backup.exists():
            shutil.copy2(p, backup)
        p.write_text(text, encoding="utf-8")
        if p.suffix == ".py":
            py_compile.compile(str(p), doraise=True)
        done.append(label)

    for n in already:
        print(f"  {n}: already points at the new location")
    for n in done:
        print(f"  {n}: command updated")
    print("\n  Nineteen prose mentions across CLAUDE.md, docs/CLEANUP.md,")
    print("  GUARDRAILS_PLAN.md and PIPELINE_ROADMAP.md are untouched. They name")
    print("  the tools in sentences rather than running them -- stale, not broken.")
    print("\n  The move should now report no invocations, and go through without "
          "-Force:\n")
    print("    .\\tidy_tools.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
