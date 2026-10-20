---
name: two-names-one-building
description: "A building's street band (LF/Pixelcoat) and door box (Zoo) named it from two tables; walker 2026-10-06 chose A (Zoo's door-box names on both), FLAPPAHS cream on green; shipped and proven in cold run 9185 (roadmap 187 CLOSED); far fabric went blended, not a card"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T18:04:52.415Z
---

Found 2026-10-06 while measuring the strip club's identity
(`docs/findings/two_names_one_building/`, roadmap 187).

**The two signs:**
- The band: Lot hangs it on the street face, and Level Factory deals it
  from Pixelcoat's sign profile.
- The door box: Deli Counter places it, and Zoo `storefront_names` names it.
- Of the 95 library shells with a door box, the band's pool held the door's
  name for 6.

**Shipped:**
- Option D: LF 0.147.0, "a band names a shop". 68 of 148 shells keep a
  band.
- Zoo 1.76.0: a retail strip is not a strip club.

**The walker's decisions, 2026-10-06:**
- **Option A:** "Agreed". One name list on both signs, the door-box list,
  because it is written to the Delco-slang brand rule.
- **FLAPPAHS colours:** "We can do the green and cream". The brand is
  cream on green, Zoo's colourway 0, and Pixelcoat's red band changes to
  match.
- **The far fence fabric:** the walker leaned to "a second, distant
  version of the fabric".
  - My cost answer: with visibility ranges the near and far fabric swap, so
    a fence still draws steel plus one fabric.
  - Worst case is +1 draw, only during the hand-off fade.
  - The far card is one translucent quad in the transparent pass.

**Shipped, same day:**
- **A:** Pixelcoat 0.61.0 is the one name list (shop families hold Zoo's
  door names, mirror-tested). LF 0.148.0 deals one business a shell and
  hands its pack to the fixtures job. Zoo 1.79.0's door box wears it.
- **Green:** Pixelcoat 0.60.0 draws FLAPPAHS in Zoo's colourway 0,
  mirror-tested.
- **Fence:** BLENDED fabric (Zoo 1.78.0, Pixelcoat 0.60.0), not a far card.
  The card failed in frames, because visibility ranges switch a whole node
  and a long run seen along its length is one node.
- **Proven:** cold run 9185 (restaurant_row_001), 0 interventions.
  deli_a01's band and door box both say SCRAPPLE & SONS DELI, in the
  package. Roadmap 187 CLOSED (root commit e8a45a8, local, not pushed).
- FLAPPAHS green has not yet been seen in a cold run: 9185 drew no gas
  station or store.

**Why it matters:** two names on one building is the clearest "reads as
generated" defect found by measurement rather than by eye (roadmap 18).

**How to apply:**
- One decider (Level Factory, which knows the street and its no-repeat
  rule) picks each building's name from one table.
- The band and the door box both render that choice.
- Any copy of the list must be held equal to it by a mirror test.

Related: [[detail-lives-in-generator-logic]], [[fake-delco-brands-funny-and-crass]],
[[authorship-guide]], [[fence-marks-the-playable-edge]].
