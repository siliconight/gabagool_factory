r"""The portable export stops shipping a dead scene and two QA instruments.

    python patch_lf_export_closure.py --explain
    python patch_lf_export_closure.py --check
    python patch_lf_export_closure.py
    python patch_lf_export_closure.py --verify <export_dir>
    python patch_lf_export_closure.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## What was measured

`patch_lf_walk_the_export.py` pointed the walk preview at the export, and the
first build of one said:

    EXPORT_CLOSURE_BROKEN: 21 unresolved res:// reference(s)
      lot_navqa_setup.gd: unresolved res://addons/heist_nav_qa/nav_qa_director.gd
      site.tscn: unresolved res://art/zoo/doorway_rockay_03_w180_o0ddf9a.glb
      ... 19 more zoo modules

40 resources declared, **21 missing**. That is the exact failure the export's
own comment describes from 2026-08-01: *"the shell opened, applied Blue Hour
correctly, and rendered nothing but sky."*

## Defect 1 -- a root `site.tscn` whose assets do not exist anywhere

The export root carries `site.tscn` (47,458 bytes) copied from
`presentation_compose/out/presentation`. It references twenty
`res://art/zoo/*.glb`, and `art/` never arrives:

    presentation_compose/out/presentation/art/dressing   EMPTY
    presentation_compose/out/presentation/art/fixtures   EMPTY
    presentation_compose/out/presentation/art/zoo        EMPTY

`_copy_tree` walks FILES, so three empty directories copy as nothing. The
twenty modules are not missing from the export -- **they do not exist on disk at
all.** The real buildings' modules are present and correct under
`lot/<archetype>/art/zoo/`, one set per building, and those resolve.

So the root scene is dead weight. `lux.applied.tscn` does not reference it: its
ext_resources are the five `res://lot/<archetype>/site.tscn`, measured. And
`mission.tscn` instances `presentation/lux.applied.tscn`, not the root scene.

**This copy has been flip-flopped once already** and the retraction is still in
`export.py`: skipping `site.tscn` broke closure with
`lux.applied.tscn: unresolved res://site.tscn`, so it was put back. Both
positions were right for their own mission shape -- a single-shell compose
INLINES its geometry and the presentation scene does name `res://site.tscn`; a
themed multi-building site instances five packages and does not.

So neither position is copied here. **The presentation scene is asked.** If it
references `res://site.tscn`, the file ships; if it does not, it is not part of
the deliverable and neither are its dangling modules. One derivation, from the
artefact that knows, instead of a third guess in the same place.

## Defect 2 -- an instrument in the deliverable

`lot_navqa_setup.gd` and `site_navqa.tscn` ship in the package, and the first
of those references `res://addons/heist_nav_qa/nav_qa_director.gd`, which is not
there and must not be. `ENGINE_GATES.md` is explicit:

    `nav_qa_director.gd` and `mp_smoke.gd` are disposable QA harnesses, and
    neither may grow into a player controller.

`localize_export` already strips `*_walk.tscn` for exactly this reason --
"development chrome, not mission content" -- and `site_walk.tscn` is stripped
today. The nav QA pair is the same class of file and was never named, so it
went out with the shell. Stripped now, on the same rule, in the same place, and
reported in `stripped_scenes` so an export says what it removed.

## What this does not do

It does not make compose write its `art/`. Whether
`presentation_compose/out/presentation/art/` SHOULD be empty for a themed
multi-building mission is a real question about that job, and the answer is
probably yes -- the modules belong to the buildings and each building has
them -- but it is a question for the composer, not for the exporter. What the
exporter owes is not to ship a scene whose assets it does not have, and that is
what changes here.

It does not touch the single-shell path. A mission whose presentation scene
names `res://site.tscn` still gets it, still gets its modules, and still closes.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

EXPORT = Path("level_factory") / "packages" / "exporting" / "export.py"
LOCALIZE = Path("level_factory") / "packages" / "exporting" / "localize.py"
SIDECAR = ".pre_exportclosure"


# --------------------------------------------------------------------------
# export.py -- ask the presentation scene whether it wants the root site
# --------------------------------------------------------------------------

SITE_OLD = '''        _copy_tree(composed_root, export_dir,
                   skip={"project.godot", "HANDOFF.md",
                         "portable_resource_manifest.json",
                         "compose.summary.json",
                         "site_main.tscn"},
                   skip_dirs={".godot", "addons"})'''

SITE_NEW = '''        # site.tscn: ASKED, not decided here for a third time.
        #
        # The comment above records this being skipped, then un-skipped when
        # closure broke with `lux.applied.tscn: unresolved res://site.tscn`.
        # Both positions were right for their own mission shape. A single-shell
        # compose INLINES its geometry and its presentation scene DOES name
        # `res://site.tscn`. A themed multi-building site instances five
        # packages and names `res://lot/<archetype>/site.tscn` instead --
        # measured on lot_demo_001: five such refs, no `res://site.tscn`.
        #
        # Shipping it anyway is not free. The composer's `art/dressing`,
        # `art/fixtures` and `art/zoo` are EMPTY for a themed mission, and
        # `_copy_tree` walks files, so three empty directories copy as nothing
        # and the scene arrives referencing twenty modules that exist nowhere
        # on disk. Measured: EXPORT_CLOSURE_BROKEN, 21 unresolved of 40
        # resources. The buildings' own modules are fine under
        # `lot/<archetype>/art/zoo/` and resolve.
        #
        # So the presentation scene decides. It is the artefact that knows.
        # BY RELATIVE PATH, not by name. `skip` matches basenames anywhere in
        # the tree and a composed root holds `site.tscn` at its root AND one
        # per building under `lot/<id>/`; a name skip took all six, and the
        # presentation scene came back with five unresolved buildings.
        wanted = _root_site_wanted(presentation_dir)
        _copy_tree(composed_root, export_dir,
                   skip={"project.godot", "HANDOFF.md",
                         "portable_resource_manifest.json",
                         "compose.summary.json",
                         "site_main.tscn"},
                   skip_rel=set() if wanted else {"site.tscn"},
                   skip_dirs={".godot", "addons"})'''


HELPER_OLD = '''def _write_project_godot(export_dir: Path, entry_scene: str, mission_id: str) -> None:'''

HELPER_NEW = '''#: `res://site.tscn`, as an ext_resource line would carry it.
_ROOT_SITE_REF = re.compile(r'^\\[ext_resource[^\\]]*path="res://site\\.tscn"',
                            re.M)


def _root_site_wanted(presentation_dir: Path | None) -> bool:
    """Does the presentation scene reference the composer's root ``site.tscn``?

    TRUE WHEN THERE IS NO PRESENTATION SCENE TO ASK. A graybox export has no
    art pass, its entry IS `site.tscn` (`write_entry_scene` says so), and
    withholding it on the strength of a question nobody answered would ship an
    empty package. Absence of evidence decides toward including, always.
    """
    if presentation_dir is None:
        return True
    scene = Path(presentation_dir) / "lux.applied.tscn"
    if not scene.is_file():
        return True
    try:
        return bool(_ROOT_SITE_REF.search(
            scene.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return True


def _write_project_godot(export_dir: Path, entry_scene: str, mission_id: str) -> None:'''


IMPORT_OLD = '''import datetime as _dt
import shutil
import zipfile'''

IMPORT_NEW = '''import datetime as _dt
import re
import shutil
import zipfile'''


TREE_OLD = '''def _copy_tree(src: Path, dst: Path, *, skip: set[str] = frozenset(),
               skip_dirs: set[str] = frozenset()) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        if item.name in skip or item.name.endswith(".provenance.json"):
            continue
        rel = item.relative_to(src)'''

TREE_NEW = '''def _copy_tree(src: Path, dst: Path, *, skip: set[str] = frozenset(),
               skip_dirs: set[str] = frozenset(),
               skip_rel: set[str] = frozenset()) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        if item.name in skip or item.name.endswith(".provenance.json"):
            continue
        rel = item.relative_to(src)
        # `skip_rel` matches a RELATIVE PATH, which `skip` cannot: the note
        # below already says `skip` matches names, and a composed root holds
        # `site.tscn` at its root AND one per building under `lot/<id>/`.
        # Skipping by name took all six. Measured: five of them, and
        # `lux.applied.tscn: unresolved res://lot/<archetype>/site.tscn` x5,
        # with the review frame going from 88% void to 98% because every
        # building had left the package.
        if rel.as_posix() in skip_rel:
            continue'''


# --------------------------------------------------------------------------
# localize.py -- the nav QA harness is chrome, like the walk scenes
# --------------------------------------------------------------------------

STRIP_OLD = '''    if strip_walk:
        for walk in sorted(export_dir.rglob("*_walk.tscn")):
            report.stripped_scenes.append(walk.relative_to(export_dir).as_posix())
            walk.unlink()'''

STRIP_NEW = '''    if strip_walk:
        for walk in sorted(export_dir.rglob("*_walk.tscn")):
            report.stripped_scenes.append(walk.relative_to(export_dir).as_posix())
            walk.unlink()

    # THE NAV QA HARNESS IS THE SAME CLASS OF FILE and was never named, so it
    # shipped. `ENGINE_GATES.md`: "`nav_qa_director.gd` and `mp_smoke.gd` are
    # disposable QA harnesses, and neither may grow into a player controller."
    #
    # Measured on lot_demo_001's portable export: `lot_navqa_setup.gd` shipped
    # and referenced `res://addons/heist_nav_qa/nav_qa_director.gd`, which a
    # portable package cannot contain by contract -- one of 21 unresolved
    # references. An instrument in the deliverable, and a dangling one.
    #
    # Stripped unconditionally, not under `strip_walk`. That flag exists so a
    # profile can ASK for the walk scene; nothing asks for the QA harness, and
    # a parameter nobody passes is an unfinished thought. If a caller ever
    # wants it, it gets its own flag and its own reason.
    for name in _QA_HARNESS_FILES:
        for stray in sorted(export_dir.rglob(name)):
            report.stripped_scenes.append(
                stray.relative_to(export_dir).as_posix())
            stray.unlink()'''


QA_OLD = '''def localize_export(export_dir: Path, *, addon_sources: dict[str, Path],'''

QA_NEW = '''#: Disposable QA harnesses that have no business in a deliverable.
#: `site_navqa.tscn` is Lot's nav-QA scene and `lot_navqa_setup.gd` is the
#: script that wires it to `res://addons/heist_nav_qa/nav_qa_director.gd` --
#: an addon a portable package cannot carry by contract. `mp_smoke*` is named
#: alongside them in ENGINE_GATES and is listed here for the same reason,
#: whether or not a given mission emits one.
_QA_HARNESS_FILES = ("site_navqa.tscn", "lot_navqa_setup.gd",
                     "mp_smoke.gd", "mp_smoke_node.gd")


def localize_export(export_dir: Path, *, addon_sources: dict[str, Path],'''


EDITS = {
    EXPORT: ((IMPORT_OLD, IMPORT_NEW), (TREE_OLD, TREE_NEW),
             (HELPER_OLD, HELPER_NEW), (SITE_OLD, SITE_NEW)),
    LOCALIZE: ((QA_OLD, QA_NEW), (STRIP_OLD, STRIP_NEW)),
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
    from packages.exporting import export as ex
    from packages.exporting import localize as lo
    if not hasattr(ex, "_root_site_wanted"):
        print("  unpatched: the composer's root site.tscn ships unconditionally")
        print("  and the nav QA harness ships with the shell. Measured on")
        print("  lot_demo_001: 21 of 40 resources unresolved -- 20 zoo modules")
        print("  the compose art/ dirs are EMPTY of, and one addon script.")
        return 0
    print("  root site.tscn ships only when the presentation scene names it")
    print(f"  QA harness stripped: {', '.join(lo._QA_HARNESS_FILES)}")
    print()
    print("  no presentation dir -> ships (a graybox export IS site.tscn):",
          ex._root_site_wanted(None))
    return 0


def _verify(export_dir: Path) -> int:
    print(f"  {export_dir}")
    bad = 0
    for name in ("site_navqa.tscn", "lot_navqa_setup.gd", "mp_smoke.gd"):
        hits = sorted(p.relative_to(export_dir).as_posix()
                      for p in export_dir.rglob(name))
        print(f"    {name:<22} "
              f"{'absent (correct)' if not hits else 'PRESENT: ' + hits[0]}")
        if hits:
            bad = 1

    pres = export_dir / "presentation" / "lux.applied.tscn"
    root = export_dir / "site.tscn"
    if pres.is_file():
        names_it = bool(re.search(
            r'^\[ext_resource[^\]]*path="res://site\.tscn"',
            pres.read_text(encoding="utf-8", errors="replace"), re.M))
        print(f"    presentation names root site.tscn   {names_it}")
        print(f"    root site.tscn present              {root.is_file()}")
        if root.is_file() and not names_it:
            # DEAD WEIGHT, NOT A DEFECT, and a first draft of this called it
            # one -- it printed "SHIPPED BUT UNREFERENCED, this is the 20
            # dangling modules" and exited 1 over an export the scanner had
            # just called clean, 38 resources and 0 missing.
            #
            # The two are different facts. After the fix, the root `site.tscn`
            # is the THEMED site from the functional base, not the composer's
            # single-building scene, and its own references resolve. It is
            # unreferenced because `mission.tscn` instances the presentation
            # scene, which is `write_entry_scene`'s decision and correct. Some
            # 47 KB of alternative entry is worth a note, not a failure.
            #
            # Whether it dangles is what the closure scan below answers, and
            # that is the line to read.
            print("      unreferenced -- mission.tscn instances the "
                  "presentation scene instead. Dead weight, not a defect; the "
                  "closure verdict below is what says whether it dangles.")
    scan = export_dir / "export_closure_scan.json"
    if scan.is_file():
        try:
            data = json.loads(scan.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if data is None or "ok" not in data:
            print("    closure verdict        UNREADABLE")
            bad = 1
        else:
            print(f"    closure verdict        "
                  f"{'clean' if data.get('ok') else 'BROKEN'}"
                  f"   ({data.get('resource_count', '?')} resources, "
                  f"{data.get('missing_resource_count', '?')} missing)")
            for issue in (data.get("issues") or [])[:6]:
                print(f"      {issue if isinstance(issue, str) else issue}")
            if not data.get("ok"):
                bad = 1
    return bad


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to an export dir")
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
        print("  python patch_lf_export_closure.py --verify \\")
        print("    lot-demo-ws\\.level_factory\\exports\\"
              "lot_demo_001.portable-godot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
