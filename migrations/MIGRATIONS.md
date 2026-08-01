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
| `patch_check_all_scope.py` | 12019 | 2026-07-31 19:09 | check_all's gdscript row never ran. Two defects, and they are not the same one. |
| `patch_claude_md_goal.py` | 6881 | 2026-07-31 22:05 | CLAUDE.md gains the thing it never stated: what the factory is FOR. |
| `patch_gdcheck_tokens.py` | 9918 | 2026-07-31 22:09 | gdcheck flagged four files and was wrong on all four. Two defects, one cause. |
| `patch_roadmap_goal.py` | 8161 | 2026-07-31 21:15 | Items 17 and 18: the pipeline has never been run cold, and nothing measures feel. |

