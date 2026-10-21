---
name: stanchions-indoors-barricades-outdoors
description: "walker 2026-10-20 -- steel crowd barricades are outdoor/police kit; indoor queues (box office, bank) use retractable-belt stanchions"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-21T04:10:38.418Z
---

Steel crowd-control barricades (Zoo `crowd_barrier`) belong OUTDOORS -- "metal barriers are for outdoor concerts or riot protection from police". Indoors, a queue is lined with RETRACTABLE-BELT STANCHIONS -- "stanchion or stanchions are likley more common for banks and indoor common areas" -- black posts on round weighted bases, a flat black belt taut at waist height, lanes switching back in front of a desk (the walker's photo, 2026-10-20). Asked what arena_a02's barricades were for, the walker chose "queue lanes to the box office".

**Why:** a prop has to make sense where it stands; four steel barricades in a line across an arena's indoor event floor answered no question a visitor would ask.

**How to apply:** an indoor queue is Zoo 1.119.0's `stanchion_run`, laid by Deli Counter 0.243.0's `ticket_queue` (generator logic, never hand-placed); a barricade line waits for Lot to know where a crowd or a cordon stands (roadmap 273). Before placing any crowd-control prop, ask what crowd it controls and whether it is inside or out. Banks' teller lines get one too since Deli Counter 0.244.0 (roadmap 275 CLOSED); a queue is circulation, not furniture -- furnish does not count its runs. Related: [[detail-lives-in-generator-logic]], [[game-is-a-series-of-shooting-galleries]].
