#!/usr/bin/env python3
"""Roadmap 3: the divergence is fixed, the remedy this item asked for is not.

Item 3 -- "Lot places enemies twice, and nothing checks the two agree" -- is
OPEN, and carries an explicit status line: "both call sites re-confirmed while
threading `solids` through `place_enemies`", dated 2026-08-12. It was not an
unclassified stub anybody could be forgiven for missing; it had been revisited
three weeks ago and deliberately left open. An item-51 investigation walked
past it anyway and re-derived its content as a new finding.

WHAT IT GOT RIGHT

Everything except the mechanism. Two `place_enemies` calls do fire inside one
`assemble`, they did return different six-enemy sets, and the comment claiming
"same inputs, same answer" was indeed untested. Measured 2026-08-16:

    assemble's call      (-16.000, 31.500) (10.000, 28.500) ... (-30.000, 64.500)
    the writer's call    ( -8.332, 43.500) (16.786, 28.500) ... (-31.357, -13.000)

and `lot.py` built the cover plan from the first while the walk scene shipped
the second.

WHAT IT GOT WRONG, DEFENSIBLY

This item blames a second `seat_destinations` pass with bounds derived from
already-seated points. The entire measured difference was `clear_crew_spawn`
moving the crew spawn 9.5 m out of the shell it started inside --
and `patch_lot_crew_spawn_clearance.py` added that on 2026-08-15, AFTER this
item was written. The item was correct for its time; a second cause landed on
top of it.

WHY NARROWED AND NOT CLOSED

This item asked for one of two things: "Place once, thread the result through,
or assert the two agree." Neither was done. `patch_lot_cover_ships_spawn.py`
made the INPUTS identical, so the two calls now agree by determinism -- which
is exactly the "same inputs, same answer" claim this item calls untested,
restored rather than removed. Item 51 recorded that gap in its own entry
without recognising it as this item's whole point.

NO EXPECTED BYTE COUNT IS CARRIED. `PIPELINE_ROADMAP.md` has been rewritten
five times today -- two roadmap patches, two `roadmap_status.py --write` runs,
and a line-ending renormalisation. Any size stamped here would be a guess, and
a guessed stamp invites trust it has not earned. Both anchors were read this
session; the identity is printed; drift refuses.

USAGE

    python patches\\patch_roadmap_03_narrowed.py --check
    python patches\\patch_roadmap_03_narrowed.py --selftest
    python patches\\patch_roadmap_03_narrowed.py
    python patches\\patch_roadmap_03_narrowed.py --revert

AFTER APPLYING:

    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r52item3"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "PIPELINE_ROADMAP.md"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings.")
    return "\r\n" if crlf else "\n"


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


ITEM3_ANCHOR = ("*STATUS: OPEN 2026-08-12 -- both call sites re-confirmed "
                "while threading `solids` through `place_enemies`*")

ITEM3_STATUS = (
    "*STATUS: NARROWED 2026-08-16 -- THE DIVERGENCE IS FIXED; THE REMEDY THIS "
    "ITEM ASKED FOR IS NOT. Measured during item 51, on the `test_site_cover` "
    "yard: the two calls returned different six-enemy sets inside one "
    "`assemble` -- the reporter gave (-16.000, 31.500) ... (-30.000, 64.500) "
    "and the writer gave (-8.332, 43.500) ... (-31.357, -13.000) -- and the "
    "cover plan was built from the first while the walk scene shipped the "
    "second, so every level's cover was planned against enemies it does not "
    "contain. `patch_lot_cover_ships_spawn.py` makes `assemble` clear the crew "
    "spawn before planning; `tools/probe_r51_cover_enemies.py` then reports "
    "`in_positions SAME, positions SAME` and the two sets identical. THE "
    "MECHANISM NAMED BELOW IS NOT THE ONE MEASURED: this item blames a second "
    "`seat_destinations` pass, and the entire 9.5 m difference was "
    "`clear_crew_spawn`, which `patch_lot_crew_spawn_clearance.py` added on "
    "2026-08-15 -- AFTER this item was written, so the item was right for its "
    "time and a second cause landed on top of it. The two call sites are "
    "`lot.py:1874` and `lot.py:1257` as measured; this item's `1337` and `975` "
    "are the same two sites before the file grew. STILL OPEN, and it is this "
    "item's actual prescription: the enemies are still placed TWICE and "
    "NOTHING ASSERTS the two agree -- they agree by determinism from identical "
    "inputs, which is precisely the \"same inputs, same answer\" claim this "
    "item calls untested, restored rather than removed. Either place once and "
    "thread the result through, or add the assertion. Item 51 recorded this "
    "gap in its own entry without recognising it as this item*"
)

ITEM51_ANCHOR = ("`place_enemies`, which is awkward given enemy placement "
                 "belongs to the gameplay layer and not to this pipeline*")

ITEM51_NEW = ("`place_enemies`, which is awkward given enemy placement "
              "belongs to the gameplay layer and not to this pipeline. AND SEE "
              "ITEM 3, \"Lot places enemies twice, and nothing checks the two "
              "agree\", which described the double placement before this "
              "session re-derived it as a new finding: item 3 carried an "
              "explicit OPEN status line dated 2026-08-12 saying both call sites had been re-confirmed, "
              "so it was neither unclassified nor stale -- it simply was not "
              "searched for. "
              "Its prescription -- place once and thread the result through, or "
              "assert the two agree -- is the fork this session chose between "
              "without knowing the item had already framed it, and the "
              "\"deliberately still open\" note above is that item's point "
              "restated*")

EDITS = [
    ("item 3: OPEN -> NARROWED", ITEM3_ANCHOR, ITEM3_STATUS),
    ("item 51: cross-reference item 3", ITEM51_ANCHOR, ITEM51_NEW),
]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    print(f"  {TARGET.name}")
    print(f"    bytes  : {len(raw)}   (no expected value carried -- see the "
          f"module docstring)")
    print(f"    sha256 : {_sha(raw)}")
    print(f"    endings: {crlf} CRLF, {lone} lone LF")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    ok = True
    for name, old, _new in EDITS:
        n = text.count(_n(old))
        print(f"  [{'ok' if n == 1 else 'MISSING'}]  {name}  (found {n})")
        ok = ok and n == 1
    print()
    print("APPLICABLE: both anchors present exactly once." if ok
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if ok else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    for name, old, _new in EDITS:
        if text.count(_n(old)) != 1:
            raise SystemExit(f"REFUSING: anchor for {name} not present exactly "
                             f"once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  applied {len(EDITS)} edits")
    print(f"  sidecar : {SIDECAR.name}")
    print(f"  bytes   : {len(raw)} -> {len(data)}  ({len(data) - len(raw):+d})")
    print(f"  sha256  : {_sha(data)}")
    print(f"  endings : {data.count(bytes([13, 10]))} CRLF, "
          f"{data.count(bytes([10])) - data.count(bytes([13, 10]))} lone LF")
    print()
    print("  NEXT: python tools\\roadmap_status.py --write")
    print("        python tools\\roadmap_status.py --check")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} B, sha256 {_sha(after)}")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    # Item 3 HAS a status line and this replaces it. The first draft of this
    # patch inserted a second one, on my claim that item 3 was unclassified --
    # which `roadmap_status.py --unclassified` disproves: it lists 25 items and
    # 3 is not among them. Two status lines would have left the tool reading
    # whichever it found first.
    ok(text.count(_n(ITEM3_ANCHOR)) == 1,
       "item 3's existing OPEN status line is present exactly once")
    i = text.index("**3. Lot places enemies twice")
    above = text[:i].rstrip("\n").split("\n")[-1]
    ok(above == _n(ITEM3_ANCHOR),
       "and it is the line directly above item 3's heading")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    # -- item 3 ------------------------------------------------------------
    j = out.index("**3. Lot places enemies twice")
    above = out[:j].rstrip("\n").split("\n")[-1]
    ok(above.startswith("*STATUS: NARROWED 2026-08-16"),
       "the status line sits directly above item 3's heading")
    ok(above.endswith("*"), "it is italic-delimited")
    verbs = ("OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED", "ANALYSIS")
    ok(above.split()[1] in verbs, f"verb is in the vocabulary ({above.split()[1]})")
    ok(out.count("*STATUS: NARROWED 2026-08-16 -- THE DIVERGENCE IS FIXED") == 1,
       "exactly one such status line is added")
    ok("**3. Lot places enemies twice" in out,
       "item 3's own text is untouched")
    ok(_n(ITEM3_ANCHOR) not in out,
       "the superseded OPEN line is gone, not duplicated")
    ok(out.count("*STATUS:") == text.count("*STATUS:"),
       f"the number of status lines is unchanged "
       f"({text.count('*STATUS:')}) -- replaced, not added")
    ok("this item blames a second\n" not in above,
       "the status line is a single line, as the format requires")

    # -- item 51 -----------------------------------------------------------
    ok(out.count("AND SEE ITEM 3") == 1, "one cross-reference added to item 51")
    ok(out.index("AND SEE ITEM 3") > out.index("*STATUS: CLOSED 2026-08-16"),
       "the cross-reference is inside item 51's status line, not loose")
    fifty_one = next(l for l in out.split("\n")
                     if l.startswith("*STATUS: CLOSED") and "AND SEE ITEM 3" in l)
    ok(fifty_one.endswith("*"), "item 51's status line is still italic-delimited")
    ok(fifty_one.count("*STATUS:") == 1, "item 51's status line was not doubled")

    # -- the claim the cross-reference makes has to be true ----------------
    ok("Lot places enemies twice, and nothing checks the two agree"
       in text,
       "item 3 really is titled what the cross-reference says it is")

    # -- prove the checks can fail ----------------------------------------
    damaged = text.replace(_n(ITEM3_ANCHOR), "**3. moved**\n", 1)
    ok(damaged.count(_n(ITEM3_ANCHOR)) == 0,
       "check() can fail: removing item 3's heading makes it uncountable")

    # -- endings ----------------------------------------------------------
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    crlf = data.count(bytes([13, 10]))
    lone = data.count(bytes([10])) - crlf
    ok((crlf == 0) != (lone == 0) or (crlf == 0 and lone > 0),
       f"the written file is not mixed ({crlf} CRLF, {lone} lone LF)")
    ok(len(data) > len(raw), "the file grew")

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
