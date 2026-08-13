r"""Point the self-check bots at the scene the preview actually wraps.

    python patch_lf_walk_bot_scene.py --check
    python patch_lf_walk_bot_scene.py
    python patch_lf_walk_bot_scene.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

TWO DEFECTS, BOTH INTRODUCED BY WALKING THE EXPORT.

1. THE SELF-CHECK HAS NOT RUN SINCE `patch_lf_walk_the_export.py`.

`walk_bot.gd` and `shot_bot.gd` both default to `var _scene_path :=
"res://site.tscn"` and both already accept an override -- args[1] for the walk
bot, args[2] for the shot bot. `walk_bot.py` passes neither. That was harmless
while the preview copied the content scene next to its wrapper; the preview now
wraps the EXPORT's `mission.tscn`, and `site.tscn` is not reachable from it, so
it is not copied in. Measured on lot_demo_001's preview directory: no
`site.tscn`, no `buildings/`.

    walk bot: ERROR cannot load scene res://site.tscn
    shot bot: ERROR cannot load scene res://site.tscn
    the preview is built, but this level does not pass its own
    traversal/visual check -- walk it and confirm before shipping

That last line reads as a verdict and is an absence. Both bots died before
walking anything, and the sentence is indistinguishable from a level that
failed. Same shape as the closure scan certifying an empty package, in the
instrument that was supposed to catch it.

`build_walk_preview` already returns `level_scene`, and `cmd_walk` already
prints it. The value was sitting in the report the whole time.

2. THE PREVIEW PROJECT LACKS THE WARNING SETTING THE EXPORT WRITES.

`export.py::_write_project_godot` sets
`gdscript/warnings/inference_on_variant=1` with a comment recording why:
engine defaults escalate inference-on-Variant to a LOAD-KILLING error, and it
"took two dependents down as compile knock-ons" on real hardware. The preview
builder writes its own `project.godot` and never got it, so the same localized
scripts parse in one project and not the other:

    preview:   SCRIPT ERROR: Parse Error ... lux_area_light_rig.gd:61
               ERROR: Failed to load script ... with error "Parse error"
    export:    portability-test -> parser_error_count: 0

Both numbers are correct. They are different projects. The area-light rig was
simply not loading in the preview, which means the lighting a human signed off
by eye was missing a rig.

Copied verbatim from `export.py`, comment included, because two projects
disagreeing about what a complete `project.godot` contains is exactly the
defect `cater.py` is carried in the roadmap for.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BOT = Path("level_factory/packages/preview/walk_bot.py")
PREVIEW = Path("level_factory/packages/preview/walk_preview.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_botscene"


OLD_WALK = '''def run_walk_bot(godot_exe, project_dir, *, out_json=None, timeout=600) -> dict:
    """Physics traversal proof. Returns the parsed verdict dict."""
    project_dir = Path(project_dir)
    out = Path(out_json) if out_json else project_dir / "walkbot.json"
    proc = _run([str(godot_exe), "--headless", "--path", str(project_dir),
                 "--script", WALK_SCRIPT, "--", str(out)], timeout)
    return _read_verdict(out, proc, "walk bot")'''

NEW_WALK = '''def run_walk_bot(godot_exe, project_dir, *, out_json=None, scene=None,
                 timeout=600) -> dict:
    """Physics traversal proof. Returns the parsed verdict dict.

    `scene` is the project-relative scene to walk. `walk_bot.gd` reads it from
    args[1] and has always been able to; nothing passed it, so it fell back to
    its `res://site.tscn` default. That default stopped existing when the
    preview began wrapping the export's `mission.tscn`, and the bot failed to
    load anything while the run still printed a sentence about the level not
    passing its own check.
    """
    project_dir = Path(project_dir)
    out = Path(out_json) if out_json else project_dir / "walkbot.json"
    argv = [str(godot_exe), "--headless", "--path", str(project_dir),
            "--script", WALK_SCRIPT, "--", str(out)]
    if scene:
        argv.append(_res_path(scene))
    proc = _run(argv, timeout)
    return _read_verdict(out, proc, "walk bot")'''


OLD_SHOT = '''    proc = _run([*prefix, str(godot_exe), "--rendering-driver", "opengl3",
                 "--path", str(project_dir), "--script", SHOT_SCRIPT,
                 "--", str(out), str(shots)], timeout)
    return _read_verdict(out, proc, "shot bot")'''

NEW_SHOT = '''    argv = [*prefix, str(godot_exe), "--rendering-driver", "opengl3",
            "--path", str(project_dir), "--script", SHOT_SCRIPT,
            "--", str(out), str(shots)]
    if scene:
        # args[2] for this one; the walk bot reads args[1]. The scripts differ
        # and the order is theirs, so it is read from them rather than assumed.
        argv.append(_res_path(scene))
    proc = _run(argv, timeout)
    return _read_verdict(out, proc, "shot bot")'''


OLD_SHOT_SIG = '''def run_shot_bot(godot_exe, project_dir, *, shots_dir=None, out_json=None,
                 timeout=900) -> dict:'''

NEW_SHOT_SIG = '''def _res_path(scene: str) -> str:
    """A bare scene name as the bots expect it: a `res://` path."""
    return scene if str(scene).startswith("res://") else f"res://{scene}"


def run_shot_bot(godot_exe, project_dir, *, shots_dir=None, out_json=None,
                 scene=None, timeout=900) -> dict:'''


OLD_CALL_WALK = '''                walk_v = _bot.run_walk_bot(godot_exe, report["dest"])'''
NEW_CALL_WALK = '''                walk_v = _bot.run_walk_bot(godot_exe, report["dest"],
                                           scene=report.get("level_scene"))'''

OLD_CALL_SHOT = '''                shot_v = _bot.run_shot_bot(godot_exe, report["dest"])'''
NEW_CALL_SHOT = '''                shot_v = _bot.run_shot_bot(godot_exe, report["dest"],
                                           scene=report.get("level_scene"))'''


OLD_PROJECT = '''[rendering]
renderer/rendering_method="gl_compatibility"
"""'''

NEW_PROJECT = '''[rendering]
renderer/rendering_method="gl_compatibility"

[debug]
; Verbatim from export.py::_write_project_godot, and it must stay verbatim:
; localized tool scripts are strict-clean under their home projects' warning
; config, while engine DEFAULTS escalate inference-on-Variant to a load-killing
; error. Proven on hardware -- lux_root.gd:218 took two dependents down as
; compile knock-ons -- and proven again here on 2026-08-12, where the preview
; lacked this block and lux_area_light_rig.gd:61 failed to parse in a walk of
; the same package the export's portability test scored parser_error_count 0.
; Two projects disagreeing about what a complete project.godot contains is how
; a human signs off lighting that was missing a rig.
gdscript/warnings/inference_on_variant=1
"""'''


EDITS = {
    BOT: ((OLD_WALK, NEW_WALK), (OLD_SHOT_SIG, NEW_SHOT_SIG),
          (OLD_SHOT, NEW_SHOT)),
    COMMANDS: ((OLD_CALL_WALK, NEW_CALL_WALK), (OLD_CALL_SHOT, NEW_CALL_SHOT)),
    PREVIEW: ((OLD_PROJECT, NEW_PROJECT),),
}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

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
            print(f"  anchor starts: {old.splitlines()[0][:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
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


def main(argv: list[str]) -> int:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
