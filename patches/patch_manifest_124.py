r"""factory 1.24.0 -- Lux is a layer you can decline, and three empty packages.

    python patches\patch_manifest_124.py --check
    python patches\patch_manifest_124.py
    python patches\patch_manifest_124.py --selftest
    python patches\patch_manifest_124.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.35.0, v0.36.0 and v0.37.0.

WHAT MOVES

    level_factory   0.34.0  -> 0.37.0
    factory_version 1.23.0  -> 1.24.0

Nine tools unchanged.

WHAT THE SET NOW DOES

Roadmap item 47. `LAYER_LIGHT` (0.35.0) splits Lux's apply pass out of the
art layer; `MODE_ART_UNLIT` (0.36.0) drops Lux's result at EXPORT time, so
one build ships two comparable archives; 0.37.0 makes the assembled themed
site reach the package at all, which is what an unlit one has to open.

`--art` still means art + light and `--target presentation` still plans the
full stack. Nothing anyone types today produces a different package than it
did at 1.23.0.

THE THING THIS SET IS ACTUALLY ABOUT

Three packages that opened to nothing, and passed every check.

The first real art-unlit export of lot_demo_001 held 180 files and 28.6 MB
of themed geometry with an entry that instanced nothing, and
`export_closure_scan.json` said `ok: true, resource_count: 6`. Closure walks
FROM the entry, so an entry referencing nothing is trivially closed: the
emptier the package, the more certainly it passed. The guard added for that
then found pure-shell had been hollow since this mission grew a
`dispatch_handoff` -- `base_dir` chose the handoff OR the graybox, and a
layer goes on a base rather than replacing it. Two test fixtures turned out
to have described empty packages since the day they were written.

MEASURED, WITH THE NUMBERS

    level_factory tests/unit                 659 passed
    level_factory tests/service+integration   28 passed
    level_factory tests/real_tools             9 passed, 1 skipped
    lot_demo_001 exported all three modes, compared file by file:
      unlit entry 571 B (instancing nothing) -> 688 B instancing
      res://site.tscn; unlit drops Lux's outputs and its whole runtime,
      33 files, and nothing else; both packages share an interior folder.

NOT MEASURED, AND SAY SO

No mission has been RUN with `--art --unlit` through Blender and Godot. The
art-unlit packages here were built by exporting a mission that ran Lux and
subtracting, which is the case the A/B needs but not the case a collaborator
producing their own unlit level would hit. Roadmap 47 stage 3b.

The one skipped real-tool test is `test_real_adapters.py::dispatch`, skipped
for missing example build inputs including `build/lux/lux.profile.json`. It
is the only test in the repository that exercises Dispatch consuming Lux's
output -- which is the relationship 0.35.0's `dispatch_dep` conditional
rewired. It has been skipped for want of fixture data, not by this work, and
it is named here rather than counted as green.

A PROCESS FAILURE WORTH RECORDING IN THE CERTIFICATION

0.34.0 through 0.37.0 each reported "still green" against 28 tests from
`tests/service` and `tests/integration`. `tests/unit` is 659 and none of them
ran it; `test_fanout.py` was red from 0.35.0 onward and told nobody. A subset
described as the suite is the same instrument failure this set is about, one
level up. Every level_factory selftest now runs `tests/unit` whole.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_124"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.34.0", "0.37.0"),
}

OLD_FV, NEW_FV = "1.23.0", "1.24.0"

ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.24.0] - 2026-08-15

level_factory 0.34.0 -> 0.37.0. The other nine tools are unchanged from
factory-v1.23.0.

WHAT THE SET NOW DOES

Roadmap item 47. `LAYER_LIGHT` splits Lux's apply pass out of the art layer,
`MODE_ART_UNLIT` drops Lux's result at export time so one build ships two
comparable archives, and the assembled themed site now reaches the package at
all -- which is what an unlit one has to open.

Only the apply pass moved. `zoo_fixtures_build` bakes the physical light
hardware and `lux_fixture_gate` machine-checks it, and both stay in the art
layer: a floating light or a dark fixture is broken GEOMETRY whoever lights
it. An unlit package therefore ships validated fixtures and their `LuxEmit`
markers, which another lighting system can read as a contract.

`--art` still means art + light, and `--target presentation` still plans the
full stack. Nothing anyone types today produces a different package than it
did at 1.23.0.

THREE PACKAGES THAT OPENED TO NOTHING, AND PASSED

The first real art-unlit export of lot_demo_001 held 180 files and 28.6 MB of
themed geometry with an entry that instanced nothing:

    export_closure_scan.json: {"ok": true, "resource_count": 6,
                               "missing_resource_count": 0}

Closure walks FROM the entry, so an entry that references nothing is
trivially closed -- the emptier the package, the more certainly it passed.
The portability test would have agreed too, because the entry prints its
marker whether or not it added a child.

`themed_site_assemble` writes a 31,872 byte `site.tscn` that reached no
package; the lit export got away with it because Lux's output stands in for
the assembly. `write_entry_scene` now refuses to write an entry that
instances nothing, and it knows nothing about modes, so a mode nobody has
written yet cannot ship hollow either.

That guard then found pure-shell hollow since this mission grew a
`dispatch_handoff`: `base_dir` chose the handoff OR the graybox, where a
layer goes ON a base. Two exports of lot_demo_001 measure it -- 2026-08-10,
before the handoff existed, carried a 25,378 byte site.tscn and a 688 byte
entry; today's carried neither. And two closure fixtures turned out to have
described empty packages since the day they were written.

MEASURED

    tests/unit                  659 passed
    tests/service+integration    28 passed
    tests/real_tools              9 passed, 1 skipped
    lot_demo_001, all three modes exported and compared file by file:
      the unlit entry went from 571 bytes instancing nothing to 688 bytes
      instancing res://site.tscn; the unlit package drops Lux's outputs and
      its entire runtime -- 33 files -- and nothing else; both packages share
      an interior folder name so a recipient can swap one for the other
      without every res:// path moving.

NOT MEASURED

No mission has been RUN with `--art --unlit` through Blender and Godot. The
art-unlit packages here were built by exporting a mission that RAN Lux and
subtracting -- the case the A/B needs, not the case a collaborator producing
their own unlit level would hit. Roadmap 47 stage 3b.

The skipped real-tool test is the Dispatch adapter, skipped for missing
example build inputs including `build/lux/lux.profile.json`. It is the only
test that exercises Dispatch consuming Lux's output, which is the
relationship 0.35.0's `dispatch_dep` conditional rewired. Skipped for want of
fixture data, not by this work, and named here rather than counted as green.

A PROCESS FAILURE, RECORDED IN THE CERTIFICATION

0.34.0 through 0.37.0 each reported "still green" against 28 tests.
`tests/unit` is 659 and none of them ran it; `test_fanout.py` was red from
0.35.0 onward and told nobody. A subset described as the suite is the same
instrument failure this set is about, one level up. Every level_factory
selftest now runs `tests/unit` whole.
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
    """Refuse to pin a version the tool on disk does not claim."""
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

    moved = 0
    for tool, meta in sorted(data["tools"].items()):
        d = root / (meta.get("path") or tool)
        v = version_of(d / "VERSION")
        agree = (v == meta["version"])
        if tool == "pixelcoat" and v is None:
            agree = True  # version lives in pixelcoat/version.py, per its note
        if not agree:
            moved += 1
            print(f"       {tool}: manifest {meta['version']}, disk {v}")
    check("every pin agrees with the tool on disk", moved == 0)

    untouched = [t for t in data["tools"] if t not in PINS]
    check("nine tools were not in PINS", len(untouched) == 9)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"one factory-v{NEW_FV} entry",
          cl.count(f"## [factory-v{NEW_FV}]") == 1)
    top = re.search(r"^##\s*\[factory-v([0-9]+\.[0-9]+\.[0-9]+)\]", cl, re.M)
    check("it is the newest entry",
          top is not None and top.group(1) == NEW_FV)

    # The entry has to carry the numbers, not the adjectives.
    check("it records the unit count that four releases did not run",
          "tests/unit                  659 passed" in cl)
    check("and the entry-scene measurement",
          "571 bytes instancing nothing to 688 bytes" in flat)
    check("and says what was NOT measured",
          "No mission has been RUN with `--art --unlit`" in flat)
    check("and names the skipped real-tool test rather than counting it green",
          "named here rather than counted as green" in flat)
    check("and records the process failure",
          "A subset described as the suite" in flat)

    print()
    print("  NOT VERIFIED HERE: that v0.35.0, v0.36.0 and v0.37.0 exist on")
    print("  origin. `git tag -l` in level_factory is that check; this reads")
    print("  working trees.")

    print()
    print("  the certified set is 1.24.0"
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
        print("    python patches\\patch_manifest_124.py --selftest")
        print()
        print("  Then commit factory.manifest.json + CHANGELOG.md and tag")
        print("  factory-v1.24.0.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
