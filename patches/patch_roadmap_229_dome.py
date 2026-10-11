"""Roadmap 229: the dome (Zoo 1.98.0/1.98.1, Lux 0.75.0, Deli Counter 0.208.0, cold run 9239), and
two new items 9239 surfaced: 232, `add_hemisphere` keeps the lower half (four species' caps hang
inside their bodies); 233, a fixture's same-material parts are separate meshes (a pendant pays a
draw for its cord). Appends one paragraph to 229's body and the two items at the end of the
roadmap; 229's status is not touched (its species step is in flight until 9241 sees the fix). Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_229_dome.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD_229 = "\n\n**229. "
TAIL_229 = ("The fixture is still a troffer: a home's dome or pendant is the species step. Not seen in a "
            "level yet; a residence-heavy brief (apartment_walkup, twin) would show it.")
ADD_229 = """

**THE DOME, 2026-10-11** (Zoo 1.98.0 `dome_fixture`, Lux 0.75.0 `dome` rig, Deli Counter 0.208.0; `docs/cold_runs/cold_9239/NOTES.md`). The species step's first fixture: a home's room -- by its building or by its own words, `_home_room` -- writes `dome` anchors where it wrote `fluorescent`, the same rows, ids, drops and positions; Zoo hangs a flush-mount dome on each (a canopy on the ceiling, a frosted bowl, a finial; mount `hang`); Lux lights it warm from 0.17 m under the anchor, below the deepest bowl Zoo builds, its range derived so the pool reaches its 7 m bay's corner (`tools/dome_lamp_selftest.gd`, 10 checks). The library rebuilt: 67 home rows carrying 213 lamps in 18 buildings moved from `fluorescent` to `dome` one for one, every other type unchanged (`docs/findings/fixture_rows/type_census.py`, 0.207.1's 1,071 / 4,102 fluorescent before, 1,004 / 3,889 after). Cold run 9239 (9233's lot, its one home room the deli's apartment hideout, 0 interventions): the domes travelled every stage, the bake read the hideout's bad troffer tube gone (213 steady, 29 failing), and the room read warm where 9238's was a cool dim grey -- **but the fixture was wrong twice.** Its glass hung UP into the ceiling (measured in the shipped GLB: from the canopy's underside to 5.4 cm above the ceiling plane), because `geometry.add_hemisphere` keeps the lower half though its docstring says upper (printed in Blender: z -1 .. 0) and 1.98.0 mirrored it; and a dome was three meshes where a troffer is two (the canopy and finial, one material, two objects, in a fixtures GLB exported unmerged), +6 draws at 24 of 53 headings at no frame cost. Zoo 1.98.1 lays the bowl at `rim - |z|` and closes it inside the canopy, and makes the canopy and finial one mesh (built in Blender: the glass under the canopy, faces down; census 310 tris, 0 pairs). Cold run 9241 is the fix's reading. Still owed: a residence-heavy lot for the look, and the pendant and the other species the guide names (strip light, sconce, high-bay, exit sign)."""

ITEMS = """

*STATUS: OPEN 2026-10-11 -- measured, not started. `geometry.add_hemisphere` (Zoo) documents an "upper hemisphere shell (open bottom)" and keeps the LOWER half: printed in Blender 5.1.1, a unit hemisphere at the origin returns 101 vertices at z -1.0000 .. 0.0000 with faces pointing down and out (mean face normal z -0.64) -- its bisect keeps the side opposite its plane normal. Its four callers besides the dome all place it as a cap ON TOP -- `bollard` at the post's top, `exhaust_fan` on its drum, `soda_cup` as its lid, `helmet` as its shell -- so each builds its cap hanging inside its own body, hidden. Found by the dome (roadmap 229, cold run 9239), whose 1.98.1 no longer depends on the helper's side. Owner: Zoo. Fix the helper to keep what it says (or say what it keeps), then each of the four needs its census and a frame: the caps will appear, which is a look change, and a cap that rises may meet another part's plane.*

**232. `add_hemisphere` keeps the lower half: four species' caps hang inside their bodies.** The bollard is flat-topped where its genome meant a domed cap, the exhaust fan's dome is inside its drum, the soda cup's lid inside the cup, and the helmet's shell -- the whole helmet -- is a bowl below its own origin. None of it has shown as a defect, because a cap hidden inside a solid draws nothing wrong; it draws nothing. The measurement and the dome's way round it are in `docs/cold_runs/cold_9239/` (`hemisphere_probe.py`, run in Blender). The fix is one line in the helper -- keep the upper half -- and four censuses and four frames to see what each species looks like with the cap it was written to have.

*STATUS: OPEN 2026-10-11 -- measured, not started. A building's fixtures ship as one GLB per scope with every fixture's parts as separate meshes (`build.build_fixtures` exports with `merge_parts=False`, on purpose: the GLB is a layer of many fixtures, and merging across them would cost culling), so a fixture whose parts share a material pays a draw per part where one would do. Read off cold run 9239's deli fixtures GLB: a pendant is a bulb (lens) and a socket and a cord (one metal) -- 46 metal meshes for 23 pendants where 23 would carry them -- and the dome was the same until Zoo 1.98.1 folded its finial into its canopy (+6 draws at 24 of 53 headings for six domes, measured). Owner: Zoo. The lever: join a placement's parts by material inside `build_fixtures`, per fixture and never across fixtures (the module rule, `merge.py`'s), then price it the cover merge's way.*

**233. A fixture's same-material parts are separate meshes: a pendant pays a draw for its cord.** Merging per placement keeps every fixture its own culling unit while removing the parts' extra submissions: in the deli alone, 23 pendants' cords and sockets would go from 46 meshes to 23. Every fixture species with two parts in one material is in scope (the streetlight's pole and head, the wall pack's arm and body, the sign box's cabinet and arms); the troffer, two parts in two materials, is not. What it must keep: the `LuxEmit_*` markers beside their own hardware (empties, outside the mesh pool), the lens materials' names (Lux's emissive binder keys on `M_*_Lens`), and each part's shading (no welding, as `merge.py` keeps it)."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE DOME, 2026-10-11" not in text and "\n**232. " not in text, "already applied"
    h = text.find(HEAD_229)
    assert h > 0 and text.count(HEAD_229) == 1, "229's heading not found once"
    nxt = text.find("\n\n*STATUS:", h + 10)
    body = text[h:nxt]
    assert body.endswith(TAIL_229), ("229's body does not end where this patch read it", body[-120:])
    text = text[:nxt] + ADD_229 + text[nxt:]
    assert text.endswith("\n")
    text = text.rstrip("\n") + ITEMS + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 229 paragraph appended, items 232 and 233 opened; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
