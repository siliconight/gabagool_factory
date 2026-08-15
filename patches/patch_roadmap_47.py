r"""Roadmap item 47 -- Lux out of the art pass.

    python patch_roadmap_47.py --check
    python patch_roadmap_47.py
    python patch_roadmap_47.py --selftest
    python patch_roadmap_47.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools/roadmap_status.py --write

WHY IT IS WRITTEN DOWN NOW, BEFORE ANY WORK

Raised in conversation and not worked. That is exactly the reason: nothing in
a conversation survives, and this factory spent a day learning that a claim
which lives only in someone's memory is a claim nobody can check. Asked
whether we had discussed this before, I could not tell -- the earlier part of
that session had been compacted away and the answer was not in the record.

The item is small on purpose. It states the goal, the three places the seam
is already half-cut, and the four questions that want answers before code.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r47"

OLD_42 = None
INSERT = '''*STATUS: OPEN 2026-08-14 -- raised, not worked. The seam is already half-cut in three places: `_PRESENTATION_FILES` names Lux's two outputs by hand, `pure-shell` drops them, and `lux_strategy` is already a choice. What is missing is a third strategy value and a split of LAYER_ART*

**47. A recipient with their own lighting has to take ours or take graybox.**
The goal, stated plainly: a Level Factory package that had a FULL art pass,
where including Lux is a choice. Another team may have their own lighting
system and still want the kits, the materials and the wear.

Today there are two useful answers and neither is that one:

```
portable-godot   everything, Lux included
pure-shell       functional geometry + collision only -- the whole art pass
                 goes with it
```

**The seam is already named, by hand, in `export.py`:**

```python
# Files that carry presentation only (dropped in pure-shell mode).
_PRESENTATION_FILES = {"lux.applied.tscn", "lux.quality.json"}
```

Those two files are Lux's output and nothing else's. Somebody has already
written down where lighting ends -- it is just wired to a mode that also
throws away Zoo, Pixelcoat and Patina.

**The bundling is one level up.** `--art` is described in the CLI as "add the
Art layer (Zoo/Pixelcoat/Patina/Lux)" -- one layer, four tools. Three of them
do SURFACE work a recipient keeps. The fourth does lighting they replace.
Splitting that is most of the item.

**And `lux_strategy` is already a choice with the wrong options.**
`localized` copies the minimal Lux runtime into the package; `baked` writes
presentation to vertex/lightmap data so no Lux runtime is needed. Neither
serves a studio with its own lighting: baked light data is still OUR lighting
decisions welded into their level. The missing value is a third one -- ship
the art, ship no light.

FOUR QUESTIONS, AND THEY WANT ANSWERS BEFORE CODE

1. **Absent or ignorable?** Does "no Lux" mean the lightmaps are not in the
   package, or present and safely ignored? Absent is smaller and honest;
   ignorable lets a recipient A/B ours against theirs. They are different
   products.
2. **Do the light ANCHORS ship anyway?** Lot derives where lights were
   intended to go. A team bringing its own lighting still probably wants that
   -- it is level design intent, not a lighting solution. Item 38 is about
   those anchors hanging below the slab, so they are real data with a known
   history.
3. **What is the entry scene?** `write_entry_scene` makes a graybox export's
   entry `site.tscn` and a lit export's entry the presentation scene. An
   art-pass-without-Lux package has a composed root and no
   `lux.applied.tscn`. Nothing decides that case today.
4. **A fourth layer, a sub-flag on `--art`, or a third export mode?** All
   three work. A mode is the cheapest to package and the most visible in the
   name; a layer is the most honest about what actually ran. Decide before
   building, because the answer changes what `--force` re-runs.

WHAT IS ALREADY PAID FOR

A third profile costs nothing in naming. `export_build_dir_name` and the
archive grammar both carry the profile (level_factory 0.26.0 and 0.27.0), so
`LF_<mission>.art-unlit/` coexists with the other two in one workspace by
construction, and the archive says which one it is. That was not true a day
before this was written.

**But the closure scan and the portability test have never seen this mode.**
`CLOSURE_ENFORCED`'s comment is the precedent: a mode nobody has scanned gets
scanned before it gets enforced, and the first run that scans it is expected
to find something.

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
    if _as("**47. A recipient with their own lighting", eol) in out:
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

    check("item 47 is present", "**47. A recipient with their own lighting" in md)
    i47 = md.index("**47. A recipient with their own lighting")
    before = md[:i47].rstrip().splitlines()[-1]
    check("it carries a STATUS line directly above it",
          before.startswith("*STATUS: ") and before.endswith("*"))
    check("the status says raised, not worked",
          "raised, not worked" in before)
    check("the numbering is contiguous through 47",
          [int(m) for m in re.findall(r"^\*\*(\d+)\. ", md, re.M)][-3:]
          == [45, 46, 47])

    check("it states the goal in one sentence",
          "including Lux is a choice" in flat)
    check("it names the two modes that exist and why neither fits",
          "portable-godot" in md and "pure-shell" in md
          and "the whole art pass" in flat)
    check("it quotes the seam that is already cut",
          "_PRESENTATION_FILES" in md
          and "lux.applied.tscn" in md and "lux.quality.json" in md)
    check("it names the bundling one level up",
          "Zoo/Pixelcoat/Patina/Lux" in md and "one layer, four tools" in flat)
    check("it says why `baked` is not the answer",
          "welded into their level" in flat)
    check("all four questions are there",
          "1. **Absent or ignorable?**" in md
          and "2. **Do the light ANCHORS ship anyway?**" in md
          and "3. **What is the entry scene?**" in md
          and "4. **A fourth layer" in md)
    check("the anchors question is tied to a real item",
          "Item 38" in md)
    check("it says the naming already supports a third profile",
          "0.26.0 and 0.27.0" in md and "art-unlit" in md)
    check("and that the new mode has never been scanned",
          "CLOSURE_ENFORCED" in md and "gets scanned before it gets enforced"
          in flat)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  written down before it is worked, which is the point"
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
        print("    python patches\\patch_roadmap_47.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
        print()
        print("  the table at the top is DERIVED -- it will not show 47")
        print("  until --write regenerates it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
