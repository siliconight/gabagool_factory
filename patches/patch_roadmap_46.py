r"""Roadmap item 46 -- the destructible declaration.

    python patch_roadmap_46.py --check
    python patch_roadmap_46.py
    python patch_roadmap_46.py --selftest
    python patch_roadmap_46.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools/roadmap_status.py --write

From `Replicated_Destructible_Proxy_Breakable_Glass`. The question it was
raised with -- whether this can live in tools that deliberately do not
overstep into authoritative gameplay, server, netcode or backend -- has a
clean answer, and the source document draws the line itself: "The shards are
not the glass. The state is the glass."

The factory can own the shards, the declaration and the assets, and never
touch the state.

The item exists to hold two things that are easy to lose: that Deli Counter
already emits `breach_class` and `material` on all 76 openings and both are
null, so the vocabulary is half-built; and that a destructible with two
collision states has no answer yet in FUNCTIONAL_LOCK.md, which protects one.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r46"

OLD_42 = None
INSERT = '''*STATUS: OPEN 2026-08-14 -- specified by `Replicated_Destructible_Proxy_Breakable_Glass`; the declaration vocabulary already exists in Deli Counter's openings and is null on all 76. BLOCKED on one question: a destructible has two collision states and the functional lock protects one*

**46. The destructible declaration, not the destructible system.**
A window needs a very small server-authoritative representation -- an id and
`INTACT`/`BROKEN`, with collision on or off. Everything expensive is local:
mesh swap, authored fracture pattern, shards, particles, short-lived debris
physics that nobody replicates.

The source document draws this pipeline's boundary better than the boundary
statement does:

> The shards are not the glass. The state is the glass.

**What stays downstream, and it is most of the networking.** Server validates
the hit. Server owns and replicates persistent state. Late joiners get "this
pane is already broken" and never the original impact event. The transient
`BreakGlass(id, impact, direction, seed)` is the runtime's to send. Every one
of those is named in `HANDOFF_LANGUAGE` already -- "the production game
runtime remains authoritative for mission progression, gameplay behavior,
enemy AI, replication, persistence, late joining, reconnection, and online
correctness."

**What the factory owns is everything that has to exist before any of that
can run:**

- **The declaration.** A stable id per destructible, its state set, and a
  named collision representation per state. Shell metadata, the same shape as
  a gameplay anchor. Dispatch already ships "runtime integration
  requirements"; this is one more requirement, not an implementation.
- **Both collision states as authored geometry.** The intact collider and
  whatever remains once it is broken. The runtime toggles; it does not
  author.
- **The fracture library.** `BreakPattern_01..06` is a Zoo asset family with
  `collision_policy: none`, and the broken-frame mesh is another. Pixelcoat
  skins them. Same machinery as item 44.
- **The presentation tiers.** Mesh-swap / authored fracture / rich shards is
  `quality_tier`, which item 45's dressing manifest already proposes.
- **The packaging split.** Dispatch puts the declaration on the gameplay side
  and every shard under the presentation branch, where it can be culled
  whole.

THE VOCABULARY IS HALF-BUILT AND NOBODY HAS NOTICED

Deli Counter already emits this on all 76 openings of `lot_demo_001`:

```json
{"kind": "door", "breach_class": null, "material": null,
 "reinforceable": false, "vaultable": false, "wall": "ext_0_N",
 "width": 1.8, "height": 2.2, "sill": 0.0, "story": 0}
```

`breach_class` is a breakability classification that exists, is emitted on
every opening, and is read by nothing. `material` is null too -- and material
is what decides whether a thing shatters, splinters or dents. This is
considerably cheaper than it looks, because the first pass is populating
fields that are already in the contract rather than adding any.

**And the gate is already in place.** Since level_factory 0.29.0 the
functional lock hashes `openings` WHOLE, `breach_class` and `reinforceable`
included. The moment those are populated, changing one is drift on a real
comparison. Nothing needs building for that.

BLOCKING QUESTION, AND IT COMES BEFORE CODE

**Two collision states, one hash.** If `BROKEN` disables or replaces a
collider, an object has two collision representations and the lock protects
exactly one. Which one is the locked shell -- intact, or the worst case, or
both as a set? `docs/FUNCTIONAL_LOCK.md` has no answer today, and the answer
belongs in that document before a destructible enters a locked shell rather
than after. A shell whose collision is conditional is a different kind of
object from the one that document was written about.

DO NOT BAKE THE SEED

`pattern = hash(glass_id + break_seed) % pattern_count`. `break_seed` is a
per-break runtime value. The factory ships the pattern library and the
selection RULE; if it ships a chosen pattern, every window in every session
breaks the same way. Everything else in this pipeline is
deterministic-from-a-seed and that instinct will pull the wrong way exactly
once, here.

GENERALISE IT, PER THE SOURCE

Window, door, fence, light, crate, monitor. Each keeps a simple authoritative
state and collision representation; the art layer makes the transition look
complicated. Build it as a Replicated Destructible Proxy declaration rather
than a glass feature, or the second destructible re-opens the contract.

'''

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor.

    PIPELINE_ROADMAP.md is CRLF while every file under level_factory/ is LF,
    and `Path.read_text()` normalises newlines -- so a check written with
    read_text reports a CRLF file as LF and an LF-only patch then refuses a
    file it could have handled. That is how this patch was written the first
    time.
    """
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

    out = body
    done = 0

    anchor = _as("\n### Not to be worked on\n", eol)
    if _as("**46. The destructible declaration", eol) in out:
        done += 1
    elif out.count(anchor) == 1:
        out = out.replace(
            anchor, _as("\n" + INSERT + "### Not to be worked on\n", eol), 1)
    else:
        print(f"REFUSING: the 'Not to be worked on' heading occurs "
              f"{out.count(anchor)} time(s), expected 1")
        return 1

    if done == 1:
        print(f"  already applied  {ROADMAP}")
        return 0

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

    check("item 46 is present", "**46. The destructible declaration" in md)
    i46 = md.index("**46. The destructible declaration")
    before = md[:i46].rstrip().splitlines()[-1]
    check("it carries a STATUS line directly above it",
          before.startswith("*STATUS: ") and before.endswith("*"))
    check("the numbering is contiguous through 46",
          [int(m) for m in re.findall(r"^\*\*(\d+)\. ", md, re.M)][-5:]
          == [42, 43, 44, 45, 46])

    check("it quotes the principle that draws the boundary",
          "The shards are not the glass" in md)
    check("and cites the handoff language rather than paraphrasing it",
          "replication, persistence, late joining, reconnection" in flat)
    # `flat` on both halves. The fifth assertion this session to fail on a
    # line wrap rather than on substance; prose in a markdown file wraps.
    check("it keeps validation and replication downstream",
          "Server validates the hit" in flat
          and "runtime's to send" in flat)
    check("it names what the factory owns instead",
          "The declaration." in md and "The fracture library." in md
          and "The packaging split." in md)

    check("THE EVIDENCE: breach_class exists and is null",
          "breach_class" in md and "read by nothing" in flat)
    check("and that material is null too, which decides the break",
          "shatters, splinters or dents" in flat)
    check("it says the lock already covers those fields",
          "hashes `openings` WHOLE" in md)

    check("THE BLOCKING QUESTION is named and scoped to the doc",
          "Two collision states, one hash" in md
          and "FUNCTIONAL_LOCK.md` has no answer today" in md)
    check("and it says the answer comes before the code",
          "before a destructible enters a locked shell" in flat)
    check("the seed caution is there",
          "DO NOT BAKE THE SEED" in md and "break_seed" in md)
    check("and it says why this pipeline will get it wrong",
          "pull the wrong way exactly once" in flat)
    check("it generalises past glass",
          "Window, door, fence, light, crate, monitor" in md)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  one item, one blocking question, and no netcode in it"
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
        print("    python patches\\patch_roadmap_46.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
        print()
        print("  the table at the top is DERIVED -- it will not show 46")
        print("  until --write regenerates it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
