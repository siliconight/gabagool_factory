r"""level_factory 0.36.0 (amendment) -- a fourth list nobody knew was a list.

    python patches\patch_lf_036b.py --check
    python patches\patch_lf_036b.py
    python patches\patch_lf_036b.py --selftest
    python patches\patch_lf_036b.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_036.py.

WHAT FAILED, ON REAL DATA

    exported lot_demo_001 [portable-godot] -> ...LF_lot_demo_001.portable-godot
    internal error: 'art-unlit'

A KeyError. 0.36.0 added the mode in `export.py`, added it to `main.py`'s
argparse choices, and covered it with fourteen tests -- every one of which
calls `export_mission` directly and therefore never went through the command
that a person actually types.

`cmd_export` held a third list:

    mode_map = {"portable-godot": MODE_PORTABLE, "pure-shell": MODE_PURE_SHELL,
                "source-authoring": MODE_SOURCE}
    profile = ExportProfile(mode=mode_map[args.mode], ...)

Read what it maps. `MODE_PORTABLE` IS the string `"portable-godot"`. Every
entry maps a value to itself. It is an identity dict whose only real effect
is to raise KeyError on any mode it has not been told about -- a copy of the
constants, keyed by their own values, that had to be maintained in parallel
with them and had no other job.

`cmd_portability_test`, twelve lines below, already reads `args.mode`
straight through. The sibling command proves the map was never needed.

THE FIX IS DELETION, AND THEN A TEST SO IT CANNOT COME BACK

The map goes. `argparse` already constrains the string to `choices`, and the
constants ARE those strings.

That alone would leave the underlying problem: the CLI's `choices` list and
the modes `export.py` knows are two lists that must agree and nothing checked
that they did. So `export.py` now publishes `MODES`, and a test PARSES
`main.py` with `ast`, pulls the `choices` out of every `--mode` argument, and
asserts both directions -- no choice the code cannot honour, no mode the CLI
cannot reach. Adding a fifth mode and forgetting one place now fails a test
instead of failing in front of a user with a bare KeyError.

WHY THE FOURTEEN TESTS DID NOT CATCH IT

They exercise `export_mission`, which is the right unit for "which files does
this mode copy". Nothing exercised `cmd_export`. The gap is not that the
tests were weak; it is that they tested the layer below the one that broke.
The new test picks the seam between them -- argparse's choices and the
library's constants -- rather than adding a fifteenth test of the same layer.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPORT = "level_factory/packages/exporting/export.py"
CMDS = "level_factory/apps/cli/commands/__init__.py"
NEW_TEST = "level_factory/tests/unit/test_export_modes_agree.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_036b"

EDITS: list[tuple[str, str, str]] = [
    (EXPORT,
     "UNLIT_MODES = frozenset({MODE_PURE_SHELL, MODE_ART_UNLIT})\n",

     "UNLIT_MODES = frozenset({MODE_PURE_SHELL, MODE_ART_UNLIT})\n"
     "\n"
     "#: Every mode this module can build. The CLI's `--mode` choices must\n"
     "#: equal this set, and `test_export_modes_agree.py` asserts it by\n"
     "#: parsing main.py rather than by anyone remembering.\n"
     "#:\n"
     "#: There used to be a fourth list: `cmd_export` kept a `mode_map` that\n"
     "#: mapped each CLI string to the constant of the same value -- an\n"
     "#: identity dict whose only effect was to raise KeyError on a mode it had\n"
     "#: not been told about. It did exactly that the first time `art-unlit`\n"
     "#: was typed at a real workspace.\n"
     "MODES = frozenset({MODE_PORTABLE, MODE_ART_UNLIT, MODE_PURE_SHELL,\n"
     "                   MODE_SOURCE})\n"),

    (CMDS,
     "    from packages.exporting.export import (\n"
     "        ExportProfile, MODE_PORTABLE, MODE_PURE_SHELL, MODE_SOURCE,\n"
     "        export_mission, zip_export,\n"
     "    )\n",

     "    from packages.exporting.export import (\n"
     "        MODES, ExportProfile, export_mission, zip_export,\n"
     "    )\n"),

    (CMDS,
     '    mode_map = {"portable-godot": MODE_PORTABLE, "pure-shell": MODE_PURE_SHELL,\n'
     '                "source-authoring": MODE_SOURCE}\n'
     "    profile = ExportProfile(mode=mode_map[args.mode],\n"
     '                            include_walk=bool(getattr(args, "include_walk", False)))\n',

     "    # STRAIGHT THROUGH, as `cmd_portability_test` twelve lines below has\n"
     "    # always done. This mapped each CLI string to the constant holding\n"
     "    # that same string -- an identity dict that had to learn every new\n"
     "    # mode and whose only real behaviour was KeyError on one it had not\n"
     "    # been told about. `art-unlit` hit exactly that, on a real workspace,\n"
     "    # after fourteen tests that all called export_mission directly.\n"
     "    if args.mode not in MODES:\n"
     "        print(f\"unknown export mode {args.mode!r}; \"\n"
     "              f\"known: {', '.join(sorted(MODES))}\", file=sys.stderr)\n"
     "        return EXIT_BLOCKED\n"
     "    profile = ExportProfile(mode=args.mode,\n"
     '                            include_walk=bool(getattr(args, "include_walk", False)))\n'),

    (CHANGELOG,
     "manifest claims, not that the engine likes the result.\n",

     "manifest claims, not that the engine likes the result.\n"
     "\n"
     "AMENDED, SAME VERSION -- A FOURTH LIST NOBODY KNEW WAS A LIST\n"
     "\n"
     "The first real `export --mode art-unlit` against a workspace failed:\n"
     "`internal error: 'art-unlit'`. A KeyError, from a third place the mode\n"
     "had to be registered:\n"
     "\n"
     "    mode_map = {\"portable-godot\": MODE_PORTABLE, ...}\n"
     "\n"
     "Every entry mapped a value to itself -- `MODE_PORTABLE` IS the string\n"
     "`\"portable-godot\"` -- so the dict's only real behaviour was raising\n"
     "KeyError on a mode it had not been told about. `cmd_portability_test`\n"
     "twelve lines below already read `args.mode` straight through, which is\n"
     "the proof it was never needed.\n"
     "\n"
     "The fourteen tests missed it because they exercise `export_mission`,\n"
     "which is the right unit for 'which files does this mode copy'. Nothing\n"
     "exercised `cmd_export`. So the map is deleted, `export.py` publishes\n"
     "`MODES`, and a new test PARSES `main.py` with `ast` and asserts the\n"
     "argparse `--mode` choices and that set are equal in both directions.\n"
     "Adding a fifth mode and forgetting one place is now a failing test\n"
     "rather than a bare KeyError in front of whoever typed it.\n"),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""The CLI's --mode choices and the exporter's modes are one list.

Written after `export --mode art-unlit` failed on a real workspace with
`internal error: 'art-unlit'` -- a KeyError from a third list holding the
same fact. This reads main.py's argparse choices out of the SOURCE rather
than from a copy, so the two cannot drift apart again quietly.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.exporting.export import MODES  # noqa: E402

MAIN = ROOT / "apps" / "cli" / "main.py"


def _mode_choices():
    """Every `choices=[...]` attached to a `--mode` argument in main.py.

    Parsed, not imported: `main.py` builds its parser inside a function and
    importing it to ask would run the CLI's own wiring. The literal is what
    a user is actually constrained by.
    """
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        if not (node.args and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--mode"):
            continue
        for kw in node.keywords:
            if kw.arg == "choices" and isinstance(kw.value, (ast.List, ast.Tuple)):
                found.append(frozenset(
                    e.value for e in kw.value.elts
                    if isinstance(e, ast.Constant)))
    return found


def test_main_declares_mode_choices_somewhere():
    """If this fails the parse broke, and every test below is vacuous."""
    assert _mode_choices(), "no --mode choices found in main.py"


def test_every_cli_choice_is_a_mode_the_exporter_knows():
    """THE BUG. `art-unlit` was a choice the code could not honour."""
    for choices in _mode_choices():
        unknown = choices - MODES
        assert not unknown, f"CLI offers {sorted(unknown)}, exporter knows {sorted(MODES)}"


def test_every_mode_the_exporter_knows_is_reachable_from_the_cli():
    """The other direction: a mode nobody can type is a mode nobody uses."""
    offered = set()
    for choices in _mode_choices():
        offered |= set(choices)
    missing = MODES - offered
    assert not missing, f"exporter knows {sorted(missing)} but no --mode offers it"


def test_all_the_mode_arguments_offer_the_same_set():
    """`export` and `portability-test` both take --mode. A package you can
    build in a mode you cannot then portability-test is half a feature."""
    sets = _mode_choices()
    assert len(set(sets)) == 1, f"--mode choices differ between commands: {sets}"


def test_cmd_export_does_not_keep_its_own_copy():
    """The identity dict, asserted gone.

    `mode_map` mapped each CLI string to the constant of that same value and
    existed only to raise KeyError on a mode it had not learned. Its absence
    is the fix; this is what stops it growing back.
    """
    src = (ROOT / "apps" / "cli" / "commands" / "__init__.py").read_text(
        encoding="utf-8")
    code = "\\n".join(l for l in src.splitlines()
                     if not l.strip().startswith("#"))
    assert "mode_map" not in code
''',
}


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

    print("  the two lists, asserted equal --")
    r = run("tests/unit/test_export_modes_agree.py")
    for line in (r.stdout + r.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THE MODE LISTS AGREE", r.returncode == 0)

    print()
    print("  0.36.0's own tests, unchanged --")
    r2 = run("tests/unit/test_art_unlit_export.py", "tests/unit/test_export_layers.py",
             "tests/unit/test_export_localize.py")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("STILL PASS", r2.returncode == 0)

    print()
    print("  service + integration -- ~2.5 min --")
    r3 = run("tests/service", "tests/integration")
    for line in (r3.stdout + r3.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("STILL GREEN", r3.returncode == 0)

    src = (root / CMDS).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))
    check("the identity dict is gone", "mode_map" not in code)
    check("and cmd_export uses args.mode directly",
          "ExportProfile(mode=args.mode," in code)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("the entry names what actually failed",
          "internal error: 'art-unlit'" in flat)
    check("and says why fourteen tests missed it",
          "Nothing exercised `cmd_export`" in flat)

    print()
    print("  NOT VERIFIED HERE: the export itself. Re-run it --")
    print("    python level_factory\\apps\\cli\\main.py -C <ws> export "
          "<mission> --mode art-unlit --format folder")
    print("    python tools\\probe_unlit_ab.py <ws> <mission>")

    print()
    print("  one list, in one place"
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
        for rel in (EXPORT, CMDS, CHANGELOG):
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
        print("    python patches\\patch_lf_036b.py --selftest")
        print()
        print("  Then the export that failed, and the probe.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
