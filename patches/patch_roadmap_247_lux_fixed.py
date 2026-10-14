"""Roadmap 247, 2026-10-14: Lux's light energies traced and fixed in Lux 0.77.0 and Level Factory 0.208.0, proven by
cold runs 9301 and 9302 -- the status stays NARROWED, its Left down to Godot's per-save ids; one body paragraph after
the Zoo one, at the end of the file. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_247_lux_fixed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("22 of 3,283 files different. Left: Godot's per-save ids in the scenes the export saves, and Lux's "
              "eleven light energies in its applied scene (`docs/findings/roofprops_bytes/README.md`, \"What remains "
              "of 247\").*")
STATUS_NEW = ("22 of 3,283 files different. Lux's eleven light energies fixed in Lux 0.77.0 (4ce4c85) and Level "
              "Factory 0.208.0 (b8fe4f7): the rigs animated from their own clocks through the seven frames "
              "`run_lux_apply.gd` awaits, and every rig now rests before the pack; cold runs 9301 and 9302, one command "
              "twice, read all 12 scenes Godot saves -- the applied scene among them -- 0 lines apart once its per-save "
              "ids are masked. Left: those ids, node `unique_id`s and drawn resource ids, and the metadata that hashes "
              "them (`docs/findings/roofprops_bytes/README.md`, \"What remains of 247\").*")

BODY_ANCHOR = ("Found on the way, filed apart: Zoo's `test_club_bpy.py` golden digests fail on 1.108.0 as on 1.109.0, "
               "and run only inside Blender.\n")
BODY_NEW = BODY_ANCHOR + (
    "\n**LUX'S ENERGIES, TRACED AND FIXED, 2026-10-14** (`docs/findings/roofprops_bytes/`: "
    "`lux_apply_replay.out.txt`, `lux_energy_pairs_9300_9301.out.txt`, `per_save_ids_9301_9302.out.txt`; "
    "`patches/patch_lux_rig_rest.py`, `patch_lf_rigs_rest.py`; `docs/cold_runs/cold_9301/`, `cold_9302/`). The "
    "eleven energies are already apart in the `lux_apply` job's own output, before the bake touches the scene. "
    "`run_lux_apply.gd` runs as a headless `SceneTree` script and awaits seven frames before it packs; Lux's "
    "fluorescent and streetlight rigs animate a failing or flickering lamp from their own clocks on each, by the "
    "frame's wall-clock delta, and the stage light cycles its colours on its own -- so `pack()` saved a different "
    "moment every run. **Lux 0.77.0** (4ce4c85): the three rigs answer `rest()`, every lamp back at what its rebuild "
    "gave it, a failing lens at its own glow, every clock at zero; `tools/rig_rest_selftest.gd`, 24 checks, fails on "
    "0.76.1 on its four `rest()` checks while its driven cases pass there. **Level Factory 0.208.0** (b8fe4f7): "
    "every rig in `lux_light_rig` rested after the last frame awaited and before the pack, and counted in the log. "
    "Replayed before shipping from a copy of 9300's staging folder: two unpatched applied scenes 10 lines apart once "
    "the per-save ids are masked, two patched ones 0; patched against unpatched, 12 lines -- the 10 lights that "
    "wandered, and two poles, `site_pole_46` and `site_pole_76`, saved at 0.0 in every run because their failing "
    "cycle starts dark, now at the energy their rebuild gives. Cold run 9301 (0 interventions, 216 rigs at rest): "
    "13 lights in the applied scene at rest against 9300's, the lightmap 9300's byte for byte though two poles save "
    "at 34.12 where they saved at 0.0 -- a saved energy never reaches the bake, as `_rebuild`, which frees every "
    "saved lamp at load, says -- and nothing the graders read moved. Cold run 9302, the same command again (0 "
    "interventions): 22 of 3,283 files differ from 9301, and all 12 scenes Godot saves read 0 lines apart once its "
    "per-save ids are masked. What two runs of one command still disagree on: those ids, and the metadata recording "
    "times, paths and their hashes.\n")


def _span(text, number):
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**LUX'S ENERGIES, TRACED AND FIXED, 2026-10-14**" not in text, "already applied"
    for old in (STATUS_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 247)
    assert s < text.find(STATUS_OLD) < h, "247's status is not where it was read"
    assert text.endswith(BODY_ANCHOR), "247's body does not end there"
    for line in BODY_NEW.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(BODY_ANCHOR, BODY_NEW)
    s, h, e = _span(text, 247)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-14 -- the roof props fixed in Zoo 1.109.0"), \
        "247's status moved"
    assert text[s + 2:h].endswith(STATUS_NEW), "247's status does not adjoin its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 247 NARROWED: Lux 0.77.0 and Level Factory 0.208.0; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
