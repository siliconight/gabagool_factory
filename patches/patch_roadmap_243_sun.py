"""Roadmap 243: the tiers shown, the sun baked at the walker's call (Lux 0.76.0, 0.76.1), proven in cold
run 9265, and what the baked sun changes taken apart (`docs/findings/lux_tiers/`). Replaces 243's status
(asserted once and still above its heading) and appends one paragraph to its body, the roadmap's last.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_243_sun.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S243_OLD = ("*STATUS: OPEN 2026-10-12 -- found, a call for the walker. `LuxRoot.quality_tier` defaults to High "
            "and no tool sets it, so every package runs High (12 shadow casters, sun shadows, post-fx, glow) on "
            "GL Compatibility; roadmap 60's Compatibility tier (4 casters, no sun shadows, no post-fx, no glow) "
            "has never shipped. Measured on cold run 9262's package (`docs/findings/pole_line/`): its twelve "
            "shadowed street lights cost 300 draws a heading; a budget of 8 saves 118, of 4 saves 241.*")
S243_NEW = ("*STATUS: NARROWED 2026-10-12 -- the tier's largest cost taken out at the walker's call: on cold run "
            "9264's level the sun's live shadows were 1,854 of High's 2,642 draws a heading and 3.56 ms of an "
            "8.0 ms median p95 (`docs/findings/lux_tiers/`). Lux 0.76.0 bakes the sun while a lightmap shows -- "
            "static in the editor, so Level Factory's bake carries it; static and unshadowed at run time; "
            "dynamic with the preset's shadows whenever no lightmap shows, the power cut included -- and cold "
            "run 9265 proves it in a real drive (0 interventions): the sun static and unshadowed as the game "
            "runs it, the frames the chosen arm's within a re-bake's noise, -1,854.4 draws a heading and the "
            "p95 -3.03 ms at the median against a 0.24 ms noise floor, headings over 16.7 ms 5 -> 1. What it "
            "gives up, measured: what moves takes and casts no sun shadow, and the backdrop -- outside Level "
            "Factory's bake -- takes the sun with no shadow and casts none on the level. Left: which tier a "
            "package runs (the walker's; High with the sun baked draws 788 a heading against Low's 538); the "
            "street lights' shadow budget (with 240); the backdrop's look under a baked sun (levers in the "
            "findings); the level's sunlit faces reading darker under the baked sun, 1.6 levels of it "
            "specular, the rest unattributed.*")

BODY_243 = """

**THE TIERS SHOWN AND THE SUN BAKED, 2026-10-12** (`docs/findings/lux_tiers/`). Asked which tier, the walker: "didn't know we had this... not sure", so the four were shown on cold run 9264's level (`tier_frames.py`, `tiers.png`): High 2,642 draws a heading and a 7.73 ms median p95, Medium 2,457 and 7.21, Low and Compatibility 538 and 4.18 to 4.32 -- High and Medium dark and contrasty with the film look, Low and Compatibility brighter and flatter, every surface readable. "Test the High look without sun shadows": arm A, the preset's sun shadows off, 788 draws and 4.46 ms, reads as Low with High's post look; arm B2, the sun built static and re-baked, then drawn without its shadows, 788 draws and 4.42 ms, the nearest to High (`sun_variants.py`, `sun_price.py`). The walker: "Bake the sun by default". Lux 0.76.0 (`patches/patch_lux_sun_baked.py`; `tools/sun_bake_selftest.gd`, 12 checks, five failing on 0.75.0) and cold run 9265 (`docs/cold_runs/cold_9265/`: `sun_state.gd` against 9264's package as the control, the frames, the price). **RETRACTED, KEPT:** arm B -- the sun static with its shadow flag off for the bake -- was filed as baking unoccluded, "as flat as A", and Lux 0.76.0's comment repeated it as measured; B's frames were in no table, and measured they are B2's within a re-bake's noise (1.6 to 2.5 levels): the flag does not change the bake. Lux 0.76.1 (`patches/patch_lux_sun_comment.py`) corrects the comment, no behaviour changed. **WHAT THE BAKED SUN CHANGES, TAKEN APART** (`sun_occluders.sh`, `backdrop_split.sh`, `spec_arm.sh`). Level Factory bakes `bake.tscn`, the presentation scene; the game's `mission.tscn` also loads `site_backdrop.tscn` -- 25 MultiMeshes of 269 instances, rowhomes 8 to 11 m high and a 40 m water tower in rows round the level 58 to 181 m out, its west and north sides between blue hour's sun and the level -- which no bake has seen. Split by pixel: about half of corner's difference and half of elev_N's lie on the backdrop, which under the baked sun takes the sun with no shadow from anything (corner's far row 60.5 -> 66.2 luma, elev_N's homes 15.6 -> 36.5); its long shadows no longer fall on the level (taken away under the live sun, the level at up 52.6 -> 59.1); a lightmap's missing specular is 1.3 to 1.6 levels on the level; the rest of the level's sunlit faces reading darker under the baked sun (up 57.5 against 46.9 with both taken away) is not attributed. Levers, none taken: the backdrop as a caster in the bake (what the lightmapper does with a MultiMesh is unmeasured), its own lighting by cause, or nothing -- far scenery, its shadows short under a higher sun."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE TIERS SHOWN AND THE SUN BAKED" not in text, "already applied"
    assert text.count(S243_OLD) == 1, "243's status not found once"
    text = text.replace(S243_OLD, S243_NEW)
    h = text.find("\n\n**243. ")
    assert h > 0 and text[h - len(S243_NEW):h] == S243_NEW, "243's status does not sit above its heading"
    assert text.find("\n\n*STATUS:", h + 10) < 0, "243 is not the roadmap's last item"
    assert text.endswith("than the RTX 2060.\n"), text[-80:]
    text = text[:-1] + BODY_243 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 243: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
