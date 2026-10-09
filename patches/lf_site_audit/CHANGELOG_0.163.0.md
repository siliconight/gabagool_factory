## [0.163.0] - Lot's site audit reaches the validation report

**Roadmap 215.** Lot runs its site audit (`site_audit.py`) at the end of
every assembly. It checks the exfil shape, responder pressure, safe anchors,
leg rhythm and street crossings. Until Lot 0.102.0 it printed its findings to
the job log and kept none. So this report carried no `S_` code, and no cold
run's findings diff, which counts this report's codes, ever counted one.

Measured on cold run 9209's seed_9181:
- **The job log** printed one MED, `S_RESPONDER_ARC`: all three responder
  stops inside a 6-degree arc of the objective. It also printed three INFO:
  `S_GETAWAY_AT_SPAWN`, and `S_STREET_CROSS` twice.
- **`validation/club_block_014.json`** held none of them.

**Read.** Lot 0.102.0 keeps the audit as `site_audit` in
`<stem>.site.gameplay.json`. `adapters.lot.normalize_validation` reads
each finding as an issue, at this model's severities
(`LOT_SITE_AUDIT_SEVERITY`):

| the audit | this report |
|---|---|
| HIGH | major |
| MED | moderate |
| INFO | info |

- **Category:** `combat_structure`.
- **Nothing blocks, HIGH included.** The audit is report-only, like Deli
  Counter's `combat_audit`. No rule raises HIGH today.
- **No block, or one this adapter cannot read,** raises
  `LOT_SITE_AUDIT_UNREAD` (moderate, non-blocking), rather than nothing. An
  absent audit and a clean one must not look alike. A Lot before 0.102.0
  raises it on every candidate.

**The stub Lot** under `tests/fixtures/repos/lot/` writes the block, as the
real one does: empty and clean.

**Tests.** `tests/unit/test_site_audit_report.py`, 13:
- **Lot's own audit and record, read by this adapter.** A site shaped like
  9209's seed_9181 (the van at the spawn, three stops within a few degrees,
  both legs across a road) gives the four codes the job log printed: one
  moderate, three info, none blocking.
- **No block** is one `LOT_SITE_AUDIT_UNREAD`.
- **A clean audit** says nothing. This one is a guard: it passes on 0.162.1
  too.
- **Eight shapes this adapter cannot read** are each one
  `LOT_SITE_AUDIT_UNREAD`. Among them: positions in place of fields, an
  unknown severity, an unhashable severity and a missing code.
- **HIGH** is a major, and not a blocker.
- **Every severity Lot's source writes** is one this adapter names.

All but the clean-audit guard fail on 0.162.1. `test_real_lot`
(`tests/real_tools/`) now also checks that the real Lot's block is read:
`gs_heist`, the calibration site, has three INFO findings and no
`LOT_SITE_AUDIT_UNREAD`.

**Suite:** 2,048 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). That is
2,034 + 13 + 1: `test_sibling_locator.py` checks every `.py` file in the
repo, so the new test file is one more case there (303 to 304).

