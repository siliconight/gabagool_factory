"""Lux 0.78.0: Lux's runtime scaffolding stays ownerless in the editor, unless a LuxRoot asks (factory roadmap 24).

MEASURED FIRST (the factory's `docs/findings/lux_owner_24/`): `owner_probe.py` opened cold run 9323's shipped
`presentation/lux.applied.tscn` in Godot's headless editor, let the @tool scripts run, saved, and diffed. One save
ADDED 7 nodes to the shipped scene -- `LuxRoot/LuxSun`, `LuxRoot/LuxWorldEnvironment`, and the post stack (a
CanvasLayer, auto-named because the `LuxPostFX` module already holds the name, with its BackBufferCopy,
LuxPostRect, LuxCRTBackBuffer and LuxCRTRect). A second save added the same 7, not 14: `_build_modules` clears its
own scaffolding before it rebuilds (`patch_lux_rebuild.py`'s loop), so the clean editor does not multiply what it
keeps -- the item's four suns need something else, still not isolated. What it keeps is the defect: runtime
scaffolding saved into a shipped scene by one Ctrl+S, which a consumer then carries in version control.

THE CAUSE, read at the sites: every one of the seven is owned to `edited_scene_root` under
`if Engine.is_editor_hint()` -- `lux_environment.gd` (the WorldEnvironment), `lux_lighting.gd` (the sun),
`lux_post_fx.gd` (the stack, two blocks). Ownership is the whole difference between scaffolding and a member a
save keeps (the item, 2026-08-01). The light loader and fixture spawner own what the APPLY step persists, and are
not touched.

THE RULE, a call made 2026-10-19 under the walker's standing instruction to make decisions that can be changed
later: runtime scaffolding is ownerless in the editor too, so the editor still draws it and no save keeps it; a
LuxRoot that wants it kept as its own nodes says so, `persist_scaffolding_in_editor` (default off), and the four
sites ask it. Lux's dock and editor plugin own none of these nodes and reference none of them.

What it changes (anchored; each file pinned by hash; nothing written on a miss; LF-safe):
  * addons/lux/runtime/lux_root.gd -- `@export_group("Editor")`, `persist_scaffolding_in_editor`.
  * addons/lux/runtime/lux_environment.gd, lux_lighting.gd, lux_post_fx.gd -- the four owner sites ask it.
  * tools/scaffold_owner_selftest.gd (new): the setting exists, defaults off, and every editor-time owner site in
    the three modules asks it (fails on 0.77.0).
  * VERSION 0.77.0 -> 0.78.0, CHANGELOG.

THE BEHAVIOUR'S PROOF is the factory's probe re-run on a copy of the same package carrying this runtime
(`owner_probe.py ... --runtime lux/addons/lux/runtime`): a save adds nothing.

    python patches/patch_lux_scaffold_ownerless.py --tests   # the selftest only (prove it fails first)
    python patches/patch_lux_scaffold_ownerless.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LUX = ROOT / "lux"
RT = LUX / "addons" / "lux" / "runtime"
FILES = {
    RT / "lux_root.gd": "3c9676ad06c260ad",
    RT / "lux_environment.gd": "99871731f4271af7",
    RT / "lux_lighting.gd": "9007cfc5d402091d",
    RT / "lux_post_fx.gd": "506a8b535d43c48b",
}

ROOT_OLD = '@export_group("Startup")\n@export var apply_on_ready: bool = true\n'
ROOT_NEW = '''@export_group("Editor")
## KEEP LUX'S RUNTIME SCAFFOLDING WHEN THE SCENE IS SAVED IN THE EDITOR (0.78.0,
## the factory's roadmap 24). Off by default: the WorldEnvironment, sun and post
## stack this node builds on ready are runtime scaffolding, and owned to the
## edited scene one Ctrl+S kept all seven of those nodes in it -- measured by
## opening a shipped `lux.applied.tscn` in the editor and saving it (the
## factory's docs/findings/lux_owner_24/). Off, the editor still draws them and
## no save keeps them. On, they are owned again and shown in the Scene dock,
## for a level that wants them as its own nodes. A call made 2026-10-19 and
## meant to be changed.
@export var persist_scaffolding_in_editor: bool = false

''' + ROOT_OLD

GUARD_OLD = "\tif Engine.is_editor_hint() and parent.get_tree() != null:\n"
GUARD_NEW = ("\t# Ownerless in the editor too unless the LuxRoot asks (0.78.0, factory roadmap 24):\n"
             "\t# owned, one Ctrl+S kept this runtime scaffolding in the scene.\n"
             "\tif Engine.is_editor_hint() and parent.get_tree() != null \\\n"
             "\t\t\tand parent.get(\"persist_scaffolding_in_editor\") == true:\n")

SELFTEST = r'''extends SceneTree
## Lux's runtime scaffolding stays ownerless in the editor unless a LuxRoot asks (0.78.0, the factory's roadmap 24).
##
##     godot --headless --path lux -s res://tools/scaffold_owner_selftest.gd
##
## Exit 0 = every check held. Exit 1 = a check failed. Exit 2 = could not run.
##
## The behaviour needs the editor, so it is proven where the defect was measured: the factory's
## docs/findings/lux_owner_24/owner_probe.py opens a shipped scene in the headless editor, saves it and diffs --
## 7 nodes added on 0.77.0, none on 0.78.0. This holds the rule in the source, outside the editor: LuxRoot carries
## `persist_scaffolding_in_editor`, off by default, and every editor-time owner assignment in the environment,
## lighting and post-FX modules asks it. Fails on 0.77.0, which has no setting.

const ROOT_SCRIPT := "res://addons/lux/runtime/lux_root.gd"
const MODULES := ["res://addons/lux/runtime/lux_environment.gd", "res://addons/lux/runtime/lux_lighting.gd",
	"res://addons/lux/runtime/lux_post_fx.gd"]

var _fails: int = 0


func _initialize() -> void:
	_main()


func _check(label: String, ok: bool) -> void:
	if not ok:
		_fails += 1
	print("%s  %s" % ["ok  " if ok else "FAIL", label])


func _main() -> void:
	if not ResourceLoader.exists(ROOT_SCRIPT):
		print("could not run: no %s" % ROOT_SCRIPT)
		quit(2)
		return
	var script: GDScript = load(ROOT_SCRIPT) as GDScript
	var found: bool = false
	var default_off: bool = false
	for p in script.get_script_property_list():
		if String(p.get("name", "")) == "persist_scaffolding_in_editor":
			found = true
	if found:
		default_off = script.get_property_default_value(&"persist_scaffolding_in_editor") == false
	_check("LuxRoot carries persist_scaffolding_in_editor", found)
	_check("and it is off by default", default_off)
	for path in MODULES:
		var src: String = FileAccess.get_file_as_string(path)
		var sites: int = 0
		var asked: int = 0
		var lines: PackedStringArray = src.split("\n")
		for i in range(lines.size()):
			var ln: String = lines[i]
			if ln.contains("Engine.is_editor_hint()") and ln.contains("get_tree() != null"):
				sites += 1
				var block: String = ln + (lines[i + 1] if i + 1 < lines.size() else "")
				if block.contains("persist_scaffolding_in_editor"):
					asked += 1
		_check("%s: %d editor-time owner site(s), every one asks the LuxRoot" % [path.get_file(), sites],
			sites > 0 and asked == sites)
	print("selftest: %d check(s) failed" % _fails)
	quit(1 if _fails > 0 else 0)
'''

CHANGELOG = '''## [0.78.0] - runtime scaffolding stays ownerless in the editor, unless a LuxRoot asks

**The factory's roadmap 24, measured.** Opening cold run 9323's shipped `lux.applied.tscn` in Godot's headless
editor and saving it ADDED 7 nodes: `LuxSun`, `LuxWorldEnvironment`, and the post stack's CanvasLayer with its
BackBufferCopy, LuxPostRect, LuxCRTBackBuffer and LuxCRTRect. A second save added the same 7, not 14, because
`_build_modules` clears its own scaffolding first, so a clean editor keeps it without multiplying it. Every one was
owned to `edited_scene_root` under `if Engine.is_editor_hint()` in the environment, lighting and post-FX modules,
and ownership is all that separates scaffolding from a member a save keeps.

**The rule, a call made 2026-10-19 and meant to be changed:** runtime scaffolding is ownerless in the editor too.
The editor still draws it, and no save keeps it. A LuxRoot that wants it kept sets `persist_scaffolding_in_editor`,
default off. The light loader and fixture spawner own what the apply step persists, and are unchanged.

### Added
- `LuxRoot.persist_scaffolding_in_editor` (an Editor group), asked by the four editor-time owner sites.
- `tools/scaffold_owner_selftest.gd`, which fails on 0.77.0.

### Proven
The factory's `docs/findings/lux_owner_24/owner_probe.py`, re-run on a copy of the same package carrying this
runtime: a save adds nothing.

'''


def _once(text, old, new, what, count=1):
    assert text.count(old) == count, (what, text.count(old))
    return text.replace(old, new)


def write_tests():
    p = LUX / "tools" / "scaffold_owner_selftest.gd"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(SELFTEST, encoding="utf-8", newline="\n")
    print("wrote lux/tools/scaffold_owner_selftest.gd")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    texts = {}
    for path, sha in FILES.items():
        raw = path.read_bytes()
        assert b"\r\n" not in raw, f"{path.name} is LF"
        got = hashlib.sha256(raw).hexdigest()[:16]
        assert got == sha, (f"{path.name} is not the file this patch read", got)
        texts[path] = raw.decode("utf-8")
    assert "persist_scaffolding_in_editor" not in texts[RT / "lux_root.gd"], "already applied"
    texts[RT / "lux_root.gd"] = _once(texts[RT / "lux_root.gd"], ROOT_OLD, ROOT_NEW, "LuxRoot's Startup group")
    texts[RT / "lux_environment.gd"] = _once(texts[RT / "lux_environment.gd"], GUARD_OLD, GUARD_NEW, "the environment's site")
    texts[RT / "lux_lighting.gd"] = _once(texts[RT / "lux_lighting.gd"], GUARD_OLD, GUARD_NEW, "the sun's site")
    texts[RT / "lux_post_fx.gd"] = _once(texts[RT / "lux_post_fx.gd"], GUARD_OLD, GUARD_NEW, "the post stack's sites", 2)
    v = LUX / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Lux 0.77.0", v.read_text(encoding="utf-8")
    cl = LUX / "CHANGELOG.md"
    rawc = cl.read_bytes()
    assert b"\r\n" not in rawc, "CHANGELOG.md is LF"
    text = rawc.decode("utf-8")
    head = "# Changelog\n\n"
    assert text.startswith(head + "## [0.77.0]"), text[:60]
    for path, t in texts.items():
        path.write_bytes(t.encode("utf-8"))
    v.write_text("Lux 0.78.0", encoding="utf-8")
    cl.write_bytes((head + CHANGELOG + text[len(head):]).encode("utf-8"))
    write_tests()
    print("Lux 0.78.0 applied: four owner sites ask LuxRoot.persist_scaffolding_in_editor; selftest, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
