r"""Make VERSION and CHANGELOG agree in the three tools where they do not.

    python patch_version_reconcile.py --check
    python patch_version_reconcile.py
    python patch_version_reconcile.py --selftest
    python patch_version_reconcile.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHAT THE THREE NUMBERS ARE FOR. Every tool answers "what version is this?"
three times: the manifest pins what was CERTIFIED, `VERSION` names what the
code IS, and the CHANGELOG records what CHANGED. `verify-manifest` compares
the first two and, since 0.24.0, notices when either has outrun its commits.
It has never read the third -- 0.24.0's own entry says so: "the CHANGELOG is
a third number this does not read."

Reading it turns "five tools STALE" into five different problems:

    tool           manifest   VERSION   newest CHANGELOG
    deli_counter   0.88.0     0.89.0    0.89.0     pin behind, tool agrees
    dispatch       0.3.0      0.3.0     0.3.0      fine
    laser_tag      0.8.0      0.8.0     none       no CHANGELOG at all
    level_factory  0.22.0     0.24.0    0.24.0     pin behind, tool agrees
    lot            0.32.0     0.33.0    0.41.0     <- fixed here
    lux            0.15.4     0.16.0    0.16.0     pin behind, tool agrees
    patina         0.18.0     0.18.0    0.19.0     <- fixed here
    pipeline       0.5.0      0.5.0     0.1.0      four undocumented releases
    pixelcoat      0.11.0     0.11.0    0.11.0     fine
    zoo            0.32.0     0.32.0    0.31.0     <- fixed here

DISPATCH WAS NEVER BROKEN AND I REPORTED IT AS BROKEN. Its CHANGELOG heads
each entry `## v0.3.0 - 2026-07-11` rather than `## [0.3.0]`, and the first
pass matched only the bracketed form, so a tool in perfect agreement with
itself came back "VERSION != CHANGELOG". The heading reader here accepts both
shapes and the v-prefix. Worth stating because it is the same failure this
patch exists to fix: an instrument disagreeing with the thing it measures and
the instrument being wrong.

THREE FIXES, EACH READ OFF THE FILE RATHER THAN DECIDED.

`lot` -- CHANGELOG carries 0.33.0 through 0.41.0, nine consecutive entries,
each a paragraph of argument about a real change ("the walker could not climb
a legal stair"). VERSION says 0.33.0. Nothing was skipped and nothing was
written ahead: the entries were kept and VERSION stopped being bumped
alongside them. The CHANGELOG is the record, so VERSION follows it to 0.41.0.

`patina` -- the same shape, one step: CHANGELOG 0.19.0, VERSION 0.18.0.

`zoo` -- the interesting one, and no number needs inventing. Its CHANGELOG
opens with an entry sitting ABOVE the `# Changelog` title, numbered 0.31.0 --
and a SECOND `## [0.31.0]` follows the title. Two entries, one number, one of
them outside the document. VERSION says 0.32.0 and there is no 0.32.0 entry.
So the stray entry IS 0.32.0's: the three visual themes across the species
set, 205 tests green. It gets its right number and moves below the title.
That is a renumber and a move, not a rewrite.

WHAT IS DELIBERATELY LEFT ALONE. `pipeline` documents v0.1.0 while VERSION
says 0.5.0 -- four releases with no entry. There is nothing on disk that says
what changed in them, and inventing four entries would put fiction in the one
file whose job is to be the record. `laser_tag` has no CHANGELOG at all; it
is a Godot addon directory holding VERSION and `addons/`, so it may not want
one. Both need a person and their history, which is what
`tools/draft_version_bumps.py` is for.

THE MANIFEST PINS ARE ALSO LEFT ALONE, ON PURPOSE. Five of them are behind
their tools. Moving a pin is not bookkeeping -- it is the claim that THIS
combination was certified, and that claim is made by a run, not by an edit.
This patch only makes each tool agree with itself. Certifying the set is the
next decision, and a separate one.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

SIDECAR = ".pre_reconcile"

#: (file, old, new). Whole-line or whole-block anchors, one occurrence each.
EDITS: list[tuple[str, str, str]] = [
    ("lot/VERSION", "Lot 0.33.0", "Lot 0.41.0"),
    ("patina/VERSION", "Patina 0.18.0", "Patina 0.19.0"),
    ("zoo/CHANGELOG.md",
     "## [0.31.0] - Three visual themes across the species set\n"
     "\n"
     "- **center_city** (polished commercial: low wear, cooler/lighter, clean\n"
     "  materials) and **industrial_flats** (port/works: high wear, desaturated\n"
     "  iron tones, metal-first) join **delco** in every species genome (46) --\n"
     "  deterministic derivations of each species' anchor style, resolved through\n"
     "  the standard _pick_style_tag/resolve_module_plan path. 205 tests green.\n"
     "\n"
     "# Changelog\n"
     "\n",
     "# Changelog\n"
     "\n"
     "## [0.32.0] - Three visual themes across the species set\n"
     "\n"
     "- **center_city** (polished commercial: low wear, cooler/lighter, clean\n"
     "  materials) and **industrial_flats** (port/works: high wear, desaturated\n"
     "  iron tones, metal-first) join **delco** in every species genome (46) --\n"
     "  deterministic derivations of each species' anchor style, resolved through\n"
     "  the standard _pick_style_tag/resolve_module_plan path. 205 tests green.\n"
     "\n"),
]

#: Both heading shapes this repo uses: `## [0.19.0] - ...` and `## v0.3.0 - ...`
_HEADING = re.compile(r"^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?", re.M)

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor.

    `patina/VERSION` is CRLF and `lot/VERSION` is bare LF with no trailing
    newline at all, in the same operation.
    """
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def newest_entry(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = _HEADING.search(path.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def version_of(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"[0-9]+\.[0-9]+\.[0-9]+",
                  path.read_text(encoding="utf-8", errors="replace"))
    return m.group(0) if m else None


def _apply(root: Path, *, check: bool) -> int:
    rc = 0
    for rel, old, new in EDITS:
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            rc = 1
            continue
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        eol = _eol(body)
        o, n = _as(old, eol), _as(new, eol)

        if n in body:
            print(f"  already applied  {rel}")
            continue
        count = body.count(o)
        if count != 1:
            print(f"REFUSING: {rel} -- the anchor occurs {count} time(s), "
                  f"expected 1")
            rc = 1
            continue

        out = body.replace(o, n, 1)
        data = out.encode("utf-8")
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return rc


def selftest(root: Path) -> int:
    """Check the OUTCOME -- that each tool now agrees with itself."""
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    for tool in ("lot", "patina", "zoo"):
        v = version_of(root / tool / "VERSION")
        c = newest_entry(root / tool / "CHANGELOG.md")
        check(f"{tool:<9} VERSION {v} == newest entry {c}", v == c and v)

    z = (root / "zoo/CHANGELOG.md").read_text(encoding="utf-8")
    check("zoo: the title is the first line",
          z.lstrip().startswith("# Changelog"))
    check("zoo: exactly one 0.32.0 entry", z.count("## [0.32.0]") == 1)
    check("zoo: exactly one 0.31.0 entry", z.count("## [0.31.0]") == 1)
    check("zoo: the moved entry kept its body",
          "205 tests green." in z and "industrial_flats" in z)
    check("zoo: nothing else lost", len(z) > 44_000)

    lot = (root / "lot/CHANGELOG.md").read_text(encoding="utf-8")
    check("lot: 0.33.0 through 0.41.0 are all still there",
          all(f"## [0.{n}.0]" in lot for n in range(33, 42)))

    # The tools this patch does NOT touch must be unchanged.
    for tool, want in (("dispatch", "0.3.0"), ("pixelcoat", "0.11.0")):
        v = version_of(root / tool / "VERSION")
        c = newest_entry(root / tool / "CHANGELOG.md")
        check(f"{tool:<9} still agrees at {want}", v == c == want)

    print()
    print("  every tool this touches now agrees with itself"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def report(root: Path) -> int:
    """The three numbers, side by side, for all ten tools."""
    import json
    man = json.loads((root / "factory.manifest.json").read_text(
        encoding="utf-8"))
    print(f"\n  factory_version {man.get('factory_version')}\n")
    print(f"  {'tool':<15}{'manifest':<11}{'VERSION':<11}{'CHANGELOG':<11}")
    print("  " + "-" * 55)
    for name in sorted(man.get("tools", {})):
        e = man["tools"][name]
        d = root / str(e.get("path", name))
        v = version_of(d / "VERSION") or "-"
        c = newest_entry(d / "CHANGELOG.md") or "-"
        pin = e.get("version", "-")
        note = ("" if pin == v == c else
                "tool disagrees with itself" if v != c and c != "-" else
                "no CHANGELOG" if c == "-" else
                "pin behind")
        print(f"  {name:<15}{pin:<11}{v:<11}{c:<11} {note}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--report" in argv:
        return report(root)
    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel, _o, _n in EDITS:
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
        print("  Each tool now agrees with itself. Commit and tag INSIDE each:")
        print('    git -C lot    commit -am "0.41.0 -- VERSION follows the '
              'CHANGELOG"   && git -C lot tag v0.41.0')
        print('    git -C patina commit -am "0.19.0 -- VERSION follows the '
              'CHANGELOG"   && git -C patina tag v0.19.0')
        print('    git -C zoo    commit -am "0.32.0 -- the stray entry gets '
              'its number"  && git -C zoo tag v0.32.0')
        print()
        print("  Then: python patches\\patch_version_reconcile.py --report")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
