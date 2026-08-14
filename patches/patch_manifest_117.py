r"""factory 1.17.0 -- the same code, under names that are finally accurate.

    python patch_manifest_117.py --check
    python patch_manifest_117.py
    python patch_manifest_117.py --selftest
    python patch_manifest_117.py --revert

Run from the FACTORY ROOT. Run it AFTER the five tool repos are committed and
tagged -- a pin naming a tag that does not exist is the failure this whole
sequence has been about.

WHAT MOVES

    dispatch        0.3.0   -> 0.3.1
    level_factory   0.24.0  -> 0.25.0
    pipeline        0.5.0   -> 0.6.0
    pixelcoat       0.11.0  -> 0.12.0
    zoo             0.32.0  -> 0.36.0
    factory_version 1.16.0  -> 1.17.0

THIS IS NOT A NEW CERTIFICATION OF BEHAVIOUR, AND SAYING SO IS THE POINT.
Four of those five tools shipped no new code today. `pixelcoat`'s eleven
commits, `zoo`'s seventeen, `dispatch`'s README edit and `pipeline`'s
guard-rail stamp were all committed BEFORE factory-v1.16.0 was cut, and were
already on disk when it was certified. What changed is that each now has a
VERSION and a CHANGELOG entry that names that code. The set being pinned is
the set that was already running.

`level_factory` 0.25.0 is the exception and the only new code in this bump:
`verify-manifest` reads the CHANGELOG as a third number.

Which makes 1.17.0 a bookkeeping release, and a certified set that does not
distinguish those from behaviour releases is telling its reader that
something was verified when nothing was.

THE MANIFEST DESCRIPTION IS NOT TOUCHED. It opens "Re-certified 2026-08-14,
on the art layer" and lists what was run -- the mission re-run and its 40 /
55 / 60 grades, the clean-project package test, the four engine-confirmed
shell fixes. All of that is still exactly as true and exactly as recent as it
was this morning, because nothing new was run since. Rewriting it to look
fresher would be the same lie in a different file.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_117"

PINS: dict[str, tuple[str, str]] = {
    "dispatch": ("0.3.0", "0.3.1"),
    "level_factory": ("0.24.0", "0.25.0"),
    "pipeline": ("0.5.0", "0.6.0"),
    "pixelcoat": ("0.11.0", "0.12.0"),
    "zoo": ("0.32.0", "0.36.0"),
}

OLD_FV, NEW_FV = "1.16.0", "1.17.0"

#: The 1.16.0 entry was inserted after this same preamble, so the newest
#: entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.17.0] - 2026-08-14

A bookkeeping release. Four of the five tools shipped no new code; they
finally have version numbers that name the code they were already running.

dispatch 0.3.0 -> 0.3.1, level_factory 0.24.0 -> 0.25.0, pipeline 0.5.0 ->
0.6.0, pixelcoat 0.11.0 -> 0.12.0, zoo 0.32.0 -> 0.36.0. deli_counter 0.89.0,
laser_tag 0.8.0, lot 0.41.0, lux 0.16.0 and patina 0.19.0 are unchanged from
factory-v1.16.0.

THE DISTINCTION THAT MATTERS HERE

`pixelcoat`'s eleven commits, `zoo`'s seventeen, `dispatch`'s README edit and
`pipeline`'s guard-rail stamp were all committed BEFORE factory-v1.16.0 was
cut. That code was on disk and inside the set when 1.16.0 was certified this
morning. Nothing about the running system changed between then and now.

What changed is that `verify-manifest` reported four tools STALE -- code
committed after the VERSION naming it -- so each got the version and the
CHANGELOG entry it was owed. The set being pinned is the set that was already
running, under names that are now accurate.

A certified set that does not separate bookkeeping from behaviour tells its
reader something was verified when nothing was. So: nothing new was verified
for this bump.

THE ONE PIECE OF NEW CODE

`level_factory` 0.25.0 teaches `verify-manifest` to read the CHANGELOG as a
third number, which 0.24.0's own entry had flagged as known and unaddressed.
Two statuses: UNRELEASED (the CHANGELOG ahead of VERSION) and UNDOCUMENTED
(VERSION ahead of the CHANGELOG), both outranking DRIFT, because a tool that
does not know its own version cannot be pinned by anyone.

It immediately found what it was built for -- `pipeline` documenting v0.1.0
against a VERSION of 0.5.0, five releases with no entries -- and it caught
its author twice inside an hour: once asserting `pipeline` would report
UNRELEASED when it reports UNDOCUMENTED, and once reporting `dispatch` as
disagreeing with itself because the first heading reader only understood
`## [0.3.0]` and dispatch writes `## v0.3.0`.

WHAT WAS RUN

Every patch's selftest, and level_factory 0.25.0's against the real factory:
eleven mechanism checks on fixtures that cannot drift, plus a live
`verify_manifest` over all ten tools. After this the run reads ten OK.

WHAT WAS NOT RUN

Everything engine-shaped. No mission re-run, no walk sweep, no pack load
check, no unit suites, since factory-v1.16.0 this morning. The evidence for
the SET is 1.16.0's evidence, unchanged, which is why the manifest
description still carries 1.16.0's date and is not rewritten here.

KNOWN FAILING, UNCHANGED FROM 1.16.0

`check_all` freshness still reports 57 buildings whose geometry no longer
matches the spec or builder that made them. Three demo shells still fail
nav_gate -- `cbp`, `night_pawn`, `primos_pizza` -- none of them in the
`lot_demo_001` draw.

ZOO JUMPED TO 0.36.0, AND WHY

`zoo`'s tags run to v0.35.0. Its VERSION had been reset backwards to 0.31.0
at some point, so every number written since was landing on history that
already existed. Today's release was drafted as 0.33.0 and `git tag` refused
it -- v0.33.0 has meant "Phase 1 structural species" since it was cut. The
refusal is the only reason this was noticed.

Worse, earlier the same day I had force-moved `v0.32.0` off `a944ccd`
("enriched kit index, missing-module gap report, slot-fit authority over
genome ranges") onto a CHANGELOG correction, having read it as a stale tag on
a bad entry. It was a real release, and a reset version number looks exactly
like a stale tag from the outside. The tag is restored to `a944ccd`; zoo's
work today is one release at 0.36.0, above everything; and the entry explains
the 0.32-0.35 gap rather than leaving a reader to assume the numbering is
arbitrary.

This also closes what factory-v1.16.0 recorded as unresolved -- that
factory-v1.3.0 reported "zoo 0.34.0 -> 0.35.0" while zoo's CHANGELOG had
never held a 0.33, 0.34 or 0.35 entry. It had held them. The entries were
lost in the reset; the tags survived.

STILL OPEN

`laser_tag` has no CHANGELOG at all. It is a Godot addon directory holding
VERSION and `addons/`, so it may never want one, but nothing has decided
that.

And two entries written today record what they could not establish rather
than filling it in: `pipeline` v0.6.0 names the 6 lines in
`building_configuration_registry.json` it did not read, and `zoo` 0.36.0
names the commit in its range -- `5bbe380`, "checkpoint: uncommitted working
tree" -- that says nothing about itself.

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


def _preflight(root: Path) -> int:
    """Refuse to pin a version the tool on disk does not claim.

    1.16.0 moved five pins to match five VERSION files and that was safe only
    because the VERSION files had already been fixed. Doing it in the other
    order writes a pin nothing supports, which is the exact failure this
    manifest exists to prevent.
    """
    bad = 0
    for tool, (_old, new) in PINS.items():
        d = root / tool
        v = version_of(d / "VERSION")
        c = newest_entry(d / "CHANGELOG.md")
        if v != new:
            print(f"REFUSING: {tool}/VERSION says {v}, not {new} -- run its "
                  f"patch first")
            bad = 1
        elif c is not None and c != new:
            print(f"REFUSING: {tool}'s newest CHANGELOG entry is {c}, not "
                  f"{new} -- the tool does not agree with itself yet")
            bad = 1
    return bad


def _apply(root: Path, *, check: bool) -> int:
    if _preflight(root):
        return 1

    mp, cp = root / MANIFEST, root / CHANGELOG
    mraw = mp.read_bytes()
    mbody = mraw.decode("utf-8")

    if f'"factory_version": "{NEW_FV}"' in mbody:
        print(f"  already applied  {MANIFEST}")
    else:
        out = mbody
        for tool, (old, new) in PINS.items():
            a = _pin_anchor(tool, old)
            if out.count(a) != 1:
                print(f"REFUSING: {tool} pin anchor occurs {out.count(a)} "
                      f"time(s), expected 1 (already {new}?)")
                return 1
            out = out.replace(a, _pin_anchor(tool, new), 1)
        fv = f'"factory_version": "{OLD_FV}"'
        if out.count(fv) != 1:
            print(f"REFUSING: factory_version {OLD_FV} occurs {out.count(fv)} "
                  f"time(s)")
            return 1
        out = out.replace(fv, f'"factory_version": "{NEW_FV}"', 1)

        try:
            data = json.loads(out)
        except ValueError as exc:
            print(f"REFUSING: the result is not valid JSON: {exc}")
            return 1
        for tool, (_o, new) in PINS.items():
            if data["tools"][tool]["version"] != new:
                print(f"REFUSING: {tool} reads "
                      f"{data['tools'][tool]['version']} after the edit")
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
    if "## [factory-v1.17.0]" in cbody:
        print(f"  already applied  {CHANGELOG}")
        return 0
    eol = _eol(cbody)
    a = _as(ANCHOR, eol)
    if cbody.count(a) != 1:
        print(f"REFUSING: the CHANGELOG preamble occurs {cbody.count(a)} "
              f"time(s), expected 1")
        return 1
    cout = cbody.replace(a, a + _as(ENTRY, eol), 1)
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

    for name, entry in sorted(data["tools"].items()):
        d = root / str(entry.get("path", name))
        pin, tag = entry.get("version"), entry.get("tag")
        v, c = version_of(d / "VERSION"), newest_entry(d / "CHANGELOG.md")
        check(f"{name:<14} tag {tag} matches pin", tag == f"v{pin}")
        if c is None:
            check(f"{name:<14} pin {pin} == VERSION {v} (no CHANGELOG)",
                  pin == v)
        else:
            check(f"{name:<14} pin {pin} == VERSION {v} == CHANGELOG {c}",
                  pin == v == c)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("one 1.17.0 entry", cl.count("## [factory-v1.17.0]") == 1)
    check("1.16.0 and the older entries survive",
          all(s in cl for s in ("## [factory-v1.16.0]", "## [factory-v1.3.0]",
                                "## [factory-v1.0.0]")))
    check("it is the newest entry",
          cl.index("factory-v1.17.0") < cl.index("factory-v1.16.0"))
    check("it says nothing new was verified",
          "nothing new was verified" in cl)
    check("it separates bookkeeping from behaviour",
          "bookkeeping" in cl and "BEFORE factory-v1.16.0" in cl)
    check("it explains zoo's jump to 0.36.0",
          "ZOO JUMPED TO 0.36.0" in cl and "a944ccd" in cl)
    check("it closes 1.16.0's unresolved zoo question",
          "It had held them" in cl)
    check("the description still carries 1.16.0's evidence, unrewritten",
          "Re-certified 2026-08-14" in data["description"]
          and "PRIOR CERTIFICATION, 2026-07-28" in data["description"])

    # The instrument's own verdict, if 0.25.0 is in.
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        results = contracts.verify_manifest(root)
        print()
        width = max(len(r.adapter_id) for r in results)
        for r in results:
            print(f"    {r.status:<13} {r.adapter_id:<{width}}  "
                  f"{r.message[:74]}")
        print(f"\n    worst: {contracts.worst_status(results)}")
        notok = [r.adapter_id for r in results if r.status != contracts.OK]
        check(f"every tool reads OK{'' if not notok else f' (not: {notok})'}",
              not notok)
    except Exception as exc:
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  the manifest and the ten tools tell the same story"
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
        print("    python patches\\patch_manifest_117.py --selftest")
        print('    git commit -am "factory 1.17.0 -- bookkeeping: five pins '
              'name the code already running"')
        print('    git tag -a factory-v1.17.0 -m "factory 1.17.0"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
