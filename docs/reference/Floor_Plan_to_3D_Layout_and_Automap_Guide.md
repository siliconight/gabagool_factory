# Floor Plan to 3D Layout and Automap Guide

**Purpose:** Turn traditional floor plans into a multilevel 3D building layout, an exploded architectural diagram, and an interactive game map.

**Workflow:** Blender for geometry authoring; Godot for the playable blockout and interactive map.

**Game context:** A four-player cooperative PvE heist game with buildings, vertical routes, and large numbers of enemies.

## 1. What these representations are called

The two reference images show different ways to visualize a building's 3D layout. Both can start from a traditional floor plan, but they preserve different information.

| Reference | Name | What it shows |
| --- | --- | --- |
| Separated floors with walls, rooms, and architectural details | **Exploded axonometric view**, with architectural cutaways | How the building fits together: rooms, floors, openings, stairs, and vertical relationships. |
| Floating floor surfaces with highlighted edges and player markers | **3D automap** or **3D tactical map** | Where players can go, how spaces connect, and where important things are. |

“Isometric map” is also a useful search term, although **axonometric** is the broader architectural term. Isometric is a particular type of axonometric projection.

A useful name for the proposed tool is **Floor Plan to 3D Layout and Automap Generator**. This is a descriptive project name, not a formal industry standard.

The key step is turning the floor plan into structured spaces and connections. Once those exist, the building, architectural diagram, and simplified game map can all be generated from the same layout.

## 2. Establish scale and align the plans

Start with a floor plan for each level.

1. Import an image as a tracing reference, or use vector outlines when available.
2. Calibrate the drawing against a known measurement.
3. Align every floor to the same origin using stairwells, elevator shafts, or structural columns.
4. Remove drawing information that is irrelevant to geometry: dimension arrows, furniture symbols, and annotation lines.

For example, a corridor marked as 12 metres long should become 12 metres in the model.

**Techniques:** Reference-image tracing, vector cleanup, snapping, and coordinate alignment.

**Output:** Clean, measured outlines for each floor, all using a consistent scale and coordinate system.

An image contains pixels; a usable layout needs measured boundaries. Do not treat every line in a drawing as a physical object.

## 3. Identify what each shape means

Trace and label the drawing as meaningful elements.

| Element | Information to retain |
| --- | --- |
| Room or corridor | Boundary polygon, name, floor, intended use |
| Wall | Path or footprint, thickness, height |
| Door | Position, width, connected spaces |
| Window | Position, width, sill and opening heights |
| Stair or ramp | Start, end, footprint, elevations |
| Atrium or shaft | Empty footprint and the floors it passes through |
| Gameplay connection | Access conditions, direction, locked/unlocked state |

This is **semantic modeling**: identifying which lines represent walls, doors, or other features.

For automation, computer vision can propose these elements, but ambiguous boundaries and connections need review. A door swing arc must not become a curved wall.

Give spaces and connections stable identifiers. A room's identity should survive a change to its shape so objectives, labels, and discovery state can remain associated with it.

**Output:** A structured layout containing spaces, boundaries, openings, and connections, rather than an unlabeled collection of polygons.

## 4. Supply the missing vertical information

A floor plan usually does not completely describe the third dimension. Add:

- Floor elevations and floor-to-floor heights.
- Ceiling heights and slab thicknesses.
- Stair rises, runs, and landings.
- Ramps and changes in floor level.
- Double-height rooms, balconies, bridges, and openings between floors.

An atrium needs a hole in the upper floor, not just an “atrium” label. A staircase needs an upper landing that reaches the intended floor and an opening that provides sufficient headroom.

This is where a flat layout becomes a **multilevel spatial model**. Record missing dimensions as design assumptions so they can be revised deliberately.

**Output:** A layout with actual elevations, vertical clearances, and explicit connections between levels.

## 5. Build a simple 3D blockout in Blender

Use the traced shapes to construct the building.

| Operation | Technique |
| --- | --- |
| Turn room outlines into floors | Fill polygons and triangulate correctly, preserving holes |
| Give floors thickness | Extrusion or the Solidify modifier |
| Create walls | Extrude wall footprints upward |
| Create doors and windows | Build wall segments around openings, or subtract opening volumes |
| Create stairs | Generate repeated steps and landings from measured rise/run |
| Organize levels | Separate collections or parent objects for each floor |

Blender's Solidify modifier adds thickness to mesh surfaces, making it useful for floor slabs and other thin surfaces. [1]

Use plain materials at this stage. Establish whether the spaces connect before investing in detailed art.

For a four-player PvE game, walk through the blockout with the actual player controller. Check:

- Whether players can pass each other in corridors.
- Whether doorways become unintended queues.
- Whether stairs and landings have usable clearance.
- Whether teammates have space to fight, retreat, and revive.
- Whether enemies can reach the areas their encounter design requires.
- Whether cover and major obstructions leave the intended routes usable.

A faithful architectural reconstruction is a starting point. Changes made for gameplay should update the shared layout so the building and map stay consistent.

**Output:** A simple, traversable 3D building suitable for spatial review and gameplay testing.

## 6. Generate the exploded architectural view

Starting from the blockout:

1. Hide roofs and selected ceilings.
2. Cut away walls that obscure important interiors.
3. Move each floor upward by an additional **display offset**.
4. Keep floors horizontally aligned so their relationships remain visible.
5. Use an angled orthographic camera.
6. Add outlines, restrained shading, floor labels, and callouts.

**Techniques:** Exploded transforms, cutaway visibility, orthographic projection, and architectural line rendering.

The display offsets belong to the visualization. They must not change the building's actual floor elevations, collision, or navigation geometry.

Keep the source building intact and apply the exploded arrangement to a presentation representation. This makes it possible to switch between assembled and separated views without changing gameplay geometry.

**Output:** A readable diagram of the building's floors, rooms, openings, and vertical relationships.

## 7. Generate the simplified automap mesh

Create a second representation focused on movement and orientation.

### Keep

- Room and corridor footprints.
- Stairs, ramps, bridges, and balconies.
- Openings and major obstructions that affect routes.
- Doors and important landmarks.

### Simplify or omit

- Decorative props and small surface details.
- Ceilings and tall walls that obstruct the map view.
- Architectural detail that does not help explain the route or identify a place.

### Geometry process

1. Combine adjacent floor regions where appropriate.
2. Preserve holes, disconnected areas, and meaningful room boundaries.
3. Simplify outlines without closing narrow passages.
4. Triangulate the surfaces.
5. Add shallow thickness so edges remain readable.
6. Draw highlighted boundaries.

**Techniques:** Polygon union/difference, constrained simplification, triangulation, extrusion, and boundary extraction.

Do not merge across walls merely because neighboring floor surfaces touch. Preserve room identity even when regions share a render mesh.

The highlighted outlines in the tactical-map reference can be reproduced with boundary geometry or an outline shader. A general wireframe would also expose internal triangle edges, producing a much noisier result.

The map geometry can be generated in Blender or directly in Godot. Godot's `SurfaceTool` constructs meshes from vertices and their attributes and commits the result to an `ArrayMesh`. [2]

**Output:** Lightweight map geometry that communicates routes and elevation without reproducing every detail of the game world.

## 8. Give the map its own presentation in Godot

Use a dedicated map scene rendered through a `SubViewport`, with its own 3D world and camera. Godot supports separate viewport worlds through `own_world_3d` and orthographic projection through `Camera3D`. [3][4]

Add:

- Orbit, pan, zoom, and recenter controls.
- A top-down/angled-view toggle.
- Floor selection.
- Strong emphasis on the selected floor and subdued surrounding floors.
- Player, teammate, objective, exit, and door markers.
- Optional room discovery or fog of war.

An orthographic camera keeps objects the same apparent size regardless of their distance from the camera, which is useful for a diagram-like map. [4]

### Keep markers aligned with the map

Store each marker's world position and floor/space identity. Two teammates can occupy the same horizontal position on different floors.

Apply the same world-to-map transformation to geometry and markers. If floors are separated visually, apply the corresponding display offset to their markers as well. Otherwise, icons will float away from the rooms they belong to.

Stairs, ramps, and landings need explicit transition handling. Choosing a floor solely from the nearest floor elevation can produce incorrect switches while a player moves between levels.

**Output:** An interactive map that remains aligned with player positions, objectives, and the building layout.

## 9. Validate connections separately from appearance

Maintain a **connectivity graph** alongside the geometry:

- Rooms, corridors, and landings are nodes.
- Doors, stairs, elevators, and drops are connections.
- Connections record direction and access conditions.

This lets the tools answer questions such as:

- Can players reach the exit from the objective?
- Does locking this door disconnect a required route?
- Is a drop one-way?
- Does the upper landing connect to the intended corridor?
- Are two spaces visually adjacent but physically separated?

The graph describes intended connectivity. Player-controller and navigation tests establish whether the generated geometry actually supports it. A connected graph alone does not prove that four players can move comfortably through a doorway or fight effectively in a room.

### Use the navigation mesh as supporting evidence

A navigation mesh helps test traversal, but it should not be the sole source of the player-facing map.

Godot's navmesh describes positions an agent's centre can traverse. Baking shrinks it by the configured agent radius, so its boundaries do not necessarily match the building. Navigation also operates separately from rendering and physics. [5]

Use the structured building layout to generate the visual map, and use the navmesh to check traversal for the relevant agent sizes and movement rules.

**Output:** Evidence that the map, intended connections, collision, and actual traversal agree.

## 10. Recommended first prototype

Build a small test building containing:

- Two floors.
- Six rooms.
- One staircase.
- One atrium.
- An entrance, an objective, and an exit.

Produce both an exploded architectural view and an interactive automap from the shared layout.

### Acceptance checks

| Check | Expected result |
| --- | --- |
| Change a doorway's position or width | Building geometry, intended connectivity, and map representation update consistently. |
| Move or resize the staircase | Steps, landings, floor openings, and map connections remain aligned. |
| Inspect the atrium | The upper floor preserves the opening rather than filling it with a walkable surface. |
| Place players directly above one another | Markers identify the correct floors. |
| Separate floors in the presentation | Geometry and markers move together; gameplay elevations remain unchanged. |
| Lock a route | Connectivity checks respect the door state and identify whether a valid alternative exists. |
| Traverse with four players and representative enemies | Physical clearances and route behavior match the intended encounter. |

Establish these behaviors before expanding to a complete building or adding detailed art.

## 11. Source references

The workflow and tool organization above are proposed implementation choices. The following official documentation supports the specific Blender and Godot capabilities cited. The linked `latest` and `stable` documentation can change; use the matching documentation version when implementing against a pinned tool release.

1. **Blender Manual — Solidify Modifier.** Adding thickness to mesh surfaces.  
   [Read the official documentation](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/solidify.html)

2. **Godot Documentation — Using the SurfaceTool.** Building meshes from vertex attributes and committing an `ArrayMesh`.  
   [Read the official documentation](https://docs.godotengine.org/en/stable/tutorials/3d/procedural_geometry/surfacetool.html)

3. **Godot Documentation — Viewport.** Separate 3D worlds through `own_world_3d`.  
   [Read the official documentation](https://docs.godotengine.org/en/stable/classes/class_viewport.html)

4. **Godot Documentation — Camera3D.** Orthographic projection, camera sizing, and viewport camera behavior.  
   [Read the official documentation](https://docs.godotengine.org/en/stable/classes/class_camera3d.html)

5. **Godot Documentation — Using navigation meshes.** Agent-centre traversal, baking, agent-radius offsets, and separation from rendering and physics.  
   [Read the official documentation](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationmeshes.html)

