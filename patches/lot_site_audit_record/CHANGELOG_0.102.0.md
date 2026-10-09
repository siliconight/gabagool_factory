## 0.102.0 - the site audit is kept in the gameplay manifest, not only printed

**Roadmap 215.** `assemble` runs `site_audit` at the end of every assembly
and printed its report to the job log. It kept nothing, so no report counted
a finding it raised. On cold run 9209's seed_9181:
- **The job log** printed one MED (`S_RESPONDER_ARC`) and three INFO
  (`S_GETAWAY_AT_SPAWN`, `S_STREET_CROSS` twice).
- **Level Factory's validation report** carried no `S_` code.
- **So no cold run's findings diff,** which counts that report's codes, has
  ever counted the site audit.

**Kept.** `site_audit.record` turns the audit into the block the site's
`.site.gameplay.json` now carries as `site_audit`:
- `mode`, and `counts` by severity;
- `findings`, one dict a finding: `severity` (HIGH, MED or INFO), `code`
  and `message`. They are named fields, not the tuple's positions, so a
  reader that cannot find one can say so.

The job log prints the same report as before. Level Factory 0.163.0 reads
the block into its validation report.

**Tests.** `tests/test_site_audit_kept.py`, three:
- the manifest keeps exactly the findings the job log prints:
  `example_compound.json`, 2 MED and 1 INFO;
- the counts are the findings;
- a finding is named fields.

All three fail on 0.101.0, which has no block and no `record`.

**Suite:** 713 passed (710 + 3), `python -m pytest -q`.

