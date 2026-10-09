"""Roadmap 217 and 218, appended after item 216.

217: levels read by day and by night -- the light instruments, Lux 0.71.0's
dusk-to-dawn lamps proven in cold run 9214, and the walker's lighting spec set
against the code, with what that comparison measured.
218: the export's import pass checked nothing -- found by cold run 9214,
fixed in Level Factory 0.163.1.

Appends after the file's last line, which must be item 216's and appear once.
Refuses while a result placeholder is left in the text. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

LAST = ("- **Which species first.** `red_maple`, the default form, unless the walker "
        "says otherwise.\n")

ITEMS = r"""
*STATUS: NARROWED 2026-10-09 -- the instruments exist, and the street lamps are dark by day. Root tools `light_breakdown.py`, `light_check.py` and `lux_rebake.py` measure a level by source, by room and street against named floors, and at any slot by an exact re-bake. Lux 0.71.0 darkens poles and wall packs under the four day presets, proven in cold run 9214 (0 interventions): a hidden lamp is not baked (wall pack 002's wall 32.5, against 48.0 with the lamps forced on), and the lamps move the check's 23 stations by 0.2 or less. The walker's lighting spec, set against the code, found three gaps: the bake holds no sky, fluorescents scale with the slot, and Heavy Rain's shadowless sun lights rooms through their roofs, which is why 12 of 16 interior stations outshine its street (objective 67.8 to 39.9 with the sun off; the fluorescent boost at 1.0 moves rooms 0 to 11.8). The same level as a clear afternoon has 2. That shadow was refused on price in Lux 0.38.0; on it, the rooms fall 5.6 to 31.6 and 12 WARNs become 7, and the price predates the light bake and the merges. The sky in the bake lifts a clear afternoon's street +15.1 and +21.4 at no run-time cost. Open: the walker's calls on Heavy Rain's sun, the sky in the bake, and where the night boost lives; morning and noon presets.*

**217. Levels read by day and by night.** The walker, 2026-10-09:
- "build that light breakdown instrument";
- "I want this tool or a tool that can make sure levels look good in both interiors and exteriors for both day and night lighting";
- "a good call out is that street lamps aren't usually on during the day";
- and, with a lighting spec: "this could help Lux and you?"

Item 198 found the dark rooms at night. This item is the standing check, and what it found by day.

**THE INSTRUMENTS** (factory root, `tools/`).
- **`light_breakdown.py`.** look_shots with one source switched off at a time (`--switch-off`: lightmap, live, sun, ambient, probes, emission, sky, fog), with combinations (`--also`) and a fills-on/fills-off re-bake (`--fills`). *Its drops are luma after the grade, not shares of the light* (corrected in `docs/findings/light_breakdown/README.md`).
- **`light_check.py`.** One station a room (the night census's derivation) plus the mission's exterior cameras, each held to a named floor:
  - a ROW room p50 >= 10, a MOODY room 5 (provisional), a den of sin exempt;
  - the street p50 > 1 with near-clip <= 5%;
  - a facade's p95 >= 10;
  - by day, a room brighter than the street warns.
  - A slot other than the level's own is re-baked first.
- **`lux_rebake.py`.** Level Factory's own `bake()` on a copy, under another preset (`--preset`), any preset field (`--set`), no fills (`--no-fills`), or the bake's environment on (`--bake-environment scene`). A re-bake with no change reproduced cold run 9213's frames to 0.0 at every camera.

**LUX 0.71.0: THE DUSK-TO-DAWN LAMPS** (`patches/patch_lux_dusk_to_dawn.py`).
- **The switch.** `LuxPreset.street_lamps_lit` is false on the four day presets: Delco Summer Afternoon, Delco Arcade, SoF PC2000 and Heavy Rain. The `streetlight` and `wall_pack` rows set `LuxLightRig.dusk_to_dawn`, and the rig hides and darkens its lens.
- **Proven in cold run 9214,** bank_block_001 at afternoon with rain (`docs/cold_runs/cold_9214/NOTES.md`, `street_lamps_by_day.png`):
  - **A hidden lamp is not baked.** Wall pack 002's wall reads 32.5, its sidewalk 62.3 and its lens 28.1. With the lamps forced on by a re-bake, the way every day level shipped before, they read 48.0, 84.2 and 60.2.
  - **At the light check's 23 stations the lamps move nothing,** 0.2 or less. A daylit street hides a lamp, as the spec says.
- **What stays lit by day is a call the walker can move:** canopies, signs, store glass, the payphone, every room.
- **Every wall pack is outside, over an exterior door:** 389 of 389, all derived (`docs/findings/lighting_spec_vs_lux/wall_pack_census.py`). So the spec's warning, that a day switch must spare lamps in shade or indoors, does not bite.

**WHAT THE CHECK FOUND.**
- **Cold run 9213, club_block_014 at midnight:** the airport terminal's check-in hall fails (p50 8), and the north facade is black. Re-baked to afternoon, everything passes.
- **Cold run 9214, bank_block_001, Heavy Rain as shipped:** 10 PASS, 12 WARN. 12 of 16 interior stations read brighter than the street's median 47.5 (rooms 36.6 to 83.8). Re-baked at night: the bank's grand lobby and the casino's gaming floor fail (p50 9 each), and the north facade warns (p95 3). Re-baked under Blue Hour, the evening slot: the grand lobby (p50 3), the stone vault (p50 2), and the extraction, where players leave at the van, "collapsed to black" (p50 1).

**THE LIGHTING SPEC SET AGAINST THE CODE** (`docs/reference/Godot_4_7_Natural_and_Artificial_Lighting_Spec.md`; `docs/findings/lighting_spec_vs_lux/`). Its model is illuminance = sun + sky + bounce + lamps, added before display mapping, and a lamp's output is fixed unless a dimmer, sensor, schedule or recorded override changes it.
- **Agrees:** a dusk-to-dawn sensor is a legitimate schedule; a baked light does not follow the sun, and we bake per slot; on Compatibility the tools are lightmaps, probes and fills; fixtures use attenuation 2.
- **Gap 1: the bake holds no sky.** `light_bake.py:113` sets `environment_mode = 0`, which arrived with Level Factory 0.131.0 and no recorded reason, and a lightmapped surface takes no ambient at run time.
  - Measured by re-baking 9214's level with the scene's environment, slot by slot (`docs/findings/lighting_spec_vs_lux/`):
    - **A clear afternoon** (the level re-baked under Delco Summer Afternoon): the street cameras +15.1 and +21.4, the facades +2.7 to +15.9, the rooms -0.1 to +1.2, and 2 WARNs to 0. Shade reads as daylight instead of near black (`sky_in_the_bake_clear_afternoon.png`).
    - **Heavy Rain:** +0.3 to +2.3 outside.
    - **Blue Hour:** +0.5 to +3.7 outside.
    - **Delco Night:** two outer facades +3.3 and +4.4, the rest 0.2 or less.
    - **Every room in every slot** moved 1.2 or less: a sealed room takes no sky.
    - The bake time is unchanged (81 to 96 s either way). At run time it costs nothing.
- **Gap 2: fluorescents scale with the slot.** `fluorescent_energy_scale` is 1.0 at Delco Summer Afternoon and Delco Arcade, 1.7 at SoF PC2000, 3.7 at Blue Hour, 4.3 in Heavy Rain, 5.0 at Mission Goes Hot, 5.7 at the Gas Station, and 6.0 at the three night presets.
  - It reaches only rigs that `scales_with_preset`: fluorescent rows, and those marked `preset_scaled`. Bulbs are exempt by the walker's call of 2026-09-28.
  - Street lamps, wall packs and the payphone hood do not scale, so the balance between a room's tubes and the street shifts sixfold from afternoon to night.
  - The spec calls brightening lamps as the sun dims a "don't". Compatibility has no auto-exposure, and the scale stands in for one.
- **Gap 3: Heavy Rain's sun casts no shadow, and lights rooms through their roofs.** It is the only preset with the sun on and `sun_shadows = false`. At 9214's interior cameras (`light_breakdown.py`):
  - switching the sun off takes the objective room from 67.8 to 39.9, and a drywall room from 57.5 to 35.5;
  - the fluorescent boost is not the cause: re-baked at 1.0 for 4.3, the rooms move 0 to 11.8, and all 12 still warn;
  - the same level re-baked as a clear afternoon, whose sun casts shadows, warns on 2 rooms (mezzanine 74.3 and upper ring 67.9, over a street of 64.9);
  - **outside, the fog carries Heavy Rain's day:** fog off takes the overview from 95.2 to 32.6.
  - **Re-baked with the sun's shadow on,** the rooms fall 5.6 to 31.6 and 12 WARNs become 7. The sun then moves the rooms by 0.0, and they read by their own fixtures (`heavy_rain_sun_shadow_rooms.png`).
  - **That shadow was a recorded trade.** Lux 0.38.0 (`resources/lux_preset.gd`) refused it on price: +3.2 to +8.1 ms at the orthogonal 60 m setting on cold run 9054's walk, against a ~2 ms budget, "the shadow PASS re-drawing the site".
    - It named the rooms' cost, and an unpriced free lever: a cull-mask split, the sun lighting exterior layers only.
    - Both predate the light bake (-12 % frame), the Empties' merge (-686 draws) and the cover merge (-1.86 ms). Neither has been re-priced.
  - *Not established:* with the shadow on, two elevation cameras changed colour as well as brightness (north +15.0, west +17.0). They look in across the perimeter fence's blended far fabric, a candidate, untested.

**NOT TAKEN UP.** Physical light units (re-tuning the whole library for nothing visible on its own); SDFGI, VoxelGI and native auto-exposure (Forward+ only); the spec's acceptance tests as a set.

**THE WALKER'S CALLS.**
- **The sky in the bake.** Level Factory's `environment_mode` 0 to 1 is one line. It is measured at four slots, it costs nothing at run time, and it does not touch the rooms. Recommended. The look is the call: shade on a clear afternoon goes from near black to blue-grey daylight.
- **Heavy Rain's sun.** Three ways:
  - re-price its shadow on today's package, since the 0.38.0 price predates the bake and the merges;
  - build the free lever, the sun on exterior layers only, which needs interiors on a layer of their own, Deli Counter's and Level Factory's to give;
  - keep the recorded trade.
- **The night boost.** Keep it in the fluorescent rigs as a recorded override, or move it out of the lamps so every source keeps its balance. On 9214 under Heavy Rain it is not what lights the rooms.
- **Morning and noon** have no preset yet (LEVEL_STANDARD section 17).

**NOT ESTABLISHED.**
- The warm patch at the foot of 9214's pole 24 is there with the lamp on or off (+0.7); what lights it was not measured.
- The night and evening FAILs on bank_block_001 and 9213's check-in hall are not worked, the black extraction at Blue Hour among them.

*STATUS: NARROWED 2026-10-09 -- shipped, not yet run cold. Level Factory 0.163.1 checks every import pass (a model counts once its sidecar's `dest_files` are there), repeats a short pass up to 3 times, keeps every pass's exit code and output in `<package>.import.log` beside the package, and stops the export on a pass that never completes; `ensure_imported` no longer takes a `.godot` folder for an import. 8 of its 9 tests fail on 0.163.0; the suite reads 2,058 passed, 14 skipped, 1 xfailed. Cold run 9214's first pass imported 0 of 425 models, the occluder bake said `ok` with 0 modules, and the Empties' merge refused; the same package imported 425 of 425 in seven fresh reruns. Open: a cold run on 0.163.1, and why the pass stopped short.*

**218. The export's import pass checked nothing.** Found 2026-10-09 by cold run 9214, which stopped at its export and finished on a recorded retry (0 interventions, 1 retry).

**WHAT HAPPENED** (`docs/cold_runs/cold_9214/NOTES.md`, and the first attempt's records beside it).
- **The pass.** At 15:30:40 the export ran Godot's `--import` on the fresh package (`export.py`, `_write_import_sidecars`). It left sidecars on 140 of the package's 975 importable files, all SkyMint's (they arrive with Lux's runtime carrying their own), and on none of its 425 models.
- **Nothing looked.**
  - The pass's exit code and output were thrown away.
  - `occluders.ensure_imported` took the `.godot` folder the pass left for an import.
  - The occluder bake loaded a scene whose every module was missing and wrote `ok: true`, 0 occluders from 0 modules. The export printed that line as a result.
  - The Empties' merge was the first step to refuse: "no side to merge" on all 12.
- **Not the content.** The same package imported 425 of 425 in seven fresh reruns, 37 to 45 s each, two of them from the export's exact starting state.
- **Not established: why the pass stopped short.** Godot's output was not kept. An external USB drive was throwing disk errors that day; they had stopped three minutes before, and cold run 9213 exported cleanly during them.

**LEVEL FACTORY 0.163.1** (`patches/patch_lf_import_pass_verified.py`, its sources in `patches/lf_import_pass_verified/`).
- **What counts as imported.** `occluders.unimported_models`: a model whose sidecar names `dest_files` that are there. The shape was read off a real Godot 4.7 sidecar from 9214's package. A sidecar naming no files is an unrecognised shape and does not count. `package_models` skips `.godot/` and any `.gdignore` folder, as Godot does.
- **The export's pass** checks itself after every run, repeats a short pass up to `IMPORT_PASSES` (3, chosen: one short pass in eight, about 40 s a pass), keeps every pass's output in `<package>.import.log` beside the package, and raises `ExportImportError` on a pass that never completes. The second pass, after the sidecar rewrite, is checked the same way. No Godot at all is still a setup problem.
- **`ensure_imported`** returns early only when every model is imported, and refuses an import that leaves any behind. The occluder bake, the Empties' merge and the greybox census start there.
- **The stub Godot imports models.** `tests/fixtures/bin/godot.py` wrote a bare `.godot`, and two integration tests had passed on it only because nothing checked. On this change they stopped with "3 of 3 model(s) unimported", and the stub now writes each model's sidecar the way Godot 4.7 does.

**NOT DONE.**
- **The occluder bake still says `ok` on a scene with no modules.** The import check now stops the export before it can, but the bake cannot tell an empty site from an unloadable one.
"""


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "RESULT" not in ITEMS and "STATUS " not in ITEMS.replace("*STATUS: ", ""), \
        "a result placeholder is left in the items"
    assert text.endswith(LAST), "the roadmap no longer ends with item 216's last line"
    assert text.count(LAST) == 1, text.count(LAST)
    assert "**217. " not in text and "**218. " not in text, "already applied"
    ROADMAP.write_bytes((text + ITEMS).encode("utf-8"))
    print("appended items 217 and 218")


if __name__ == "__main__":
    main()
