"""Level Factory 0.132.0: a building faces the street with its front door.

Step 2 of `docs/proposals/LAND_USE_DESIGN.md`, agreed by the walker
2026-10-03 ("agreed, lets move"). Every building's yaw was drawn at random
from 0/90/180/270; it is now the yaw that faces its front door -- read off
Deli Counter's gameplay file (`packages/pipeline/front_door.py`) -- to the
through road, which the road grammar always runs south of the row. A
building with no ground door keeps the drawn yaw, and the draw is still
made, so every other number a seed produces (the nudges, the roles) is
unchanged.

New files from `lf_front_doors/`: `packages/pipeline/front_door.py`,
`tests/unit/test_front_door.py`. Anchored edits (every anchor once; refuses
on a miss): `site_variation.site_placements` takes `fronts`; both call
sites in `apps/cli/commands/__init__.py` pass them and record each
building's front on its spec record. CHANGELOG and VERSION from
`lf_front_doors/CHANGELOG_0.132.0.md`.

    python patch_lf_front_doors.py
    LF_ROOT=<copy> python patch_lf_front_doors.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_front_doors"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.131.0", v
    assert not (LF / "packages" / "pipeline" / "front_door.py").exists(), "already applied"
    (LF / "packages" / "pipeline" / "front_door.py").write_bytes((SRC / "front_door.py").read_bytes())
    (LF / "tests" / "unit" / "test_front_door.py").write_bytes((SRC / "test_front_door.py").read_bytes())
    _edit(LF / "packages" / "pipeline" / "site_variation.py", [
        ("def site_placements(seed: int, count: int, *, spacing: int = 45,\n"
         "                    footprints=None, shape=None) -> dict:\n",
         "def site_placements(seed: int, count: int, *, spacing: int = 45,\n"
         "                    footprints=None, shape=None, fronts=None) -> dict:\n"),
        ("        rot = _YAW[next(rng) % len(_YAW)]\n",
         "        rot = _YAW[next(rng) % len(_YAW)]\n"
         "        # THE FRONT DOOR FACES THE STREET (0.132.0): `fronts[i]` is the yaw\n"
         "        # that turns building i's front door to the through road\n"
         "        # (`front_door.facing_yaw`), None where it has no ground door. The\n"
         "        # draw above is still made, so no other number this seed gives moves.\n"
         "        if fronts is not None and i < len(fronts) and fronts[i] is not None:\n"
         "            rot = int(fronts[i])\n"),
    ])
    _edit(LF / "apps" / "cli" / "commands" / "__init__.py", [
        ("        footprints = building_library.footprints_for(lot, shell_footprint)\n"
         "        placed = site_placements(seed, len(lot), footprints=footprints,\n"
         "                                 shape=model.site_shape)\n",
         "        footprints = building_library.footprints_for(lot, shell_footprint)\n"
         "        # each building's front door, read off its own gameplay (0.132.0)\n"
         "        from packages.pipeline import front_door as _fd\n"
         "        front_of = [_fd.front_wall_of(e[\"gameplay\"]) for e in lot]\n"
         "        placed = site_placements(seed, len(lot), footprints=footprints,\n"
         "                                 shape=model.site_shape,\n"
         "                                 fronts=[_fd.facing_yaw(w) for w, _r in front_of])\n"),
        ("            {\"id\": f\"b{i}\", **_source(e), \"gameplay\": e[\"gameplay\"],\n"
         "             \"archetype\": e[\"id\"],\n"
         "             \"at\": p[\"at\"], \"rot\": p[\"rot\"]}\n"
         "            for i, (e, p) in enumerate(zip(lot, placed[\"buildings\"]))\n",
         "            {\"id\": f\"b{i}\", **_source(e), \"gameplay\": e[\"gameplay\"],\n"
         "             \"archetype\": e[\"id\"],\n"
         "             \"at\": p[\"at\"], \"rot\": p[\"rot\"],\n"
         "             \"front\": {\"wall\": fw[0], \"reason\": fw[1]}}\n"
         "            for i, (e, p, fw) in enumerate(zip(lot, placed[\"buildings\"], front_of))\n"),
        ("        placed = site_placements(seed, count, spacing=spacing)\n",
         "        from packages.pipeline import front_door as _fd\n"
         "        shell_front = _fd.front_wall_of(gameplay)\n"
         "        placed = site_placements(seed, count, spacing=spacing,\n"
         "                                 fronts=[_fd.facing_yaw(shell_front[0])] * count)\n"),
    ])
    entry = (SRC / "CHANGELOG_0.132.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.132.0]" not in d and d.startswith(b"## [0.131.0]")
    cl.write_bytes(entry.encode("utf-8") + d)
    (LF / "VERSION").write_bytes(b"0.132.0")
    print("0.131.0 -> 0.132.0")


if __name__ == "__main__":
    main()
