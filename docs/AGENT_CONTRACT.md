# The Agent Contract — character sizes and everything derived from them

**Status: ratified (values = the Phase 0 shakedown's proven numbers).**
The body-metrics sibling of `COORDINATE_CONTRACT.md`. One file —
`deli_counter/agent_contract.json` — owns every character dimension and every
clearance derived from it. Change a body there, re-run the gates, and every
validator, bake, and walktest agrees. Nothing hardcodes a body size anymore;
every consumer carries a fallback equal to the ratified values, so a missing
file degrades gracefully instead of breaking the pipeline.

## Why this exists

The engine-gate shakedown proved these numbers interlock in non-obvious ways:
a 0.4 m nav agent at 0.25 m voxels silently erodes 1.0 m of every doorway
(erosion is `ceil(radius/cell)` whole cells per side), fragmenting legal
buildings into disjoint navmesh islands. Door width, agent radius, and bake
cell size are ONE decision, not three.

## The knobs (deli_counter/agent_contract.json)

| Section | What it owns |
|---|---|
| `characters.player` | capsule radius/height, eye height, crouch, max step-up, walk speed |
| `characters.npc_*` | per-class NPC bodies (cops share player metrics until a distinct class ships) |
| `nav_bake` | agent radius/height, max climb, max slope, cell size/height for every navmesh bake |
| `clearances` | minimum door width, corridor width, headroom — WITH the derivation formula recorded |
| `qa` | walktest arrival radius, stuck timeout, snap tolerance, walker capsule |
| `review` | character-reference height, gameplay-camera eye height |

## The derivation rules (keep these true when you change a body)

1. `nav_bake.agent_radius_m` ≥ fattest navigating character radius + 0.05.
2. `clearances.min_door_width_m` ≥ `2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size`.
   Widening the character means widening doors OR shrinking bake cells.
3. `nav_bake.agent_max_slope_deg` > steepest legal stair pitch (~45°) with
   headroom — slope *legality* is validate.py's job; the bake only needs to
   accept what validate approves.
4. `nav_bake.agent_max_climb_m` ≥ max step rise (guards.py STEP-RISE budget).
5. `qa.arrive_dist_m` > anchor float height (markers sit ~1 m above the mesh;
   arrival is measured horizontally for exactly this reason).

## Who reads it

- **deli_counter**: `agent_contract.py` (loader) → `navigability.py` door/agent
  thresholds; `nav_gate.py` passes `DC_NAV_*`/`DC_QA_*` env into
  `nav_gate.gd` (which falls back to ratified constants).
- **lot**: `lot.py::_agent()` (searches `$DC_AGENT_CONTRACT`, then the
  deli_counter sibling repo) → walk + nav-QA scene bake parameters;
  `walktest.py` bridges the env into `nav_qa_director.gd`.
- **review/renders**: character reference + eye heights.
- **Deli Counter specs**: authors own their door widths, but the validator
  enforces `clearances.min_door_width_m` — the reference spec's 1.25 m doors
  came from this contract.

## Changing a character size — the checklist

1. Edit `deli_counter/agent_contract.json` (body + re-derive rules 1–5).
2. `python deli_counter/validate.py --all` — narrow doors/corridors surface
   here first, as offline findings.
3. Rebuild affected shells, then the engine gates: `nav_gate.py --all`,
   `godot_gate.py --all`, `walktest.py`, `mp_smoke.py`.
4. If doors had to widen: fix the SPECS (the offline validator names them),
   never the tolerance.
5. Re-certify the factory set and bump pins as usual.

Distinct NPC classes larger than the player (heavies, dozers) get their own
`characters.npc_<class>` entry, and `nav_bake.agent_radius_m` moves up to the
fattest navigator — which cascades to doors via rule 2. That cascade being
*visible in one file* is the whole point.
