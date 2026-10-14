"""Roadmap 241 and 247, 2026-10-14: a package carries the buildings its scene stands -- Level Factory 0.207.0, cold
run 9298 -- and what that run found beside it.

241 stays NARROWED: its status gains 0.207.0 before its Left clause, and one body paragraph follows the awning's.
247 stays OPEN: its status and body gain Lux's applied scene, whose eleven light energies differ between runs. The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_standing_lot.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_241_OLD = "its frame time unpriced on a busy machine. Left: the walker's eye on 9287's"
STATUS_241_NEW = ("its frame time unpriced on a busy machine. Level Factory 0.207.0 (dff4b8c) ships only the `lot/` "
                  "packages the assembly stands: cold run 9298 (0 interventions) carried 13 of 16, 11.4 MB and 95 baked "
                  "imports fewer, and moved nothing the graders read. Left: the walker's eye on 9287's")

BODY_241_ANCHOR = ("with themselves by 0.48 and 1.22 ms with StarCraft II running on the machine.\n\n")
BODY_241_NEW = BODY_241_ANCHOR + (
    "**WHAT A PACKAGE CARRIES, 2026-10-14** (`patches/patch_lf_standing_lot.py` and `lf_standing_lot/`; "
    "`docs/cold_runs/cold_9298/`). Found with cold run 9295 and recorded then: the package carried every Empty the "
    "brief was themed with, standing or not. The compose stage themes every corner block and mid-rise an urban brief "
    "is given, a candidate stands some, and the export copied the composed root whole: 9297's package carried sixteen "
    "`lot/` packages while its assembly scene named thirteen. **Level Factory 0.207.0** (dff4b8c) leaves out a composed "
    "`lot/<id>/` no scene stands and prints which. What stands is read off the assembly's own `lot/<id>/site.tscn` "
    "references, and a package is matched on a relative path's first two parts, never on a name -- `_copy_tree`'s "
    "`skip` matches basenames anywhere, the failure `skip_rel` was written for. Where no assembly scene can say, "
    "nothing is left out. Its test fails on 0.206.1 on its two defect cases and passes its three controls there. Cold "
    "run 9298 (0 interventions, seed_9104 named against 9297's; `package_trim.py`, which read 0 on a package against "
    "itself and saw the awning between 9296 and 9297): `lot/` packages 16 -> 13, files 3,704 -> 3,283, bytes 210.7 -> "
    "199.1 MB, the light bake's model imports 711 -> 616 with lightmap users unchanged at 3,147, the closure clean. "
    "Every other file is byte-identical but the 23 any two exports differ in, each attributed in the run's NOTES: "
    "timestamps and paths, the trim's own records, Godot's per-save ids (0 lines once masked, `per_save_ids.py`) and "
    "Lux's applied scene. Nothing the graders read moved. Not priced: nothing left out was instanced, and StarCraft II "
    "was running; the editor's import and the bake were no faster in that one run (75.4 s against 70.4, 38.7 s "
    "against 36.4). Found there and recorded under 247: Lux's applied scene is not byte-stable either.\n\n")

STATUS_247_OLD = ("*STATUS: OPEN 2026-10-14 -- measured, not traced: one mesh, the satellite dish's, the same 376 "
                  "triangles with 64 of its vertices in another order; the step that reorders them is Zoo's to find.*")
STATUS_247_NEW = ("*STATUS: OPEN 2026-10-14 -- measured, not traced: one mesh, the satellite dish's, the same 376 "
                  "triangles with 64 of its vertices in another order; the step that reorders them is Zoo's to find. "
                  "Found beside it with cold run 9298: Lux's applied scene, the same ten lights' energies differing in "
                  "every pair of runs since 9295 by about one part in 10,000; not traced.*")

BODY_247_ANCHOR = ("so the reordering more likely happens inside one part's build. Not traced: which step, and why one "
                   "run in three.\n")
BODY_247_NEW = BODY_247_ANCHOR + (
    "\n**LUX'S APPLIED SCENE, 2026-10-14** (`docs/findings/roofprops_bytes/lux_energy_pairs.py`, "
    "`lux_energy_pairs.out.txt`; `docs/cold_runs/cold_9298/NOTES.md`). Attributing every file cold run 9298's package "
    "differed from 9297's in found one more: urban_row_001's packaged `presentation/lux.applied.tscn`, with node "
    "`unique_id`s and Godot's drawn resource ids masked, still differs in 10 or 11 of its 9,581 lines in every pair "
    "from 9295 to 9298. The same ten lights' `light_energy` move by about one part in 10,000 -- seven "
    "`Spawned_pendant_*` fluoros under `LuxFixtureLights`, and `site_pole_43`, `site_pole_53` and `site_lamp_78` "
    "under `LuxClub` -- and `Spawned_fluorescent_038_dup2` reads 2.618 in 9295, 9296 and 9298 and 3.7 in 9297. "
    "Not traced: what sets those energies, and whether these eleven are among the level's 27 live rigs.\n")


def _span(text, number):
    """(status start, heading, next status) of item `number`; the last item runs to the end."""
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**WHAT A PACKAGE CARRIES, 2026-10-14**" not in text, "already applied"
    for old in (STATUS_241_OLD, BODY_241_ANCHOR, STATUS_247_OLD, BODY_247_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 241)
    assert s < text.find(STATUS_241_OLD) < h, "the Left clause is not 241's status"
    assert h < text.find(BODY_241_ANCHOR) < e, "the body anchor is not 241's"
    s, h, e = _span(text, 247)
    assert s < text.find(STATUS_247_OLD) < h, "247's status is not where it was read"
    assert h < text.find(BODY_247_ANCHOR) < e and text.endswith(BODY_247_ANCHOR), "247's body does not end there"
    for block in (BODY_241_NEW, BODY_247_NEW):
        for line in block.splitlines():
            assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = (text.replace(STATUS_241_OLD, STATUS_241_NEW).replace(BODY_241_ANCHOR, BODY_241_NEW)
            .replace(STATUS_247_OLD, STATUS_247_NEW).replace(BODY_247_ANCHOR, BODY_247_NEW))
    s, h, e = _span(text, 241)
    assert text[s + 2:].startswith("*STATUS: NARROWED 2026-10-13 -- steps 2 and 3's first cut"), "241's status moved"
    s, h, e = _span(text, 247)
    assert text[s + 2:h] == STATUS_247_NEW, "247's status does not adjoin its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 241 and 247: the package trim and Lux's energies; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
