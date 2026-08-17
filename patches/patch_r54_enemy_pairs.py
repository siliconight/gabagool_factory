"""Lot stops spending its cover budget on enemy-to-enemy lines.

WHAT THIS CHANGES
-----------------
One anchored edit to `lot/site_cover.py`, inside `plan_cover`'s nested
`outstanding()`: the comprehension that feeds the opening pass now skips
any line whose BOTH endpoints are enemy spawns.

WHY
---
`open_sightlines` is all-pairs over the marker dict. `lot.py:1920` builds
that dict as three mission markers plus one `Enemy_{i}` per placed enemy,
so K enemies contribute C(K,2) lines that describe enemies shooting each
other. Lot's opening budget is twelve pieces and it was buying them.

MEASURED, not assumed. The shipped export
`workspaces/lot-demo-ws/.level_factory/exports/LF_lot_demo_001.pure-shell/
site.site.gameplay.json` carries 16 placed pieces, each with a `breaks`
field naming the pair it was placed for:

    11  route@N -> Enemy_M      (the route pass)
     3  Enemy_M -> LT_ObjectivePoint
     2  Enemy_M -> Enemy_N      <-- these two
     0  anything touching LT_PlayerSpawn

The two are `Enemy_2 -> Enemy_5` and `Enemy_1 -> Enemy_5`.

WHAT THIS DOES NOT DO
---------------------
It does not free budget for crew lines. On `lot_demo_001` only five lines
qualified for the opening pass at all, so the pass will place three rather
than five and the two slots go UNUSED. Predicted: placed 16 -> 14, opening
5 -> 3, route pass unchanged at 11, still_open 0, route_open 14,
unbreakable 0, pinches 0. If the rerun shows anything else, this patch's
reasoning is wrong and it should be reverted.

It also does not decouple Lot from enemy placement. 15 of the 16 pieces
are placed against an `Enemy_*` point; the enemy markers are a six-sample
approximation of "somewhere a shooter could stand". Re-posing that on
standable ground within OPENING_RANGE of the route is a separate item.

WHAT IT DELIBERATELY LEAVES ALONE
---------------------------------
`open_sightlines` itself. It has eight other callers, including
`level_factory/packages/validation/sightlines.py` and `.../tactical.py`.
Laser Tag reading enemy-to-enemy lines is legitimate advisory work. It is
Lot's BUDGET that should not pay for them, so the filter lives at the
point of spend.

USAGE
    python patches\\patch_r54_enemy_pairs.py --check
    python patches\\patch_r54_enemy_pairs.py --selftest
    python patches\\patch_r54_enemy_pairs.py
    python patches\\patch_r54_enemy_pairs.py --revert
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TAG = "r54enemypairs"
ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "site_cover.py"
FILES = (TARGET,)

#: The one line the edit is anchored to, matched on its STRIPPED form so
#: the continuation indent of the comprehension above it is never guessed.
ANCHOR = "if (line[0], line[1]) not in refused]"

#: What must still be true of the file for this edit to mean anything.
REQUIRED = (
    'ENEMY_PREFIX = "Enemy_"',
    "def outstanding():",
    "def open_sightlines(points: dict, rects, *, limit: float):",
)

COMMENT = (
    "# ENEMY-ENEMY LINES ARE NOT LOT'S BUDGET TO SPEND.",
    "# `open_sightlines` is all-pairs, so K enemies add",
    "# C(K,2) lines that say nothing about the crew. On the",
    "# shipped `lot_demo_001` export the opening pass placed",
    "# five pieces and two of them broke `Enemy_2 -> Enemy_5`",
    "# and `Enemy_1 -> Enemy_5`, while nothing at all was",
    "# placed on a line touching LT_PlayerSpawn.",
    "# `open_sightlines` itself is unchanged, so Laser Tag and",
    "# the validation package still read those lines; it is",
    "# only Lot that stops paying for them. The enemy points",
    "# are still an input here -- removing them is the",
    "# re-posing item, not this one.",
)


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _eol(p: Path) -> str:
    """Keyed off the FILE, never off an anchor. Refuses on mixed."""
    b = p.read_bytes()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    cr = b.count(b"\r") - crlf
    if cr:
        raise SystemExit(f"REFUSING: {p.name} contains {cr} bare CR")
    if crlf and lf:
        raise SystemExit(
            f"REFUSING: {p.name} has mixed endings ({crlf} CRLF, {lf} LF)")
    return "\r\n" if crlf else "\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()[:16]


def _block(indent: str) -> list:
    """The lines that replace the anchor. ONE definition, so no count is
    ever stated in prose -- the selftest measures len(_block("")) instead."""
    out = [indent + "if (line[0], line[1]) not in refused"]
    out += [indent + c for c in COMMENT]
    out += [
        indent + "and not (line[0].startswith(ENEMY_PREFIX)",
        indent + "         and line[1].startswith(ENEMY_PREFIX))]",
    ]
    return out


def transform(text: str) -> str:
    """text -> text. Newline-agnostic: caller supplies \\n-normalised text."""
    for needle in REQUIRED:
        if needle not in text:
            raise SystemExit(f"REFUSING: site_cover.py no longer contains {needle!r}")

    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.strip() == ANCHOR]
    if len(hits) != 1:
        raise SystemExit(
            f"REFUSING: {len(hits)} line(s) strip to the anchor, expected exactly 1. "
            f"Either the file drifted or this patch is already applied.")
    i = hits[0]
    raw = lines[i]
    indent = raw[:len(raw) - len(raw.lstrip())]

    return "\n".join(lines[:i] + _block(indent) + lines[i + 1:])


def _import_real():
    """Import site_cover NORMALLY, for real geometry.

    An earlier version of this selftest exec'd the PATCHED source into a
    synthetic module. That failed with `'NoneType' has no attribute
    '__dict__'` -- module-level code in site_cover.py evidently looks
    itself up in sys.modules, which a synthetic module is not in.

    Exec'ing a copy was never necessary. The predicate this patch adds is
    a pure expression on line[0]/line[1]; it needs real LINES, not a real
    patched module. That the patched file compiles, and that its
    open_sightlines is byte-identical, are asserted separately above.
    """
    lot = str(ROOT / "lot")
    if lot not in sys.path:
        sys.path.insert(0, lot)
    import importlib
    return importlib.import_module("site_cover")


def check() -> int:
    problems = []
    for p in FILES:
        if not p.exists():
            problems.append(f"missing: {p}")
    if problems:
        for m in problems:
            print("  " + m)
        return 1

    text = TARGET.read_text(encoding="utf-8")
    n = sum(1 for ln in text.split("\n") if ln.strip() == ANCHOR)
    print(f"anchor lines matching (stripped): {n}   [want exactly 1]")
    naive = text.count(ANCHOR)
    print(f"naive substring count of the same text: {naive}"
          "   [printed so the two can be compared]")
    for needle in REQUIRED:
        print(f"  present: {needle!r} -> {needle in text}")
    if _sidecar(TARGET).exists():
        print(f"  NOTE: {_sidecar(TARGET).name} exists -- already applied? use --revert")

    b = TARGET.read_bytes()
    print(f"\n{TARGET.relative_to(ROOT)}  {len(b)} B  sha256 {_sha(b)}  eol "
          f"{'CRLF' if _eol(TARGET) == chr(13) + chr(10) else 'LF'}")
    if n != 1:
        print("\nNOT APPLICABLE")
        return 1
    out = transform(text)
    eol = _eol(TARGET)
    nb = out.replace("\n", eol).encode("utf-8")
    print(f"APPLICABLE: {len(b)} -> {len(nb)} B  ({len(nb) - len(b):+d})")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(("[ok]  " if cond else "[FAIL]  ") + label)
        if not cond:
            fails.append(label)

    for p in FILES:
        ok(p.exists(), f"{p.relative_to(ROOT)} exists")
    if fails:
        return 1

    old = TARGET.read_text(encoding="utf-8")

    # -- the anchor is unique, and the naive form is reported beside it ----
    stripped = sum(1 for ln in old.split("\n") if ln.strip() == ANCHOR)
    naive = old.count(ANCHOR)
    print(f"        (stripped-line matches {stripped}, naive substring {naive})")
    ok(stripped == 1, "exactly one line strips to the anchor")

    new = transform(old)

    # -- the edit landed, and is the only thing that moved ----------------
    ok(ANCHOR not in new,
       "the bracket-terminated anchor line is gone")
    ok(new.count("ENEMY_PREFIX") == old.count("ENEMY_PREFIX") + 2,
       f"ENEMY_PREFIX uses {old.count('ENEMY_PREFIX')} -> "
       f"{new.count('ENEMY_PREFIX')} (+2)")
    grew = len(new.split("\n")) - len(old.split("\n"))
    want = len(_block("")) - 1
    ok(grew == want, f"line count grew by {grew}, derived expectation {want}")

    # -- it is still Python ------------------------------------------------
    try:
        compile(new, str(TARGET), "exec")
        ok(True, "the patched file compiles")
    except SyntaxError as exc:
        ok(False, f"the patched file compiles ({exc})")
        return 1

    # -- open_sightlines is byte-identical, for its seven other callers ---
    def grab(text, name):
        ls = text.split("\n")
        for i, ln in enumerate(ls):
            if ln.startswith("def ") and ln.split("(")[0][4:].strip() == name:
                hi = i + 1
                while hi < len(ls) and not ls[hi].startswith(("def ", "class ")):
                    hi += 1
                return "\n".join(ls[i:hi])
        return None

    ok(grab(old, "open_sightlines") is not None, "open_sightlines was found")
    ok(grab(old, "open_sightlines") == grab(new, "open_sightlines"),
       "open_sightlines is byte-identical after the edit")

    # -- idempotence: applying twice refuses -------------------------------
    try:
        transform(new)
        ok(False, "re-applying refuses")
    except SystemExit:
        ok(True, "re-applying refuses")

    # -- drift: two anchors refuses ----------------------------------------
    synthetic = old.replace(ANCHOR, ANCHOR + "\n" + " " * 17 + ANCHOR, 1)
    try:
        transform(synthetic)
        ok(False, "a drifted file with two anchors refuses")
    except SystemExit:
        ok(True, "a drifted file with two anchors refuses")

    # -- the predicate, on real geometry, before vs after -------------------
    POINTS = {
        "LT_PlayerSpawn": (0.0, 0.0),
        "LT_ObjectivePoint": (0.0, -60.0),
        "Enemy_0": (60.0, 0.0),
        "Enemy_1": (-60.0, 0.0),
        "Enemy_2": (0.0, 60.0),
    }
    try:
        mod = _import_real()
    except Exception as exc:
        import traceback
        ok(False, f"site_cover imports ({type(exc).__name__}: {exc})")
        print(traceback.format_exc())
        return 1
    ok(True, "site_cover imports (real module, for real geometry)")

    lines = mod.open_sightlines(POINTS, [], limit=45.0)
    pairs = [(a, b) for a, b, _pa, _pb, _d in lines]
    ee = [(a, b) for a, b in pairs
          if a.startswith(mod.ENEMY_PREFIX) and b.startswith(mod.ENEMY_PREFIX)]
    other = [(a, b) for a, b in pairs if (a, b) not in ee]
    print(f"        (open_sightlines returned {len(pairs)} lines: "
          f"{len(ee)} enemy-enemy, {len(other)} other)")
    ok(len(pairs) > 0,
       "open_sightlines returns lines on the synthetic yard "
       "(if 0, open_span with no rects behaves differently than assumed)")
    ok(len(ee) >= 1, "the synthetic yard really does contain enemy-enemy lines")

    kept = [(a, b) for a, b in pairs
            if not (a.startswith(mod.ENEMY_PREFIX)
                    and b.startswith(mod.ENEMY_PREFIX))]
    ok(len(kept) == len(other), "the new predicate keeps every non-enemy-enemy line")
    ok(all(not (a.startswith("Enemy_") and b.startswith("Enemy_"))
           for a, b in kept), "the new predicate drops every enemy-enemy line")
    ok(len(kept) < len(pairs), "it actually removes something (not a no-op)")

    print("\n" + ("SELFTEST PASSED" if not fails
                  else f"SELFTEST FAILED: {len(fails)}"))
    return 1 if fails else 0


def apply() -> int:
    for p in FILES:
        if not p.exists():
            raise SystemExit(f"REFUSING: missing {p}")
        if _sidecar(p).exists():
            raise SystemExit(f"REFUSING: {_sidecar(p).name} exists. Use --revert.")

    old_b = TARGET.read_bytes()
    eol = _eol(TARGET)
    out = transform(TARGET.read_text(encoding="utf-8"))
    new_b = out.replace("\n", eol).encode("utf-8")

    _sidecar(TARGET).write_bytes(old_b)
    TARGET.write_text(out, encoding="utf-8", newline=eol)

    print(f"{TARGET.relative_to(ROOT)}")
    print(f"  {len(old_b)} B  sha256 {_sha(old_b)}")
    print(f"  {len(new_b)} B  sha256 {_sha(new_b)}   ({len(new_b) - len(old_b):+d})")
    print(f"  sidecar: {_sidecar(TARGET).name}")
    print("\nNEXT -- the evidence bar, suite then the probe rerun:")
    print("    cd lot; python -m pytest tests -q; cd ..")
    print("    (then re-export lot_demo_001 and re-run the breaks probe)")
    print("\nPREDICTED on lot_demo_001: placed 16 -> 14, opening 5 -> 3,")
    print("route pass 11 unchanged, still_open 0, route_open 14, pinches 0.")
    return 0


def revert() -> int:
    s = _sidecar(TARGET)
    if not s.exists():
        raise SystemExit(f"REFUSING: no {s.name} to revert from")
    b = s.read_bytes()
    TARGET.write_bytes(b)
    s.unlink()
    print(f"reverted {TARGET.relative_to(ROOT)} to {len(b)} B sha256 {_sha(b)}")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg:
        raise SystemExit(f"unknown argument {arg!r}; "
                         f"use --check, --selftest, --revert, or no argument")
    return apply()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
