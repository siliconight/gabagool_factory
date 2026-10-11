"""Laser Tag 0.27.0: the navigation map updates on the evaluation's own thread, so the clock need not
wait on real seconds (factory roadmap 239).

Anchored edits: `scripts/core/LT_Const.gd` (`synchronous_navigation`, `navigation_is_synchronous`:
the world's map, every region under a scene and each region's own map set synchronous, and the
dial read back), `runners/run_map_eval.gd` (`_run` sets them before the bake, lets a physics frame
pass for the server commands to land, reads them back and says so; the header documents the
engine's `--fixed-fps 60` and what `--time-scale` multiplies; the clock comment that said the
evaluation did not wait on real seconds corrected), and a new
`runners/tests/test_navigation_is_synchronous.gd` from `lt_sync_nav/test_navigation_is_synchronous.gd.txt`.
Each file pinned by hash and each anchor asserted once, nothing written on a miss; the files' own
line endings kept. Applies on 0.26.0. CHANGELOG and VERSION from `lt_sync_nav/CHANGELOG_0.27.0.md`;
`--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_lt_sync_nav.py --results-pending
    python patches/patch_lt_sync_nav.py --fill
    LT_ROOT=<a copy, or a staged project's root> python patches/patch_lt_sync_nav.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_sync_nav"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_TESTS": "result_tests.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.26.0", b"Laser Tag 0.27.0"
CHANGELOG_HEAD = "# Changelog\n\n## [0.26.0] - an enemy is the contract's body too\n"
A = "addons/laser_tag_tool/"
CONST = A + "scripts/core/LT_Const.gd"
RUNNER = A + "runners/run_map_eval.gd"
TEST = A + "runners/tests/test_navigation_is_synchronous.gd"
SHA = {CONST: "e0c9e4fc94887ad5", RUNNER: "c757deeecf9cefb2"}

C_OLD = ("\treturn sqrt(horizontal * horizontal + vertical * vertical)\n"
         "\n"
         "static func _ensure_key(action: StringName, keycode: Key) -> void:\n")
C_NEW = ("\treturn sqrt(horizontal * horizontal + vertical * vertical)\n"
         "\n"
         "## THE NAVIGATION MAP UPDATES ON THE CALLER'S THREAD (0.27.0, factory roadmap\n"
         "## 239). Godot 4.7 runs a map's and a region's iterations on worker threads\n"
         "## unless told otherwise, so WHEN a navigation update lands is wall time, and\n"
         "## an evaluation that reads it repeats only as far as the machine is idle:\n"
         "## three evaluations at once moved a few event positions by 0.01 m, and the\n"
         "## engine's `--fixed-fps` clock moved a crew's stuck count 9 -> 21 with the\n"
         "## physics step unchanged. Synchronous, every report measured read the same\n"
         "## under either clock and any load. This sets the world's map, every region\n"
         "## under `scene_root` and each region's own map, and returns how many regions\n"
         "## it set. The setters are server COMMANDS that land at the next sync -- read\n"
         "## straight back they still say asynchronous (measured) -- so a caller lets a\n"
         "## physics frame pass before it asks `navigation_is_synchronous`.\n"
         "static func synchronous_navigation(scene_root: Node) -> int:\n"
         "\tvar count := 0\n"
         "\tvar viewport: Viewport = scene_root.get_viewport()\n"
         "\tif viewport != null and viewport.get_world_3d() != null:\n"
         "\t\tNavigationServer3D.map_set_use_async_iterations(\n"
         "\t\t\tviewport.get_world_3d().navigation_map, false)\n"
         "\tfor node in scene_root.find_children(\"*\", \"NavigationRegion3D\", true, false):\n"
         "\t\tvar region: NavigationRegion3D = node as NavigationRegion3D\n"
         "\t\tif region.get_navigation_map().is_valid():\n"
         "\t\t\tNavigationServer3D.map_set_use_async_iterations(region.get_navigation_map(), false)\n"
         "\t\tNavigationServer3D.region_set_use_async_iterations(region.get_rid(), false)\n"
         "\t\tcount += 1\n"
         "\treturn count\n"
         "\n"
         "## Whether the world's map and every region under `scene_root` (and its map)\n"
         "## update synchronously: the dial read back, once the commands have landed.\n"
         "static func navigation_is_synchronous(scene_root: Node) -> bool:\n"
         "\tvar viewport: Viewport = scene_root.get_viewport()\n"
         "\tif viewport != null and viewport.get_world_3d() != null:\n"
         "\t\tif NavigationServer3D.map_get_use_async_iterations(viewport.get_world_3d().navigation_map):\n"
         "\t\t\treturn false\n"
         "\tfor node in scene_root.find_children(\"*\", \"NavigationRegion3D\", true, false):\n"
         "\t\tvar region: NavigationRegion3D = node as NavigationRegion3D\n"
         "\t\tif NavigationServer3D.region_get_use_async_iterations(region.get_rid()):\n"
         "\t\t\treturn false\n"
         "\t\tif region.get_navigation_map().is_valid() \\\n"
         "\t\t\t\tand NavigationServer3D.map_get_use_async_iterations(region.get_navigation_map()):\n"
         "\t\t\treturn false\n"
         "\treturn true\n"
         "\n"
         "static func _ensure_key(action: StringName, keycode: Key) -> void:\n")

R_USE_OLD = "##   godot --headless --path . -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \\\n"
R_USE_NEW = ("##   godot --headless --fixed-fps 60 --path . -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \\\n")
R_TS_OLD = "##   --time-scale X    sim speed multiplier (default 4.0)\n"
R_TS_NEW = ("##   --time-scale X    the physics step's multiplier (default 4.0: Godot scales\n"
            "##                     the step, so 4 simulates at 1/15 s where the game steps\n"
            "##                     at 1/60)\n")
R_ARGS_OLD = "## Args without `--` also work for compatibility with the TDD examples.\n"
R_ARGS_NEW = ("## Args without `--` also work for compatibility with the TDD examples.\n"
              "##\n"
              "## THE CLOCK (0.27.0, factory roadmap 239). `--fixed-fps 60` is an ENGINE\n"
              "## argument, before `--`: each frame is one physics step (the project's 60\n"
              "## ticks), computed as fast as the processor allows. Without it Godot paces the\n"
              "## run to `--time-scale` x real seconds -- measured on cold runs 9245 and 9247,\n"
              "## every evaluation simulated 3.91 to 3.97 times its wall time, so most of a\n"
              "## ten-minute job was waiting; cold run 9247's seed_9104 took 593 s that way and\n"
              "## 21 s under the fixed clock, its report identical in every field. The two\n"
              "## clocks read the same because the navigation map updates on this thread\n"
              "## (`LT_Const.synchronous_navigation`, in `_run`); the engine does not tell a\n"
              "## script which clock it runs on (`OS.get_cmdline_args` omits `--fixed-fps`),\n"
              "## so the caller chooses it and nothing here can check.\n")
R_CLOCK_OLD = ("\t# Headless evaluation shouldn't wait on real-world seconds. Raise the\n"
               "\t# per-frame physics step cap so high time scales don't fall behind.\n")
R_CLOCK_NEW = ("\t# THE STEP, NOT THE SPEED. `time_scale` multiplies the physics step (4 is\n"
               "\t# 1/15 s). This comment said \"headless evaluation shouldn't wait on\n"
               "\t# real-world seconds\"; measured, it did, and does unless the engine runs\n"
               "\t# under `--fixed-fps` (the header). The step cap lets a synchronised clock\n"
               "\t# catch up after a slow frame; under a fixed clock a frame is one step.\n")
R_RUN_OLD = ("\t\targs: Dictionary) -> void:\n"
             "\tif args.has(\"bake-nav\"):\n"
             "\t\tawait _bake_navigation(harness.get_parent())\n")
R_RUN_NEW = ("\t\targs: Dictionary) -> void:\n"
             "\t# THE MAP UPDATES ON THIS THREAD (0.27.0): `LT_Const.synchronous_navigation`,\n"
             "\t# before the bake, so the bake's own region update is synchronous too. Its\n"
             "\t# setters land at the next sync, so a physics frame passes before they are\n"
             "\t# read back: a dial confirmed, not assumed.\n"
             "\tvar regions: int = LT_Const.synchronous_navigation(harness.get_parent())\n"
             "\tawait physics_frame\n"
             "\tif LT_Const.navigation_is_synchronous(harness.get_parent()):\n"
             "\t\tprint(\"[LT] navigation: the map and %d region(s) update on this thread\" % regions)\n"
             "\telse:\n"
             "\t\tpush_warning(\"[LT] navigation still updates on worker threads: when an \"\n"
             "\t\t\t+ \"update lands is wall time, so this report may not repeat\")\n"
             "\tif args.has(\"bake-nav\"):\n"
             "\t\tawait _bake_navigation(harness.get_parent())\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LT / "VERSION").read_bytes().strip() == VERSION, (LT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.27.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.27.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LT_ROOT"):
        sys.exit("refusing: --draft is for an LT_ROOT copy, never the repo")
    test_text = _src("test_navigation_is_synchronous.gd.txt")
    assert "LT_Const.synchronous_navigation(" in test_text
    assert not (LT / TEST).exists(), "already applied"

    cp, c_eol, const = _read(CONST)
    assert "func synchronous_navigation" not in const, "already applied"
    const = _once(const, C_OLD, C_NEW, "LT_Const: the helpers before _ensure_key")
    rp, r_eol, runner = _read(RUNNER)
    runner = _once(runner, R_USE_OLD, R_USE_NEW, "the usage line")
    runner = _once(runner, R_TS_OLD, R_TS_NEW, "--time-scale's line")
    runner = _once(runner, R_ARGS_OLD, R_ARGS_NEW, "the header's last line")
    runner = _once(runner, R_CLOCK_OLD, R_CLOCK_NEW, "the clock comment")
    runner = _once(runner, R_RUN_OLD, R_RUN_NEW, "_run's head")

    # A staged project carries the addon and not the repository's CHANGELOG or VERSION: a draft
    # there is the code change alone, which is what an A/B on a staged level needs.
    staged = DRAFT and not (LT / "CHANGELOG.md").exists()
    if not staged:
        assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
        entry = _src("CHANGELOG_0.27.0.md")
        assert entry.startswith("## [0.27.0] - "), entry[:40]
        if not DRAFT:
            left = entry
            if PENDING:
                for key in RESULTS:
                    left = left.replace(key, "")
            assert "RESULT_" not in left, "the changelog still carries an unfilled result"
        cl = LT / "CHANGELOG.md"
        cl_raw = cl.read_bytes()
        cl_eol = _eol(cl_raw, "CHANGELOG.md")
        cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
        assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(cp, c_eol, const)
    _write(rp, r_eol, runner)
    (LT / TEST).write_bytes(test_text.encode("utf-8"))
    if not staged:
        head = "# Changelog\n\n"
        _write(cl, cl_eol, head + entry.rstrip("\n") + "\n\n" + cl_text[len(head):])
        (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.26.0 -> 0.27.0" + (" (DRAFT" + (", code only, staged project)" if staged else ")") if DRAFT else ""))


if __name__ == "__main__":
    main()
