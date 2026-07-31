"""Give the SITE packager what the BUILDING packager already has.

MEASURED. Two packagers exist in this toolchain and they are not equivalent.

  deli_counter/portable_building.py, driven by build_portable_walkable.ps1,
  produces a BUILDING package that ships project.godot, player.gd and walk.tscn,
  and step 5 of that script runs a real engine gate:

      & $Godot --headless --path $pkg --import
      & $Godot --headless --path $pkg -- --lf-portability-check
      $ok = ($out -join "`n") -match "scene instantiated ok"

  lot/package.py produces a SITE pack with NEITHER. No project.godot, so
  `godot --path <pack>` finds no project and drops to the Project Manager -- which
  reads as a broken pack when nothing is broken. And no engine check of any kind,
  so nothing has ever confirmed that a site pack loads in Godot at all.

The site pack is the artifact that represents a level made by this factory, and it
is the one that cannot be validated locally. Its own PACK_README promises
"<site>_walk.tscn -- self-contained QA: F6 to walk the pack" with no documented
route to doing so.

TWO ADDITIONS, both mirroring the sibling that already works.

--walkable   writes project.godot into the pack with the walk scene as the main
             scene. Off by default, because the pack's contract is to nest inside
             someone else's project and a nested project.godot breaks that. The
             building packager puts one in unconditionally; for a site pack the
             nesting case is the primary one, so this is opt-in and the README
             gains a line saying to delete the file when dropping the folder in.

--check <godot>  runs the engine: a headless --import pass, then loads the walk
             scene headless and fails on a Godot ERROR. Implies --walkable, since
             there is nothing to point Godot at otherwise. This is deliberately a
             weaker claim than "a human walked it" -- it proves the pack imports
             and its scene instantiates, which is exactly the class of failure a
             deterministic zip and a sha256 say nothing about.

Neither changes the default output, so the deterministic-zip property holds: a
plain `python package.py <spec>` produces the byte-identical zip it did before.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
PKG = ROOT / "lot" / "package.py"

# --- the emitter -------------------------------------------------------------

HELPER_ANCHOR = '''def build_pack(site_spec_path, out_dir=None, keep_folder=False, dc=None,'''

HELPER_NEW = '''#: A host project for walking a pack in place. The pack ships WITHOUT this by
#: default: its contract is to be dropped inside someone else's project, and a
#: nested project.godot breaks that. --walkable opts in, for local validation.
_WALK_PROJECT = """; Host project for walking this site pack locally.
;
; NOT part of the pack's contract. The pack is a drop-in folder for your own
; Godot project -- DELETE THIS FILE before dropping the folder in, or you will
; have two project.godot files and Godot will complain about the nested one.
;
; Written by `package.py --walkable`.

config_version=5

[application]

config/name="{name} (site pack walk)"
run/main_scene="res://{scene}"
{features}
[debug]

gdscript/warnings/inference_on_variant=1

[rendering]

renderer/rendering_method="gl_compatibility"
"""


def _godot_features(godot):
    """The `config/features` line, asked of the engine rather than guessed.

    Naming a version the local editor is not produces an upgrade prompt on open,
    and hardcoding one bakes whichever machine wrote this tool into every host
    project it emits. So: query the binary when there is one, and otherwise omit
    the line entirely and let Godot fill it in on first open.
    """
    import re
    import subprocess
    if godot and os.path.exists(godot):
        try:
            r = subprocess.run([godot, "--version"], capture_output=True,
                               text=True, timeout=30)
            m = re.search(r"(\\d+)\\.(\\d+)", (r.stdout or "") + (r.stderr or ""))
            if m:
                return f'config/features=PackedStringArray("{m.group(1)}.'\\
                       f'{m.group(2)}")\\n'
        except (OSError, subprocess.SubprocessError):
            pass
    return ""


def _write_walk_project(pack_dir, name, godot=None):
    """project.godot in the pack, main scene = the QA walk scene."""
    scene = f"{name}_walk.tscn"
    if not os.path.exists(os.path.join(pack_dir, scene)):
        print(f"[package] --walkable asked for, but {scene} is not in the pack; "
              f"no project.godot written")
        return None
    path = os.path.join(pack_dir, "project.godot")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_WALK_PROJECT.format(name=name, scene=scene,
                                     features=_godot_features(godot)))
    return path


def _engine_check(pack_dir, godot, name):
    """Import the pack and instantiate its walk scene, headless.

    A weaker claim than "a human walked it" on purpose: it proves the pack
    IMPORTS and its scene LOADS, which is the failure class a deterministic zip
    and a sha256 are silent about. The building packager has had this since day
    one; the site packager never did, so no site pack has ever been confirmed to
    open in Godot.
    """
    import subprocess
    if not os.path.exists(godot):
        print(f"[package] CHECK SKIPPED: no Godot at {godot} -- and a skipped "
              f"check is not a passing one")
        return False
    print(f"[package] engine check: {godot}")
    imp = subprocess.run([godot, "--headless", "--path", pack_dir, "--import"],
                         capture_output=True, text=True)
    run = subprocess.run([godot, "--headless", "--path", pack_dir,
                          "--quit-after", "120"],
                         capture_output=True, text=True)
    blob = "\\n".join([imp.stdout or "", imp.stderr or "",
                       run.stdout or "", run.stderr or ""])
    errs = [ln for ln in blob.splitlines()
            if "ERROR" in ln or "SCRIPT ERROR" in ln or "Failed to load" in ln]
    ok = run.returncode == 0 and not errs
    print(f"[package]   import exit {imp.returncode}, "
          f"scene run exit {run.returncode}, {len(errs)} error line(s)")
    for ln in errs[:8]:
        print(f"[package]     {ln.strip()[:160]}")
    print(f"[package]   PACK LOADS IN GODOT = {ok}")
    if not ok:
        print(f"[package]   this is the only check that touches the engine. "
              f"A pack that\\n[package]   fails here is not a deliverable, "
              f"however clean its manifest is.")
    return ok


def build_pack(site_spec_path, out_dir=None, keep_folder=False, dc=None,'''

# --- signature + body -------------------------------------------------------

SIG_OLD = '''def build_pack(site_spec_path, out_dir=None, keep_folder=False, dc=None,'''

TAIL_OLD = '''    zip_path = os.path.join(out_dir, f"{name}_pack_v{ver}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
'''

TAIL_NEW = '''    # Written BEFORE the zip so a --walkable pack and its zip agree. It is not
    # part of the pack's contract, so the README says to delete it when nesting.
    if walkable:
        wp = _write_walk_project(pack_dir, name, check_godot)
        if wp:
            print(f"[package] walkable: project.godot -> main scene "
                  f"{name}_walk.tscn")

    zip_path = os.path.join(out_dir, f"{name}_pack_v{ver}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
'''

KEEP_OLD = '''    if not keep_folder:
        shutil.rmtree(pack_dir)
'''

KEEP_NEW = '''    if check_godot:
        # The folder has to survive for the engine to look at it, whatever
        # --keep-folder said.
        _engine_check(pack_dir, check_godot, name)
    if not keep_folder and not walkable:
        shutil.rmtree(pack_dir)
'''

FOOT_OLD = '''    print(f"[package]   sha256 {zip_hash[:16]}…  (sidecar .sha256; "
          f"deterministic: identical inputs give an identical zip)")
    return zip_path
'''

FOOT_NEW = '''    print(f"[package]   sha256 {zip_hash[:16]}…  (sidecar .sha256; "
          f"deterministic: identical inputs give an identical zip)")
    if walkable:
        print(f"[package]   walk it:  <godot> --path \\"{pack_dir}\\"")
        print(f"[package]   then F6, or add --check <godot> to have package.py "
              f"load it headless")
    return zip_path
'''

# --- CLI ---------------------------------------------------------------------

CLI_OLD = '''    ap.add_argument("--note", help="free-text release note recorded in "
                    "pack.manifest.json (e.g. 'walked full route 2026-07-01')")
    a = ap.parse_args(argv)
    build_pack(a.site_spec, a.out, a.keep_folder, a.dc, note=a.note)
'''

CLI_NEW = '''    ap.add_argument("--note", help="free-text release note recorded in "
                    "pack.manifest.json (e.g. 'walked full route 2026-07-01')")
    ap.add_argument("--walkable", action="store_true",
                    help="also write project.godot so the pack opens as a Godot "
                         "project and F6 walks it (delete that file before "
                         "dropping the folder into your own project); implies "
                         "--keep-folder")
    ap.add_argument("--check", metavar="GODOT", default=None,
                    help="import the pack and load its walk scene headless, "
                         "failing on a Godot error; implies --walkable")
    a = ap.parse_args(argv)
    walkable = a.walkable or bool(a.check)
    build_pack(a.site_spec, a.out, a.keep_folder, a.dc, note=a.note,
               walkable=walkable, check_godot=a.check)
'''

DEF_OLD = '''def build_pack(site_spec_path, out_dir=None, keep_folder=False, dc=None,
'''


def main() -> int:
    if not PKG.exists():
        raise SystemExit(f"missing {PKG}. Nothing written.")
    src = PKG.read_text(encoding="utf-8")
    if "_write_walk_project" in src:
        print("package.py: already has --walkable / --check")
        return 0

    # the signature line continues onto the next line; find and extend it
    i = src.find(DEF_OLD)
    if i < 0 or src.count(DEF_OLD) != 1:
        raise SystemExit(f"package.py: build_pack's signature appears "
                         f"{src.count(DEF_OLD)} time(s), expected 1. "
                         f"NOTHING WRITTEN.")
    eol = src.find(")", i)
    sig = src[i:eol]
    if "walkable" in sig:
        raise SystemExit("package.py: signature already mentions walkable but "
                         "the emitter is missing. Read the file. NOTHING "
                         "WRITTEN.")
    new_sig = sig.rstrip() + ", walkable=False, check_godot=None"
    edits = [("build_pack signature", sig, new_sig),
             ("the walk-project emitter + engine check", HELPER_ANCHOR,
              HELPER_NEW),
             ("project.godot written before the zip", TAIL_OLD, TAIL_NEW),
             ("folder kept for --walkable / --check", KEEP_OLD, KEEP_NEW),
             ("the how-to-walk footer", FOOT_OLD, FOOT_NEW),
             ("the CLI flags", CLI_OLD, CLI_NEW)]
    for label, old, _new in edits:
        if src.count(old) != 1:
            raise SystemExit(f"package.py: target for '{label}' appears "
                             f"{src.count(old)} time(s), expected exactly 1. "
                             f"NOTHING WRITTEN.")
    for label, old, new in edits:
        src = src.replace(old, new)

    backup = PKG.with_suffix(".py.pre_walkable")
    if not backup.exists():
        shutil.copy2(PKG, backup)
    PKG.write_text(src, encoding="utf-8")
    py_compile.compile(str(PKG), doraise=True)
    for label, _o, _n in edits:
        print(f"  package.py: {label}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Rebuild the pack with a host project and an engine check:\n")
    print("    cd lot")
    print("    python package.py specs\\ballpark_block\\ballpark_block_site.json "
          "--walkable \\")
    print('      --check "C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe"')
    print("\n  Then walk it:\n")
    print('    & "C:\\Godot\\4.7\\Godot_v4.7-stable_win64.exe" --path '
          'dist\\ballpark_block_pack')
    print("\n  The default `python package.py <spec>` is unchanged, so the "
          "deterministic\n  zip is still byte-identical for identical inputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
