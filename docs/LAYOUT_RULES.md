# LAYOUT_RULES — real-architecture guard rails for heist shells (v1)

Research-derived rules that make generated buildings read as real places AND
provably-fun FPS spaces. Each rule states WHERE it is (or will be) enforced:
`[gate]` an existing engine/offline gate already covers it, `[lint]` checked by
`deli_counter/layout_lint.py` (new, this doc's executable half), `[template]`
enforced by construction in the spec factories, `[todo]` identified gap.

## A. Egress & circulation (IBC-derived, gamified)

Real codes force the shapes players subconsciously expect. Numbers below are
IBC Chapter 10 rules of thumb (sprinklered commercial), used as *readability*
targets, not legal compliance.

- **A1 Two ways out.** Any room a player can occupy needs 2 independent exits
  once it's more than ~7 m deep (real: common path of egress limit 75-100 ft).
  Objective rooms already require 2 openings to different neighbors `[gate:
  PVP-ROUTES]`; A1 extends the *check* to every large room `[lint L1]`.
- **A2 Building exits.** Every building: ≥2 exterior exits on ≥2 different
  faces (real: >49 occupants → 2 exits). `[lint L2]`
- **A3 Travel distance.** From any room, the room-graph path to an exterior
  exit stays under ~60 m (real: 200-250 ft exit access travel). Long-travel
  rooms are where players feel "trapped in a maze". `[lint L3]`
- **A4 No deep dead ends.** A connector/corridor room with a single opening
  reads as a mistake beyond ~6 m (real: 20 ft dead-end corridor limit) — in
  PvP it's a kill-box with no counterplay. `[lint L4]`
- **A5 Door and corridor minimums.** Doors ≥1.25 m (our nav contract already
  exceeds the real 32 in clear) `[template R1 + gate: nav]`.

## B. The secure chain (banks, casinos, vaults)

Real money rooms sit behind LAYERS, and players read that instantly.

- **B1 Public → staff → secure, never public → secure by door.** No standard
  door connects a `public_entry` room directly to an `objective_room`. A
  *breach* may (that's the heist fantasy: attackers MAKE the illegal path);
  a door may not (real banks put the vault behind the teller line + a
  controlled corridor; casinos put the count room behind the cage with
  multi-person access). `[lint L5]` — current ground_west venue template
  violates this (hall→secure door added for route redundancy); fix is to
  route the second access through the service band `[todo: p4lib v2]`.
- **B2 Vault walls are never the front wall.** Objective rooms don't touch
  the wall face holding the main public entry. `[lint L6]`
- **B3 The cage faces the floor.** Bank teller lines / casino cages sit on
  the seam between public hall and staff band with sightlines INTO the hall
  (defender anchor logic — this is why defender spawns live there). `[template
  p4lib DFD placement]`

## C. Reading as a real building (signature moves per family)

One or two spatial moves make a type legible from inside:

- **C1 Public halls are TALL.** Banking halls, market halls, terminals,
  concourses: 1.3-2× the height of their back-of-house. Our venues carry
  sh 4.6-6.5 vs standard 3.0-3.6 `[template]`; lint warns when a
  `public_entry` room lives on a story under 4.2 m in a civic/venue family.
  `[lint L7]`
- **C2 The program must exist.** A bank without a teller zone is a box. Per
  family, lint warns when the signature rooms/props are absent: bank →
  teller band + vault; casino → cage + count; market → stall grid; terminal
  → check-in + baggage band; station → fare hall + money room. `[lint L8,
  by room id/role vocabulary]` — the deeper fix is Zoo interior prop passes
  (teller_line, vault_door, safe_deposit_boxes species) `[todo: art pass]`.
- **C3 Service face ≠ public face.** Loading docks, crew doors, and roof
  ladders live on non-public faces. `[template p4lib garage/E-service]`

## D. Combat-space rules (FPS canon, on top of the pvp gates)

- **D1 3-4 chokepoints, one per lane; no single point covers all of them.**
  Site-level `[gate: lot approach routes]`; building-level proxy: objective
  openings must not all be visible from one room `[gate: PVP-ROUTES
  different-neighbors]`.
- **D2 Err on less cover; never repeat identical waist-high boxes.** The
  Level Design Book's "cover boxes" anti-pattern is EXACTLY a uniform
  rowbank(): lint warns when ≥4 volumes share identical dims in a line —
  vary dims/height/rotation instead. `[lint L9]` — current venue specs
  trip this on purpose-built slot banks/stalls; vary them in v2. `[todo]`
- **D3 Corners: bevel where you want wide fights, keep sharp where you want
  safe rotations.** Module-level concern → Zoo wall corner variants
  `[todo: art pass]`.
- **D4 Flanks are optional, risk-priced.** Roof ladder + breach walls are the
  flank budget; every objective needs a main door path AND a priced
  alternative `[gate: PVP-ROUTES + R4 ladders]`.

## E. Where each layer enforces

```
brief/spec authoring   p2lib/p4lib templates  (R1-R6, tall-stair, B3, C1, C3)
offline spec gate      validate.py + audit_specs + layout_lint.py  (A*, B*, C2, D2)
engine gates           nav_gate / godot_gate / walktest / mp_smoke  (traversal truth)
site gates             lot.py pvp gates  (spawn separation, approaches)  (D1)
art pass               zoo/patina/pixelcoat/lux  (C2 props, D3 corners)
orchestration          level_factory  (locks + regression: collision/anchors/routes)
```

## Sources

IBC egress numbers: [meltplan IBC means-of-egress summary](https://www.meltplan.com/buildingcodes/ibc/means-of-egress),
[ICC IBC Ch.10](https://codes.iccsafe.org/content/IBC2021P2/chapter-10-means-of-egress),
[UpCodes §1006](https://up.codes/s/number-of-exits-and-exit-access-doorways).
Bank branch planning: [Design Collaborative branch models](https://designcollaborative.com/banking-branch-models/),
[The Financial Brand on teller placement](https://thefinancialbrand.com/news/banking-branch-transformation/why-tellers-belong-in-the-back-of-branches-13219),
[Steelcase retail banking](https://www.steelcase.com/spaces/designing-retail-banking-spaces/).
Casino cash spine: [Hospitality Ops Intel casino vault/cage/count](https://hospitalityopsintel.com/hospitality/casino-vault-technology/),
[NV Gaming surveillance standards](https://www.gaming.nv.gov/siteassets/content/home/features/Regulation5SurveillanceStandards.pdf).
FPS combat spaces: [The Level Design Book — map balance](https://book.leveldesignbook.com/process/combat/balance),
[WoLD chokepoint principles](https://www.worldofleveldesign.com/categories/csgo-tutorials/csgo-principles-choke-point-level-design.php),
[GameDeveloper on competitive FPS layouts](https://www.gamedeveloper.com/design/analyzing-level-layouts-to-improve-level-design-in-competitive-fps).
Dimensional reference: [Neufert Architects' Data](https://www.uceb.eu/DATA/CivBook/03.%20Architect_s%20Data.pdf).
