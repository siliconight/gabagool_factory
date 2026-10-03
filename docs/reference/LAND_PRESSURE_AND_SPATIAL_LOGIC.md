# Land Pressure and Spatial Logic for Procedural AI

## Purpose

This document defines how AI-driven environment tools should allocate land, arrange buildings, and explain the space between them. It applies to settlement planning, roads, parcels, building generation, exterior dressing, and non-playable backdrops.

The intended result is a believable game environment whose spatial organization reflects human needs, competing uses, and development history. Pennsylvania examples support a fictional 1990s setting, but the rules can be adapted elsewhere.

This is a proposed design specification, not a real-estate valuation model, surveyed reconstruction, or verified implementation. Numeric presets below are authored starting points for game generation, not measured regional averages or building-code requirements.

## 1. Governing principle

**Treat usable space as a resource that people compete for, pay for, and adapt to.**

Where demand for a location is strong relative to the supply of usable land, development generally faces pressure to accommodate more activity within less space. Where that pressure is weaker, activities can occupy larger sites and sit farther apart.

However, land price alone does not determine building spacing. Ownership, transportation, existing parcel boundaries, construction costs, terrain, infrastructure, regulations, and history influence what actually gets built.

The generator must ask:

1. Why is this activity located here?
2. How much space does it need to function?
3. How much space can it plausibly occupy in this district?
4. How do people, goods, vehicles, and services reach it?
5. What explains the land left around it?

Buildings are consequences of these decisions. Do not begin by scattering building assets across an empty plane.

## 2. Concepts the tools must keep separate

| Concept | Meaning for generation | Do not confuse it with |
| --- | --- | --- |
| Land pressure | Competition for a limited amount of usable land | A literal dollar value |
| Desirability | Reasons a particular user wants a location: access, customers, privacy, productive soil, views | A single universal ranking of places |
| Built density | Amount of building floor area or footprint within a defined area | Pedestrian or traffic congestion |
| Activity intensity | How many people or operations use a place and when | Building height alone |
| Congestion | Demand exceeding available movement or service capacity | Dense development automatically |
| Development capacity | What terrain, infrastructure, rules, and construction permit | What the market would prefer |
| Historical form | Inherited streets, parcels, buildings, and infrastructure | Present-day demand |

A quiet rowhouse street can have high built density. A low-density commercial road can be congested. A rural estate can be expensive and spacious. A declining industrial neighborhood can retain tightly packed buildings despite weak current demand.

**Never equate rural with undesirable, dense with poor, spacious with wealthy, or crowded with dirty.** Maintenance, wealth, vacancy, and density must remain separate controls.

## 3. Generate at several scales

### Region

Establish rivers, slopes, productive land, major routes, employment centers, and settlement clusters. Decide which areas are developed, cultivated, wooded, constrained, or reserved.

### District

Assign a coherent development pattern: rowhouse neighborhood, borough main street, industrial corridor, suburban strip, rural village, farm landscape, or another authored type. Establish the dominant era and transportation pattern.

### Block and parcel

Lay out streets and ownership boundaries. Allocate frontages, access, buildable envelopes, and open-space uses. Neighboring parcels should inherit shared conditions rather than receive unrelated random values.

### Building and service space

Fit structures and their support needs into parcels. Account for entrances, delivery access, trash, parking where applicable, yards, storage, and utilities.

### Detail

Place objects only after their use and access are established. A dumpster belongs where collection is possible. A shed needs a usable approach. A fence should express a boundary or enclosure.

### Backdrop

Continue the district's roof rhythm, street direction, clusters, and open-space structure beyond the playable boundary. Reduce geometric detail with distance while preserving the larger pattern.

## 4. Required generation inputs

Use explicit controls rather than asking an AI to interpret only “urban” or “rural.” Normalized controls range from 0 to 1 and express relative design intent within a project.

| Input | Meaning | Expected influence |
| --- | --- | --- |
| `land_pressure` | Competition for usable sites | Parcel coverage, sharing, infill, pressure to use frontage |
| `accessibility` | Ease of reaching jobs, customers, transport, or services | Location of activity clusters |
| `development_restriction` | Strength of authored limits on building form | Height, setbacks, protected gaps |
| `car_dependence` | Importance of private vehicle access | Driveways, parking allocation, road-oriented layouts |
| `service_intensity` | Space needed for goods, equipment, and operations | Loading areas, yards, access width |
| `privacy_preference` | Desired separation and enclosure | Setbacks, screening, private land allocation |
| `historical_persistence` | Degree to which inherited form survives | Retained small lots, older alignments, reused buildings |
| `vacancy_level` | Share of unused properties or buildings | Vacant structures and explained gaps |
| `maintenance_level` | Upkeep and repair condition | Surface wear and repairs, not spacing |
| `terrain_constraints` | Authored slopes, water, floodplain, or other exclusions | Buildable land and access routes |
| `era_profile` | Period and development history | Eligible buildings, transport assumptions, infrastructure |
| `settlement_archetype` | Dominant spatial pattern | Correlated defaults for all downstream tools |

Keep actual parcel dimensions, street widths, setbacks, and access envelopes in meters. Do not turn normalized controls directly into arbitrary distances without an archetype-specific mapping.

## 5. Spatial rules

### 5.1 High land pressure

Prefer smaller parcels, greater building coverage, shared boundaries, attached forms where appropriate, and efficient use of street frontage. Allow upward expansion only when the archetype, construction system, and restrictions support it.

Accommodate support functions through rear yards, alleys, shared courts, basements, or other plausible arrangements. High land pressure must not erase operational needs.

A small urban business may have no dedicated parking. It still needs a credible way to receive goods and remove waste.

### 5.2 Lower land pressure

Allow larger sites, detached structures, broad yards, surface parking, outbuildings, and greater separation between properties.

Do not maximize spacing everywhere. Related functions still cluster to reduce travel and simplify work. A farmhouse, barn, workshop, and equipment shed can form a compact group surrounded by extensive fields.

### 5.3 Frontage has a function

Businesses that benefit from visibility should favor accessible streets and intersections. Allocate street-facing entrances, windows, signs, and approaches accordingly.

Do not spend desirable frontage on unexplained gaps while placing every active business behind them. Exceptions need a reason, such as parking-oriented retail, a forecourt, retained residential setback, or an unusual parcel.

### 5.4 Open land must have a role

Partition all non-building parcel area into explicit uses. Valid roles include circulation, yard, garden, parking, loading, outdoor storage, drainage, cultivation, woodland, recreation, vacancy, and reserved expansion.

An explanation must affect geometry or dressing. A drainage area should have appropriate shape and connection; an agricultural field should read as a field. A text label cannot rescue implausible placement.

### 5.5 Density changes around useful places

Build clusters around centers of activity and allow development to thin between them. Use streets, parcel transitions, railways, waterways, terrain, and development phases to organize these changes.

A rural village can be compact. An urban park can be open. A railway can create an abrupt edge. Avoid requiring a perfectly smooth center-to-edge gradient.

### 5.6 History constrains the present

Generate an initial pattern, then apply a small number of coherent changes: subdivision, infill, demolition, lot consolidation, conversion, or outward expansion.

A former house converted to a shop may retain its setback. An industrial site may absorb several parcels. A vacant lot can preserve the outline of a demolished building.

Do not regenerate every parcel from current land pressure alone.

### 5.7 Variation must be correlated

Sample a district pattern first, a block variation second, and limited parcel variation last. Preserve common building lines and recurring lot widths where they belong.

Use purposeful exceptions rather than independent random offsets on every building. Deliberate repetition can be historically and visually correct.

## 6. Starting archetypes

These are qualitative art-direction presets. They describe tendencies, not mandatory facts about every location.

| Archetype | Building pattern | Space between structures | Access and open land |
| --- | --- | --- | --- |
| Philadelphia rowhouse block | Narrow attached buildings and repeated frontage | Usually no side gap within a row; separation at block ends or specific breaks | Rear yards, sidewalks, curb access, occasional alleys |
| Delco borough main street | Close-set storefronts, some apartments above | Small gaps or attached runs | Rear servicing, small lots, side streets, shared access |
| Older detached neighborhood | Repeated modest lots and consistent street rhythm | Limited but readable side yards | Small gardens, driveways where feasible, occasional garages |
| Suburban commercial strip | Detached businesses oriented toward road access | Broad gaps often occupied by parking or circulation | Driveways, parking fields, loading behind or beside buildings |
| Industrial corridor | Large footprints and operational yards | Clearance determined by trucks, rail, storage, or process | Service routes and equipment yards; limited decorative land |
| Rural village | Compact group at a crossroads or along a main road | Tight near the center, wider toward the edges | Short local connections and surrounding fields or woodland |
| Farm landscape | Clustered farmstead within large working parcels | Small distances inside the cluster; large distances between clusters | Fields, lanes, work yards, hedgerows, woods |
| Rural estate | Low building coverage despite potential high land value | Intentional privacy and separation | Grounds, screening, long approach, accessory buildings |

## 7. Metrics the tools should calculate

Always state the measurement boundary. A dense farmstead inside a large agricultural parcel is different from a dense district.

- **Parcel coverage:** union area of building footprints divided by parcel area.
- **Floor-area ratio:** total above-ground floor area divided by parcel area, using a consistent project definition.
- **Frontage occupancy:** building frontage projected onto the designated street frontage, divided by that frontage length. Handle corner frontages separately to avoid double counting.
- **Setback:** distance from building to the relevant parcel boundary. Record front, side, and rear separately.
- **Building separation:** shortest exterior-to-exterior distance between distinct buildings; attached buildings may have zero separation.
- **Open-space allocation:** area assigned to each non-building use, with no accidental overlaps or unassigned remainder.
- **Access connectivity:** whether required entrances and service areas connect to suitable public or shared routes.

Do not use a single average spacing value to represent an entire region. Record distributions and cluster membership. Rural settings should be capable of combining close farmstead spacing with large gaps between properties.

### Illustrative coverage bands

For initial tuning only, a project might use 0.55–0.85 parcel coverage for a compact attached block, 0.20–0.40 for a detached residential parcel, and 0.03–0.12 for a rural residential parcel. These are authored examples, not regional measurements.

Agricultural holdings need separate farmstead and whole-parcel measurements. Do not apply a rural residential coverage target to a complete farm.

Geometry and functional requirements take precedence over hitting a band. If a parcel cannot accommodate the requested form, revise the parcel or building program; do not shrink essential clearances invisibly.

## 8. Shared contract across tools

All tools must consume the same versioned spatial plan and stable IDs.

| Tool | Owns | Must preserve |
| --- | --- | --- |
| Settlement planner | Districts, centers, exclusions, broad land uses | Regional constraints and era |
| Street tool | Roads, sidewalks, intersections, access connections | District structure and reserved corridors |
| Parcel tool | Boundaries, frontage, buildable envelopes | Street access and land-use intent |
| Building tool | Footprints, height, entrances, attachments | Envelopes and required service space |
| Dressing tool | Fences, vegetation, storage, bins, signs | Access routes, ownership boundaries, use labels |
| Backdrop tool | Distant continuation and simplified masses | District rhythm and major alignments |
| Validator | Metrics, violations, repair requests | Authoritative plan and authored exceptions |

Downstream tools must return a conflict when they cannot comply. They must not silently move a road, widen a lot, erase a service area, or change a district's density.

Each parcel record should include its polygon, land use, frontage edges, buildable envelope, neighboring IDs, access connections, open-space allocations, generated metrics, and concise reasons for exceptions.

## 9. Example configuration

This JSON is a design contract example, not an existing engine API. Polygon geometry and asset catalog references would be supplied by the implementing toolset.

```json
{
  "schema_version": "1.0",
  "seed": 199004,
  "district_id": "borough_main_street_01",
  "era_profile": "fictional_pennsylvania_1990s",
  "settlement_archetype": "borough_main_street",
  "controls": {
    "land_pressure": 0.75,
    "accessibility": 0.85,
    "development_restriction": 0.45,
    "car_dependence": 0.45,
    "service_intensity": 0.50,
    "privacy_preference": 0.20,
    "historical_persistence": 0.85,
    "vacancy_level": 0.10,
    "maintenance_level": 0.55
  },
  "authored_targets": {
    "parcel_coverage_band": [0.50, 0.80],
    "stories_band": [2, 3],
    "front_setback_m_band": [0.0, 3.0]
  },
  "preferred_patterns": [
    "continuous_storefront_runs",
    "apartments_above_some_shops",
    "rear_or_shared_service_access",
    "small_rear_parking_areas"
  ],
  "required_constraints": [
    "account_for_all_parcel_area",
    "connect_required_entrances",
    "preserve_service_clearances",
    "respect_terrain_exclusions"
  ],
  "exception_policy": "require_reason_and_validator_review"
}
```

Use this as a district baseline. Do not apply identical values to every parcel. Pin the seed, configuration, asset catalog version, and generator version for reproducibility.

## 10. Generation and repair sequence

1. **Establish constraints.** Load playable boundaries, terrain, exclusions, required mission locations, era, and performance budgets.
2. **Choose settlement structure.** Place centers and assign coherent district archetypes.
3. **Build movement networks.** Connect streets and service routes before committing building footprints.
4. **Divide land.** Create parcels with usable frontage or explicitly defined shared access.
5. **Allocate uses.** Reserve building, circulation, operational, and open-space areas together.
6. **Fit buildings.** Select forms that meet their program inside the available envelopes.
7. **Apply history.** Introduce controlled conversions, infill, consolidated lots, or vacancies.
8. **Dress by purpose.** Add objects and vegetation without consuming reserved clearance.
9. **Continue the backdrop.** Extend the apparent settlement pattern beyond the playable area.
10. **Validate and repair.** Fix the smallest affected scope; rerun dependent checks after each change.

Use explicit repair limits. After repeated failure, return the conflicting requirements to the caller rather than accepting invalid geometry or looping indefinitely. Preserve approved parcels during local repairs unless a wider change is explicitly required.

## 11. Validation requirements

### Hard failures

- Building extends outside its permitted envelope without an authored allowance.
- Required entrance, loading area, or service point lacks usable access.
- Assigned land uses overlap incompatibly or leave unexplained parcel area.
- Geometry enters a prohibited terrain or infrastructure corridor.
- Dressing blocks a required route or clearance.
- A downstream tool changes authoritative boundaries without approval from the owning tool.

### Plausibility warnings

- Every building has identical spacing despite different parcel and use conditions.
- A high-pressure main street contains repeated unexplained frontage gaps.
- Rural houses and barns are evenly scattered with no farmstead clusters.
- A working commercial or industrial site has no space for its operations.
- High current vacancy has erased all evidence of the older street and parcel pattern.
- Density changes abruptly without a boundary, development phase, or other explanation.
- Exceptions are so frequent that the selected archetype no longer describes the district.

### Review scenarios

| Scenario | Expected result |
| --- | --- |
| Raise land pressure with other constraints held constant | Tendency toward more efficient land use, unless limits prevent it; unresolved demand is reported |
| Raise privacy preference under restrictive development rules | More separation may persist despite high value or demand |
| Lower current demand in an old compact district | Inherited geometry remains; vacancy or reuse changes |
| Generate a farm district | Tight functional farmstead groups within larger open holdings |
| Add a rural village center | Local concentration appears without urbanizing the whole region |
| Add heavy delivery requirements | Service geometry changes or the parcel is rejected |
| Reserve a combat or traversal space | Space receives a plausible use and remains functionally clear |

These are acceptance criteria for implementation. This document does not claim the toolset has passed them.

## 12. Gameplay and runtime integration

Believability must support play. Reserve mission routes, encounter spaces, sightlines, navigation clearances, and multiplayer needs before finalizing parcels.

Where gameplay requires extra room, choose a plausible spatial use: loading court, vacant lot, parking area, park, service lane, forecourt, or work yard. Avoid expanding every street and gap equally, which weakens the district's identity.

Visual density does not require every building to be enterable or fully simulated. Use compact exterior shells and simplified distant masses where appropriate. Preserve the appearance of attached buildings even if assets are authored separately.

Track runtime budgets independently from land pressure. Reducing object count should simplify geometry or dressing while preserving frontage, clusters, and open-space purpose. Do not turn an urban block into widely separated buildings merely to meet an asset budget.

## 13. Instruction block for an AI planner

> Generate land use before placing buildings. Treat usable space as a constrained resource whose allocation depends on demand, accessibility, ownership, history, terrain, transportation, and development limits.
>
> Under high land pressure, favor efficient parcel use, concentrated frontage, shared boundaries, and appropriate infill or vertical development. Preserve functional access and service space. Under lower pressure, allow larger parcels and more separation, while clustering related activities for convenience.
>
> Do not equate rural land with low desirability, density with poverty, or congestion with building count. Keep maintenance, vacancy, wealth, and spatial form separate.
>
> Establish regional clusters, district patterns, streets, and parcels before selecting building assets. Assign every substantial open area a use that is visible in its geometry or treatment. Use correlated variation and limited, explained exceptions.
>
> Preserve historical patterns when current conditions change. Respect shared spatial records across tools. Return conflicts instead of silently breaking boundaries, clearances, access, or gameplay requirements.
>
> Report the selected archetype, key assumptions, measured spatial outcomes, exceptions, and unresolved constraints. Validate the generated geometry; a plausible written explanation alone is insufficient.

## Definition of success

A viewer should be able to infer why buildings are close together here, farther apart there, clustered around one road, and absent from another area. The tools should be able to demonstrate those reasons through parcel geometry, land-use allocation, access, and consistent settlement structure.
