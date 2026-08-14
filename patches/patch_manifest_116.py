r"""factory 1.16.0 -- the pins catch up to the tools they name.

    python patch_manifest_116.py --check
    python patch_manifest_116.py
    python patch_manifest_116.py --selftest
    python patch_manifest_116.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHAT MOVES. Five pins and the factory version:

    deli_counter    0.88.0  -> 0.89.0
    level_factory   0.22.0  -> 0.24.0
    lot             0.32.0  -> 0.41.0
    lux             0.15.4  -> 0.16.0
    patina          0.18.0  -> 0.19.0
    factory_version 1.15.0  -> 1.16.0

`dispatch` 0.3.0, `pipeline` 0.5.0, `pixelcoat` 0.11.0, `zoo` 0.32.0 and
`laser_tag` 0.8.0 are already correct and are not touched.

A PIN IS A CLAIM, SO THE ENTRY SAYS WHAT WAS ACTUALLY RUN. Moving a pin
asserts that this combination was verified together. The honest version of
that claim, for 2026-08-14, includes what was NOT run and what is known to be
failing, and both go in the CHANGELOG entry rather than being left for
someone to discover. A set recorded as clean when a check reports 57 findings
is the same failure as a VERSION that outran its commits.

THE MANIFEST DESCRIPTION IS PREPENDED, NOT REPLACED. It currently opens
"Re-certified 2026-07-28" and then runs 2,000 words of evidence for that set:
the anchor/marker distinction, seed 5017's stuck walker, seventeen of twenty
sites re-walked. That is a real record and overwriting it would delete
history to make the top of the file current. The new certification goes in
front and the old text is kept behind a PRIOR CERTIFICATION marker.

TWO THINGS RECORDED AS UNRESOLVED, BECAUSE THEY ARE.

The factory CHANGELOG's newest entry is `factory-v1.3.0` while
`factory_version` says 1.15.0 -- twelve certified sets with no entry. This
adds a thirteenth on top of that hole rather than inventing twelve.

And `factory-v1.3.0` records "zoo 0.34.0 -> 0.35.0". Zoo's own CHANGELOG has
never contained a 0.33, 0.34 or 0.35 entry; before today its newest was
0.31.0, written twice. Either zoo was renumbered, its entries were lost, or
the factory entry named versions that never shipped. Nothing on disk says
which, so the entry says that rather than guessing.

THE EDIT IS VALIDATED AS JSON BEFORE IT IS WRITTEN. `json.loads` on the
result, same role `compile()` plays for the .py patches -- a manifest that
does not parse takes every tool with it.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_116"

#: tool -> (old, new). Both `version` and `tag` move together.
PINS: dict[str, tuple[str, str]] = {
    "deli_counter": ("0.88.0", "0.89.0"),
    "level_factory": ("0.22.0", "0.24.0"),
    "lot": ("0.32.0", "0.41.0"),
    "lux": ("0.15.4", "0.16.0"),
    "patina": ("0.18.0", "0.19.0"),
}

OLD_FV, NEW_FV = "1.15.0", "1.16.0"

#: Prepended to the manifest description. No double quotes -- this lands
#: inside a JSON string literal.
DESC_OLD = ('"description": "The certified lockstep set: these tool versions '
            'were verified TOGETHER. Re-certified 2026-07-28.')

DESC_NEW = (
    '"description": "The certified lockstep set: these tool versions were '
    'verified TOGETHER. Re-certified 2026-08-14, on the art layer. What was '
    'run: the mission re-ran end to end and graded its three candidates 40 / '
    '55 / 60, selecting lot_demo_001.candidate.seed_5219; check_all reports '
    'gdscript, stairs and steps clean; the portable package opened in a clean '
    'Godot project with zero plugins, zero autoloads and zero external '
    'references, 18.6 MB across 212 entries; four deli_counter shell fixes '
    'were engine-confirmed, taking nav_gate from 7 of 135 shells failing to '
    '3. What was NOT run and is therefore not covered by this set: the walk '
    'sweep (library_walk, needs Godot, about an hour for 20 sites), the pack '
    'load check, and the lot and deli_counter unit suites. What is known '
    'failing: check_all freshness reports 57 buildings whose geometry no '
    'longer matches the spec or builder that made them, and three demo shells '
    '-- cbp, night_pawn and primos_pizza -- still fail nav_gate; none of the '
    'three is in the lot_demo_001 draw, and cbp fails on a first floor '
    'fragmented across 63 islands rather than on the stair geometry the other '
    'fixes addressed. PRIOR CERTIFICATION, 2026-07-28:')

ENTRY = """## [factory-v1.16.0] - 2026-08-14

The art layer, certified, and the pins catch up to the tools they name.

deli_counter 0.88.0 -> 0.89.0, level_factory 0.22.0 -> 0.24.0, lot 0.32.0 ->
0.41.0, lux 0.15.4 -> 0.16.0, patina 0.18.0 -> 0.19.0. dispatch 0.3.0,
pipeline 0.5.0, pixelcoat 0.11.0, zoo 0.32.0 and laser_tag 0.8.0 were already
correct.

Four of those five pins were behind because VERSION moved and nothing moved
the pin. `lot` is the exception and the interesting one: its CHANGELOG
carried nine consecutive entries from 0.33.0 to 0.41.0 while its VERSION file
still said 0.33.0 and this manifest pinned 0.32.0 -- three different answers
to one question, none of them agreeing. `patch_version_reconcile.py` made
each tool agree with itself first; this makes the manifest agree with them.

WHAT WAS RUN FOR THIS CERTIFICATION

- The mission re-ran end to end on the themed draw and graded its three
  candidates 40 / 55 / 60, selecting `lot_demo_001.candidate.seed_5219`.
  That re-run overturned SESSION_0811's conclusion that the Laser Tag score
  was a plateau: the plateau was an artifact of grading the greybox draw
  while the themed draw shipped.
- `check_all`: gdscript clean, stairs clean, steps clean.
- The portable package opened in a clean Godot project -- zero plugins, zero
  autoloads, zero external references, 18.6 MB across 212 entries.
- Four deli_counter shell fixes engine-confirmed, taking nav_gate from 7 of
  135 shells failing to 3.

WHAT WAS NOT RUN, AND IS THEREFORE NOT COVERED

The walk sweep (`library_walk.py`, needs Godot, about an hour for 20 sites),
the pack load check, and the `lot` and `deli_counter` unit suites. A set that
does not say what it skipped reads as a set that skipped nothing.

WHAT IS KNOWN FAILING

- `check_all` freshness: 57 buildings whose geometry no longer matches the
  spec or builder that made them.
- Three demo shells still fail nav_gate: `cbp`, `night_pawn`, `primos_pizza`.
  None is in the `lot_demo_001` draw. `cbp` is not the same defect as the
  four that were fixed -- its first floor fragments across 63 islands, 32 of
  them 2 polygons or fewer, so no stair fix reaches it.

UNRESOLVED, AND RECORDED RATHER THAN PINNED PAST

This entry sits directly on top of `factory-v1.3.0`. Twelve certified sets
between them have no entry at all -- 1.4 through 1.15 were pinned without
being written down. They are not reconstructed here; there is nothing on disk
to reconstruct them from, and inventing twelve entries would put fiction in
the file whose only job is to be the record.

And `factory-v1.3.0` records "zoo 0.34.0 -> 0.35.0". Zoo's own CHANGELOG has
never contained a 0.33.0, 0.34.0 or 0.35.0 entry; before 2026-08-14 its
newest was 0.31.0, and that number appeared twice. Either zoo was renumbered
downward at some point, its entries were lost, or that line named versions
that never shipped. Nothing on disk says which, so this says so instead of
choosing.

"""

_CRLF = "\r\n"


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pin_anchor(tool: str, ver: str) -> str:
    """The tool's version+tag pair, which is unique in the file."""
    return (f'"{tool}": {{\n      "version": "{ver}",\n'
            f'      "tag": "v{ver}",')


def newest_entry(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?",
                  path.read_text(encoding="utf-8", errors="replace"), re.M)
    return m.group(1) if m else None


def version_of(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"[0-9]+\.[0-9]+\.[0-9]+",
                  path.read_text(encoding="utf-8", errors="replace"))
    return m.group(0) if m else None


def _apply(root: Path, *, check: bool) -> int:
    mp, cp = root / MANIFEST, root / CHANGELOG
    if not mp.is_file():
        print(f"REFUSING: no {MANIFEST} here")
        return 1

    mraw = mp.read_bytes()
    mbody = mraw.decode("utf-8")

    if f'"factory_version": "{NEW_FV}"' in mbody:
        print("  already applied  factory.manifest.json")
    else:
        out = mbody
        for tool, (old, new) in PINS.items():
            a = _pin_anchor(tool, old)
            if out.count(a) != 1:
                print(f"REFUSING: {tool} pin anchor occurs "
                      f"{out.count(a)} time(s), expected 1 "
                      f"(is it already {new}?)")
                return 1
            out = out.replace(a, _pin_anchor(tool, new), 1)

        fv = f'"factory_version": "{OLD_FV}"'
        if out.count(fv) != 1:
            print(f"REFUSING: factory_version {OLD_FV} occurs "
                  f"{out.count(fv)} time(s)")
            return 1
        out = out.replace(fv, f'"factory_version": "{NEW_FV}"', 1)

        if out.count(DESC_OLD) != 1:
            print("REFUSING: the description does not open as expected")
            return 1
        out = out.replace(DESC_OLD, DESC_NEW, 1)

        # A manifest that does not parse takes every tool with it.
        try:
            data = json.loads(out)
        except ValueError as exc:
            print(f"REFUSING: the result is not valid JSON: {exc}")
            return 1
        for tool, (_o, new) in PINS.items():
            got = data["tools"][tool]["version"]
            if got != new:
                print(f"REFUSING: {tool} reads {got} after the edit, "
                      f"wanted {new}")
                return 1

        blob = out.encode("utf-8")
        if check:
            print(f"  would patch  {MANIFEST}  {len(mraw):,} -> {len(blob):,} "
                  f"bytes ({len(blob) - len(mraw):+,})")
        else:
            side = mp.with_suffix(mp.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(mraw)
            mp.write_bytes(blob)
            print(f"  patched      {MANIFEST}  {len(mraw):,} -> {len(blob):,} "
                  f"bytes  sha256 {_sha(blob)[:16]}")

    craw = cp.read_bytes()
    cbody = craw.decode("utf-8")
    if "## [factory-v1.16.0]" in cbody:
        print("  already applied  CHANGELOG.md")
        return 0
    eol = _eol(cbody)
    head, _sep, tail = cbody.partition(
        _as("own CHANGELOG.\n\n", eol))
    if not _sep:
        print("REFUSING: cannot find the CHANGELOG preamble to insert after")
        return 1
    cout = head + _sep + _as(ENTRY, eol) + tail
    cblob = cout.encode("utf-8")
    if check:
        print(f"  would patch  {CHANGELOG}  {len(craw):,} -> {len(cblob):,} "
              f"bytes ({len(cblob) - len(craw):+,})")
        return 0
    side = cp.with_suffix(cp.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(craw)
    cp.write_bytes(cblob)
    print(f"  patched      {CHANGELOG}  {len(craw):,} -> {len(cblob):,} bytes "
          f"({len(cblob) - len(craw):+,})  sha256 {_sha(cblob)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    check(f"factory_version is {NEW_FV}",
          data.get("factory_version") == NEW_FV)

    # THE REAL POST-CONDITION: all three numbers agree, per tool, on disk.
    for name, entry in sorted(data["tools"].items()):
        d = root / str(entry.get("path", name))
        pin = entry.get("version")
        tag = entry.get("tag")
        v = version_of(d / "VERSION")
        c = newest_entry(d / "CHANGELOG.md")
        check(f"{name:<14} tag matches pin ({tag})", tag == f"v{pin}")
        if name == "pipeline":
            check(f"{name:<14} pin {pin} == VERSION {v} "
                  f"(CHANGELOG {c} known behind)", pin == v)
        elif c is None:
            check(f"{name:<14} pin {pin} == VERSION {v} (no CHANGELOG)",
                  pin == v)
        else:
            check(f"{name:<14} pin {pin} == VERSION {v} == CHANGELOG {c}",
                  pin == v == c)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("CHANGELOG has exactly one 1.16.0 entry",
          cl.count("## [factory-v1.16.0]") == 1)
    check("the older entries survived",
          "## [factory-v1.3.0]" in cl and "## [factory-v1.0.0]" in cl)
    check("the entry says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "library_walk" in cl)
    check("the entry says what is known failing",
          "57 buildings" in cl and "primos_pizza" in cl)
    check("the description kept the prior certification",
          "PRIOR CERTIFICATION, 2026-07-28" in data["description"]
          and "seed 5017" in data["description"])

    print()
    print("  the manifest and the tools tell the same story"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / MANIFEST).is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (MANIFEST, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  Verify against the tools, then commit HERE (the manifest is")
        print("  the factory's own file, not a tool's):")
        print("    python patches\\patch_manifest_116.py --selftest")
        print("    python patches\\patch_version_reconcile.py --report")
        print('    git commit -am "factory 1.16.0 -- pins catch up to the '
              'tools they name"')
        print("    git tag factory-v1.16.0 && git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
