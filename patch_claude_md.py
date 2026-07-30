"""Write down what this pass cost, in the three places it belongs.

Four rules earned between the 20/20 sweep and the step gate going green. Each one
is here because not having it cost a measurement cycle, and three of the four are
refinements of rules already in the file rather than new ideas -- which is itself
the finding: the existing rules were right and not specific enough to fire.

1. GROUNDING gets the recovery procedure. The rule already says a staged file
   whose byte count disagrees with the device is not the file. It did not say what
   to do next, so the honest reading was "stop". lot.py and agent_contract.json
   both served stale bytes this session while their .pre_* backups staged clean,
   and applying the known patch scripts to a backup reproduced both live files to
   the byte -- 85,287 and 4,981, delta zero. That turns a hard stop into a
   five-minute detour, and it is worth writing down before the next time.

2. INSTRUMENTS gets the box-inflation trap. Allowing `margin` of slack on each of
   a polygon's own axes is a BOX inflation, not the set of points within `margin`
   of the polygon; near a corner it over-reports by up to sqrt(2)*margin. That is
   what put two sidewalk sections into LOT_STEP_BLOCKS_A_ROUTE whose exact
   clearance from the route was 3.43 m against a 3.00 m half-width. Same family as
   the polygon centroids and the level line already listed there.

3. A NEW SECTION for the two that have no home yet: attribute every item in a
   gate's output before patching it, and treat an unused parameter as an
   unfinished thought.

Asserts each anchor, refuses to write on a miss, idempotent.
"""
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
MD = ROOT / "CLAUDE.md"

# --- 1. grounding: how to recover, not just when to stop --------------------

GROUND_ANCHOR = """`patch_*.py` scripts must keep asserting their targets and refusing to write on a
miss. That guard is the backstop, not the plan.
"""

GROUND_ADD = """`patch_*.py` scripts must keep asserting their targets and refusing to write on a
miss. That guard is the backstop, not the plan.

**When the bridge poisons one path, reconstruct rather than stop.** The staleness
is per-path, not global: `lot.py` served 68,904 bytes against a reported 85,287
while `lot.py.pre_accessor` staged clean at 83,419 in the same call, and
`agent_contract.json` served 1,811 against 4,981 while `_bridge/ac_0729b.json`
was correct. Every `patch_*.py` in the root records the exact before-and-after
text it applied, so the live file can be rebuilt from the nearest clean backup
plus the patches that followed it — and the rebuild is *verifiable*, because a
byte count that lands exactly on the device's figure is not a coincidence at four
significant figures. Both files above reconstructed to delta zero. Do that before
declaring a file unreadable; ask only when no clean ancestor exists.
"""

# --- 2. instruments: a margin per axis is a box, not a radius ---------------

INSTR_ANCHOR = """- A capsule resting exactly on a surface registers as an overlap in
  `intersect_shape` — there is no epsilon. Use a ray when the question is "what
  is the floor here"; use a shape when the question is "does a body fit".
"""

INSTR_ADD = """- A capsule resting exactly on a surface registers as an overlap in
  `intersect_shape` — there is no epsilon. Use a ray when the question is "what
  is the floor here"; use a shape when the question is "does a body fit".
- **A margin allowed per axis is a box, not a radius.** Adding `margin` to each
  side of a separating-axis test inflates a polygon along its own axes, which
  over-reports near a corner by up to `sqrt(2) * margin`. `site_steps._point_in`
  did exactly that and reported two sidewalk sections as blocking a route whose
  exact clearance to them was 3.43 m against a 3.00 m half-width. Keep the
  projection test as a cheap reject — it is a superset, so it cannot produce a
  false negative — and decide with a real point-to-edge distance.
"""

# --- 3. two new rules -------------------------------------------------------

NEW_SECTION = """
## Attribute every item in a gate's output before patching it

`LOT_STEP_BLOCKS_A_ROUTE` reported 7 transitions on one site and read like one
defect with one number wrong. It was three: 4 were the kerb cut being the width
of the path rather than of the crossing, 2 were the gate over-reporting at a
polygon corner, and 1 was a slab thickness 17 mm over the walk limit. Fixing only
the obvious one would have left 3 findings after a 58-minute sweep and looked like
the fix had not worked.

Splitting the count first cost ten minutes and saved two sweeps. So: before
writing a patch against a gate's output, account for every item in it, and check
each fix against the count it is supposed to remove. Isolating them is cheap —
running the patched checker against the *old* scene showed 7 → 5, confirming the
instrument fix alone owned exactly 2, before any geometry moved.

Where a fix cannot be isolated, say which items it is *assumed* to cover, so the
residue after the next run is diagnostic rather than a surprise.

## An unused parameter is an unfinished thought

`_kerb_crossings` has accepted the kerb band's depth since it was written and
never read it. Whoever wrote that signature knew the depth mattered to the answer
and stopped before using it — and the crossing width was wrong by up to 5.99 m as
a direct result. Grep for parameters nothing reads; each one is somebody's
abandoned intent, and it is usually the missing term in the formula immediately
below it.

The same applies to a knob with no effect (see the null-result rule above) and to
a code path that cannot fire: `python site_steps.py <scene>` never passes
`site_spec`, so `on_route` is always empty and the only major finding it has is
unreachable from the CLI. A check that cannot fail is indistinguishable from one
that passed.
"""


def main() -> int:
    if not MD.exists():
        raise SystemExit(f"missing {MD}. Nothing written.")
    src = MD.read_text(encoding="utf-8")
    original = src
    done, skipped = [], []

    for label, anchor, replacement, sentinel in (
        ("Grounding: reconstruct a poisoned path rather than stopping",
         GROUND_ANCHOR, GROUND_ADD, "reconstruct rather than stop"),
        ("Instruments: a margin per axis is a box, not a radius",
         INSTR_ANCHOR, INSTR_ADD, "is a box, not a radius"),
    ):
        if sentinel in src:
            skipped.append(label)
            continue
        if src.count(anchor) != 1:
            raise SystemExit(f"{label}: anchor appears {src.count(anchor)} "
                             f"time(s), expected exactly 1. Read CLAUDE.md "
                             f"rather than forcing this. NOTHING WRITTEN.")
        src = src.replace(anchor, replacement)
        done.append(label)

    if "## Attribute every item in a gate's output before patching it" in src:
        skipped.append("two new sections (attribution, unused parameters)")
    else:
        src = src.rstrip("\n") + "\n" + NEW_SECTION
        done.append("two new sections (attribution, unused parameters)")

    if src == original:
        print("CLAUDE.md: already carries all four rules. Nothing written.")
        return 0

    backup = MD.with_suffix(".md.pre_rules")
    if not backup.exists():
        backup.write_bytes(MD.read_bytes())
    MD.write_text(src, encoding="utf-8")

    print("CLAUDE.md:")
    for line in done:
        print(f"  added   {line}")
    for line in skipped:
        print(f"  present {line}")
    print(f"  {len(original)} -> {len(src)} characters; previous file kept at "
          f"{backup.name}")
    heads = [l for l in src.splitlines() if l.startswith("## ")]
    print(f"\n  sections now ({len(heads)}):")
    for h in heads:
        print(f"    {h[3:]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
