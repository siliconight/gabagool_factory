r"""Roadmap item 46, rewritten against the thing itself.

    python patch_roadmap_46_measured.py --check
    python patch_roadmap_46_measured.py
    python patch_roadmap_46_measured.py --selftest
    python patch_roadmap_46_measured.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools/roadmap_status.py --write

WHY

I wrote item 46 saying the declaration vocabulary was "half-built" and that
the first pass was populating `breach_class` and `material`. Both statements
were made from a partial copy of `deli_counter` that the device bridge served
me -- `interactives.py` and `docs/INTERACTIVES.md` were absent from my tree
and present on disk, 9,867 and 7,041 bytes.

The declaration is not half-built. It is finished, documented, and generated
on every run. `docs/INTERACTIVES.md` opens with the exact boundary the
question was asked about -- "The contract describes STATE, never
SYNCHRONIZATION ... Deli Counter must never emit a field that tells the
netcode HOW to replicate" -- and `window -> [intact, broken]` on
`breakable: true` is the breakable-glass case, already inferred.

WHAT IS ACTUALLY WRONG, MEASURED IN THREE PLACES

    deli_generate  shell.gameplay.json   "interactives": 9   per building
    lot_assemble   site.site.gameplay.json   no `interactives` key at all
    the package    LF_lot_demo_001_...zip    0 files mention "interactive"

Five buildings, roughly forty-five replicable state machines, generated every
run and reaching nobody. `INTERACTIVES.md` says the game reads them to
replicate state; the package does not contain them.

The item now says that, and the work it names is a boundary rather than a
design.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r46m"

_CRLF = "\r\n"

START = "*STATUS: OPEN 2026-08-14 -- specified by `Replicated_Destructible_Proxy"
END = "### Not to be worked on"

NEW = '''*STATUS: NARROWED 2026-08-14 -- MEASURED, and the scope inverted. The declaration is not missing; it is finished and dropped. `deli_counter/interactives.py` + `docs/INTERACTIVES.md` emit 9 replicable state machines per building. `site.site.gameplay.json` has no `interactives` key. The shipped package contains zero files mentioning "interactive". The work is a boundary, not a design*

**46. Forty-five state machines a run, reaching nobody.**
The question this started from -- can a destructible system live in tools that
deliberately do not overstep into authoritative gameplay, netcode or backend
-- was answered before it was asked. `deli_counter/docs/INTERACTIVES.md`:

> **The contract describes STATE, never SYNCHRONIZATION.** It says *what* is
> interactive, *what discrete states* it can be in, and *what named
> transitions* move between them. It says **nothing** about who is
> authoritative, how state replicates, tick rate, or interpolation.
>
> Deli Counter must never emit a field that tells the netcode *how* to
> replicate.

That is the boundary, written down and implemented. `Replicated Destructible
Proxy` describes a system whose declaration layer this factory already
builds.

WHAT DELI COUNTER ALREADY EMITS

Every interactive fixture is `(stable_id, states[], default, transitions[])`
-- the entire networked surface -- and the doc's own table shows it mapping
onto snapshot, event/RPC, lockstep and rollback without committing to any:

```json
{ "id": "primos_pizza:if:2cf6a380", "kind": "breach_wall",
  "slot_ref": "ext_0_N_open1",
  "states": ["intact", "breached"], "default": "intact",
  "transitions": [{"event": "breach", "from": "intact", "to": "breached"}],
  "reversible": false, "source": "inferred" }
```

Inference covers the cases without any authoring: `door`/`garage` ->
`[closed, open]`, `breach` -> `[intact, breached]`, `vault` -> `[locked,
unlocked, open, breached]`, `teller` -> `[intact, shattered]`, `safe_deposit`
-> `[intact, drilled]`. A `window` opts in with `breakable: true` and becomes
`[intact, broken]` -- which is the breakable-glass case from the source
document, already built.

**Ids are derived from place, never from an array index** --
`sha1(building, wall, story, kind, round(pos, 4))` -- because openings are
re-sorted by position during the geometry pass and an index would renumber.
Moving an opening changes its id, which is correct: it is a new place.

**And the two-collision-states question already has an answer at this layer.**
`<building>.slots.json` carries `collision_per_state: {"intact": true,
"breached": false}` beside `state_geometry: {"intact": "wall", "breached":
"breach"}`. DC says which states collide. What it does not say is which of
them the FUNCTIONAL LOCK protects, and that question is still open (below).

THE MEASUREMENT

```
deli_generate  shell.gameplay.json       "interactives": 9    per building
lot_assemble   site.site.gameplay.json   no `interactives` key
the package    LF_lot_demo_001_*.zip     0 files mention "interactive"
```

The package's only gameplay file is `gameplay_anchors.json`, carrying
`anchors, dispatch_version, mission_id, schema`. `INTERACTIVES.md` says the
game reads the `interactives` array to replicate state. It never arrives.

**Same shape as the thirteen dropped markers**, and found the same way: Lot
assembles from Deli's shells and carries forward what it restates, and
`interactives` is not in that set. This one is worse because there is no
partial overlap to argue about -- the key is simply absent.

THE WORK

1. **Lot carries `interactives` into the assembled site**, namespaced per
   building the way markers are. Ids are already globally unique
   (`<building>:if:<hash>`), so this is a concatenation, not a merge.
2. **Dispatch ships them** beside `gameplay_anchors.json` -- gameplay side of
   the packaging split, not presentation. They ARE the netcode's input.
3. **The lock protects them.** `interactives` becomes a protected key, so an
   art pass that changes which fixtures exist or what states they have is
   drift. Every mechanism for this exists as of level_factory 0.31.0; it is
   one entry in `PROTECTED_KEYS` once the key is present.
4. **Then, and only then, `breach_class` and `material`.** Both are still
   null on all 76 openings and read by nothing. They are real gaps -- material
   is what decides whether a thing shatters, splinters or dents -- but
   populating them before the pipe is connected is decorating a disconnected
   pipe.

STILL OPEN, AND IT BLOCKS STEP 3

**Two collision states, one hash.** `collision_per_state` says a breached
wall does not collide. The functional lock hashes one collision fingerprint.
Which state is the locked shell -- default, worst case, or every state as a
set? `docs/FUNCTIONAL_LOCK.md` has no answer, and a shell whose collision is
conditional is a different kind of object from the one that document
describes. Answer it there before `interactives` enters the protected set.

**And `INTERACTIVES.md` says its twin lives in the zoo repo** -- "the same
file lives in the **zoo** repo -- keep them in sync." Nothing checks that they
are. Two copies of a contract with no comparison between them is the shape of
every other defect in this file.

'''


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    if _as("**46. Forty-five state machines a run", eol) in body:
        print(f"  already applied  {ROADMAP}")
        return 0

    start = _as(START, eol)
    end = _as(END, eol)
    if body.count(start) != 1:
        print(f"REFUSING: item 46's original status line occurs "
              f"{body.count(start)} time(s), expected 1 -- run "
              f"patch_roadmap_46.py first")
        return 1
    if body.count(end) != 1:
        print(f"REFUSING: the 'Not to be worked on' heading occurs "
              f"{body.count(end)} time(s), expected 1")
        return 1
    i, j = body.index(start), body.index(end)
    if j < i:
        print("REFUSING: item 46 is not the last item; this replaces the "
              "block between it and 'Not to be worked on'")
        return 1

    out = body[:i] + _as(NEW, eol) + body[j:]
    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import re
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    disk = (root / ROADMAP).read_bytes().decode("utf-8")
    check("the file's line endings are preserved",
          disk.count(_CRLF) > 0 or "\r" not in disk)
    md = disk.replace(_CRLF, "\n")
    flat = " ".join(md.split())

    check("item 46 is the measured one now",
          "**46. Forty-five state machines a run" in md)
    check("and the wrong claim is gone",
          "the declaration vocabulary already exists" not in flat
          and "half-built" not in flat)
    i46 = md.index("**46. Forty-five state machines")
    before = md[:i46].rstrip().splitlines()[-1]
    check("it carries a STATUS line directly above it",
          before.startswith("*STATUS: ") and before.endswith("*"))
    check("the status is NARROWED, not OPEN -- the scope changed",
          before.startswith("*STATUS: NARROWED"))
    check("numbering still runs to 46",
          [int(m) for m in re.findall(r"^\*\*(\d+)\. ", md, re.M)][-2:]
          == [45, 46])

    check("it quotes the contract's own boundary statement",
          "describes STATE, never SYNCHRONIZATION" in flat)
    # Blockquote markers survive the whitespace collapse -- "... *how* to >
    # replicate" -- so strip them first. Sixth assertion this session to trip
    # on typography instead of substance.
    quoted = " ".join(md.replace("\n> ", "\n").split())
    check("and that DC must not say HOW to replicate",
          "tells the netcode *how* to replicate" in quoted)
    check("it carries the three measurements",
          '"interactives": 9' in md
          and "no `interactives` key" in md
          and '0 files mention "interactive"' in md)
    check("it names the package's only gameplay file",
          "gameplay_anchors.json" in md and "dispatch_version" in md)
    check("it names the breakable-glass case as already inferred",
          "breakable: true" in md and "[intact, broken]" in md)
    check("it records that ids come from place, not an index",
          "never from an array index" in flat)
    check("it says collision_per_state already answers half the question",
          "collision_per_state" in md)
    check("the work is four ordered steps",
          "1. **Lot carries" in md and "4. **Then, and only then" in md)
    check("and breach_class is demoted to step 4",
          "decorating a disconnected pipe" in flat)
    check("the lock question is still named as blocking",
          "Two collision states, one hash" in md
          and "before `interactives` enters the protected set" in flat)
    check("and the zoo twin is flagged as uncompared",
          "lives in the **zoo** repo" in md and "Nothing checks that they" in
          flat.replace("  ", " "))

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  the item now says what was measured, and what it costs to be wrong"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {ROADMAP}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {ROADMAP}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_roadmap_46_measured.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
