r"""factory 1.23.0 -- item 43 answered, and the art layer stops being Lux.

    python patches\patch_manifest_123.py --check
    python patches\patch_manifest_123.py
    python patches\patch_manifest_123.py --selftest
    python patches\patch_manifest_123.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.33.0 and v0.34.0.

WHAT MOVES

    level_factory   0.32.0  -> 0.34.0
    factory_version 1.22.0  -> 1.23.0

Nine tools unchanged.

TWO TOOL RELEASES IN ONE FACTORY VERSION, ON PURPOSE. 0.33.0 was tagged and
never pinned -- the suite it repaired was still being measured when it
landed. Pinning 0.32.0 -> 0.34.0 in one step is honest about that: the
certified combination skips a version it never certified, and this entry says
which one and why.

WHAT factory-v1.22.0 LEFT OPEN

Its own entry recorded nine failing tests and refused to say whether 0.32.0
caused them: "the comparison is one revert and two runs, and it has not been
run." It has now been run, and the answer is no.

The nine were ONE failure with eight downstream absences.
`presentation_compose` failed on a missing `*_dressing.glb`, so
`themed_site_assemble`, `lux_apply` and `dispatch_handoff` never ran, which
is why the facade reported PLANNED nodes and no `mission.tscn` appeared.

The cause was in the test fixture, not the product: the stub Zoo's `--dress`
branch wrote its index and no geometry, while its own `--fixtures` branch
next to it had always written both. That is why `lux_fixture_gate` succeeded
in the same run this broke. `dressing_glb", "_dressing.glb"` appears twice in
`adapters/presentation/__init__.py.pre_032` and twice in the current file,
unchanged -- so the guard predates 0.32.0 by about nine days, and 0.32.0 only
made it visible.

Roadmap item 43 closes on that. It was never the regression it looked like.

WHAT 0.33.0 AND 0.34.0 ALSO FOUND

Three defects sat behind that one, and each was a check that could not see
what it claimed to cover:

  * `zoo_dressing_build` declared only its index as an expected output, so a
    bake that published no geometry reported SUCCEEDED and the failure
    surfaced two stages later as somebody else's input error, naming a
    directory upstream. It declares the `.glb` now and fails as itself.

  * The integration test asserted `stage in stdout` against a run that prints
    a status word per job. `bank_block_001.presentation_compose  failed`
    CONTAINS "presentation_compose", so that assertion PASSED on the stage
    that broke the run. Six of its eight checks would pass on a totally
    failed run. It reads the status word now.

  * `cmd_export` answered "did the art layer run?" with `lux_dir.exists()`.
    A mission whose art pass succeeded and whose Lux stage failed exported an
    LF_MANIFEST.json declaring no art layer, on a package full of art. That
    was wrong before roadmap 47 and becomes structural under it, so it landed
    alone, against a suite measured green, ahead of the change that makes it
    urgent.

MEASURED AFTER: level_factory tests/service + tests/integration, 28 passed,
0 failed -- the first green reading on those two directories since collection
broke.

WHAT THIS DOES NOT PIN

`pyproject.toml` said 0.22.0 against a VERSION of 0.33.0 and is corrected in
0.34.0, but nothing in the manifest reads it. Noted because an installed
copy had been reporting a version eleven releases stale, and no gate here
would have caught it.

The `level_factory` note in factory.manifest.json still stops at 0.22.0. It
is left alone, as factory-v1.22.0 left it -- this patch moves pins, and
rewriting a nine-release archaeology field is not a pin.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_123"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.32.0", "0.34.0"),
}

OLD_FV, NEW_FV = "1.22.0", "1.23.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.23.0] - 2026-08-15

level_factory 0.32.0 -> 0.34.0. The other nine tools are unchanged from
factory-v1.22.0.

TWO TOOL RELEASES IN ONE FACTORY VERSION. 0.33.0 was tagged and never
pinned; the suite it repaired was still being measured when it landed. The
certified combination skips a version it never certified, and this says
which.

ITEM 43 IS ANSWERED, AND THE ANSWER IS NO

factory-v1.22.0 recorded nine failing tests and refused to say whether
0.32.0 caused them: "the comparison is one revert and two runs, and it has
not been run." It has been run.

The nine were ONE failure with eight downstream absences.
`presentation_compose` failed on a missing `*_dressing.glb`, so
`themed_site_assemble`, `lux_apply` and `dispatch_handoff` never ran -- which
is why the facade reported PLANNED nodes, the dashboard stayed `pending`, no
`mission.tscn` appeared and `review` said "no presentation previews".

The cause was the test fixture, not the product. The stub Zoo's `--dress`
branch wrote its index and no geometry, while its own `--fixtures` branch
twenty lines above had always written both -- which is exactly why
`lux_fixture_gate` succeeded in the run this broke. Real Zoo's `--dress`
publishes geometry.

NOT A 0.32.0 REGRESSION. `dressing_glb", "_dressing.glb"` appears twice in
`adapters/presentation/__init__.py.pre_032` and twice in the current file,
unchanged. The guard predates 0.32.0 by about nine days. 0.32.0 repaired
collection and turned the lights on in a room that had been dark since
2026-08-06.

THREE CHECKS THAT COULD NOT SEE WHAT THEY COVERED

`zoo_dressing_build` declared only its index as an expected output, so a bake
that published no geometry reported SUCCEEDED and the failure surfaced two
stages downstream as somebody else's input error. It declares the `.glb` now
and fails as itself.

The integration test asserted `stage in stdout` against a run that prints a
status word per job, so the line `bank_block_001.presentation_compose
failed` satisfied the assertion for `presentation_compose`. Six of its eight
checks would pass on a run where every stage failed; the only two that caught
anything did so by never appearing at all. It reads the status word now and
accepts `succeeded` or `cache`.

`cmd_export` answered "did the ART layer run?" with `lux_dir.exists()`. A
mission whose Pixelcoat/Zoo/Patina pass succeeded and whose Lux stage failed
exported an LF_MANIFEST.json declaring no art layer, on a package full of
art, and nothing reads that field so nothing objected. It is a named
function with a test now, and the test asserts the old rule's output as a
floor over all eight combinations -- this may report more layers than before,
never fewer.

That last one was wrong before roadmap 47 and becomes structural under it,
where art-without-light is the normal case rather than a failure. It landed
alone, against a suite measured green, ahead of the change that makes it
urgent.

MEASURED

level_factory `tests/service` + `tests/integration`: 28 passed, 0 failed.
The first green reading on those two directories since collection broke. The
presentation chain runs end to end -- locked shell, art pass, Lux, Dispatch,
export, portability -- for the first time since roughly 2026-08-06.

NOT PINNED HERE

`pyproject.toml` had said 0.22.0 against a VERSION of 0.33.0 and is corrected
in 0.34.0. Nothing in the manifest reads it, and no gate here would have
caught eleven releases of drift.
"""

_CRLF = "\r\n"


def _eol(body: str) -> str:
    return _CRLF if _CRLF in body else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


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
                print(f"REFUSING: {name} changed and is not in PINS")
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
                  f"bytes ({len(blob) - len(mraw):+,})  "
                  f"sha256 {_sha(blob)[:16]}")

    craw = cp.read_bytes()
    cbody = craw.decode("utf-8")
    eol = _eol(cbody)
    if f"## [factory-v{NEW_FV}]" in cbody:
        print(f"  already applied  {CHANGELOG}")
        return 0
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
    for tool, (_o, new) in PINS.items():
        check(f"{tool} is pinned {new}",
              data["tools"][tool]["version"] == new)
        check(f"{tool}'s tag matches its version",
              data["tools"][tool]["tag"] == f"v{new}")

    # THE PIN IS A CLAIM ABOUT DISK. Check it against disk, not against
    # itself -- a manifest that agrees with a manifest proves nothing.
    moved = 0
    for tool, meta in sorted(data["tools"].items()):
        d = root / (meta.get("path") or tool)
        v = version_of(d / "VERSION")
        c = newest_entry(d / "CHANGELOG.md")
        agree = (v == meta["version"])
        if tool == "pixelcoat" and v is None:
            agree = True  # version lives in pixelcoat/version.py, per its note
        if not agree:
            moved += 1
            print(f"       {tool}: manifest {meta['version']}, disk {v}, "
                  f"newest entry {c}")
    check("every pin agrees with the tool on disk", moved == 0)

    untouched = [t for t in data["tools"] if t not in PINS]
    check("nine tools were not in PINS", len(untouched) == 9)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"one factory-v{NEW_FV} entry",
          cl.count(f"## [factory-v{NEW_FV}]") == 1)
    # `newest_entry` reads TOOL changelogs (`## [0.34.0]`). Factory headings
    # read `## [factory-v1.23.0]`, which that regex does not match at all --
    # it returns None and the check fails on a correctly-placed entry. The
    # factory changelog needs its own pattern, not a borrowed one.
    top = re.search(r"^##\s*\[factory-v([0-9]+\.[0-9]+\.[0-9]+)\]", cl, re.M)
    check("it is the newest entry",
          top is not None and top.group(1) == NEW_FV)
    if top is not None and top.group(1) != NEW_FV:
        print(f"       newest heading is factory-v{top.group(1)}")
    check("it answers what 1.22.0 left open",
          "It has been run." in flat)
    check("and says the nine were not a 0.32.0 regression",
          "NOT A 0.32.0 REGRESSION" in flat)
    check("and records the measurement, not just the claim",
          "28 passed, 0 failed" in flat)
    check("and names the skipped tool release",
          "0.33.0 was tagged and never pinned" in flat)

    print()
    print("  NOT VERIFIED HERE: that the tags exist on origin. `git tag -l`")
    print("  in each tool repo is the check, and this reads working trees.")

    print()
    print("  the certified set is 1.23.0"
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
        print("    python patches\\patch_manifest_123.py --selftest")
        print()
        print("  Then commit the factory: factory.manifest.json + CHANGELOG.md,")
        print("  tag factory-v1.23.0.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
