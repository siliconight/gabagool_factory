r"""Level Factory 0.39.0 -- roadmap 49: the composed root lands where the
assembly scene says it does.

    python patches\\patch_lf_039.py --check
    python patches\\patch_lf_039.py
    python patches\\patch_lf_039.py --selftest
    python patches\\patch_lf_039.py --revert

Run from the FACTORY ROOT.

    packages/exporting/export.py   `_assembly_building_dir`, and the copy
                                   destination that uses it
    tests/unit/test_assembly_building_dir.py   new
    VERSION, CHANGELOG.md          0.38.0 -> 0.39.0

VERIFY IT ON THE REAL PACKAGE, not just here. Every job in the 3b workspace is
cached, so this is seconds and needs no Blender or Godot:

    $ws = "workspaces\\unlit-3b-ws"
    python level_factory\\apps\\cli\\main.py -C $ws export unlit_probe_001 --mode art-unlit --format folder
    python level_factory\\apps\\cli\\main.py -C $ws export unlit_probe_001 --mode portable-godot --format folder

BEFORE: both report EXPORT_CLOSURE_BROKEN, `site.tscn: relative ext_resource
resolves to nothing: lot/shell/site.tscn`, resource_count 2 of 56 files.
AFTER: `"ok": true` and a resource_count in the thirties. If the count is
still 2, this patch did not do what it claims and the selftest below is
lying about something.

THE DISCRIMINATOR IS READ, NOT INFERRED. The first design for this used
`_root_site_wanted(presentation_dir)` as the single-shell test. It is not
one -- it returns True whenever there is no Lux scene to ask, so on a mission
that never ran Lux it is True for the wrong reason and would misfire on
exactly the packages this fixes. The assembly scene names the directory it
needs; `_assembly_building_dir` reads it.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

LF = "level_factory"
EXPORT = f"{LF}/packages/exporting/export.py"
TESTF = f"{LF}/tests/unit/test_assembly_building_dir.py"
VERSION = f"{LF}/VERSION"
CHANGELOG = f"{LF}/CHANGELOG.md"
SIDECAR = ".pre_039"
OLD_VER, NEW_VER = "0.38.0", "0.39.0"

#: The export.py this was written against. Reported, not enforced: the anchors
#: refuse on drift by themselves, and a hash gate would block a file that had
#: moved for an unrelated reason in a way the anchors would have handled.
SOURCE_SHA = "5303e3d0cf6a2999"

OLD_COPY = '        wanted = _root_site_wanted(presentation_dir)\n        _copy_tree(composed_root, export_dir,\n                   skip={"project.godot", "HANDOFF.md",\n                         "portable_resource_manifest.json",\n                         "compose.summary.json",\n                         "site_main.tscn"},\n                   skip_rel=set() if wanted else {"site.tscn"},\n                   skip_dirs={".godot", "addons"})'
NEW_COPY = '        wanted = _root_site_wanted(presentation_dir)\n        # WHERE THE COMPOSED ROOT LANDS. Roadmap 49.\n        #\n        # It used to land at the package root, always. That is right for a\n        # VARIED lot, whose composed root already holds `lot/<archetype>/`\n        # per building and whose references therefore resolve. It is wrong\n        # for a SINGLE-SHELL mission: there the composed root IS the one\n        # building, flat -- `site.tscn`, `site_base.glb`, `art/` -- and step\n        # 2.5 below then overwrites the root `site.tscn` with the ASSEMBLY\n        # scene, whose only `ext_resource` is `lot/<id>/site.tscn`. Nothing\n        # ever created that directory in the package, so every single-shell\n        # themed export since 0.37.0 has shipped a level that cannot open,\n        # in BOTH modes. Measured on unlit_probe_001: 56 files, entry\n        # reaches 2.\n        #\n        # ASK THE ARTEFACT, do not infer the mission shape. The assembly\n        # scene names the path it needs and `site_packages.py` has already\n        # staged exactly that directory beside it; `_assembly_building_dir`\n        # reads the name out of the scene rather than guessing from a flag.\n        # `_root_site_wanted` is NOT that test and was briefly mistaken for\n        # it: it returns True whenever there is no Lux scene to ask, which\n        # on a mission that never ran Lux is every time.\n        building_rel = _assembly_building_dir(themed_site_dir, composed_root)\n        dest = (export_dir / building_rel) if building_rel else export_dir\n        # AND THE COMPOSER\'S OWN site.tscn IS WANTED when it is going under\n        # `lot/<id>/`, because there it IS the building the assembly names.\n        # Skipping it would recreate the same dangling reference one\n        # directory down.\n        _copy_tree(composed_root, dest,\n                   skip={"project.godot", "HANDOFF.md",\n                         "portable_resource_manifest.json",\n                         "compose.summary.json",\n                         "site_main.tscn"},\n                   skip_rel=(set() if (wanted or building_rel)\n                             else {"site.tscn"}),\n                   skip_dirs={".godot", "addons"})'
HELPER = '#: One `lot/<id>/site.tscn` reference in an assembly scene. The id is whatever\n#: `_write_site_spec` put there -- a literal "shell" on the single-shell branch,\n#: an archetype id on the varied one -- so this reads it rather than assuming.\n_LOT_SITE_REF = re.compile(r\'path="(lot/([^"/]+)/site\\.tscn)"\')\n\n\ndef _assembly_building_dir(themed_site_dir, composed_root) -> str:\n    """``"lot/<id>"`` when the composed root belongs under it, else ``""``.\n\n    ROADMAP 49. Returns non-empty only when ALL of these hold, and each one\n    is a fact read off disk rather than a guess about the mission:\n\n      * there is an assembly scene (`themed_site_assemble`\'s `site.tscn`)\n      * it names exactly ONE `lot/<id>/site.tscn` -- more than one is a varied\n        lot, which the composed root already carries and which this must not\n        touch\n      * the composed root has no `lot/` of its own -- if it does, it is that\n        varied lot and its buildings are already in the right place\n\n    Returns a POSIX-style relative string because it is joined onto a Path by\n    the caller and compared in tests; `Path` would make the test assertion\n    platform-dependent for no benefit.\n\n    Never raises. An unreadable assembly scene answers "" -- the previous\n    behaviour -- because a copy destination is not the place to discover a\n    corrupt scene, and the closure scan reports it a few lines later with the\n    detail this function does not have.\n    """\n    if not themed_site_dir:\n        return ""\n    scene = Path(themed_site_dir) / "site.tscn"\n    if not scene.is_file():\n        return ""\n    if composed_root and (Path(composed_root) / "lot").is_dir():\n        return ""\n    try:\n        text = scene.read_text(encoding="utf-8", errors="replace")\n    except OSError:\n        return ""\n    hits = {m.group(1) for m in _LOT_SITE_REF.finditer(text)}\n    if len(hits) != 1:\n        return ""\n    return str(next(iter(hits))).rsplit("/", 1)[0]\n\n\n'
HELPER_ANCHOR = 'def _root_site_wanted(presentation_dir: Path | None) -> bool:'
TEST_SRC = '"""Roadmap 49: the composed root lands where the assembly scene says it does.\n\n`export_mission` copies the composed root into the package. Where it lands\nused to be unconditional -- the package root -- which is right for a varied\nlot (its composed root already holds `lot/<archetype>/` per building) and\nwrong for a single-shell mission, where the composed root IS the one building\nlaid flat. Step 2.5 then overwrites the root `site.tscn` with the ASSEMBLY\nscene, whose only `ext_resource` is `lot/<id>/site.tscn` -- a directory\nnothing put in the package. Measured on unlit_probe_001, 2026-08-16: 56 files\nshipped, the entry reached 2, EXPORT_CLOSURE_BROKEN in BOTH portable-godot\nand art-unlit. Every single-shell themed export since 0.37.0 was unopenable.\n\nThese test `_assembly_building_dir`, which decides it. Each case is a fact it\nreads off disk, so each test writes that fact and asserts the answer.\n\nRun:  python -m pytest tests/unit/test_assembly_building_dir.py\n"""\nfrom pathlib import Path\n\nfrom packages.exporting.export import _assembly_building_dir\n\n\ndef _assembly(tmp: Path, body: str) -> Path:\n    d = tmp / "themed"\n    d.mkdir(parents=True, exist_ok=True)\n    (d / "site.tscn").write_text(body, encoding="utf-8")\n    return d\n\n\nONE = (\'[gd_scene load_steps=2 format=3]\\n\\n\'\n       \'[ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]\\n\')\nFIVE = \'[gd_scene format=3]\\n\' + "".join(\n    f\'[ext_resource type="PackedScene" path="lot/a0{i}/site.tscn" id="b{i}"]\\n\'\n    for i in range(1, 6))\n\n\ndef test_a_single_reference_names_its_directory(tmp_path):\n    themed = _assembly(tmp_path, ONE)\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(themed, composed) == "lot/shell"\n\n\ndef test_the_id_is_read_not_assumed(tmp_path):\n    """`shell` is a literal on one code branch, not a universal name."""\n    themed = _assembly(tmp_path, ONE.replace("lot/shell/", "lot/depot_a01/"))\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(themed, composed) == "lot/depot_a01"\n\n\ndef test_a_varied_lot_is_left_alone(tmp_path):\n    """Five references is a varied lot; its composed root already carries the\n    buildings and moving it would break what works."""\n    themed = _assembly(tmp_path, FIVE)\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(themed, composed) == ""\n\n\ndef test_a_composed_root_that_already_has_lot_is_left_alone(tmp_path):\n    """The second guard, and it is not redundant with the first: a composed\n    root holding `lot/` is the varied shape even if the scene names one."""\n    themed = _assembly(tmp_path, ONE)\n    composed = tmp_path / "composed"\n    (composed / "lot" / "shell").mkdir(parents=True)\n    assert _assembly_building_dir(themed, composed) == ""\n\n\ndef test_no_assembly_scene_changes_nothing(tmp_path):\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(tmp_path / "nope", composed) == ""\n    assert _assembly_building_dir(None, composed) == ""\n\n\ndef test_a_scene_naming_no_lot_reference_changes_nothing(tmp_path):\n    """A graybox assembly instances geometry directly and names no package."""\n    themed = _assembly(tmp_path, \'[gd_scene format=3]\\n\'\n                       \'[ext_resource type="PackedScene" \'\n                       \'path="buildings/shell.glb" id="b1"]\\n\')\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(themed, composed) == ""\n\n\ndef test_the_same_reference_twice_is_still_one_directory(tmp_path):\n    """Two placements of ONE building -- the ids are deduped, not counted."""\n    themed = _assembly(tmp_path, ONE + ONE.splitlines()[-1] + "\\n")\n    composed = tmp_path / "composed"\n    composed.mkdir()\n    assert _assembly_building_dir(themed, composed) == "lot/shell"\n'
CHANGELOG_ENTRY = "## [0.39.0] - the composed root lands where the assembly says it does\n\nEvery single-shell themed export since 0.37.0 has shipped a level that cannot\nopen, in BOTH `portable-godot` and `art-unlit`. Measured on unlit_probe_001,\n2026-08-16: 56 files, 7,158,515 bytes, and the entry scene reaches TWO of\nthem.\n\n    site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn\n    resource_count: 2\n\nWHY\n\n`export_mission` step 2 copies the composed root to the package ROOT. Step\n2.5 -- added in 0.37.0 -- then copies `themed_site_assemble/out/site.tscn`\nover the root `site.tscn`, and copies nothing else out of that job. On a\nVARIED lot that is fine: the composed root already holds `lot/<archetype>/`\nper building, so the assembly's references resolve. On a SINGLE-SHELL mission\nthe composed root IS the one building laid flat, and the assembly names\n`lot/<id>/site.tscn` -- a directory `site_packages.py` staged in the job's\nout dir and the export never carried.\n\n0.37.0 was right about the problem it fixed -- on lot_demo_001 the assembly\nscene reached no package at all and an unlit export instanced nothing -- and\nit was measured on that five-building mission, which is the shape where this\ndoes not bite.\n\nTHE FIX\n\n`_assembly_building_dir` reads the assembly scene and returns `lot/<id>` when\nit names exactly one such package AND the composed root has no `lot/` of its\nown. The composed root is then copied there instead of to the package root,\nso the building lives under `lot/<id>/` on both mission shapes and the\nassembly's reference resolves. The composer's own `site.tscn` stops being\nskipped in that case, because under `lot/<id>/` it IS the building.\n\nASKED, NOT INFERRED. The first attempt at this used\n`_root_site_wanted(presentation_dir)` as the single-shell test. It is not\none: it returns True whenever there is no Lux scene to ask, which on a\nmission that never ran Lux is every time. The scene that names the path is\nthe artefact that knows, which is the rule this file already states about the\npresentation scene two comments earlier.\n\nRoadmap item 49, third reading. The two earlier readings -- the lot drawing\nthis pipeline's own output, and the export flattening `lot/shell/` -- are\nrecorded there as wrong, with what refuted each.\n\n"

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    # EVERY FILE THIS TOUCHES, CHECKED UP FRONT. Found by running the patch in
    # a tree with no CHANGELOG.md: it edited export.py, wrote the test, bumped
    # VERSION and THEN died with a traceback on the missing file, leaving three
    # of four edits applied. A patch that half-applies and raises is worse than
    # one that refuses, and this whole convention exists to refuse.
    missing = [r for r in (EXPORT, VERSION, CHANGELOG)
               if not (root / r).is_file()]
    if missing:
        print("REFUSING: not here -- run from the factory root:")
        for r in missing:
            print(f"    {r}")
        return 1
    p = root / EXPORT
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)
    if _sha(raw)[:16] != SOURCE_SHA:
        print(f"  NOTE: {EXPORT} is sha256 {_sha(raw)[:16]}, written against "
              f"{SOURCE_SHA}. The anchors below decide.")

    out = body
    done = 0
    for old, new, what in ((OLD_COPY, NEW_COPY, "the copy destination"),
                           (HELPER_ANCHOR, HELPER + HELPER_ANCHOR,
                            "_assembly_building_dir")):
        o, n = _as(old, eol), _as(new, eol)
        if n in out:
            done += 1
        elif out.count(o) == 1:
            out = out.replace(o, n, 1)
        else:
            print(f"REFUSING: the anchor for {what} occurs {out.count(o)} "
                  f"time(s), expected 1")
            return 1
    if done == 1:
        print(f"REFUSING: one of two edits is already present -- {EXPORT} is "
              f"half-patched. Revert or fix by hand.")
        return 1

    if done == 2:
        print(f"  already applied  {EXPORT}")
    elif check:
        data = out.encode("utf-8")
        print(f"  would patch  {EXPORT}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
    else:
        data = out.encode("utf-8")
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {EXPORT}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")

    t = root / TESTF
    if t.is_file() and t.read_text(encoding="utf-8").replace(_CRLF, "\n") \
            == TEST_SRC:
        print(f"  already there    {TESTF}")
    elif check:
        print(f"  would create {TESTF}  {len(TEST_SRC.encode()):,} bytes")
    else:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(TEST_SRC.encode("utf-8"))
        print(f"  created      {TESTF}  {len(TEST_SRC.encode()):,} bytes")

    v = root / VERSION
    cur = v.read_bytes().decode("utf-8").strip()
    if cur == NEW_VER:
        print(f"  already {NEW_VER}     {VERSION}")
    elif cur != OLD_VER:
        print(f"REFUSING: {VERSION} is {cur!r}, expected {OLD_VER!r}")
        return 1
    elif check:
        print(f"  would bump   {VERSION}  {OLD_VER} -> {NEW_VER}")
    else:
        v.write_bytes(NEW_VER.encode("utf-8"))
        print(f"  bumped       {VERSION}  {OLD_VER} -> {NEW_VER}")

    c = root / CHANGELOG
    craw = c.read_bytes()
    cbody = craw.decode("utf-8")
    ceol = _eol(cbody)
    head = _as(f"## [{OLD_VER}] - ", ceol)
    if _as(f"## [{NEW_VER}] - ", ceol) in cbody:
        print(f"  already has {NEW_VER}  {CHANGELOG}")
    elif cbody.count(head) != 1:
        print(f"REFUSING: {CHANGELOG} has {cbody.count(head)} "
              f"'## [{OLD_VER}] - ' headings, expected 1")
        return 1
    else:
        cnew = cbody.replace(head, _as(CHANGELOG_ENTRY, ceol) + head, 1)
        if check:
            print(f"  would patch  {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cnew.encode()):,} bytes")
        else:
            side = c.with_suffix(c.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(craw)
            c.write_bytes(cnew.encode("utf-8"))
            print(f"  patched      {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cnew.encode()):,} bytes")
    return 0


def _pytest(root: Path, *args: str) -> tuple[int, str]:
    """RETURN CODE, not text. 0 passed, 1 failed, 5 collected nothing --
    and 5 is a FAILURE here, it is what a broken import looks like."""
    proc = subprocess.run([sys.executable, "-m", "pytest", *args],
                          cwd=str(root / LF), capture_output=True, text=True)
    return proc.returncode, ((proc.stdout or "")[-1500:]
                             + (proc.stderr or "")[-600:])


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    src = (root / EXPORT).read_text(encoding="utf-8")
    check("the helper is defined", "def _assembly_building_dir(" in src)
    check("...and the copy destination uses it",
          "building_rel = _assembly_building_dir(themed_site_dir, "
          "composed_root)" in src
          and "dest = (export_dir / building_rel) if building_rel "
              "else export_dir" in src)
    check("...and _copy_tree writes to dest, not to export_dir",
          "_copy_tree(composed_root, dest," in src)
    check("the composer's site.tscn stops being skipped when it is the "
          "building",
          "skip_rel=(set() if (wanted or building_rel)" in src)
    check("_root_site_wanted is NOT used as the discriminator",
          "_assembly_building_dir(themed_site_dir" in src
          and "dest = (export_dir / _root_site_wanted" not in src)
    check("the module still compiles", _compiles(root / EXPORT))

    check("the new test file exists", (root / TESTF).is_file())

    check(f"VERSION is {NEW_VER}",
          (root / VERSION).read_text(encoding="utf-8").strip() == NEW_VER)
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"CHANGELOG leads with {NEW_VER}",
          cl.lstrip().startswith(f"## [{NEW_VER}]"))
    check("...and says BOTH modes were broken, not just unlit",
          "in BOTH `portable-godot` and `art-unlit`" in cl)
    check("...and credits 0.37.0 rather than only blaming it",
          "0.37.0 was right about the problem it fixed" in cl)
    check("...and records the discriminator that was rejected",
          "It is not\none:" in cl or "ASKED, NOT INFERRED" in cl)

    print()
    print("  running the new tests")
    rc, tail = _pytest(root, "tests/unit/test_assembly_building_dir.py")
    check(f"the new tests pass (pytest rc={rc})", rc == 0)
    if rc != 0:
        print(tail)

    print()
    print("  running tests/unit WHOLE")
    rc2, tail2 = _pytest(root, "tests/unit")
    check(f"tests/unit passes (pytest rc={rc2})", rc2 == 0)
    if rc2 != 0:
        print(tail2)

    print()
    if bad:
        print(f"  {bad} FAILURE(S)")
    else:
        print("  green here proves the FUNCTION. It does not prove the")
        print("  PACKAGE -- re-export unlit_probe_001 and read the closure")
        print("  scan. resource_count must leave 2.")
    return 1 if bad else 0


def _compiles(p: Path) -> bool:
    import py_compile
    import tempfile
    try:
        with tempfile.TemporaryDirectory() as d:
            py_compile.compile(str(p), cfile=str(Path(d) / "x.pyc"),
                               doraise=True)
        return True
    except Exception as exc:                      # noqa: BLE001
        print(f"       {exc}")
        return False


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        rc = 0
        for rel in (EXPORT, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if side.is_file():
                p.write_bytes(side.read_bytes())
                print(f"  reverted     {rel}")
            else:
                print(f"  no sidecar for {rel}")
                rc = 1
        (root / VERSION).write_bytes(OLD_VER.encode("utf-8"))
        print(f"  reverted     {VERSION} -> {OLD_VER}")
        t = root / TESTF
        if t.is_file():
            t.unlink()
            print(f"  removed      {TESTF}")
        return rc
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_039.py --selftest")
        print()
        print("  then the proof, on the real package (all jobs cached):")
        print('    $ws = "workspaces\\unlit-3b-ws"')
        print("    python level_factory\\apps\\cli\\main.py -C $ws export "
              "unlit_probe_001 --mode art-unlit --format folder")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
