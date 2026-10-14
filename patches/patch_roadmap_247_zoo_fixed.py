"""Roadmap 247, 2026-10-14: the roof props traced and fixed in Zoo 1.109.0, proven by cold runs 9299 and 9300 --
the status OPEN -> NARROWED, what remains named in it; one body paragraph after the Lux one, at the end of the file.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_247_zoo_fixed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("*STATUS: OPEN 2026-10-14 -- measured, not traced: one mesh, the satellite dish's, the same 376 triangles "
              "with 64 of its vertices in another order; the step that reorders them is Zoo's to find. Found beside it "
              "with cold run 9298: Lux's applied scene, the same ten lights' energies differing in every pair of runs "
              "since 9295 by about one part in 10,000; not traced.*")
STATUS_NEW = ("*STATUS: NARROWED 2026-10-14 -- the roof props fixed in Zoo 1.109.0 (c2edb80): the satellite dish's bowl, "
              "a `create_uvsphere` whose faces come in an order that changes from process to process, left the bevel "
              "with its faces starting at other corners, which `bm_to_object`'s sort by corners cannot undo "
              "(`docs/findings/roofprops_bytes/stage_runs.py`), and `bevel_edges` now restarts every face it leaves at "
              "its lowest vertex. Cold run 9298's 40 Zoo jobs, replayed three times each: 39 byte-stable on 1.108.0, "
              "40 on 1.109.0. Cold runs 9299 and 9300, one command twice: every GLB and the lightmap the same bytes, "
              "22 of 3,283 files different. Left: Godot's per-save ids in the scenes the export saves, and Lux's "
              "eleven light energies in its applied scene (`docs/findings/roofprops_bytes/README.md`, \"What remains "
              "of 247\").*")

BODY_ANCHOR = ("Not traced: what sets those energies, and whether these eleven are among the level's 27 live rigs.\n")
BODY_NEW = BODY_ANCHOR + (
    "\n**TRACED AND FIXED IN ZOO, 2026-10-14** (`docs/findings/roofprops_bytes/`: `stage_digest.py` and "
    "`stage_runs.py`, `shuffle_bevel.py`, `normal_shift.py`, `churn.py`; `patches/patch_zoo_bevel_restart.py`; "
    "`docs/cold_runs/cold_9299/`, `cold_9300/`). Cold run 9298's roof-props command, replayed six times on Zoo "
    "1.108.0, built the GLB four ways, one of them 9294's and 9296's bytes; over all 40 of 9298's Zoo jobs, three "
    "replays each, it was the only one to vary. `stage_runs.py` ran the job's own command with Zoo's build steps wrapped "
    "in memory and the dish's parts digested after each, in six fresh processes: the pole, the arm and the feed are "
    "one mesh throughout; the bowl, an `add_ellipsoid`, reaches the bevel with its faces in five orders in six -- the "
    "same faces from the same corners -- and leaves it with the same faces starting at other corners, which the 1.103.0 "
    "sort by corners orders four ways. **Refuted and kept:** \"one build's normals are others, by up to 1.67\" -- "
    "`zoo_repro_probe.how` sorts each array alone, and a 1e-4 wobble pairs different vertices; paired by position and "
    "UV the variants' normals lie within 0.0044 degrees. Bytes, not shading. `shuffle_bevel.py`, one process, the "
    "bowl's faces laid in six orders: bevelled as laid, six meshes and then four; sorted back into one order first, "
    "six and six -- the bevel's start moves with more than the order; restarted at the lowest vertex just after the "
    "bevel, one mesh, the same in two processes. **Zoo 1.109.0** (c2edb80) does that in `bevel_edges`, and "
    "`start_at_lowest` carries every loop layer's corner data with its corners where it refused any -- a turning part "
    "reaches the bevel with its UVMap and Pivot layers. Replayed: 40 of 40 jobs byte-stable. The one-time move, "
    "measured against a 1.108.0 replay as the control (1 file): 1,138 of 1,866 files in all 40 jobs, positions, "
    "colours and UVs reordered, normals within 0.013 degrees over 797,941 paired vertices. Cold run 9299 (0 "
    "interventions) moved nothing the graders read and 1,078 package files, 364 of its 596 GLBs and what follows "
    "from them; cold run 9300, the same command again (0 interventions), differs from 9299 in 22 of 3,283 files, every "
    "GLB and the lightmap the same bytes. What two runs still disagree on: Godot's per-save ids -- node `unique_id`s "
    "and drawn resource ids, 0 lines once masked -- in `bake.tscn`, the standing Empties' `site.tscn` and Lux's "
    "applied scene; Lux's eleven light energies; and the metadata recording times, paths and the hashes of those. "
    "Found on the way, filed apart: Zoo's `test_club_bpy.py` golden digests fail on 1.108.0 as on 1.109.0, and run "
    "only inside Blender.\n")


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
    assert "**TRACED AND FIXED IN ZOO, 2026-10-14**" not in text, "already applied"
    for old in (STATUS_OLD, BODY_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 247)
    assert s < text.find(STATUS_OLD) < h, "247's status is not where it was read"
    assert text.endswith(BODY_ANCHOR), "247's body does not end there"
    for line in BODY_NEW.splitlines():
        assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(STATUS_OLD, STATUS_NEW).replace(BODY_ANCHOR, BODY_NEW)
    s, h, e = _span(text, 247)
    assert text[s + 2:h] == STATUS_NEW, "247's status does not adjoin its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 247 NARROWED: Zoo 1.109.0; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
