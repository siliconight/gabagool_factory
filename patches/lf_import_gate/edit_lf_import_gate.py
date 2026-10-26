"""Level Factory 0.257.0 on a clone: a walk whose preview did not finish importing fails and says why, and the
authoring project is committed in the Godot editor's own format (the factory's
docs/findings/walk_2026-10-26_panel/, L1 and P7). Anchored; refuses on a miss.

    python edit_lf_import_gate.py <clone>

Copies packages/preview/import_gate.py, tests/unit/test_walk_import_gate.py and apps/godot/README.md from `src/`.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for p in sorted((HERE / "src").rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(HERE / "src")).replace("\\", "/")
        assert not (C / rel).exists(), rel
        (C / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, C / rel)
        print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("apps/cli/commands/__init__.py", [
    ('''    godot_exe = str(ws.load_tools_local().get("godot_executable") or "")
    if godot_exe:
        try:
            subprocess.run([godot_exe, "--headless", "--path", report["dest"],
                            "--import"], capture_output=True, timeout=600)
            print("  imported: resources ready (headless --import pass)")
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"  WARNING: headless import failed ({exc}) -- open once "
                  f"with -e before playing", file=sys.stderr)
''', '''    #
    # AND A FAILED IMPORT FAILS THE WALK (0.257.0). It was a warning, and the
    # walker fell through the floor of the first building they walked into: the
    # import had been killed at its 600 s timeout with 96 of 758 imports
    # unwritten, every shell among them, and the walk finished ok (the
    # factory's docs/findings/walk_2026-10-26_panel/, L1). Judged by what the
    # pass left, with the light bake's bound for importing the same package.
    godot_exe = str(ws.load_tools_local().get("godot_executable") or "")
    if godot_exe:
        from packages.preview import import_gate
        imported, said = import_gate.import_preview(godot_exe, Path(report["dest"]))
        if not imported:
            print(f"BLOCKED: the walk preview is not playable: {said}. Walk "
                  f"again; it re-runs the import.", file=sys.stderr)
            return EXIT_BLOCKED
        print(f"  {said}")
'''),
])

edit("packages/service/walking.py", [
    ('''            if code not in (0, 1):
                raise layouts.LayoutError("leg_failed", "the preview exited %d; its output is in %s" % (code, log))''',
     '''            if code not in (0, 1):
                # say WHY when the walk said it (0.257.0: a preview that did not finish importing BLOCKS)
                blocked = [ln for ln in log.read_text(encoding="utf-8", errors="replace").splitlines()
                           if ln.startswith("BLOCKED:")] if log.exists() else []
                raise layouts.LayoutError("leg_failed", (blocked[-1][len("BLOCKED: "):] if blocked else
                                                         "the preview exited %d" % code)
                                          + "; its output is in %s" % log)'''),
])

# P7: the editor rewrites project.godot in its own format whenever it saves, which dirtied the repo the first time
# the walker closed it. Commit the editor's form; the note that headed the file moves to the project's README.
edit("apps/godot/project.godot", [
    ('''; The Gabagool Factory authoring project: open this folder in Godot 4.7 and the Factory panel appears in the
; right-hand dock. It finds the factory by walking up from here (`docs/AUTHORING_LOOP.md` at the factory root).
''', '''; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters
'''),
])
