"""The factory's render probes shoot the scene a walk preview actually plays, and a frame with nothing in it fails.

FOUND 2026-10-26 (the factory's docs/findings/walk_2026-10-26_panel/, L4). The walker called the supermarket "far
too dark"; `tools/light_check.py` on the same preview passed all 29 stations -- every one at mean 76.0, p50 76, and
every PNG one flat value, luma 76 = Godot's default clear colour 0.3. Nothing had rendered.

`light_census.default_scene`, which `look_shots`, `light_check` and `light_breakdown` use, picks "the single
*_walk.tscn". A Level Factory walk PREVIEW's level is `walk.tscn` and its player rig is `player_walk.tscn`, so the
rule picked the rig: a camera over an empty world. `mesh_light_census` met exactly this on 2026-08-23 and was fixed
alone (the project's `run/main_scene` first); the rule stayed in `light_census` and `dressing_in_nav`.

  1. `light_census.default_scene` is `mesh_light_census`'s: the project's run/main_scene, else the single
     *_walk.tscn. `dressing_in_nav` imports it instead of keeping a copy.
  2. `light_check.judge` FAILS a frame whose p05 equals its p95 -- one flat value is not a lit room and not a dark
     one, it is nothing rendered -- so a probe that shoots the wrong scene cannot pass a level again.

Anchored: each target asserted once; nothing written on a miss. Run from the factory root:

    python patches/patch_root_scene_choice.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def edit(rel, edits):
    p = ROOT / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s: anchor found %d times: %r; nothing written" % (rel, t.count(old), old[:70]))
        t = t.replace(old, new)
    return p, (t.replace("\n", "\r\n") if crlf else t)


GOOD = '''def default_scene(project_dir):
    """The project's own run/main_scene, else the single *_walk.tscn.

    The main scene comes FIRST: the *_walk.tscn rule picks `player_walk.tscn` -- the player rig, no level -- in a
    Level Factory walk preview, whose level is `walk.tscn`. `mesh_light_census` measured an honest, useless zero
    that way on 2026-08-23, and on 2026-10-26 `light_check` passed 29 frames of Godot's clear colour (the
    factory's docs/findings/walk_2026-10-26_panel/, L4). The scene the project runs is the scene a person walks.
    """
    pg = os.path.join(project_dir, "project.godot")
    if os.path.isfile(pg):
        with open(pg, encoding="utf-8", errors="replace") as f:
            m = re.search(r'run/main_scene="res://([^"]+)"', f.read())
        if m and os.path.isfile(os.path.join(project_dir, m.group(1))):
            return m.group(1)
    walks = sorted(f for f in os.listdir(project_dir)
                   if f.endswith("_walk.tscn"))
    if len(walks) != 1:
        raise ProbeFailed(
            "no run/main_scene in project.godot, and expected exactly one "
            "*_walk.tscn in " + project_dir + ", found " +
            str(len(walks)) + ": " + str(walks) + ". Pass --scene.")
    return walks[0]
'''

plans = []
lc = (ROOT / "tools" / "light_census.py").read_text(encoding="utf-8")
plans.append(edit("tools/light_census.py", [
    ('''def default_scene(project_dir):
    """The single *_walk.tscn, the way lux_inject.py picks one."""
    walks = sorted(f for f in os.listdir(project_dir)
                   if f.endswith("_walk.tscn"))
    if len(walks) != 1:
        raise ProbeFailed(
            "expected exactly one *_walk.tscn in " + project_dir + ", found " +
            str(len(walks)) + ": " + str(walks) + ". Pass --scene.")
    return walks[0]
''', GOOD),
] + ([] if "\nimport re\n" in lc else [("\nimport os\n", "\nimport os\nimport re\n")])))

plans.append(edit("tools/dressing_in_nav.py", [
    ('''def default_scene(project_dir):
    """The single *_walk.tscn, the way light_census picks one."""
    walks = sorted(f for f in os.listdir(project_dir)
                   if f.endswith("_walk.tscn"))
    if len(walks) != 1:
        raise ProbeFailed(
            "expected exactly one *_walk.tscn in " + project_dir + ", found "
            + str(len(walks)) + ": " + str(walks) + ". Pass --scene.")
    return walks[0]
''', '''from light_census import default_scene  # noqa: E402,F401  -- the run/main_scene first (2026-10-26)
'''),
]))

plans.append(edit("tools/light_check.py", [
    ('''    """(verdict, rule) for one station's frame."""
    p50, near, mean = shot["p50"], shot["near_clipped_pct"], shot["mean"]
''', '''    """(verdict, rule) for one station's frame."""
    p50, near, mean = shot["p50"], shot["near_clipped_pct"], shot["mean"]
    # NOTHING RENDERED (2026-10-26): one flat value from p05 to p95 is not a lit room or a dark one. Twenty-nine
    # frames of Godot's clear colour (luma 76) passed every rule below when the probe shot the player rig's scene
    # instead of the level (docs/findings/walk_2026-10-26_panel/, L4).
    if shot.get("p05") is not None and shot.get("p95") is not None and shot["p05"] == shot["p95"]:
        return "FAIL", "NO FRAME: one flat value, p05 = p95 = %d -- nothing rendered (the wrong scene?)" % shot["p95"]
'''),
]))

for p, text in plans:
    p.write_bytes(text.encode("utf-8"))
    print("wrote", p.relative_to(ROOT))
