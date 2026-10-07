# Dynamic Walkable City and Level Design Brief

## Purpose

Give an AI city planner a repeatable method for creating compact, believable, highly playable 3D city levels. The generator must make places that feel like parts of a real settlement while giving players memorable choices about where to go, how to get there, and what height or exposure to accept.

This brief is for authored, game-sized districts—not accurate full-scale city simulations. It is designed for a 1990s Delco / southeastern Pennsylvania heist game, but its planning rules can be adapted to other settings.

## Design intent

Create a legible **hub-and-spoke place**:

- A strong destination or activity center gives the level a reason to exist.
- Nearby buildings and public spaces support, feed, overlook, service, or contrast with that center.
- Streets and paths form a connected network that brings players toward the hub from more than one direction.
- Side routes, interior connections, alleys, stairs, ramps, overpasses, and upper floors create meaningful choices.
- The surrounding district continues beyond the playable routes so the level feels embedded in a larger city.

“Hub and spoke” describes the spatial logic, not a literal wheel. Do not make every route a dead-end ray aimed at a central building. Join spokes with cross streets, alleys, courtyards, building interiors, or upper-level paths so players can loop, flank, retreat, and discover alternate approaches.

## The city must satisfy two tests

### It makes sense as a place

Every building, gap, route, and height change has a plausible reason. Land pressure, parcel history, terrain, transportation, access, ownership, and building use shape the layout. A business needs customers and deliveries; a residence needs a front door and a private edge; an industrial site needs room to operate. Open land has a role such as sidewalk, yard, loading, parking, drainage, garden, rail, vacant parcel, or public space.

### It plays as a level

The main goal is easy to understand from the street and map. Players can read where they are, recognize useful landmarks, and predict some consequences of a route choice. Routes differ in exposure, distance, height, cover, visibility, or access—not just decorative shape. Shortcuts have a cost, restriction, risk, or discovery requirement that makes them interesting.

A layout that passes only one test is incomplete. Realistic buildings with no meaningful movement are scenery. A maze of arbitrary gameplay corridors does not feel like a city.

## Spatial planning order

Generate from large relationships toward detail. Do not scatter buildings on an empty plane and connect them afterward.

1. **Establish the site.** Set the playable boundary, surrounding context, terrain, drainage, transport lines, existing streets, and off-limits areas.
2. **Choose the district structure.** Identify the center, edges, land pressure, era, dominant uses, and development history. Define at least one transition into adjacent districts.
3. **Place the level anchor.** Choose the primary score target or other destination. Define why it is here, what approaches it needs, and what can be seen from or into it.
4. **Build the movement graph.** Place primary streets and pedestrian routes, then secondary connections, service routes, and vertical links. Confirm routes work before fixing building footprints.
5. **Divide blocks into parcels.** Respect frontage, access, lot rhythm, existing alignments, and support space. Use the existing Land Pressure and Spatial Logic guidance for parcel allocation and open-space roles.
6. **Assign compatible neighbors.** Place support, complementary, contrasting, and buffer uses around the anchor according to their shared needs and conflicts.
7. **Fit building mass and playable floors.** Assign footprint, height, entrance locations, interior access, and service areas inside each parcel.
8. **Add controlled history.** Apply conversions, additions, vacancy, infill, demolition, or lot consolidation as coherent local patterns—not independent random effects.
9. **Dress, light, and extend the backdrop.** Add signs, vehicles, utilities, vegetation, clutter, and distant massing only after they respect routes and use.
10. **Run traversal and plausibility reviews.** Repair the smallest failing area, then recheck all affected connections.

## Place grammar: hub, spokes, loops, and edges

### 1. Hub

The hub is the district’s strongest functional and visual anchor. It may be a bank, pharmacy, market, courthouse, rail station, bar, factory, plaza, or other destination.

The planner must define:

- **Reason for location:** intersection, transit access, customer base, waterfront, industrial access, historic parcel, or another clear cause.
- **Approach sides:** which faces are public, service-facing, private, restricted, or visually exposed.
- **Visibility:** where the hub is visible, partially visible, or hidden. Use signs, rooflines, street bends, trees, and building mass to reveal it in stages.
- **Operational space:** entrances, deliveries, trash, parking or curb access, emergency access, and any heist-specific access points.
- **Play role:** destination, landmark, encounter space, objective area, or social center.

The hub need not be centered geometrically. It should be central in the level’s movement and activity logic.

### 2. Spokes

Give the hub at least three distinct approach routes when the level’s footprint allows it. Each route should have a clear identity and a reason to exist. Examples include a commercial main street, a residential side street, an alley/service lane, a transit or rail edge, a parking approach, or an elevated connection.

For each spoke, state:

- Start and end nodes.
- Approximate travel distance and travel time at the project’s normal player movement speed.
- Exposure, cover, sightlines, and likely points of observation.
- Height changes and access requirements.
- What activity or building fronts the route.
- What makes it meaningfully different from the other approaches.

Spokes should not be cosmetic duplicates. If two routes have the same distance, visibility, cover, and access, merge them or give one a distinct purpose.

### 3. Cross-links and loops

Connect spokes away from the hub to make the district feel walkable and allow meaningful rerouting. Use cross streets, mid-block passages, alleys, courtyards, shared lobbies, stairs, ramps, bridges, or connected upper floors where plausible.

The planner should create:

- At least one short loop around or near the hub.
- At least one longer route that bypasses the most exposed area.
- At least one optional shortcut with a readable cost or condition.
- More than one way to recover from a blocked or unsafe route, unless the mission deliberately imposes a temporary lock.

Dead ends are allowed when they serve a purpose: a loading yard, cul-de-sac, fenced lot, rooftop access, or risk/reward branch. Label them as intentional and give the player a reason to enter or a clear reason to avoid them.

### 4. Edges and transitions

A believable level has different conditions at its edges. Transition from active frontage to residential, industrial, rail, highway, woods, water, or lower-density land in a way that explains the change. Avoid clipping a dense street grid at the map boundary without a road continuation, wall, grade change, rail corridor, construction edge, or visual backdrop to explain it.

Extend street directions, roof rhythms, utility lines, terrain, and district silhouettes into the non-playable world. Distant massing should reinforce where the player is and where the city continues.

## Verticality with a reason

Verticality is a usable route and a change in how players understand or control space. Do not equate it with making every building tall.

Use three connected layers where suitable:

| Layer | Common functions | Design questions |
| --- | --- | --- |
| Street and ground | Entrances, storefronts, sidewalks, service yards, parking, underpasses | Can players read the main route and move between front and back? |
| Raised or below-grade | Stairs, balconies, fire escapes, bridges, ramps, rail embankments, basements, tunnels | Who built or uses this connection? Is it reachable, visible, and safe to traverse? |
| Upper floors and roofs | Apartments above shops, offices, overlook positions, rooftop access, vertical objective routes | What is visible from here? How does a player enter and leave? |

Vertical connections must join actual route nodes: stairs land on a sidewalk or floor; ladders have a reachable top and bottom; bridges have approaches; doors connect to usable interiors. Do not create isolated balconies, inaccessible rooftops, stairs that terminate into walls, or floors with no circulation logic unless they are deliberately blocked and labeled.

Use height to create choices: a higher route may improve sightlines but expose the player; a basement may provide concealment but reduce exits; an elevated crossing may shorten travel but have limited cover. Give players readable cues before committing to a route.

Prefer a few purposeful height changes across a compact district to uniform elevation noise. Tie steps and ramps to topography, infrastructure, building types, accessibility, or construction history. Include ramps or alternate routes where the intended experience requires them.

## Building relationships and adjacency logic

Assign every building a use, activity level, access needs, public/private status, height role, and relationship to nearby uses. Neighbors should share a practical reason to be near one another or create a deliberate contrast.

### Useful adjacency patterns

| Anchor or district | Nearby uses that make sense | Spatial connection |
| --- | --- | --- |
| Bank or score target | Shops, offices, apartments, ATM, parking, bus stop, civic services, alley, service access | Prominent street frontage plus less-visible delivery or back access |
| Main-street business | Other shops, apartments above, small plaza, side-street services, loading alley | Continuous pedestrian frontage; goods reach rear or curb access |
| Grocery or market | Small retail, housing, transit stop, parking, loading area, waste enclosure | Customer access in front; service access separated where possible |
| Bar or restaurant | Other evening uses, apartments, parking, taxi/curb space, lit side street | Visible entrance; quieter residential edge buffered by distance or mass |
| Industrial or warehouse site | Rail or truck access, repair shop, storage yard, workers’ services, utility corridor | Larger parcels and service routes; buffer noisy or hazardous activity |
| Transit node | Retail, ticketing, civic services, dense housing, taxi/parking, pedestrian routes | Multiple approaches and a clear public forecourt or platform connection |
| Residential block | Small corner shop, school/church, park, garage, bus stop, local services | Quieter streets, direct front doors, yards, and transitions to busier uses |

These are patterns, not fixed recipes. Apply local history and era. A vacant building may remain beside active businesses because it was part of the same commercial row; do not scatter vacancies randomly across all zones.

### Adjacency rules

- Put uses together when they share customers, workers, deliveries, transport, utilities, or services.
- Separate or buffer uses that conflict in noise, privacy, safety, traffic, or operating hours.
- Give public uses a legible approach and private or service uses a less prominent one.
- Place entrances on routes that their users would actually take. A front door should face a street, court, or clear path; a loading door should meet a service route.
- Use building form to show relationships: attached storefronts, shared walls, apartments above retail, rear yards, service alleys, fenced operational sites, or a deliberate setback.
- If two neighboring uses seem unrelated, create a transition parcel, explain their shared history, or move one.

## Game-like density and landmarks

Generate at the scale of player attention, not real-world census data. Use compression carefully: shorten uninteresting travel while preserving the cues and transitions that make the district coherent.

Create a hierarchy of landmarks:

1. **Primary:** hub or score target, visible from several routes.
2. **Secondary:** distinctive corner business, church, water tower, transit structure, sign, or elevated feature that helps orientation.
3. **Local:** storefront sign, mural, parked vehicle, utility pole cluster, doorway, or yard feature that confirms the player’s immediate location.

Do not make every building equally prominent. Keep some facades quiet, repeat ordinary forms where a real block would repeat them, and reserve contrast for places that matter. Use bends, building height, signs, lighting, and view corridors to reveal landmarks in sequence instead of showing everything at once.

The city can feel larger than its traversable footprint through converging roads, partial views, distant blocks, traffic sound, rail infrastructure, skyline silhouettes, and contextual buildings beyond the playable boundary. Do not promise access to a visible space unless it is reachable or clearly reads as backdrop.

## AI planner input contract

The planner should accept structured constraints and return an inspectable plan, not only a rendered layout.

### Required inputs

- `level_id`, `seed`, `generator_version`, `asset_catalog_version`
- `setting`, `era_profile`, `district_archetype`, `development_history`
- `playable_boundary`, `backdrop_boundary`, `terrain`, `infrastructure`, `exclusions`
- `anchor_use`, `anchor_location_or_zone`, `anchor_play_role`
- `building_count_band`, `enterable_building_count_band`, `height_range`
- `player_speed`, `target_traversal_time`, `mission_entry_points`, `mission_exit_conditions`
- `land_pressure`, `car_dependence`, `service_intensity`, `vacancy_level`, `maintenance_level`, `historical_persistence`
- `performance_budget`, `accessibility_requirements`, `required_path_types`

Treat numeric values as authored project constraints or starting points, not universal real-world facts. Reuse district archetype controls and parcel/open-space accounting from the Land Pressure and Spatial Logic specification.

### Required outputs

Return a versioned spatial plan containing:

- District zones and the reason each zone exists.
- Street/block/parcel geometry with stable IDs, frontage, access, and assigned open-space uses.
- Building records with use, massing, height, entrances, accessible floors, service areas, neighbors, and adjacency reasons.
- A traversable route graph with nodes, edges, width, slope/height change, traversal estimate, visibility/exposure tags, access rules, and blocked-state behavior.
- Landmark and view-corridor placements.
- Playable and non-playable boundary treatment.
- Metrics, warnings, and unresolved conflicts.

### Example route edge

```json
{
  "edge_id": "alley_to_rooftop_stair_02",
  "from_node": "rear_alley_midblock",
  "to_node": "office_roof_access",
  "type": "exterior_stairs",
  "public_access": false,
  "access_rule": "door_unlocked_after_alarm",
  "traversal_seconds": 7,
  "height_change_m": 4.2,
  "visibility_tags": ["overlooks_score_target", "exposed_from_main_street"],
  "cover_tags": ["partial_wall_cover"],
  "design_reason": "Service stair retained from the building's former warehouse use"
}
```

This is an illustrative data contract, not an engine API. The level tool may choose a different schema if it preserves the same information.

## Validation gates

### Hard failures

- The primary hub has no clear playable approach or no functional relationship to its parcel and neighbors.
- A required route is disconnected, unreachable, or terminates at invalid geometry.
- A vertical connection does not join usable spaces at both ends.
- Required building entrances, service areas, or mission entry/exit points lack access.
- A route or entrance violates a declared accessibility or gameplay requirement.
- Buildings block required routes, sightlines, or reserved service clearance.
- Parcels contain unexplained leftover area or incompatible overlapping uses.
- The playable edge ends without a credible transition or boundary explanation.

### Design warnings

- All routes converge into one chokepoint without a stated gameplay purpose.
- Every spoke is a dead end or every route has the same tactical profile.
- The hub is hidden from all approaches without an intended reveal sequence.
- Vertical features are decorative, disconnected, or offer no meaningful choice.
- Buildings have no entrance orientation, service access, or plausible neighbor logic.
- Building height, spacing, or frontage varies independently without district-level pattern.
- Density, maintenance, vacancy, and wealth have been treated as the same control.
- The map relies on long blank walks, repeated identical blocks, or unexplained open parcels.
- A distant landmark implies access that does not exist.

### Traversal review

For every mission entry point and the hub, test at minimum:

- Fastest route.
- Safest or least-visible route.
- Most elevated route, if present.
- Service/alley route, if present.
- One alternate route after a selected edge is blocked.

Record distance, estimated time, height changes, exposure, bottlenecks, and route affordances. Review from player eye level, not only in a top-down view. Then inspect the plan from above to check network connectivity and block structure.

## Example district seed: borough main-street score

**Anchor:** A small local bank branch on a prominent corner, built into a two- or three-story commercial block.

**Supporting neighbors:** A check-cashing or insurance office, barber or deli, apartments above shops, a bus stop, a small parking lot or curbside spaces, and a service alley behind the commercial row.

**Contrast and transition:** A quieter residential side street begins one block away. A former light-industrial parcel or rail edge explains a less polished boundary on one side. One vacant storefront remains in the older row, while active businesses cluster around the intersection.

**Route structure:** Main street is the most legible approach. A parallel side street offers a quieter route. The rear alley gives service access and a concealed path. A cross street and one mid-block connection create a loop. A stair or fire escape reaches an upper-floor route that overlooks the bank but is exposed from the intersection. The streets continue visually beyond the level boundary.

**Play read:** The bank is the primary landmark, but the deli sign, bus shelter, church roof, or water tower helps players navigate. The shortest route is visible; the alternative routes are discoverable through building form and access cues. Each route has a gameplay tradeoff and a plausible local purpose.

This seed defines relationships, not a fixed layout. The planner should adapt parcel shapes, building count, exact distances, and access to the mission footprint and performance budget.

## Bethesda references: what to learn

Use Bethesda as a source of process and design observation, not as a formula to copy. Useful takeaways are:

- Start with the intended player feeling and how the world should invite exploration.
- Make the world feel coherent before forcing gameplay onto it; then guide players toward useful activity.
- Give locations identity through how their inhabitants live, work, move, and use the place.
- Iterate through the world to find slow or empty stretches, then add, remove, or reshape content to improve pacing.
- Use modular building systems to create many coherent combinations, and test those systems in graybox layouts before polishing.

For this project, translate those ideas into district rules, readable route graphs, plausible adjacency, and repeatable validation. Do not assume that Bethesda’s spaces are generated by a literal hub-and-spoke algorithm; the hub-and-spoke model here is a planning abstraction for the AI creator.

## References

- Todd Howard interview on world feel, exploration, town identity, and how gameplay is layered into a plausible world. Fast Company, “How To Create A World: Skyrim’s Director On Building A Never-Ending Fantasy”: https://www.fastcompany.com/1679118/how-to-create-a-world-skyrims-director-on-building-a-never-ending-fantasy
- Joel Burgess and Nathan Purkeypile, “Skyrim’s Modular Approach to Level Design.” Game Developer, adapted from their GDC 2013 talk; discusses modular kits, testing kit behavior, and graybox layout: https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design
- Joel Burgess, “Level Design in a Day: How We Used Iterative Level Design to Ship Skyrim and Fallout 3.” GDC Vault, 2014: https://www.gdcvault.com/play/1020777/Level-Design-in-a-Day
- Current project companion: *Land Pressure and Spatial Logic for Procedural AI* (Library file). Use it for land allocation, archetypes, parcel logic, open-space roles, history, and validation.
