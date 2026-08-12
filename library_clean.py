"""How many shells are actually clean, and can a varied lot be drawn from them.

    python library_clean.py <deli_counter/build>
    python library_clean.py <deli_counter/build> --list

Pure: reads the manifests already on disk. No Blender, no Godot, no rebuild.

## The question this answers, and why it is not one number

The census says 17 shells carry no warnings and 30 have all markers reachable.
Those are different 17 and 30 and the overlap is unknown -- and the overlap is
the number that decides whether "select only clean shells into a themed lot" is
a rule or a wish.

`pick_lot` also draws one shell per FAMILY, so 5 clean shells spread over 3
families cannot fill a 5-building lot. A count alone would look sufficient and
fail at selection. Families are counted here for that reason.

## Three states, not two

A shell with `markers.checked == 0` has not been judged reachable. It is
UNJUDGED, not passing. Folding it in with the shells that were checked and
found reachable would be inventing evidence -- the same move as reading
`passed=True` off a gate that emitted ten warnings.

## Tiers, reported rather than chosen between

Which defects should keep a shell out of a themed lot is a decision about the
game, not about the data, so this prints several bars and the lot each one
could still fill. Nothing here picks one.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

_VARIANT = re.compile(r"_a\d+$")


def family(aid: str) -> str:
    return _VARIANT.sub("", aid)


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python library_clean.py <deli_counter/build> [--list]")
        return 2
    root = Path(argv[0])
    show = "--list" in argv
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    rows = []
    for p in sorted(root.glob("*.glb")):
        aid = p.name[: -len(".glb")]
        v = _load(root / f"{aid}.validation.json")
        n = _load(root / f"{aid}.navgate.json")
        if v is None:
            rows.append((aid, None, None, None, None))
            continue
        gates = v.get("gates") or {}
        counts = {g: len((b or {}).get("warnings") or []) for g, b in gates.items()}
        total = sum(counts.values())
        checked = reach = None
        if n is not None:
            m = n.get("markers") or {}
            checked = int(m.get("checked") or 0)
            reach = int(m.get("reachable") or 0)
        rows.append((aid, total, counts, checked, reach))

    judged = [r for r in rows if r[1] is not None]
    print(f"library: {root}")
    print(f"  {len(rows)} shells, {len(judged)} with a validation manifest")
    print()

    def reachable_ok(checked, reach):
        """True only when it was CHECKED and everything was reachable."""
        return checked is not None and checked > 0 and reach == checked

    def unjudged(checked):
        return checked is None or checked == 0

    TIERS = [
        ("no warnings at all, all markers reachable",
         lambda t, c, ch, r: t == 0 and reachable_ok(ch, r)),
        ("no warnings at all (reachability ignored)",
         lambda t, c, ch, r: t == 0),
        ("all markers reachable (warnings ignored)",
         lambda t, c, ch, r: reachable_ok(ch, r)),
        ("no STAIRWELL or LADDER warning, all markers reachable",
         lambda t, c, ch, r: not c.get("stairwell") and not c.get("ladder")
         and reachable_ok(ch, r)),
        ("no STAIRWELL warning (reachability ignored)",
         lambda t, c, ch, r: not c.get("stairwell")),
    ]

    print(f"{'bar':>58}  {'shells':>6} {'families':>9}  5-family lot?")
    for label, pred in TIERS:
        hits = [r for r in judged if pred(r[1], r[2], r[3], r[4])]
        fams = sorted({family(r[0]) for r in hits})
        ok = "YES" if len(fams) >= 5 else f"NO ({len(fams)} fam)"
        print(f"{label:>58}  {len(hits):>6} {len(fams):>9}  {ok}")
        if show and hits:
            by = collections.defaultdict(list)
            for r in hits:
                by[family(r[0])].append(r[0])
            for f in fams[:12]:
                print(f"        {f:24} {', '.join(sorted(by[f]))}")
            if len(fams) > 12:
                print(f"        ... and {len(fams) - 12} more families")
            print()

    unj = [r for r in judged if unjudged(r[3])]
    print()
    print(f"UNJUDGED for reachability (markers.checked == 0 or no navgate): "
          f"{len(unj)}")
    print("  These are not passing. Nothing has asked whether they are "
          "reachable.")
    if show and unj:
        print("  " + ", ".join(r[0] for r in unj[:20]))

    nom = [r for r in rows if r[1] is None]
    if nom:
        print()
        print(f"NO VALIDATION MANIFEST: {len(nom)} -- never judged at all")
        print("  " + ", ".join(r[0] for r in nom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
