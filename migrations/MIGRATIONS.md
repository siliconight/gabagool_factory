# Migrations

One-shot scripts that have already run. **Do not delete them.**

Twice in one session a file the device bridge served stale was recovered by
applying the patches that followed an older backup and confirming the result
landed on the byte count the device reported. That works only because each
script records the exact before-and-after text it applied. These are the only
record of how the current source came to be.

Moved here by `tidy_migrations.ps1`. What stays at the root: the checkers
(`check_*.py`, `gdcheck.py`), the harnesses (`library_walk.py`,
`rebuild_buildings.py`), the standing tools, and the documents.

The split is a RULE, not a list -- `patch*.py` and `commit_*.ps1` are
generated name-spaces, so any enumeration of them is out of date the next time
somebody fixes something.

## 2026-08

| script | bytes | last written | what it did |
| --- | ---: | --- | --- |
| `patch_roadmap_props.py` | 7194 | 2026-08-01 11:31 | Item 22: outdoor props have no swap contract. Plus four carried smalls. |

