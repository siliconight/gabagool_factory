r"""Is the lot drawing Level Factory's own output as a source archetype?

    python tools\probe_lot_own_output.py
    python tools\probe_lot_own_output.py --seed 5017 --count 1
    python tools\probe_lot_own_output.py --library <build_dir> --suspect shell site

Run from anywhere; the factory root is found by walking up for
`factory.manifest.json`.

ROADMAP ITEM 49, THE QUESTION THAT COMES FIRST

`unlit_probe_001` exported a package whose `site.tscn` reads

    [ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]

and whose `resource_manifest.json` lists `assets/lot.glb` and
`assets/shell.glb` at the SAME sha256, `a929d7d2...`, 242,176 bytes each. The
archetype the lot drew is called `shell`. Before anyone fixes the missing
`lot/shell/` directory, the question is whether that directory SHOULD exist --
because if `shell` is this pipeline's own generated shell, read back out of
`deli_counter/build` as though it were an authored archetype, then staging it
would ship the wrong thing correctly.

WHY source_exclusion CANNOT ANSWER IT TODAY

It catches exactly two things, and says so:

    ids beginning "lf_"           Level Factory's own composed output
    validation.json facade=true   Deli Counter's own word for a street wall

A file called `shell.glb` starts with neither. It is not prefixed, and Deli
Counter would not call it a facade. If it is in that directory with its
`.gameplay.json` and `.slots.json` beside it, `index` reports it complete and
`pick_lot` may draw it.

WHAT THIS PROBE DOES

It calls the pipeline's OWN functions -- `index`, `source_exclusion`,
`require_themed_shells`, `pick_lot` -- and reports what they say. It does not
reimplement any of them, and it does not decide anything: no exit code means
"defect". A human reads the draw and the file dates and says whether `shell`
is an archetype.

WHAT IT CANNOT SAY

It cannot tell you what a PAST run drew. `pick_lot` is deterministic on
(pool, seed, count), so replaying it here reproduces a draw only if the
library is in the same state it was in then -- and this probe prints the file
dates precisely because that is the thing most likely to have changed. If the
draw it prints disagrees with the package on disk, the library moved, and
that is a finding of its own rather than a bug in this script.

It also cannot tell you whether an entry is authored. It can only report the
tells: whether Deli Counter ever judged it (`<id>.validation.json`), whether
the nav gate ever ran on it (`<id>.navgate.json`), whether it can carry art
(`<id>.lights.json`), and when its files were written. An archetype nobody
has judged, written minutes ago, sitting in a directory that is both the
source and the sink, is worth a human look. It is not proof.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path


def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Same rule as `probe_pool_divergence.py`: the manifest is the marker
    because it is the one file that defines this place and exists in no tool
    repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()
sys.path.insert(0, str(ROOT / "level_factory"))

DEFAULT_LIBRARY = ROOT / "deli_counter" / "build"
#: Names this pipeline writes for its own artifacts. NOT a blocklist -- the
#: probe reports on them, it does not exclude them. `shell` is here because
#: roadmap 49 found it in a package; the others are its neighbours in every
#: job out/ dir, and if one of them is ever indexed the same way, the reader
#: should find out from a probe rather than from an export.
DEFAULT_SUSPECTS = ("shell", "site", "site_base", "lot")


def _stamp(p: Path) -> str:
    try:
        t = p.stat().st_mtime
    except OSError:
        return "-"
    return _dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")


def _ids(entries) -> list[str]:
    return [e.get("id", "?") for e in entries]


def _report_one(BL, lib: Path, aid: str, complete, incomplete, non_source,
                themed) -> None:
    """Everything the library says about one id, in one block."""
    in_c = next((e for e in complete if e.get("id") == aid), None)
    in_i = next((e for e in incomplete if e.get("id") == aid), None)
    in_n = next((e for e in non_source if e.get("id") == aid), None)
    in_t = any(e.get("id") == aid for e in themed)
    glb = lib / f"{aid}.glb"

    print(f"  {aid}")
    if not glb.is_file() and not (in_c or in_i or in_n):
        print(f"      not in this library at all")
        print()
        return

    where = ("COMPLETE -- drawable" if in_c else
             "incomplete" if in_i else
             "non-source (excluded)" if in_n else
             "has a .glb but index did not classify it")
    print(f"      index says      : {where}")
    if in_n:
        print(f"      exclusion reason: {in_n.get('reason', '')[:96]}")
    if in_i:
        print(f"      missing         : {', '.join(in_i.get('missing', []))}")
    if in_c:
        print(f"      in themed pool  : {'YES' if in_t else 'no'}")
        print(f"      family          : {in_c.get('family')}")
    # The tells. Each one is a question, not a verdict.
    for suf, what in ((".glb", "geometry"),
                      (".gameplay.json", "gameplay"),
                      (".slots.json", "slots"),
                      (".validation.json", "Deli Counter judged it"),
                      (".navgate.json", "nav gate ran"),
                      (".lights.json", "can carry art")):
        p = lib / f"{aid}{suf}"
        mark = _stamp(p) if p.is_file() else "ABSENT"
        print(f"      {suf:<18} {mark:<17} {what}")
    print(f"      source_exclusion: "
          f"{BL.source_exclusion(lib, aid) or '(none -- treated as authored)'}")
    print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--library", default=str(DEFAULT_LIBRARY),
                    help="Deli Counter build dir (default: deli_counter/build)")
    ap.add_argument("--seed", type=int, default=5017,
                    help="candidate seed to replay (default 5017, unlit_probe_001)")
    ap.add_argument("--count", type=int, default=1,
                    help="buildings in the lot (default 1, as unlit_probe_001)")
    ap.add_argument("--suspect", nargs="*", default=list(DEFAULT_SUSPECTS),
                    help="ids to interrogate by name")
    ap.add_argument("--newest", type=int, default=12,
                    help="how many of the newest drawable entries to list")
    args = ap.parse_args(argv)

    from packages.pipeline import building_library as BL

    lib = Path(args.library)
    if not lib.is_dir():
        print(f"not a directory: {lib}")
        return 2

    complete, incomplete, non_source = BL.index(lib)

    # `require_themed_shells` RAISES rather than returning a short list -- by
    # design, and its docstring is emphatic about why. A probe that let that
    # escape would die on exactly the libraries most worth asking about, so
    # the refusal is CAUGHT AND REPORTED here. Found by running this script
    # against a library too small to fill the lot, which is what it is for.
    themed, themed_refused = [], ""
    if complete:
        try:
            themed = BL.require_themed_shells(list(complete), args.count)
        except Exception as exc:                              # noqa: BLE001
            themed_refused = str(exc)

    print(f"library {lib}")
    print(f"  {len(complete)} complete (drawable), {len(incomplete)} "
          f"incomplete, {len(non_source)} excluded as non-source")
    if themed_refused:
        print(f"  themed pool at count={args.count}: REFUSED")
        print(f"    {themed_refused[:200]}")
        print(f"    -- an --art run on this library would fail here, before")
        print(f"       any of the questions below. That is the finding.")
    else:
        print(f"  themed pool at count={args.count}: {len(themed)} of "
              f"{len(complete)}")
    print()

    print("WHAT source_exclusion ALREADY CATCHES")
    if not non_source:
        print("  nothing -- every .glb in this directory indexed as a source")
    for e in sorted(non_source, key=lambda x: x.get("id", "")):
        print(f"  {e.get('id')}")
    print()

    print("THE NAMED SUSPECTS -- ids this pipeline writes for its own outputs")
    for aid in args.suspect:
        _report_one(BL, lib, aid, complete, incomplete, non_source, themed)

    print(f"THE DRAW, replayed at seed {args.seed}, count {args.count}")
    if not complete:
        print("  nothing to draw from")
        return 1
    wide = _ids(BL.pick_lot(list(complete), args.seed, args.count))
    narrow = _ids(BL.pick_lot(list(themed), args.seed, args.count)) \
        if themed else []
    print(f"  wide pool   ({len(complete):>3} shells): "
          f"{', '.join(wide) or '-'}")
    if themed_refused:
        print(f"  themed pool     (refused): the pipeline never gets a draw")
    else:
        print(f"  themed pool ({len(themed):>3} shells): "
              f"{', '.join(narrow) or '-'}")
    if themed_refused:
        pass
    elif wide != narrow:
        print("  the two pools draw differently at this seed -- which is item")
        print("  48's whole subject, and 0.38.0 made the pipeline use the")
        print("  themed one in both passes. This line is the LIBRARY's answer,")
        print("  not the pipeline's; the pipeline now draws the second row.")
    else:
        print("  both pools draw the same lot at this seed")
    drawn = set(narrow or wide)
    hits = sorted(drawn.intersection(args.suspect))
    if hits:
        print()
        print(f"  LOOK the draw contains {', '.join(hits)} -- a name this")
        print(f"       pipeline writes for its own output. That is roadmap 49's")
        print(f"       first question and it is answered YES on this library.")
    print()

    print(f"THE {args.newest} NEWEST DRAWABLE ENTRIES, and whether anyone judged them")
    print(f"  {'id':<44} {'written':<17} judged  navgate  art")
    rows = []
    for e in complete:
        aid = e.get("id", "?")
        rows.append((lib / f"{aid}.glb", aid, e))
    rows.sort(key=lambda r: (r[0].stat().st_mtime if r[0].is_file() else 0),
              reverse=True)
    for p, aid, e in rows[:max(0, args.newest)]:
        judged = "yes" if (lib / f"{aid}.validation.json").is_file() else "NO "
        print(f"  {aid[:44]:<44} {_stamp(p):<17} {judged:<7} "
              f"{'yes' if e.get('navgate') else 'NO ':<8} "
              f"{'yes' if e.get('lights') else 'NO '}")
    print()
    print("  `judged` is `<id>.validation.json`, the manifest source_exclusion")
    print("  reads for `facade`. Its ABSENCE is deliberately not an exclusion")
    print("  -- index's docstring says so, and names the one authored shell")
    print("  that has none. So a row reading NO is a question, not a verdict.")
    print()
    print("  This probe decides nothing and exits 0 either way. What it is for")
    print("  is putting the draw, the exclusion rule and the file dates on one")
    print("  screen, so the next person does not have to reconstruct them from")
    print("  an export that failed to open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
