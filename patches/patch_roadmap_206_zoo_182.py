"""Roadmap: item 206 NARROWED -- the getaway van is built (Zoo 1.82.0's
`step_van`) and not yet placed. Phase 1's figures go in, and what parking it
at the spawn touches, each reference re-read 2026-10-07.

    python patch_roadmap_206_zoo_182.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_van.py left it
(1,274,288 bytes, LF, as read 2026-10-07): 206's status line by its unique
prefix, directly above its heading; the last line of 206's WHAT THE FACTORY
DOES TODAY with the NEXT heading under it; and 206's "What it is" bullet.
Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_PREFIX = "*STATUS: OPEN 2026-10-07 -- the walker's design, not yet built: the getaway vehicle is a Chevrolet"
STATUS_NEW = ("*STATUS: NARROWED 2026-10-07 -- the van is built and not yet placed: Zoo 1.82.0's `step_van`, a "
              "P30-style step van in matte black gone chalky, builds PASS at an exact fit (2.600 x 6.800 x 3.050), "
              "4,860 tris against 5,500, five submissions, 0 coincident pairs at six sizes, and awaits the walker's "
              "verdict on its frames. Nothing parks it at the spawn yet: the extraction is still a seeded draw among "
              "the buildings that are not the spawn, and the score building itself on 43 of 136 multi-building "
              "candidate specs on disk and on 2 of cold run 9195's 3 candidates. Comps: "
              "`docs/reference/GETAWAY_VAN_COMPS.md`.*\n")

ANCHOR_TODAY = ("- The package carries three extraction anchors on cold run 9194's level (`lot:EXIT`, `lot:STREET`, "
                "`lot:STREET_25`), none marked as the mission's (item 204).\n"
                "\n"
                "**NEXT.**\n")
PHASE_1 = ("**PHASE 1 -- THE VAN, BUILT (Zoo 1.82.0, 2026-10-07).** `step_van` is a species of its own, laid out "
           "in pure Python (`zoo_keeper/core/van_forms.py`) and built by `recipes/step_van.py`. Its record is "
           "`patches/patch_zoo_step_van.py` with `patches/zoo_step_van/`.\n"
           "- **What it is.** A tall box behind a flat-nosed cab, a raked two-piece windshield, round headlamps "
           "in square bezels with amber lamps over them, black bumpers, tall mirrors on tube arms, amber clearance "
           "lamps, dual rear wheels on steel discs and rear doors. It carries no maker's mark and no lettering. The "
           "slot is exact (mirror heads, bumpers, clearance lamps), the collision is the slot's box, and the crew's "
           "door is on the kerb side (`ATT_side_door`).\n"
           "- **The finish is its history, on one material** (`paint_matte`, a new kind). Near-black low down, "
           "sun-chalked on the roof and upper panels, dust on the lower third, rust at the arches and the rocker, "
           "and one grey primer patch on the kerb side, per corner in `Wear` (`geometry.tint_wear_by`). It is "
           "deterministic: the same van in every level.\n"
           "- **Built at 2.6 x 6.8 x 3.05:** PASS, an exact fit, 4,860 tris (4,640 and 5,080 at the genome's "
           "corners) against 5,500, and five submissions (paint, painted parts, rubber, interior, glass). "
           "`tools/coplanar_probe.py` and the census read 0 coincident pairs at six sizes. Two defects were found "
           "on the way and fixed at their source: 10-12 coincident pairs a build, and the van standing 10.3 mm off "
           "the ground, because at 14 segments no tyre vertex points down (`van_forms.axle_height`; the fit test "
           "fails at all three sizes with it reverted).\n"
           "- **The frames are deterministic.** From `zoo/`, `blender --background --python "
           "tools/preview_specimen.py -- --species step_van --dims 2.6 6.8 3.05 --theme delco_1997 --azimuth A "
           "--eye 1.7 --dist 10 --render <png>` at A = -45 (front), 225 (kerb side) and 135 (rear). The preview's "
           "sun is on +X, the road side, so the kerb side and the rear stand in shade.\n"
           "- **Unproven:** the walker has not judged the frames, and nothing places the van.\n"
           "\n"
           "**NEXT.**\n")

OLD_WHAT = ("- **What it is -- decided:** a step van -- walk-in body and cab as one box, flat split windshield, "
            "round headlights in square bezels, walk-in side door -- matte black, sun-faded, rust at the arches "
            "and seams, grime on the lower third. One hero prop, the same truck in every level. The comps and "
            "what each tool owes them: `docs/reference/GETAWAY_VAN_COMPS.md`. Show the walker a frame before it "
            "rolls out.\n")
NEW_WHAT = ("- **What it is -- decided, and built** (Zoo 1.82.0, phase 1 above). The walker judges the frames "
            "before it rolls out. *As first filed:* \"a step van -- walk-in body and cab as one box, flat split "
            "windshield, round headlights in square bezels, walk-in side door -- matte black, sun-faded, rust at "
            "the arches and seams, grime on the lower third. One hero prop, the same truck in every level.\"\n"
            "- **What parking it touches** (each reference re-read 2026-10-07, nothing patched yet):\n"
            "  - **Lot.** The cover planners keep 3 m off every mission marker (`site_cover.MARKER_CLEARANCE`), "
            "so the van needs a placement of its own. It runs after `site_spawns.clear_crew_spawn` (`lot.py:3272`) "
            "and before `site_spawns.place_enemies` (`lot.py:3276`), at the curb, with the spawn on the sidewalk "
            "by its kerb-side door: a crew member spawned inside its collision box fails Laser Tag's "
            "`SPAWN_IN_COLLISION` (`LT_MapEvalHarness.gd:340`). It wants a `COVER_MATERIALS` row "
            "(`lot.py:1615`).\n"
            "  - **Lot's audit.** `S_BACKTRACK` (`site_audit.py:169`, pinned by `tests/test_lot.py:775`) fires "
            "when the extraction stands within `BACKTRACK_NEAR` of the spawn and within `BACKTRACK_ANGLE` of its "
            "bearing from the objective. With the van at the spawn that is 0 m and 0 degrees on every level, so "
            "the rule must recognise the getaway van. `S_RESPONDER_CAMP` (`site_audit.py:198`) checks the crew "
            "spawn and the extraction separately, so one responder spawn near the van would report twice.\n"
            "  - **Level Factory.** `site_variation.site_placements` (`packages/pipeline/site_variation.py`) "
            "draws the extraction last, among the buildings that are not the spawn. Under the walker's rule the "
            "extraction is the spawn, and that draw is still made, so no other number a seed gives moves (the "
            "pattern its objective and front-door changes already follow).\n"
            "  - **Laser Tag.** When the crew's bot is stuck, `_update_stuck` (`LT_BotPlayerController.gd:394`) "
            "advances it to the next route point, `mini(_route_index + 1, size - 1)`. That gives up the point it "
            "was stuck on rather than reaching it. On a route that ends where it starts, the last point is the "
            "first, so read what completion means there before a there-and-back route is trusted.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1274288, "PIPELINE_ROADMAP.md is %d bytes, read at 1,274,288" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for name, anchor in (("today", ANCHOR_TODAY), ("what", OLD_WHAT)):
        assert text.count(anchor) == 1, "%s found %d times" % (name, text.count(anchor))
    text = _replace_status(text, STATUS_PREFIX, STATUS_NEW, "**206. ")
    text = text.replace(ANCHOR_TODAY, ANCHOR_TODAY[:ANCHOR_TODAY.index("**NEXT.**")] + PHASE_1)
    text = text.replace(OLD_WHAT, NEW_WHAT)
    RM.write_bytes(text.encode("utf-8"))
    print("206 NARROWED: phase 1 in; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
