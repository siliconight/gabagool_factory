"""The level standard v1.2: cold run 9194, the first level whose score is the
building its brief asked for.

    python patch_level_standard_v1_2.py

Each change was read against the run's own artefacts or the code on 2026-10-07:
  - §4: Level Factory 0.152.0 (`building_library.score_building`,
    `site_placements(..., objective=)`, `objective_from`); 9194's three
    candidates put the score in b0, a bank, objective point the basement vault
  - §5: `walktest_navqa`'s path proofs are home -> each anchor plus a chain
    through them (seed_9054: 25 legs, none vault -> extraction); 9194's crew
    wedged leaving the vault on bank_branch_a04 (roadmap 203)
  - MacDade item 0: done
  - Appendix A: `target_minutes` reaches nothing. v1.1 said "Laser Tag's
    scenario timing, BUILT"; nothing in lasertag/ or in Level Factory's Laser
    Tag path reads it (searched for target_min, minutes, session, time_limit)

Anchored on docs/LEVEL_STANDARD.md as 411e4d8 left it (64,274 bytes, LF).
Every anchor must match once; nothing is written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "LEVEL_STANDARD.md"

EDITS = [
    # the version line
    ("**This is v1.1** (2026-10-07). v1's tool claims were re-checked against the\n"
     "code by a full capability sweep, and 26 were corrected\n"
     "(`patches/patch_level_standard_v1_1.py` lists each, and the code it was\n"
     "checked against). Its spine",
     "**This is v1.2** (2026-10-07). It records cold run 9194, the first level\n"
     "whose score is the building its brief asked for (§4, §5, Part II's first\n"
     "item and Appendix A; `patches/patch_level_standard_v1_2.py`). v1.1\n"
     "re-checked v1's tool claims against the code by a full capability sweep\n"
     "and corrected 26 (`patches/patch_level_standard_v1_1.py` lists each, and\n"
     "the code it was checked against). Its spine"),
    # §4: the score building
    ("- **The score building is a seeded pick, not a decision.**\n"
     "  `site_variation.site_placements` draws the spawn and the objective\n"
     "  building independently from the seed. It ignores the archetype, and it\n"
     "  ignores which building holds the objective rooms. The objective can even\n"
     "  be the spawn building. GAP, owner Level Factory: the score should be the\n"
     "  building the brief asked for. Dispatch's mission flow is spawn -> extract\n"
     "  only.\n",
     "- **The score is the building the brief asked for** (Level Factory\n"
     "  0.152.0, roadmap 201). On a library lot `pick_lot` places the\n"
     "  archetype's family first, and `building_library.score_building` makes\n"
     "  that building, b0, the objective. The spawn is drawn among the others,\n"
     "  and the site spec records which rule decided (`objective_from`:\n"
     "  `archetype` or `seed`). With no family for the archetype the seeded pick\n"
     "  stands, and says so. Proven in cold run 9194: all three bank_block_001\n"
     "  candidates put the score in a bank's basement vault. BUILT. Dispatch's\n"
     "  mission flow is spawn -> extract only.\n"
     "  - *v1.1 read GAP here, correctly at the time:* the spawn and the\n"
     "    objective were two independent seeded draws, blind to the archetype,\n"
     "    and the objective could be the spawn building.\n"
     "  - *What it exposed:* on bank_branch_a04 the crew wedges leaving the\n"
     "    vault (roadmap 203, §5).\n"),
    # §5: what the walk test proves
    ("| everything reachable | Deli Counter's nav gate on every library build; Level Factory's structural checks "
     "(\"blockers open\") on every leg of a run; the walk test (`walktest_navqa`), which picks the candidate; Laser "
     "Tag's route completion and stuck events | GATE (nav gate, blockers); MEASURED (walk test, Laser Tag: advisory "
     "by contract) |\n",
     "| everything reachable | Deli Counter's nav gate on every library build; Level Factory's structural checks "
     "(\"blockers open\") on every leg of a run; the walk test (`walktest_navqa`), which picks the candidate; Laser "
     "Tag's route completion and stuck events, which the cold driver's pick reads since roadmap 203 | GATE (nav gate, "
     "blockers); MEASURED (walk test, Laser Tag: advisory by contract). GAP: the walk test proves home -> each anchor "
     "and a chain through them, never the mission's order (spawn -> objective -> extraction). Cold run 9194's crew "
     "wedged on the leg it skipped, leaving the vault (roadmap 203) |\n"),
    # Part II, MacDade's first item
    ("0. **The score is the building the brief asked for.** Today the objective\n"
     "   building is a seeded pick, independent of the archetype and of which\n"
     "   building holds the vault (§4). Owner: Level Factory. It is the cheapest\n"
     "   item here and the one every other item assumes.\n",
     "0. **The score is the building the brief asked for.** DONE: Level Factory\n"
     "   0.152.0, proven in cold run 9194 (§4). It sent the crew into a bank's\n"
     "   vault for the first time, and on one bank variant they wedge leaving it\n"
     "   (roadmap 203): a defect no level could show while the score was\n"
     "   elsewhere.\n"),
    # Appendix A: target_minutes
    ("| session_min | `target_minutes` | Laser Tag's scenario timing | BUILT |\n",
     "| session_min | `target_minutes` | **nothing reads it.** *v1.1 read \"Laser Tag's scenario timing, BUILT\":* "
     "wrong. Nothing in Laser Tag or in Level Factory's Laser Tag path reads it (re-checked 2026-10-07). Lot's pacing "
     "estimate is the reader it was meant for, and is wired by Level Factory 0.153.0 | GAP (roadmap 200) |\n"),
]


def main():
    data = DOC.read_bytes()
    assert len(data) == 64274, "LEVEL_STANDARD.md is %d bytes, read at 64,274" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    for old, new in EDITS:
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    print("LEVEL_STANDARD.md: v1.2, %d edits, %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
