"""The major list still says it does not affect the verdict. It does now.

    1 MAJOR gate finding(s) on 1 site(s). These do NOT affect the verdict above yet:

That sentence was true for exactly two sweeps -- it was written by
patch_sweep_gates.py to make the reporting-only stage unmistakable, and
patch_gates_bind.py made it false without touching it.

Small, and worth doing immediately. A message that contradicts the behaviour it
describes is how a reader learns to stop believing the output, and this whole pass
has been about output that could not be believed: a `pass` from a harness that did
not look at the gates, a check that went quiet and read as clean, a severity table
that disagreed with the emitters. Leaving a stale sentence in the one report that
now decides pass or fail would undo a fair amount of that.

Asserts its target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LW = ROOT / "library_walk.py"

OLD = '''        print(f"{len(_blocking)} MAJOR gate finding(s) on "
              f"{len({n for n, _c, _m in _blocking})} site(s). These do NOT "
              f"affect the verdict above yet:")
'''

NEW = '''        print(f"{len(_blocking)} MAJOR gate finding(s) on "
              f"{len({n for n, _c, _m in _blocking})} site(s). Each one makes "
              f"its site `blocked` above,\\nwhatever the walkers reported:")
'''


def main() -> int:
    if not LW.exists():
        raise SystemExit(f"missing {LW}. Nothing written.")
    src = LW.read_text(encoding="utf-8")
    if "makes \" \n" in src or "`blocked` above" in src:
        print("library_walk.py: the major list already describes what it does")
        return 0
    if '_walked = s["ok"] is True' not in src:
        raise SystemExit("library_walk.py does not bind gates yet -- run "
                         "patch_gates_bind.py first. NOTHING WRITTEN.")
    if src.count(OLD) != 1:
        raise SystemExit(f"library_walk.py: the major-list header appears "
                         f"{src.count(OLD)} time(s), expected exactly 1. "
                         f"NOTHING WRITTEN.")
    backup = LW.with_suffix(".py.pre_bindtext")
    if not backup.exists():
        shutil.copy2(LW, backup)
    LW.write_text(src.replace(OLD, NEW), encoding="utf-8")
    py_compile.compile(str(LW), doraise=True)
    print("  library_walk.py: the major list says it blocks, because it does")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  No behaviour change -- one sentence. No need to re-sweep for it; "
          "it will\n  read correctly on the next run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
