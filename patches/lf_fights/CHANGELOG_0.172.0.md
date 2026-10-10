## [0.172.0] - The walk's visual check fails a fight, not a sparkle

**Roadmap 225.** 0.171.0 let the walk preview's shot bot see again. Seeing,
it failed two of cold run 9222's interior stations on jitter, 3.60% and
2.33%, and said coplanar surfaces were fighting. Mapped pixel by pixel, every
change was scattered over the drop ceiling's acoustic tiles, a wall and a
floor. Nothing flipped as a face. That is texture sparkle, a sub-pixel blend
of one texture, which the share of changed pixels cannot tell from a fight.

### What separates them, measured

**The control.** Two quads, red and blue, 0.01 mm apart: a real z-fight, as
a scene.

| on the shot bot's sampled grid | the control | 9222's five stations |
|---|---|---|
| share of samples that change by more than 12 | 2.02% | 0.01% to 3.64% |
| median change | 255 | 16 to 19 at the four interiors; 42 at the exterior, over its 7 changed samples |
| changes over 64, as a share of the frame | 2.02% | 0.00% to 0.12% |

**Why the size of the change separates them.** A pixel that z-fights swaps
between two surfaces' colours. One that sparkles shifts by a blend of one
texture.

**Two designs were refuted on the way.** Both are kept in the factory's
`docs/findings/shotbot_sparkle/`:
- **Judge the largest connected region of change.** The control's fight broke
  into regions of at most 54 samples, and the sparkle's of 28. A gate at 64
  passed the control.
- **Move the near plane instead of the camera.** That leaves every pixel's
  texture sample in place, so it cannot sparkle, but it flipped 0 samples on
  the control as well.

### What it is now

`shot_bot.gd` counts a **fight**: a sampled pixel that changes by more than
`FIGHT_DELTA`, 64 of 255.
- **The verdict.** A station fails when fights pass `FIGHT_FAIL_PCT`, 0.5% of
  the frame. The control is at 2.02% and 9222's worst at 0.12%, a margin of
  about four times either side.
- **What is still reported:** every change over `DIFF_TOL`, as `jitter_pct`,
  as before.
- **Sparkle.** A station whose small changes pass 2.0%, with fights under the
  gate, is noted as sparkle and never failed. 2.0% is the number that used to
  be the verdict.
- **The summary line** reads, for example: `jitter 3.64%, fighting 0.12%,
  void 0.0%  (sparkle: small flips of one texture, not a fight)`.

**Measured on 9222's preview with `mission.tscn`:**
- all five stations pass;
- Ladder_ladder_0_base and Ladder_ladder_1_top are noted as sparkle (jitter
  3.64% and 2.33%, fighting 0.12% and 0.03%);
- the control fails, fighting 2.02%.

**What it no longer catches: a fight between two surfaces within 64 of each
other.** That is a near-invisible fight, and the trade is that a texture
cannot fail a station by shimmering.

### Tests
`tests/unit/test_shotbot_fights.py`, 5. The script needs a display, so it is
read here, and the runs above are what proved it:
- a fight is a flip over 64, failing past 0.5%, and the old count is gone;
- the verdict reads fights, not every change;
- the gate sits between the measured control and the worst sparkle;
- the summary names fighting and notes sparkle;
- a verdict from before 0.172.0 still reads. A control, and it passes on
  0.171.0 too.

On 0.171.0 the other four fail.

Suite: 2,153 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.171.0 gave
2,147. The 5 tests here account for 5 of the 6. The sixth is
`test_sibling_locator`'s guard, which runs once per `.py` in the repo: 316
cases on 0.171.0 and 317 here.
