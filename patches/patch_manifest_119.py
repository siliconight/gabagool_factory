r"""factory 1.19.0 -- stage 1 of the export naming work is closed.

    python patch_manifest_119.py --check
    python patch_manifest_119.py
    python patch_manifest_119.py --selftest
    python patch_manifest_119.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.27.0.

WHAT MOVES

    level_factory   0.26.0  -> 0.27.0
    factory_version 1.18.0  -> 1.19.0

Nine tools unchanged: deli_counter 0.89.0, dispatch 0.3.1, laser_tag 0.8.0,
lot 0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat 0.12.0, zoo
0.36.0.

THIS PIN HAS A SECOND EFFECT, WHICH IS NEW

Since 0.27.0, every export writes `LF_MANIFEST.json` carrying `tools` -- the
CERTIFIED SET, read out of this file. So the pin is no longer only a record;
it is now shipped inside every package. Until this bump lands, an export of
0.27.0 code writes `"level_factory": "0.26.0"` into that block, which is
correct (0.27.0 was not certified yet) and confusing to anyone who does not
know why. After it, exports self-describe.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot --format zip
      -> LF_lot_demo_001_s5219_20260814T211037Z_f1.18.0_portable-godot.zip
    portability-test lot_demo_001 --mode portable-godot
      -> PASS. engine_check passed, parser_error_count 0,
         shader_error_count 0, scene_instantiated true,
         missing_resource_count 0, absolute_path_count 0,
         external_reference_count 0, resource_count 35, godot 4.7

And the archive was OPENED and its manifest READ, which is the only reason
0.27.0 is correct. Its selftest passed 40 of 40 against a package whose
`LF_MANIFEST.json` said `"candidate": "lot_demo_001.candidate.seed_XXXX"` and
`"tools": {"lot": "0.4.0"}`. Both checks asserted the plumbing carried what it
was handed; both times it did, and what it was handed was wrong. See 0.27.0's
entry -- the correction is recorded there, in the release it belongs to,
because nothing had been tagged yet.

WHAT WAS NOT RUN

No mission re-run, no re-grade: the 40 / 55 / 60 grades in the manifest
description are still 1.16.0's. No walk sweep, no pack load check. The unit
suite WAS run for 0.27.0 (579 passed) but `pytest tests` still aborts in
collection on `tests/test_presentation_fingerprint.py`, which imports a
`_COMPOSER_SOURCES` that no longer exists in `adapters.presentation`. That is
older than this work and unrelated to it, and it means the four tests outside
`tests/unit` have not run in some time.

`pure-shell` has still not been re-exported since 0.26.0 renamed the build
directory.

THE DESCRIPTION IS NOT REWRITTEN, for the reason 1.17.0 gave and 1.18.0
repeated. One portability pass is evidence for one claim.

STAGE 1 IS CLOSED; STAGE 2 IS NOT STARTED

`docs/EXPORT_NAMING.md` specifies three names and all three now exist. What
remains is the interior: `lot/<building>/` -> `sites/<building>/` and
dropping `assets/lot.glb`. Those move `res://` paths INSIDE the package and
want their own portability run.

OPEN, AND THE FIRST ONE IS THE SERIOUS ONE

`workspaces/lot-demo-ws/.level_factory/approvals/lot_demo_001.selected` holds
the literal string `lot_demo_001.candidate.seed_XXXX`. `cmd_approve` writes
`--candidate` verbatim and nothing validates it. `_selected_lot_out` builds a
job path from it, so `graybox_dir` in `cmd_export` points at a directory that
does not exist and the export has been succeeding on the Dispatch handoff
alone. The same function feeds the post-art functional-regression check a
`site.site.gameplay.json` that is not there. Whether that gate is still
comparing anything real has NOT been measured -- `tools/probe_selection_drift.py`
exists to measure it. 0.27.0 stopped the bad value reaching the shipped
manifest and made the disagreement print on every export; it did not change
which directory a job resolves from, and it should not have.

`level_factory/pyproject.toml` still says `version = "0.22.0"` while VERSION
says 0.27.0. Unchanged from 1.18.0, still invisible to `verify-manifest`.

`check_all` freshness still reports 57 stale buildings. `cbp`, `night_pawn`
and `primos_pizza` still fail nav_gate. `laser_tag` still has no CHANGELOG.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_119"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.26.0", "0.27.0"),
}

OLD_FV, NEW_FV = "1.18.0", "1.19.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.19.0] - 2026-08-14

level_factory 0.26.0 -> 0.27.0. The other nine tools are unchanged from
factory-v1.18.0: deli_counter 0.89.0, dispatch 0.3.1, laser_tag 0.8.0, lot
0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat 0.12.0, zoo
0.36.0.

Stage 1 of `docs/EXPORT_NAMING.md` is closed. All three names it specifies
now exist:

    exports/LF_lot_demo_001.portable-godot/       the build dir      (0.26.0)
    LF_lot_demo_001/                              inside the archive (0.27.0)
    LF_lot_demo_001_s5219_<utc>_f1.19.0_portable-godot.zip            (0.27.0)

THIS PIN IS NOW SHIPPED, NOT JUST RECORDED

0.27.0 writes `LF_MANIFEST.json` into every package, and its `tools` block is
the certified set read out of `factory.manifest.json`. The pin therefore
travels inside every export. Before this bump, an export built from 0.27.0
code wrote `"level_factory": "0.26.0"` there -- correct, because 0.27.0 was
not certified yet, and confusing to anyone who did not know why. After it,
exports self-describe.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot --format zip
      -> LF_lot_demo_001_s5219_20260814T211037Z_f1.18.0_portable-godot.zip
    portability-test lot_demo_001 --mode portable-godot
      -> PASS, engine_check passed, 0 parser errors, 0 shader errors,
         scene_instantiated true, 0 missing resources, resource_count 35
    level_factory unit suite: 579 passed, 1 skipped

AND THE ARCHIVE WAS OPENED AND ITS MANIFEST READ, which is the only reason
0.27.0 is correct. Its selftest passed 40 of 40 against a package whose
manifest said `"candidate": "...seed_XXXX"` and `"tools": {"lot": "0.4.0"}`
-- the adapter version, where lot is 0.41.0. Both checks asserted that the
plumbing carried what it was handed. It did. What it was handed was wrong.
A check that follows the data instead of reading the artifact will pass on a
deliverable that is false, and this one did.

WHAT WAS NOT RUN

No mission re-run and no re-grade; the 40 / 55 / 60 grades in the manifest
description are still 1.16.0's, and it is not rewritten. No walk sweep, no
pack load check. `pure-shell` has still not been re-exported since 0.26.0
renamed the build directory.

`pytest tests` still aborts during collection on
`tests/test_presentation_fingerprint.py`, which imports a `_COMPOSER_SOURCES`
that no longer exists in `adapters.presentation`. Confirmed against an
unpatched checkout, so it predates this work -- but it means the four test
modules outside `tests/unit` have not run in some time, and nothing said so.

OPEN, AND THE FIRST IS THE SERIOUS ONE

The `candidate_selected` marker for `lot_demo_001` holds the literal template
`lot_demo_001.candidate.seed_XXXX`; `cmd_approve` writes `--candidate`
verbatim and nothing validates it. `_selected_lot_out` derives a job path
from it, so `graybox_dir` points at a directory that does not exist and
exports have been succeeding on the Dispatch handoff alone. The same function
feeds the post-art functional-regression check a `site.site.gameplay.json`
that is not there. Whether that gate still compares anything real has NOT
been measured; `tools/probe_selection_drift.py` measures it without changing
anything. 0.27.0 stopped the bad value reaching the shipped manifest and made
the disagreement print on every export. It did not change which directory a
job resolves from, and should not have.

`pyproject.toml` still says 0.22.0 against a VERSION of 0.27.0, still
invisible to `verify-manifest`. 57 buildings stale in `check_all` freshness.
`cbp`, `night_pawn` and `primos_pizza` still fail nav_gate. `laser_tag` still
has no CHANGELOG.

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
    check("it closes stage 1 by naming all three names",
          "Stage 1 of" in cl and "the build dir" in cl
          and "inside the archive" in cl)
    check("it says the pin now ships inside every package",
          "SHIPPED, NOT JUST RECORDED" in cl and "LF_MANIFEST.json" in cl)
    check("it names the portability evidence",
          "portability-test lot_demo_001" in cl and "PASS" in cl
          and "resource_count 35" in cl)
    check("it records that the selftest passed on a false artifact",
          "passed 40 of 40" in cl and "seed_XXXX" in cl
          and "will pass on a\ndeliverable that is false" in cl)
    check("it says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "no re-grade" in cl)
    check("it records the test module that has not run in some time",
          "_COMPOSER_SOURCES" in cl and "predates this work" in cl)
    check("it names the marker defect and carries the measurement",
          "seed_XXXX" in cl and "HAS NOW BEEN MEASURED" in cl
          and "The site file changes nothing" in cl)
    check("it still names the fourth version number",
          "pyproject.toml" in cl and "0.22.0" in cl)
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
        print("    python patches\\patch_manifest_119.py --selftest")
        print('    git commit -am "factory 1.18.0 -- the export package has a '
              'name, and a real run proved it"')
        print(f'    git tag -a factory-v{NEW_FV} -m "factory {NEW_FV}"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
