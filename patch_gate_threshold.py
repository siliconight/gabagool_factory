"""Blocking is `major`. Moderate is advice, and advice does not fail a build.

MY ERROR, caught by running it. When phase 2 replaced the hardcoded severity map
with the emitters' own values, I set the blocking threshold at rank >= 2 -- major
AND moderate. That conflated "moderate now exists as a level" with "moderate
should block a release". The emitters never said that.

WHAT THE SWEEP SHOWED. At rank >= 2, LOT_GROUND_EXTENDED and LOT_ROUTE_EXPOSED
appear on nearly every site and the blocking list runs to ~35 entries across
almost the whole library. Read what they say:

    LOT_GROUND_EXTENDED   "the declared 210 x 150 m ground plate does not cover
                           the site it was built for; extended to 216 x 150 m so
                           <buildings> stand on ground"
    LOT_ROUTE_EXPOSED     "7 stretch(es) of the crew's route lie within 45 m of an
                           enemy spawn across open ground with nothing to hide
                           behind"

The first is Lot reporting a fix it already applied -- and site_extent.py:359 sets
it `moderate` for a deliberate reason recorded right there: the geometry is fine,
the SPEC is still wrong at the source and will stay wrong until someone edits it.
The second is a genuine tactical concern on a level that works.

Both are correct as designer advice. Neither means the build is broken. Severity
in these emitters answers "how much should a designer care", which is a different
axis from "should this fail a release", and no threshold on one can separate the
other.

THE CALIBRATION THE DATA SUPPORTS. At `major` only, the same sweep produced
exactly ONE finding across twenty sites -- ref_pvp's objective at 3.60 m with 0%
traversal. That is a gate that gets believed. A gate that fails nineteen of twenty
sites gets switched off by the first person trying to ship, and then it is worse
than no gate at all.

The four codes the emitters call major are all "this level does not work":

    LOT_DESTINATION_ABOVE_FLOOR    an objective nothing can path to
    LOT_DESTINATION_ON_PROP        an objective standing on furniture
    LOT_ENEMY_SPAWN_IN_THE_OPEN    a spawn with no cover at all
    LOT_ENEMY_SPAWN_UNPLACEABLE    a spawn that could not be placed
    LOT_SHELL_NO_COLLISION         a building you walk through

MODERATE DOES NOT DISAPPEAR. It gets its own list, labelled as what it is. Hiding
it would trade one wrong threshold for a quieter one, and the whole point of this
pass is that a finding nobody sees is a finding nobody fixes.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LW = ROOT / "library_walk.py"

RANK_OLD = '''#: Severities the emitters actually use. Not a classification -- only an ordering,
#: so the report can rank and the verdict can eventually threshold. A severity not
#: listed here is surfaced as-is rather than assumed harmless.
SEVERITY_RANK = {"major": 3, "moderate": 2, "minor": 1, "info": 0}
'''

RANK_NEW = '''#: Severities the emitters actually use. Not a classification -- only an ordering,
#: so the report can rank and the verdict can eventually threshold. A severity not
#: listed here is surfaced as-is rather than assumed harmless.
SEVERITY_RANK = {"major": 3, "moderate": 2, "minor": 1, "info": 0}

#: What BLOCKS. `major` only, and that is a deliberate calibration rather than a
#: default: at moderate-and-above the same sweep listed ~35 findings across
#: nineteen of twenty sites, because LOT_GROUND_EXTENDED and LOT_ROUTE_EXPOSED are
#: moderate on almost every site. Both are correct as designer advice --
#: site_extent.py:359 rates the first moderate precisely because the geometry was
#: fixed while the SPEC stays wrong -- and neither means the level is broken.
#:
#: Severity here answers "how much should a designer care". Whether a build should
#: fail is a different axis, and no threshold on the first can stand in for the
#: second. At `major` the same run produced exactly ONE finding in twenty sites,
#: and every major code is "this level does not work": an objective nothing can
#: path to, an objective on furniture, an unplaceable spawn, a spawn with no
#: cover, a building you walk through.
#:
#: A gate that fails nineteen of twenty sites gets switched off by the first
#: person trying to ship, and is then worse than no gate.
BLOCKING_RANK = 3
'''

ROW_OLD = '''        _g = s.get("gates")
        _major = ("?" if _g is None else
                  sum(1 for _c, _sev, _m in _g
                      if SEVERITY_RANK.get(_sev, 3) >= 2))
'''

ROW_NEW = '''        _g = s.get("gates")
        _major = ("?" if _g is None else
                  sum(1 for _c, _sev, _m in _g
                      if SEVERITY_RANK.get(_sev, BLOCKING_RANK) >= BLOCKING_RANK))
'''

TAIL_OLD = '''    _blocking, _unclassified, _minor = [], [], 0
    for name, _mid, _was, s in results:
        _g = s.get("gates")
        if _g is None:
            # The contract could not be read. Not clean -- unchecked.
            _unclassified.append((name, "CONTRACT UNREADABLE",
                                  "no <site>.site.gameplay.json to read "
                                  "findings from"))
            continue
        for code, sev, msg in _g:
            rank = SEVERITY_RANK.get(sev)
            if rank is None:
                _unclassified.append((name, code, f"severity {sev!r}: {msg}"))
            elif rank >= 2:
                _blocking.append((name, code, msg))
            else:
                _minor += 1
'''

TAIL_NEW = '''    _blocking, _advice, _unclassified, _minor = [], [], [], 0
    for name, _mid, _was, s in results:
        _g = s.get("gates")
        if _g is None:
            # The contract could not be read. Not clean -- unchecked.
            _unclassified.append((name, "CONTRACT UNREADABLE",
                                  "no <site>.site.gameplay.json to read "
                                  "findings from"))
            continue
        for code, sev, msg in _g:
            rank = SEVERITY_RANK.get(sev)
            if rank is None:
                _unclassified.append((name, code, f"severity {sev!r}: {msg}"))
            elif rank >= BLOCKING_RANK:
                _blocking.append((name, code, msg))
            elif rank == 2:
                # Advice, not a blocker. Listed on its own rather than hidden:
                # a finding nobody sees is a finding nobody fixes, and folding
                # these into the minor count would trade one wrong threshold for
                # a quieter one.
                _advice.append((name, code, msg))
            else:
                _minor += 1
'''

REPORT_OLD = '''    else:
        print("No major gate findings.")
'''

REPORT_NEW = '''    else:
        print("No major gate findings.")
    if _advice:
        _sites = len({n for n, _c, _m in _advice})
        print(f"\\n{len(_advice)} moderate finding(s) on {_sites} site(s) -- "
              f"designer advice, NOT blockers.\\nThe level works; the spec or the "
              f"tactical layout wants attention:")
        _by_code = {}
        for name, code, _m in _advice:
            _by_code.setdefault(code, []).append(name)
        for code, names in sorted(_by_code.items()):
            _shown = ", ".join(sorted(names)[:6])
            _more = f" +{len(names) - 6} more" if len(names) > 6 else ""
            print(f"  {code:<32}{len(names):>3} site(s): {_shown}{_more}")
'''

FOOT_OLD = '''    print(f"\\n{_minor} minor/info finding(s) not listed. Severity comes from "
          f"the emitter that\\nraised each finding, not from this script -- "
          f"major and moderate are listed\\nabove, minor and info are counted "
          f"here, and `?` in the gates column means the\\ncontract could not be "
          f"read.")
'''

FOOT_NEW = '''    print(f"\\n{_minor} minor/info finding(s) not listed. Severity comes from "
          f"the emitter that\\nraised each finding, not from this script. Only "
          f"`major` counts in the gates\\ncolumn and only `major` will block "
          f"when the verdict starts depending on it;\\nmoderate is grouped above "
          f"as advice, minor and info are counted here, and `?`\\nmeans the "
          f"contract could not be read at all.")
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
    if "BLOCKING_RANK" in src:
        print("library_walk.py: blocking threshold already set to major")
        return 0
    if "SEVERITY_RANK" not in src:
        raise SystemExit("library_walk.py has no SEVERITY_RANK -- run "
                         "patch_findings_source.py first. NOTHING WRITTEN.")
    done = []
    src = _swap(src, RANK_OLD, RANK_NEW,
                "library_walk.py: BLOCKING_RANK, with the calibration recorded",
                done)
    src = _swap(src, ROW_OLD, ROW_NEW,
                "library_walk.py: the gates column counts major only", done)
    src = _swap(src, TAIL_OLD, TAIL_NEW,
                "library_walk.py: moderate split out from blocking", done)
    src = _swap(src, REPORT_OLD, REPORT_NEW,
                "library_walk.py: moderate listed as advice, grouped by code",
                done)
    src = _swap(src, FOOT_OLD, FOOT_NEW,
                "library_walk.py: the footer", done)

    backup = LW.with_suffix(".py.pre_threshold")
    if not backup.exists():
        shutil.copy2(LW, backup)
    LW.write_text(src, encoding="utf-8")
    py_compile.compile(str(LW), doraise=True)
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Expected on the next sweep: the gates column drops to ONE entry "
          "(ref_pvp),\n  a moderate block appears grouped by code rather than "
          "site by site, and the\n  minor/info count goes back up.\n")
    print("    python library_walk.py --timeout 1800")
    print("\n  If that holds, step 3 is one line -- fail a site whose blocking "
          "count is\n  non-zero -- and it would fail exactly one site, for a "
          "reason already\n  measured and already on the open list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
