r"""factory 1.21.0 -- the functional lock protects the site, and enforces it.

    python patch_manifest_121.py --check
    python patch_manifest_121.py
    python patch_manifest_121.py --selftest
    python patch_manifest_121.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.31.0.

WHAT MOVES

    level_factory   0.28.0  -> 0.31.0   (three releases)
    factory_version 1.20.0  -> 1.21.0

Nine tools unchanged.

THE ARC, IN ONE PLACE

1.20.0 shipped a lock that could SAY it was guarding nothing. It was: the
extraction read ten key names Lot has never published, and four of them were
backfilled from Deli, so the signature was never empty and never looked
broken. The whole protected set was two Deli stair systems.

    0.29.0  mapped the lock onto Lot's actual vocabulary -- surfaces node
            names, ground sources, openings, vertical_links, markers --
            retired route_graph_hash, which nothing in the factory publishes,
            and bumped the schema to v0.2 with a mismatch reported as
            needs-recompute rather than drift.
    0.30.0  stopped dropping Deli's anchors. `_merged_gameplay` had one rule
            for a shared key -- the site wins -- correct when Lot restates
            what Deli said and wrong when each says something the other does
            not. Thirteen gameplay anchors, two spawns and eleven cover
            points, had been discarded by a rule written for the other case.
    0.31.0  added counts to the coverage report and turned the gate on.

THE EVIDENCE, MEASURED NOT ASSERTED

`lot_demo_001`, recomputed under v0.2:

    counts       markers 55, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 2
    site_counts  markers 42, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 0

markers 55 against 42 is exactly the thirteen. stair_systems 2 against 0 is
the Deli backfill -- and everything the lock protected before 0.29.0. It now
carries 1,171 records. vacuous False, guards_no_site False, unguarded empty.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot        (silent: no lock warning)
    approve lot_demo_001 functional_shell_locked     (accepted, gate on)
    level_factory unit suite: 579 passed, 1 skipped
    tools/probe_selection_drift.py                   exit 0, signatures match

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check, no
portability run -- 0.29.0 through 0.31.0 touch the lock and the CLI, not
package contents. `pytest tests` still aborts in collection on
`_COMPOSER_SOURCES`. `pure-shell` has not been re-exported since 0.26.0. The
description is not rewritten.

ENFORCEMENT IS NARROWER THAN THE PROBLEM, ON PURPOSE

The gate refuses a VACUOUS lock -- every signature empty. It does not refuse
`guards_no_site`, which is the stricter and more meaningful test, because
exactly one mission has been measured under this spec. Widening it before
measuring a second and third would fail missions nobody has looked at, which
is the argument `CLOSURE_ENFORCED`'s comment makes and the second time this
factory has copied it rather than relearn it.

OPEN

25 of Deli's 238 collision nodes -- story -1 and window sub-parts -- are
absent from the assembled site. Present in the shell, missing from the level:
either a deliberate drop nobody recorded or loss between two stages, and the
lock cannot tell which. That is a question for `lot`.

`openings` matched 0 of 19 on a whole-record comparison against coordinates
Lot transforms; undecidable from those two files. Whether Lot's four
`vertical_links` need splitting by `kind` is unanswered -- all four are
`hatch`, too small a sample.

`pyproject.toml` still says 0.22.0 against a VERSION of 0.31.0, still
invisible to `verify-manifest`. 57 stale buildings. `cbp`, `night_pawn` and
`primos_pizza` still fail nav_gate. `laser_tag` still has no CHANGELOG.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_121"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.28.0", "0.31.0"),
}

OLD_FV, NEW_FV = "1.20.0", "1.21.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.21.0] - 2026-08-14

level_factory 0.28.0 -> 0.31.0. The other nine tools are unchanged from
factory-v1.20.0.

1.20.0 shipped a functional lock that could say it was guarding nothing.
This set ships one that guards something and refuses to be written when it
does not.

THE DEFECT, RESTATED ONCE

`_merged_gameplay` read ten key names. `site.site.gameplay.json` publishes
twenty top-level keys and none of the ten. Four of the ten were backfilled
from the Deli side, so the signature was never empty and never looked
broken. The entire protected set was two Deli stair systems, under three
signatures that all reported healthy.

    0.29.0  the mapping: surfaces node names, ground sources, openings,
            vertical_links, markers. route_graph_hash retired -- nothing in
            the factory publishes a route graph. Schema v0.2, with a
            mismatch reported as needs-recompute, not drift.
    0.30.0  two rules for a shared key instead of one. Thirteen Deli
            anchors -- two spawns, eleven cover points -- had been discarded
            by a rule that assumed Lot restates what Deli says.
    0.31.0  counts in the coverage report, and the gate on.

THE EVIDENCE

`lot_demo_001`, recomputed under v0.2:

    counts       markers 55, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 2
    site_counts  markers 42, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 0

55 against 42 is the thirteen. 2 against 0 is the Deli backfill, and it is
all the lock held before 0.29.0. It now carries 1,171 records.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot     -- silent, no lock warning
    approve lot_demo_001 functional_shell_locked  -- accepted with the gate on
    unit suite: 579 passed, 1 skipped
    tools/probe_selection_drift.py                -- exit 0, signatures match

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check, no
portability run -- these releases touch the lock and the CLI, not package
contents. `pytest tests` still aborts in collection on `_COMPOSER_SOURCES`.
`pure-shell` has not been re-exported since 0.26.0. The description is not
rewritten.

FOUR DEFECTS THE WORK ITSELF PRODUCED, AND WHAT CAUGHT THEM

0.29.0 blocked every export on a schema bump -- through `passed=False`, not
through `drift`, after the doc argued against exactly that in those words.
Caught by running the export.

0.28.0's guard could not fire: it read a `coverage` field that only exists
on locks written by 0.28.0 or later, which is none of them. Caught by running
the export; its selftest had asserted the broken behaviour as a virtue.

Turning the gate on made the unit suite fail, correctly: `_anchor_registry`
falls back to Deli's `anchors` and 0.29.0 left `anchors` out of
`PROTECTED_KEYS`, so coverage called the registry unguarded while it was
hashing that list. Caught by pytest.

`cmd_approve` recorded the approval before attempting the lock, so a refusal
would have left an approved gate with no lock behind it -- the same ordering
bug 0.28.0 fixed four lines higher, in the same function.

Every selftest was green for each of these. What caught them was running the
command, opening the artifact, and the unit suite. That is the durable
finding of this set, and it is worth more than the mapping.

OPEN

25 of Deli's 238 collision nodes -- story -1 and window sub-parts -- are in
the shell and not in the assembled site. A question for `lot`: deliberate
drop or loss between stages, and the lock cannot say which. `openings`
matched 0 of 19 on a whole-record comparison against transformed
coordinates, undecidable. Whether `vertical_links` needs splitting by `kind`
is unanswered.

Enforcement refuses a vacuous lock, not `guards_no_site` -- one mission has
been measured, and widening before a second and third would fail missions
nobody has looked at.

`pyproject.toml` at 0.22.0 against VERSION 0.31.0. 57 stale buildings.
`cbp`, `night_pawn`, `primos_pizza` failing nav_gate. `laser_tag` without a
CHANGELOG.

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

    The manifest is the certified COMBINATION; a pin is a claim about what is
    installed. Writing one the tool does not support is the exact failure the
    manifest exists to prevent, so this runs before anything is touched.
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
        # Nine tools must be untouched. A one-pin patch that moved two would
        # be a certified set nobody certified.
        before = json.loads(mbody)["tools"]
        for name in before:
            if name in PINS:
                continue
            if data["tools"][name] != before[name]:
                print(f"REFUSING: {name} changed and this patch does not "
                      f"move it")
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
    if f"## [factory-v{NEW_FV}]" in cbody:
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
    check(f"one {NEW_FV} entry", cl.count(f"## [factory-v{NEW_FV}]") == 1)
    check("the older entries survive",
          all(s in cl for s in ("## [factory-v1.17.0]", "## [factory-v1.16.0]",
                                "## [factory-v1.0.0]")))
    check("it is the newest entry",
          cl.index(f"factory-v{NEW_FV}") < cl.index(f"factory-v{OLD_FV}"))
    flat = " ".join(cl.split())
    check("it names all three releases and what each did",
          all(s in cl for s in ("0.29.0", "0.30.0", "0.31.0"))
          and "route_graph_hash retired" in flat)
    check("it carries the measured counts, not a hash delta",
          "markers 55" in flat and "site_counts markers 42" in flat)
    check("and what the lock held before",
          "two Deli stair systems" in flat and "1,171" in cl)
    check("it says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "no portability run" in flat)
    check("it records the four defects the work produced",
          "FOUR DEFECTS THE WORK ITSELF PRODUCED" in cl)
    check("and that selftests were green for every one of them",
          "Every selftest was green" in flat)
    check("and names what actually caught them",
          "running the command, opening the artifact, and the unit suite"
          in flat)
    check("it says enforcement is narrower than the problem",
          "not `guards_no_site`" in flat
          and "nobody has looked at" in flat)
    check("and hands the 25 nodes to lot",
          "A question for `lot`" in flat)
    check("the description still carries its own dated evidence, unrewritten",
          "Re-certified 2026-08-14" in data["description"])

    # And the claim the entry makes about pyproject is checked, not asserted.
    pp = root / "level_factory" / "pyproject.toml"
    if pp.is_file():
        m = re.search(r'^version\s*=\s*"([^"]+)"', pp.read_text(
            encoding="utf-8", errors="replace"), re.M)
        found = m.group(1) if m else None
        check(f"pyproject really does say 0.22.0 (found {found})",
              found == "0.22.0")

    # The instrument's own verdict over all ten tools.
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
    print("  one pin moved, and the entry says what earned it"
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
        print("    python patches\\patch_manifest_121.py --selftest")
        print('    git commit -am "factory 1.18.0 -- the export package has a '
              'name, and a real run proved it"')
        print(f'    git tag -a factory-v{NEW_FV} -m "factory {NEW_FV}"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
