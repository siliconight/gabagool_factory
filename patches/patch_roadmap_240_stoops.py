"""Roadmap 240, 2026-10-13: the rowhouse front's stoops built and proven (Deli Counter 0.211.0/0.211.1, Level
Factory 0.195.0/0.196.0; cold runs 9271 and 9272; `docs/proposals/ROWHOUSE_STOOP.md`). Replaces the end of
240's status (asserted once and still directly above its heading) and appends one paragraph to its body,
before 241's status. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check`.

    python patches/patch_roadmap_240_stoops.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S240_OLD = ("Left: the street lights' shadow cost, the walker's call with that seen; the frames beside the comps "
            "for the walker's eye; then the rowhouse front, the roofscape's rear ells, and the coating when a "
            "1990s source says how common it was.*")
S240_NEW = ("The rowhouse front's stoops are built: every rowhome Empty stands three steps up, its door and window "
            "raised, on a stoop the contract body walks with no step-up code (Deli Counter 0.211.0/0.211.1, Level "
            "Factory 0.195.0/0.196.0; cold runs 9271 and 9272, 0 interventions each; +6.5 draws a heading on the "
            "mean, p95 +0.04 ms against a 0.06 ms floor). Left: the street lights' shadow cost, the walker's call "
            "with that seen; the frames beside the comps for the walker's eye; the front's iron railings, its "
            "dishes and parged fronts; then the roofscape's rear ells, and the coating when a 1990s source says "
            "how common it was.*")

BODY_240 = """

**THE STOOPS, 2026-10-13** (`docs/proposals/ROWHOUSE_STOOP.md`; `docs/cold_runs/cold_9271/`, `cold_9272/`). **Grounded:** the comps' "three or four steps up to each door, with iron railings; the first floor stands above the sidewalk"; Philadelphia's *Rowhouse Manual* (City Planning Commission, 2008, p. 13): "Most existing rowhouses are a few steps up from the street", no dimensions; the residential code fills them (IRC R311.7.5: a riser at most 7 3/4 in, a tread at least 10 in). **The contract decides the collision:** a 7 in riser is 1.7 times the 0.1025 m unassisted step, so, as the stairs do, the stoop is walked on one ramp whose top face is the nosing line (32.5 deg), its foot at grade a tread past the bottom riser, its head on the landing's edge. **Deli Counter 0.211.0** (`stoop.py`; `patches/patch_dc_rowhome_stoop.py`): three 7 in risers on 11 in treads, a 0.9 m landing, 1.5 m across, 1.74 m deep with its ramp -- inside Level Factory's 2.0 m terrace frontage, which four risers would not be. The ground storey's door and window rise together, a 0.3834 m sill on the 0.3 m slab; all twelve rowhomes take three. **Level Factory 0.195.0** (`patches/patch_lf_terrace_stoop.py`): the terrace read each house's extent off its colliders, and read whole every house would have stood 1.738 m further back; it reads the house without its stoop (`street_line.STOOP_COLLIDERS`), so 9271's 23 blockers and plate are 9270's to the digit. **Cold run 9271** (0 interventions): the contract body with no step-up code walks up gs_empty_rowhome_a's stoop onto its landing (feet 0.534 m, against the door), where a solid block and a single 7 in riser stop it. **It found two things, both fixed and proven in 9272** (0 interventions). `PRESENTATION_CIRCULATION` 0 -> 12 read each landing as a prop 0.15 m into its own doorway -- the gate's offset: `doorway_volume` starts a door at the wall's bottom plus the sill, the builder 0.15 m higher. It is recorded, not changed; Deli Counter 0.211.1 draws the stoop as `stair`, the way to the door. The price read +22.7 draws a heading (+93 at the worst): the Empties' merge takes apart only slots whose names give a side, and the stoop's give none. Level Factory 0.196.0 merges `stoop_*` with the front. **In 9272:** findings back to 117; 36 meshes into 12; +6.5 draws a heading on the mean (at most +29), p95 +0.04 ms against a 0.06 ms floor; the walk to the millimetre. **For the walker's eye:** `cold_9271/stoops.png`, the stoops in concrete without their iron railings (Zoo's, next); and three risers or four, the tread's stone, one railing or two, the proposal's open calls."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE STOOPS, 2026-10-13" not in text, "already applied"
    assert text.count(S240_OLD) == 1, "240's status end not found once"
    text = text.replace(S240_OLD, S240_NEW)
    h = text.find("\n\n**240. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s:h].endswith(S240_NEW), "240's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "241 does not follow 240"
    text = text[:nxt] + BODY_240 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
