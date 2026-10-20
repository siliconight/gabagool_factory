---
name: gate-commits-on-the-patch
description: "Chain patch -> regenerate -> git commit with && only; a `;` before git add let a refused patch's commit through (b9c6635, 2026-10-07)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T14:28:44.028Z
---

On 2026-10-07 a roadmap patch refused: its anchor missed, which is the guard
working. The command line ran `python patch ... && ... ; git add ... && git
commit`. The `;` let the commit run anyway, and b9c6635 claimed "roadmap: 201
OPEN" while carrying only the patch script.

**Why:** a patch that refuses on a miss is the backstop
(`docs/SHIPPING_A_CHANGE.md` step 3). A commit that ignores the refusal
throws that backstop away and writes a false record.

**How to apply:**
- Every step from the patch to `git commit` is joined with `&&`. Never `;`
  before `git add` or `git commit`.
- When a bad commit happens, fix forward with a commit that names the bad one
  and says what it carried. Do not amend.

Related: [[bash-heredoc-large-bodies-fail]].
