"""Deli Counter hand-copies six names out of Zoo. Nothing checked they agreed.

    python test_mirror_agreement.py            # standalone, prints what it read
    python -m pytest test_mirror_agreement.py  # or collected

## Why this exists

`deli_counter/themed_tscn.py` carries its own copies of `PLATE_ROLES`,
`OPENING_ROLES`, `slot_typename`, `void_tag`, `opening_tag` and `module_stem`,
each labelled in a comment as a mirror of `zoo_keeper.core.kit`. Zoo builds the
module; DC writes the `.tscn` that names it. If the two disagree about a
filename by one character, the scene references a module that was never built.

That happened. `roof` was added to Zoo's `PLATE_ROLES` and not to DC's, so DC
wrote `roof_rockay_01_w4000` while Zoo built
`roof_rockay_01_w4000_d3000_v72fc6e`. An orphan of the old name from a previous
run was still sitting in `art/zoo/`, so the load succeeded, and the orphan was a
solid plate over a cut stairwell. It was found by a bot walking into it.

## What it checks, and why not just the tuple

Tuple equality alone would NOT have caught a drifted `void_tag` -- both sides
would agree on which roles get a `_v` tag and still produce different tags. So
this compares the FILENAME, which is the actual contract, at three depths:

  1. every name DC's source declares as a mirror actually exists in Zoo;
  2. mirrored callables have identical signatures (parameter names AND order);
  3. mirrored callables return identical values over a shared corpus, including
     the asymmetry the docstrings promise -- a plate's voids are a SET and sort,
     a slot's openings keep ORDER, so reordering the first must not change the
     tag and reordering the second must.

Check 1 is discovered from DC's own `#: Mirror of ...` comments, so a mirror
added later is enrolled automatically rather than needing someone to remember.

## No skips

If a module cannot be imported or a mirrored name is missing, this FAILS. A
test that skips when it cannot find its subject reports the same green as a
test that ran, which is the substitution this repo has been bitten by before.
"""
from __future__ import annotations

import importlib
import inspect
import re
import sys
from pathlib import Path

DC_REL = Path("deli_counter") / "themed_tscn.py"
ZOO_REL = Path("zoo") / "zoo_keeper" / "core" / "kit.py"

MIRROR_RE = re.compile(r"Mirror of ``zoo_keeper\.core\.kit\.([A-Za-z_][A-Za-z_0-9]*)``")


# ----------------------------------------------------------------- locating
def factory_root() -> Path:
    """Walk up until both repos are visible. Fails loudly rather than guessing."""
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / DC_REL).is_file() and (base / ZOO_REL).is_file():
            return base
    raise SystemExit(
        f"cannot see both {DC_REL} and {ZOO_REL} from {here.parent} or any "
        f"parent. This test spans two repos and must run from a tree that "
        f"holds both.")


def load(repo_dir: Path, dotted: str):
    """Import a module the way ITS OWN repo expects to be imported.

    Loading by file path alone fails: `themed_tscn` does
    `from tscn_export import ...`, a sibling import that needs
    `deli_counter/` on `sys.path`. Each repo root goes on the path only for
    the duration of its own import, so DC's modules cannot shadow Zoo's."""
    old = list(sys.path)
    sys.path.insert(0, str(repo_dir))
    try:
        return importlib.import_module(dotted)
    except ImportError as exc:
        raise SystemExit(
            f"cannot import {dotted} with {repo_dir} on sys.path: {exc}\n"
            f"This test must import both copies to compare them; it will not "
            f"skip.") from exc
    finally:
        sys.path[:] = old


ROOT = factory_root()
DC = load(ROOT / DC_REL.parts[0], "themed_tscn")
ZOO = load(ROOT / ZOO_REL.parts[0], "zoo_keeper.core.kit")
DC_SRC = (ROOT / DC_REL).read_text(encoding="utf-8")


# ------------------------------------------------------------------- corpus
VOIDS = [
    None,
    [],
    [{"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}],
    [{"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2},
     {"x0": 2.0, "y0": 3.0, "x1": 4.0, "y1": 5.0}],
    [{"x0": 2.0, "y0": 3.0, "x1": 4.0, "y1": 5.0},
     {"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}],   # same set, reordered
    [{"x0": -1.5, "y0": -2.25, "x1": 0.0, "y1": 0.125}],
]

OPENINGS = [
    None,
    [],
    [{"kind": "doorway", "x0": 1.0, "y0": 0.0, "x1": 2.4, "y1": 2.1}],
    [{"kind": "doorway", "x0": 1.0, "y0": 0.0, "x1": 2.4, "y1": 2.1},
     {"kind": "window", "x0": 5.0, "y0": 1.0, "x1": 6.6, "y1": 2.8}],
    [{"kind": "window", "x0": 5.0, "y0": 1.0, "x1": 6.6, "y1": 2.8},
     {"kind": "doorway", "x0": 1.0, "y0": 0.0, "x1": 2.4, "y1": 2.1}],  # reordered
]

TYPENAMES = [("wall", "end"), ("wall", None), ("wall", ""), ("roof", None),
             ("roof", "end"), ("floor", "end"), ("ceiling", None),
             ("doorway", None), ("prop", None)]

#: Values offered to `module_stem` by PARAMETER NAME, so the call is built from
#: the signature rather than from a remembered argument order.
STEM_VALUES = {
    "typ": ["roof", "floor", "ceiling", "wall", "wallEnd", "doorway"],
    "theme": ["rockay"],
    "style": [1, 2],
    "width_cm": [4000, 160, None],
    "state": [None, "breached"],
    "depth_cm": [3000, 1200, None],
    # `module_stem` adds the `_v` / `_o` prefixes itself -- `void_tag` and
    # `opening_tag` return the bare digest, so these are bare too.
    "voids_tag": [None, "72fc6e", "a4904f"],
    "openings_tag": [None, "933dff", "ff03c6"],
}

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  [ok]   {label}")
    else:
        print(f"  [FAIL] {label}" + (f"\n         {detail}" if detail else ""))
        FAILURES.append(label)


# -------------------------------------------------------------------- tests
def test_every_declared_mirror_exists_in_zoo():
    """DC's own comments name its mirrors. Each one must be a real Zoo name."""
    declared = sorted(set(MIRROR_RE.findall(DC_SRC)))
    check("themed_tscn declares at least one mirror", bool(declared),
          "no `Mirror of ``zoo_keeper.core.kit.X``` comments found -- either "
          "the convention changed or this test is reading the wrong file")
    for name in declared:
        check(f"kit.{name} exists (declared as a mirror)", hasattr(ZOO, name))
        check(f"themed_tscn.{name} exists", hasattr(DC, name))
    return declared


def test_mirrored_constants_are_equal():
    for name in ("PLATE_ROLES", "OPENING_ROLES"):
        a, b = getattr(DC, name, None), getattr(ZOO, name, None)
        check(f"{name} equal", a == b, f"themed_tscn {a!r}  !=  kit {b!r}")


def test_mirrored_signatures_match():
    """Same parameter names in the same order, or the value comparison below
    would be comparing two different functions and calling it agreement."""
    for name in ("slot_typename", "void_tag", "opening_tag", "module_stem"):
        f, g = getattr(DC, name, None), getattr(ZOO, name, None)
        if f is None or g is None:
            check(f"{name} present on both sides", False)
            continue
        pa = list(inspect.signature(f).parameters)
        pb = list(inspect.signature(g).parameters)
        check(f"{name} signature", pa == pb,
              f"themed_tscn({', '.join(pa)})  !=  kit({', '.join(pb)})")


def test_slot_typename_agrees():
    for role, mod in TYPENAMES:
        a, b = DC.slot_typename(role, mod), ZOO.slot_typename(role, mod)
        check(f"slot_typename({role!r}, {mod!r}) -> {a!r}", a == b,
              f"themed_tscn {a!r} != kit {b!r}")


def test_void_tag_agrees():
    for v in VOIDS:
        a, b = DC.void_tag(v), ZOO.void_tag(v)
        n = "None" if v is None else f"{len(v)} rect(s)"
        check(f"void_tag({n}) -> {a!r}", a == b,
              f"themed_tscn {a!r} != kit {b!r}")


def test_void_tag_is_order_insensitive_on_both_sides():
    """`opening_tag`'s docstring: 'A plate's voids are a set and sort; these do
    not.' Both mirrors must honour that, or two identical plates get two names."""
    a1, a2 = DC.void_tag(VOIDS[3]), DC.void_tag(VOIDS[4])
    b1, b2 = ZOO.void_tag(VOIDS[3]), ZOO.void_tag(VOIDS[4])
    check("void_tag ignores rect order (themed_tscn)", a1 == a2,
          f"{a1!r} != {a2!r}")
    check("void_tag ignores rect order (kit)", b1 == b2, f"{b1!r} != {b2!r}")


def test_opening_tag_agrees_and_keeps_order():
    for o in OPENINGS:
        a, b = DC.opening_tag(o), ZOO.opening_tag(o)
        n = "None" if o is None else f"{len(o)} opening(s)"
        check(f"opening_tag({n}) -> {a!r}", a == b,
              f"themed_tscn {a!r} != kit {b!r}")
    # ORDER IS KEPT: only the first opening is cut, so a different order is a
    # different module. Both sides must agree that these are NOT the same.
    d1, d2 = DC.opening_tag(OPENINGS[3]), DC.opening_tag(OPENINGS[4])
    z1, z2 = ZOO.opening_tag(OPENINGS[3]), ZOO.opening_tag(OPENINGS[4])
    check("opening_tag keeps order (themed_tscn)", d1 != d2,
          f"reordered openings produced the same tag {d1!r}")
    check("opening_tag keeps order (kit)", z1 != z2,
          f"reordered openings produced the same tag {z1!r}")


def _stem_calls():
    """Build every call positionally from the SHARED signature."""
    params = list(inspect.signature(ZOO.module_stem).parameters)
    unknown = [p for p in params if p not in STEM_VALUES]
    if unknown:
        check("module_stem corpus covers every parameter", False,
              f"no corpus values for {unknown!r} -- add them to STEM_VALUES "
              f"rather than letting the parameter go untested")
        return
    # One axis varied at a time against a fixed base: full cross product is
    # 864 calls and says nothing more than this does.
    base = {p: STEM_VALUES[p][0] for p in params}
    seen = set()
    for p in params:
        for val in STEM_VALUES[p]:
            args = dict(base, **{p: val})
            key = tuple(repr(args[q]) for q in params)
            if key in seen:
                continue
            seen.add(key)
            yield [args[q] for q in params]


def test_module_stem_agrees():
    n = 0
    for args in _stem_calls():
        a = DC.module_stem(*args)
        b = ZOO.module_stem(*args)
        n += 1
        if a != b:
            check(f"module_stem{tuple(args)!r}", False,
                  f"themed_tscn {a!r} != kit {b!r}")
            return
    check(f"module_stem agrees on {n} calls", n > 0,
          "no calls were made -- the corpus did not cover the signature")


def test_the_regression_that_started_this():
    """bank_branch_a04's roof: 40.0 x 30.0 plate with the ladder's void. The
    name DC writes into site.tscn must be the name Zoo built."""
    voids = [{"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}]
    slot = {"role": "roof", "size_mod": None,
            "fit": {"dims": [40.0, 30.0, 0.3], "voids": voids}}
    stem, scaled = DC.resolve_themed_stem(slot, "rockay", 1)

    # Build Zoo's name for the same slot from the SHARED signature, rather than
    # asserting a `_d`/`_v` spelling this test would then be the only record of.
    params = list(inspect.signature(ZOO.module_stem).parameters)
    vals = {"typ": ZOO.slot_typename("roof", None), "theme": "rockay",
            "style": 1, "width_cm": 4000, "state": DC._default_stem_state(slot),
            "depth_cm": 3000, "voids_tag": ZOO.void_tag(voids),
            "openings_tag": None}
    missing = [p for p in params if p not in vals]
    check("regression case covers module_stem's signature", not missing,
          f"no value for {missing!r}")
    expected = None if missing else ZOO.module_stem(*[vals[p] for p in params])

    check(f"roof stem is the name Zoo builds -> {expected!r}", stem == expected,
          f"themed_tscn {stem!r} != kit {expected!r}\n"
          f"         this is the ladder: the scene names a module nobody built")
    check("roof stem is not scaled", scaled is False, f"scaled={scaled!r}")


def main() -> int:
    print(f"\n  factory root  {ROOT}")
    print(f"  deli counter  {DC_REL}   -> {DC.__name__} from {DC.__file__}")
    print(f"  zoo           {ZOO_REL}  -> {ZOO.__name__} from {ZOO.__file__}\n")
    declared = test_every_declared_mirror_exists_in_zoo()
    print(f"\n  mirrors declared in themed_tscn.py: {', '.join(declared)}\n")
    for fn in (test_mirrored_constants_are_equal,
               test_mirrored_signatures_match,
               test_slot_typename_agrees,
               test_void_tag_agrees,
               test_void_tag_is_order_insensitive_on_both_sides,
               test_opening_tag_agrees_and_keeps_order,
               test_module_stem_agrees,
               test_the_regression_that_started_this):
        fn()
    print()
    if FAILURES:
        print(f"  {len(FAILURES)} disagreement(s) between the two copies:")
        for f in FAILURES:
            print(f"    - {f}")
        print("\n  These are HAND COPIES. Fix the copy that is wrong; do not "
              "make the test tolerant.")
        return 1
    print("  the two copies agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
