"""Write patches/patch_roadmap_guides_2026_10_21.py: items 285-291, filed from the two documents the walker shared on
2026-10-21 and their chase reports (docs/findings/guides_2026-10-21/), appended after the last item. Copied from
make_roadmap_283.py's append half. Refuses if the patch name is taken.

    python make_roadmap_guides_1021.py <item 288's text file>
"""
import pathlib
import re
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_guides_2026_10_21.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t
heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", t)]
assert heads[-1] == 284 == max(heads), heads[-3:]
ITEM_288 = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").strip("\n")
assert ITEM_288.startswith("*STATUS: ") and "\n\n**288. " in ITEM_288, ITEM_288[:120]

TDD = "`docs/proposals/Blender_Retopology_Planner_Executor_TDD_v3.0_Godot47_Runtime_MultiMesh.md`"
GUIDE = "`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`"
ITEMS = (
    "*STATUS: OPEN 2026-10-21 -- measured chasing the walker's retopology TDD "
    "(`docs/findings/guides_2026-10-21/retopo_tdd.md`); not started.*\n\n"
    "**285. Back-face culling is off on every surface the factory ships.** The walker, 2026-10-21, sharing " + TDD +
    ": \"this should be used for zoo and deli counter big time\". Its retopology core finds nothing to reduce here "
    "(Zoo builds from primitives, a 2 m wall module 12 triangles; Deli Counter's boolean-cut walls never draw); its "
    "runtime half's first gap is this one. Measured on cold run 9370's package: 410 of 410 materials in its 134 GLBs "
    "are `doubleSided: true`, 376 of them opaque (read again before filing); all 1,067 materials embedded in its "
    "1,066 merged and extracted meshes carry `cull_mode = 2`, CULL_DISABLED (the pass's own decoder, "
    "`retopo_tdd/rsrc_read.py`). Zoo sets `use_backface_culling` only to False, on cards "
    "(`zoo_keeper/bpylayer/materials.py:831`, `:849`); Deli Counter's greybox material never sets it; Level "
    "Factory's import and merges copy what arrives. Of the 1,104 opaque visual primitives a scene uses, 1,039 are "
    "closed shells wound outward with no flipped edge -- culling hides nothing on them -- and 65 are open, almost all "
    "flat art faces (pole flyers; the payphone's, ATM's and video poker's faces; three sign-box faces; two roof "
    "props). Never priced. The saving is GPU-side, and this machine's RTX 2060 is CPU-bound at all 14 of cold run "
    "9369's stations, so a price here can show only that nothing moved. **What would close it:** Zoo writing "
    "`doubleSided: false` on a GLB material whenever every surface using it is a closed outward shell -- derived per "
    "material per built file, not chosen, so an open face keeps both sides -- and Deli Counter's greybox likewise; "
    "Level Factory's merge read to see whether it keys a surface by material identity or by name, so that a culled "
    "and an unculled material of one name never share a surface; an A/B in one session against a no-change control "
    "run twice, draws unmoved and frames diffed for any face that vanished; the low-end machine's price owed.\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured chasing the walker's retopology TDD; not started.*\n\n"
    "**286. Nothing decides which meshes cast shadows.** Measured on cold run 9370's package: only Lot's seven "
    "overhead-wire meshes, its ten drain meshes and the backdrop ground set `cast_shadow` off (35 lines over 22 "
    "scenes); everything else casts -- 1,055 merged building meshes, all 29 MultiMeshes including the four site-wide "
    "dressing batches, every GLB-instanced node -- and 12 lights ship with live shadows. The factory priced those "
    "shadow maps at 300.1 draws a heading with 12 shadowed lights and 59.2 with 4 (roadmap 243, cold run 9262), and "
    "draws are what frame time follows here. The TDD's section 32.5 asks for a shadow class per asset: required, "
    "optional, none. **What would close it:** `level_factory/tools/draw_attrib.gd` splitting each heading's draws "
    "into the colour pass and the local-light shadow pass, the shadow casters grouped by size and by Zoo category; one "
    "A/B turning casting off on the class with the most shadow submissions and the least shadow role (the dressing and "
    "small clutter), against the package as shipped twice in one session, frames at the lit stations. Which classes "
    "may stop casting is the walker's call, and never a shadow that matters for cover or mood.\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured chasing the walker's retopology TDD; not started.*\n\n"
    "**287. A package's manifest names the factory's release pins, not the tools that built it.** Cold run 9370's "
    "`LF_MANIFEST.json` `tools` block (`tools_source: factory.manifest.json`) reads Deli Counter 0.241.0, Zoo "
    "1.117.0 and Level Factory 0.227.0; the run's own `before.json` `versions` reads 0.248.0, 1.120.1 and 0.228.0 "
    "(both read again before filing). A recipient -- the collaborator making levels on their own machines -- cannot "
    "read from a package which tool versions made it. **What would close it:** the manifest recording each tool's "
    "VERSION and commit as read at build time from the repositories the workspace named, the release pins kept beside "
    "them under their own name, and a package whose two disagree saying so.\n\n"
    + ITEM_288 + "\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured chasing the lived-in levels guide "
    "(`docs/findings/guides_2026-10-21/lived_in.md`); not started.*\n\n"
    "**289. Level Factory's sightline advisory crosses at 1.2 m; the contract crosses at 1.3.** "
    "`level_factory/packages/validation/sightlines.py` sights from `EYE_HEIGHT = 1.4` -- \"from the Laser Tag "
    "scripts\", the bot's probe as it once was -- at a 1.0 m chest, so its `MIN_COVER_HEIGHT` is 1.2, and "
    "`packages/validation/tactical.py` advises from it through the Laser Tag adapter. Laser Tag sights from "
    "`player_eye_height_m` and `enemy_eye_height_m`, 1.6 both (`LT_TestScenario.gd:38`, `:58`), Lot carries 1.6 and "
    "1.3 (`lot/site_cover.py:63`, `:70`), and the agent contract's lines cross at `cover_break_height_m`, 1.3. The "
    "contract's own note is stale the other way: it says \"Lot still carries 1.2\" (`agent_contract.json` "
    "`sightlines`), and Lot does not. Two instruments for one question: the advisory counts a 1.2 to 1.3 m solid as "
    "breaking a line both sides see over. **What would close it:** the advisory's heights read from the contract -- "
    "the crew's and the enemy's sight heights and the aim -- with a test that fails on 1.4; the contract's note "
    "naming what still carries the old crossing, or nothing.\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured chasing the lived-in levels guide; not started.*\n\n"
    "**290. Laser Tag counts a shot into a teammate as a hit, and nothing a teammate stood in front of.** "
    "`LT_Shooter.gd` types a crew shot that meets a teammate `FRIENDLY_HIT` and does no damage; "
    "`LT_MetricsCollector.gd`'s match counts it in `shots_hit` through its default branch (`_: "
    "current[\"shots_hit\"] += 1`, read again before filing), so a crew's hit rate includes its own players' backs. "
    "`LT_LineOfSightTester.has_line_of_sight` returns `collider == target`, so a teammate in the line silently denies "
    "the shot and nothing counts it; nothing counts the enemies with a line on one crew member at once, either. The "
    "guide filed the same day (" + GUIDE + ", sections 4 and 7) names teammates obstructing shots and simultaneous "
    "attackers as what a four-player fight is lost to. **What would close it:** `FRIENDLY_HIT` counted on its own and "
    "never as a hit; the line-of-sight checks a teammate denied counted beside it; per crew bot per second, the "
    "enemies with a line to it and the eight bearings they hold, reported and never scored, because spawns are "
    "provisional -- one bounded change, the walker's rule for Laser Tag.\n\n"
    "*STATUS: OPEN 2026-10-21 -- measured chasing the lived-in levels guide; not started.*\n\n"
    "**291. A second route can end under the shooter who holds the first.** `combat_audit._disjoint_paths2` and "
    "`tactical._count_independent_routes` find node-disjoint routes from the entries to an objective and know nothing "
    "of firing lines: two routes whose last doors one standing position sees are one option, which the guide (section "
    "6) calls the alternate that fails -- \"two aisles that converge immediately under the same shooter\". **What "
    "would close it:** for each objective and fortifiable room, whether one standing position in it or in its holdout "
    "neighbour sees the final doorway of both disjoint routes, asked with `sightlines.py`'s occluders; the rooms where "
    "one shooter holds both, counted and named, and read beside roadmap 245's static four-player congestion check.\n")

PATCH = '''"""Items 285-291, filed from the two documents the walker shared on 2026-10-21 -- the retopology TDD (285-287) and
the lived-in levels guide (288-291) -- and their chase reports (`docs/findings/guides_2026-10-21/`). Copied from
`patch_roadmap_283_storey_shelter.py`'s append half: appends the items after the last item (asserted to be 284). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_guides_2026_10_21.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**285. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 284 or heads[-1] != 284:
        raise SystemExit("REFUSED: the last item is not 284; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    text = text + "\\n" + ITEMS
    for n in range(285, 292):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("items 285-291 appended; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (ITEMS,)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
