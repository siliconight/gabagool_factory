---
document_id: pa_1990s_building_adjacency_and_level_layout
schema_version: "1.0.0"
document_version: "1.0.0"
created: "2026-10-10"
language: en-US
format: markdown_with_yaml
intended_consumers: [human_level_designer, procedural_planner, language_model, layout_validator]
setting:
  country: US
  state: PA
  year_range_inclusive: [1990, 1999]
  primary_region: southeastern_pennsylvania
  priority_counties: [Philadelphia, Delaware]
  secondary_counties: [Chester, Montgomery, Bucks, Lancaster, Berks, Lehigh, Northampton]
authority: proposed_game_design_specification
historical_claims: source_cited
numeric_defaults: author_proposed_starting_points_not_measured_standards
units: {distance: m, area: m2, angle: degrees, time: seconds}
---

# 1990s Pennsylvania: Building Relationships and Playable Place Design

A guide for a level-layout system that must decide what belongs together, what separates it, what connects it, and how it becomes a believable place to play.

**Contents:** [Core task](#1-what-this-guide-asks-the-layout-brain-to-do) · [Regional context](#2-choose-the-place-before-choosing-the-buildings) · [Relationship types](#3-describe-the-relationship-precisely) · [Generation order](#4-generation-order-and-constraint-precedence) · [84 building types](#5-neighbor-selection-broad-compatibility-and-specific-uses) · [32 adjacency rules](#6-explicit-adjacency-rules-and-believable-exceptions) · [Connecting spaces](#7-the-spaces-between-buildings-do-most-of-the-work) · [Set dressing and life](#8-set-dressing-objects-should-have-causes) · [Period accuracy](#9-make-the-year-visible-through-operation) · [Gameplay](#10-turn-a-believable-place-into-a-good-level) · [18 site recipes](#11-reusable-neighborhood-and-site-recipes) · [Machine output and examples](#12-output-contract-for-a-layout-brain) · [Validation](#13-validation-and-review) · [Sources](#14-sources-and-evidence-boundaries).

## 1. What this guide asks the layout brain to do

**Build a place with reasons, then shape that place into a level.** A plausible town is not a shuffled list of interesting buildings. It is a network of households, customers, employers, deliveries, institutions, infrastructure, and older decisions that still affect the ground plan.

A pharmacy beside a clinic has a customer relationship. A diner beside a trucking yard serves a workforce. A church beside a cemetery has a historical relationship. A pool beside an airport may belong to a hotel, recreation club, or neighborhood that predates airport expansion. The same pool opening directly onto an aircraft apron is a different proposition: ownership, access, operations, and the physical boundary no longer make sense.

The central question is not simply **“Can A be next to B?”** It is:

> What kind of adjacency is this, why did it happen, who uses the connection, what manages the conflict, and what can the player see that makes the answer apparent?

The generator must produce five connected results:

1. **Place logic:** a location, development history, local economy, and coherent mix of uses.
2. **Physical layout:** terrain, streets, parcels, building fronts and backs, open spaces, and boundaries.
3. **Operational layout:** customer access, resident access, staff access, deliveries, refuse, maintenance, and utilities.
4. **Playable layout:** readable destinations, useful choices, loops, vertical routes, encounter spaces, and exits.
5. **Evidence of life:** activity, care, wear, sound, signs, and objects placed by identifiable people for identifiable reasons.

This is a design specification for fictional game spaces. Its scores, dimensions, ratios, and acceptance gates are proposed production defaults, not surveyed Pennsylvania statistics or building-code requirements. Source-backed historical observations are identified separately. Reconstructing a real property requires evidence for that property and year.

### 1.1 Non-negotiable reasoning rules

- **Proximity is not permission.** Two properties can touch without sharing a door, driveway, customer entrance, or right of access.
- **A good story needs geometry.** An explanation must change ownership, routing, boundaries, visible evidence, or operations. A sentence alone cannot repair an impossible plan.
- **Historical plausibility is not ideal planning.** Homes and factories really can be uncomfortable neighbors. Preserve credible inherited conflicts instead of making every district perfectly separated.
- **Ordinary buildings are necessary.** Housing, workshops, storage, small offices, and closed façades make the unusual destination feel grounded.
- **Repetition is natural.** Rowhouses, shop bays, parking modules, and farm structures repeat because people build in systems. Vary their use and history; do not scramble every module.
- **Creativity belongs in relationships.** Prefer a memorable, explained combination over a collection of unrelated landmarks.
- **Physical evidence carries the explanation.** A player should understand the place without reading the generator's notes.

### 1.2 How to ingest this document

The YAML front matter describes the document. Every fenced `yaml` block is a separate parseable mapping with a unique top-level key. Extract and parse the blocks independently, then merge their top-level keys into a rule package. Do not parse the whole Markdown file as YAML.

Tables and prose explain intent. YAML contains stable identifiers, enumerations, catalog records, explicit rule records, and example payloads. Lists in catalog fields are suggestions unless the field is named `requires`, `must`, or a rule explicitly makes them mandatory. Empty arrays mean “none declared”; `null` means “unknown”; missing required fields are validation errors. A blank value must never be silently treated as evidence.

The package is a specification for a planner to implement, not a prebuilt layout engine. Validators must implement the named predicates and report their results; a language model must not mark a geometric check as passed merely because it described the intended result.

## 2. Choose the place before choosing the buildings

### 2.1 Input contract

Set the exact year, municipality type, terrain, land pressure, and dominant reason the area exists. “Pennsylvania, 1990s” is too broad to determine a credible block.

```yaml
input_contract:
  required:
    - setting_year
    - county
    - settlement_profile
    - development_history
    - economic_anchor
    - terrain_profile
    - season
    - local_time
    - playable_bounds_m
    - player_count
    - movement_profile
    - mission_requirements
  optional:
    - municipality_reference
    - historical_reference_ids
    - protected_landmarks
    - desired_unusual_pairing
    - asset_catalog_ids
    - performance_budget
    - accessibility_goals
    - weather
  suggested_fiction_defaults:
    setting_year: 1995
    county: Delaware
    settlement_profile: mature_inner_suburb
    development_history: "Older transit neighborhood with later roadside infill."
    economic_anchor: neighborhood_services
    terrain_profile: gently_rolling_with_creek
    season: late_summer
    local_time: "16:30"
    player_count: 4
    movement_profile: cooperative_first_person
  required_explicit_choices:
    - playable_bounds_m
    - mission_requirements
  coordinates:
    plan_axes: {x: east, y: north, z: up}
    origin: southwest_corner_of_declared_world_bounds
    engine_conversion: explicit_adapter_required
  missing_input_policy:
    fiction_context: use_declared_defaults_and_report_assumptions
    real_site_reconstruction: request_or_retrieve_missing_evidence
    geometry_or_mission_constraint: do_not_invent_a_pass_result
```

The four-player default is a useful co-op starting point, not a requirement for all projects. Scene size must come from the mission brief; this document does not force a town into a universal meter count.

### 2.2 Regional profiles

The following are **design composites**, not claims that every town in a county looks alike. Delaware County's planning material distinguishes mature neighborhoods, growing suburbs, central places, and activity corridors; use that variety rather than one generic “Delco” texture. [S02]

| Profile ID | Suitable reference context | Organizing pattern | Likely anchors and neighbors | Common mistake |
|---|---|---|---|---|
| `philly_rowhouse` | Philadelphia residential blocks and neighborhood commercial streets | Tight parcels; attached fronts; side streets; varied rear access | Corner store, takeout, tavern, school, church, recreation ground | Giving every house a driveway, side gap, and enormous lawn |
| `mature_inner_suburb` | Older Delaware County boroughs and inner suburbs | Rows, twins, detached homes, small apartments; older shopping street; transit where evidenced | Deli, pharmacy, garage, church, civic hall, station or bus stop | Treating all of Delco as either downtown Philadelphia or low-density rural land |
| `borough_center` | Media-, Lansdowne-, or West Chester-inspired fictional centers | Connected commercial frontage with homes close behind | Bank, courthouse or municipal hall where appropriate, offices, diner, theater | Assigning every borough a county courthouse or regional hospital |
| `rail_suburb` | Selected Main Line and other rail-served town centers | Station-centered service cluster transitioning to residential streets | Small offices, bakery, shops, apartments, church | Giving every station a huge terminal and every shop a vast private lot |
| `postwar_suburb` | Postwar neighborhoods in Delaware, Montgomery, or Bucks County | Repeated housing lots; collector roads; shopping and schools as separate nodes | Elementary school, pool club, park, neighborhood shopping center | Inserting a heavy industrial gate in the middle of a residential cul-de-sac without history |
| `arterial_strip` | Older commercial roads across southeastern PA | Traffic-facing signs; individual curb cuts or shared lots; shallow commercial depth | Diner, motel, garage, fuel station, bowling, strip retail | A continuous pedestrian main street behind an uninterrupted field of parking |
| `river_industry` | Delaware River industrial corridor and similar working waterfronts | Large parcels, freight access, infrastructure barriers, surviving older streets | Factory, warehouse, trucking, utility plant, worker housing, tavern | Turning every waterfront into a contemporary leisure promenade |
| `creek_mill_edge` | Creek valleys and older mill settlements | Roads and structures respond to grade, water, and former industrial use | Mill, workshops, modest homes, bridge, woodland edge | A flat grid crossing the creek repeatedly with no reason or bridge structure |
| `rural_market_town` | Chester, Lancaster, Berks, and other agricultural districts | Compact village or crossroads serving a much larger hinterland | Feed store, repair, church, market, diner, fire company | Spreading every building evenly across a field |
| `farmstead` | A researched agricultural subregion | Related working buildings, yards, lanes, fields, drainage, and landforms | House, barn, machinery shed, crop or livestock support | One decorative barn disconnected from fields and farm work |
| `institutional_campus` | College, hospital, school, museum, or country-club grounds | Common ownership and internal circulation | Main institution, grounds, maintenance, support buildings | Treating every campus building as an unrelated commercial parcel |
| `airport_edge` | Fictional PHL-region airport fringe | Landside arrivals, hotels, rental vehicles, freight, and distinct controlled operations | Terminal, airport hotel, rental lot, office, cargo facility | Compressing runway, terminal, hotel pool, and neighborhood sidewalk into one undivided courtyard |

Historic urban form is shaped by the street grid, building size, setbacks, and public spaces. PHMC describes urban districts as combinations of residential, commercial, and industrial resources. That supports mixed places; it does not make every mixture equally convincing. [S03]

Streetcar-era suburbs and postwar car-oriented subdivisions have different organizing patterns. Use an established development pattern and then add dated alterations. Do not average both into an indistinct middle. [S04]

Philadelphia's rowhouses are an important local building type with substantial variation in age, size, and form. The city's manual also describes the historical relationship between housing, work, and waterfront industry. Use that as context, not as an instruction to copy one house everywhere. [S01]

### 2.3 Three layers of time

Every principal parcel should have a short, causal timeline:

1. **Original purpose:** why this building and parcel first existed.
2. **Major change:** addition, conversion, road widening, subdivision, fire loss, closure, or new ownership.
3. **Present condition in the selected 1990s year:** current tenant, active entrances, maintenance, surviving traces.

Example: a 1920s repair garage became an appliance repair shop in 1978. In 1995 it retains a wide service door, patched paving, a small parts counter, and a newer painted sign. This is more informative than “old building, randomized grime.”

A 1990s setting contains many buildings and objects made before 1990. It should also contain maintained property, recent repairs, and some new construction. Do not confuse a historical period with universal abandonment.

## 3. Describe the relationship precisely

### 3.1 Adjacency is a typed relationship

```yaml
relationship_vocabulary:
  spatial_relations:
    same_structure: "Distinct uses within one building; may be vertically stacked."
    shared_boundary: "Parcels touch; access is not implied."
    across_local_street: "Opposite edges of a local street; crossing must be modeled."
    across_arterial: "Visible proximity across a major road; pedestrian connectivity is separate."
    same_block: "Within one block; does not imply a shared boundary."
    same_campus: "A common institution or coordinated estate links the uses."
    district_near: "Within the declared local catchment; actual route distance is recorded."
    visual_only: "Visible from the level but not reachable within its traversal graph."
  functional_relations:
    - serves_customers_of
    - serves_workers_of
    - supplies
    - shares_owner_with
    - shares_facility_with
    - historically_predates
    - reuses_former_site_of
    - competes_with
    - incidental_neighbor_of
  edge_channels:
    - pedestrian_public
    - pedestrian_authorized
    - resident
    - vehicle_public
    - delivery
    - refuse
    - emergency
    - utility
    - visual
    - acoustic
  access_classes: [public, customer, resident, staff, service, controlled, closed]
  compatibility_verdicts:
    prefer: "Fits the declared relation and context; mandatory checks still apply."
    allow: "Ordinary possibility with no special explanation required."
    condition: "Requires specified ownership, access, separation, history, or evidence."
    repair: "Current proposal fails; modify its layout before accepting."
    reject: "Violates a non-waivable project constraint or remains impossible after repair."
  unknown_policy: review_and_explain
```

`district_near` must include a route distance and catchment assumption. It must not secretly mean “within 50 meters” everywhere. A rural repair shop can serve farms several kilometers away; a corner store typically relies on a more local pattern. A level may show only a small part of either catchment.

Spatial relations may be symmetric, but functional relations can be directional. Store each functional relationship as a `kind`, `from_id`, and `to_id` record. “House predates factory” and “factory predates house” are different histories. Symmetric relationships such as shared ownership can use either ordering, provided their meaning remains symmetric.

### 3.2 Evaluate five separate questions

| Question | Example of a good answer | Failure to catch |
|---|---|---|
| **Functional fit** | Lunch counter serves factory shifts | Assuming every warehouse needs another warehouse as its only neighbor |
| **Physical fit** | Storefront aligns to the sidewalk; deliveries reach the rear | Buildings technically fit while their doors face fences |
| **Operational fit** | Hotel guests reach the pool through hotel grounds | All properties share an unrestricted maintenance door |
| **Historical fit** | Homes predate expansion of an adjoining industrial site | Deleting all uncomfortable historical juxtapositions |
| **Gameplay fit** | Public street and service lane provide legible route choices | A believable map with only one repetitive corridor |

Assess front-to-front, front-to-back, and back-to-back conditions separately. A restaurant can share a rear service area with a shop while both preserve public entrances on the street. The same loading area placed between the restaurant's dining terrace and the shop window would read differently.

### 3.3 Conflict is not a single distance

For each edge, consider noise, odor, heavy traffic, privacy, visual exposure, crowding, illumination, and access restrictions. A fence can define ownership; it does not eliminate industrial noise. Trees can soften a view; they do not make a runway compatible with unrestricted pedestrian activity. Record what a buffer actually does.

Use one or more of these responses:

- Reorient the quiet façade away from the disturbance.
- Put storage, parking, a service court, or another less-sensitive use on the affected edge.
- Separate circulation systems while keeping visual proximity.
- Increase space or insert a public street where the setting supports it.
- Show an inherited conflict with credible boundaries and consequences.
- Move the use elsewhere if its operation still cannot function.

## 4. Generation order and constraint precedence

### 4.1 Solve the ground plan before filling it

1. **Read the brief.** Lock year, area type, world bounds, mission needs, and movement assumptions.
2. **Explain the settlement.** Choose one primary anchor and supporting reasons people live or work there.
3. **Lay down persistent features.** Terrain, waterways, rail alignments, major roads, and preserved properties.
4. **Make blocks and parcels.** Respect the chosen pattern, land pressure, grade, and existing roads.
5. **Reserve required open space.** Service yards, school grounds, field access, parking where appropriate, and water margins.
6. **Place the primary destination.** Include its complete operational footprint, not just its building mesh.
7. **Choose useful neighbors.** Add related uses and ordinary supporting fabric. Resolve conditional pairings.
8. **Connect users and services.** Build public, private, staff, and delivery graphs independently, then identify authorized overlaps.
9. **Shape the playable route.** Add meaningful choices, loops, landmarks, bottlenecks, and pauses without breaking place logic.
10. **Populate the ground.** Assign an owner, action, support surface, and clearance to important props.
11. **Run state changes.** Test occupied, closed, alarmed, blocked, and evacuation states relevant to the mission.
12. **Validate and repair.** Produce a reasoned report with failed checks and remaining assumptions.

If a terminal, refinery, college, or large hospital does not fit, represent a credible portion of the complex with continuations beyond the play boundary. Do not shrink essential operations until the place becomes nonsensical.

### 4.2 Precedence

```yaml
constraint_policy:
  evaluation_order:
    - explicit_project_constraints
    - geometric_and_graph_invariants
    - setting_year_and_asset_provenance
    - access_and_operational_requirements
    - explicit_pair_rules
    - settlement_profile_fit
    - category_affinity
    - creative_variation
  non_waivable:
    - referenced_id_exists
    - mandatory_route_is_reachable_in_required_state
    - required_clearance_is_satisfied
    - required_structure_has_support
    - mutually_exclusive_occupancy_does_not_overlap
    - water_crossing_has_a_declared_crossing_type
    - year_locked_asset_is_not_later_than_setting
    - claimed_restricted_boundary_has_no_unintentional_public_edge
  exceptions_may_modify:
    - usual_neighbor_preference
    - typical_parcel_pattern
    - ideal_noise_or_privacy_relationship
    - common_ownership_assumption
  exception_may_not_modify: non_waivable
  contradiction_policy: reject_current_candidate_and_repair
  unknown_rule_policy: require_reason_and_validation
```

Game-specific infiltration, destruction, or trespass can be an intentional state transition. It must be declared as such. A boundary that can be deliberately crossed is different from a planner accidentally merging public and private spaces.

### 4.3 Score feasible alternatives; never score away a failure

After mandatory checks pass, compare candidates using the following **tunable editorial score**. It measures design intent, not historical probability.

```yaml
candidate_scoring:
  score_range: [0, 100]
  component_ranges: [0, 1]
  weights:
    regional_and_period_fit: 20
    adjacency_explanation: 20
    operational_completeness: 20
    gameplay_and_wayfinding: 25
    evidence_of_life: 10
    purposeful_novelty: 5
  formula: sum_weight_times_component
  gate: mandatory_checks_pass_before_ranking
  novelty_policy: no_credit_for_unexplained_randomness
  score_is_not: probability_or_regulatory_compliance
  audit_required:
    - evidence_for_each_component
    - failed_or_unrun_checks
    - assumptions
    - accepted_exceptions
```

Use profile-constrained selection with quotas for ordinary uses and repeated fabric. Do not choose each neighbor independently: a deli, clinic, garage, warehouse, pool, and cathedral can each be individually plausible in a county while their combined arrangement is incoherent.

### 4.4 Conservative repair order

Try the smallest change that preserves the useful idea:

1. Change the facing or entrance location.
2. Change the connector or access permission.
3. Add an operationally meaningful boundary, yard, or support use.
4. Reclassify the relationship from direct adjacency to district proximity.
5. Replace a generic use with a credible subtype, such as public pool → hotel pool.
6. Add a documented history and its visible consequences, if history truly explains the conflict.
7. Move or replace the building.

Do not satisfy every exception by adding a sign, a fence, and the word “historic.”

## 5. Neighbor selection: broad compatibility and specific uses

### 5.1 Broad affinity matrix

This matrix concerns **district-level likelihood in a suitable context**. It does not authorize a shared doorway, parcel boundary, or access route. A high score for transportation and housing can describe a station neighborhood; it does not approve housing on an aircraft apron.

Values are editorial weights: `2` strong fit, `1` useful possibility, `0` context-dependent, `-1` usually weak, `-2` significant conflict requiring explanation. They are not probabilities. Specific pair rules and operational checks outrank this matrix.

```yaml
category_affinity:
  relation_scope: district_near
  symmetric: true
  order: [res, ret, civ, rec, ngt, lgt, hvy, trn, agr]
  categories:
    res: housing
    ret: commerce_offices_and_lodging
    civ: civic_care_and_institutions
    rec: recreation_and_culture
    ngt: nightlife_and_adult_entertainment
    lgt: workshops_storage_and_light_production
    hvy: heavy_industry_and_major_utilities
    trn: transportation_and_vehicle_services
    agr: farming_and_agricultural_support
  rows:
    res: [ 2,  2,  2,  2,  0,  0, -2,  1,  1]
    ret: [ 2,  2,  2,  2,  2,  1, -1,  2,  1]
    civ: [ 2,  2,  2,  2,  0,  0, -2,  1,  1]
    rec: [ 2,  2,  2,  2,  1,  0, -2,  1,  1]
    ngt: [ 0,  2,  0,  1,  2,  1, -1,  1,  0]
    lgt: [ 0,  1,  0,  0,  1,  2,  1,  2,  1]
    hvy: [-2, -1, -2, -2, -1,  1,  2,  2,  0]
    trn: [ 1,  2,  1,  1,  1,  2,  2,  2,  1]
    agr: [ 1,  1,  1,  1,  0,  1,  0,  1,  2]
```

### 5.2 Building catalog

Each record states a usual role, useful neighbors, minimum support program, and the important placement caution. Neighbor lists are **suggestions, not exhaustive allowed lists**. Multiple tenants may occupy one structure. A school gym, pool plant room, maintenance shed, or chapel can be a component rather than a separate freestanding building.

`requires` entries are functional requirements. They can be satisfied within the building, elsewhere on the site, or by a declared shared facility. The output must identify the provider. A requirement does not automatically create a large separate room, parking lot, or road.

```yaml
support_program:
  public_entry: "A legible entrance connected to an appropriate public route."
  resident_entry: "A route and threshold for residents, independent where needed."
  staff_access: "An authorized way for staff to reach work areas."
  goods_access: "A credible route and handling point for the stated goods and vehicle scale."
  refuse_access: "A storage and collection arrangement proportional to the use."
  service_space: "Space for maintenance, storage, plant, or repair as the use demands."
  utility_service: "A declared supply and connection appropriate to the use."
  toilet_access: "An appropriate on-site or declared shared provision."
  outdoor_yard: "Usable outdoor working or private space; not a decorative gap."
  vehicle_access: "A connected drivable route with tested entrance and turning geometry."
  stopping_area: "A workable loading, pickup, or short-stop location."
  parking_strategy: "Street, shared, on-site, remote, or limited parking stated explicitly."
  separation: "A declared boundary and treatment for conflicting activities."
  emergency_access: "A credible emergency response approach; not a code certification."
  customer_waiting: "A waiting or queue area outside the movement clearance."
  pedestrian_crossing: "A declared crossing where the use depends on reaching the opposite side."
  freight_interface: "A loading interface and connected freight route at matching scale."
  rail_interface: "A physically coherent track and platform or freight relationship."
  water_interface: "A coherent relationship to navigable water, shoreline, or water supply."
  field_access: "A working connection to fields, grazing, or agricultural land."
  animal_support: "Appropriate holding, care, and staff facilities for depicted animals."
  controlled_threshold: "A boundary with explicit permitted users and game states."
  assembly_space: "Space for the people implied by the facility and its schedule."
  changing_space: "A changing arrangement associated with sport or swimming."
  pool_plant: "A declared circulation and maintenance provision for a functioning pool."
  kitchen_support: "A preparation, storage, exhaust, and waste arrangement appropriate to food service."
  building_connection: "A stated physical and ownership relationship to the host building."
  landscape_extent: "Enough land or visible continuation to support the claimed use."
  runway_context: "A plausible airfield context beyond the terminal; may extend outside play."
```

All occupied types additionally need a proportionate utility, refuse, staff or resident, and emergency strategy. This general requirement is not repeated in every row. The catalog does not certify real-world code compliance.

```yaml
building_catalog:
  - {id: rowhouse, category: res, role: ordinary_fabric, neighbors: [rowhouse, corner_store, church, school, playground], requires: [resident_entry, refuse_access], caution: "Use attached fronts and a coherent rear-access pattern; not every row has a vehicle alley."}
  - {id: twin_house, category: res, role: ordinary_fabric, neighbors: [twin_house, detached_house, corner_store, church], requires: [resident_entry, outdoor_yard], caution: "Paired construction is deliberate; side gaps and driveways follow the local pattern."}
  - {id: detached_house, category: res, role: ordinary_fabric, neighbors: [detached_house, school, public_pool, church], requires: [resident_entry, outdoor_yard, parking_strategy], caution: "Plot width, setback, and driveway pattern depend on development era and land pressure."}
  - {id: apartment, category: res, role: ordinary_fabric, neighbors: [grocery, laundromat, rail_station, park], requires: [resident_entry, refuse_access, parking_strategy], caution: "A converted house, urban walk-up, and garden complex need different footprints."}
  - {id: shop_house, category: res, role: mixed_use_fabric, neighbors: [shop_house, deli, pharmacy, tavern], requires: [public_entry, resident_entry, goods_access], caution: "Separate tenant access and make vertical stacking explicit."}
  - {id: farmhouse, category: res, role: farm_residence, neighbors: [barn, machine_shed, greenhouse], requires: [resident_entry, vehicle_access, landscape_extent], caution: "House placement relates to the working farm, road, drainage, and history."}
  - {id: corner_store, category: ret, role: daily_service, neighbors: [rowhouse, apartment, school, laundromat], requires: [public_entry, goods_access, refuse_access], caution: "A small store may receive curbside or handcart deliveries; it need not have a truck dock."}
  - {id: deli, category: ret, role: daily_service, neighbors: [rowhouse, office, rail_station, factory], requires: [public_entry, kitchen_support, goods_access], caution: "Connect lunch trade and supply access without putting bins in the customer queue."}
  - {id: diner, category: ret, role: gathering_place, neighbors: [motel, truck_depot, repair_garage, office], requires: [public_entry, kitchen_support, parking_strategy], caution: "Choose an urban storefront or roadside format before assigning parking."}
  - {id: restaurant, category: ret, role: destination_or_service, neighbors: [office, cinema, hotel, shop_house], requires: [public_entry, kitchen_support, goods_access], caution: "Exhaust and refuse need a credible edge, especially under apartments."}
  - {id: pizzeria, category: ret, role: neighborhood_food, neighbors: [video_store, laundromat, tavern, rowhouse], requires: [public_entry, kitchen_support, stopping_area], caution: "Account for takeout, delivery pickup, and evening activity."}
  - {id: pharmacy, category: ret, role: daily_service, neighbors: [clinic, grocery, apartment, office], requires: [public_entry, goods_access, customer_waiting], caution: "A small borough pharmacy and a freestanding chain store are different site types."}
  - {id: grocery, category: ret, role: retail_anchor, neighbors: [pharmacy, laundromat, apartment, strip_center], requires: [public_entry, goods_access, refuse_access, parking_strategy], caution: "Give a supermarket a real delivery and refuse arrangement; avoid tiny rear alleys for large trailers."}
  - {id: strip_center, category: ret, role: multi_tenant_shell, neighbors: [grocery, fuel_station, apartment, bowling], requires: [public_entry, vehicle_access, parking_strategy, goods_access], caution: "Tenants share an organizing shell and circulation; do not count the shell as another shop."}
  - {id: shopping_mall, category: ret, role: regional_anchor, neighbors: [cinema, hotel, office, fuel_station], requires: [public_entry, assembly_space, goods_access, vehicle_access, parking_strategy], caution: "Show a credible portion of a large complex with service access and off-map continuation."}
  - {id: bank, category: ret, role: commercial_service, neighbors: [office, courthouse, grocery, shop_house], requires: [public_entry, staff_access, customer_waiting], caution: "A main-street bank need not have a drive-through; vehicle formats require queue space."}
  - {id: hardware, category: ret, role: trade_and_household_service, neighbors: [repair_garage, rowhouse, workshop, feed_store], requires: [public_entry, goods_access, service_space], caution: "Distinguish a small shop from a building-supply yard."}
  - {id: laundromat, category: ret, role: daily_service, neighbors: [apartment, corner_store, pizzeria, barber_salon], requires: [public_entry, utility_service, service_space], caution: "Machines, ventilation, maintenance, and waiting need more than a sign."}
  - {id: barber_salon, category: ret, role: daily_service, neighbors: [corner_store, laundromat, shop_house, pharmacy], requires: [public_entry, utility_service, customer_waiting], caution: "Use a small ordinary tenant bay unless the brief says otherwise."}
  - {id: video_store, category: ret, role: period_retail, neighbors: [pizzeria, grocery, strip_center, apartment], requires: [public_entry, goods_access, stopping_area], caution: "Treat it as a functioning rental business in the selected year, not automatic nostalgia clutter."}
  - {id: liquor_store, category: ret, role: specialty_retail, neighbors: [grocery, shop_house, strip_center, office], requires: [public_entry, goods_access], caution: "Verify the chosen Pennsylvania retail format, signage, and year before depicting a real brand."}
  - {id: beer_distributor, category: ret, role: specialty_retail_and_storage, neighbors: [hardware, warehouse, strip_center, repair_garage], requires: [public_entry, goods_access, stopping_area], caution: "Represent the selected period's distribution format; do not infer a modern supermarket beer aisle."}
  - {id: office, category: ret, role: employment, neighbors: [deli, bank, clinic, rail_station], requires: [public_entry, staff_access, parking_strategy], caution: "Choose upper-floor office, small converted house, or office park; they are not interchangeable."}
  - {id: motel, category: ret, role: roadside_lodging, neighbors: [diner, fuel_station, repair_garage, airport_terminal], requires: [public_entry, resident_entry, vehicle_access, service_space], caution: "A pool is optional and needs its own enclosure and service provision."}
  - {id: hotel, category: ret, role: destination_lodging, neighbors: [office, restaurant, airport_terminal, museum], requires: [public_entry, resident_entry, goods_access, stopping_area], caution: "Guests, servicing, parking, and event visitors should not all use one indistinct threshold."}
  - {id: clinic, category: civ, role: local_care, neighbors: [pharmacy, apartment, office, grocery], requires: [public_entry, customer_waiting, stopping_area], caution: "Keep patient access legible and avoid routing it through a working service yard."}
  - {id: hospital, category: civ, role: regional_care_anchor, neighbors: [clinic, pharmacy, office, hotel], requires: [public_entry, emergency_access, goods_access, controlled_threshold, service_space], caution: "Separate major patient, emergency, and service flows; show a campus fragment if necessary."}
  - {id: school, category: civ, role: neighborhood_institution, neighbors: [sports_field, playground, church, rowhouse], requires: [public_entry, assembly_space, goods_access, stopping_area], caution: "Primary pupil routes should not depend on traversing industrial loading or vehicle storage."}
  - {id: college, category: civ, role: campus_anchor, neighbors: [library, apartment, tavern, sports_field], requires: [public_entry, assembly_space, service_space, goods_access], caution: "Common ownership and campus paths can explain uses that would be odd as unrelated parcels."}
  - {id: church, category: civ, role: community_anchor, neighbors: [rowhouse, school, cemetery, community_center], requires: [public_entry, assembly_space, parking_strategy], caution: "Congregation size, setting, and construction era determine the site; not every church has a large lot."}
  - {id: cemetery, category: civ, role: landscape_institution, neighbors: [church, funeral_home, park, detached_house], requires: [public_entry, vehicle_access, service_space, landscape_extent], caution: "Provide an entrance and maintenance logic; treat burial plots as a specific land use, not generic clutter."}
  - {id: funeral_home, category: civ, role: community_service, neighbors: [church, cemetery, detached_house, office], requires: [public_entry, stopping_area, staff_access], caution: "Front presentation and discreet servicing need different spatial treatment."}
  - {id: municipal_hall, category: civ, role: civic_anchor, neighbors: [library, post_office, police_station, park], requires: [public_entry, customer_waiting, staff_access], caution: "Scale the institution to the municipality rather than giving every village a monumental city hall."}
  - {id: courthouse, category: civ, role: administrative_anchor, neighbors: [office, bank, diner, parking_garage], requires: [public_entry, controlled_threshold, staff_access, assembly_space], caution: "Use county-seat or specifically justified context; distinguish public and restricted circulation."}
  - {id: police_station, category: civ, role: municipal_service, neighbors: [municipal_hall, courthouse, office, fire_station], requires: [public_entry, controlled_threshold, vehicle_access, staff_access], caution: "A public lobby is not a public route through staff and holding areas."}
  - {id: fire_station, category: civ, role: emergency_service, neighbors: [municipal_hall, diner, rowhouse, community_center], requires: [vehicle_access, emergency_access, assembly_space], caution: "Keep the apparatus apron and departure path free even when a hall hosts an event."}
  - {id: library, category: civ, role: neighborhood_institution, neighbors: [school, municipal_hall, park, apartment], requires: [public_entry, goods_access, customer_waiting], caution: "A calm entrance is useful; proximity to a lively street does not make the whole building silent."}
  - {id: post_office, category: civ, role: logistics_and_public_service, neighbors: [municipal_hall, shop_house, office, diner], requires: [public_entry, goods_access, staff_access, stopping_area], caution: "Separate mail handling from the public queue; scale freight to the branch."}
  - {id: union_hall, category: civ, role: community_and_workforce, neighbors: [factory, tavern, rowhouse, diner], requires: [public_entry, assembly_space, parking_strategy], caution: "Use meeting, event, and notice-board evidence; it need not be active at every hour."}
  - {id: community_center, category: rec, role: local_recreation_anchor, neighbors: [public_pool, playground, sports_field, rowhouse], requires: [public_entry, assembly_space, service_space], caution: "Shared ownership may justify common changing rooms or maintenance, if explicitly connected."}
  - {id: public_pool, category: rec, role: seasonal_recreation, neighbors: [community_center, school, park, detached_house], requires: [public_entry, changing_space, pool_plant, separation], caution: "Membership or municipal operation, hours, enclosure, and seasonal state must be declared."}
  - {id: hotel_pool, category: rec, role: lodging_amenity, neighbors: [hotel, motel], requires: [building_connection, changing_space, pool_plant, separation], caution: "A guest amenity is not automatically a public shortcut or separate civic facility."}
  - {id: playground, category: rec, role: local_recreation, neighbors: [school, park, rowhouse, apartment], requires: [public_entry, separation, service_space], caution: "Boundaries should respond to streets and other hazards; do not use random equipment as general-purpose cover."}
  - {id: park, category: rec, role: public_landscape, neighbors: [rowhouse, school, library, community_center], requires: [public_entry, service_space, landscape_extent], caution: "Choose a maintained square, playing park, wooded tract, or creek margin; each has different density and access."}
  - {id: sports_field, category: rec, role: scheduled_recreation, neighbors: [school, community_center, park, public_pool], requires: [public_entry, service_space, landscape_extent], caution: "Reserve the playing area before adding paths, spectators, or outbuildings."}
  - {id: bowling, category: rec, role: evening_destination, neighbors: [diner, strip_center, tavern, cinema], requires: [public_entry, assembly_space, service_space, parking_strategy], caution: "The long-span interior must fit the exterior massing; do not fit full lanes into a shallow shop."}
  - {id: cinema, category: rec, role: cultural_destination, neighbors: [restaurant, arcade, shopping_mall, tavern], requires: [public_entry, assembly_space, service_space], caution: "A main-street single-screen theater and a multiplex have different parcels and arrival patterns."}
  - {id: arcade, category: rec, role: leisure_tenant, neighbors: [cinema, shopping_mall, pizzeria, bowling], requires: [public_entry, utility_service, service_space], caution: "Choose a plausible tenant size and activity level instead of inserting it into every block."}
  - {id: museum, category: rec, role: cultural_anchor, neighbors: [park, college, office, restaurant], requires: [public_entry, goods_access, service_space, controlled_threshold], caution: "Collection handling and public circulation need distinct treatment; use a site-specific institutional context."}
  - {id: zoo, category: rec, role: large_specialty_campus, neighbors: [park, museum, parking_garage], requires: [public_entry, animal_support, service_space, goods_access, landscape_extent], caution: "Needs a dedicated campus and service program; it is not a casual filler parcel."}
  - {id: aquarium, category: rec, role: large_specialty_institution, neighbors: [museum, park, restaurant], requires: [public_entry, animal_support, utility_service, service_space, goods_access], caution: "Require a specific fictional premise or dated local reference; a nearby out-of-state institution is not automatically a PA site."}
  - {id: country_club, category: rec, role: private_recreation_campus, neighbors: [hotel, sports_field, detached_house], requires: [controlled_threshold, service_space, landscape_extent, vehicle_access], caution: "Declare any private club pool as an owned component; a golf-course claim requires substantial land or off-map continuation."}
  - {id: marina, category: rec, role: water_recreation_and_service, neighbors: [restaurant, boat_storage, repair_garage], requires: [water_interface, vehicle_access, service_space, controlled_threshold], caution: "Distinguish working yard, launch, pedestrian dock, and public restaurant."}
  - {id: tavern, category: ngt, role: neighborhood_evening_service, neighbors: [rowhouse, pizzeria, union_hall, factory], requires: [public_entry, goods_access, refuse_access, toilet_access], caution: "Rowhouse adjacency can be ordinary; scale noise and exterior activity to the actual venue."}
  - {id: nightclub, category: ngt, role: nightlife_destination, neighbors: [restaurant, cinema, warehouse, parking_garage], requires: [public_entry, assembly_space, stopping_area, separation], caution: "Queues, late departures, sound, and neighbors matter; do not classify it as a quiet tavern."}
  - {id: adult_venue, category: ngt, role: specialized_nightlife, neighbors: [motel, warehouse, diner, repair_garage], requires: [public_entry, separation, parking_strategy], caution: "Require a specific local history or fictional siting premise; avoid automatic placement beside school entrances."}
  - {id: repair_garage, category: lgt, role: vehicle_repair_service, neighbors: [fuel_station, hardware, diner, body_shop], requires: [vehicle_access, outdoor_yard, service_space, refuse_access], caution: "Reserve the work apron and stored vehicles; bays must face a usable approach."}
  - {id: body_shop, category: lgt, role: vehicle_repair_service, neighbors: [repair_garage, warehouse, scrap_yard], requires: [vehicle_access, outdoor_yard, separation, utility_service], caution: "Painting, storage, ventilation, and work vehicles need a credible rear or side relationship."}
  - {id: print_shop, category: lgt, role: local_production, neighbors: [office, courthouse, shop_house, warehouse], requires: [public_entry, goods_access, service_space], caution: "A copy shop and a large printing works require different noise and freight assumptions."}
  - {id: workshop, category: lgt, role: ordinary_workplace, neighbors: [hardware, warehouse, repair_garage, rowhouse], requires: [goods_access, service_space, utility_service], caution: "Declare the trade and scale; a cabinet shop is not an interchangeable generic factory."}
  - {id: warehouse, category: lgt, role: storage_and_distribution, neighbors: [truck_depot, factory, building_supply, airport_cargo], requires: [freight_interface, vehicle_access, service_space], caution: "Cargo type and delivery vehicle set the dock and yard geometry."}
  - {id: food_plant, category: lgt, role: production_anchor, neighbors: [warehouse, truck_depot, factory], requires: [goods_access, service_space, utility_service, separation], caution: "Distinguish public sales, if any, from production and service spaces."}
  - {id: brewery, category: lgt, role: beverage_production, neighbors: [warehouse, restaurant, tavern, truck_depot], requires: [goods_access, utility_service, service_space, refuse_access], caution: "Specify historic industrial brewery or dated brewpub; do not assume a contemporary taproom district."}
  - {id: building_supply, category: lgt, role: trade_supplier, neighbors: [hardware, workshop, truck_depot, repair_garage], requires: [public_entry, goods_access, outdoor_yard, vehicle_access], caution: "Separate trade loading from the public counter and preserve material-length clearance."}
  - {id: storage_facility, category: lgt, role: storage, neighbors: [warehouse, repair_garage, building_supply], requires: [vehicle_access, controlled_threshold, service_space], caution: "An arterial-edge location can fit, but its doors still need usable vehicle approaches."}
  - {id: boat_storage, category: lgt, role: seasonal_storage_and_repair, neighbors: [marina, warehouse, repair_garage], requires: [vehicle_access, outdoor_yard, service_space], caution: "Allow room for moving boats; a dense stack of decorative hulls is not an operating yard."}
  - {id: factory, category: hvy, role: industrial_anchor, neighbors: [warehouse, truck_depot, utility_plant, rowhouse], requires: [freight_interface, utility_service, service_space, controlled_threshold], caution: "Specify what is made, which parts operate, and how the workforce and goods arrive."}
  - {id: refinery, category: hvy, role: large_process_industry, neighbors: [utility_plant, warehouse, truck_depot], requires: [utility_service, controlled_threshold, service_space, landscape_extent], caution: "Use a credible site fragment and separated public edge; never a tiny decorative lot beside a playground."}
  - {id: scrap_yard, category: hvy, role: material_recovery, neighbors: [body_shop, warehouse, truck_depot], requires: [vehicle_access, outdoor_yard, controlled_threshold, separation], caution: "Give material sorting and vehicle movement enough space; do not make every pile arbitrary."}
  - {id: utility_plant, category: hvy, role: infrastructure_anchor, neighbors: [factory, warehouse, truck_depot], requires: [utility_service, service_space, controlled_threshold, vehicle_access], caution: "A small substation, treatment plant, and major generating station are separate subtypes."}
  - {id: rail_station, category: trn, role: passenger_access, neighbors: [office, deli, apartment, shop_house], requires: [public_entry, rail_interface, pedestrian_crossing], caution: "Tracks, platforms, approaches, and service year must agree; freight facilities are separate."}
  - {id: bus_depot, category: trn, role: fleet_storage_and_maintenance, neighbors: [repair_garage, warehouse, office], requires: [vehicle_access, outdoor_yard, staff_access, service_space], caution: "A depot is not a roadside bus stop or automatically a passenger terminal."}
  - {id: truck_depot, category: trn, role: freight_service, neighbors: [warehouse, diner, repair_garage, fuel_station], requires: [vehicle_access, outdoor_yard, freight_interface], caution: "Test turning, queuing, and departure routes with the intended truck."}
  - {id: airport_terminal, category: trn, role: transport_anchor, neighbors: [hotel, rental_car_lot, rail_station, parking_garage], requires: [public_entry, controlled_threshold, stopping_area, goods_access, runway_context], caution: "Landside public space and airside operations are distinct even in a pre-TSA setting."}
  - {id: airport_cargo, category: trn, role: airport_freight, neighbors: [warehouse, truck_depot, airport_operations], requires: [freight_interface, controlled_threshold, vehicle_access, runway_context], caution: "Separate road freight access from aircraft operating areas."}
  - {id: airport_operations, category: trn, role: airfield_support, neighbors: [airport_terminal, airport_cargo, utility_plant], requires: [controlled_threshold, service_space, vehicle_access, runway_context], caution: "Aprons and support areas are parts of a larger airfield system, not public plazas."}
  - {id: parking_garage, category: trn, role: access_support, neighbors: [office, courthouse, hospital, airport_terminal], requires: [vehicle_access, public_entry, service_space], caution: "Provide separate intelligible pedestrian exits and a plausible ramp system."}
  - {id: fuel_station, category: trn, role: vehicle_service, neighbors: [repair_garage, diner, motel, strip_center], requires: [vehicle_access, goods_access, service_space, separation], caution: "Choose a dated format and workable delivery route; do not place pumps in a pedestrian forecourt."}
  - {id: rental_car_lot, category: trn, role: travel_support, neighbors: [airport_terminal, hotel, repair_garage], requires: [public_entry, vehicle_access, outdoor_yard, staff_access], caution: "Vehicle circulation and customer arrival need an actual connection to the travel hub."}
  - {id: barn, category: agr, role: agricultural_work, neighbors: [farmhouse, machine_shed, greenhouse], requires: [field_access, service_space, vehicle_access], caution: "Choose crop, livestock, storage, or mixed use and a historically suitable form."}
  - {id: machine_shed, category: agr, role: agricultural_support, neighbors: [barn, farmhouse, feed_store], requires: [vehicle_access, service_space, field_access], caution: "Doors and yard must accommodate the stored machinery."}
  - {id: feed_store, category: agr, role: rural_trade, neighbors: [hardware, repair_garage, produce_market, barn], requires: [public_entry, goods_access, vehicle_access], caution: "Connect to the agricultural catchment; every customer need not own the farm next door."}
  - {id: produce_market, category: agr, role: local_food_trade, neighbors: [farmhouse, feed_store, diner, greenhouse], requires: [public_entry, goods_access, stopping_area], caution: "Distinguish farm stand, seasonal outdoor market, and permanent market hall."}
  - {id: greenhouse, category: agr, role: horticulture, neighbors: [farmhouse, barn, produce_market], requires: [utility_service, goods_access, service_space, landscape_extent], caution: "Allow working aisles, storage, watering, and seasonal operations."}
```

**Vacancy, construction, and conversion are states, not generic building types.** A closed grocery retains grocery geometry. A vacant house retains domestic scale. A demolished rowhouse lot retains former party-wall evidence, street alignment, and a current owner or custodian. “Abandoned” must not mean unbounded, ownerless, or accessible from every side.

Industrial sites should express a specific production history, transport need, and resource relationship. PHMC identifies those as key parts of industrial landscapes and notes that worker housing can be part of the same historical setting. [S05]

Farm layouts likewise need the relationships among buildings, fields, hedgerows, and landforms. PHMC's agricultural guidance treats the farmstead and surrounding landscape together. Use regional farm references before selecting outbuildings; no single barn package represents every Pennsylvania farm. [S06, S07]

## 6. Explicit adjacency rules and believable exceptions

These rules are author-proposed design decisions. They describe a believable fictional layout, not a list of legally permitted or prohibited land uses. A specific real place or unusual historical condition may justify a different result through the exception contract.

Rule matching is symmetric unless `directional: true`. Match any listed `a` type to any listed `b` type and one of the listed relations. Evaluate all matching rules; fulfill every applicable requirement. If requirements conflict, repair or report the conflict. A `prefer` verdict never cancels a `condition` from another rule. Unlisted pairs receive contextual review, not automatic rejection.

```yaml
pair_rules:
  - id: P01
    match: {a: [airport_terminal, airport_operations, airport_cargo], b: [public_pool], relations: [shared_boundary, same_structure, same_campus]}
    verdict: condition
    requires: ["Identify pool owner and users.", "Keep pool access outside airside operations.", "Explain the shared site or inherited neighborhood edge."]
    evidence: [separate_entrance, pool_identity, operational_boundary]
    repair: "Use a recreation parcel on the landside edge, or replace the use with a hotel-owned pool and a hotel."
  - id: P02
    match: {a: [airport_terminal], b: [hotel, motel], relations: [district_near, same_campus, across_local_street]}
    verdict: prefer
    requires: ["Provide a credible landside walking, road, or shuttle relationship."]
    evidence: [travel_signage, luggage_arrivals, pickup_area]
    repair: "Move lodging to the landside network; do not route hotel guests across operating aprons."
  - id: P03
    match: {a: [hotel, motel], b: [hotel_pool], relations: [same_structure, same_campus, shared_boundary]}
    verdict: prefer
    requires: ["Declare lodging ownership or managed amenity rights.", "Provide guest access, enclosure, and pool maintenance."]
    evidence: [matching_property_identity, guest_threshold, pool_service_access]
    repair: "Connect through lodging grounds or model an actual separate membership facility."
  - id: P04
    match: {a: [clinic, hospital], b: [pharmacy], relations: [same_structure, same_block, district_near, across_local_street]}
    verdict: prefer
    requires: ["Connect patients to the pharmacy by an intelligible public route."]
    evidence: [public_signage, sidewalk_or_lobby, patient_arrival]
    repair: "Remove required travel through staff-only or freight areas."
  - id: P05
    match: {a: [school], b: [playground, sports_field, community_center], relations: [same_campus, shared_boundary, same_block]}
    verdict: prefer
    requires: ["Declare shared or separate ownership and after-hours access."]
    evidence: [school_or_recreation_identity, scheduled_use, managed_gate]
    repair: "Add an appropriate path and boundary instead of merging all grounds."
  - id: P06
    match: {a: [school, playground, public_pool], b: [refinery, scrap_yard, truck_depot], relations: [shared_boundary, same_structure, same_campus]}
    verdict: condition
    requires: ["Demonstrate site-specific or fictional development history.", "Separate primary public approaches from industrial traffic and work areas.", "Represent unresolved nuisance honestly."]
    evidence: [distinct_public_entrance, industrial_boundary, history_trace]
    repair: "Move recreation toward a residential or civic edge; retain industry as a separated neighbor if justified."
  - id: P07
    match: {a: [school], b: [adult_venue, nightclub], relations: [shared_boundary, across_local_street, same_structure]}
    verdict: condition
    requires: ["Use a specific local-history or fictional siting premise.", "Resolve queues, hours, signage, and separate entrances."]
    evidence: [independent_frontages, time_separation, visible_property_limits]
    repair: "Place the venue on a commercial or industrial edge unless the unusual relationship is central and supported."
  - id: P08
    match: {a: [rowhouse, apartment, shop_house], b: [corner_store, deli, pharmacy, barber_salon], relations: [same_structure, shared_boundary, same_block, across_local_street]}
    verdict: prefer
    requires: ["Keep residential entry and commercial servicing workable."]
    evidence: [distinct_address_or_entry, customer_frontage, delivery_arrangement]
    repair: "Separate thresholds, adjust the rear edge, or use an end-of-row commercial bay."
  - id: P09
    match: {a: [apartment, shop_house], b: [restaurant, pizzeria, tavern], relations: [same_structure, shared_boundary]}
    verdict: condition
    requires: ["Explain exhaust, refuse, deliveries, and resident entry.", "Account for the venue's operating hours."]
    evidence: [rear_service_items, exhaust_location, residential_threshold]
    repair: "Move service activity to a credible edge; do not invent perfect sound isolation."
  - id: P10
    match: {a: [rowhouse, twin_house, apartment], b: [tavern], relations: [shared_boundary, same_block, across_local_street]}
    verdict: allow
    requires: ["Scale crowds and exterior noise to a neighborhood establishment."]
    evidence: [small_frontage, local_customer_cues, modest_delivery]
    repair: "If it behaves like a major nightclub, classify and evaluate it as one."
  - id: P11
    match: {a: [rowhouse, apartment, detached_house], b: [nightclub], relations: [shared_boundary, same_structure]}
    verdict: condition
    requires: ["Explain development history, noise exposure, queues, and late departures."]
    evidence: [managed_entry, affected_residential_edge, venue_scale]
    repair: "Reorient the venue or move the main public edge to a commercial street."
  - id: P12
    match: {a: [factory], b: [rowhouse, twin_house, union_hall, tavern], relations: [same_block, shared_boundary, across_local_street, district_near]}
    verdict: condition
    requires: ["Explain the employment and development relationship.", "Give homes and workers usable approaches independent of freight operations."]
    evidence: [worker_route, older_housing_fabric, factory_boundary]
    repair: "Separate goods and residential access while preserving the inherited juxtaposition."
  - id: P13
    match: {a: [warehouse, factory, airport_cargo], b: [truck_depot], relations: [shared_boundary, same_campus, district_near]}
    verdict: prefer
    requires: ["Connect freight facilities to the appropriate road network.", "Verify actual swept paths and staging space."]
    evidence: [loading_interfaces, truck_approaches, logistics_identity]
    repair: "Use smaller vehicles or a larger yard; a nearby road alone does not solve loading."
  - id: P14
    match: {a: [truck_depot, factory, bus_depot], b: [diner, deli], relations: [district_near, across_local_street, same_block]}
    verdict: prefer
    requires: ["Identify staff or driver customer access."]
    evidence: [shift_timing, lunch_trade, separated_food_entry]
    repair: "Put the eatery on the public edge, not inside a controlled work route."
  - id: P15
    match: {a: [church], b: [cemetery, school, community_center], relations: [same_campus, shared_boundary, same_block]}
    verdict: prefer
    requires: ["State whether institutions share ownership and which paths remain public."]
    evidence: [coherent_site_identity, institution_paths, maintenance_access]
    repair: "Preserve individual thresholds when ownership differs."
  - id: P16
    match: {a: [cemetery], b: [nightclub, scrap_yard, truck_depot], relations: [shared_boundary, same_campus]}
    verdict: condition
    requires: ["Explain the inherited edge and preserve distinct circulation and land use."]
    evidence: [cemetery_boundary, separate_gates, contrasting_maintenance]
    repair: "Use a boundary or intermediate service edge; do not turn graves into a loading yard."
  - id: P17
    match: {a: [rail_station], b: [deli, office, shop_house, apartment], relations: [same_block, across_local_street, district_near]}
    verdict: prefer
    requires: ["Provide an actual platform access route and verify that the service exists in the selected year."]
    evidence: [station_entry, dated_transit_identity, commuter_route]
    repair: "Add the missing access connection; tracks alone are not a passenger station."
  - id: P18
    match: {a: [motel], b: [diner, fuel_station, repair_garage], relations: [shared_boundary, across_local_street, district_near]}
    verdict: prefer
    requires: ["Use a coherent roadside arrival pattern and separate property access where needed."]
    evidence: [road_signs, driveway_logic, guest_route]
    repair: "Connect via frontage or local roads rather than an impossible direct ramp."
  - id: P19
    match: {a: [grocery], b: [pharmacy, laundromat, video_store, pizzeria], relations: [same_structure, same_campus, same_block]}
    verdict: prefer
    requires: ["Model separate tenants and any shared parking or servicing rights."]
    evidence: [tenant_frontages, common_walkway, coordinated_loading]
    repair: "Reserve a service edge and keep customer crossings comprehensible."
  - id: P20
    match: {a: [repair_garage, body_shop, building_supply], b: [rowhouse, apartment], relations: [shared_boundary, same_structure]}
    verdict: condition
    requires: ["State work scale and history.", "Preserve residential access outside the working apron."]
    evidence: [trade_identity, work_boundary, residential_front]
    repair: "Reduce workshop scale, reorient the bay, or relocate the heavy work."
  - id: P21
    match: {a: [hospital], b: [factory, nightclub, truck_depot], relations: [shared_boundary, same_structure]}
    verdict: condition
    requires: ["Distinguish patient, service, and less-sensitive campus edges.", "Explain the inherited condition if significant conflict remains."]
    evidence: [public_arrival, service_edge, separate_traffic]
    repair: "Use a less-sensitive edge or increase separation; do not route patients through the conflicting use."
  - id: P22
    match: {a: [farmhouse], b: [barn, machine_shed, greenhouse], relations: [same_campus, across_local_street, shared_boundary]}
    verdict: prefer
    requires: ["Choose an agricultural operation and connect its working buildings to land and roads."]
    evidence: [farm_lane, work_yard, field_relationship]
    repair: "Arrange around actual work, drainage, and terrain instead of a symmetrical decorative ring."
  - id: P23
    match: {a: [feed_store, produce_market], b: [hardware, repair_garage, diner], relations: [same_block, district_near, across_local_street]}
    verdict: prefer
    requires: ["Identify the rural catchment and arrival pattern."]
    evidence: [trade_traffic, seasonal_goods, village_or_crossroads_frontage]
    repair: "Use a market-town node rather than scattering services arbitrarily through fields."
  - id: P24
    match: {a: [marina], b: [restaurant, boat_storage], relations: [same_campus, shared_boundary, same_block]}
    verdict: prefer
    requires: ["Connect the site to suitable water.", "Separate diners and dock pedestrians from active boat handling."]
    evidence: [shoreline_access, dock_route, working_yard]
    repair: "Relocate the yard or public path; a painted blue boundary is not a navigable waterfront."
  - id: P25
    match: {a: [museum, library], b: [park, college, office, restaurant], relations: [same_campus, same_block, district_near]}
    verdict: prefer
    requires: ["Provide public arrival and separate servicing where the program needs it."]
    evidence: [institution_entry, visitor_route, service_threshold]
    repair: "Retain cultural identity without turning the whole neighborhood into a monumental plaza."
  - id: P26
    match: {a: [zoo, aquarium], b: [rowhouse, corner_store, repair_garage], relations: [shared_boundary, same_structure]}
    verdict: condition
    requires: ["Provide a dedicated institutional program and specific site premise.", "Explain how the large use meets smaller neighbors."]
    evidence: [institution_boundary, support_program, scale_transition]
    repair: "Show a campus edge or small annex instead of forcing the whole destination into a normal shop bay."
  - id: P27
    match: {a: [fire_station], b: [community_center, municipal_hall, rowhouse], relations: [same_structure, same_block, shared_boundary]}
    verdict: allow
    requires: ["Preserve apparatus departure geometry in every scheduled use state."]
    evidence: [clear_apron, distinct_hall_entry, emergency_route]
    repair: "Move event parking and furniture outside the vehicle path."
  - id: P28
    match: {a: [courthouse], b: [office, bank, diner, parking_garage], relations: [same_block, district_near, across_local_street]}
    verdict: prefer
    requires: ["Use a plausible administrative center and appropriate public connections."]
    evidence: [office_signs, civic_arrival, lunch_trade]
    repair: "Downgrade to municipal offices if the settlement does not support a courthouse."
  - id: P29
    match: {a: [shopping_mall], b: [farmhouse, barn], relations: [shared_boundary, across_arterial]}
    verdict: condition
    requires: ["Explain development encroachment, retained ownership, or reuse.", "Keep remaining farm access functional."]
    evidence: [old_lane, changed_parcel_edge, contrasting_building_ages]
    repair: "Preserve the surviving parcel and access instead of dropping a barn into mall parking."
  - id: P30
    match: {a: [fuel_station], b: [playground, public_pool, school], relations: [shared_boundary, same_campus]}
    verdict: condition
    requires: ["Separate children or swimmers from fueling and delivery circulation.", "Explain the site history and edge treatment."]
    evidence: [distinct_paths, boundary, independent_entrances]
    repair: "Move the active public frontage to another edge or choose a less-conflicting neighbor."
  - id: P31
    match: {a: [cinema, bowling], b: [restaurant, arcade, tavern, video_store], relations: [same_structure, same_campus, same_block]}
    verdict: prefer
    requires: ["Allow event arrival, queuing, and deliveries without erasing separate tenant identity."]
    evidence: [evening_schedule, coherent_frontages, shared_or_adjacent_arrival]
    repair: "Adjust crowd space and servicing; avoid filling every empty bay with another attraction."
  - id: P32
    match: {a: [refinery, airport_operations, utility_plant], b: [park, public_pool, detached_house], relations: [visual_only, district_near]}
    verdict: allow
    requires: ["Keep the real separation and declared access boundary legible.", "Explain site history when the juxtaposition is important."]
    evidence: [intervening_land_or_roads, distinct_access, distance_cues]
    repair: "Restore the missing spatial separation instead of forbidding the skyline relationship."
```

### 6.1 Exception contract

An exception is not a random-probability roll. It is a small design proposal with visible proof. At least one piece of evidence must concern the physical relationship; two unrelated signs do not count as two convincing explanations.

```yaml
exception_contract:
  required_fields:
    - exception_id
    - affected_instance_ids
    - affected_rule_ids
    - unusual_relationship
    - causal_explanation
    - ownership_or_history
    - access_solution
    - remaining_conflicts
    - visible_evidence
    - gameplay_reason
    - mandatory_check_results
  acceptance_conditions:
    - causal_explanation_changes_the_layout
    - visible_evidence_includes_a_spatial_fact
    - minimum_two_complementary_evidence_items
    - no_non_waivable_failure
    - remaining_conflicts_are_disclosed
  default_budget:
    interpretation: editorial_starting_point
    conspicuous_exceptions_per_small_level: [0, 2]
    budget_is_not_a_probability: true
```

### 6.2 Airport and pool: four different answers

| Proposed layout | Verdict | What makes it work or fail |
|---|---|---|
| Public pool directly opens onto active aircraft apron | Repair or reject the current layout | Public recreation and airfield operations share an unexplained circulation space |
| Terminal near hotel; hotel has enclosed guest pool | Strong fit with normal support checks | Travel demand explains lodging; lodging explains the pool; landside access and ownership explain the connection |
| Older neighborhood pool visible beyond the airport perimeter | Plausible with history and geometry | The pool can predate expansion and have its own roads, entrance, and community |
| Former terminal converted into a recreation center with a pool | Creative conditional fit | Conversion date, new structure and services, former airport traces, and current operating boundaries must all agree |

Do not insert a hotel label solely to excuse the pool. Show a hotel-sized program, guest arrival, rooms or a credible off-map continuation, housekeeping access, and an amenity route. Conversely, a pool beyond an airport fence does not require the invention of a hotel if an older neighborhood already explains it.

### 6.3 Useful creative exceptions

| Combination | Causal explanation | Spatial proof | Potential play value |
|---|---|---|---|
| Chapel and hospital | Small worship space within the institution | Campus signs, public corridor, different acoustic character | A calm orientation room between busier areas |
| Firehouse and banquet hall | Community events share the organization’s property | Separate public hall entrance; clear apparatus apron | A civilian gathering space beside a working service zone |
| Mill and rehearsal rooms | Partial conversion of older industrial floors | New tenant doors in old bays; retained loading geometry | Layered vertical circulation and contrasting occupancy |
| Church and rowhouses | Institution grew within an established neighborhood | Different parcel size and roofline in a continuous street | Strong landmark without a huge empty plaza |
| Market and former station | Transport building retained or adapted for commerce | Old structural spans, dated rail traces, new public arrangement | Memorable indoor circulation tied to the city's history |
| Motel and small pool beside a workshop | Separate roadside businesses developed over time | Property line, guest courtyard, screened work yard | Public frontage and quieter rear route with clear ownership |
| Farmhouse beside new shopping development | Owner retained a parcel as surrounding land changed | Old lane, mature boundary trees, contrasting grades and paving | An irregular edge and a useful landmark |
| Cemetery beside industrial land | Different institutions expanded into neighboring land | Old wall, separate gates, distinct maintenance and sound | A legible transition rather than an arbitrary biome switch |

Reading Terminal Market is a documented example of an unusual relationship with a clear cause: the market opened beneath a railroad terminal in 1893. Its later history also matters—do not infer that the same overhead train operation continued unchanged through a chosen 1990s scene. [S08]

## 7. The spaces between buildings do most of the work

### 7.1 Give every building a front, working edge, and address

Record the following before decorative placement:

- The principal public or residential entrance and the route that reaches it.
- The façade that addresses the street, yard, court, or campus.
- Any secondary entrance, its users, and whether it is normally open.
- Where goods arrive, how they move inside, and how refuse leaves.
- Which side belongs to the neighbor and whether any access agreement exists.
- Which edge is quiet, private, noisy, exposed, or used for work.
- Whether the building is enterable, a shallow interior, or a façade-only background asset.

Not every building needs a separate rear door. A small historic shop may be serviced from the front. Its loading event then uses the actual street and schedule; the generator must not pretend the activity happens through a solid wall.

### 7.2 Connector catalog

A connector requires endpoints, an owner or governing context, allowed users, physical clearance, and an operating state. A path mesh without endpoints is not a connection. A line across private land is not automatically public access.

```yaml
connector_catalog:
  - {id: sidewalk, channels: [pedestrian_public], use: "Continuous street-facing movement between public entrances.", needs: [curb_relationship, entrance_clearance, crossing_connections]}
  - {id: local_street, channels: [vehicle_public, delivery, emergency], use: "Local access and address structure.", needs: [junctions, vehicle_envelope, curb_access]}
  - {id: arterial, channels: [vehicle_public, delivery, emergency], use: "Through movement and commercial visibility.", needs: [controlled_access_points, crossing_strategy, regional_continuation]}
  - {id: public_walk, channels: [pedestrian_public], use: "Park, campus, or civic route where access is explicitly public.", needs: [public_right_or_permission, drainage, endpoints]}
  - {id: private_walk, channels: [resident, pedestrian_authorized], use: "Resident, guest, or member movement within property.", needs: [owner, access_threshold, endpoints]}
  - {id: rear_passage, channels: [resident, pedestrian_authorized, refuse], use: "Narrow access behind domestic or small commercial buildings.", needs: [access_rights, clear_width, termination]}
  - {id: service_lane, channels: [delivery, refuse, emergency, pedestrian_authorized], use: "Shared or private working access at appropriate scale.", needs: [access_rights, vehicle_envelope, loading_clearance]}
  - {id: shared_court, channels: [pedestrian_public, pedestrian_authorized], use: "Common arrival or circulation space between related uses.", needs: [declared_users, frontage_relationship, queue_and_clear_zones]}
  - {id: driveway, channels: [resident, vehicle_public, delivery], use: "Road-to-property vehicle connection with use-specific permissions.", needs: [owner, curb_connection, vehicle_envelope]}
  - {id: loading_apron, channels: [delivery, pedestrian_authorized], use: "Transfer and maneuvering space at a working entrance.", needs: [cargo_scale, sweep_clearance, dock_or_door_match]}
  - {id: parking_walk, channels: [pedestrian_public], use: "Pedestrian route from parking to destination.", needs: [arrival_endpoint, crossing_treatment, clear_destination]}
  - {id: crossing, channels: [pedestrian_public], use: "Declared passage across a road or other conflicting route.", needs: [both_endpoints, visibility, state_control_if_needed]}
  - {id: gate, channels: [pedestrian_authorized, resident, delivery], use: "Explicit change in access permissions.", needs: [owner, dimensions, lock_or_open_state]}
  - {id: stair, channels: [pedestrian_public, pedestrian_authorized, resident], use: "Supported connection between real elevations.", needs: [landings, head_clearance, declared_users]}
  - {id: ramp, channels: [pedestrian_public, pedestrian_authorized, delivery], use: "Grade connection designed for a specified user or vehicle.", needs: [slope, landings_or_turns, load_and_clearance]}
  - {id: footbridge, channels: [pedestrian_public, pedestrian_authorized], use: "Purposeful crossing of water, rail, or grade.", needs: [supports, endpoints, obstacle_clearance]}
  - {id: road_bridge, channels: [vehicle_public, delivery, emergency], use: "Vehicle crossing matched to the road and terrain.", needs: [approaches, supports, vehicle_envelope]}
  - {id: underpass, channels: [pedestrian_public, vehicle_public, delivery], use: "Explicit grade separation under supported infrastructure.", needs: [head_clearance, drainage, sight_and_exit_logic]}
  - {id: interior_link, channels: [pedestrian_public, pedestrian_authorized, resident], use: "Connection between uses with actual common access rights.", needs: [ownership_or_agreement, threshold, level_alignment]}
  - {id: elevated_service_walk, channels: [pedestrian_authorized], use: "Maintenance or industrial circulation at height.", needs: [work_purpose, structural_support, access_and_exit]}
  - {id: farm_lane, channels: [resident, delivery, pedestrian_authorized], use: "Working route among farm road, yards, and land.", needs: [farm_operation, vehicle_envelope, drainage]}
  - {id: desire_path, channels: [pedestrian_public, pedestrian_authorized], use: "Repeated informal movement between actual destinations.", needs: [motivating_shortcut, access_context, wear_consistency]}
```

`channels` lists capabilities a connector can support; an instance must choose its actual channels and permissions. A driveway does not automatically grant public vehicle access. A desire path can represent tolerated use or trespass; record which.

### 7.3 Select the correct street-side relationship

| Pattern | Public face | Working face | Useful in-between space | Avoid |
|---|---|---|---|---|
| Attached commercial street | Shop windows and doors at sidewalk | Rear lane, side passage, or timed front delivery | Narrow passage, small rear court, upper-floor stair | A freestanding parking ring around each tenant |
| Rowhouse block | Stoop, porch, or small front setback | Yard and locally consistent refuse access | Shared passage, garden gate, corner opening | Assuming every rear boundary is a public alley |
| Roadside strip | Sign and arrival visible from road | Rear or side service zone | Shared lot walkway, frontage drive, driveway edge | Customers crossing active loading every time they enter |
| Industrial block | Office or employee gate | Freight docks and process yards | Workforce route, staging area, separate service gate | Giving visitors equal access to every yard |
| Civic campus | Recognizable entrance and approach | Groundskeeping and institutional service edge | Courtyard, lawn, walk, covered arrival | Institutional buildings disconnected by leftover grass |
| Farmstead | House and road arrival | Work yard, barn doors, lanes | Orchard edge, farm lane, turnout | Dense urban curb and sidewalk vocabulary pasted everywhere |
| Recreation ground | Admission, path, or park entrance | Maintenance access | Changing building, shaded waiting, fence line | Equipment filling the entire parcel with no circulation |

### 7.4 Dimensions for initial greyboxing

These are **proposed game-authoring envelopes**, not measured local averages, legal minima, or instructions to resize every real place. They assume human-scale first-person movement. Validate against the actual collision capsule, animation, camera, AI, vehicles, and accessibility goals. Width means **unobstructed usable width**, excluding poles, furniture, open doors, and bins.

| Element | Initial design range | Application |
|---|---:|---|
| Tight single-file secondary passage | 1.0–1.5 m | Brief tension route; avoid as the only high-traffic team route |
| Comfortable two-way pedestrian route | 1.8–3.0 m | Ordinary movement; increase where players stop or turn |
| Busy frontage or team regrouping strip | 3.0–5.0 m | Distinguish moving space from waiting and prop space |
| Small service lane for van-scale work | 3.5–5.0 m | Not automatically adequate for large trucks or turning |
| Small public court | 10–25 m across | Scale to surrounding uses and actual activity |
| Initial focal-point spacing along a main playable route | 20–50 m traveled | A corner, landmark view, threshold, or meaningful choice; not a requirement for constant combat |
| Typical local route choice detour | 10–40 seconds | Tune by movement, stakes, and route differences; not a universal target |

For parcel massing, start with contextual relationships rather than one universal setback. Attached rows may have zero side separation because they share walls. A detached house needs an intentional side condition. Large commercial and industrial buildings need room for the operations they imply. When exact historic scale matters, measure a dated reference instead of using these ranges.

Do not linearly shrink a real site. Keep convincing door heights, vehicle envelopes, stairs, frontage modules, and work zones. Compress long travel distances, duplicate wings, or nonessential land; preserve the functional transitions that explain the destination.

### 7.5 Terrain and drainage

- Roads, lots, floors, and paths must meet their actual elevations. Record retaining walls, stairs, ramps, or cut-and-fill where needed.
- Creeks interrupt routes. A visible crossing needs a bridge, culvert, ford appropriate to the setting, or a deliberate gameplay traversal type.
- Rainwater follows grade. Puddles collect in low spots; downspouts and gutters have destinations; debris can accumulate against obstructions.
- A basement or underpass cannot be casually placed below a water body with no structural or drainage explanation.
- A raised rail line can explain an underpass and a local dead end; it cannot become a paper-thin wall with floating tracks.
- Hedges, woodland, fences, yards, and utility corridors create spatial boundaries with reasons. Use them to define the playable area without making every edge a cliff.

### 7.6 Parking and deliveries without losing the neighborhood

Require a `parking_strategy`, not a large parking lot for every use. Street parking, shared parking, walking, transit, an off-map garage, and limited parking can each fit different places. Do not add current suburban parking assumptions to a tight historic shopping street.

Choose delivery vehicle scale first: handcart, small van, box truck, tractor-trailer, rail car, or specialized vehicle. A dock, lane, and turn that fit a van may fail for a trailer. Test swept paths with the actual vehicle model; a centerline curve by itself is not sufficient.

Loading, customer parking, and refuse collection can share space at different times. If they do, record the schedule and test the overlap state. A coherent temporary blockage can become a play event; an unexplained permanent blockage is a planning error.

## 8. Set dressing: objects should have causes

### 8.1 Use an actor–action–trace model

Place a prop because a person or process caused it to be there. Record who uses it, what surface supports it, how it arrives, where it is kept, and what clear space it needs. “Makes the scene look busy” is not a sufficient reason for a focal prop.

```yaml
dressing_contract:
  required_for_focal_props:
    - prop_id
    - asset_type
    - owner_id
    - purpose
    - placement_anchor
    - orientation_reason
    - support_surface
    - state
    - clearance_group
  optional:
    - user_actor_id
    - delivery_or_storage_origin
    - last_action
    - time_window
    - weather_response
    - maintenance_age_years
    - interaction_id
    - collision_class
    - visibility_class
  collision_classes: [none, movement_only, projectile_only, movement_and_projectile]
  visibility_classes: [no_screening, partial_screening, opaque_screening]
  placement_layers:
    - fixed_infrastructure
    - working_equipment
    - current_activity
    - wear_and_residue
    - rare_story_detail
  randomization_order:
    - choose_owner_and_function
    - choose_eligible_anchor
    - reserve_clearance
    - choose_coherent_asset_family
    - vary_condition_within_history
    - apply_small_bounded_transform_variation
  fail_conditions:
    - no_support_surface
    - blocks_required_route
    - contradicts_use_or_setting_year
    - duplicates_unique_story_item_without_reason
    - signals_interaction_that_does_not_exist
```

Small generic debris can be generated in batches with inherited ownership and placement rules. Do not require a unique biography for each leaf. Apply detailed reasoning where the player reads intent or where movement can be affected.

### 8.2 Causal prop families

| Place or activity | Objects that belong | Where and why | Evidence of ongoing life | Gameplay use or caution |
|---|---|---|---|---|
| Rowhouse front | Chair, planter, doormat, house number, broom | Kept against the owner's frontage or stoop | Swept patch, moved chair, watered pot | Defines ownership; preserve a usable sidewalk |
| Rowhouse rear | Clothesline, refuse containers, small shed, garden tools | Within the actual yard or permitted access strip | Laundry schedule, repaired fence, worn latch | Gives rear route identity without making every fence climbable |
| Corner store | Crate return, small display, delivery dolly, newspaper rack | Near selling or loading activity, outside the main clear zone | Restocking, handwritten sale card | Shelves and windows orient; display clutter is not reliable cover |
| Deli or pizzeria | Menu board, food boxes, apron hooks, delivery bags | Counter, prep space, or departure point | Order collection, steam, trash awaiting pickup | Separate customers from working circulation |
| Diner | Booths, stools, condiment holders, posted specials | Repeated functional layout with wear at high use | Coffee refill, late breakfast, shift customers | Strong visual ordering; do not fill every table equally |
| Tavern | Delivery cases, wall notices, bar stools, coat hooks | Storage and social surfaces with clear service routes | Different occupation at opening and closing | Local hub; alcohol containers are not universal outdoor clutter |
| Grocery | Carts or baskets, price cards, rolling stock cages, cartons | Customer threshold and actual restocking routes | Partly stocked shelf, active checkout | Distinguish shopping circulation from the service yard |
| Video store | Return slot, membership notice, shelving, promotion stand | Entrance and counter support the rental transaction | Returns to sort, staff-selected display | Period-specific identity through function rather than a pile of VHS tapes |
| Laundromat | Baskets, folding table, chairs, soap dispenser | Along washing, waiting, and folding sequence | Different machine states, folded stack | Machines form predictable spaces; preserve door clearance |
| Repair garage | Tool chest, air hose, jack, tires, parts bins | Tied to an actual work bay and current job | Removed wheel, swept working patch, parts delivery | Plausible cover and blockers; do not leave every tool in the travel path |
| Body shop | Vehicle panels, masked work, racks, stored cars | Defined preparation, storage, and working areas | One repair in progress, changing vehicle inventory | Useful large shapes; ventilation and separation still need logic |
| Warehouse | Pallets, racks, labels, carts, packing area | Flow from delivery to storage to dispatch | Empty return stacks, partial order, active dock | Explain crate scale and contents; avoid uniform crate mazes |
| Factory employee edge | Time notice, bicycle rack, lunch bench, lockers | Between staff arrival and work | Shift change, break, posted maintenance | Adds ordinary human scale to a large industrial site |
| Factory freight edge | Dock bumpers, bollards, hoses, bins, service equipment | Protects and supports actual operations | Tire wear, loaded bay, repaired impact damage | Strong encounter geometry that has a reason to exist |
| Office | Directory, desk phone, filing cabinets, notice board | Public orientation and staff workflow | Open desk, coat, delivered mail | Good wayfinding; do not make every office a server room |
| Clinic | Reception seats, appointment notices, paper records, supply trolley | Arrival, waiting, and clinical support | Staff restocking, patients waiting | Calm public approach contrasts with service spaces |
| Church or hall | Bulletin, folding chairs, coat rack, event supplies | Entry and spaces used by the actual event | Setup, rehearsal, cleanup | Flexible gathering space; activity follows a schedule |
| Cemetery | Maintenance cart, flower bins, tools, water point | Gate, service building, or active maintenance area | Fresh flowers beside older plantings | Distinct routes and atmosphere; avoid indiscriminate debris |
| School | Bicycle racks, notices, sports storage, maintenance cart | Entry, grounds, service edge | Dismissal, practice, custodial work | Keep pupil and service routes understandable |
| Pool | Lifeguard furniture, lane gear, towel storage, posted hours | Edge, changing area, and plant access | Swimmers, cleaning, seasonal cover | Wet surfaces and enclosure explain movement; chairs are not structural barriers |
| Park or field | Bench, drinking point, bins, backstop, grounds equipment | At actual gathering and maintenance locations | Mown paths, worn goalmouth, scheduled game | Open space can be useful; do not clutter the playing surface |
| Station or bus stop | Timetable, bench if appropriate, shelter if appropriate, litter bin | Where people actually board or wait | Arrival pulse, changing queue, departing vehicle | A transit stop needs a service relationship, not a shelter on a random wall |
| Hotel or motel | Luggage cart, room numbers, housekeeping cart, vending | Guest routes and back-of-house storage | Check-in, room turnover, shuttle arrival | Amenities share property identity; servicing supports alternate routes |
| Marina | Coiled lines, life rings, hose points, boat stands | Different objects for dock, repair yard, and storage | Launch preparation, maintenance, seasonal storage | Water edges require clear traversal rules |
| Farm | Feed containers, stacked materials, implements, wash station | Connected to the selected crop or livestock work | Harvest, feeding, repair, seasonal storage | Objects must support the chosen operation, not generic rural decoration |
| Construction or demolition | Fencing, materials, equipment, debris separation | Within a declared work area with access | Active phase and a plausible next task | Temporary routes and changed sightlines need their own state tests |

### 8.3 Shared edges tell especially useful stories

- A store's rear deliveries and an apartment's resident entrance can use different parts of one court. Changes in paving, lighting, signs, and storage show the division.
- A service lane can contain neat commercial bins, one repaired fence, and a carefully maintained garden behind another property. Maintenance follows owners, not a global dirt slider.
- A bus stop produces waiting and short bursts of activity. Nearby food retail may respond to that demand; not every stop needs a shop.
- A shared parking lot can have different tenant signs, worn crossing paths, and one disputed or blocked space. Keep the operational consequences legible.
- A former loading opening converted into a shop window explains both unusual architecture and a change of use.
- A long-standing tree can explain a bent path or irregular wall. It should not appear as random noise in the middle of a loading turn.

### 8.4 Variation rules that preserve human intent

Align shelves to walls, chairs to tables, cars to parking logic, and pallets to handling space. Imperfection comes after that intent: one moved chair, a replaced fence panel, a bent sign, a different curtain, a patch over a utility cut.

Use correlated variation. One owner tends to buy related chairs; one resurfacing job affects a coherent patch; one delivery creates a local group of matching cartons. Avoid independent rotation and material randomization on every object.

Leave some space empty because it is needed: turning, queuing, unloading, mowing, visibility, assembly, or simply an uncluttered front step. Empty space should have a role, but it does not always need a visible prop proving that role.

### 8.5 Activity, time, and weather

```yaml
activity_model:
  entity_fields: [actor_group, home_or_origin, destination, activity, schedule, access_permissions]
  scene_states: [normal_open, normal_closed, delivery_active, event_active, disrupted]
  example_day:
    morning: [commuting, opening_shops, deliveries, school_arrival]
    midday: [lunch_trade, errands, maintenance]
    afternoon: [school_dismissal, shopping, shift_change]
    evening: [dining, recreation, meetings, home_activity]
    late_night: [selected_late_venues, cleaning, sparse_traffic]
  season_effects:
    summer: [pool_operation_if_open, outdoor_seating_where_owned, vegetation_growth]
    autumn: [leaf_accumulation_at_edges, sports_or_school_schedule, changing_daylight]
    winter: [snow_storage_where_present, cleared_priority_paths, reduced_outdoor_activity]
    spring: [grounds_work, wet_soil_tracks, seasonal_reopening]
  low_cost_representation:
    - scheduled_sound
    - selected_lit_windows
    - one_visible_worker
    - changing_delivery_or_parking_state
    - evidence_of_recent_activity
```

Do not activate every possible event simultaneously. A school dismissal, late-night club queue, Sunday service, pool opening, and full factory shift change need a compatible date and time if they appear together.

Rain darkens exposed surfaces unevenly, creates shelter-seeking behavior, and moves waiting activity under real cover. Snow piles go somewhere and may obstruct parking or visibility. Windblown debris collects at edges and obstacles. These effects should change routes and maintenance evidence consistently.

Life does not require a large simulated population. One purposeful action, a credible sound source, and the visible result of work can communicate more than many NPCs walking random loops.

## 9. Make the year visible through operation

### 9.1 Period rules

Choose a year between 1990 and 1999. Use the building's construction and alteration history independently of that date. A Victorian house, a 1950s diner, a 1970s storefront renovation, and a 1994 addition can coexist; their relationships should reveal why.

| Subject | Useful period direction | What requires checking or exclusion |
|---|---|---|
| Communication | Landlines, payphones where demand supports them, paper notices, fax machines, pagers in relevant work | Smartphone navigation, app pickup, QR-centered transactions, contemporary digital interfaces |
| Retail | Small neighborhood businesses, supermarkets, malls, strip centers, rental and repair businesses | Today's exact tenant lists, brands, sign designs, checkout interfaces, and business models |
| Transit | Dated route identities, schedules, vehicle types, tickets, stations, and waiting patterns | Present-day route branding or stations assumed to have existed unchanged |
| Airport | Period terminals, landside arrival, airline operations, controlled airside access | TSA branding and later terminal expansions inserted into the 1990s |
| Vehicles | A mixture of older and recent-for-the-year vehicles matched to owners and work | Treating every vehicle as either a pristine new 1995 car or an antique |
| Office equipment | Paper storage and period equipment chosen by business scale | Modern ultrathin displays, ubiquitous laptops, modern Wi-Fi signage |
| Advertising | Dated graphic styles and transaction details; business signs that have a reason to be visible | A universal neon palette, identical faded posters, or modern web and social conventions |
| Lighting | Different owners and installation eras; older fixtures mixed with replacements | One identical contemporary LED fixture family across every street, yard, and room |
| Accessibility changes | Site- and date-specific alterations, such as an added entrance route | Assuming all old buildings were either unchanged or completely rebuilt by a single year |
| Utilities | Infrastructure following streets, lots, and service needs | Random utility poles, cables without endpoints, or rooftop equipment with no building function |
| Vacant property | Specific former use, closure date, retained ownership, and remaining maintenance | Making every neighborhood uniformly ruined or every disused site freely accessible |

A later feature is not justified by being physically possible. Its presence must fit the selected place, year, business, and adoption history. Conversely, some electronic signs, computers, surveillance, and advanced equipment existed in the period; do not remove technology categorically when a suitable dated reference supports it.

### 9.2 Verified date examples

- PHL's official history places the opening of International Terminal A in March 1991, the consolidated Terminal B/C in June 1998, Terminal F in June 2001, and Terminal A-West in May 2003. A 1995 scene must not use the later facilities as already operating. [S09]
- SEPTA's Airport Line began service in 1985, so airport rail access can fit a 1990s regional setting. Verify the particular station and arrangement represented rather than copying a current map. [S10]
- The legislation establishing TSA dates to November 19, 2001. Exclude TSA branding from a 1990s scene; this does not mean airports previously had no screening or controlled areas. [S11]
- DVRPC provides a 1990 land-use dataset. Use date-matched regional evidence when reconstructing a place; a current parcel map alone cannot establish what occupied a site in 1995. [S12]

These examples show why exact-year checks matter. They are not a complete period asset blacklist.

```yaml
period_validation:
  asset_record_fields:
    - asset_id
    - depicted_use
    - earliest_supported_year
    - latest_supported_year_or_null
    - geographic_scope
    - reference_id_or_declared_fiction
  unknown_dates: flag_for_review
  factual_date_locks:
    - {feature: phl_terminal_a_original_international_open, earliest_year: 1991, reference: S09}
    - {feature: phl_consolidated_terminal_bc_open, earliest_year: 1998, reference: S09}
    - {feature: phl_terminal_f_open, earliest_year: 2001, reference: S09}
    - {feature: phl_terminal_a_west_open, earliest_year: 2003, reference: S09}
    - {feature: septa_airport_line_service, earliest_year: 1985, reference: S10}
    - {feature: tsa_as_an_agency, earliest_year: 2001, reference: S11}
  within_year_precision:
    policy: consult_source_for_month_and_day_if_scene_precedes_opening
  general_policy:
    later_real_feature: reject_if_year_locked
    invented_business: allow_if_its_operation_and_assets_fit_period
    borrowed_modern_site_layout: require_historical_verification_or_mark_as_fictional_composite
```

### 9.3 Pennsylvania without caricature

Use location, infrastructure, housing form, terrain, and institutions before novelty signs. Not every Delco street needs every regional reference. Not every rural Pennsylvania farm is Amish. Agricultural practice, cultural identity, wealth, and maintenance must come from an actual premise or reference, not random assignment.

Show care and ordinary life across income levels. A small or aging property can be meticulously maintained; a prosperous operation can have a messy working yard. Do not use poverty, ethnicity, religion, or disability as a shortcut for disorder or criminality.

When using fictional satirical businesses, keep their underlying operations recognizable. The joke can change the name and advertising; it should not erase why the building has a customer entrance, a kitchen, a delivery point, and neighbors.

## 10. Turn a believable place into a good level

### 10.1 Separate the world graph from the playable graph

The world graph contains all modeled connections and their normal users. The playable graph contains the routes available to players in each game state. Some buildings can be visible but not enterable. Some working routes can become playable through a declared mission event. Keep both graphs coherent.

An inaccessible building still needs plausible occupation, street address, and service logic. Its interior can remain unmodeled. An off-map road should read as continuing somewhere; it does not need a full simulated town at the far end.

### 10.2 Use hubs that already have a reason to gather people

Good hubs include a commercial intersection, station forecourt, small civic square, shopping-center walkway, shared industrial yard, motel court, or farm work yard. They differ in ownership and access; do not treat them as the same plaza mesh.

Each spoke should offer a recognizable destination or function: front entrance, resident street, service edge, upper floor, maintenance area, or exit route. Give spokes different spatial character and a relationship to the hub. A hub is not useful merely because five corridors meet there.

Secondary loops can link two spokes through a believable rear lane, connected courtyard, shared institutional interior, or terrain route. Avoid making every property permeable; one or two well-explained cross-connections can provide strong choice while the rest remain convincing buildings.

### 10.3 Design route choice as a tradeoff

| Route family | Place-based explanation | Distinct experience | Required check |
|---|---|---|---|
| Public frontage | Normal customer or resident approach | Clear orientation, visibility, potential activity | Entrance actually connects to the destination |
| Service approach | Deliveries, staff, maintenance | Work spaces, tighter turns, different cover | Ownership, gate state, vehicle clearance, and route permissions |
| Shared institutional interior | Related uses within one campus or building | Controlled thresholds, calmer or more complex rooms | Shared ownership or access agreement and aligned floor levels |
| Upper route | Existing stair, mezzanine, raised street, or maintenance access | Overlook, exposure, altered approach | Structural support, entry, exit, collision, and AI handling |
| Landscape route | Park edge, creek crossing, field lane, embankment path | Open exposure or vegetation screening | Terrain, permissions, crossing feasibility, and weather state |

Two doors five meters apart leading into the same unbranched corridor are not two meaningful routes. Alternatives should differ in visibility, travel time, timing, access requirement, vertical position, or interaction. Not every route needs equal length or tactical value at every moment.

### 10.4 Support four players without making everything oversized

- Provide regrouping space at important decisions and before long narrow sections.
- Avoid putting a frequently used interaction exactly where it blocks everyone else's only route.
- Test a player stopping, turning, reviving, carrying an objective, or being joined by teammates in relevant places.
- Preserve some tight passages when they create useful tension; give them readable ends and sensible encounter behavior.
- Do not force permanent team splits unless the mission explicitly supports them.
- Ensure required transitions, exits, and state changes work for all players; an attractive route that strands one participant is a failure.
- Decide whether AI uses the same routes, a subset, or additional declared links. Do not assume a decorative stair automatically provides valid navigation.

### 10.5 Verticality from the setting

Use a sloped street with a lower rear entrance, a split-level shop, a warehouse mezzanine, a supported loading platform, a church balcony, a motel's exterior gallery, an institutional stair, a raised rail corridor, or a bank-barn relationship to grade where the selected building type supports it.

Every playable upper space needs a reason to exist and a way to reach and leave it. Floors require support; stairs need landings; roof equipment needs maintenance access. Avoid universal rooftop bridges, identical fire escapes on every building, or ladders added only because the player needed another route.

An overlook should alter decisions, not dominate the entire level without response. Test what it reveals, who can reach it, what obstructs it, and how it changes the encounter. A high position can be memorable even if it overlooks only one yard.

### 10.6 Cover, concealment, and collision

Distinguish movement obstruction, visual screening, and projectile protection in the asset data. A hedge may screen a view without stopping bullets. A chair may slow movement without providing protection. A substantial wall may provide both. The project's actual simulation decides these properties.

Place durable obstructions where people need them: retaining walls on grade, masonry property boundaries, loading structures, columns supporting roofs, parked vehicles in real parking or work areas. Use smaller props to communicate use, not to manufacture a battlefield of waist-high boxes.

Do not assume that every parked vehicle, pallet, fence, or vending machine gives identical cover. Collision should match the visual promise closely enough that players learn consistent rules.

### 10.7 Pacing and legibility

Alternate movement, orientation, choice, commitment, activity, and breathing room. Spatial rhythm can come from a narrow street opening into a court, an interior revealing a rear yard, or a noisy road giving way to a sheltered institutional path. Every contrast does not require a different building category.

Use one dominant landmark for a small area and secondary cues at decisions. A church tower, water tank, theater marquee, unusual roof, or industrial stack can orient players. Support this with addresses, storefront identities, consistent material families, and actual views of destinations.

Avoid making every façade equally loud. If every building is the hero building, players lose both hierarchy and a believable neighborhood.

### 10.8 Scope and performance

Choose which buildings need full interiors, shallow visible rooms, or façade-only treatment. Make the decision from mission use, sightlines, and expected player access. A closed building may be essential to the place even when its interior is not worth building.

Use repeated building modules with intentional variations in tenancy, condition, additions, and signage. Reserve unique geometry for meaningful silhouettes and routes. Keep collision simple where detailed contact does not matter; avoid making small decorative clutter a navigation obstacle.

Plan visibility breaks around streets, terrain, courtyards, and building masses. Treat lights, animated activity, transparency, audio, and AI as budgeted features. This document proposes spatial design; actual rendering and simulation performance must be measured in the target engine and hardware.

### 10.9 Editable gameplay targets

```yaml
gameplay_defaults:
  purpose: starting_targets_for_a_small_cooperative_mission
  target_enterable_buildings: [3, 8]
  ordinary_nonhero_building_share: [0.50, 0.75]
  share_denominator: all_building_instances_including_facade_only
  share_exclusions: [landscape_features, connector_objects, tenant_components]
  primary_landmarks_per_local_area: [1, 2]
  meaningful_approaches_to_primary_mission_area: 2
  return_loop: preferred
  simultaneous_choices_at_major_decision: [2, 3]
  exceptions:
    - "A focused interior mission may use one building."
    - "An intentional single-access destination needs an explicit pacing and team-movement solution."
    - "Campus or industrial missions may use repeated support structures instead of residential filler."
  route_tests:
    - group_can_regroup_at_major_decisions
    - objective_interaction_does_not_accidentally_seal_only_route
    - alternate_approaches_differ_meaningfully
    - required_paths_work_in_each_required_mission_state
    - visible_destinations_have_consistent_access_signals
```

These numbers are defaults to tune in playtests, not minimum content quotas. The narrowest believable version of a mission is often better than adding several unrelated destinations merely to hit a range.

## 11. Reusable neighborhood and site recipes

Each recipe is a starting relationship, not a mandatory shopping list. `ordinary_fabric` repeats as needed. `connectors` refer to Section 7. A recipe may omit a secondary use if the remaining place still works. Do not combine all recipes in one level.

```yaml
cluster_templates:
  - id: C01_corner_services
    profiles: [philly_rowhouse, mature_inner_suburb]
    anchor: corner_store
    supporting: [pizzeria, laundromat]
    ordinary_fabric: [rowhouse, shop_house]
    connectors: [sidewalk, local_street, rear_passage]
    evidence: [store_delivery, domestic_frontages, tenant_changes]
    play: "Readable corner hub; one credible rear connection; repeated houses establish scale."
    avoid: "A separate parking moat around every shop."
  - id: C02_borough_civic_center
    profiles: [borough_center]
    anchor: municipal_hall
    supporting: [library, bank, diner, post_office]
    ordinary_fabric: [office, shop_house]
    connectors: [sidewalk, shared_court, local_street]
    evidence: [civic_notices, business_hours, lunchtime_trade]
    play: "Public arrival hub with secondary routes behind ordinary commercial fronts."
    avoid: "An unrelated monumental institution on every corner."
  - id: C03_station_neighborhood
    profiles: [rail_suburb, mature_inner_suburb]
    anchor: rail_station
    supporting: [deli, pharmacy, office]
    ordinary_fabric: [apartment, twin_house, shop_house]
    connectors: [sidewalk, crossing, parking_walk]
    evidence: [dated_timetables, commuter_arrivals, continuous_station_access]
    play: "Station landmark and distinct paths along either side of the transport barrier."
    avoid: "Public routes casually crossing tracks wherever convenient."
  - id: C04_industrial_residential_edge
    profiles: [river_industry, creek_mill_edge]
    anchor: factory
    supporting: [warehouse, tavern, union_hall]
    ordinary_fabric: [rowhouse, workshop]
    connectors: [local_street, service_lane, sidewalk, gate]
    evidence: [shift_change, freight_edges, older_housing]
    play: "Contrast public street, worker route, and working yard without erasing boundaries."
    avoid: "A fictional buffer that makes all historical conflict disappear."
  - id: C05_repair_and_trade_strip
    profiles: [arterial_strip, mature_inner_suburb]
    anchor: repair_garage
    supporting: [hardware, building_supply, diner]
    ordinary_fabric: [workshop, office]
    connectors: [driveway, service_lane, sidewalk, loading_apron]
    evidence: [jobs_in_progress, trade_deliveries, owner_specific_storage]
    play: "Different yard shapes and indoor work areas create choices tied to actual trades."
    avoid: "Every bay opening into the same unusable vehicle bottleneck."
  - id: C06_neighborhood_recreation
    profiles: [postwar_suburb, mature_inner_suburb]
    anchor: community_center
    supporting: [public_pool, sports_field, playground]
    ordinary_fabric: [detached_house, twin_house]
    connectors: [public_walk, private_walk, gate, local_street]
    evidence: [opening_schedule, changing_facilities, grounds_maintenance]
    play: "Open field, enclosed pool, and community interior provide distinct spaces."
    avoid: "All activities occupying one unbounded surface or operating out of season."
  - id: C07_parish_block
    profiles: [philly_rowhouse, mature_inner_suburb, borough_center]
    anchor: church
    supporting: [school, community_center]
    ordinary_fabric: [rowhouse, twin_house]
    connectors: [sidewalk, shared_court, gate, private_walk]
    evidence: [shared_institution_identity, event_notices, separate_school_access]
    play: "Landmark, gathering court, and service edge form a compact coherent complex."
    avoid: "Treating shared religious identity as automatic public access to every room."
  - id: C08_roadside_lodging
    profiles: [arterial_strip, airport_edge]
    anchor: motel
    supporting: [diner, fuel_station, hotel_pool]
    ordinary_fabric: [office, repair_garage]
    connectors: [driveway, private_walk, parking_walk, service_lane]
    evidence: [room_turnover, traveler_arrivals, enclosed_guest_amenity]
    play: "Guest court, service strip, and neighboring business offer distinct routes."
    avoid: "A pool that substitutes for the hotel's entire operating program."
  - id: C09_small_shopping_center
    profiles: [arterial_strip, postwar_suburb]
    anchor: strip_center
    supporting: [grocery, video_store, pharmacy, pizzeria]
    ordinary_fabric: [barber_salon, office]
    connectors: [parking_walk, shared_court, service_lane, driveway]
    evidence: [tenant_signs, cart_or_basket_logic, delivery_timing]
    play: "Public walkway and rear service spine offer different connected routes."
    avoid: "Counting each tenant as an unrelated freestanding building."
  - id: C10_evening_main_street
    profiles: [borough_center, philly_rowhouse]
    anchor: cinema
    supporting: [restaurant, tavern, arcade]
    ordinary_fabric: [shop_house, apartment, office]
    connectors: [sidewalk, local_street, rear_passage]
    evidence: [show_times, staggered_open_hours, lived_in_upper_floors]
    play: "A recognizable evening destination with quiet edges and residential consequences."
    avoid: "Maximum crowds and bright signage across every façade."
  - id: C11_hospital_edge
    profiles: [institutional_campus, mature_inner_suburb]
    anchor: hospital
    supporting: [clinic, pharmacy, office, deli]
    ordinary_fabric: [apartment, office]
    connectors: [public_walk, interior_link, service_lane, driveway]
    evidence: [patient_arrival, staff_route, goods_service]
    play: "Choose one campus edge or building cluster; preserve distinct public and service journeys."
    avoid: "Compressing an entire regional medical center into a single tiny footprint."
  - id: C12_creek_mill_conversion
    profiles: [creek_mill_edge]
    anchor: factory
    supporting: [workshop, print_shop, office]
    ordinary_fabric: [rowhouse, warehouse]
    connectors: [road_bridge, service_lane, stair, public_walk]
    evidence: [old_industrial_structure, dated_tenant_conversion, creek_response]
    play: "Grade, former loading levels, and selective reuse create justified verticality."
    avoid: "Pretending the mill can operate without its terrain and transport relationship."
  - id: C13_rural_crossroads
    profiles: [rural_market_town]
    anchor: feed_store
    supporting: [hardware, diner, repair_garage, fire_station]
    ordinary_fabric: [detached_house, workshop]
    connectors: [local_street, driveway, sidewalk, farm_lane]
    evidence: [agricultural_trade,local_notice_board,seasonal_work]
    play: "Compact service node with land and road continuations beyond the core."
    avoid: "A detached urban downtown surrounded by decorative crop texture."
  - id: C14_working_farm
    profiles: [farmstead]
    anchor: barn
    supporting: [farmhouse, machine_shed, greenhouse]
    ordinary_fabric: [machine_shed]
    connectors: [farm_lane, driveway, gate, private_walk]
    evidence: [chosen_farm_operation,working_fields,maintenance]
    play: "Work yard organizes structures; landforms and farm tasks create movement choices."
    avoid: "All barn types, animals, and crop systems combined without a farm premise."
  - id: C15_marina_restaurant
    profiles: [river_industry, institutional_campus]
    anchor: marina
    supporting: [restaurant, boat_storage, repair_garage]
    ordinary_fabric: [office, workshop]
    connectors: [private_walk, public_walk, driveway, gate]
    evidence: [water_access,public_dining,seasonal_boat_work]
    play: "Public restaurant and working waterfront share an area with clear limits."
    avoid: "Assuming every riverbank is a usable harbor."
  - id: C16_airport_landside_edge
    profiles: [airport_edge]
    anchor: airport_terminal
    supporting: [hotel, hotel_pool, rental_car_lot, parking_garage]
    ordinary_fabric: [office, warehouse]
    connectors: [sidewalk, parking_walk, local_street, gate]
    evidence: [traveler_access,hotel_ownership,airfield_boundary]
    play: "Travel hub plus guest amenity; airport operations remain a distinct system."
    avoid: "Using the apron as a public shortcut between leisure and lodging."
  - id: C17_administrative_lunch_district
    profiles: [borough_center]
    anchor: courthouse
    supporting: [office, bank, diner, print_shop]
    ordinary_fabric: [shop_house, apartment]
    connectors: [sidewalk, crossing, rear_passage]
    evidence: [public_services,professional_offices,weekday_schedule]
    play: "Civic destination with ordinary streets and a quieter after-hours state."
    avoid: "An administrative institution with no population or regional role to support it."
  - id: C18_large_cultural_campus_edge
    profiles: [institutional_campus]
    anchor: museum
    supporting: [park, restaurant, college]
    ordinary_fabric: [office]
    connectors: [public_walk, shared_court, service_lane, interior_link]
    evidence: [visitor_arrival,collection_service,grounds_work]
    play: "One public institution, one landscape edge, and one working edge make a readable slice."
    avoid: "Adding zoo, aquarium, museum, stadium, and airport merely because each is interesting."
```

Recipe identifiers define the relationship, not a real municipality or actual business inventory. When a recipe uses a multi-tenant shell, model the shell and tenant components without overlapping or double-counting full building masses.

## 12. Output contract for a layout brain

### 12.1 Required output

Return structured decisions before producing final geometry. Every important neighbor relationship must be explainable in one concrete sentence. Every claimed route must later be backed by geometry and a navigation check.

```yaml
output_contract:
  required_top_level:
    - plan_id
    - stage
    - setting
    - assumptions
    - place_explanation
    - development_history
    - owners
    - parcels
    - buildings
    - components
    - relationships
    - connectors
    - playable_graph
    - activity_states
    - focal_props
    - accepted_exceptions
    - validation_report
  stages: [semantic_concept, geometric_greybox, tested_level]
  id_policy: unique_stable_ascii_identifiers
  references: all_referenced_ids_must_resolve
  geometry_policy:
    semantic_concept: missing_geometry_allowed_if_reported_unrun
    geometric_greybox: footprints_elevations_and_route_geometry_required
    tested_level: actual_engine_validation_and_playtest_evidence_required
  parcel_fields:
    required: [id, owner_id, use, access_rights, geometry_status]
    greybox_required: [boundary_polygon_xy_m, ground_elevation_reference]
  building_fields:
    required: [id, archetype_id, parcel_id, owner_id, occupancy_state, representation, entrances, support_providers, history]
    greybox_required: [footprint_polygon_xy_m, base_z_m, height_m, floor_elevations_m]
  building_representations: [full_interior, partial_interior, facade_only]
  occupancy_states: [operating, temporarily_closed, vacant, under_construction, partly_occupied]
  component_fields:
    required: [id, parent_building_or_parcel_id, use, owner_id, access_class]
  relationship_fields:
    required: [id, a_id, b_id, spatial_relation, functional_relations, verdict, because, applicable_rule_ids, evidence_ids]
    district_near_required: [route_distance_m_or_null, distance_status, catchment_reason]
  functional_relation_fields:
    required: [kind, from_id, to_id]
    kind_enum: relationship_vocabulary.functional_relations
    endpoint_policy: both_ids_must_be_the_relationship_endpoints
  connector_fields:
    required: [id, connector_type, from_id, to_id, owner_or_authority_id, channels, permitted_users, state_rules, geometry_status]
    greybox_required: [path_xyz_m, minimum_clear_width_m, minimum_clear_height_m]
    vehicle_route_required: [vehicle_envelope_id, swept_path_check]
  prop_fields: dressing_contract.required_for_focal_props
  validation_result_fields: [check_id, status, evidence, affected_ids, required_repair]
  validation_statuses: [pass, fail, unrun, not_applicable]
  approval_policy:
    semantic_concept: may_advance_with_declared_geometry_checks_unrun
    geometric_greybox: cannot_advance_with_mandatory_geometry_or_graph_failures
    tested_level: requires_all_applicable_mandatory_checks_passed
```

The lists above define a minimum contract, not a complete JSON Schema. In implementation, validate types, enums, references, and state transitions with a real schema and explicit geometry tests. Add project fields under a versioned namespace instead of silently changing these meanings.

### 12.2 A worked semantic plan: ordinary Delco commercial edge

**Fictional premise:** a small hardware store grew alongside an older residential street. A garage occupies a neighboring trade parcel. A deli serves residents and workers. The mission concerns a package in the hardware stockroom. This is one commercial fragment within a larger neighborhood, not a whole town containing only four buildings.

The following is a **bounded logical example**, not a complete `output_contract` payload or a tested map. It demonstrates the relationship, ownership, access-state, and graph fields that tend to be lost in free-form prompts. Geometry and all unshown normal-world routes remain to be authored and checked.

```yaml
semantic_example:
  plan_id: mercer_street_trade_edge
  stage: semantic_concept
  setting: {year: 1995, county: Delaware, profile: mature_inner_suburb, season: late_summer, local_time: "16:30"}
  assumptions:
    - "Fictional composite, not a reconstruction of an actual property."
    - "The service lane has an explicit shared-access agreement."
    - "The mission grants players permission to use the hardware stockroom and participating trade yards."
  owners:
    - {id: own_borough, role: public_street_authority}
    - {id: own_hardware, role: hardware_operator}
    - {id: own_garage, role: garage_operator}
    - {id: own_deli, role: deli_operator}
    - {id: own_residents, role: residential_property_owners}
    - {id: own_lane_group, role: recorded_shared_access_group}
  buildings:
    - {id: b_hardware, archetype_id: hardware, owner_id: own_hardware, representation: full_interior}
    - {id: b_garage, archetype_id: repair_garage, owner_id: own_garage, representation: partial_interior}
    - {id: b_deli, archetype_id: deli, owner_id: own_deli, representation: full_interior}
    - {id: b_house_01, archetype_id: rowhouse, owner_id: own_residents, representation: facade_only}
    - {id: b_house_02, archetype_id: rowhouse, owner_id: own_residents, representation: facade_only}
    - {id: b_house_03, archetype_id: rowhouse, owner_id: own_residents, representation: facade_only}
    - {id: b_house_04, archetype_id: rowhouse, owner_id: own_residents, representation: facade_only}
  relationships:
    - id: rel_trade_edge
      a_id: b_hardware
      b_id: b_garage
      spatial_relation: same_block
      functional_relations:
        - {kind: supplies, from_id: b_hardware, to_id: b_garage}
      verdict: allow
      because: "The hardware shop serves nearby trades and residents; the garage reaches the shared lane under a declared agreement."
      applicable_rule_ids: []
      evidence_ids: [feature_trade_loading, feature_shared_lane_notice]
    - id: rel_residential_edge
      a_id: b_garage
      b_id: b_house_01
      spatial_relation: shared_boundary
      functional_relations:
        - {kind: historically_predates, from_id: b_house_01, to_id: b_garage}
      verdict: condition
      because: "The house predates the garage; its street entrance remains independent of the work apron."
      applicable_rule_ids: [P20]
      evidence_ids: [feature_domestic_threshold, feature_yard_boundary]
  features:
    - {id: feature_trade_loading, owner_id: own_hardware, fact: "Goods handling occupies the hardware rear edge."}
    - {id: feature_shared_lane_notice, owner_id: own_lane_group, fact: "A shared lane is physically continuous and marked for participating users."}
    - {id: feature_domestic_threshold, owner_id: own_residents, fact: "The house has a separate street-facing stoop and entrance."}
    - {id: feature_yard_boundary, owner_id: own_garage, fact: "A wall and gate define the work yard; they do not claim to eliminate its noise."}
  states: [normal_open, mission_authorized, delivery_active]
  graph_nodes:
    - {id: n_arrival, function: public_arrival}
    - {id: n_corner, function: local_landmark_and_regroup}
    - {id: n_shop, function: hardware_sales_floor, building_id: b_hardware}
    - {id: n_stock, function: hardware_stockroom, building_id: b_hardware}
    - {id: n_west_lane, function: shared_lane_west}
    - {id: n_rear_yard, function: hardware_service_yard}
    - {id: n_garage_apron, function: garage_working_edge, building_id: b_garage}
    - {id: n_exit, function: east_street_return}
  graph_edges:
    - {id: e01, endpoints: [n_arrival, n_corner], connector_type: sidewalk, bidirectional: true, player_states: [normal_open, mission_authorized, delivery_active]}
    - {id: e02, endpoints: [n_corner, n_shop], connector_type: sidewalk, bidirectional: true, player_states: [normal_open, mission_authorized, delivery_active]}
    - {id: e03, endpoints: [n_shop, n_stock], connector_type: interior_link, bidirectional: true, player_states: [mission_authorized]}
    - {id: e04, endpoints: [n_arrival, n_west_lane], connector_type: gate, bidirectional: true, player_states: [mission_authorized]}
    - {id: e05, endpoints: [n_west_lane, n_rear_yard], connector_type: service_lane, bidirectional: true, player_states: [mission_authorized]}
    - {id: e06, endpoints: [n_rear_yard, n_stock], connector_type: gate, bidirectional: true, player_states: [mission_authorized]}
    - {id: e07, endpoints: [n_rear_yard, n_garage_apron], connector_type: service_lane, bidirectional: true, player_states: [mission_authorized]}
    - {id: e08, endpoints: [n_garage_apron, n_exit], connector_type: gate, bidirectional: true, player_states: [mission_authorized]}
    - {id: e09, endpoints: [n_exit, n_corner], connector_type: sidewalk, bidirectional: true, player_states: [normal_open, mission_authorized, delivery_active]}
  objective:
    id: objective_package
    node_id: n_stock
    required_state: mission_authorized
    approaches:
      public_front: [e01, e02, e03]
      authorized_rear: [e04, e05, e06]
    return_loop: [e06, e07, e08, e09]
  validation_scope:
    graph_connectivity: structurally_checkable_from_this_example
    route_distinctness: front_and_rear_have_distinct_intermediate_nodes
    geometry_clearance: unrun
    vehicle_sweeps: unrun
    sightlines_and_combat: unrun
    historical_site_verification: not_applicable_fictional_composite
    release_approval: not_requested
```

The hardware and garage do not acquire unrestricted access to the houses because they share a block. The service lane is a real agreement, not a universal alley. Front and rear routes differ in use and character. In `normal_open`, players can browse the shop but cannot automatically enter its stockroom. These distinctions make the plan usable by both an environment generator and a mission system.

`delivery_active` is a separate illustrative state. If the mission can overlap a delivery, implement a combined state or independent state variables and validate that combination; do not assume that testing each state separately proves every overlap works.

### 12.3 Airport pool exception record

This is an illustrative exception payload. Its entities are declared locally. It remains conditional until the actual layout proves the physical checks.

```yaml
airport_pool_example:
  entities:
    - {id: air_terminal, archetype_id: airport_terminal}
    - {id: travel_hotel, archetype_id: hotel}
    - {id: guest_pool, archetype_id: hotel_pool}
  exception:
    exception_id: EX_airport_pool
    affected_instance_ids: [air_terminal, travel_hotel, guest_pool]
    affected_rule_ids: [P02, P03]
    unusual_relationship: "A swimming pool is visually close to a passenger terminal."
    causal_explanation: "A landside hotel serves travelers and operates the pool as a guest amenity."
    ownership_or_history: "Hotel and pool share an operator; neither is part of the aircraft operating area."
    access_solution: "Terminal-to-hotel travel uses landside access; pool entry is through hotel grounds."
    remaining_conflicts: [aircraft_noise, road_noise]
    visible_evidence:
      - "The hotel building and fenced courtyard physically separate guest activity from the working airport edge."
      - "Room access, property signs, towels, and housekeeping tie the pool to the hotel."
      - "An independent plant and maintenance route supports the pool."
    gameplay_reason: "The quieter enclosed guest court offers a recognizable spatial contrast near the busy travel hub."
    mandatory_check_results:
      - {check_id: pool_support_program, status: unrun}
      - {check_id: no_accidental_public_airside_edge, status: unrun}
      - {check_id: guest_route_geometry, status: unrun}
    verdict: condition
```

This resolves the *apparent* oddity; it does not override a failed airport boundary. Because the pool's actual use is `hotel_pool`, the direct public-pool rule P01 no longer describes the proposal. Reclassification must be reflected in the operation and geometry, not just the type name.

### 12.4 Compact reusable instruction to the planner

```text
Design a fictional 1990s Pennsylvania place using the supplied setting and mission.
Choose a settlement profile, development history, and economic anchor before buildings.
Reserve streets, terrain, parcels, service areas, and required open space first.
Use the building catalog and explicit pair rules; treat broad affinity as a preference.
Separate spatial proximity, ownership, public access, and working connections.
Give each important adjacency a concrete reason and visible supporting evidence.
Preserve plausible inherited conflicts; do not invent perfect zoning or universal decay.
Use ordinary repeated fabric to support a limited number of memorable destinations.
Create meaningful playable routes from credible public, private, and service circulation.
Give upper routes structure, access, and exits. Give focal props an owner and purpose.
Make activity, wear, signs, and equipment agree with year, season, and local time.
Use the exception contract for unusual combinations; story alone cannot waive geometry.
Return a versioned plan, assumptions, relationships, graph, activity states, and checks.
Mark untested geometry and gameplay as unrun. Never invent a passed validation result.
Repair impossible arrangements while preserving the strongest useful design idea.
```

For a small-context local model, parse the catalogs once and retrieve only the selected profile, relevant building records, matching pair rules, connector records, and output contract for a given decision. Keep non-waivable constraints available on every pass. Use deterministic code for ID resolution, graph reachability, footprint intersections, and measurements; use the model for proposals and explanations.

## 13. Validation and review

### 13.1 Required review passes

| Check ID | Question | Evidence needed |
|---|---|---|
| V01 | Does this place have a coherent reason to exist? | Setting, anchor, catchment, supporting uses, and development history |
| V02 | Do important adjacencies have the right relation and verdict? | Matched pair rules, ownership, permissions, and required evidence |
| V03 | Can all occupied uses actually operate? | Resolved support providers, staff or resident access, goods and refuse arrangements |
| V04 | Do mandatory routes reach their destinations? | Graph tests for each required state, followed by actual navigation checks |
| V05 | Are parcels, buildings, and routes geometrically coherent? | Footprints, elevations, non-overlap, supported structures, connected entrances |
| V06 | Can the intended users and vehicles fit? | Capsule and clearance checks, animation tests, swept paths, queue and work-space checks |
| V07 | Are unusual neighbors visibly explained? | Accepted exception records with spatial evidence and remaining conflicts |
| V08 | Does the scene fit its specific year? | Dated reference or declared fictional design for sensitive assets and institutions |
| V09 | Are routes meaningful and readable? | Route comparison, player observation, view checks, consistent access signals |
| V10 | Does the level support the player group? | Regrouping, interactions, transitions, return paths, and state-change tests |
| V11 | Do props follow activity and preserve movement? | Ownership, support surfaces, alignment, collision, and reserved clear zones |
| V12 | Are time, season, weather, and activity consistent? | One coherent state model and tested combinations |
| V13 | Is there enough ordinary fabric and deliberate empty space? | Building hierarchy, owner-specific maintenance, working clearances, open-space purpose |
| V14 | Does the target build perform adequately? | Measurements in the actual engine, scene, hardware, and multiplayer conditions |

### 13.2 Acceptance cases for the planner implementation

These are **specification test cases**, not a claim that a game implementation has already passed them. They test consequential failure modes rather than stylistic trivia.

```yaml
acceptance_cases:
  - {id: T01, input: "Public pool has an unrestricted edge to active airside operations.", expected: repair_or_reject, reason: "Ownership and public access cannot be explained by visual proximity alone."}
  - {id: T02, input: "Hotel-owned pool has guest access and support facilities beside a landside airport hotel.", expected: allow_after_checks, reason: "Ownership and travel demand explain the use; actual geometry remains mandatory."}
  - {id: T03, input: "Older houses face a street beside a factory with separate freight access.", expected: conditional_allow, reason: "An inherited industrial-residential edge can be historically plausible."}
  - {id: T04, input: "Small rowhouse corner shop has timed curbside delivery and no dock.", expected: allow_after_checks, reason: "Operations can fit the scale without imposing suburban loading geometry."}
  - {id: T05, input: "Large trailer delivery is claimed through a van-sized route with no swept-path result.", expected: do_not_mark_passed, reason: "Adjacency score does not prove service geometry."}
  - {id: T06, input: "School sports field shares grounds but its after-hours gate state is unspecified.", expected: request_or_assign_and_test_state, reason: "Co-location does not define access."}
  - {id: T07, input: "A 1995 PHL reconstruction contains operating Terminal F.", expected: reject_period_asset, reason: "The verified opening year is 2001."}
  - {id: T08, input: "Two adjacent tenants share a loading court but have separate public doors.", expected: allow_after_checks, reason: "A shared service arrangement can preserve distinct customer access."}
  - {id: T09, input: "Four-player route passes a usable interaction in a narrow corridor.", expected: test_congestion_and_repair_if_needed, reason: "Topology alone does not establish group usability."}
  - {id: T10, input: "A rooftop shortcut has a ladder but no supported landing or exit.", expected: repair_or_reject, reason: "Gameplay intent cannot replace structure and connectivity."}
  - {id: T11, input: "A field has random pallets, shopping carts, and neon signs with no owner or activity.", expected: remove_or_reassign_dressing, reason: "The objects lack a causal relationship to the place."}
  - {id: T12, input: "Road and bridge are separately plausible but their elevations do not meet.", expected: fail_geometry, reason: "Local asset validity does not prove a valid assembled connection."}
  - {id: T13, input: "Pool is closed for winter but swimming activity remains enabled.", expected: fail_state_consistency, reason: "Seasonal operation and activity disagree."}
  - {id: T14, input: "Public and service approaches are individually valid but meet at one blocked mandatory door.", expected: fail_required_reachability_in_blocked_state, reason: "Two route labels do not guarantee a usable alternative."}
  - {id: T15, input: "A recipe contains an unknown building or connector ID.", expected: fail_reference_validation, reason: "Do not silently invent an asset or reinterpret a typo."}
  - {id: T16, input: "A semantic plan lacks geometric measurements but claims final approval.", expected: reject_approval_status, reason: "Unrun mandatory checks must remain visible."}
```

### 13.3 Common failures and targeted fixes

| Failure | Why it reads as generated | Repair |
|---|---|---|
| Interesting-building soup | No economic or historical organizing idea | Pick an anchor and replace unrelated attractions with supporting fabric |
| Every building equally spaced | Ignores parcel history and land pressure | Use the selected lot pattern; vary through meaningful subdivision or change |
| Perfectly segregated districts everywhere | Erases the inherited mix of older places | Permit credible older conflicts and give them real boundaries and consequences |
| All buildings freely interconnected | Confuses proximity with ownership | Remove accidental links; keep a few justified shared or mission-enabled routes |
| Huge parking lots behind every use | Applies one suburban assumption to all contexts | Select a parking strategy by profile, use, and history |
| Doors opening into walls, hedges, or parked cars | No entrance-to-network validation | Reserve threshold space before props and parking |
| Roads painted beneath buildings or floating over slopes | Assets were placed before terrain and circulation | Rebuild the block ground plan and solve elevations |
| Identical rear alleys on every block | Treats one optional pattern as universal | Choose block-specific rear access, passages, yards, and dead ends |
| Every building derelict | Replaces history with one condition slider | Assign occupancy and maintenance by owner and use |
| Random grime everywhere | Dirt has no activity, weather, or gravity | Concentrate wear at actual movement and collection points |
| Crate cover in every open space | Combat props have no economic purpose | Use real work structures, parking, grade, and property boundaries |
| Convenient ladder on every façade | Verticality is detached from use | Use a few supported, purposeful upper connections |
| Empty city with busy signage | Promised activity has no users or traces | Add scheduled action, sound, and evidence of recent use |
| Constant activity at all hours | No time model | Select a few active businesses and explain the quieter ones |
| One fence “solves” every conflict | Visual separation is confused with noise, traffic, and access control | Evaluate each conflict channel independently |
| Historic explanation with no visible consequence | The rationale exists only in notes | Add actual retained geometry, different ages, property lines, or reuse evidence |

### 13.4 Definition of done

A finished layout lets a reviewer answer, from the scene and its supporting data:

1. Why are these uses here, and why are they neighbors?
2. Who owns and uses each important space?
3. How do people, goods, vehicles, and maintenance reach their destinations?
4. What prevents conflicting activities from accidentally sharing the same space?
5. What does the place do at this hour, in this season, in this year?
6. Where do players go, what choices matter, and how do they regroup or return?
7. Which details show ongoing life, and which ordinary spaces give that life room?
8. Which checks passed in a real build, and which assumptions still need verification?

If a strange pairing has convincing answers, keep it. If an ordinary pairing cannot operate, repair it. Believability comes from the relationships and their visible consequences.

## 14. Sources and evidence boundaries

Sources below were consulted on October 10, 2026. Planning and preservation documents published after the 1990s can describe older urban forms; their current recommendations and inventories are not automatically evidence of a site's condition in 1995. The adjacency catalog, numerical ranges, gameplay targets, recipes, and acceptance cases in this guide are original design synthesis, not standards quoted from these sources.

| ID | Primary source | What it supports | What it does not establish |
|---|---|---|---|
| S01 | City of Philadelphia, [Philadelphia Rowhouse Manual](https://www.phila.gov/media/20190521124726/Philadelphia_Rowhouse_Manual.pdf), 2008 | Rowhouse forms, historical development, and relationship to city fabric | Exact 1990s condition, access rights, or dimensions for every block |
| S02 | Delaware County Planning, [Planner's Portfolio: Character Areas](https://delcopa.gov/planning/education/plannersportfolios/PlannersPortfolioCharacterAreas), issue dated March 2016 | The county's variety of mature neighborhoods, suburbs, centers, and corridors | A 1995 business inventory or universal pattern for the whole county |
| S03 | PHMC, [Urban Historic Landscapes](https://www.phmc.state.pa.us/portal/communities/architecture/landscapes/urban.html), archived field guide | Relationships among density, streets, buildings, open space, and mixed historic uses | The compatibility scores or gameplay rules in this guide |
| S04 | PHMC, [Suburban Historic Landscapes](https://www.phmc.state.pa.us/portal/communities/architecture/landscapes/suburban.html), archived field guide | Differences among rail or streetcar suburbs and later automobile-oriented development | A single design applicable to every Pennsylvania suburb |
| S05 | PHMC, [Industrial Historic Landscapes](https://www.phmc.state.pa.us/portal/communities/architecture/landscapes/industrial.html), archived field guide | Industry-specific buildings, transport and resource relationships, and associated worker housing | The operation, ownership, or public access of an individual 1990s factory |
| S06 | PHMC, [Agricultural Historic Landscapes](https://www.phmc.state.pa.us/portal/communities/architecture/landscapes/agricultural.html), archived field guide | Farm buildings as part of a working landscape of landforms, fields, and boundaries | One farm program suitable for every agricultural region |
| S07 | Pennsylvania Historical and Museum Commission, [Field Guide for Agricultural Resources](https://www.pa.gov/agencies/phmc/historic-preservation/education-outreach/pennsylvania-agricultural-history-project/field-guide-agricultural-resources) | A primary starting point for identifying farm building types and regional agricultural context | Proof that a particular historic structure remained in the same use in the 1990s |
| S08 | Reading Terminal Market, [History](https://readingterminalmarket.org/about-the-market/history/) | The documented historical relationship between market and railroad terminal | Permission to copy its historical operation unchanged into any later year |
| S09 | Philadelphia International Airport, [1980s–1990s history](https://www.phl.org/about/history/history1980) | Dated terminal, rail-access, road, and cargo developments, including later opening dates | A full reconstruction of the airport or a rule that all airport fringes share one layout |
| S10 | SEPTA, [Airport Line Turns 39](https://wwww.septa.org/news/airportlineturns39/) | The Airport Line's April 28, 1985 start | Exact historic layouts and branding of every station |
| S11 | U.S. Government Publishing Office, [Public Law 107-71](https://www.govinfo.gov/content/pkg/PLAW-107publ71/html/PLAW-107publ71.htm), November 19, 2001, Section 101 | Establishment of TSA after the guide's 1990s setting | Detailed reconstruction of earlier airport screening procedures |
| S12 | Delaware Valley Regional Planning Commission, [Land Use 1990](https://catalog.dvrpc.org/dataset/land-use-1990) | Availability of regional land-use evidence tied to 1990 | Building-level interiors, specific tenants, or changes between 1990 and the selected scene year |

### 14.1 Reference workflow for a new location

1. Find a dated aerial, map, photograph, planning record, or institutional history for the intended region and period.
2. Extract relationships: roads, parcels, building orientation, scale, recurring types, working edges, and public destinations.
3. Record which observations are verified, inferred, or fictional.
4. Choose the smallest set of patterns that explains the proposed level.
5. Transform those patterns for gameplay while retaining their causes and spatial consequences.
6. Recheck date-sensitive infrastructure, institutions, signage, and business formats before building final assets.

Public accessibility of a reference does not by itself grant rights to redistribute its photographs or maps. This document links to sources; it does not bundle their imagery.
