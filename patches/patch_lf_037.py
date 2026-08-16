r"""level_factory 0.37.0 -- the package that opened to nothing, and passed.

    python patches\patch_lf_037.py --check
    python patches\patch_lf_037.py
    python patches\patch_lf_037.py --selftest
    python patches\patch_lf_037.py --revert

Run from the FACTORY ROOT. Roadmap item 47, stage 3.

WHAT A REAL EXPORT PRODUCED

The first art-unlit package built from a real mission -- lot_demo_001, 180
files, 28.6 MB of themed geometry -- opened to an empty scene. Its entire
entry:

    func _ready() -> void:
        print('scene instantiated ok')

No `load()`, no `add_child()`. The lit package's entry has a
`load('res://presentation/lux.applied.tscn')` block; the unlit one has
nothing where that block would be.

AND EVERY INSTRUMENT AGREED IT WAS FINE

    export_closure_scan.json: {"ok": true, "resource_count": 6,
                               "missing_resource_count": 0}

Six resources, in a 180-file package. Closure walks FROM the entry scene, and
an entry that references nothing is trivially closed -- the emptier the
package, the more certainly it passes. The portability test would have agreed
too: `mission.tscn` prints `scene instantiated ok` whether or not it added a
child. Three green readings over an empty level.

WHY IT WAS EMPTY

There is no `site.tscn` at the export root -- in EITHER package.
`themed_site_assemble` writes one (31,872 bytes on lot_demo_001), and it is
exported into nothing. The lit package gets away with it because
`presentation/lux.applied.tscn` is Lux's output OVER that assembly and so
stands in for it. Drop Lux and the five `lot/<archetype>/site.tscn` packages
are left with nothing that positions them.

`write_entry_scene`'s `elif site.exists()` could never have caught this: the
file it looks for was never in the package. 0.36.0's docstring correction
described that fallback as correct for art-unlit, and it would have been --
if the file were there.

TWO CHANGES, AND THE SECOND IS THE ONE THAT GENERALISES

1. THE ASSEMBLY SCENE SHIPS. `themed_site_assemble`'s `site.tscn` is copied
   to the package root for every mode that carries art. It is copied AFTER
   the composed root, deliberately: `_root_site_wanted` may have let the
   composer's own root `site.tscn` through, and for a single-shell mission
   that file is the composed BUILDING while this one is the assembled SITE.
   Lux is run against the assembly, so a reference to `res://site.tscn` must
   resolve to the assembly.

   This is NOT the RETRACTED position in export.py's long comment. That
   argument is about the COMPOSER's root site.tscn, whose `art/dressing`,
   `art/fixtures` and `art/zoo` are empty for a themed mission and which
   arrives referencing twenty modules that exist nowhere -- measured, 21
   unresolved of 40. This is a different file from a different stage, and its
   references are the five `lot/<archetype>/site.tscn` that the package
   already contains and that closure already reroots.

2. AN ENTRY THAT INSTANCES NOTHING IS AN ERROR. `write_entry_scene` raises
   rather than writing an entry with an empty body. It knows nothing about
   modes, so a mode nobody has written yet cannot ship hollow either. This is
   the general guard; change 1 is the specific repair, and change 1 alone
   would have left the next empty package to be found by somebody opening it.

   `export_closure.json` also now records `entry_instances` -- what the entry
   actually names -- so the artifact answers the question rather than
   requiring someone to read the scene.

WHAT THE EXISTING TESTS COULD NOT SEE

0.36.0's fourteen tests build their handoff fixture with a `site.tscn` in it,
so the base copy always put one at the export root and every package had
something to instance. The fixture was accidentally healthier than a real
mission. The new tests build one WITHOUT that file, which is the shape
lot_demo_001 actually has.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPORT = "level_factory/packages/exporting/export.py"
LOCALIZE = "level_factory/packages/exporting/localize.py"
CMDS = "level_factory/apps/cli/commands/__init__.py"
NEW_TEST = "level_factory/tests/unit/test_entry_content.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_037"

OLD_V, NEW_V = "0.36.0", "0.37.0"

EDITS: list[tuple[str, str, str]] = [
    # ------------------------------------------------- the guard's exception
    (LOCALIZE,
     "@dataclass\nclass LocalizeReport:\n",

     "class ExportContentError(RuntimeError):\n"
     '    """A package has nothing for its entry scene to instance.\n'
     "\n"
     "    Raised rather than returned because there is no partial success\n"
     "    here: an export that writes an entry adding no children produces a\n"
     "    package that opens to an empty level and passes every check that\n"
     "    starts from the entry.\n"
     '    """\n'
     "\n"
     "\n"
     "@dataclass\nclass LocalizeReport:\n"),

    (LOCALIZE,
     "    entry_scene: str | None = None\n",

     "    entry_scene: str | None = None\n"
     "    #: What the entry actually INSTANCES. Recorded because\n"
     "    #: `entry_scene` only ever says `mission.tscn`, which is true of a\n"
     "    #: package that opens to nothing.\n"
     "    entry_instances: list[str] = field(default_factory=list)\n"),

    (LOCALIZE,
     '            "entry_scene": self.entry_scene,\n',

     '            "entry_scene": self.entry_scene,\n'
     '            "entry_instances": list(self.entry_instances),\n'),

    (LOCALIZE,
     "    if pres.exists():\n"
     '        candidates.append("presentation/lux.applied.tscn")\n'
     "    elif site.exists():\n"
     '        candidates.append("site.tscn")\n'
     "    lines = \"\"\n",

     "    if pres.exists():\n"
     '        candidates.append("presentation/lux.applied.tscn")\n'
     "    elif site.exists():\n"
     '        candidates.append("site.tscn")\n'
     "    # AN ENTRY THAT INSTANCES NOTHING IS NOT AN ENTRY.\n"
     "    #\n"
     "    # Measured 2026-08-15 on lot_demo_001. An art-unlit export held 180\n"
     "    # files and 28.6 MB of themed geometry, no scene at the root that\n"
     "    # placed any of it, and a mission.tscn whose _ready() only printed.\n"
     "    # Everything agreed it was fine: export_closure_scan.json said\n"
     "    # `ok: true` with `resource_count: 6`, because closure walks FROM\n"
     "    # the entry and an entry that references nothing is trivially\n"
     "    # closed. The emptier the package, the more certainly it passed.\n"
     "    #\n"
     "    # This knows nothing about export modes on purpose. A mode nobody\n"
     "    # has written yet cannot ship hollow either.\n"
     "    if not candidates:\n"
     "        raise ExportContentError(\n"
     '            f"{export_dir.name}: nothing for the entry scene to "\n'
     '            f"instance -- no presentation/lux.applied.tscn and no "\n'
     '            f"site.tscn. A package whose entry adds no children opens "\n'
     '            f"to an empty level, and closure passes it because there "\n'
     '            f"is nothing left to fail on.")\n'
     "    lines = \"\"\n"),

    (LOCALIZE,
     '    report.entry_scene = "mission.tscn"\n'
     '    return "mission.tscn"\n',

     '    report.entry_scene = "mission.tscn"\n'
     "    report.entry_instances = list(candidates)\n"
     '    return "mission.tscn"\n'),

    # ------------------------------------------------ the assembly scene
    (EXPORT,
     "    # 3. Source authoring (only in source mode).\n",

     "    # 2.5 THE ASSEMBLY SCENE.\n"
     "    #\n"
     "    # `themed_site_assemble` is the stage that makes a PLACE -- Lot re-run\n"
     "    # over the composed buildings at the placements the graybox candidate\n"
     "    # was judged on -- and its `site.tscn` was exported into nothing. The\n"
     "    # lit package got away with that because\n"
     "    # `presentation/lux.applied.tscn` is Lux's output OVER the assembly\n"
     "    # and stands in for it. Drop Lux and the `lot/<archetype>/site.tscn`\n"
     "    # packages are left with nothing that positions them: measured on\n"
     "    # lot_demo_001, an art-unlit export of 180 files whose entry\n"
     "    # instanced nothing at all.\n"
     "    #\n"
     "    # NOT the RETRACTED position in the comment above. That argument is\n"
     "    # about the COMPOSER's root site.tscn, whose art/dressing,\n"
     "    # art/fixtures and art/zoo are empty for a themed mission and which\n"
     "    # arrives referencing twenty modules that exist nowhere -- measured,\n"
     "    # 21 unresolved of 40. This is a different file from a different\n"
     "    # stage, and it names the five lot/<archetype>/site.tscn the package\n"
     "    # already carries.\n"
     "    #\n"
     "    # AFTER the composed copy, deliberately. `_root_site_wanted` may have\n"
     "    # let the composer's own root site.tscn through, and for a\n"
     "    # single-shell mission that file is the composed BUILDING while this\n"
     "    # is the assembled SITE. Lux is run against the assembly, so a\n"
     "    # reference to res://site.tscn has to resolve to the assembly.\n"
     "    if profile.mode != MODE_PURE_SHELL and themed_site_dir:\n"
     "        themed_scene = Path(themed_site_dir) / \"site.tscn\"\n"
     "        if themed_scene.is_file():\n"
     "            shutil.copy2(str(themed_scene), str(export_dir / \"site.tscn\"))\n"
     "\n"
     "    # 3. Source authoring (only in source mode).\n"),

    (EXPORT,
     "    presentation_dir: Path | None,\n",

     "    presentation_dir: Path | None,\n"
     "    themed_site_dir: Path | None = None,\n"),

    # ------------------------------------------------------------ the caller
    (CMDS,
     '    compose_root = (jobs_dir / f"{mission_id}.presentation_compose"\n'
     '                    / "out" / "presentation")\n',

     '    compose_root = (jobs_dir / f"{mission_id}.presentation_compose"\n'
     '                    / "out" / "presentation")\n'
     "    # The assembled themed SITE. Not the same thing as the composed\n"
     "    # building above it, and until 0.37.0 it reached no package.\n"
     '    themed_site_dir = jobs_dir / f"{mission_id}.themed_site_assemble" / "out"\n'),

    (CMDS,
     "        presentation_dir=presentation_dir, source_dir=source_dir,\n",

     "        presentation_dir=presentation_dir, source_dir=source_dir,\n"
     "        themed_site_dir=(themed_site_dir if themed_site_dir.exists()\n"
     "                         else None),\n"),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""A package must have something for its entry to instance.

Written after the first real art-unlit export -- lot_demo_001, 180 files,
28.6 MB of themed geometry -- opened to an empty scene, with
`export_closure_scan.json` reporting `ok: true` and `resource_count: 6`.
Closure walks from the entry, so an entry that references nothing is
trivially closed.

0.36.0's fixtures could not reproduce it: their handoff directory contains a
`site.tscn`, so the base copy always left something at the export root. These
build a mission WITHOUT that file, which is the shape a real one has.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.exporting.export import (  # noqa: E402
    MODE_ART_UNLIT, MODE_PORTABLE, ExportProfile, export_mission,
)
from packages.exporting.localize import (  # noqa: E402
    ExportContentError, write_entry_scene, LocalizeReport,
)


def _mission(root, *, with_lux=True):
    """Job directories shaped like a REAL art-passed mission.

    Note what the handoff does NOT contain: a root `site.tscn`. On
    lot_demo_001 the handoff carries mission JSON and the per-building
    packages, and the only scene that assembles them is Lux's output.
    """
    handoff = root / "handoff"
    handoff.mkdir(parents=True)
    (handoff / "mission_manifest.json").write_text("{}")

    lux = root / "lux_out"
    lux.mkdir(parents=True)
    if with_lux:
        (lux / "lux.applied.tscn").write_text("[gd_scene]\\n")
        (lux / "lux.quality.json").write_text("{}")

    composed = root / "composed"
    (composed / "lot" / "b1").mkdir(parents=True)
    (composed / "lot" / "b1" / "site.tscn").write_text("[gd_scene]\\n")
    (composed / "wall.glb").write_bytes(b"glTF")

    themed = root / "themed"
    themed.mkdir(parents=True)
    (themed / "site.tscn").write_text(
        '[gd_scene]\\n[ext_resource path="res://lot/b1/site.tscn"]\\n')
    return handoff, lux, composed, themed


def _export(root, mode, *, themed=True, with_lux=True):
    handoff, lux, composed, themed_dir = _mission(root / mode,
                                                  with_lux=with_lux)
    return export_mission(
        mission_id="m1", out_root=root / mode / "exports",
        profile=ExportProfile(mode=mode),
        handoff_dir=handoff, presentation_dir=lux, composed_root=composed,
        themed_site_dir=themed_dir if themed else None,
        source_dir=None, tool_versions={}, layers=frozenset({"art"}),
    )


# -------------------------------------------------------------- the guard

def test_an_entry_with_nothing_to_instance_raises(tmp_path):
    """THE BUG, as an exception instead of a silent empty package."""
    report = LocalizeReport()
    (tmp_path / "empty").mkdir()
    with pytest.raises(ExportContentError) as exc:
        write_entry_scene(tmp_path / "empty", report)
    assert "empty level" in str(exc.value)


def test_the_guard_does_not_fire_when_there_is_a_site(tmp_path):
    d = tmp_path / "ok"
    d.mkdir()
    (d / "site.tscn").write_text("[gd_scene]\\n")
    report = LocalizeReport()
    assert write_entry_scene(d, report) == "mission.tscn"
    assert report.entry_instances == ["site.tscn"]


def test_the_report_records_what_the_entry_instances(tmp_path):
    """`entry_scene` says `mission.tscn` for a hollow package too."""
    d = tmp_path / "lit"
    (d / "presentation").mkdir(parents=True)
    (d / "presentation" / "lux.applied.tscn").write_text("[gd_scene]\\n")
    report = LocalizeReport()
    write_entry_scene(d, report)
    assert report.entry_instances == ["presentation/lux.applied.tscn"]
    assert report.as_dict()["entry_instances"] == [
        "presentation/lux.applied.tscn"]


# ------------------------------------------------------- the assembly scene

def test_the_themed_site_reaches_the_package(tmp_path):
    result = _export(tmp_path, MODE_ART_UNLIT)
    assert (result.export_dir / "site.tscn").is_file()


def test_the_unlit_entry_instances_it(tmp_path):
    result = _export(tmp_path, MODE_ART_UNLIT)
    body = (result.export_dir / "mission.tscn").read_text()
    assert "res://site.tscn" in body
    assert "add_child" in body


def test_the_lit_entry_still_prefers_the_presentation_scene(tmp_path):
    result = _export(tmp_path, MODE_PORTABLE)
    body = (result.export_dir / "mission.tscn").read_text()
    assert "res://presentation/lux.applied.tscn" in body


def test_the_lit_package_also_carries_the_assembly(tmp_path):
    """It is what lux.applied.tscn was lit against; a single-shell mission's
    presentation scene names res://site.tscn directly."""
    result = _export(tmp_path, MODE_PORTABLE)
    assert (result.export_dir / "site.tscn").is_file()


def test_without_a_themed_site_an_unlit_export_refuses(tmp_path):
    """The old behaviour, now loud.

    No Lux output and no assembly is exactly what shipped 180 files and an
    empty scene. It raises rather than producing that package.
    """
    with pytest.raises(ExportContentError):
        _export(tmp_path, MODE_ART_UNLIT, themed=False, with_lux=False)


def test_the_closure_report_names_the_instance(tmp_path):
    result = _export(tmp_path, MODE_ART_UNLIT)
    report = json.loads(
        (result.export_dir / "export_closure.json").read_text())
    assert report["entry_instances"] == ["site.tscn"]
''',
}

ENTRY = """## [0.37.0] - the package that opened to nothing, and passed

The first art-unlit package built from a real mission -- lot_demo_001, 180
files, 28.6 MB of themed geometry -- opened to an empty scene. Its whole
entry was `print('scene instantiated ok')`: no `load()`, no `add_child()`.

EVERY INSTRUMENT AGREED IT WAS FINE

    export_closure_scan.json: {"ok": true, "resource_count": 6,
                               "missing_resource_count": 0}

Six resources in a 180-file package. Closure walks FROM the entry scene, so
an entry that references nothing is trivially closed -- the emptier the
package, the more certainly it passes. The portability test would have agreed
too, because `mission.tscn` prints its marker whether or not it added a
child.

WHY

There is no `site.tscn` at the export root, in EITHER package.
`themed_site_assemble` writes one -- 31,872 bytes on lot_demo_001 -- and it
reached no package. The lit export got away with it because
`presentation/lux.applied.tscn` is Lux's output OVER that assembly and stands
in for it. Drop Lux and the five `lot/<archetype>/site.tscn` packages have
nothing positioning them.

`write_entry_scene`'s `elif site.exists()` could never have caught this: the
file it looks for was never in the package. 0.36.0's docstring called that
fallback correct for art-unlit, and it would have been, if the file were
there.

TWO CHANGES

The assembly scene ships. `themed_site_assemble`'s `site.tscn` is copied to
the package root for every mode carrying art, AFTER the composed root --
`_root_site_wanted` may have let the composer's own root site.tscn through,
and for a single-shell mission that is the composed BUILDING while this is
the assembled SITE. Lux runs against the assembly, so `res://site.tscn` must
resolve to the assembly.

This is not the RETRACTED position in export.py's comment. That is about the
COMPOSER's root site.tscn, whose art/ directories are empty for a themed
mission and which arrives referencing twenty modules that exist nowhere
(measured: 21 unresolved of 40). Different file, different stage, and its
references are the five the package already carries.

An entry that instances nothing is an error. `write_entry_scene` raises
`ExportContentError` instead of writing an empty body. It knows nothing about
modes, so a mode nobody has written yet cannot ship hollow either -- the
repair is specific, this guard is general, and the repair alone would have
left the next empty package to be found by whoever opened it.
`export_closure.json` also records `entry_instances`, because `entry_scene`
says `mission.tscn` for a hollow package too.

WHAT THE OLD TESTS COULD NOT SEE

0.36.0's fourteen tests build a handoff containing `site.tscn`, so the base
copy always left something at the export root and every package had something
to instance. The fixture was accidentally healthier than a real mission. The
new tests build one without it.
"""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        eol = _eol(raw)
        out, done = raw.decode("utf-8"), 0
        for old, new in edits:
            old_f, new_f = _as(old, eol), _as(new, eol)
            if new_f in out:
                done += 1
                continue
            if out.count(old_f) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old_f)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old_f, new_f, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if p.suffix == ".py":
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
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

    for rel, content in NEW_FILES.items():
        p = root / rel
        data = content.encode("utf-8")
        if p.is_file():
            if p.read_bytes() == data:
                print(f"  already applied  {rel}")
                continue
            print(f"REFUSING: {rel} exists and is not what this patch writes")
            return 1
        try:
            compile(content, str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: {rel} -- does not parse: {exc}")
            return 1
        if check:
            print(f"  would create {rel}  {len(data):,} bytes")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print(f"  created      {rel}  {len(data):,} bytes  "
              f"sha256 {_sha(data)[:16]}")

    vp, cp = root / VERSION_F, root / CHANGELOG
    vraw, craw = vp.read_bytes(), cp.read_bytes()
    vbody, cbody = vraw.decode("utf-8"), craw.decode("utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V}")
        return 1
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  +{len(ENTRY) + 1:,} bytes")
        return 0
    for q, rawb in ((vp, vraw), (cp, craw)):
        side = q.with_suffix(q.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(rawb)
    vp.write_bytes(vbody.replace(OLD_V, NEW_V, 1).encode("utf-8"))
    ceol = _eol(craw)
    cp.write_bytes((_as(ENTRY, ceol) + _as("\n", ceol) + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
    import subprocess
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()

    def run(*paths):
        return subprocess.run([sys.executable, "-m", "pytest", *paths],
                              cwd=str(lf), capture_output=True, text=True)

    print("  the entry-content tests --")
    r = run("tests/unit/test_entry_content.py")
    for line in (r.stdout + r.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("A PACKAGE MUST HAVE SOMETHING TO INSTANCE", r.returncode == 0)

    print()
    print("  the export suite, including 0.36.0's fourteen --")
    r2 = run("tests/unit/test_art_unlit_export.py",
             "tests/unit/test_export_layers.py",
             "tests/unit/test_export_localize.py",
             "tests/unit/test_closure_export.py",
             "tests/unit/test_export_modes_agree.py")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THE EXPORT SUITE PASSES", r2.returncode == 0)

    print()
    print("  service + integration -- ~2.5 min --")
    r3 = run("tests/service", "tests/integration")
    for line in (r3.stdout + r3.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("STILL GREEN -- the lit package is unchanged in what it instances",
          r3.returncode == 0)

    loc = (root / LOCALIZE).read_text(encoding="utf-8")
    check("the guard raises rather than returning",
          "raise ExportContentError(" in loc)
    check("and it does not branch on the export mode",
          "MODE_" not in loc.split("def write_entry_scene")[-1])

    exp = (root / EXPORT).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in exp.splitlines()
                     if not ln.strip().startswith("#"))
    check("the assembly copy runs after the composed copy",
          code.index("themed_scene") > code.index("skip_dirs="))

    v = (root / VERSION_F).read_text(encoding="utf-8").strip()
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", v == NEW_V)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry records what closure said about the empty package",
          '"resource_count": 6' in flat)
    check("and separates this from the RETRACTED composer argument",
          "Different file, different stage" in flat)

    print()
    print("  NOT VERIFIED HERE: the real export. Re-run both and re-probe --")
    print("    python level_factory\\apps\\cli\\main.py -C <ws> export "
          "<mission> --mode portable-godot --format folder")
    print("    python level_factory\\apps\\cli\\main.py -C <ws> export "
          "<mission> --mode art-unlit --format folder")
    print("    python tools\\probe_unlit_ab.py <ws> <mission>")

    print()
    print("  a package has something to open"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        bad = 0
        for rel in (EXPORT, LOCALIZE, CMDS, VERSION_F, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        for rel, content in NEW_FILES.items():
            p = root / rel
            if not p.is_file():
                print(f"  already gone {rel}")
                continue
            if p.read_bytes() != content.encode("utf-8"):
                print(f"  KEPT (edited since) {rel}")
                bad = 1
                continue
            p.unlink()
            print(f"  removed      {rel}")
        return bad
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_037.py --selftest")
        print()
        print("  Then re-export BOTH modes and re-run the probe. The unlit")
        print("  entry must instance res://site.tscn; last time it instanced")
        print("  nothing and three checks called that fine.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
