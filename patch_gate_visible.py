"""Make the step gate's output survive library_walk's filter.

The gate is wired and running. It reported nothing, and neither did its failure
branch -- which is the tell, because a site that reported three findings when
site_steps.py was run standalone cannot suddenly have none.

library_walk.py forwards a build's output through

    if line.startswith("[lot]"):
        print("  " + line)

The two-space indent seen in the console is added THERE. lot.py's own prints
start at column zero. The gate I wrote printed

    f"  [lot] {code}: {message}"

copying the indentation from the console rather than from the file, so
startswith("[lot]") was false and every line the gate produced was dropped --
the findings AND the "STEP GATE DID NOT RUN" notice that exists precisely so a
dead check cannot pass for a quiet one.

That is the fourth silenced-output defect in this pass: Write-Host not being
pipeable, git's stderr sent to $null while a checkout failed, walktest's inner
timeout hidden behind an outer one, and now this. Same shape as the rest --
a cheap proxy for "did it work" (the absence of complaint) standing in for the
expensive truth (whether anything ran).

Asserts its target before writing, and is idempotent.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"

OLD = '''        for _i in result_steps:
            print(f"  [lot] {_i['code']}: {_i['message']}")
    except Exception as _e:
        print(f"  [lot] STEP GATE DID NOT RUN ({type(_e).__name__}: {_e}) -- "
              f"a silent check is not a passing one")
'''

NEW = '''        for _i in result_steps:
            # Column zero, and the prefix library_walk.py filters on. Its
            # forwarder does `if line.startswith("[lot]")` and adds the indent
            # itself, so a leading space here means the line is dropped -- which
            # silently hid this gate's first live run, findings and failures
            # alike.
            print(f"[lot] {_i['code']}: {_i['message']}")
    except Exception as _e:
        print(f"[lot] STEP GATE DID NOT RUN ({type(_e).__name__}: {_e}) -- "
              f"a silent check is not a passing one")
'''


def main() -> int:
    src = LOT_PY.read_text(encoding="utf-8")
    if 'print(f"[lot] {_i[\'code\']}' in src:
        print("lot.py: gate output already unindented")
        return 0
    if src.count(OLD) != 1:
        raise SystemExit(
            f"lot.py: the gate's print block appears {src.count(OLD)} time(s), "
            f"expected exactly 1. Run patch_player_and_gate.py first, or read "
            f"the file. Nothing written.")
    backup = LOT_PY.with_suffix(".py.pre_visible")
    if not backup.exists():
        shutil.copy2(LOT_PY, backup)
    LOT_PY.write_text(src.replace(OLD, NEW), encoding="utf-8")
    py_compile.compile(str(LOT_PY), doraise=True)
    print("lot.py: gate prints at column zero, so library_walk forwards them")
    print(f"lot.py: compiles; previous file kept at {backup.name}")
    print("\n  every [lot] line lot.py emits, checked for the same mistake:")
    bad = [n for n, l in enumerate(LOT_PY.read_text(encoding="utf-8").splitlines(), 1)
           if "[lot]" in l and "print(" in l and 'f"  [lot]' in l]
    if bad:
        print(f"    still indented at line(s): {bad}")
    else:
        print("    none indented -- all of them will survive the filter")
    print("\n  rebuild and expect the gate to speak:")
    print("    python library_walk.py --only ballpark_block --timeout 1800")
    print("  ballpark_block reported 3 findings standalone (two kerb sections")
    print("  off-route, one courtyard edge at 0.12 against a 0.1025 limit), so")
    print("  seeing zero again would mean the gate still is not running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
