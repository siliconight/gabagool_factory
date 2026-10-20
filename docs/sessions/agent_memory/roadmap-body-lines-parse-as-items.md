---
name: roadmap-body-lines-parse-as-items
description: In PIPELINE_ROADMAP.md a body line starting **<digits>. is parsed as an item heading; write step lines as **Step N ...**
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T10:55:36.042Z
---

`tools/roadmap_status.py` reads any line matching `^\*\*(\d+)\. ` as an
item heading (`_ITEM`). On 2026-10-10 three step lines written into items
224 and 225 ("**1. MEASURED ...**", "**1. DONE ...**", "**2. ANSWERED
...**") became a second item 1 twice and a second item 2. The index
counted 229 items for 226, and `--check` still said "index matches its
items", because it regenerates from the same parse.

**Why:** the check cannot catch it, so it ships silently and corrupts the
index and the counts.

**How to apply:**
- In a roadmap item's body, write numbered steps as `**Step 1, ...**` or
  `**1)` mid-line, never `**1. ` at a line start.
- After `--write`, compare the count line's item total with the highest
  item number.

Related: [[gabagool-roadmap-edit]].
