"""Phase 1 step 3: a major gate finding fails the site.

The gates stop being advisory here. Everything before this was building the case
that the threshold is right, and the case is now measured rather than argued:

    reporting-only sweep, blocking at major     1 finding, 1 site, 20 of 20 pass
    reporting-only sweep, blocking at moderate  ~35 findings, 19 of 20 sites

The second is what this patch would have done if written a step earlier, and it
would have been switched off within a day. The first is a gate a person believes.

WHAT CHANGES. A site whose blocking count is non-zero reports `blocked` instead of
`pass` and is counted as a regression. Exactly one site does today: ref_pvp, whose
objective marker stands 3.60 m above the ground plane and reports 0% traversal --
measured, on the open list, and genuinely a level that does not work.

THE LIBRARY GOES 20/20 -> 19/20, and stays there until that objective is fixed.
That is the intended behaviour and it is worth saying plainly: anything that
expects a green twenty will now see red, and the correct response is to fix the
site rather than the gate.

WHY `blocked` AND NOT `fail`. The `now` column already carries the walktest's own
verdicts -- TIMEOUT, NO REPORT, ASSEMBLE FAILED, SPEC MISSING. Those say the
measurement did not complete. `blocked` says the measurement completed and the
level is broken anyway, which is a different fact and the whole reason this column
was worth adding. A reader can tell at a glance whether to look at the harness or
at the level.

WHAT STILL DOES NOT BLOCK. Moderate, minor and info, for the reasons recorded on
BLOCKING_RANK. And a site whose contract could not be read shows `?` -- it is
neither clean nor blocked, because a check that did not run must not report what a
clean run reports. It is counted as a regression too: unchecked is not passed.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LW = ROOT / "library_walk.py"

VERDICT_OLD = '''        now = "pass" if s["ok"] is True else str(s["ok"])
        legs = f"{s['legs'] - s['failed']}/{s['legs']}"
        _g = s.get("gates")
        _major = ("?" if _g is None else
                  sum(1 for _c, _sev, _m in _g
                      if SEVERITY_RANK.get(_sev, BLOCKING_RANK) >= BLOCKING_RANK))
        print(f"{name:<22} {was:<12} {now:<14} {s['anchors']:>7} "
              f"{s['stranded']:>6} {s['no_floor']:>7} {s['barrier']:>7} "
              f"{legs:>9} {s['stuck']:>5} {(_major or ''):>7}")
        (clean if s["ok"] is True else regressions).append(name)
'''

VERDICT_NEW = '''        legs = f"{s['legs'] - s['failed']}/{s['legs']}"
        _g = s.get("gates")
        _major = ("?" if _g is None else
                  sum(1 for _c, _sev, _m in _g
                      if SEVERITY_RANK.get(_sev, BLOCKING_RANK) >= BLOCKING_RANK))
        # The walkers finishing is necessary and not sufficient. `now` carries
        # the walktest's own verdicts -- TIMEOUT, NO REPORT, ASSEMBLE FAILED --
        # and those all mean the measurement did not complete. `blocked` means it
        # DID complete and the level is broken anyway, which is a different fact
        # and the reason the gates column was worth adding. A `?` means the
        # contract could not be read: neither clean nor blocked, and not passed,
        # because a check that did not run must not report what a clean run
        # reports.
        _walked = s["ok"] is True
        if not _walked:
            now = str(s["ok"])
        elif _major == "?":
            now = "unchecked"
        elif _major:
            now = "blocked"
        else:
            now = "pass"
        print(f"{name:<22} {was:<12} {now:<14} {s['anchors']:>7} "
              f"{s['stranded']:>6} {s['no_floor']:>7} {s['barrier']:>7} "
              f"{legs:>9} {s['stuck']:>5} {(_major or ''):>7}")
        (clean if now == "pass" else regressions).append(name)
'''

FOOT_OLD = '''    print(f"{len(clean)} of {len(results)} come back ok; "
          f"{time.time() - t_all:.0f}s total")
'''

FOOT_NEW = '''    print(f"{len(clean)} of {len(results)} come back ok; "
          f"{time.time() - t_all:.0f}s total")
    _blocked_sites = [n for n, _m, _w, s in results
                      if s["ok"] is True and s.get("gates")
                      and any(SEVERITY_RANK.get(sev, BLOCKING_RANK)
                              >= BLOCKING_RANK for _c, sev, _m2 in s["gates"])]
    if _blocked_sites:
        print(f"{len(_blocked_sites)} walked clean and are BLOCKED by a gate: "
              f"{', '.join(_blocked_sites)}")
        print("  The walkers finished. The level is broken anyway -- see the "
              "major list below.")
'''

RETURN_OLD = '''    return 0 if not regressions else 1
'''

RETURN_NEW = '''    # Non-zero when anything did not come back clean, INCLUDING a site the
    # walkers completed that a gate blocks. Before this, a blocked site exited 0
    # and every wrapper read that as success.
    return 0 if not regressions else 1
'''


def _swap(src, old, new, label, done):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. NOTHING WRITTEN.")
    done.append(label)
    return src.replace(old, new)


def main() -> int:
    if not LW.exists():
        raise SystemExit(f"missing {LW}. Nothing written.")
    src = LW.read_text(encoding="utf-8")
    if '_walked = s["ok"] is True' in src:
        print("library_walk.py: gates already bind the verdict")
        return 0
    if "BLOCKING_RANK" not in src:
        raise SystemExit("library_walk.py has no BLOCKING_RANK -- run "
                         "patch_gate_threshold.py first. NOTHING WRITTEN.")
    done = []
    src = _swap(src, VERDICT_OLD, VERDICT_NEW,
                "library_walk.py: a major finding makes the site `blocked`", done)
    src = _swap(src, FOOT_OLD, FOOT_NEW,
                "library_walk.py: blocked sites named under the count", done)
    if RETURN_OLD in src:
        src = _swap(src, RETURN_OLD, RETURN_NEW,
                    "library_walk.py: the return comment", done)
    else:
        done.append("library_walk.py: no `return 0 if not regressions` to "
                    "annotate -- check the exit code by hand")

    backup = LW.with_suffix(".py.pre_bind")
    if not backup.exists():
        shutil.copy2(LW, backup)
    LW.write_text(src, encoding="utf-8")
    py_compile.compile(str(LW), doraise=True)
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  THE GATES NOW BIND. Expect 19 of 20, with ref_pvp reading "
          "`blocked` --\n  it walked clean and its objective is 3.60 m off the "
          "floor at 0% traversal.\n  That is the gate working. Fix the site, not "
          "the gate.\n")
    print("    python library_walk.py --timeout 1800")
    print("\n  If anything OTHER than ref_pvp reads `blocked`, stop and read its "
          "finding\n  before touching either -- that is a site whose defect was "
          "never measured,\n  or a gate that is wrong about it, and the two look "
          "identical from here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
