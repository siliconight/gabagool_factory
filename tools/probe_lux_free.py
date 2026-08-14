r"""Does the exported package need the Lux plugin? Measure, do not assume.

    python probe_lux_free.py <export_dir>

Two claims live inside "Lux isn't needed", and only one of them is true:

  THE FACTORY needs Lux on disk. `lux_apply` is a pipeline job; it runs the
  real addon out of a real checkout. Nothing here disputes that.

  THE PACKAGE must not. `portable-godot` promises no addons, and `localize.py`
  keeps that promise by copying the referenced Lux scripts to `runtime/lux/`
  and rewriting every `res://addons/lux/...` reference to point there.

This probe tests the second claim only, and tests the part that is easy to get
wrong. `scan_closure` already checks that every `res://` path resolves. It
cannot check GDScript's OTHER reference mechanism: a global class name carries
no path, so a script pulled in by name leaves nothing for a path scanner to
follow. That exact hole shipped once -- localize.py's own docstring records the
v0.10.1 hardware run localizing `lux_root.gd` and none of the classes it names,
for 30 parse errors in a clean project and a package that scanned clean.

So this checks four things:

  1. no surviving `res://addons/` reference anywhere in the package
  2. project.godot enables no plugin and declares no autoload
  3. the localized runtime is actually present, not just referenced
  4. CLASS-NAME CLOSURE: every `extends <Name>`, every `script_class=` in a
     .tres, and every Lux-looking identifier used in package scripts resolves
     to a `class_name` declared INSIDE the package

Point 4 is a heuristic and says so where it reports. A clean result here means
no static evidence that Lux is required. The engine's own answer comes from
`level-factory portability-test <mission>`, which opens the package in a clean
project and counts parse errors; a class-name failure surfaces there and
nowhere else. This probe is what you run first because it is instant.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TEXT = {".tscn", ".tres", ".gd", ".gdshader", ".godot", ".cfg", ".import"}

_ADDON_REF = re.compile(r'res://addons/([A-Za-z0-9_]+)/([^"\')\s]*)')
_CLASS_DECL = re.compile(r'^class_name\s+([A-Za-z_]\w*)', re.M)
_EXTENDS = re.compile(r'^extends\s+([A-Za-z_]\w*)', re.M)
_SCRIPT_CLASS = re.compile(r'script_class\s*=\s*"([A-Za-z_]\w*)"')
_LUXY = re.compile(r'\b(Lux[A-Z]\w*)\b')

#: A GDScript string literal, including the &"StringName" form.
_STRING = re.compile(r'&?"(?:[^"\\]|\\.)*"' + r"|&?'(?:[^'\\]|\\.)*'")


def _code_only(text: str) -> str:
    """GDScript with string literals and comments blanked out.

    The `Lux*` scan is looking for a CLASS used by name. Run against raw text
    it also finds node names (`sun.name = &"LuxSun"`), prose inside a preset's
    `description` field, and the word LuxSun inside a comment. Measured on
    lot_demo_001: 8 reported, 8 false, which is an instrument nobody reads
    twice. Blank the non-code first and the check means what it says.
    """
    out = []
    for line in text.splitlines():
        line = _STRING.sub('""', line)
        cut = line.find("#")
        out.append(line if cut == -1 else line[:cut])
    return "\n".join(out)

#: Godot base classes a localized Lux script legitimately extends. Not a full
#: engine list: anything not here is REPORTED, not failed, and the report says
#: which file to look at. A guardrail that guesses at the engine's whole type
#: table would be wrong in a new way every release.
_ENGINE_BASES = {
    "Node", "Node2D", "Node3D", "Resource", "RefCounted", "Object",
    "Control", "CanvasLayer", "Camera3D", "DirectionalLight3D", "OmniLight3D",
    "SpotLight3D", "WorldEnvironment", "MeshInstance3D", "EditorPlugin",
    "EditorInspectorPlugin", "Sprite2D", "Area3D", "StaticBody3D",
    "CharacterBody3D", "RigidBody3D", "Shader", "ShaderMaterial", "Environment",
}


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("usage: probe_lux_free.py <export_dir>")
    root = Path(argv[0])
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    files = [p for p in sorted(root.rglob("*"))
             if p.is_file() and (p.suffix in TEXT or p.name == "project.godot")]
    print(f"probing {root}")
    print(f"  {len(files)} text resource(s)")
    print()

    fail = 0

    # ---------------------------------------------------------- 1. addons/
    print("1. surviving res://addons/ references")
    hits = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in _ADDON_REF.finditer(text):
            hits.append((f.relative_to(root).as_posix(), m.group(0)))
    if hits:
        fail += 1
        for rel, ref in hits[:20]:
            print(f"   FAIL  {rel}: {ref}")
        if len(hits) > 20:
            print(f"   ... and {len(hits) - 20} more")
    else:
        print("   none. Every addon reference was rewritten or stripped.")
    print()

    # ------------------------------------------------- 2. project.godot
    print("2. project.godot")
    proj = root / "project.godot"
    if not proj.is_file():
        print("   FAIL  no project.godot")
        fail += 1
    else:
        ptext = proj.read_text(encoding="utf-8", errors="replace")
        plugin = "enabled=PackedStringArray(" in ptext and "res://addons" in ptext
        autoload = "[autoload]" in ptext
        print(f"   {'FAIL  enables an editor plugin' if plugin else 'no editor plugin enabled'}")
        print(f"   {'FAIL  declares autoload(s)' if autoload else 'no autoloads declared'}")
        fail += plugin + autoload
    print()

    # ------------------------------------------- 3. localized runtime present
    print("3. localized Lux runtime on disk")
    rt = root / "runtime" / "lux"
    if rt.is_dir():
        gd = sorted(rt.rglob("*.gd"))
        tres = sorted(rt.rglob("*.tres"))
        shad = sorted(rt.rglob("*.gdshader"))
        print(f"   present: {len(gd)} script(s), {len(tres)} preset(s), "
              f"{len(shad)} shader(s)")
    else:
        gd = []
        pres_scene = root / "presentation" / "lux.applied.tscn"
        if pres_scene.is_file():
            print("   FAIL  a presentation scene ships but runtime/lux/ is absent")
            fail += 1
        else:
            print("   absent, and no presentation scene ships -- graybox export")
    print()

    # ------------------------------------------------ 4. class-name closure
    print("4. class-name closure  (the check res:// scanning cannot do)")
    declared = set()
    for f in files:
        if f.suffix == ".gd":
            declared |= set(_CLASS_DECL.findall(
                f.read_text(encoding="utf-8", errors="replace")))
    print(f"   {len(declared)} class_name declaration(s) inside the package")

    missing: list[str] = []
    for f in files:
        if f.suffix not in (".gd", ".tres", ".tscn"):
            continue
        rel = f.relative_to(root).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        for name in _EXTENDS.findall(text):
            if name not in declared and name not in _ENGINE_BASES:
                missing.append(f"{rel}: extends {name}")
        for name in _SCRIPT_CLASS.findall(text):
            if name not in declared:
                missing.append(f"{rel}: script_class=\"{name}\"")
        # CODE POSITIONS IN .gd ONLY. A .tscn's `Lux*` hits are node NAMES
        # (`[node name="LuxFixtureLights"]`) and a .tres's are prose in a
        # description field; neither is a class reference, and a scene
        # attaches its scripts by ExtResource path, which check 1 and
        # scan_closure already follow.
        if f.suffix == ".gd":
            for name in set(_LUXY.findall(_code_only(text))):
                if name not in declared:
                    missing.append(f"{rel}: names {name} in code")

    if missing:
        print(f"   {len(missing)} unresolved name(s):")
        for m in sorted(set(missing))[:25]:
            print(f"   FAIL  {m}")
        fail += 1
    else:
        print("   every extends, script_class and Lux* name resolves inside "
              "the package")
    print("   (heuristic: an unlisted ENGINE base class reports here too. Read "
          "the file before believing it.)")
    print()

    # ------------------------------------------------------------- verdict
    print("=" * 62)
    if fail:
        print(f"LUX STILL REQUIRED, or unproven: {fail} check(s) failed above.")
        return 1
    print("NO STATIC EVIDENCE THE PACKAGE NEEDS LUX.")
    print("  The factory still needs the Lux checkout to BUILD -- lux_apply is")
    print("  a pipeline job. This says only that the OUTPUT stands alone.")
    print("  Confirm with the engine before claiming it:")
    print("    level-factory portability-test <mission_id>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
