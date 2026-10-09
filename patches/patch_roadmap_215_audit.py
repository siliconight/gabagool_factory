"""Roadmap 215 NARROWED: the site audit reaches the validation report (Lot
0.102.0, Level Factory 0.163.0, cold run 9210). The arc question stays open.

Anchored on 215's status block and on its last body line, which is the
roadmap's last line; each must match exactly once, or nothing is written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-08 -- split out of item 212 at its close, not worked. On club_block_014 (cold run 9209) "
    "the site audit reports all three responder arrivals inside a 6-degree arc of the objective, and that finding "
    "-- with every other site-audit finding -- reaches no report: it is in Lot's job log only.*\n"
    "\n"
    "**215. "
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-09 -- the site audit reaches the validation report. Lot 0.102.0 keeps it in the "
    "site's gameplay manifest and Level Factory 0.163.0 reads it, one non-blocking issue a finding (HIGH major, MED "
    "moderate, INFO info), `LOT_SITE_AUDIT_UNREAD` when it cannot. Cold run 9210 (club_block_014, 0 interventions): "
    "findings 58 to 72, every one of the 14 new ones attributed to a Lot run and matching its job log; "
    "`S_RESPONDER_ARC` fires on all three candidates, at 33, 6 and 16 degrees. Open: the arc question itself, now "
    "counted on every run of this mission.*\n"
    "\n"
    "**215. "
)

TAIL = ("- **First, separately:** carry the site audit into the validation report, so whatever it says is "
        "counted.\n")
NEW_TAIL = (
    "- **First, separately:** carry the site audit into the validation report, so whatever it says is counted. "
    "*Done, below.*\n"
    "\n"
    "**LOT 0.102.0 AND LEVEL FACTORY 0.163.0, DONE: THE AUDIT IS COUNTED (2026-10-09)** "
    "(`patches/patch_lot_site_audit_record.py`, `patch_lf_site_audit.py`). Instrument work: it makes findings Lot "
    "already computed visible to the report and to every cold run's findings diff. It reduces no interventions by "
    "itself.\n"
    "- **Lot keeps it.** `site_audit.record` makes the block, and `assemble` writes it as `site_audit` in "
    "`<stem>.site.gameplay.json`: the mode, the counts, and one dict a finding (`severity`, `code`, `message`). The "
    "fields are named, not the tuple's positions. The job log prints the same report as before.\n"
    "- **Level Factory reads it.** `adapters.lot.normalize_validation` reads each finding as an issue:\n"
    "  - HIGH as major, MED as moderate, INFO as info (`LOT_SITE_AUDIT_SEVERITY`);\n"
    "  - category `combat_structure`;\n"
    "  - never blocking: the audit is report-only, HIGH included.\n"
    "  - No block, or a shape it cannot read, is `LOT_SITE_AUDIT_UNREAD`. An absent audit and a clean one must "
    "not look alike.\n"
    "- **Tests.** Lot: 3, all failing on 0.101.0. Level Factory: 13, all but one failing on 0.162.1. The one is a "
    "guard: a clean audit says nothing.\n"
    "  - The Level Factory test reads Lot's own `audit` and `record`, so a change to Lot's shape fails there.\n"
    "  - `test_real_lot` fails against Lot 0.101.0 and passes against 0.102.0.\n"
    "- **Cold run 9210** (`docs/cold_runs/cold_9210/NOTES.md`, `audit_codes.py`): findings 58 to 72.\n"
    "  - `S_GETAWAY_AT_SPAWN` 0 to 4, `S_RESPONDER_ARC` 0 to 4, `S_STREET_CROSS` 0 to 6.\n"
    "  - Four of each, because the selected candidate is assembled twice, as a candidate and themed. Six "
    "crossings, because seed_9080's legs cross no road.\n"
    "  - The pick is unchanged (seed_9181): moderate and info move no count of majors.\n"
    "- **The arc question is unchanged in substance and is now counted.** `S_RESPONDER_ARC` fires on every "
    "candidate of club_block_014, at 33, 6 and 16 degrees against the rule's 210. The options above stand.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(OLD_STATUS) != 1:
        sys.exit("refusing: 215's status block matches %d times" % text.count(OLD_STATUS))
    text = text.replace(OLD_STATUS, NEW_STATUS)
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: 215's last line is not the end of the file")
    text = text[: -len(TAIL)] + NEW_TAIL
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 215 narrowed; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
