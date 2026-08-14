r"""level_factory 0.25.0 -- verify-manifest reads the third number.

    python patch_lf_025.py --check
    python patch_lf_025.py
    python patch_lf_025.py --selftest    (run it AFTER applying)
    python patch_lf_025.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHY. 0.24.0's own entry closes with this:

    KNOWN AND NOT ADDRESSED HERE: the CHANGELOG is a third number this does
    not read. `lot`'s CHANGELOG documents 0.41.0 while its VERSION says
    0.33.0 and the manifest pins 0.32.0 -- three answers to one question, and
    this check compares two of them.

It was right, and on 2026-08-14 finding out cost twenty staged files and a
person reading them. The check reported `lot` as STALE -- true, and the least
interesting true thing about it. Meanwhile `zoo` shipped 0.32.0 with no entry
for it, and its CHANGELOG carried the number 0.31.0 twice, once above the
document title. Neither was visible to an instrument comparing a pin to a
VERSION file.

TWO NEW STATUSES, BECAUSE THERE ARE TWO FAILURES AND THEY WANT OPPOSITE FIXES.

    UNRELEASED     the CHANGELOG is AHEAD of VERSION. Entries exist for
                   versions the tool never claimed to be. `lot`: nine
                   consecutive entries, 0.33.0 through 0.41.0, against a
                   VERSION file reading 0.33.0. The record is right and
                   VERSION should follow it.

    UNDOCUMENTED   VERSION is AHEAD of the CHANGELOG. A release with no
                   entry. `zoo` before this session: VERSION 0.32.0, newest
                   entry 0.31.0. The version is right and the record owes an
                   entry.

Collapsing both into one status would produce a message that cannot tell you
which file to edit, which is most of what a status is for.

IT IS CHECKED FIRST, AND NOT ONLY FROM OK -- WHICH IS THE OPPOSITE OF STALE.
STALE escalates only from OK on the argument that if the numbers already
disagree, DRIFT's message is more useful. That argument does not survive
contact with `lot`: it was DRIFT (pin 0.32.0, VERSION 0.33.0), and DRIFT says
"re-run the smoke and re-certify", which would have pinned 0.33.0 -- a number
that was wrong by eight releases. A tool that does not know its own version
cannot be pinned at all, so that finding has to outrank the pin being behind.

Severity gains two ranks between DRIFT and INCOMPATIBLE:

    OK 0 < UNKNOWN 1 < STALE 2 < DRIFT 3 < UNDOCUMENTED 4
       < UNRELEASED 4 < INCOMPATIBLE 5

BOTH HEADING SHAPES ARE READ, BECAUSE BOTH ARE IN USE. `patina` writes
`## [0.19.0] - 2026-08-02`, `dispatch` writes `## v0.3.0 - 2026-07-11`, and
`pipeline` writes `## [v0.1.0] - 2026-07-17`. A reader that accepted only the
bracketed form reported `dispatch` -- a tool in perfect agreement with itself
-- as disagreeing, on the first pass of this work. An instrument that
misreads the record is the failure it was built to catch.

NO CHANGELOG MEANS NO OPINION. `laser_tag` is a Godot addon directory holding
`VERSION` and `addons/`; it has no CHANGELOG and may never want one. A missing
file yields None and the tool is judged on the two numbers it does have, the
same way a missing version degrades to UNKNOWN rather than a false OK.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_025"

CONTRACTS = "level_factory/packages/tools/contracts.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"

OLD_V, NEW_V = "0.24.0", "0.25.0"

EDITS: list[tuple[str, str, str]] = [

    # ------------------------------------------------- statuses + severity --
    (CONTRACTS,
     '#: The pin matches the VERSION file, and the VERSION file is older than the\n'
     '#: code it names. Sits below DRIFT because the numbers still agree -- what has\n'
     '#: gone stale is the claim that the number means anything.\n'
     'STALE = "STALE"\n'
     '_SEVERITY = {OK: 0, UNKNOWN: 1, STALE: 2, DRIFT: 3, INCOMPATIBLE: 4}\n',

     '#: The pin matches the VERSION file, and the VERSION file is older than the\n'
     '#: code it names. Sits below DRIFT because the numbers still agree -- what has\n'
     '#: gone stale is the claim that the number means anything.\n'
     'STALE = "STALE"\n'
     '#: The CHANGELOG documents versions the tool never claimed to be -- entries\n'
     '#: exist above what VERSION says. `lot` carried nine of them, 0.33.0 through\n'
     '#: 0.41.0, against a VERSION file reading 0.33.0. The record is right; VERSION\n'
     '#: should follow it.\n'
     'UNRELEASED = "UNRELEASED"\n'
     '#: A release with no entry -- VERSION is ahead of the newest heading. `zoo`\n'
     '#: shipped 0.32.0 while its CHANGELOG still stopped at 0.31.0. The version is\n'
     '#: right; the record owes an entry.\n'
     'UNDOCUMENTED = "UNDOCUMENTED"\n'
     '#: Both outrank DRIFT. A pin being behind has an obvious fix; a tool that does\n'
     '#: not know its own version cannot be pinned at all, so it has to be the\n'
     '#: louder finding. `lot` was DRIFT and STALE and neither said the useful\n'
     '#: thing.\n'
     '_SEVERITY = {OK: 0, UNKNOWN: 1, STALE: 2, DRIFT: 3, UNDOCUMENTED: 4,\n'
     '             UNRELEASED: 4, INCOMPATIBLE: 5}\n'),

    # --------------------------------------------------- ContractResult field --
    (CONTRACTS,
     '    #: For STALE: the newest source file that outran VERSION. Naming it is the\n'
     '    #: difference between a verdict and a place to look.\n'
     '    stale_because: str | None = None\n',

     '    #: For STALE: the newest source file that outran VERSION. Naming it is the\n'
     '    #: difference between a verdict and a place to look.\n'
     '    stale_because: str | None = None\n'
     '    #: The version in the newest CHANGELOG heading. None when the tool has no\n'
     '    #: CHANGELOG, which is not a finding -- see `newest_changelog_entry`.\n'
     '    documented: str | None = None\n'),

    (CONTRACTS,
     '            "certified_from": self.source,\n'
     '            "stale_because": self.stale_because,\n'
     '        }\n',

     '            "certified_from": self.source,\n'
     '            "stale_because": self.stale_because,\n'
     '            "documented": self.documented,\n'
     '        }\n'),

    # --------------------------------------------------------------- messages --
    (CONTRACTS,
     '        if self.status == DRIFT:\n'
     '            return (f"installed {self.installed} != certified {self.certified} "\n'
     '                    f"(same major) — re-run the real-tool smoke and re-certify")\n',

     '        if self.status == UNRELEASED:\n'
     '            return (f"the CHANGELOG documents {self.documented} but VERSION "\n'
     '                    f"says {self.installed} -- the record is ahead of the "\n'
     '                    f"version; bump VERSION to follow it, then re-pin")\n'
     '        if self.status == UNDOCUMENTED:\n'
     '            return (f"VERSION says {self.installed} but the newest CHANGELOG "\n'
     '                    f"entry is {self.documented} -- this release has no "\n'
     '                    f"entry; write one")\n'
     '        if self.status == DRIFT:\n'
     '            return (f"installed {self.installed} != certified {self.certified} "\n'
     '                    f"(same major) — re-run the real-tool smoke and re-certify")\n'),

    # ------------------------------------------------------- the new readers --
    (CONTRACTS,
     'def stale_source(tool_dir) -> str | None:\n',

     'def newest_changelog_entry(tool_dir) -> str | None:\n'
     '    """The version in the newest CHANGELOG heading, or None.\n'
     '\n'
     '    BOTH SHAPES IN USE HERE ARE ACCEPTED. `patina` writes `## [0.19.0] -\n'
     '    2026-08-02`, `dispatch` writes `## v0.3.0 - 2026-07-11`, `pipeline`\n'
     '    writes `## [v0.1.0] - 2026-07-17`. A reader that took only the bracketed\n'
     '    form reported `dispatch` -- a tool in perfect agreement with itself -- as\n'
     '    disagreeing. An instrument that misreads the record is the failure this\n'
     '    module exists to catch.\n'
     '\n'
     '    NEWEST MEANS FIRST, NOT HIGHEST. These files are written newest-first and\n'
     '    the top entry is the claim being made. Taking the maximum instead would\n'
     '    have hidden `zoo`, whose stray entry sat ABOVE the document title with a\n'
     '    number already used further down.\n'
     '\n'
     '    ``None`` when there is no CHANGELOG or no heading in it. That is not a\n'
     '    finding: `laser_tag` is an addon directory holding VERSION and addons/,\n'
     '    and may never want one. A missing file means no opinion, the same way a\n'
     '    missing version degrades to UNKNOWN rather than to a false OK.\n'
     '    """\n'
     '    from pathlib import Path as _P\n'
     '    p = _P(str(tool_dir)) / "CHANGELOG.md"\n'
     '    try:\n'
     '        text = p.read_text(encoding="utf-8", errors="replace")\n'
     '    except OSError:\n'
     '        return None\n'
     '    m = re.search(r"^##\\s*\\[?v?(\\d+\\.\\d+\\.\\d+)\\]?", text, re.M)\n'
     '    return m.group(1) if m else None\n'
     '\n'
     '\n'
     'def self_disagreement(installed: str | None,\n'
     '                      documented: str | None) -> str | None:\n'
     '    """UNRELEASED, UNDOCUMENTED, or None -- does the tool agree with itself?\n'
     '\n'
     '    Compares the two numbers the TOOL owns. The manifest pin is not involved:\n'
     '    a tool that does not know its own version cannot be pinned correctly by\n'
     '    anyone, so this is answerable without asking what was certified.\n'
     '    """\n'
     '    i, d = parse_semver(installed), parse_semver(documented)\n'
     '    if i is None or d is None or i == d:\n'
     '        return None\n'
     '    return UNDOCUMENTED if i > d else UNRELEASED\n'
     '\n'
     '\n'
     'def stale_source(tool_dir) -> str | None:\n'),

    # ------------------------------------------------------- verify_manifest --
    (CONTRACTS,
     '        status = compare(pinned, installed.get(name))\n'
     '        because = None\n'
     '        if status == OK:\n'
     '            # ONLY from OK. If the numbers already disagree the staleness\n'
     '            # question is moot, and DRIFT\'s message is the more useful one.\n'
     '            from pathlib import Path as _P\n'
     '            tool_dir = _P(str(factory_root)) / str(\n'
     '                manifest["tools"][name].get("path", name))\n'
     '            because = stale_source(tool_dir)\n'
     '            if because:\n'
     '                status = STALE\n'
     '        results.append(ContractResult(\n'
     '            adapter_id=name,\n'
     '            certified=pinned,\n'
     '            installed=installed.get(name),\n'
     '            status=status,\n'
     '            source="factory.manifest",\n'
     '            stale_because=because,\n'
     '        ))\n',

     '        from pathlib import Path as _P\n'
     '        tool_dir = _P(str(factory_root)) / str(\n'
     '            manifest["tools"][name].get("path", name))\n'
     '        status = compare(pinned, installed.get(name))\n'
     '        because = None\n'
     '        documented = newest_changelog_entry(tool_dir)\n'
     '\n'
     '        # THE THIRD NUMBER IS CHECKED FIRST, AND NOT ONLY FROM OK -- which\n'
     '        # is the opposite of how STALE is reached, on purpose. STALE\n'
     '        # escalates only from OK because if the numbers already disagree,\n'
     '        # DRIFT\'s message is more useful. That does not survive `lot`: it\n'
     '        # was DRIFT (pin 0.32.0, VERSION 0.33.0), and DRIFT says "re-run the\n'
     '        # smoke and re-certify" -- which would have pinned 0.33.0, wrong by\n'
     '        # eight releases, while its CHANGELOG said 0.41.0. A tool that does\n'
     '        # not know its own version cannot be pinned, so that has to outrank\n'
     '        # the pin being behind.\n'
     '        disagreement = self_disagreement(installed.get(name), documented)\n'
     '        if disagreement:\n'
     '            status = disagreement\n'
     '        elif status == OK:\n'
     '            because = stale_source(tool_dir)\n'
     '            if because:\n'
     '                status = STALE\n'
     '        results.append(ContractResult(\n'
     '            adapter_id=name,\n'
     '            certified=pinned,\n'
     '            installed=installed.get(name),\n'
     '            status=status,\n'
     '            source="factory.manifest",\n'
     '            stale_because=because,\n'
     '            documented=documented,\n'
     '        ))\n'),

    # ------------------------------------------------------------ exit codes --
    (COMMANDS,
     '    if worst == getattr(contracts, "STALE", "STALE"):\n'
     '        # A pin that matches a VERSION file older than its own code is not a\n'
     '        # pass. Same exit treatment as DRIFT, because it wants the same thing\n'
     '        # doing: bump the tool, then re-certify the set.\n'
     '        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS\n',

     '    if worst in (getattr(contracts, "UNRELEASED", "UNRELEASED"),\n'
     '                 getattr(contracts, "UNDOCUMENTED", "UNDOCUMENTED")):\n'
     '        # The tool disagrees with ITSELF -- its CHANGELOG and its VERSION name\n'
     '        # different releases. Nothing can be pinned correctly until that is\n'
     '        # settled, so this exits the same way INCOMPATIBLE does under --strict\n'
     '        # and as findings otherwise.\n'
     '        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS\n'
     '    if worst == getattr(contracts, "STALE", "STALE"):\n'
     '        # A pin that matches a VERSION file older than its own code is not a\n'
     '        # pass. Same exit treatment as DRIFT, because it wants the same thing\n'
     '        # doing: bump the tool, then re-certify the set.\n'
     '        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS\n'),
]

ENTRY = """## [0.25.0] - the CHANGELOG is the third number, and now it is read

0.24.0 taught `verify-manifest` to notice a pin matching a stale VERSION, and
closed by naming what it still could not see:

    KNOWN AND NOT ADDRESSED HERE: the CHANGELOG is a third number this does
    not read. `lot`'s CHANGELOG documents 0.41.0 while its VERSION says
    0.33.0 and the manifest pins 0.32.0 -- three answers to one question, and
    this check compares two of them.

On 2026-08-14 finding that out cost twenty staged files and a person reading
them. The check said `lot` was STALE, which was true and the least
interesting true thing about it. `zoo` was worse and entirely invisible: it
had shipped 0.32.0 with no entry for it, and its CHANGELOG carried the number
0.31.0 twice -- once above the document's own title.

- **Two statuses, not one.** `UNRELEASED` is the CHANGELOG ahead of VERSION:
  entries for releases the tool never claimed to be. `UNDOCUMENTED` is
  VERSION ahead of the CHANGELOG: a release with no entry. They want opposite
  fixes -- bump the version, or write the entry -- and one status could not
  say which.
- **Checked first, and not only from OK.** STALE escalates only from OK on
  the argument that DRIFT's message is more useful when the numbers already
  disagree. `lot` refutes that: it was DRIFT, and DRIFT says "re-run the
  smoke and re-certify", which would have pinned 0.33.0 -- wrong by eight
  releases. A tool that does not know its own version cannot be pinned by
  anyone, so it outranks a pin being behind. `_SEVERITY` gains two ranks
  between DRIFT and INCOMPATIBLE.
- **`newest_changelog_entry` reads both heading shapes in use.** `patina`
  writes `## [0.19.0] - ...`, `dispatch` writes `## v0.3.0 - ...`, `pipeline`
  writes `## [v0.1.0] - ...`. The first cut of this reader took only the
  bracketed form and reported `dispatch` -- in perfect agreement with itself
  -- as disagreeing. An instrument that misreads the record is precisely the
  failure this module exists to catch, so the bug is recorded rather than
  quietly fixed.
- **Newest means FIRST, not highest.** These files are written newest-first
  and the top entry is the claim being made. Taking the maximum would have
  hidden `zoo`, whose stray entry sat above the title carrying a number
  already used below it.
- **No CHANGELOG means no opinion.** `laser_tag` is an addon directory
  holding VERSION and `addons/`. A missing file yields None and the tool is
  judged on the two numbers it has, the same way a missing version degrades
  to UNKNOWN rather than to a false OK.
- **`cli/commands`:** both statuses exit EXIT_FINDINGS, or EXIT_CONFIG under
  `--strict`.

Against the factory as of factory-v1.16.0 this reports nine tools OK and one
UNDOCUMENTED: `pipeline`, whose VERSION says 0.5.0 while its newest entry is
v0.1.0 -- four releases with no entry. That one is real and still open.

Worth noting which status that is, because the first draft of this entry said
UNRELEASED and its own selftest refuted it. `pipeline` has releases with no
entries, not entries with no release; the CHANGELOG is BEHIND. Two statuses
exist precisely so that distinction cannot be waved at, and it caught the
person who wrote them within a minute of their existing.
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


def _apply(root: Path, *, check: bool) -> int:
    rc = 0
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            rc = 1
            continue
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        eol = _eol(body)
        out, done, failed = body, 0, False

        for old, new in edits:
            o, n = _as(old, eol), _as(new, eol)
            if n in out:
                done += 1
                continue
            if out.count(o) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(o)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:68]}")
                rc, failed = 1, True
                break
            out = out.replace(o, n, 1)
        if failed:
            continue
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        try:
            compile(out, str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
            rc = 1
            continue
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

    # --------------------------------------------------- VERSION + CHANGELOG --
    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return rc
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V} "
              f"(found {vbody.strip()!r})")
        return 1
    if f"## [{NEW_V}]" in cbody:
        print(f"REFUSING: the CHANGELOG already has a {NEW_V} entry")
        return 1
    ceol = _eol(cbody)
    vout = vbody.replace(OLD_V, NEW_V, 1)
    cout = _as(ENTRY, ceol) + ceol + cbody
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  "
              f"+{len(cout.encode('utf-8')) - len(cbody.encode('utf-8')):,} bytes")
        return rc
    for p, raw in ((vp, vbody.encode("utf-8")), (cp, cbody.encode("utf-8"))):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
    vp.write_bytes(vout.encode("utf-8"))
    cp.write_bytes(cout.encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print(f"  prepended    CHANGELOG.md")
    return rc


def selftest(root: Path) -> int:
    """Exercise the real functions, then run the real check on the real factory."""
    import importlib
    import shutil
    import tempfile

    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    contracts = importlib.import_module("packages.tools.contracts")
    importlib.reload(contracts)

    tmp = Path(tempfile.mkdtemp())
    try:
        def mk(name: str, text: str | None) -> Path:
            d = tmp / name
            d.mkdir(parents=True, exist_ok=True)
            if text is not None:
                (d / "CHANGELOG.md").write_text(text, encoding="utf-8")
            return d

        # Every heading shape actually in use in this factory.
        check("bracketed heading",
              contracts.newest_changelog_entry(
                  mk("a", "# Changelog\n\n## [0.19.0] - 2026-08-02\n")) == "0.19.0")
        check("v-prefixed heading (dispatch's shape)",
              contracts.newest_changelog_entry(
                  mk("b", "# Changelog\n\n## v0.3.0 - 2026-07-11\n")) == "0.3.0")
        check("bracketed AND v-prefixed (pipeline's shape)",
              contracts.newest_changelog_entry(
                  mk("c", "# Pipeline Changelog\n\n## [v0.1.0] - x\n")) == "0.1.0")
        check("no CHANGELOG is no opinion, not a finding",
              contracts.newest_changelog_entry(mk("d", None)) is None)
        # zoo's shape: a stray entry above the title, reusing a number.
        check("newest means FIRST, not highest",
              contracts.newest_changelog_entry(mk(
                  "e", "## [0.28.0] - stray\n\n# Changelog\n\n"
                       "## [0.31.0] - real\n")) == "0.28.0")

        check("CHANGELOG ahead -> UNRELEASED (lot)",
              contracts.self_disagreement("Lot 0.33.0", "0.41.0")
              == contracts.UNRELEASED)
        check("VERSION ahead -> UNDOCUMENTED (zoo, before)",
              contracts.self_disagreement("Zoo 0.32.0", "0.31.0")
              == contracts.UNDOCUMENTED)
        check("agreement is not a finding",
              contracts.self_disagreement("Patina 0.19.0", "0.19.0") is None)
        check("a missing CHANGELOG is not a finding",
              contracts.self_disagreement("Laser Tag 0.8.0", None) is None)

        check("both outrank DRIFT",
              contracts._SEVERITY[contracts.UNRELEASED]
              > contracts._SEVERITY[contracts.DRIFT]
              and contracts._SEVERITY[contracts.UNDOCUMENTED]
              > contracts._SEVERITY[contracts.DRIFT])
        check("neither outranks INCOMPATIBLE",
              contracts._SEVERITY[contracts.INCOMPATIBLE]
              > contracts._SEVERITY[contracts.UNRELEASED])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  and against the real factory:")
    results = contracts.verify_manifest(root)
    width = max(len(r.adapter_id) for r in results)
    for r in results:
        print(f"    {r.status:<13} {r.adapter_id:<{width}}  {r.message[:76]}")
    worst = contracts.worst_status(results)
    print(f"\n    worst: {worst}")

    named = {r.adapter_id: r.status for r in results}
    # NO ASSERTION ABOUT A SPECIFIC TOOL'S CURRENT STATUS. An earlier version
    # asserted `pipeline == UNDOCUMENTED`, which was true when this was written
    # and false four commits later once pipeline's CHANGELOG was backfilled.
    # A test that pins the factory's present state fails the moment the state
    # improves, which trains people to ignore it. The MECHANISM is what has to
    # hold, and that is proved above on fixtures that cannot drift; the run
    # against the real factory is a report, not an assertion.
    flagged = [f"{k} ({v})" for k, v in sorted(named.items())
               if v in (contracts.UNRELEASED, contracts.UNDOCUMENTED)]
    print(f"    disagreeing with themselves: "
          f"{', '.join(flagged) if flagged else 'none'}")
    # NOT `== OK`. The first draft asserted that and failed against the real
    # factory, where dispatch is STALE -- its code has commits newer than its
    # VERSION, which is 0.24.0's check working, not this one misreading. The
    # claim being tested is only that its `## v0.3.0` headings parse, so the
    # assertion is that the two NEW statuses do not fire.
    check("dispatch is not caught by the new statuses -- its v-prefixed "
          "headings read fine",
          named.get("dispatch") not in (contracts.UNRELEASED,
                                        contracts.UNDOCUMENTED))
    check("laser_tag is not punished for having no CHANGELOG",
          named.get("laser_tag") not in (contracts.UNRELEASED,
                                         contracts.UNDOCUMENTED))
    # level_factory reads DRIFT here on purpose: this bump makes it 0.25.0
    # while the manifest still pins 0.24.0. The pin moves after the commit,
    # not before, so DRIFT is the correct answer at this moment.
    check("level_factory is DRIFT, not a CHANGELOG finding -- the pin moves "
          "after the commit",
          named.get("level_factory") not in (contracts.UNRELEASED,
                                             contracts.UNDOCUMENTED))

    print()
    print("  ready to commit and tag" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in dict.fromkeys([r for r, _o, _n in EDITS]
                                 + [VERSION_F, CHANGELOG]):
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
        print("  python patches\\patch_lf_025.py --selftest")
        print()
        print("  then, INSIDE level_factory:")
        print("    git -C level_factory add -A")
        print('    git -C level_factory commit -m "0.25.0 -- verify-manifest '
              'reads the CHANGELOG"')
        print("    git -C level_factory tag -a v0.25.0 -m "
              '"0.25.0 -- verify-manifest reads the CHANGELOG"')
        print("    git -C level_factory push --follow-tags")
        print()
        print("  the manifest pin moves to 0.25.0 after that, not before.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
