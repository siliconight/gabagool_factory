---
name: gate-commits-on-the-patch
description: "Chain patch -> regenerate -> git commit with && only, and never pipe a gating step (a pipeline takes its LAST stage's exit); a `;` let a refused patch's commit through (b9c6635)"
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
- **A pipeline hides a failure from `&&`.** `step | grep | cut && next` takes
  CUT's exit, so a failing `step` lets `next` run. 2026-10-21: a test-proof
  script failed to generate, `| grep | cut` passed 0 on, and the chain applied
  Deli Counter 0.248.0's patch to the real repo before the proof existed --
  harmless that time (the proof runs in a clone), but the gate was gone. Never
  pipe a step that gates the next one; or `set -o pipefail`, or test
  `${PIPESTATUS[0]}`.

Related: [[bash-heredoc-large-bodies-fail]].
