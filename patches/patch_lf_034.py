r"""level_factory 0.34.0 -- the art layer was reported from Lux's output.

    python patches\patch_lf_034.py --check
    python patches\patch_lf_034.py
    python patches\patch_lf_034.py --selftest
    python patches\patch_lf_034.py --revert

Run from the FACTORY ROOT.

WHAT IS WRONG

`cmd_export` does not take the layer set from the run that produced the
mission. It infers it from what is on disk:

    layers = set()
    if handoff_dir.exists():
        layers.add(LAYER_GAMEPLAY)
    if lux_dir.exists():
        layers.add(LAYER_ART)

`lux_dir` is `<mission>.lux_apply/out`. So the question "did the ART layer
run?" is answered by "did LUX produce output?", and those are not the same
question. Everything Pixelcoat, Zoo and Patina built, and the themed site
assembled from them, is invisible to this check.

It is wrong TODAY, with no new feature involved: a mission whose art pass
succeeded and whose `lux_apply` failed exports an `LF_MANIFEST.json` saying
the package has no art layer, on a package full of art. Nothing checks that
field, so nothing has ever said so.

It gets worse the moment `lux_apply` moves behind its own layer (roadmap 47),
because then an ART-WITHOUT-LIGHT package is the normal case rather than a
failure, and every one of them would ship a manifest denying its own
contents. That is why this lands FIRST, on its own, against a suite measured
green -- rather than inside the change that makes it urgent.

THE FIX, AND WHY IT IS A UNION

    art = compose_root.exists() or lux_dir.exists()

`presentation_compose/out/presentation` is what the art layer PRODUCES: the
composed themed building the site is assembled from. That is the honest
signal.

`or lux_dir.exists()` is kept deliberately. This function must never report
FEWER layers than the code it replaces, or an existing workspace that
exports fine today starts describing itself differently after an upgrade.
Lux output still implies an art pass, because Lux runs on the composed site
and cannot exist without one. The union is strictly wider than the old test
and strictly narrower than lying.

It is now a named function with a test, because the mapping from artifacts to
layers is a DECISION, and the reason this went unnoticed for weeks is that
the decision was four inline lines in the middle of a 90-line command.

THE PATHS STAY IN cmd_export ON PURPOSE

`_layers_produced` takes three directories, it does not spell them. The bug
was never how the path is written -- it was which artifact stands for which
layer. Moving the path expressions in here would put a second derivation of
`<mission>.<stage>/out` in a second place, which is the shape
`walk_content_dir` warns about in its own docstring, four hundred lines up.

ALSO IN THIS RELEASE

`pyproject.toml` said `version = "0.22.0"` while `VERSION` said `0.33.0` --
eleven releases of drift. Nothing reads pyproject for the running version, so
nothing broke; an INSTALLED copy has been reporting a version from six days
ago. Bumped, and the selftest now asserts the two agree, so it cannot drift
eleven releases again without something saying so.

A NOTE ON `-qq`, WHICH COST TWO WRONG CHECKS TODAY

`pyproject.toml` carries `addopts = "-q"`. Every `python -m pytest ... -q`
therefore runs at `-qq`, and at two the run summary line disappears
entirely -- which is why `suite.txt` was 80 bytes of dots with no `28 passed`
in it, and why two successive attempts to detect "did the test run" by
reading pytest's prose were both wrong. The return code was always the
answer. Recorded here because the next person to grep for a count line
deserves to know it was never going to be there.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CMDS = "level_factory/apps/cli/commands/__init__.py"
PYPROJECT = "level_factory/pyproject.toml"
NEW_TEST = "level_factory/tests/unit/test_export_layers.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_034"

OLD_V, NEW_V = "0.33.0", "0.34.0"
OLD_PYPROJECT_V = 'version = "0.22.0"'
NEW_PYPROJECT_V = 'version = "0.34.0"'

EDITS: list[tuple[str, str, str]] = [
    (CMDS,
     "def cmd_export(args) -> int:\n",

     "def _layers_produced(*, compose_root: Path, lux_dir: Path,\n"
     "                     handoff_dir: Path) -> set:\n"
     '    """Which composable layers a finished mission actually PRODUCED.\n'
     "\n"
     "    THE ART LAYER IS NOT LUX. This was four inline lines in `cmd_export`\n"
     "    and it read `lux_dir.exists()` to decide whether the art layer ran,\n"
     "    so a mission whose Pixelcoat/Zoo/Patina pass succeeded and whose\n"
     "    `lux_apply` failed exported an LF_MANIFEST.json declaring no art\n"
     "    layer -- on a package full of art. Nothing reads that field, so\n"
     "    nothing ever objected.\n"
     "\n"
     "    `presentation_compose/out/presentation` is what the art layer\n"
     "    produces and is therefore what stands for it.\n"
     "\n"
     "    THE `or lux_dir.exists()` IS NOT REDUNDANT. This must never report\n"
     "    fewer layers than the four lines it replaces, or a workspace that\n"
     "    exports correctly today would describe itself differently after an\n"
     "    upgrade. Lux runs on the composed site and cannot exist without\n"
     "    one, so its output still implies an art pass. Strictly wider than\n"
     "    the old test; strictly narrower than lying.\n"
     "\n"
     "    It takes directories rather than a mission id BECAUSE the bug was\n"
     "    never how a job path is spelled. Building `<mission>.<stage>/out`\n"
     "    here would put a second derivation of that name in a second place --\n"
     "    the failure `walk_content_dir` describes in its own docstring.\n"
     '    """\n'
     "    from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY\n"
     "    layers = set()\n"
     "    if compose_root.exists() or lux_dir.exists():\n"
     "        layers.add(LAYER_ART)\n"
     "    if handoff_dir.exists():\n"
     "        layers.add(LAYER_GAMEPLAY)\n"
     "    return layers\n"
     "\n"
     "\n"
     "def cmd_export(args) -> int:\n"),

    (CMDS,
     "    # Resolve which layers were actually produced, and the functional base.\n"
     "    layers = set()\n"
     "    if handoff_dir.exists():\n"
     "        layers.add(LAYER_GAMEPLAY)\n"
     "    if lux_dir.exists():\n"
     "        layers.add(LAYER_ART)\n",

     "    # Resolve which layers were actually produced, and the functional base.\n"
     "    # The mapping from artifacts to layers is a decision with a name and a\n"
     "    # test now; see `_layers_produced` for why the art layer is not Lux.\n"
     "    layers = _layers_produced(compose_root=compose_root, lux_dir=lux_dir,\n"
     "                              handoff_dir=handoff_dir)\n"),

    (PYPROJECT, OLD_PYPROJECT_V, NEW_PYPROJECT_V),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""The art layer is reported from what the art layer produces.

Written for level_factory 0.34.0. `cmd_export` inferred the art layer from
`lux_apply`'s output directory, so a mission whose art pass succeeded and
whose Lux stage failed exported a manifest declaring no art layer. These
cover the mapping itself -- which artifact stands for which layer -- not the
spelling of any job path.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from apps.cli.commands import _layers_produced  # noqa: E402
from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY  # noqa: E402


def _dirs(tmp_path, *, compose=False, lux=False, handoff=False):
    c = tmp_path / "compose" / "out" / "presentation"
    l = tmp_path / "lux" / "out"
    h = tmp_path / "handoff" / "out"
    if compose:
        c.mkdir(parents=True)
    if lux:
        l.mkdir(parents=True)
    if handoff:
        h.mkdir(parents=True)
    return {"compose_root": c, "lux_dir": l, "handoff_dir": h}


def test_the_art_pass_alone_reports_the_art_layer(tmp_path):
    """THE BUG. Art built, Lux absent -- this returned an empty set."""
    assert _layers_produced(**_dirs(tmp_path, compose=True)) == {LAYER_ART}


def test_lux_alone_still_reports_the_art_layer(tmp_path):
    """The union, not a replacement. An existing workspace must not start
    describing itself differently after the upgrade."""
    assert _layers_produced(**_dirs(tmp_path, lux=True)) == {LAYER_ART}


def test_both_report_it_once(tmp_path):
    assert _layers_produced(**_dirs(tmp_path, compose=True, lux=True)) == {LAYER_ART}


def test_a_graybox_mission_reports_no_layers(tmp_path):
    assert _layers_produced(**_dirs(tmp_path)) == set()


def test_the_gameplay_layer_is_independent(tmp_path):
    assert _layers_produced(**_dirs(tmp_path, handoff=True)) == {LAYER_GAMEPLAY}
    assert _layers_produced(
        **_dirs(tmp_path, compose=True, handoff=True)
    ) == {LAYER_ART, LAYER_GAMEPLAY}


def test_it_is_never_narrower_than_the_code_it_replaced(tmp_path):
    """The old rule, exhaustively, as the floor.

    Old: art iff lux_dir.exists(); gameplay iff handoff_dir.exists(). Every
    combination the old lines reported must still be reported.
    """
    for lux in (False, True):
        for handoff in (False, True):
            for compose in (False, True):
                old = set()
                if lux:
                    old.add(LAYER_ART)
                if handoff:
                    old.add(LAYER_GAMEPLAY)
                new = _layers_produced(
                    **_dirs(tmp_path / f"c{compose}l{lux}h{handoff}",
                            compose=compose, lux=lux, handoff=handoff))
                assert old <= new, (compose, lux, handoff, old, new)
''',
}

ENTRY = """## [0.34.0] - the art layer was reported from Lux's output

`cmd_export` does not take the layer set from the run. It infers it from what
is on disk, and it asked the wrong directory:

    if lux_dir.exists():
        layers.add(LAYER_ART)

`lux_dir` is `<mission>.lux_apply/out`. "Did the art layer run?" was answered
by "did Lux produce output?" Everything Pixelcoat, Zoo and Patina built, and
the themed site assembled from it, was invisible to that test.

WRONG TODAY, with no new feature involved. A mission whose art pass succeeded
and whose `lux_apply` failed exports an `LF_MANIFEST.json` declaring no art
layer, on a package full of art. Nothing reads that field, so nothing has
ever objected.

It becomes structural under roadmap 47, where `lux_apply` moves behind its
own layer and art-without-light is the normal case rather than a failure --
every such package would ship a manifest denying its own contents. This
lands first, alone, against a suite measured green, rather than inside the
change that makes it urgent.

THE FIX IS A UNION

    art = compose_root.exists() or lux_dir.exists()

`presentation_compose/out/presentation` is what the art layer produces, so it
is what stands for it. The `or` is deliberate: this must never report FEWER
layers than the lines it replaces, or a workspace that exports correctly
today would describe itself differently after an upgrade. Lux runs on the
composed site and cannot exist without one. Strictly wider than the old test,
strictly narrower than lying, and `test_it_is_never_narrower_than_the_code_it_replaced`
asserts exactly that over all eight combinations.

It is a named function with a test now. The reason this survived weeks is
that the decision was four inline lines in the middle of a 90-line command.
The directories are still spelled in `cmd_export` -- building
`<mission>.<stage>/out` inside the helper would put a second derivation of
that name in a second place, which is the failure `walk_content_dir`
describes in its own docstring.

ALSO

`pyproject.toml` said `0.22.0` against a `VERSION` of `0.33.0` -- eleven
releases of drift. Nothing reads pyproject for the running version, so
nothing broke, but an installed copy reported a version six days stale. The
selftest now asserts the two agree.

RECORDED FOR THE NEXT PERSON: `pyproject.toml` carries `addopts = "-q"`, so
every `pytest ... -q` actually runs at `-qq`, and at two the run summary line
is suppressed entirely. That is why a green suite writes 80 bytes of dots
with no `28 passed` line in it, and why two attempts to detect "did the test
run" by reading pytest's prose were both wrong. The return code was always
the answer.
"""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    """The FILE's line ending, never the anchor's.

    `pyproject.toml` is CRLF while every other file this touches is LF, and
    `Path.read_text()` normalises newlines away, so a check written against
    decoded text reports LF for both and the anchors silently fail to match.
    Read bytes, decide here, convert the anchor to suit.
    """
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
        body = raw.decode("utf-8")
        out, done = body, 0
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
                  f"({len(data) - len(raw):+,})  [{'CRLF' if eol != chr(10) else 'LF'}]")
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
    cp.write_bytes((_as(ENTRY, _eol(craw)) + _as("\n", _eol(craw))
                    + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
    import importlib
    import subprocess
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()
    if str(lf) not in sys.path:
        sys.path.insert(0, str(lf))

    # ---- 1. THE DECISION, CALLED. ------------------------------------------
    cmds = importlib.import_module("apps.cli.commands")
    importlib.reload(cmds)
    planner = importlib.import_module("packages.pipeline.planner")
    check("_layers_produced exists and is importable",
          hasattr(cmds, "_layers_produced"))
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        def dirs(compose=False, lux=False, handoff=False, tag=""):
            c = base / f"c{tag}" / "presentation"
            l = base / f"l{tag}"
            h = base / f"h{tag}"
            for want, d in ((compose, c), (lux, l), (handoff, h)):
                if want:
                    d.mkdir(parents=True, exist_ok=True)
            return {"compose_root": c, "lux_dir": l, "handoff_dir": h}

        art_only = cmds._layers_produced(**dirs(compose=True, tag="1"))
        check("THE BUG: an art pass with no Lux reports the art layer",
              art_only == {planner.LAYER_ART})
        check("Lux alone still reports it -- never narrower than before",
              cmds._layers_produced(**dirs(lux=True, tag="2"))
              == {planner.LAYER_ART})
        check("a graybox mission reports nothing",
              cmds._layers_produced(**dirs(tag="3")) == set())
        check("gameplay is independent of both",
              cmds._layers_produced(**dirs(handoff=True, tag="4"))
              == {planner.LAYER_GAMEPLAY})
        check("and they compose",
              cmds._layers_produced(**dirs(compose=True, handoff=True, tag="5"))
              == {planner.LAYER_ART, planner.LAYER_GAMEPLAY})

    # ---- 2. THE OLD INLINE TEST IS GONE FROM cmd_export. -------------------
    src = (root / CMDS).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))
    check("cmd_export no longer decides the art layer inline",
          "layers.add(LAYER_ART)" not in code.split("def cmd_export")[-1])
    check("and calls the named decision instead",
          "_layers_produced(compose_root=compose_root" in code)

    # ---- 3. THE VERSIONS AGREE. --------------------------------------------
    v = (root / VERSION_F).read_text(encoding="utf-8").strip()
    py = (root / PYPROJECT).read_text(encoding="utf-8")
    check(f"VERSION is {NEW_V}", v == NEW_V)
    check("pyproject agrees with VERSION -- it was eleven releases behind",
          f'version = "{v}"' in py)
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says it is wrong today, not just under roadmap 47",
          "WRONG TODAY" in flat)
    check("and records the -qq finding",
          "addopts" in flat and "-qq" in flat)

    # ---- 4. THE NEW TESTS, AND THE SUITE THEY JOIN. ------------------------
    print()
    print("  running the new unit tests --")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_export_layers.py"],
        cwd=str(lf), capture_output=True, text=True,
    )
    for line in (r.stdout + r.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    # Return code, not prose. addopts already carries -q; the summary line is
    # not there to read.
    check("THE NEW TESTS PASS", r.returncode == 0)

    print()
    print("  running service + integration, the suite measured green at 0.33.0 --")
    r2 = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/service", "tests/integration"],
        cwd=str(lf), capture_output=True, text=True,
    )
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    check("STILL GREEN", r2.returncode == 0)

    print()
    print("  NOT VERIFIED HERE: that an exported LF_MANIFEST.json carries the")
    print("  corrected layers end to end -- that needs a mission whose")
    print("  lux_apply failed, which is roadmap 47's test, not this one's.")

    print()
    print("  the art layer is reported from what the art layer produces"
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
        for rel in (CMDS, PYPROJECT, VERSION_F, CHANGELOG):
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
            # Only remove what THIS patch wrote. An edited file is somebody's
            # work now, and a revert that deletes it is a revert that loses it.
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
        print("    python patches\\patch_lf_034.py --selftest")
        print()
        print("  This is the floor for roadmap 47. The layer split lands next,")
        print("  and it is the change that makes art-without-light normal.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
