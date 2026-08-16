r"""level_factory 0.36.0 -- art-unlit: the same build, shipped twice.

    python patches\patch_lf_036.py --check
    python patches\patch_lf_036.py
    python patches\patch_lf_036.py --selftest
    python patches\patch_lf_036.py --revert

Run from the FACTORY ROOT. Roadmap item 47, stage 2.

WHAT 0.35.0 LEFT

A mission RUN without the light layer already exports correctly: no
`lux_apply` output means no `presentation/` directory, `_root_site_wanted`
keeps the themed `site.tscn`, and `write_entry_scene`'s `elif` makes that the
entry. That path needed no code.

What it could not do is take a mission that DID run Lux and ship an unlit
package from it. That is the case the A/B needs -- two archives out of one
build, so a recipient can drop in ours and theirs and compare the same
geometry under two lighting solutions. `MODE_ART_UNLIT` is that subtraction,
and it happens at EXPORT time.

TWO QUESTIONS THAT LOOKED LIKE ONE

`profile.mode == MODE_PURE_SHELL` gated three separate things, and while
pure-shell was the only mode that declined anything, one test answered all
three. They are not the same question:

    does this mode ship Lux's RESULT?   pure-shell: no    art-unlit: no
    does this mode ship the themed ART? pure-shell: no    art-unlit: YES

So the first two branches -- the `_PRESENTATION_FILES` skip and the copy of
`presentation/` -- now ask `ships_lux(mode)`, and the third, which copies the
composed themed root, keeps asking about pure-shell alone. That third branch
is the one an art-unlit package needs MOST: the composed content is the whole
point of it.

THE MANIFEST MUST NOT CLAIM THE LAYER IT JUST DROPPED

`cmd_export` derives `layers` from what is on disk, and on a lit mission that
includes the light layer -- correctly, because `lux_apply` ran. Exporting
art-unlit from that same mission would then ship an `LF_MANIFEST.json` saying
`layers: [art, gameplay, light]` on a package with no Lux output in it.

That is the identical failure 0.34.0 fixed from the other direction, where a
package full of art declared none. So `export_mission` subtracts the light
layer whenever the mode ships no Lux. The manifest describes THE PACKAGE, not
the run it came from.

THE ENTRY SCENE NEEDED NO CODE, AND ITS COMMENT DID

`write_entry_scene` already does the right thing:

    if pres.exists():   -> presentation/lux.applied.tscn
    elif site.exists(): -> site.tscn

With Lux dropped there is no `presentation/`, so the `elif` fires and the
entry instances the THEMED `site.tscn`. Correct, and by luck of good design
rather than by intent -- its docstring says "site.tscn is the entry only for
a graybox export that has no presentation pass", and an art-unlit export is
neither graybox nor without an art pass. Code that is right for a case its
own explanation excludes is code somebody later 'fixes'. The comment is
corrected; the logic is not touched.

WHAT IS STILL NOT DONE

An actual unlit RUN through the real tools, and a real art-unlit export read
back off disk. Stage 3. These tests build packages from fabricated job
directories: they prove which files a mode copies and what the manifest then
says, not that Godot opens the result.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPORT = "level_factory/packages/exporting/export.py"
LOCALIZE = "level_factory/packages/exporting/localize.py"
MAIN = "level_factory/apps/cli/main.py"
NEW_TEST = "level_factory/tests/unit/test_art_unlit_export.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_036"

OLD_V, NEW_V = "0.35.0", "0.36.0"

EDITS: list[tuple[str, str, str]] = [
    # ------------------------------------------------------------ the mode
    (EXPORT,
     'MODE_PORTABLE = "portable-godot"\n'
     'MODE_PURE_SHELL = "pure-shell"\n'
     'MODE_SOURCE = "source-authoring"\n',

     'MODE_PORTABLE = "portable-godot"\n'
     'MODE_PURE_SHELL = "pure-shell"\n'
     'MODE_ART_UNLIT = "art-unlit"\n'
     'MODE_SOURCE = "source-authoring"\n'
     "\n"
     "#: Modes that ship no Lux RESULT. Not the same set as modes that ship no\n"
     "#: art: `art-unlit` declines the render and keeps everything Pixelcoat,\n"
     "#: Zoo and Patina built, which is the entire reason it exists.\n"
     "UNLIT_MODES = frozenset({MODE_PURE_SHELL, MODE_ART_UNLIT})\n"
     "\n"
     "\n"
     "def ships_lux(mode: str) -> bool:\n"
     '    """Does a package built in this mode carry Lux\'s applied scene?\n'
     "\n"
     "    A NAMED QUESTION because `profile.mode == MODE_PURE_SHELL` was\n"
     "    answering three different ones, and only stayed correct while\n"
     "    pure-shell was the only mode that declined anything. The third of\n"
     "    those branches -- the composed themed root -- deliberately does NOT\n"
     "    use this: an unlit art package is exactly the one that wants it.\n"
     '    """\n'
     "    return mode not in UNLIT_MODES\n"),

    # ----------------------------------------- the manifest's layer set
    (EXPORT,
     "    export_dir.mkdir(parents=True, exist_ok=True)\n"
     "    layers = frozenset(layers or ())\n",

     "    export_dir.mkdir(parents=True, exist_ok=True)\n"
     "    layers = frozenset(layers or ())\n"
     "    # THE MANIFEST DESCRIBES THE PACKAGE, NOT THE RUN. `cmd_export`\n"
     "    # derives layers from what is on disk, so a lit mission reports the\n"
     "    # light layer -- correctly, `lux_apply` ran. Exporting art-unlit from\n"
     "    # that same mission would then declare a layer this package does not\n"
     "    # contain, which is 0.34.0's failure with the sign reversed.\n"
     "    if not ships_lux(profile.mode):\n"
     "        from packages.pipeline.planner import LAYER_LIGHT\n"
     "        layers = layers - {LAYER_LIGHT}\n"),

    # ------------------------------------------------- branch 1: the skip
    (EXPORT,
     "    skip: set[str] = set()\n"
     "    if profile.mode == MODE_PURE_SHELL:\n"
     "        skip |= _PRESENTATION_FILES\n",

     "    skip: set[str] = set()\n"
     "    if not ships_lux(profile.mode):\n"
     "        skip |= _PRESENTATION_FILES\n"),

    # ---------------------------------- branch 2: the presentation folder
    (EXPORT,
     "    # 2. Localize presentation (unless pure-shell).\n"
     "    if profile.mode != MODE_PURE_SHELL and presentation_dir and presentation_dir.exists():\n",

     "    # 2. Localize presentation (unless the mode ships no Lux).\n"
     "    if ships_lux(profile.mode) and presentation_dir and presentation_dir.exists():\n"),

    # -------------------------------- branch 3: NOT the same question
    (EXPORT,
     "    if (profile.mode != MODE_PURE_SHELL\n"
     "            and composed_root and composed_root.exists()):\n",

     "    # PURE-SHELL ALONE, and `art-unlit` is deliberately absent from this\n"
     "    # one: the composed themed content IS what an unlit art package\n"
     "    # ships. `ships_lux` asks a different question and using it here\n"
     "    # would strip the art out of the art-without-light mode.\n"
     "    if (profile.mode != MODE_PURE_SHELL\n"
     "            and composed_root and composed_root.exists()):\n"),

    # ------------------------------------------- the entry-scene reasoning
    (LOCALIZE,
     "    So the presentation scene wins whenever it exists, and site.tscn is the\n"
     "    entry only for a graybox export that has no presentation pass. It still\n"
     "    ships either way -- skipping it is what broke closure:\n"
     "    `lux.applied.tscn: unresolved res://site.tscn`.\n"
     '    """\n',

     "    So the presentation scene wins whenever it exists, and site.tscn is the\n"
     "    entry when there is none. It still ships either way -- skipping it is\n"
     "    what broke closure: `lux.applied.tscn: unresolved res://site.tscn`.\n"
     "\n"
     '    "ONLY FOR A GRAYBOX EXPORT" WAS TOO NARROW, and this logic was already\n'
     "    right for the case that sentence excluded. Since 0.36.0 an `art-unlit`\n"
     "    export drops Lux's two files, so there is no presentation scene to\n"
     "    prefer and the `elif` fires -- on a package that is neither graybox nor\n"
     "    without an art pass. The entry it names is the THEMED site.tscn, which\n"
     "    is correct and is the whole deliverable of that mode.\n"
     "\n"
     "    The condition is deliberately about what EXISTS rather than about the\n"
     "    mode. A mode test here would be a second place that decides what a\n"
     "    package contains, and export.py already decided by not copying the\n"
     '    file.\n'
     '    """\n'),

    # ------------------------------------------------------------- the CLI
    (MAIN,
     '    sp.add_argument("--mode", default="portable-godot",\n'
     '                    choices=["portable-godot", "pure-shell", "source-authoring"])\n'
     '    sp.add_argument("--format", default="folder", choices=["folder", "zip"])\n',

     '    sp.add_argument("--mode", default="portable-godot",\n'
     '                    choices=["portable-godot", "art-unlit", "pure-shell",\n'
     '                             "source-authoring"],\n'
     '                    help="art-unlit: the full art pass with no Lux result, "\n'
     '                         "for a team bringing its own lighting")\n'
     '    sp.add_argument("--format", default="folder", choices=["folder", "zip"])\n'),

    (MAIN,
     '    sp.add_argument("--mode", default="portable-godot",\n'
     '                    choices=["portable-godot", "pure-shell", "source-authoring"])\n'
     "    sp.set_defaults(func=cmd_portability_test)\n",

     '    sp.add_argument("--mode", default="portable-godot",\n'
     '                    choices=["portable-godot", "art-unlit", "pure-shell",\n'
     '                             "source-authoring"])\n'
     "    sp.set_defaults(func=cmd_portability_test)\n"),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""art-unlit: the art pass without the render. Roadmap 47, stage 2.

These build real packages from fabricated job directories and read back what
landed. They prove WHICH FILES a mode copies and what the manifest then
claims -- not that Godot opens the result, which is stage 3.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.exporting.export import (  # noqa: E402
    EXPORT_MANIFEST_NAME, MODE_ART_UNLIT, MODE_PORTABLE, MODE_PURE_SHELL,
    UNLIT_MODES, ExportProfile, export_mission, ships_lux,
)
from packages.pipeline.planner import (  # noqa: E402
    LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT,
)

ALL_THREE = frozenset({LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT})


# ------------------------------------------------------------- the predicate

def test_art_unlit_ships_no_lux():
    assert not ships_lux(MODE_ART_UNLIT)


def test_pure_shell_ships_no_lux():
    assert not ships_lux(MODE_PURE_SHELL)


def test_portable_godot_does():
    assert ships_lux(MODE_PORTABLE)


def test_the_unlit_set_is_exactly_those_two():
    assert UNLIT_MODES == frozenset({MODE_PURE_SHELL, MODE_ART_UNLIT})


# ----------------------------------------------------------------- a package

def _mission(root):
    """A locked mission\'s job directories, with one file of each kind."""
    handoff = root / "handoff"
    handoff.mkdir(parents=True)
    (handoff / "mission_manifest.json").write_text("{}")
    (handoff / "site.tscn").write_text("[gd_scene]\\n")
    # The handoff carries copies of Lux\'s outputs; the skip set is what keeps
    # them out of an unlit package.
    (handoff / "lux.applied.tscn").write_text("[gd_scene]\\n")
    (handoff / "lux.quality.json").write_text("{}")

    lux = root / "lux_out"
    lux.mkdir(parents=True)
    (lux / "lux.applied.tscn").write_text("[gd_scene]\\n")
    (lux / "lux.quality.json").write_text("{}")

    composed = root / "composed"
    composed.mkdir(parents=True)
    (composed / "wall.glb").write_bytes(b"glTF")
    (composed / "themed.material.tres").write_text("[gd_resource]\\n")
    return handoff, lux, composed


def _export(root, mode, *, layers=ALL_THREE):
    """Build a package. Returns (result, export_dir).

    `export_mission` names its own directory from `export_build_dir_name`, so
    the caller passes an out_root and reads back where it landed rather than
    predicting the name.
    """
    handoff, lux, composed = _mission(root / mode)
    result = export_mission(
        mission_id="m1", out_root=root / mode / "exports",
        profile=ExportProfile(mode=mode),
        handoff_dir=handoff, presentation_dir=lux, composed_root=composed,
        source_dir=None, tool_versions={}, layers=layers,
    )
    return result, result.export_dir


def _files(out):
    return {p.name for p in out.rglob("*") if p.is_file()}


def _manifest(out):
    return json.loads((out / EXPORT_MANIFEST_NAME).read_text())


def test_art_unlit_keeps_the_art(tmp_path):
    """THE POINT. Everything Zoo/Pixelcoat/Patina built is still here."""
    _, out = _export(tmp_path, MODE_ART_UNLIT)
    names = _files(out)
    assert "wall.glb" in names
    assert "themed.material.tres" in names


def test_art_unlit_drops_the_render(tmp_path):
    _, out = _export(tmp_path, MODE_ART_UNLIT)
    names = _files(out)
    assert "lux.applied.tscn" not in names
    assert "lux.quality.json" not in names
    assert not (out / "presentation").exists()


def test_portable_godot_still_ships_both(tmp_path):
    """The mode that did not change, asserted so it cannot drift."""
    _, out = _export(tmp_path, MODE_PORTABLE)
    names = _files(out)
    assert "wall.glb" in names
    assert "lux.applied.tscn" in names


def test_pure_shell_drops_both(tmp_path):
    """art-unlit sits BETWEEN the two, and this is the far end."""
    _, out = _export(tmp_path, MODE_PURE_SHELL)
    names = _files(out)
    assert "lux.applied.tscn" not in names
    assert "wall.glb" not in names


# ------------------------------------------------------------- the manifest

def test_the_manifest_does_not_claim_the_dropped_layer(tmp_path):
    """0.34.0\'s failure with the sign reversed.

    The run produced the light layer, so `cmd_export` passes it in. The
    PACKAGE has no Lux output in it, and the manifest describes the package.
    """
    _, out = _export(tmp_path, MODE_ART_UNLIT)
    got = _manifest(out)["layers"]
    assert LAYER_LIGHT not in got
    assert LAYER_ART in got
    assert LAYER_GAMEPLAY in got


def test_a_lit_export_still_claims_it(tmp_path):
    _, out = _export(tmp_path, MODE_PORTABLE)
    assert LAYER_LIGHT in _manifest(out)["layers"]


def test_the_manifest_names_the_mode(tmp_path):
    _, out = _export(tmp_path, MODE_ART_UNLIT)
    assert _manifest(out)["profile"] == "art-unlit"


def test_the_archive_name_distinguishes_the_two_packages(tmp_path):
    """The A/B this mode exists for: two archives from ONE build, told apart
    by name rather than by the recipient remembering which is which."""
    lit, _ = _export(tmp_path, MODE_PORTABLE)
    unlit, _ = _export(tmp_path, MODE_ART_UNLIT)
    assert lit.archive_name != unlit.archive_name
    assert unlit.archive_name.endswith("_art-unlit.zip")
    assert lit.archive_name.endswith("_portable-godot.zip")


def test_both_packages_use_the_same_interior_folder(tmp_path):
    """So a recipient can swap one for the other without every res:// path in
    their project moving."""
    lit, _ = _export(tmp_path, MODE_PORTABLE)
    unlit, _ = _export(tmp_path, MODE_ART_UNLIT)
    assert lit.package_dir_name == unlit.package_dir_name


# ---------------------------------------------------------------- the entry

def test_the_unlit_entry_instances_the_themed_site(tmp_path):
    """write_entry_scene needed no change; its docstring did.

    No presentation/ means the elif fires and the entry names site.tscn --
    which after themed_site_assemble is the THEMED site, not the graybox.
    """
    _, out = _export(tmp_path, MODE_ART_UNLIT)
    entry = (out / "mission.tscn").read_text()
    assert "site.tscn" in entry
    assert "lux.applied.tscn" not in entry
''',
}

ENTRY = """## [0.36.0] - art-unlit: the same build, shipped twice

0.35.0 made the light layer declinable at RUN time. A mission run unlit
already exported correctly, with no code: no `lux_apply` output means no
`presentation/` directory, so `_root_site_wanted` keeps the themed
`site.tscn` and `write_entry_scene`'s `elif` makes it the entry.

What could not be done was taking a mission that DID run Lux and shipping an
unlit package from it -- two archives out of one build, so a recipient can
drop in ours and theirs and compare the same geometry under two lighting
solutions. `MODE_ART_UNLIT` is that subtraction, at export time.

TWO QUESTIONS THAT LOOKED LIKE ONE

`profile.mode == MODE_PURE_SHELL` gated three separate things and stayed
correct only while pure-shell was the only mode that declined anything:

    does this mode ship Lux's RESULT?    pure-shell no   art-unlit no
    does this mode ship the themed ART?  pure-shell no   art-unlit YES

The `_PRESENTATION_FILES` skip and the copy of `presentation/` now ask
`ships_lux(mode)`. The third branch, which copies the composed themed root,
still asks about pure-shell alone -- and carries a comment saying why
`ships_lux` there would strip the art out of the art-without-light mode.

THE MANIFEST DESCRIBES THE PACKAGE, NOT THE RUN

`cmd_export` derives layers from what is on disk, so a lit mission reports
the light layer -- correctly, `lux_apply` ran. Exporting art-unlit from that
mission would have declared a layer the package does not contain, which is
0.34.0's failure with the sign reversed. `export_mission` subtracts the light
layer whenever the mode ships no Lux.

THE ENTRY SCENE NEEDED NO CODE AND ITS COMMENT DID

`write_entry_scene` prefers the presentation scene and falls back to
`site.tscn`. With Lux dropped the fallback fires and names the THEMED site,
which is right. Its docstring said site.tscn is the entry "only for a graybox
export that has no presentation pass", and an art-unlit export is neither
graybox nor without an art pass. Code that is correct for a case its own
explanation excludes is code somebody later 'fixes'. The comment is
corrected; the condition still asks what EXISTS rather than what mode this
is, because export.py already decided by not copying the file.

MEASURED

`tests/unit/test_art_unlit_export.py` builds real packages from fabricated
job directories and reads back what landed: art-unlit keeps `wall.glb` and
the themed material and drops both Lux files and the whole `presentation/`
folder; portable-godot still ships both; pure-shell still drops both. The two
archives differ in name and share an interior folder, so a recipient can swap
one for the other without every `res://` path moving.

NOT MEASURED

An actual unlit RUN through the real tools, and an art-unlit package opened
in Godot. Stage 3. These prove which files a mode copies and what the
manifest claims, not that the engine likes the result.
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

    print("  the art-unlit package tests --")
    r = run("tests/unit/test_art_unlit_export.py")
    for line in (r.stdout + r.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THE ART-UNLIT TESTS PASS", r.returncode == 0)

    print()
    print("  the export suite this rewires --")
    r2 = run("tests/unit/test_export_localize.py", "tests/unit/test_closure_export.py",
             "tests/unit/test_export_layers.py")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THE EXPORT SUITE PASSES", r2.returncode == 0)

    print()
    print("  service + integration -- ~2.5 min --")
    r3 = run("tests/service", "tests/integration")
    for line in (r3.stdout + r3.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("STILL GREEN -- portable-godot and pure-shell are unchanged",
          r3.returncode == 0)

    src = (root / EXPORT).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))
    check("the composed-root branch still asks about pure-shell ALONE",
          "if (profile.mode != MODE_PURE_SHELL" in code)
    # THREE, not two. This counted the two branches it CONVERTED and forgot
    # the layer subtraction added in the same patch -- a check written from
    # the intent rather than from the file. The sites are: the manifest's
    # layer set, the _PRESENTATION_FILES skip, and the presentation/ copy.
    sites = code.count("ships_lux(profile.mode)")
    check("all three Lux-shipping decisions ask the named question",
          sites == 3)
    if sites != 3:
        print(f"       found {sites}")
    check("and exactly one of them is the positive form",
          code.count("if ships_lux(profile.mode)") == 1)

    loc = (root / LOCALIZE).read_text(encoding="utf-8")
    check("write_entry_scene's LOGIC is untouched",
          'if pres.exists():' in loc and 'elif site.exists():' in loc)
    check("and it still does not branch on the mode",
          "MODE_" not in loc.split("def write_entry_scene")[-1])

    v = (root / VERSION_F).read_text(encoding="utf-8").strip()
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", v == NEW_V)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry separates the two questions",
          "does this mode ship the themed ART?" in flat)
    check("and says what is still not measured",
          "not that the engine likes the result" in flat)

    print()
    print("  NOT VERIFIED HERE: an unlit RUN through real tools, and an")
    print("  art-unlit package opened in Godot. Stage 3.")

    print()
    print("  the same build, shipped twice"
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
        for rel in (EXPORT, LOCALIZE, MAIN, VERSION_F, CHANGELOG):
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
        print("    python patches\\patch_lf_036.py --selftest")
        print()
        print("  Stage 3 is a real unlit RUN: --art --unlit through the real")
        print("  tools, exported both ways, portability-tested.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
