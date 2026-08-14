r"""Put PIPELINE_MAP.md's DAG table under factory_map.py's control.

    python patch_map_generated_block.py --check
    python patch_map_generated_block.py
    python patch_map_generated_block.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

THE DOC A NEW READER IS TOLD TO READ FIRST IS WRONG. `README.md` points at
`PIPELINE_MAP.md` as "start here", and its DAG table is hand-typed. Measured
just now by `factory_map.py --check`:

    15 stages planned; 2 named nowhere in PIPELINE_MAP.md
      ABSENT  walktest_navqa
      ABSENT  themed_site_assemble

And the sentence introducing the table says:

    "Graybox runs per candidate; everything below the gate runs once, on the
     selected candidate only."

That is false and has been since the kit fan-out. The planner's own graph says
4 stages run per candidate, 6 per archetype, 5 once per mission -- six stages
below the gate run per BUILDING, not once. Every art defect found between
2026-08-06 and 2026-08-09 was a stage computing at a coarser scope than the
thing it described, so a reader who believes this sentence is being aimed at
the exact class of bug this repo keeps finding.

WHAT THIS DOES. Replaces the hand-written table with the block
`factory_map.py` generates, markers included. After this, `factory_map.py
--check` compares the doc against the planner and exits 1 on drift, and
`--write` regenerates it. The table stops being a document and becomes a
measurement.

THE BLOCK IS COMPUTED, NOT COPIED. This patch imports `factory_map` and calls
`generated()` at apply time, so what lands in the doc is what the planner says
at the moment you run it -- not a table I transcribed off a screenshot. If the
import fails, the patch refuses rather than writing something stale.

`factory_map.py` runs its own `--selftest` before generating, asserting stage
scopes and fan-out counts against the planner, so a derivation that has gone
wrong stops this patch instead of quietly rewriting the doc.

AFTER APPLYING, WIRE IT INTO THE GATE. `factory_map.py --check` is worth a
line in whatever runs before a commit here, for the same reason
`build_freshness.py` was worth wiring into `check.py`: an instrument nobody
runs is a document with extra steps.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("PIPELINE_MAP.md")
SIDECAR = ".pre_dagblock"

#: The false sentence, and its replacement. Kept deliberately short -- the
#: generated block's own summary line carries the real counts, so this only
#: has to stop asserting the wrong thing.
OLD_INTRO = """Defined in `packages/pipeline/planner.py::plan_mission`. Graybox runs per
candidate; everything below the gate runs once, on the selected candidate only."""

NEW_INTRO = """Defined in `packages/pipeline/planner.py::plan_mission`, and the table below
is DERIVED FROM IT by `factory_map.py` rather than typed -- run
`python factory_map.py --check` to prove the doc still matches the planner,
and `--write` to regenerate it after a planner change.

Read the **Scope** column. Graybox stages run per candidate, but "everything
below the gate runs once" is NOT true and has not been since the kit fan-out:
six stages below the gate run once per BUILDING. Every art defect found
between 2026-08-06 and 2026-08-09 was a stage computing at a coarser scope
than the thing it described."""

#: The table span, replaced wholesale. Both ends must be unique.
TABLE_FIRST = "| Stage | Adapter | Resource | Depends on | Expected outputs |"
TABLE_LAST_PREFIX = "| `dispatch_handoff` |"

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _block(root: Path) -> str:
    """The generated markdown, from factory_map itself."""
    sys.path.insert(0, str(root))
    try:
        import factory_map
    except ImportError as exc:
        raise SystemExit(
            f"cannot import factory_map from {root}: {exc}\n"
            f"  it must sit in the factory root next to level_factory/")
    if factory_map._selftest():
        raise SystemExit("factory_map's selftest failed -- the derivation is "
                         "wrong, so the table it would write is not a "
                         "measurement. Fix that before running this.")
    return factory_map.generated()


def _rewrite(body: str, block: str) -> str:
    eol = _eol(body)
    lines = body.split(eol)

    firsts = [i for i, ln in enumerate(lines) if ln.strip() == TABLE_FIRST]
    lasts = [i for i, ln in enumerate(lines)
             if ln.startswith(TABLE_LAST_PREFIX)]
    if len(firsts) != 1 or len(lasts) != 1:
        raise SystemExit(f"REFUSING: expected one table header and one "
                         f"dispatch_handoff row; found {len(firsts)} and "
                         f"{len(lasts)}.")
    a, b = firsts[0], lasts[0]
    if b <= a:
        raise SystemExit("REFUSING: the dispatch_handoff row sits above the "
                         "table header -- this is not the table I expect.")

    out = lines[:a] + _as(block, eol).split(eol) + lines[b + 1:]
    return eol.join(out)


def main(argv: list[str]) -> int:
    root = Path.cwd()
    path = root / TARGET
    if not path.is_file():
        raise SystemExit(f"cannot find {TARGET} under {root} -- run from the "
                         f"factory root")
    side = path.with_suffix(path.suffix + SIDECAR)

    if "--revert" in argv:
        if not side.is_file():
            print(f"  no sidecar for {path.name}")
            return 1
        path.write_bytes(side.read_bytes())
        print(f"  reverted     {path.name}")
        return 0

    raw = path.read_bytes()
    body = raw.decode("utf-8")

    if "BEGIN GENERATED: factory_map.py" in body:
        print("  already applied  PIPELINE_MAP.md has a generated block")
        print("  from here on use: python factory_map.py --check | --write")
        return 0

    block = _block(root)
    out = _rewrite(body, block)

    eol = _eol(body)
    if OLD_INTRO.replace("\n", eol) in out:
        out = out.replace(OLD_INTRO.replace("\n", eol),
                          NEW_INTRO.replace("\n", eol), 1)
    else:
        print("  NOTE: the intro sentence was not found unchanged, so it was "
              "left alone.\n  Worth reading it yourself -- it claimed "
              "everything below the gate runs once.")

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: the edit would leave {bare} bare LF line(s) in a "
              f"CRLF document.")
        return 1

    if "--check" in argv:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        print(f"  the generated block carries "
              f"{block.count(chr(10) + '| `')} stage row(s)")
        return 0

    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    print()
    print("  now prove it holds:  python factory_map.py --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
