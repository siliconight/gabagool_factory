"""Make the walktest timeout reachable from outside walktest.py.

MEASURED. central_vault came back NO REPORT from the library sweep. It is not a
level defect and it is not a crash:

    [walktest] central_vault_navqa.tscn: TIMEOUT after 300s

All 36 path proofs pass -- 18 home->proxy and 18 proxy->proxy, longest 210.0 m.
2406 polygons in the bake, up from ~870 before cell_size dropped to 0.10. The
site is fully connected. Godot was killed before the walker phase could write
its report, so `read()` found no file and the summary said NO REPORT.

WHY THE OBVIOUS KNOB DID NOTHING. `library_walk.py --timeout` defaults to 1200
and bounds the OUTER subprocess -- the python that runs walktest.py. The number
that kills Godot is `run_one(..., timeout=300)` inside walktest.py, hardcoded,
with no CLI flag and nothing threading through to it. So passing --timeout 1200
to the sweep changed nothing about the 300 that mattered.

That is the third time in one investigation that the configurable constant was
not the one doing the work: DC_QA_ARRIVE (1.5) against a hardcoded 0.6 waypoint
consume radius, and library_walk --timeout against this. Worth naming as a shape
rather than three coincidences -- a knob that looks responsible and is not costs
a full measurement cycle every time, because the null result reads as "theory
refuted" instead of "wrong dial".

WHY 300 IS NOW TOO SMALL. It is a wall-clock bound on a simulation whose length
scales with the site. central_vault's spine is ~1352 m against a 600 s sim cap,
on a navmesh with 2.25x the polygons it had this morning. warehouse_district
(651 m spine) finishes in 246 s; central_vault does not finish in 300.

THE CHANGE. Add --timeout to walktest.py, keep 300 as the default so nothing
else moves, and have library_walk.py pass its own --timeout through instead of
only using it for the outer bound. The outer value stays what it always was;
it just now reaches the process it was supposed to govern.

Asserts every target before writing, and is idempotent.
"""
import pathlib
import py_compile

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
WT = ROOT / "lot" / "walktest.py"
LW = ROOT / "library_walk.py"

WT_OLD_ARG = '''    ap.add_argument("--report-dir", default=None,
                    help="also copy each written report into this directory")
'''

WT_NEW_ARG = '''    ap.add_argument("--report-dir", default=None,
                    help="also copy each written report into this directory")
    # A wall-clock bound on a simulation whose length scales with the site.
    # This was hardcoded at 300 in run_one, which is fine for a 651 m spine and
    # kills a 1352 m one before it can write a report -- and library_walk's own
    # --timeout bounded only the python wrapper, so raising it did nothing.
    ap.add_argument("--timeout", type=int, default=300,
                    help="seconds of WALL CLOCK per scene before Godot is "
                         "killed (default 300; a long spine on a dense "
                         "navmesh needs more)")
'''

WT_OLD_CALL = '''        if not run_one(godot, args.project, scene,
                       report_dir=args.report_dir):
'''

WT_NEW_CALL = '''        if not run_one(godot, args.project, scene,
                       timeout=args.timeout,
                       report_dir=args.report_dir):
'''

LW_OLD = '''    r = subprocess.run([sys.executable, os.path.join(LOT, "walktest.py"), proj,
                        scene, "--require", "--report-dir", proj],
                       capture_output=True, text=True, cwd=LOT, timeout=timeout,
                       env=env)
'''

LW_NEW = '''    # --timeout goes to BOTH: the inner one is what actually kills Godot, and
    # for a long time only the outer one existed, so raising the sweep's timeout
    # left the real 300 s bound untouched and long sites reported NO REPORT.
    # The outer bound is given slack so the inner one reports a clean TIMEOUT
    # rather than being cut off mid-write.
    r = subprocess.run([sys.executable, os.path.join(LOT, "walktest.py"), proj,
                        scene, "--require", "--report-dir", proj,
                        "--timeout", str(timeout)],
                       capture_output=True, text=True, cwd=LOT,
                       timeout=timeout + 120, env=env)
'''


def main() -> int:
    wt = WT.read_text(encoding="utf-8")
    if '"--timeout"' in wt:
        print("walktest.py: already has --timeout")
    else:
        for label, block in (("the --report-dir argument", WT_OLD_ARG),
                             ("the run_one call", WT_OLD_CALL)):
            if wt.count(block) != 1:
                raise SystemExit(
                    f"walktest.py: {label} appears {wt.count(block)} time(s), "
                    f"expected exactly 1. Nothing written.")
        wt = wt.replace(WT_OLD_ARG, WT_NEW_ARG).replace(WT_OLD_CALL, WT_NEW_CALL)
        WT.write_text(wt, encoding="utf-8")
        py_compile.compile(str(WT), doraise=True)
        print("walktest.py: + --timeout (default 300), threaded into run_one")

    lw = LW.read_text(encoding="utf-8")
    if '"--timeout", str(timeout)' in lw:
        print("library_walk.py: already passes --timeout through")
    else:
        if lw.count(LW_OLD) != 1:
            raise SystemExit(
                f"library_walk.py: the walktest.py invocation appears "
                f"{lw.count(LW_OLD)} time(s), expected exactly 1. Nothing "
                f"written.")
        lw = lw.replace(LW_OLD, LW_NEW)
        LW.write_text(lw, encoding="utf-8")
        py_compile.compile(str(LW), doraise=True)
        print("library_walk.py: --timeout now reaches the process it governs")

    print("\n  what each site needed, wall clock, on the dense bake:")
    for site, spine, took in (("warehouse_district", 651, "246 s  finished"),
                              ("walkup_siege", 388, "101 s  finished"),
                              ("central_vault", 1352, "killed at 300 s")):
        print(f"    {site:<20} spine ~{spine:>4} m   {took}")
    print("\n  central_vault alone:")
    print("    cd lot")
    print("    python walktest.py ..\\_runs\\central_vault_proj "
          "central_vault_navqa.tscn `")
    print("      --require --report-dir ..\\_runs\\central_vault_proj "
          "--timeout 1800")
    print("\n  or the whole library, which is what the sweep should use now:")
    print("    python library_walk.py --timeout 1800")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
