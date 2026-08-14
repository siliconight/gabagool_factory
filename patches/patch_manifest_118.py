r"""factory 1.18.0 -- the export package has a name, and a real run proved it.

    python patch_manifest_118.py --check
    python patch_manifest_118.py
    python patch_manifest_118.py --selftest
    python patch_manifest_118.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.26.0. A pin naming a tag that does not exist is the failure this manifest
exists to prevent.

WHAT MOVES

    level_factory   0.25.0  -> 0.26.0
    factory_version 1.17.0  -> 1.18.0

Nine tools are unchanged: deli_counter 0.89.0, dispatch 0.3.1, laser_tag
0.8.0, lot 0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat
0.12.0, zoo 0.36.0.

THIS ONE IS NOT BOOKKEEPING, AND THE DISTINCTION IS THE SAME ONE 1.17.0 MADE.

1.17.0 pinned code that was already running under names that had gone stale;
its entry says "nothing new was verified for this bump" because nothing was.
1.18.0 is the opposite case: new code, a behaviour change a recipient can
see, and a run that earned it rather than an argument that it should work.

WHAT WAS RUN, AND WHAT IT SHOWED

    python -m level_factory -C workspaces\lot-demo-ws \
        export lot_demo_001 --mode portable-godot
      -> .level_factory\exports\LF_lot_demo_001.portable-godot

    python -m level_factory -C workspaces\lot-demo-ws \
        portability-test lot_demo_001 --mode portable-godot
      -> status PASS, engine_check passed, parser_error_count 0,
         shader_error_count 0, scene_instantiated true,
         missing_resource_count 0, absolute_path_count 0,
         external_reference_count 0, resource_count 35, godot 4.7,
         created_at 2026-08-14T20:32:26Z

    ... export lot_demo_001 --mode portable-godot --format zip
      -> LF_lot_demo_001.portable-godot.zip

That last line is the only change in 0.26.0 with a visible before/after that
is not a rename. The archive had been `lot_demo_001.zip` -- no profile in the
name -- because `with_suffix(".zip")` reads `.portable-godot` as a file
extension and REPLACES it. Nobody decided to drop the profile; a path helper
ate it, and both profiles would have written to the same archive name. The
old 18.6 MB `lot_demo_001.zip` sat beside the new one as its own control.

WHAT WAS NOT RUN

Everything else. No mission re-run and no re-grade -- the 40 / 55 / 60 grades
in the manifest description are still 1.16.0's, from 2026-08-14 on the art
layer. No walk sweep, no pack load check, no unit suites. `pure-shell` has
NOT been re-exported since the rename; its directory under
`.level_factory\exports\` still carries the old name, and the first person to
export it will get `LF_lot_demo_001.pure-shell` beside a stale sibling.

THE DESCRIPTION IS NOT REWRITTEN, for the reason 1.17.0 gave. The portability
pass is evidence for ONE claim -- that a package still loads in a clean Godot
4.7 project after its directory was renamed -- not a re-certification of the
set. Promoting one narrow run into the set's description would make the whole
description read as fresher than it is.

STAGE 1 OF THREE, AND THE OTHER TWO ARE NOT STARTED

`docs/EXPORT_NAMING.md` (accepted 2026-08-14) specifies three names. This
release lands the first: the build directory. The archive's full name
(`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`) needs the seed, the
build time and the factory version plumbed into `export_mission`, which
changes its signature; `LF_MANIFEST.json` and repacking under a stable
`LF_<mission>/` come with it. Then the interior renames -- `lot/<building>/`
to `sites/<building>/`, dropping `assets/lot.glb` -- which move `res://`
paths inside the package and want their own portability run.

NEWLY KNOWN, AND THIS INSTRUMENT CANNOT SEE IT

`level_factory/pyproject.toml` says `version = "0.22.0"`. Its VERSION file
says 0.26.0 and its CHANGELOG's newest entry says 0.26.0. That is a FOURTH
version answer for a tool the three-number check has been reporting as OK all
day, and it reports OK because `installed_factory_versions` reads only the
VERSION file. The check is not wrong about what it measured; it is silent
about a source it never looks at. Noticed while working out how to invoke the
CLI, not by any check -- which is the whole argument for writing it down
here. Not fixed in this release.

KNOWN FAILING, UNCHANGED FROM 1.17.0

`check_all` freshness still reports 57 buildings whose geometry no longer
matches the spec or builder that made them. Three demo shells still fail
nav_gate -- `cbp`, `night_pawn`, `primos_pizza` -- none of them in the
`lot_demo_001` draw. `laser_tag` still has no CHANGELOG.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_118"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.25.0", "0.26.0"),
}

OLD_FV, NEW_FV = "1.17.0", "1.18.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.18.0] - 2026-08-14

level_factory 0.25.0 -> 0.26.0. The other nine tools are unchanged from
factory-v1.17.0: deli_counter 0.89.0, dispatch 0.3.1, laser_tag 0.8.0, lot
0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat 0.12.0, zoo
0.36.0.

NOT A BOOKKEEPING RELEASE, WHICH IS THE DISTINCTION 1.17.0 DREW

1.17.0 pinned code that was already running, under names that had gone
stale, and said plainly that nothing new was verified for it. This is the
other kind: new code, a behaviour change a recipient of a package can see,
and a run that earned it.

WHAT CHANGED

An export's directory name was composed in five places -- twice in
`packages/exporting/export.py`, three times in `apps/cli/commands`. One of
those five hardcoded `portable-godot` four lines after the block above it had
set the mode, so it was correct only for as long as the default never moved.
`ids.export_build_dir_name` is now the only definition, and it lives beside
`candidate_id` and `job_id` because those already own the rule that an id
which becomes a directory is refused rather than sanitised.

`lot_demo_001.portable-godot/` is now `LF_lot_demo_001.portable-godot/`.

THE ARCHIVE STOPS LOSING ITS PROFILE

`with_suffix(".zip")` reads `.portable-godot` as a file extension and
REPLACES it, which is the entire reason the archive was `lot_demo_001.zip`
with no profile in the name -- and why both profiles would have written to
the same archive. Nobody decided to drop it; a path helper ate it. Appending
instead of substituting gives `LF_lot_demo_001.portable-godot.zip`.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot
      -> .level_factory\\exports\\LF_lot_demo_001.portable-godot
    portability-test lot_demo_001 --mode portable-godot
      -> PASS. engine_check passed, parser_error_count 0,
         shader_error_count 0, scene_instantiated true,
         missing_resource_count 0, absolute_path_count 0,
         external_reference_count 0, resource_count 35, godot 4.7
    export ... --format zip
      -> LF_lot_demo_001.portable-godot.zip

The portability pass was re-earned, not assumed. The export directory moved,
and a package that loads in a clean Godot 4.7 project is exactly the claim a
directory rename could break.

WHAT WAS NOT RUN

No mission re-run and no re-grade: the 40 / 55 / 60 grades in the manifest
description are still 1.16.0's. No walk sweep, no pack load check, no unit
suites. `pure-shell` has not been re-exported since the rename.

The manifest description is not rewritten. One portability pass is evidence
for one claim, not a re-certification of the set.

STAGE 1 OF THREE

`docs/EXPORT_NAMING.md` specifies three names; this lands the build
directory. The full archive name needs the seed, the build time and the
factory version plumbed into `export_mission`, and `LF_MANIFEST.json` comes
with them. The interior renames (`lot/<building>/` -> `sites/<building>/`,
dropping `assets/lot.glb`) move `res://` paths and want their own
portability run.

A FOURTH VERSION NUMBER, WHICH THE CHECK CANNOT SEE

`level_factory/pyproject.toml` says `version = "0.22.0"` while VERSION and
the CHANGELOG both say 0.26.0. `verify-manifest` reports level_factory OK
because `installed_factory_versions` reads only the VERSION file. The check
is not wrong about what it measured -- it is silent about a source it never
looks at. This was noticed while working out how to invoke the CLI, not by
any check, which is the argument for recording it. Open.

KNOWN FAILING, UNCHANGED

57 buildings stale in `check_all` freshness. `cbp`, `night_pawn` and
`primos_pizza` still fail nav_gate; none are in the `lot_demo_001` draw.
`laser_tag` still has no CHANGELOG.

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
    check("it says this one is NOT bookkeeping",
          "NOT A BOOKKEEPING RELEASE" in cl)
    check("it names the portability evidence",
          "portability-test lot_demo_001" in cl and "PASS" in cl
          and "resource_count 35" in cl)
    check("it says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "no re-grade" in cl
          and "pure-shell has not been re-exported" in cl.replace("`", ""))
    check("it records the archive fix with its cause",
          'with_suffix(".zip")' in cl
          and "LF_lot_demo_001.portable-godot.zip" in cl)
    check("it names the two stages that are NOT done",
          "LF_MANIFEST.json" in cl and "sites/<building>/" in cl)
    check("it records the fourth version number",
          "pyproject.toml" in cl and "0.22.0" in cl
          and "silent about a source it never" in cl)

    # The description carries 1.16.0's evidence and is deliberately unrewritten.
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
        print("    python patches\\patch_manifest_118.py --selftest")
        print('    git commit -am "factory 1.18.0 -- the export package has a '
              'name, and a real run proved it"')
        print(f'    git tag -a factory-v{NEW_FV} -m "factory {NEW_FV}"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
