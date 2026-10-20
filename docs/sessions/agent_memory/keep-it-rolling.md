---
name: keep-it-rolling
description: "Walker 2026-10-05: keep working through the queue -- at the end of each block of work give the summary, then pick up the next suggested chunk without waiting for a yes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T02:44:04.861Z
---

The walker, 2026-10-05: "keep it rolling. Once you finish a 'session' or
'block' of work, end like you just did, then pick up the next suggested chunk
of work."

**Why:** the walker would rather steer by interrupting than approve each
step; waiting at every block boundary idles the pipeline.

**How to apply:**
- Close each block with the usual summary (what shipped, the measurements,
  what is next), then start the next chunk in the same turn.
- The next chunk is the one already suggested: the queue in
  [[empties-get-dark-interiors]] and [[cover-draws-roadmap-180]], then the
  walker's standing order ([[fence-marks-the-playable-edge]]: Empties, then
  optimise, then backdrops).
- Hard rules still hold: no tool-repo edits during a cold run, downloads and
  outward-facing actions (push, publish) still need a yes, and genuine taste
  calls are still shown as a tradeoff, not decided silently.

**2026-10-08, widened:** "keep safely chipping away at the roadmap, and make
the right decisions as you continue to iterate" -- after delegating the stage
("live or baked, whatever you think is the best"). Make the call, record why
with its measurement, and show the result in frames afterwards; ask only when
a choice is irreversible or outward-facing.

**2026-10-09, widened again, for the NEXT session:** "when we start again, I
want us to work contiously for as long as you can safely, we still have a lot
on the roadmap".
- **Next session:** start from [[open-work-2026-10-09]]'s queue and keep
  going block after block without pausing for a yes.
- **Taste calls:** ship the measured default and queue the question for the
  walker in the block summary. Do not stop the queue on it.
- **When the walker asks for a pause, honour it.** On 2026-10-09 it was
  "dont start another long task until we have a good pausing point". Then:
  finish the running step, clean up, commit, update notes, report.
- **"Safely" means the hard rules:**
  - no tool-repo edits during a cold run;
  - watch the disk (15 GB free on 2026-10-09; delete scratch copies when
    done);
  - nothing left running;
  - push, downloads and anything outward-facing still need a yes.

**2026-10-10, again, with budget:** "keep working on the roadmap, I want you to try to max out our usage limit before our reset tomorrow evening". So: no pausing for a yes, spend the budget on roadmap work, keep the hard rules.

**2026-10-13, corrected:** after I ended a block on a taste question ("is this the wall the comps meant?")
and stopped, the walker asked "why aren't you continuing to chip away at the roadmap?".
- A block summary may carry a question, but the turn does not END on it. Queue the question, then start
  the next chunk in the same turn.
- Stop only for a pause request, an irreversible or outward-facing action, or a decision the next chunk
  truly cannot proceed without. Even then, pick another chunk that can proceed.

**2026-10-14, corrected again:** I stopped after five blocks with "the rest is look work, it should wait
for the walker's eye on the frames"; the walker: "why did you stop?".
- Waiting for the walker's eye is NOT a stop condition, and neither is "it might be reworked". Queue the
  frames, build the next item anyway, and let the walker redirect by interrupting.
- Nor is the hour, the session's length, or a natural-feeling end. The only stops are the ones above.

**2026-10-19, widened: "keep chipping away at the roadmap safely and continously, make decisions that can be changed later".** The queued walker's calls are now mine to make, as reversible defaults:
- Make the call, put it behind ONE named dial (a constant, a profile flag, a family list), and write in the code, the changelog and the roadmap status that it is a call made on that date and meant to be changed, with how to change it.
- Prefer the option that moves nothing graded or shipped when the options are otherwise equal (244: crosswalks kept as built; 177: z-fight WARN now, block at zero).
- Still ask for anything irreversible or outward-facing beyond the established practice (root and tool-repo pushes of finished, tested commits have been routine since 2026-10-12).
