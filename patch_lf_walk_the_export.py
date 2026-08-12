r"""The walk preview wraps the export, so you walk what ships.

    python patch_lf_walk_the_export.py --explain
    python patch_lf_walk_the_export.py --check
    python patch_lf_walk_the_export.py
    python patch_lf_walk_the_export.py --verify <preview_dir>
    python patch_lf_walk_the_export.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## Why not the obvious fix

`_find_level_scene` prefers `site_lux.tscn`; `lux_apply` writes
`lux.applied.tscn`. Two strings that have never been the same, so the
preference has never fired, and `walk_content_dir` never looks in lux's `out/`
anyway. The obvious repair is to copy the applied scene into the preview under
the name the reader wants.

**It does not survive the contract.** `lux.applied.tscn` carries six
`res://addons/lux/` ext_resources -- `lux_root.gd`, three rigs,
`lux_light_rig.gd`, a preset -- and no `WorldEnvironment` or
`DirectionalLight3D` at all, because `LuxRoot` builds those on load. Measured on
`lot_demo_001`: 126,892 bytes, 390 nodes, 116 OmniLight3D and 11 SpotLight3D.
So the scene only renders if the Lux checkout is on disk, and PIPELINE_MAP is
unambiguous about what that makes it:

    If it only works because one of our tools is on disk, it is not a
    deliverable, it is an instrument that escaped.

Copying the addon into the preview would have been *permitted* -- the preview is
a throwaway dev project that already carries `lot_player.gd` and is never
exported -- and it would have shown the tool-on-disk look rather than the
shipped one.

## What the export already does

`export_mission` localizes exactly this. `LUX_LOCALIZED` copies the minimal Lux
runtime into the mission folder, `localize_export` is the fixer, `scan_closure`
is the judge, and `write_entry_scene` synthesizes `mission.tscn` -- a plain
Node3D whose script instances the level, with the comment "Self-contained (no
addons)". The contract is upheld at the export boundary, and the preview was
looking one boundary too early.

So the preview wraps the export. Three consequences, all wanted:

  * you look at **what actually ships**, not at an intermediate;
  * no addon travels anywhere, because the export already localized what it
    needs;
  * a closure defect breaks the preview **on your machine** instead of at a
    consumer's. That is not hypothetical -- `export_closure.json` once reported
    `"unresolved": []` on a package where 211 of 243 nodes instanced glbs it did
    not contain, and it "opened, applied Blue Hour correctly, and rendered
    nothing but sky".

## The change

`cmd_walk` runs the export first, by **calling `cmd_export`** rather than
reassembling its inputs. Those inputs -- the handoff dir, the composed root, the
lux dir, the addon sources, the layer set, the functional-lock regression check
-- are seventy lines of decisions, and a second copy of them in `cmd_walk` is
the defect this tree keeps finding. One derivation.

A consequence worth stating rather than discovering: **an export blocked by the
functional-lock regression check now blocks the walk too.** That is the right
way round. A package that failed its own gate is not a thing to go looking at
and form opinions about.

`_find_level_scene` gains `mission.tscn` at the top of its preference order,
because in an export root that is the entry and `site.tscn` is a dependency it
resolves by name. The Lux check moves off the `addons/lux` string -- which
localization removes **by design**, so the old test would have layered the dev
rig on top of Lux's own lighting and washed out the applied look -- onto the
presence of `presentation/lux.applied.tscn`, which is what `write_entry_scene`
itself keys on.

## What this does not fix

**Spawn.** `lux.applied.tscn` carries zero markers and zero `LT_*` hooks, so
`_spawn_from_scene` falls back to the origin. It already did: today's preview
reports `default (no markers) (x=0.0, y=1.5, z=3.0)`. Markers live in
`site_walk.tscn`, which is the evaluation scene and explicitly not what ships.
Wrapping the export neither causes this nor cures it, and putting a shipped
spawn point in the package is a separate decision about what the deliverable
owes its consumer.

`build_walk_preview` still accepts any content directory. Its unit tests pass
synthetic ones and keep passing; what changed is what `cmd_walk` hands it.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

WP = Path("level_factory") / "packages" / "preview" / "walk_preview.py"
CMDS = Path("level_factory") / "apps" / "cli" / "commands" / "__init__.py"
SIDECAR = ".pre_walkexport"


FIND_OLD = '''def _find_level_scene(content_dir: Path) -> str | None:
    """The drop-in content scene: the .tscn that is neither the package's
    ``*_main.tscn`` harness nor a ``*_walk.tscn`` preview. Prefer ``site.tscn``."""
    tscns = [p.name for p in sorted(content_dir.glob("*.tscn"))
             if not p.name.endswith("_main.tscn")
             and not p.name.endswith("_walk.tscn")]
    # Prefer the Lux-applied scene when the art pass produced one: walking the
    # final runtime look beats walking the unlit compose intermediate.
    if "site_lux.tscn" in tscns:
        return "site_lux.tscn"
    if "site.tscn" in tscns:
        return "site.tscn"
    return tscns[0] if tscns else None'''

FIND_NEW = '''#: The entry `write_entry_scene` synthesizes in an export. A plain Node3D whose
#: script instances the level -- "Self-contained (no addons)", in its own words.
ENTRY_SCENE = "mission.tscn"


def _find_level_scene(content_dir: Path) -> str | None:
    """The scene to walk: the export's entry, else the drop-in content scene.

    ``mission.tscn`` comes first because in an export root it IS the level, and
    `site.tscn` beside it is a dependency the presentation scene resolves by
    name rather than a second level standing next to it -- `write_entry_scene`
    makes that call and this defers to it instead of making it again.

    The `site_lux.tscn` preference below is KEPT AND DEAD, deliberately.
    `lux_apply` writes `lux.applied.tscn`; nothing has ever written this name,
    which is why the branch never fired. It stays because deleting it would
    erase the evidence that the two halves of this contract were never the same
    string -- and because the fix was not to satisfy it. The applied scene
    references `res://addons/lux/` six times and renders nothing without the
    Lux checkout on disk; the export localizes that, and walking the export is
    how the preview gets the lit look without an instrument escaping.
    """
    tscns = [p.name for p in sorted(content_dir.glob("*.tscn"))
             if not p.name.endswith("_main.tscn")
             and not p.name.endswith("_walk.tscn")]
    if ENTRY_SCENE in tscns:
        return ENTRY_SCENE
    if "site_lux.tscn" in tscns:
        return "site_lux.tscn"
    if "site.tscn" in tscns:
        return "site.tscn"
    return tscns[0] if tscns else None'''


LUX_OLD = '''    has_lux = False
    try:
        has_lux = "addons/lux" in (dest / level).read_text(encoding="utf-8")
    except OSError:
        pass'''

LUX_NEW = '''    # WHO OWNS THE LIGHT. This used to grep the level scene for `addons/lux`,
    # which works on a lux_apply intermediate and is exactly wrong on an export:
    # `localize_export` removes that string BY DESIGN -- a portable package
    # carries no addons by contract. The old test would have found nothing,
    # added the dev rig on top of Lux's own WorldEnvironment, and washed out the
    # applied look it was written to protect.
    #
    # So it asks the question the export answers: is there a presentation scene
    # in here. That is the same thing `write_entry_scene` keys on when it
    # decides what `mission.tscn` instances, so the two cannot disagree.
    has_lux = (dest / "presentation" / "lux.applied.tscn").is_file()
    if not has_lux:
        try:
            has_lux = "addons/lux" in (dest / level).read_text(encoding="utf-8")
        except OSError:
            pass'''


WALK_OLD = '''    ws = _ws(args)
    mission_id = args.mission_id
    content_dir, source_stage = walk_content_dir(ws.jobs_dir, mission_id)
    if content_dir is None:
        print(f"no walkable level for {mission_id}; run `run {mission_id} "
              f"--art` first", file=sys.stderr)
        return EXIT_BLOCKED'''

WALK_NEW = '''    ws = _ws(args)
    mission_id = args.mission_id
    content_dir, source_stage = walk_content_dir(ws.jobs_dir, mission_id)
    if content_dir is None:
        print(f"no walkable level for {mission_id}; run `run {mission_id} "
              f"--art` first", file=sys.stderr)
        return EXIT_BLOCKED

    # WALK WHAT SHIPS. The job outputs are an intermediate: `lux.applied.tscn`
    # references `res://addons/lux/` six times and renders nothing without the
    # Lux checkout on disk, which PIPELINE_MAP calls "an instrument that
    # escaped". `export_mission` localizes that, `scan_closure` judges it, and
    # `write_entry_scene` writes a `mission.tscn` whose own comment says
    # "Self-contained (no addons)". Wrapping the export is how the preview shows
    # the lit look without carrying a tool into it.
    #
    # By CALLING `cmd_export` rather than reassembling its inputs. The handoff
    # dir, composed root, lux dir, addon sources, layer set and functional-lock
    # regression check are seventy lines of decisions; a second copy of them
    # here is the defect this file keeps finding in other people's code.
    #
    # A consequence, stated rather than left to be discovered: an export blocked
    # by the regression check now blocks the walk. That is the right way round.
    # A package that failed its own gate is not a thing to go and form opinions
    # about.
    import copy as _copy
    export_args = _copy.copy(args)
    export_args.mode = "portable-godot"
    export_args.format = "dir"
    export_args.include_walk = False
    code = cmd_export(export_args)
    if code != EXIT_OK:
        print(f"walk needs an export and the export was refused; fix that "
              f"first", file=sys.stderr)
        return code
    export_dir = ws.internal_dir / "exports" / f"{mission_id}.portable-godot"
    if (export_dir / "mission.tscn").is_file():
        content_dir, source_stage = export_dir, "export (portable-godot)"
    else:
        print(f"[walk] the export produced no {export_dir / 'mission.tscn'}; "
              f"falling back to {source_stage}", file=sys.stderr)'''


EDITS = {
    WP: ((FIND_OLD, FIND_NEW), (LUX_OLD, LUX_NEW)),
    CMDS: ((WALK_OLD, WALK_NEW),),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def _explain() -> int:
    sys.path.insert(0, str(Path.cwd() / "level_factory"))
    from packages.preview import walk_preview as wp
    if not hasattr(wp, "ENTRY_SCENE"):
        print("  unpatched: `walk` wraps <mission>.themed_site_assemble/out --")
        print("  a job intermediate. Its lux scene references res://addons/lux")
        print("  six times and renders nothing without the Lux checkout on")
        print("  disk. PIPELINE_MAP: 'an instrument that escaped'.")
        return 0
    print(f"  the export entry   {wp.ENTRY_SCENE}")
    print("  preference order   mission.tscn, site_lux.tscn (dead), site.tscn")
    print()
    print("  `walk` now runs `export --mode portable-godot` first and wraps")
    print("  its output, so the preview shows the localized, closure-checked")
    print("  package rather than the job intermediate.")
    return 0


def _verify(preview: Path) -> int:
    import json
    print(f"  {preview}")
    entry = preview / "mission.tscn"
    pres = preview / "presentation" / "lux.applied.tscn"
    addons = preview / "addons"
    walk = preview / "walk.tscn"

    print(f"    mission.tscn                 "
          f"{'present' if entry.is_file() else 'absent  <- not an export'}")
    print(f"    presentation/lux.applied     "
          f"{'present' if pres.is_file() else 'absent'}")
    stray = sorted(p.name for p in addons.iterdir()) if addons.is_dir() else []
    print(f"    addons/                      "
          f"{'ABSENT (correct)' if not stray else 'PRESENT: ' + ', '.join(stray)}")

    bad = 0
    if stray:
        print("    A portable package carries no addons by contract. Something")
        print("    copied one in.")
        bad = 1
    if pres.is_file():
        text = pres.read_text(encoding="utf-8", errors="replace")
        leaked = sorted(set(
            line.split('path="')[1].split('"')[0]
            for line in text.splitlines()
            if line.startswith("[ext_resource") and "addons/" in line))
        if leaked:
            print(f"    LOCALIZATION INCOMPLETE: {len(leaked)} addon "
                  f"reference(s) survive, e.g. {leaked[0]}")
            bad = 1
        else:
            print("    every ext_resource is localized -- no addon references")

    scan = preview / "export_closure_scan.json"
    if scan.is_file():
        try:
            data = json.loads(scan.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        # THE KEYS THE JUDGE ACTUALLY WRITES. A first draft of this guessed
        # `unresolved` / `missing`, found neither, and printed "clean" over a
        # scan whose `ok` was False and whose `missing_resource_count` was 21.
        # A verify that reports a verdict it did not read is worse than one
        # that reports nothing: it looks like a check and is a decoration.
        # So an unreadable or unrecognised scan FAILS rather than passes.
        if data is None or "ok" not in data:
            print("    closure verdict              UNREADABLE -- this file "
                  "is not the shape scan_closure writes")
            bad = 1
        else:
            issues = data.get("issues") or []
            missing = int(data.get("missing_resource_count") or 0)
            print(f"    closure verdict              "
                  f"{'clean' if data.get('ok') else 'BROKEN'}"
                  f"   ({data.get('resource_count', '?')} resources, "
                  f"{missing} missing, "
                  f"{data.get('required_plugin_count', '?')} plugin(s), "
                  f"{data.get('required_autoload_count', '?')} autoload(s))")
            for issue in issues[:6]:
                detail = issue if isinstance(issue, str) else (
                    issue.get("detail") or issue.get("reference")
                    or json.dumps(issue))
                print(f"      {detail}")
            if len(issues) > 6:
                print(f"      ... and {len(issues) - 6} more")
            if not data.get("ok"):
                bad = 1
    if walk.is_file():
        wtext = walk.read_text(encoding="utf-8", errors="replace")
        wraps = "mission.tscn" if "mission.tscn" in wtext else "something else"
        rig = "preview rig present" if "PreviewLighting" in wtext else \
              "no rig -- Lux owns the light"
        print(f"    walk.tscn wraps              {wraps}   ({rig})")
    return bad


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to a built preview dir")
        return _verify(Path(argv[i + 1]))

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  python $LF -C lot-demo-ws walk lot_demo_001")
        print("  python patch_lf_walk_the_export.py --verify \\")
        print("    lot-demo-ws\\.level_factory\\preview\\lot_demo_001_walk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
