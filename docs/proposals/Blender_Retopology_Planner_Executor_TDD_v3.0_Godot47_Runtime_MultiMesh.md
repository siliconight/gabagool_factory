# Technical Design Document: Blender Retopology Planner & Executor

**Document ID:** BRPE-TDD-001  
**Version:** 3.0 — reference-grounded retopology plus Godot 4.7 runtime performance specification  
**Date:** 2026-10-21  
**Primary environment:** Blender desktop and Blender background mode; runtime target: Godot 4.7 (Forward+, Mobile or Compatibility specified per project)  
**Implementation:** Blender Python API (`bpy`), BMesh (`bmesh`), Blender modifiers/operators, `mathutils`; Python standard library only  
**Input:** Existing 3D mesh objects in Blender  
**Output:** A planned, validated, retopologized Blender mesh, Godot-ready asset/export metadata, spatial instancing recommendations, and a machine-readable report
**Reference standard:** Official Blender and **version-pinned Godot 4.7** documentation; Blender Studio production guidance; practitioner game-art resources; peer-reviewed geometry-processing literature. Foundational citations are `[R#]` in §23; engine-runtime citations are `[G#]` in §37.

> **Design principle:** Retopology is not synonymous with Decimate, and fewer triangles are not proof of faster Godot rendering. The tool must decide **which edges and surfaces should exist**, choose an appropriate construction method, and prove that the rebuilt mesh still serves the asset's intended purpose. If it cannot confidently rebuild a mesh, it must say why and provide a guided repair path rather than silently damage it.

---

### v3.0 runtime decision summary — read before implementation

**The key change:** The tool must optimize for **runtime scene cost**, not only clean mesh topology. A successful candidate is a canonical Blender mesh **plus** a plan for how Godot renders and reuses it, **plus** verified engine performance data.

| Decision | Mandatory rule |
|---|---|
| What to retopologize | Preserve the v2 source-fidelity/topology checks; choose geometry strategy based on asset role |
| What to reuse | Identify exact mesh/material archetypes; retopologize the canonical prototype once |
| When MultiMesh helps | Compare chunked MultiMesh to Forward+ automatic instancing and independent objects |
| How big a MultiMesh | Partition by visibility, lighting, archetype and shared-LOD behavior; measure, don't hardcode a distance |
| What makes the runtime fast | Draw submission **and** real submitted geometry **and** overdraw, culling, shadows, lighting and memory |
| How to ship | Export `.glb` + placement/QA manifests; a Godot 4.7 test harness verifies actual speed and correctness |

**Normative runtime extension:** §§25–38, including [G01]–[G13] engine-specific references. **Original geometry/retopology foundation:** §§1–24 and [R1]–[R18].


## 1. Executive summary

Build a Blender-only add-on, tentatively named **TopoSmith**, that examines one or more existing 3D models, creates an explicit retopology plan, executes a suitable strategy, validates the result against the source geometry, and retains both source and result for review.

The tool is intended for procedural, kitbashed, scanned, sculpted, and traditionally modeled assets, especially static environment and prop meshes. It must also recognize when a deformation-ready mesh requires guided/manual edge-loop design rather than fully automatic processing.

**Five core stages:**

1. **Inspect:** Profile evaluated geometry and detect defects, density patterns, material boundaries, sharp features, repeated grids, symmetry, thin shells, and likely deformation requirements.
2. **Plan:** Classify whole objects and mesh regions, decide what features must survive, generate candidate strategies, estimate risk and triangle savings, and write a reproducible plan.
3. **Execute:** Run the selected built-in Blender and BMesh operations on **copies**, using region-specific methods where practical.
4. **Validate:** Compare candidate meshes with source geometry using topology checks, surface-distance tests, silhouettes, sharp-edge preservation, material/attribute checks, and post-triangulation counts.
5. **Publish:** Commit a named low-poly object only when required gates pass; otherwise mark it for review with actionable diagnostics.

A planner-first workflow is the distinguishing feature. A single global target polygon count or one-click Quad Remesh is **not** the architecture. **v3.0 extension:** make the selected geometry economical *in the actual intended Godot scene* by preserving reuse, controlling material surfaces, planning MultiMesh batches, and requiring runtime benchmark evidence. See §§25–38.

**Evidence discipline:** This specification separates (1) verifiable Blender behavior, (2) published geometry-processing principles, (3) documented studio/practitioner workflows, and (4) project-specific engineering hypotheses. Only the first three may be called externally grounded. Numeric quality targets, classification cutoffs, and candidate search parameters are **proposed test values**, not industry standards.

### Non-goals

- Creating meshes from photographs, prompts, or other non-3D inputs.
- Automatically inventing missing geometry or changing an object's design.
- Guaranteeing production-quality edge loops for faces, articulated characters, or cloth without artist review.
- Replacing UV unwrapping or texture baking with inaccurate assumptions about automatic attribute preservation.
- Guaranteeing lower draw calls, smaller GPU memory use, or faster rendering from triangle reduction alone. All runtime improvements require in-engine proof.
- Relying on proprietary remesh add-ons, external executables, online services, non-Blender DCCs, or downloaded machine-learning models.
- Generating complete Godot levels or changing gameplay logic. Blender remains the sole retopology/planning/execution DCC. Built-in Blender glTF export and a JSON handoff to a **separate** Godot 4.7 validation/import harness are supported; the add-on must not depend on Godot being installed.

---

## 2. Users and representative assets

**Primary user:** Technical artist, tools engineer, or procedural modeling system running Blender as an asset-generation stage.

**Asset families:**

| Input mesh | Desired output | Likely approach | Special risk |
|---|---|---|---|
| Boolean-heavy wall, counter, vending machine, sign frame | Few large planar faces with protected bevels/openings | Planar region reconstruction + limited dissolve | Flattening holes, damaging hard corners |
| Dense, subdivided furniture or trim | Original clean cage or reduced regular grid | Un-Subdivide if the grid supports it | Misdetecting an irregular grid |
| Sculpted trash bag, rock, tree trunk, statue | Even, useful surface topology that holds silhouette | Quad remesh candidate + projection + inspection | Poor edge flow and lost material data |
| Scan-like noisy geometry | Repaired approximation only if allowed | Cleanup, possible voxel remesh, then quad/shape fit | Closed cavities and thin-shell loss |
| Chain-link mesh, leaf cards, torn poster, wiring | Preserve openings, alpha cards, distinct strands | Conservative cleanup or no-op | Voxel remesh fills openings; silhouette loss |
| Hinged door, folding prop, animated character part | Deliberate deformation zones and pivots | Preserve/rebuild articulation loops or guided retopo | Automatic remesh gives unusable bends |
| Complex assembled building asset | Different strategies across independent parts | Partition by component, optimize individually | Joining parts changes meaning and materials |

The tool must accept that **doing nothing may be the correct retopology decision**.

---

## 3. Functional requirements

### FR-01: Input and source protection

- Accept selected mesh objects, a Blender collection, or a batch configuration referencing scene object names/stable IDs.
- Support raw mesh and evaluated mesh snapshots. Default to **evaluated viewport geometry**, recording the modifier stack as a source dependency, but never applying modifiers to the original.
- Handle parent transforms, mirrored/negative scales, linked mesh data, instances, material slots, multiple UV layers, vertex groups, custom attributes, shape keys, bevel and sharp-edge metadata.
- Distinguish geometry that can be safely copied from data that cannot be carried to a new topology without explicit transfer or rebinding.
- Preserve originals in a protected source collection; put candidates into a preview collection.
- Refuse destructive execution on shared mesh data, shape-key-dependent topology, or evaluated modifiers that cannot be reproduced in a working copy without an explicit reviewed policy.

### FR-02: Mesh intelligence

- Produce an object-level and connected-component-level profile.
- Identify sharp boundaries, flat regions, dense curved regions, open boundaries, disconnected islands, suspicious internal surfaces, degenerates, and likely boolean debris.
- Record whether a mesh appears to be intentionally thin/open or unintentionally broken; uncertain cases require classification rather than automatic hole filling.
- Determine whether the existing mesh is already acceptable.

### FR-03: Planning

- Generate at least three strategy candidates when the classification permits them: conservative cleanup, shape-preserving simplification, and topology rebuild.
- Explain why each candidate is permitted or rejected.
- Predict approximate cost and risk; treat claimed triangle reduction as an **estimate**, not a fact, until preview geometry exists.
- Support per-object constraints: triangle budget, maximum geometric deviation, silhouette importance, UV/material protection, rigid vs deforming, symmetry, and permitted topology changes.
- Allow overrides of detected protected regions using face sets/attributes, vertex groups, marked edges, and artist-authored region labels.

### FR-04: Execution

- Provide Dry Run, Preview Candidate, Compare Candidates, Commit, Roll Back, and Batch Execute operations.
- Run native Blender operations via structured adapters rather than generating arbitrary operator sequences.
- Operate on a disposable mesh copy and track source-to-result provenance.
- Keep each major operation independently reproducible from a plan plus Blender version and asset fingerprint.
- Defer risky region stitching to a later implementation phase; never pretend it is solved by one modifier.

### FR-05: Verification

- Generate before/after statistics, deviation measurements, boundary/feature comparison, topology checks, and reason-coded pass/warn/fail outcomes.
- Reject results with broken required features even if triangle count drops dramatically.
- Publish reports in Blender text datablocks and sidecar JSON files when permitted by the workflow.
- Mark ambiguous meshes as `NEEDS_ARTIST_REVIEW`, not `PASS`.

---

## 4. Quality model: what counts as good retopology?

A successful result is judged against **asset intent**, not whether every face is a quad.

### A. Visual fidelity

- Preserve externally observable silhouette from specified viewing directions and distances.
- Preserve openings, recognizable proportions, bevel width, major contours, and surface changes.
- Retain shading quality when material and normal behavior are reapplied.
- Permit deletion of non-visible and redundant subdivisions only if a separate visibility/removal policy allows it.

### B. Geometric usefulness

- Rigid environment assets may use well-formed triangles or planar n-gons **if evaluated triangulation is stable and the mesh remains editable**.
- Deforming surfaces should favor intentional loop flow, even quad distribution, and sufficient loops across bend axes.
- Non-manifold edges are not universally bad: open planes, torn fabrics, foliage cards, and sheet metal may be intentional.
- Respect independent mesh shells where separation matters for materials, mechanics, rigging, or later editing.

### C. Performance relevance

- Measure **evaluated triangle count**, including the actual result of triangulating n-gons/quads; Blender polygon/face count alone is insufficient.
- Track material slots used, mesh instances, object count, bounding boxes, UV corner count, and vertex count as separate metrics.
- Warn when a candidate replaces inexpensive flat faces with high-density quad grids.
- Note that UV splits, sharp normals, material boundaries, and exporter decisions can increase final render vertices; low Blender vertex counts are not a guarantee of low GPU vertex counts.

### D. Editability

- Preserve meaningful edge boundaries on rigid objects, logical components, and deformable zones.
- Avoid long, skinny triangles, sliver faces, accidental T-junctions, unstable concave n-gons, and poles in high-deformation areas.
- Never optimize away a planned articulation seam or a mount/attachment surface.

---


## 4A. Required retopology fundamentals — the tool's knowledge base

This section is **normative**: an engineer implementing the planner must encode these distinctions rather than rely on a model or a single mesh-reduction operation. Blender describes retopology as replacing generated or sculpted topology with geometry fit for later use, and explicitly cautions that automatic remesh does not usually produce deformation-friendly edge flow. [R1]

### 4A.1 Four different jobs people call "retopology"

| Task | What changes | Success criterion | Blender implementation | What it is **not** |
|---|---|---|---|---|
| **Repair / cleanup** | Defects, redundant vertices, sliver edges | Valid, intentional existing surface | BMesh cleanup, protected dissolve [R2, R3] | Automatically rebuilding topology |
| **Simplification / LOD** | Number and placement of triangles | Lower complexity with bounded error | Decimate Collapse, optional manual optimization [R4, R16] | A guarantee of good deformation loops |
| **Remeshing / quadrangulation** | Surface tessellation and face structure | Regularity or quad-dominant sampling | QuadriFlow, Remesh, Shrinkwrap [R1, R5, R17] | Semantic interpretation of openings/joints |
| **Semantic retopology** | Intentional edge flow, patch structure and support loops | Fit for rigging, subdivision, editing, baking, or assembly | Manual/guided Poly Build, snapping, BMesh construction [R1, R6, R7] | A vertex-count contest |

**Mandatory output labels:** `CLEANED`, `SIMPLIFIED`, `AUTO_REMESHED`, `GUIDED_RETOPO`, `NO_OP`. Do not label a Decimate-only result `DEFORMATION_READY`, or an automatically generated quad mesh `HAND_AUTHORED_TOPOLOGY`.

### 4A.2 Mesh topology versus geometric shape

- **Geometry** is where surface points lie in 3D. **Topology** is how vertices, edges and faces connect. Two models can look identical while behaving very differently when bent, subdivided, UV-unwrapped or baked.
- A **quad** is a four-corner polygon; a **triangle** has three; an **n-gon** has five or more. Quads facilitate predictable loop editing and subdivision workflows, but real-time meshes are triangulated. Neither "100% quads" nor "0 n-gons" is an absolute requirement for all rigid game assets. [R4, R7, R10]
- An **edge loop** follows linked edges across quad-based flow; an **edge ring** traverses the opposite direction across the quads. A **pole** is a vertex with valence different from four in a quad interior. Poles can intentionally terminate/redirect loops; their location matters more than their mere existence. Blender Studio's topology course explicitly teaches loops, poles, stretch, pinching and articulation. [R7]
- **Support loops** establish creases for subdivision or deformation. Hard-surface baking can often preserve a bevel or sharp edge with a few geometry segments plus shading/normal data rather than dense uniform support grids. [R7, R11]
- **Boundary edges** have one incident face; **non-manifold edges** may have more than two or inconsistent configurations. A single-sided poster is an intentional open surface. A watertight solid generally should have properly paired and consistently oriented edges; do **not** blanket-repair all boundaries. [R2]
- **Face winding and normals** govern surface orientation and shading; hard edges, UV splits and material splits are distinct constraints that can coincide but are not interchangeable. [R10, R11, R12]
- **A UV is face-corner (loop) data**, not simply a property of the 3D vertex. One point on a 3D seam may need different UV coordinates on its adjoining face corners. Blender's data-transfer documentation treats these domains distinctly. [R9]

**Implementation rule:** Store topology checks and visual checks in separate objects. A good surface distance cannot prove good edge flow; a high quad percentage cannot prove silhouette fidelity.

### 4A.3 Edge flow follows the intended use

**Rigid planar hard surface:** Prefer broad planar spans, clean corners, intentional openings, bevels where visible, and economical geometry. A wall need not contain evenly spaced quads. Planar dissolve is explicitly provided for geometry made of mostly flat surfaces. [R3, R4]

**Curved rigid assets:** Allocate segments around curvature where they improve the *viewed silhouette*, not indiscriminately across entire flat/hidden regions. Keep stable ring orientation around cylinders, handles, curved pipes and trim. Avoid abrupt density transitions that produce pinching or thin triangles.

**Deforming surfaces:** Plan loops around actual bending axes, articulation zones, expression landmarks, folds or cloth seams. A bend needs usable topology on both sides of its axis and appropriate spacing through its transition. Place extraordinary vertices away from high-strain areas where possible. Blender Studio recommends loops near clothing seams/landmarks, starting symmetrically when beneficial, and coordinating pivot placement before rigging. [R6, R7]

**Background or thin cards:** Keep intended open borders, UV islands, alpha-card shapes, and separate components. Do not volumetrically remesh foliage cards, posters, chain-link patterns, ropes or cables without explicit per-component permission.

**Already clean assets:** Prefer the existing topology. The Decimate manual explains it is mostly useful when the initial mesh has redundant geometry (e.g., sculpted/subdivided), not a guarantee of improvement on an already economical model. [R4]

### 4A.4 Topology heuristics that are not universal laws

1. "All quads" — useful for subdivision and many deformers; can increase geometry waste on flat game-ready panels.
2. "Triangles are bad" — false as a general rule; triangles can be legitimate final rigid render geometry. Their position and shading implications matter.
3. "An n-gon means a defect" — false on certain static planar meshes; unstable triangulation, concavity, irregular shading or downstream editability make some n-gons unsuitable.
4. "No poles" — impossible or unnecessary for many useful quad arrangements; **poles in a bending crease** are the main risk.
5. "Even polygon density everywhere" — wasteful for a game asset; concentrate density in critical silhouettes, curvature, bake support and deformation areas.
6. "Normal maps fix every silhouette" — false; a tangent-space normal map changes shading, not the silhouette.
7. "Fewer Blender vertices means fewer runtime vertices" — false where face-corner attributes, hard normals and UV seams require multiple render vertices. Polycount's game-art discussion is useful practice context, not an exact export-count formula. [R11]
8. "Auto-remeshed quads are animation-ready" — directly contradicted by Blender's general retopology guidance. [R1]

### 4A.5 Intent, scale and viewing distance must drive density

The planner must accept at least: `view_class` (`HERO_NEAR`, `MID_DISTANCE`, `BACKGROUND`), `camera_fov`, optional approximate on-screen size, smallest meaningful feature size, and whether silhouette or deformation has priority. There is **no universal triangle-per-meter target**. A curb corner, a vending machine button, a cable and a cloth sleeve require different decisions.

**Analytic starting point (not a claimed industry threshold):** If a smooth cross-section is approximated with straight chords, chord sagitta error for arc radius `r` and segment angle `theta` is `e = r * (1 - cos(theta/2))`. Use this as a *candidate sizing estimate* for curved profiles, then validate actual silhouette in camera views. Screen-pixel thresholds must be calibrated to the project's rendering and asset-review workflow.

**Preferred tri-allocation order:** (1) retain gameplay/mechanical holes and attachment features; (2) retain silhouette and important outlines; (3) retain enough geometry for appropriate deformation; (4) retain visible bevel profiles; (5) simplify planar interiors and hidden/redundant subdivisions. This is a proposed production prioritization rule, not an immutable art law.

### 4A.6 Understand simplification theory; do not pretend Blender gives guarantees it does not

Garland and Heckbert's 1997 **quadric error metrics (QEM)** paper demonstrates error-guided mesh simplification using vertex-pair contractions. It explains the class of tradeoffs that motivate surface-preserving decimation, **but this TDD does not assert that Blender's current Decimate modifier implements exactly that paper's algorithm**. [R16]

Huang et al.'s 2018 **QuadriFlow** research addresses quadrangulation and the reduction of singularities in quad meshes. Its objective is better quadrangulation—not authored joint loops, mechanical hole semantics, UV preservation or a proof that a mesh is low-poly enough for a game. [R17]

Cignoni, Rocchini and Scopigno's 1998 **Metro** work establishes a precedent for *sampling surfaces to compare simplifications*, rather than judging changes solely through topology or vertex counts. This document adopts that verification philosophy with explicit limitations around finite sampling and small features. [R18]

### 4A.7 Foundation-to-algorithm traceability (required in code reviews)

| Source-grounded principle | Planner rule | Executor requirement | Validator requirement |
|---|---|---|---|
| Auto quad flow often not good for deformation [R1, R6] | `DEFORMING` blocks auto-publish | Guided loops/manual approval | Pose / bend tests mandatory |
| Decimate has distinct Collapse, Un-Subdivide, Planar modes [R4] | Classify planar vs grid vs arbitrary | Independent strategy adapters | Compare outputs, don't equate modes |
| Data Transfer interpolates typed layers [R9] | Explicit `preserve_*` contract | Domain-aware transfer or skip | UV/material seam and shading tests |
| Blender baking uses selected-to-active, ray distance/cage, margins [R12] | Plan bake dependency if normals change | Generate bake handoff, not silent preservation | Test bake on representative fixture |
| Poly Build and surface snapping support retopo [R1, R8] | Unknown deformation routes to guided | Prepare source / target shell | Validate final guided surface |
| Sampling compares simplified surfaces [R18] | Require bidirectional QA | Deterministic surface sample sets | Mean / P95 / max sampled deviations |
| UV/hard-normal splits affect render vertices [R11] | Separate `tris` from render vertex estimate | Preserve splitting metadata | Report split/corner counts and limits |

---

## 5. High-level architecture

```text
Scene selection / Collection / Batch manifest
               |
               v
       Snapshot & Fingerprint
               |
               v
      Geometry Profile Engine
               |
               v
  Component / Feature Segmentation
               |
               v
         Retopology Planner
      /       |         \
  Cleanup   Simplify    Rebuild/Guided
      \       |         /
               v
    Candidate Executor (copies)
               |
               v
     Geometry & Fidelity QA
               |
      +--------+--------+
      |                 |
    Pass            Warn / Fail
      |                 |
  Commit Output    Review / Roll Back
      \                 /
               v
         Report + Provenance
```

### Blender add-on package

```text
blender_toposmith/
  __init__.py
  registration.py
  ui/
    panels.py
    operators.py
    overlays.py
  core/
    snapshot.py
    profile.py
    connectivity.py
    feature_detection.py
    region_classifier.py
    planner.py
    candidate_selector.py
  strategies/
    base.py
    cleanup.py
    planar.py
    unsubdivide.py
    decimate.py
    quadriflow.py
    voxel_repair.py
    guided.py
    stitching.py              # later phase, feature gated
  validation/
    topology.py
    deviation.py
    silhouette.py
    attributes.py
    quality.py
  runtime/                    # v3.0: Blender analysis + manifests, no Godot dependency
    intent.py
    archetypes.py
    render_vertex_proxy.py
    surface_cost.py
    spatial_batching.py
    lod_hlod_plan.py
    godot_export_profile.py
    runtime_status.py
  io/
    schema.py
    reports.py
    fingerprints.py
  tests/
    fixtures/
    test_profile.py
    test_planner.py
    test_strategies.py
    test_quality.py
    test_batch.py
```

**Architectural invariant:** The `planner` depends on abstract strategy capabilities, not hardcoded knowledge of UI operators. Strategy adapters own Blender-specific side effects. Validation is independent of candidate generation.

---

## 6. Source snapshot and coordinate system

### 6.1 Geometry snapshot procedure

1. Record object name, internal persistent identifier where available, transformation matrix, parent relationship, data-block sharing, modifier inventory, materials, UV layers, attributes, shape keys, and scene version.
2. Obtain the evaluated dependency graph: `bpy.context.evaluated_depsgraph_get()`.
3. Copy the evaluated mesh into a **real, persistent candidate mesh**. An evaluated object's `to_mesh()` result is temporary and must be cleared via `to_mesh_clear()`; do not attach that temporary mesh directly to a permanent object. Use a correctly owned mesh datablock copy before cleanup.
4. Keep source and candidate in one comparison space. For QA, use consistent **world-space coordinates**, taking `matrix_world` into account. For operations requiring local-space meshes, preserve the transform mapping explicitly.
5. Store an exact source geometry fingerprint, alongside a lighter settings fingerprint, before execution.
6. Confirm that edits cannot mutate the original datablock; clone when objects share linked mesh data.

### 6.2 Transform safety

- Handle negative determinant transforms by checking winding/normal interpretation in world space.
- Never silently apply a destructive scale to the original object.
- Record effective dimension `D` as the maximum world-space axis-aligned bounding-box extent, with a nonzero epsilon for degenerate shapes.
- Use relative tolerances expressed as a fraction of `D` or as a meaningful feature dimension. Relative tolerances alone are inadequate for very thin geometry, so include a thickness constraint where known.
- Use a consistent unit policy. A centimeter-thick strip on a building cannot be treated like noise merely because it is small compared with the whole building.

---

## 7. Geometry analysis specification

### 7.1 Required profile fields

| Metric | Implementation direction | Purpose |
|---|---|---|
| Vertex, edge, face counts | Mesh/BMesh collections | Baseline complexity |
| Evaluated triangle count | `mesh.calc_loop_triangles()` and `len(mesh.loop_triangles)` | Actual rasterized geometry proxy |
| Connected components | Traverse adjacency in BMesh | Keep distinct mesh islands distinct |
| Boundary and non-manifold edges | Edge incident-face counts | Diagnose open or broken shells |
| Degenerate faces/edges | Area/length against scale-relative epsilon | Find fragile inputs |
| Loose vertices/edges | Connectivity analysis | Cleanup candidates |
| Triangle aspect ratio and edge-length distribution | Face geometry | Detect slivers and excess tessellation |
| Dihedral angle distribution | Adjacent face normals | Detect hard edges and planar patches |
| Curvature proxy | Neighborhood normal variation across edge neighborhoods | Estimate areas needing density |
| Material/UV/sharp seams | Face-corner and edge attributes | Hard protection boundaries |
| Component volume/watertightness | Manifold + winding conditions; volume only if meaningful | Volume repair eligibility |
| Repeated regular quads | Edge valence and quad-grid consistency | Un-Subdivide eligibility |
| Symmetry likelihood | Sample mirrored points against BVH | Optional constrained strategy |
| Normal inconsistency | Adjacent winding checks | Reorientation or review |
| Local geometric thickness | Opposing-ray samples where meaningful | Thin-shell protection |
| Bounding box/object transform | World-space transforms | Physical scale |
| Modifier and shape-key state | Blender object and mesh metadata | Preservation policy |

### 7.2 Protected feature graph

Produce an explicit graph of edges, surfaces, and vertices that must not be destroyed casually. Each edge may have multiple reasons:

- `BOUNDARY` — an intentional opening or component boundary.
- `HARD_EDGE` — dihedral angle exceeds threshold, with optional artist override.
- `UV_SEAM` — marked seam or discontinuous face-corner UVs.
- `MATERIAL_BORDER` — incident faces use different materials.
- `SHARP_NORMAL` — discontinuous shading/marked sharp edge.
- `SILHOUETTE_IMPORTANT` — contributes to visible outline across sampled camera directions.
- `MECHANICAL` — hinge, mounting lip, mating surface, hole rim, bolt seat.
- `DEFORMATION` — manually marked loop or bend zone.
- `ARTIST_LOCK` — do not modify without override.

**Protected status is a constraint**, not just a high scoring weight. The default must forbid dissolving locked edges and forbid hole filling on intentionally open boundary loops.

### 7.3 Region classification

Classify connected components first, then subregions where useful:

1. `PLANAR_HARD_SURFACE` — broad flat patches separated by distinct creases.
2. `CURVED_RIGID` — rigid silhouette-defining smooth bends.
3. `REGULAR_GRID` — dense but recognizably subdivided quad lattice.
4. `SCULPT_ORGANIC` — dense irregular geometry dominated by curvature.
5. `THIN_OPEN_SHELL` — single-sided or nearly zero-thickness sheets.
6. `SMALL_DELICATE` — cables, foliage, tiny supports, thin rods.
7. `DEFORMING` — artist-marked or rig-influenced surfaces.
8. `MIXED_OR_UNKNOWN` — ambiguous topology; conservative method or manual plan.

Store `confidence`, `evidence`, and `uncertainties`, not a single unconditional label.

**MVP classifier:** Deterministic threshold rules plus confidence scores; no ML dependency. Rules are configurable, versioned, and testable. Later phases can improve heuristics without changing execution contracts.

---


### 7.4 Geometry feature extractor — detailed methods and ambiguity controls

Retopology quality is limited by feature recognition. The following are **proposed algorithms**, not built-in Blender classifiers.

**A. Connected components:** Walk face-to-face adjacency through shared mesh edges; record all loose edges/verts separately. Do not join components because their positions are close. Preserve component IDs and material/attribute inventories.

**B. Face orientation and dihedral:** For each manifold edge `e` shared by `f1, f2`, compute the angle between their world-space face normals, accounting for negative determinants; then combine with explicit sharp marks, UV discontinuities, material boundaries and user locks. Angle-only detection misses visually important shallow but sharp silhouette transitions.

**C. Coplanar patches:** Region-grow across edges that are not protected when neighboring planes differ below configured *angular and point-to-plane* tolerances. Check plane offsets; parallel but offset faces must not collapse into one planar patch. Every patch records external loops and nested inner loops as a half-edge graph.

**D. UV seam detection:** Compare face-corner UV coordinates at both endpoints of each shared edge across both incident faces. Include marked seams and all UV layers required by the input contract. Coincident UV coordinates are not proof that a seam is semantically unimportant.

**E. Curvature/density:** Estimate normal variation over geodesic edge neighborhoods and compare it to local triangle area. Treat rapid changes near hard edges as feature boundaries rather than simply "dense organic" texture. This distinguishes unnecessary planar grid density from necessary curvature resolution.

**F. Grid signature:** Require a coherent quad lattice over a sufficiently large connected region, not merely a high percentage of quads. Score regular valence, aligned edge strips, regular spacing and low numbers of T-junctions or inconsistent loops. Only then try Un-Subdivide.

**G. Holes/open boundaries:** Extract each boundary cycle or open chain with winding and approximate area. The contour signature includes its perimeter, center, plane normal (where meaningful) and relation to nearby material/semantic locks. A circular bolt hole, door opening and loose poster edge are distinct.

**H. Thin feature warnings:** Combine component width, edge-length distribution, local normal pairs and bounded ray tests. Opposing-ray thickness estimates are not reliable on all open sheets; report confidence and refuse blind voxel processing below confidence floor.

**I. Surface interactions:** Record proximity between *different* components as a candidate accidental bridge risk. A touch between a shelf bracket and wall is not necessarily a weld instruction.

**J. Silhouette landmarks:** Under authored view directions, mark profile edges and vertices at extremal outline changes; prioritize them over invisible interior subdivisions. A view-dependent feature may be unimportant for a background mesh but mandatory on a hero model.

Feature detection must produce both **machine evidence** and an **artist-readable overlay**. `confidence < threshold` routes to conservative operations or approval; threshold values come from fixture calibration.

### 7.5 Half-edge/topology graph invariants

For every candidate, persist a feature-graph map from source entities to candidate *spatial correspondences*, not just integer vertex indices (which will change). Required invariants:

- `LOCKED_BOUNDARY`: same meaningful opening count and contour within tolerance; candidate edge IDs may differ.
- `LOCKED_COMPONENT`: never merged or deleted without approved waiver.
- `MECHANICAL_HOLE`: opening diameter/shape and its position remain within absolute units defined by the user.
- `MATERIAL_REGION`: material membership is preserved except explicitly remapped areas.
- `UV_ISLAND`: coverage and seam topology are checked; do not assume equal number of islands is sufficient.
- `ARTICULATION`: hinge axis, attachment seam, and guided deformation bands persist.

A geometric comparison alone is **not** sufficient to prove these invariants.

## 8. Planning engine

The planner must generate explicit alternatives, screen them against hard constraints, preview viable candidates, and select the best **passing** candidate.

### 8.1 Plan inputs

- `asset_role`: `STATIC_ENV`, `STATIC_PROP`, `RIGID_ANIMATED`, `DEFORMING`, `UNKNOWN`.
- `visual_priority`: `HERO`, `STANDARD`, `BACKGROUND`.
- `geometry_policy`: `PRESERVE_OPEN`, `PRESERVE_VOLUME`, `REPAIR_ALLOWED`, `DO_NOT_ASSUME`.
- `topology_style`: `EDITABLE_RIGID`, `QUAD_PREFERRED`, `DEFORMATION_READY`, `MIN_TRIANGLES`.
- `target_tris` and optional `max_tris`; neither may override fidelity hard gates.
- `max_p95_distance`, `max_distance`, `min_silhouette_iou`, sharp-edge deviation tolerance.
- `preserve_materials`, `preserve_uvs`, `preserve_attributes`, `preserve_sharp`, `preserve_boundaries`.
- `allow_quad_remesh`, `allow_voxel`, `allow_decimate`, `allow_component_separation`, `allow_topology_change`.
- `time_budget_seconds`, `candidate_budget`, `seed`, `interactive_vs_headless`.

### 8.2 Strategy selection rules

| Detected condition | Prefer | Avoid |
|---|---|---|
| Largely planar and dense from booleans | Protected limited dissolve, region cleanup | Uniform quad grid over walls |
| Clean, overly subdivided quad grid | Un-Subdivide trial | Blind global edge collapse |
| Dense, irregular, rigid sculpt | Quad remesh trial or conservative simplification | Assuming auto-generated quads follow animation joints |
| Noisy sealed volume and explicit repair permission | Voxel repair **as preprocessing**, then retopo | Voxel on intentionally open sheet |
| Thin/open shell or separate rods | Conservative cleanup/manual preservation | Voxel volume regeneration |
| Deforming, needs edge flow | Guided manual route with loops and surface snap | Automatic pass label without deformation test |
| Existing efficient mesh | No-op plus QA | Forced triangle reduction |
| Mixed rigid mesh with high-risk feature borders | Component/region plan | Global one-size-fits-all remesh |

**Quad remesh is not guaranteed to deliver rig-ready loops; voxel remesh is not a general final low-poly solution.** Blender's own retopology guidance distinguishes these uses.

### 8.3 Candidate ranking

First reject candidates that violate hard constraints. Among survivors:

```text
candidate_utility =
    w_visual   * fidelity_score
  + w_topology * topology_suitability
  + w_editable * editability_score
  + w_budget   * triangle_budget_score
  - w_risk     * operation_risk
  - w_cost     * execution_cost
```

Scores are normalized and calibrated with fixture assets. **Never trade away an actual hard-feature failure for a better triangle count.** Keep candidates on a Pareto frontier of fidelity, quality, and triangle count; allow user selection where multiple tradeoffs pass.

Planning output includes: rationale, permitted methods, prohibited methods, protection graph summary, estimated QA risks, initial parameters, candidate execution order, and explicit approval requirements.

---


### 8.4 Source-driven decision model with explicit prohibitions

Decision order is *hard preconditions → protection graph → candidate routes → measured QA*. Examples:

| Source condition | Hard precondition | Candidate strategies | Automatic publish policy | Evidence |
|---|---|---|---|---|
| Flat storefront wall + window cutouts | Boundary graph extracted and locked | S1 → S2 | Pass only if holes/UV borders unchanged | Blender Planar + Limited Dissolve [R3, R4] |
| Panel dense from subdivision | Quad-grid evidence high | S3; fallback S1 | Pass if surface + loop landmarks survive | Un-Subdivide documented for grids [R4] |
| Sculpted trash bag (static) | Noncritical cloth folds identified; UV policy set | S5 and S4 trials | Conditional on silhouette / attributes / shading | QuadriFlow, Decimate [R4, R5, R17] |
| Bent cable or single-sided leaf | Explicit preserve-open / thin profile | S0/S1 only by default | No voxel repair | Voxel makes a new manifold-like volume [R5] |
| Door with animated hinge | Hinge pivot/rig dependence identified | S0/S7 | Manual approval | Blender Studio landmark / pivot advice [R6] |
| Character elbow, knee, face | Bone/expression targets and representative poses available | S7; S5 as reference **only** | Pose-test + artist approval | Blender / Blender Studio [R1, R6, R7] |
| Sealed noisy scan marked repairable | Valid size scale; fragile openings annotated | S6 preprocessing → S5 | Review required for repaired topology | Remesh docs [R5] |
| Existing low-poly prop | Meets all feature and QA requirements | S0 | Valid outcome | Decimate's intended use [R4] |

**Planner must explain rejections:** e.g., `VOXEL_FORBIDDEN_OPEN_SHELL`, `QUADRIFLOW_NOT_DEFORMATION_SAFE`, `PRESERVE_UV_UNKNOWN`, `UNSUBDIV_GRID_CONFIDENCE_LOW`, `ATTRIBUTE_TRANSFER_UNVERIFIED`.

### 8.5 Planning the topology, not just picking a modifier

The planner's saved `TopologyIntent` object must contain:

```json
{
  "asset_intent": "STATIC_PROP",
  "primary_quality_goal": "SHAPE_AND_SHADING",
  "subregions": [
    {"tag": "flat_housing", "target": "LARGE_PLANAR_SPANS", "locked_features": ["front_screen_opening", "panel_uv_border"]},
    {"tag": "rounded_trim", "target": "CURVATURE_ALIGNED_RINGS", "minimum_required_shape": "silhouette_tolerance"},
    {"tag": "buttons", "target": "SEPARATE_COMPONENTS_OR_PRESERVE", "min_feature_size_m": 0.01}
  ],
  "no_go_actions": ["JOIN_DISCONNECTED_COMPONENTS", "FILL_PROTECTED_HOLES"],
  "artist_review_required": false
}
```

This is **illustrative**, not a universally correct design of vending-machine buttons. In production the tool should read configured scale and metadata rather than infer feature sizes from an object name.

The plan should state which parts will be **retained**, **simplified**, **reconstructed**, **projected**, **rebaked**, or **sent for guided authoring**. Candidate previews must use this same plan so the initial intent can be compared with the resulting mesh.

## 9. Execution strategies (Blender only)

### Strategy S0 — No-op / preserve

**When:** Already within limits, nontrivial data transfer risks, or unsafe topology change.

**Action:** Validate, optionally remove demonstrably loose unreferenced geometry on a copy, and return an unchanged mesh with a report. No-op counts as a valid solution.

### Strategy S1 — Conservative topology cleanup

**When:** Mostly usable topology with duplicate vertices, degenerate faces, unnecessary edges, or local defects.

**Operations:** Blender BMesh supports cleanup, dissolve and triangulation routines [R2]. BMesh `dissolve_degenerate`, selected `dissolve_edges` / `dissolve_verts`, guarded remove doubles, controlled dissolve, recalculation of normals when safe, and optional triangle edge beautification.

**Guardrails:**

- Merge by distance only below a scale/feature-aware epsilon and only across allowed boundaries.
- Do not merge parts merely because they occupy the same place; overlapping shells may be intentional.
- Preserve protected edges and explicit material/UV discontinuities.
- Inspect candidate after **each** cleanup class. Roll back operations that breach constraints.

### Strategy S2 — Planar hard-surface retopology

**When:** Architecture, machine housings, rectangular props, and boolean-heavy shapes with extensive coplanar faces.

**Algorithm:**

1. Segment the mesh into coplanar face clusters using a configurable dihedral tolerance and protection graph.
2. Record each cluster's external boundary and internal hole loops. Include required crease, bevel, UV, and material borders.
3. Propose `bmesh.ops.dissolve_limit` constrained by `MATERIAL`, `SEAM`, `SHARP`, `UV`, and `NORMAL` delimiters (where supported by target Blender API). For simpler cases, protected edge dissolves suffice.
4. Verify that boundary loops, holes, silhouette, and material borders survive.
5. Inspect resulting n-gon triangulation and face quality; subdivide or manually reconstruct invalid concave/degenerate regions.
6. Restore appropriate shading attributes where permitted, validate, and produce a candidate.

**Key rule:** Fewer Blender polygons can still produce almost the same number of render triangles. Report both. Do not deliberately build large coplanar quad grids simply to achieve a high quad percentage.

**Later enhancement:** True patch reconstruction from boundary loops, with constrained triangulation and quad-friendly patching on simple planar domains. Requires robust hole tracking and seam propagation; it is **not** in MVP.

### Strategy S3 — Grid recovery / Un-Subdivide

**When:** A mesh appears to have been created by repeated subdivision of regular quad topology.

**Algorithm:**

1. Confirm a high ratio of quads, mostly regular edge valence, and compatible row/column structure.
2. Duplicate mesh and run a limited, testable number of Un-Subdivide iterations (commonly test even iteration counts for inverse subdivision behavior).
3. Compare reconstructed cage against the original using BVH and silhouette QA.
4. Stop if the result introduces distortion, eliminates protected loops, or fails a grid-consistency check.

**Do not run merely because a mesh contains many quads.** Curved organic retopology can also be quad-dominant without originating from subdivision.

### Strategy S4 — Controlled decimation (optimization, not guaranteed retopology)

**When:** A rigid mesh needs a lower triangle count and clean semantic edge flow is not the dominant requirement.

**Method:** Blender explicitly separates Collapse, Un-Subdivide and Planar Decimate approaches [R4]. Trial Decimate modifier in Collapse mode at graduated ratios, optionally restricted to a vertex group to shield high-value regions. Optionally combine with protected planar cleanup.

**Constraints:** Preserve silhouette and feature gates, refuse deformation-ready promises, and inspect changes to UVs/materials/custom data. Label output `SIMPLIFIED`, not automatically `CLEAN_RETOPO`.

**Purpose:** A candidate low-poly result when performance budget dominates; not a substitute for planned edge-loop rebuilding.

### Strategy S5 — Native QuadriFlow remeshing

**When:** Irregular dense organic or curved geometry, quad-preferred output, and a recoverable source surface.

**Method:** The bundled operator offers face/edge/ratio targets, seed, boundary and sharp-preservation controls (availability and semantics must be checked for the pinned build) [R5, R14]; the published QuadriFlow method focuses on quadrangulation rather than rigging requirements [R17]. Duplicate evaluated source, run Blender's `bpy.ops.object.quadriflow_remesh` with target face budget and feature/boundary preservation options **only when supported by the installed API**; use reproducible seed and record exact arguments.

**Next steps:** Compare silhouette and surface fidelity, inspect high-risk bends/edge flow, optionally project the candidate to the original via Shrinkwrap/BVH, and validate materials/attributes from actual result (not promised behavior).

**Limitations:** Quadriflow may lose data layers or insufficiently preserve hard mechanical features. Automatic quad loops are not guaranteed usable for deformation. The operator requires a valid object/context and can be relatively expensive.

### Strategy S6 — Voxel repair as optional preprocessing

**When:** A noisy, intersecting, intentionally watertight volumetric source needs reconstruction **and the user allowed repair**.

**Method:** Trial native Voxel Remesh/Remesh modifier at several feature-aware voxel sizes, validate volume and silhouette, then optionally pass the output into S5 or S4.

**Limitations:** Voxel methods can seal openings, thicken/erase thin forms, bridge touching but separate objects, and destroy original attributes. Refuse on thin sheets, wire meshes, foliage cards, open forms, and critical holes unless explicitly approved.

**Never call the raw voxel output production-ready low-poly by default.**

### Strategy S7 — Guided/manual topology reconstruction

**When:** Deformation loops, facial topology, hinges, cloth, articulated supports, unresolved hard corners, or region stitching require artist intent.

**Tool-assisted workflow:**

1. Display source as a protected visible/reference mesh.
2. Show proposed patch boundaries and protected lines.
3. Create a lightweight editable target shell with surface snapping enabled.
4. Support Blender Poly Build, extrude, bridge edge loops, grid fill, and Shrinkwrap targeted to the source.
5. Mark necessary loops and approve patch boundaries before continuing.
6. Re-run the same automated validators for guided results.

**In-scope:** Analyze, mark problem regions, establish seed/reference surfaces, validate artist reconstruction. **Out-of-scope for MVP:** Autonomous production-quality edge-flow synthesis on arbitrary deforming objects.

### Strategy S8 — Mixed method by component/region (advanced)

For complex meshes, route **separate connected components** to different strategies first. This is much safer than cutting arbitrary surface patches apart.

A later regional pipeline can segment a single connected shell along approved closed boundary loops, process patches independently, and stitch them back. Release only once the seam engine can prove consistent boundary vertex counts, winding, position, attribute continuity, and no new T-junctions. If stitching fails, retain pieces as separate candidates for review rather than silently welding them.

---


## 9A. Topology construction playbooks (normative procedures)

These playbooks translate art fundamentals into actionable Blender-only work. The existing S0–S8 adapters remain execution primitives; these are higher-level **recipes**, not new modifiers.

### 9A.1 Rigid architecture, storefront facades, walls and curbs

**Goal:** An efficient editable mesh with meaningful cutouts, corners, proportions and UV boundaries.

1. Verify object scale / transforms; snapshot evaluated source before touching BMesh.
2. Extract intentional inner and outer boundaries and their material/UV/seam/sharp tags; mark critical holes, joints and trims.
3. Partition into adjacent approximately coplanar patches; use signed plane offsets to avoid merging separate parallel walls.
4. Trial planar dissolve (`bmesh.ops.dissolve_limit`, angular boundary and explicit delimit set) on a disposable copy. Use BMesh edge operations for tightly protected local edits. [R2, R3]
5. Reject if any cutout collapses, boundary orientation flips, a material island merges, the candidate becomes self-intersecting or triangulation degrades.
6. For complex concave n-gons, generate a reviewed constrained local subdivision/triangulation candidate. Do not promise general polygon-with-holes meshing in the MVP.
7. Preserve or reconstruct visible bevel cross sections based on silhouettes and shading; do not generate blanket support loops throughout a flat facade.
8. Produce face-by-face before/after visual overlays: corner profile, seam graph, UV islands and triangle distribution.

**Prove with:** window/door hole contour tests, world-space deviation, front and oblique orthographic silhouettes, UV material continuity and stable triangulation under the declared render path.

**False-positive example:** A 4,000-face wall becomes a 14-face n-gon with one missing doorway. Triangle count improves, but result must fail `CRITICAL_OPENING_MISSING`.

### 9A.2 Cylinders, pipes, utility poles, tires and round trim

**Goal:** Clean axial flow with just enough circumferential segments to hold the silhouette and local attachments.

1. Detect/confirm axis and whether geometry is a connected pipe, a hollow tube, a rod or an overlapping assembly.
2. Identify circumference rings, bend landmarks, junctions and protected section changes; retain branching/pipe openings.
3. Estimate ring density from circumference and curvature; keep extra rings at attachments/bends rather than uniform arbitrary increments.
4. Propose profile-preserving collapse, selected ring removal or guided ring reconstruction; do **not** average across material/UV hard boundaries.
5. Do not project vertices to the wrong nearby tube surface. If nearest-surface mapping is ambiguous, constrain by component IDs, normals and local projection direction. [R15]
6. Check profile with radial silhouette cameras and projected centerline drift; compare bore diameter where applicable.

**Prove with:** circumference/cross-section error at key stations, tube openness, bend continuity and tri count.

### 9A.3 Hard-surface machines with boolean cuts and inset panels

**Goal:** Controlled corners and stable shading with mechanical holes preserved.

1. Separate independent assemblies logically (housing, screen, panel, knobs); do not infer welding from intersection.
2. Build hard-feature graph from explicitly sharp edges, panel outlines, mechanical openings and UV/material cuts.
3. Run local planar cleanup on housing and optional controlled collapse on curved trim. Avoid uniform global remesh when flat panels dominate.
4. Where Boolean-generated triangles are necessary near openings, prioritize good triangle shape and stable final triangulation rather than arbitrary all-quad reconstruction.
5. Preserve key bevel profiles geometrically if they alter silhouette; allow normal-map detail only where a valid bake workflow exists.
6. Validate in neutral clay shading, edge-contrast test, final material shading and isolated UV view.

**Prove with:** locked cutout contour accuracy, shading discontinuity check, triangulation stability and a Blender-only normal-bake test where required. Blender's normal baking supports selected-to-active and cage/ray controls. [R12]

### 9A.4 Sculpted organic static props (rocks, bags, roots and debris)

**Goal:** Represent the intended *large and medium forms* with lower/easier surface topology, without trusting automatic quad layout as semantic artistry.

1. Identify silhouette-critical ridges, concavities, thin folds and separate components; mark truly small high-frequency sculpt detail as optional bake detail.
2. Generate a low-face-count QuadriFlow candidate and a Decimate candidate as **distinct alternatives**. [R4, R5, R17]
3. Project new geometry toward source with constrained Shrinkwrap/BVH correspondence; protect narrow gaps from accidentally snapping to the wrong side. [R15]
4. Inspect curvature distributions, pole concentrations in highly visible creases and self-intersections.
5. If texture and shading rely on sculpted detail, create a baking dependency rather than asserting low-poly geometry retains it automatically.
6. Rank candidates by silhouette, measured shape error, shading and triangle budget. Allow a slightly heavier but better-defined silhouette to win.

**Prove with:** bidirectional sampled surface differences, principal-view silhouettes, close-view shading and no critical thin-feature loss.

### 9A.5 Deformation-ready elbows, knees, cloth and faces

**Goal:** Topology designed for the intended deformation, not merely fewer polygons.

1. Require actual `deformation_intent`: hinge/bone axis, expected motion range, seam landmarks, key poses or shape keys and minimum bend quality. If missing, return `NEEDS_ARTIST_PLAN`.
2. Place/approve edge loops across the bend zone, maintain enough rows for the intended bending arc and place changes in flow away from peak compression/stretch where practical. Blender Studio addresses landmarks, seam loops, joint pivots, body loops and facial articulation. [R6, R7]
3. Use symmetry for the initial construction if helpful, but keep sanctioned asymmetry and deformation targets; Blender Studio recommends preserving a symmetrical reference copy for some character workflows. [R6]
4. Use Blender's Retopology overlay, Poly Build, snapping and optional Shrinkwrap to author a distinct cage on the source. [R1, R8, R15]
5. Preserve skeleton-independent source/target correspondence metadata. If shape keys exist, a topology change cannot simply reuse their vertex-indexed coordinates; treat reconstruction and corrective shapes as separate reviewed tasks. [R6]
6. Test representative poses: fully extended, neutral, flexed, twisted where applicable. Check local face inversions, volume loss, seam tearing, pinching and silhouette.

**Mandatory rule:** An auto quad remesh may provide a *starting shell* but must not be auto-certified as deformation-ready, even if its quads are regular and its static shape error is tiny. [R1]

### 9A.6 Intentionally open and extremely delicate models

A thin poster, a wire fence, loose cable, perforated grille or card foliage may be non-manifold by design. Default strategy is `NO_OP` or **local cleanup**. Voxel remesh, blanket hole filling, component merging and massive automatic polygon reduction are forbidden unless a human explicitly changes geometry policy. [R2, R5]

### 9A.7 Projection and attribute-transfer safety

Blender Data Transfer can interpolate UVs, colors, custom normals and other domain-dependent data through supported mappings, but that does not guarantee correct results at seams or across adjacent yet semantically distinct components. [R9]

A proposed transfer pipeline should:

- Match components/regions first; **never** use one global nearest face for several touching objects without disambiguation.
- Transfer POINT, EDGE, FACE and CORNER data via appropriate methods; preserve named layers and supported data types.
- Check UV samples near seams and material borders before passing candidate; compare UV island topology and distortion after mapping.
- Record any regenerated data and mark output incomplete until its required UV/bake/shading checks pass.
- Where normal-map baking is needed, use a Blender selected-to-active handoff with the reviewed high-poly source, the low-poly mesh, unambiguous cage/ray settings and UV padding. Validate render result; don't bake automatically in a headless MVP with no known target image setup. [R12]

---

## 10. Candidate generation and adaptive search

No optimization attempt should depend on one guessed parameter.

### MVP trial search

- `PLANAR`: angle tolerances such as 1°, 3°, and 7°; skip any violating protected edges.
- `UNSUBDIVIDE`: try 2 and 4 iterations (if classifier indicates a plausible source grid).
- `DECIMATE`: staged ratios derived from target budget, e.g. 0.8, 0.6, 0.4, with earlier termination on fidelity failure.
- `QUADRIFLOW`: test at most a few target-face values near the proposed budget (e.g. 0.75×, 1×, 1.3×).
- `VOXEL`: select sizes from measured minimum protected feature width, not one global hard-coded voxel size.

These are **initial experimental search points**, not validated best settings. Enforce a maximum candidate count and execution-time budget. Use a coarse preview first and fine validation only on promising candidates. Expensive strategies must be opt-in for large batches.

### Candidate lifecycle

```text
PLANNED -> RUNNING -> GENERATED -> QA_RUNNING -> PASS/WARN/FAIL
                                                |        |
                                           COMMITTABLE  REVIEW
```

A failed strategy must not abort the entire job if lower-risk candidates remain viable. A fatal source invariant or repeated crash must stop only that object/job, preserving originals.

---

## 11. Quality assurance and geometry comparison

### 11.1 Geometry similarity

Use `mathutils.bvhtree.BVHTree` for closest-point queries and ray-casting. Sample points proportional to **surface area**, including interior triangle samples, not vertices alone (vertex-only sampling strongly biases dense regions). Use deterministic stratified barycentric sampling on both source and candidate.

For each source sample, query nearest candidate surface; also sample candidate and query source. Report:

- Bidirectional mean and median closest-surface distance.
- **P95 distance** and maximum observed distance in each direction.
- Distances normalized by world-space bounding-box extent `D` and in Blender scene units.
- Signed/normal-direction metrics where well-defined and reliable.
- Coverage failures: missing small components, holes, or candidate protrusions.

**Limitations:** Closest point alone cannot guarantee that a cavity, thin wall, or overlapping surface is correct. Pair with feature-boundary checks and silhouette tests.

### 11.2 Silhouette tests

In a later iteration or for `HERO` assets, render source/candidate silhouette masks from a configurable set of orthographic views (default proposed: ±X, ±Y, ±Z, and selected diagonal views). Use a deterministic Blender rendering setup, common camera and framing, and compute mask intersection-over-union (IoU) plus contour mismatch.

Perspective views may be supplied for assets designed for specific gameplay cameras. An orthographic multi-view metric is a useful heuristic, **not proof of perceived equivalence** under every view, focal length, shading condition, or distance.

### 11.3 Topology and feature tests

- Degenerate face/edge count.
- Non-manifold/boundary edge differences, interpreted by asset policy.
- Connected-component count and component volume/area changes where applicable.
- Normal winding consistency and newly inverted faces.
- Triangle sliver/aspect ratio distribution.
- Sharp edge retention and positional drift.
- Hole-loop preservation and minimum feature width.
- Attribute domain/layer inventory and material assignment coverage.
- UV distortion or lost UVs when preservation is required.
- Shape keys, vertex groups, and deformation metadata explicitly intact or explicitly invalidated.
- Evaluated triangle, polygon, and vertex counts after modifiers and final triangulation.

### 11.4 Proposed initial QA presets (engineering hypotheses)

The following are **starting targets for calibration**, not established industry thresholds or universal acceptance limits:

| Gate | Hero static prop | Standard static asset | Deforming asset |
|---|---|---|---|
| Bidirectional P95 surface deviation | ≤ 0.15% of D | ≤ 0.35% of D | Project-specific; must pass deformation test |
| Silhouette IoU where available | ≥ 0.985 | ≥ 0.970 | Pose-dependent; require representative poses |
| Locked/critical opening removed | **0 allowed** | **0 allowed** | **0 allowed** |
| Protected hard edge lost | **0 allowed**, absent approved override | **0 allowed** | **0 allowed** |
| New unintentional non-manifold defects | **0 allowed** | **0 allowed** | **0 allowed** |
| Required UV/material loss | **0 allowed** | **0 allowed** | **0 allowed** |

An additional absolute error cap should be derived from smallest **protected** feature, since large `D` can hide a meaningful small detail. Maximum deviation is reported but should use robust outlier handling to distinguish sampling anomalies from true failures.

`PASS` requires all hard gates and selected quality thresholds. `WARN` means a reviewable issue without an automatic commit. `FAIL` means a violated invariant or a clearly unfit mesh. The user may explicitly waive selected non-critical gates, with waiver reason recorded in the report.

### 11.5 Geometry quality versus performance gate

The planner should not promise a target reduction if achieving it would destroy the source. Results may be:

- `PASS_TARGET_MET`: Quality passes and triangle budget is satisfied.
- `PASS_QUALITY_OVER_BUDGET`: Good topology; target is unachievable under current constraints.
- `NO_IMPROVEMENT`: Source remains the best viable candidate.
- `NEEDS_ARTIST_REVIEW`: Ambiguous form or edge flow.
- `FAIL_VALIDATION`: Structural or visual failure.

---


## 11A. Verification mathematics, coverage, and false-pass prevention

### 11A.1 Surface distance is sampled, not proven exact

The Metro paper's surface-sampling framework [R18] motivates the approach. Do not call the largest observed sample error a guaranteed mathematical Hausdorff bound; it is **sampled max**.

For surface A (source) and B (candidate), define sampled directed distances:

`d(A→B) = {min_{q on B} ||p_i - q|| : p_i sampled on surface A}`

Compute also `d(B→A)`; summarize the two distributions **separately**, then report combined `p50`, `p95`, `p99`, `max_sampled`, `mean` and `RMS`. Distances must use the same coordinate space and be stored both in physical units and as a proportion of `D`.

**Sampling method:** Triangulate a *copy* of each evaluated mesh; sample triangles proportional to world-space area using a fixed random seed; add deterministic vertex/edge/feature-corner samples; use Blender `BVHTree` closest-point queries on the opposite surface. Do not sample only at original vertices, because tessellation density will bias the comparison. [R13, R18]

**Suggested adaptive coverage strategy (engineering proposal):** Start with approximately 2,000 area samples per object or one sample per sufficiently large triangle, whichever is higher; refine near boundary loops, thin regions, marked hard features and regions where distance is elevated. Cap samples per asset and report actual count, seed and unresolved confidence. This is a **candidate default to benchmark**, not an accepted industry threshold.

### 11A.2 Silhouette tests must include purpose-driven cameras

- Sample declared production cameras first; fallback to orthographic axes and eight principal obliques when no views are provided.
- Compute foreground masks from Blender's native renderer/workbench or a tested offscreen rasterization path. Exact view/camera state must be versioned. Use normalized silhouette IoU or boundary-distance statistics.
- Sample inset shapes/doorways independently: a mesh can retain exterior outline while obliterating an internal hole.
- For animated or moving rigid objects, compare relevant pivot-driven views and authored poses.
- When GPU/offscreen context is unavailable in background mode, use a deterministic Blender-compatible CPU projection path or mark `SILHOUETTE_UNTESTED`; **do not silently skip a required gate**.

### 11A.3 Structural quality checks must respect intentional openness

**Reject where forbidden:** zero-area faces, unintentional duplicated faces, inverted winding islands, collapsed protected holes, disconnected components merged accidentally, newly self-intersecting repairs, UV borders welded against policy, and faces whose triangulation crosses a hole.

**Warn or apply intent-dependent gate:** elongated tris, n-gons, poles, open borders, normal discontinuities. On a flat wall, one well-behaved n-gon can be acceptable; a pole at a character elbow's peak deformation may be unacceptable.

**Invariant-specific unit tests:** for a mechanical cutout, compare actual loop center, shape, area, edge samples and whether a ray can pass through it. A near-zero closest-surface error can still coexist with an accidentally capped opening.

### 11A.4 UV, normals and bake verification hierarchy

1. **Layer existence:** Every required named layer still exists with matching data type/domain (or documented remap).
2. **Seam protection:** Required UV and hard-shading discontinuities still align with intended features.
3. **Texel correspondence:** Sample UV mappings near corners and seams; reject severe distortion when strict preservation applies.
4. **Shading comparison:** Render flat, smooth and material-shaded turntables to detect gradients and unwanted highlights.
5. **Normal-map continuity:** If a normal map is required, perform at least one controlled Blender bake fixture with fixed triangulation and documented cage/ray direction. Blender emphasizes margin around UV islands to avoid filtered seams. [R12]

The game-art Polycount community's production notes reinforce that UV splits and hard normals can affect final render-vertex counts and baking outcomes, but those details require validation in the intended downstream renderer; **do not present Blender's count as an exact engine vertex count**. [R11]

### 11A.5 Deformation verification protocol

For each scripted pose, evaluate armature/shape-key or test deformation on a separate candidate copy. Record:

- flipped or degenerate faces;
- relative ring-length and cross-sectional volume change;
- edge stretch ratio distribution across the bend zone;
- visual pinching/silhouette drift versus approved deforming reference;
- material/UV seam tearing;
- compliance with fixed hinge/attachment landmarks.

No single "minimum three loops per joint" universal rule is claimed. Required loop counts derive from asset shape and motion range, then are verified under pose tests. If a rig or reference poses are unavailable, the tool can mark `STATIC_SHAPE_PASS` but must not declare `DEFORMATION_READY`.

### 11A.6 Measured optimization, not misleading optimization

Measure source and candidate with identical evaluated modifier context. Report **Blender loop-triangle count** and additional face/vertex/material/UV-split statistics. Store any estimated final render-vertex count explicitly as `PROXY`, not as an actual engine metric. A mesh may drop face count yet add seams, modifiers, materials or hidden triangles. Optimize for confirmed downstream constraints, never for a vanity quad percentage. [R11, R14]

### 11A.7 Strong pass logic

```python
# Contract sketch; geometry and attribute implementations live elsewhere.

def certify(candidate_report, declared_requirements):
    for hard_gate in declared_requirements.hard_gates:
        observed = candidate_report.gates.get(hard_gate.id)
        if observed is None or observed.status in {"NOT_RUN", "UNSUPPORTED"}:
            return "NEEDS_ARTIST_REVIEW"  # never an implicit pass
        if observed.status == "FAIL":
            return "FAIL_VALIDATION"
    if declared_requirements.deformation_ready and not candidate_report.pose_test_passed:
        return "NEEDS_ARTIST_REVIEW"
    if candidate_report.meets_target_budget:
        return "PASS_TARGET_MET"
    return "PASS_QUALITY_OVER_BUDGET"
```

---

## 12. UVs, materials, normals, and other attributes

Attribute transfer is the **primary hidden risk** in auto-retopology. Topology-changing methods often invalidate face-corner indexing. The system must make this visible before execution.

### Preservation modes

1. `STRICT_PRESERVE` — only run strategies shown by tests to preserve the required data for that mesh. Abort if transfer cannot meet the exact policy.
2. `TRANSFER_AND_VALIDATE` — reconstruct/transfer supported data using source-surface correspondence and validate seam, layer, and material mapping.
3. `REBUILD_LATER` — allow new topology but flag UV/normal/bake work as unresolved; output cannot be marked fully production ready.
4. `GEOMETRY_ONLY` — explicitly permit loss of non-geometric data.

### Data requirements

- **Materials:** Preserve material identities, and reassign face material indices by closest-source-face mapping only where correspondence is unambiguous; boundaries remain protected.
- **UVs:** Face-corner data cannot safely be treated as ordinary per-vertex data. Crossing a seam requires discontinuity-aware interpolation or fresh unwrap. Reject silent seam welding.
- **Sharp edges and normals:** Re-establish intended hard/soft shading boundaries. Do not blindly copy custom normal arrays across changed topology.
- **Vertex colors and generic attributes:** Respect POINT, EDGE, FACE, and CORNER domains, interpolate only supported numeric data, and report unsupported types.
- **Vertex groups/weights:** Transfer by surface mapping only with appropriate normalization; deforming assets must still pass pose tests.
- **Shape keys:** Changing topology invalidates per-vertex shape-key correspondence. Default to protected/refuse, or require a separately approved reconstruction workflow.
- **Modifiers:** Record modifier intent; reconstruct relevant non-topology-changing modifiers on a candidate only if output comparison remains valid.

### Normal-map/baking note

A new low-poly mesh often needs a fresh UV layout and rebaking from the original high-resolution object. Blender documents selected-to-active baking, cage/ray controls and UV island margins; this makes the bake a real workflow dependency, not a cosmetic afterthought [R12]. This TDD may offer **Blender-only handoff setup** (high/low objects, cage hints, named material slots), but robust bake authoring is a separate subsystem, not an implicit feature of remeshing.

---

## 13. UI and artist review workflow

Create a dedicated **3D View > Sidebar > Retopology** panel and an optional Object Properties panel. UI should make the plan understandable before committing.

### Main sections

**1. Source** — Selected objects/collection, active geometry snapshot, read-only source stats, detected hazards.

**2. Intent** — Rigid/deforming, hero/background, target triangle count, preservation policy, hard-feature locks, optional symmetry.

**3. Analyze** — Button creates profile, shows classification and confidence. List top risks such as `OPEN_SHELL`, `BOOLEAN_SLIVERS`, or `UV_SEAMS_AT_RISK`.

**4. Plan** — Ranked strategy candidates with **why**, expected impact, risk, required approvals, and supported operations.

**5. Preview** — Before/after toggle, side-by-side or viewport overlay, source surface in a muted reference material, wireframe candidate, protected-edge visualization, distance heatmap, and silhouette QA overlay where available.

**6. Validate & Commit** — Actual counts, fidelity gates, warnings, optional reasoned waiver, commit button, rollback button.

**7. Batch Queue** — Job states, per-object method, pass/fail summary, retry with safer strategy.

### Essential user interactions

- `Analyze Selected`
- `Generate Plan`
- `Preview Recommended`
- `Try Alternative`
- `Lock Marked Edges` / `Lock Region`
- `Accept Plan Override`
- `Commit Passing Candidate`
- `Restore Original` / `Delete Previews`
- `Export JSON Report`

A one-button convenience command may **chain Analyze → Plan → Preview**, but must never silently commit a failing candidate.

---

## 14. Data contracts and machine-readable plans

Plan schemas should be stable JSON, not Blender operator logs pasted as text. Store full geometry externally/in `.blend` objects; JSON stores metadata, references, parameters, and reports.

### Example `RetopologyPlan` (illustrative)

```json
{
  "schema_version": "1.0",
  "plan_id": "retopo_wallpanel_001",
  "source": {
    "object_name": "WallPanel_HI",
    "fingerprint": "sha256:<generated-at-runtime>",
    "evaluated_geometry": true,
    "blender_version": "<from-bpy-app-version>"
  },
  "intent": {
    "asset_role": "STATIC_PROP",
    "visual_priority": "STANDARD",
    "topology_style": "EDITABLE_RIGID",
    "target_tris": 1200,
    "max_tris": 1500,
    "geometry_policy": "PRESERVE_OPEN",
    "attribute_policy": "STRICT_PRESERVE"
  },
  "constraints": {
    "max_p95_surface_error_fraction_of_D": 0.0035,
    "minimum_silhouette_iou": 0.97,
    "protect_material_borders": true,
    "protect_uv_seams": true,
    "protect_sharp_edges": true,
    "protect_boundaries": true,
    "allow_voxel": false
  },
  "analysis": {
    "primary_class": "PLANAR_HARD_SURFACE",
    "confidence": 0.91,
    "warnings": ["BOOLEAN_SLIVERS"],
    "protected_regions": ["rim_opening", "mount_holes"]
  },
  "candidates": [
    {
      "strategy": "PLANAR_PROTECTED_DISSOLVE",
      "parameters": {"angle_degrees": 3.0},
      "required_checks": ["surface", "boundaries", "materials", "uvs"]
    },
    {
      "strategy": "CONSERVATIVE_CLEANUP",
      "parameters": {"merge_distance_fraction_of_D": 0.00001},
      "required_checks": ["all_hard_gates"]
    }
  ],
  "selection_rule": "BEST_PASSING_CANDIDATE",
  "seed": 1337,
  "commit_requires": "PASS"
}
```

Numbers are intentionally examples. The implementation should not hardcode the sample asset's dimensions or target into global defaults.

### Example validation result

```json
{
  "plan_id": "retopo_wallpanel_001",
  "candidate_id": "c02",
  "status": "PASS_TARGET_MET",
  "strategy": "PLANAR_PROTECTED_DISSOLVE",
  "before": {"vertices": 4230, "polygons": 4100, "triangles": 8100},
  "after": {"vertices": 1010, "polygons": 720, "triangles": 1380},
  "qa": {
    "surface_distance_p95_fraction_of_D": 0.0011,
    "silhouette_iou": 0.986,
    "lost_protected_boundaries": 0,
    "new_unintentional_nonmanifold_edges": 0,
    "required_attributes_preserved": true
  },
  "cautions": ["TRIANGULATION_INSPECTED"],
  "source_modified": false
}
```

The example numbers show schema shape, **not measured test results**.

---

## 15. Execution controller: reference pseudocode

```python
# Pseudocode, not a drop-in Blender addon.

def process_object(source, settings):
    snapshot = create_owned_geometry_snapshot(source)
    profile = analyze_geometry(snapshot, settings)
    plan = generate_plan(profile, settings)

    if plan.requires_manual_classification:
        return review_result(plan, "AMBIGUOUS_GEOMETRY")

    candidates = []
    for proposed in plan.ranked_candidates[:settings.max_candidates]:
        if not capabilities_available(proposed, blender_version()):
            record_skip(proposed, "BLENDER_API_UNAVAILABLE")
            continue

        candidate = duplicate_snapshot(snapshot)
        try:
            execute_strategy(candidate, proposed)
            result = validate_both_directions(
                source_snapshot=snapshot,
                candidate=candidate,
                profile=profile,
                constraints=plan.constraints,
            )
        except RecoverableStrategyError as error:
            discard_candidate(candidate)
            record_strategy_error(proposed, error)
            continue

        candidates.append((candidate, result))
        if should_stop_early(candidates, plan):
            break

    selected = select_best_passing_candidate(candidates, plan)
    if selected is None:
        return review_result(plan, "NO_PASSING_CANDIDATE")

    publish_preview(selected)
    if settings.auto_commit and selected.result.status == "PASS_TARGET_MET":
        commit_immutable_result(selected, provenance=plan)
    return selected.result
```

### Blender API mapping

| Need | Blender-native API |
|---|---|
| Mesh editing | `bmesh`, `bmesh.ops` |
| Protected planar dissolve | `bmesh.ops.dissolve_limit` with boundary delimiters |
| Cleanup | `bmesh.ops.dissolve_degenerate`, guarded merge/dissolve |
| Grid reduction | `bmesh.ops.unsubdivide` or Decimate `UNSUBDIV` |
| Controlled reduction | `DecimateModifier` (`COLLAPSE`, `DISSOLVE`, `UNSUBDIV`) |
| Quad remeshing | `bpy.ops.object.quadriflow_remesh` |
| Volumetric remeshing | `bpy.ops.object.voxel_remesh` / native Remesh modifier |
| Surface matching | `mathutils.bvhtree.BVHTree`, `ShrinkwrapModifier` |
| Triangle counts | `Mesh.calc_loop_triangles` and `Mesh.loop_triangles` |
| Candidate snapshot | Evaluated object mesh + owned mesh data-block |
| Interactive manual edits | Blender Poly Build, snapping, bridge/grid fill |

**Blender version policy:** Provide capability checks instead of assuming every operator argument is stable across major versions. Check `bpy.app.version`, operator poll/context, supported RNA property names, and declared attribute behavior. Automated CI must actually run supported Blender builds.

---

## 16. Headless/batch execution and safety

### Command-line behavior

A batch runner launches through Blender itself, for example:

```bash
blender --background asset_working.blend --python run_retopology_batch.py -- --config retopo_batch.json
```

The `run_retopology_batch.py` runner parses arguments following `--`, loads the add-on, locates referenced objects/collections, executes permitted candidates, and emits JSON reports. It must never depend on interactive screen regions unless the strategy is explicitly UI-only.

### Reliability requirements

- Never mutate original geometry automatically.
- Operations are transactional at the **candidate** level: clone → modify → validate → commit or discard.
- Operator context for native Blender operators must be set intentionally (active object, selection, object mode, supported window context). Prefer direct data/BMesh APIs when possible.
- No unguarded asynchronous manipulation of Blender datablocks. Geometry operations generally run on Blender's main thread; expensive background/headless work should run as a separate Blender process, not a thread modifying `bpy` data.
- Report cancellation, timeout, unsupported geometry, out-of-memory, and API failure distinctly.
- Save checkpoints only with explicit destination and policy; do not overwrite the source `.blend` by default.
- Running twice against the same frozen source/settings should select the same strategy and produce comparable output within declared numeric tolerances. Report seeds and Blender version.
- Record peak memory and duration, if measurable, for search-budget tuning.

---

## 17. Engineering milestones and scope

### Phase 0 — Baseline instrumentation

**Deliver:** Reliable source snapshotting, profile extraction, evaluated triangle counts, connected-component analysis, protected edge detection, and source/preview collections.

**Exit test:** Handles real mesh assets without modifying originals, including mirrored transforms, linked meshes, open shells, and modifier stacks.

### Phase 1 — Useful MVP: rigid asset retopology

**Deliver:** Deterministic planner; S0 no-op, S1 cleanup, S2 protected planar dissolve, S3 Un-Subdivide, S4 controlled decimation; distance QA; object-level plan/report; preview/commit/rollback.

**Why this first:** Many environment and prop assets suffer from boolean debris, excessive planar edges, and wasteful subdivision. These cases can be improved without pretending automatic character topology is solved.

**Exit test:** At least one passing candidate or a truthful no-op/review result on the rigid fixture suite; no critical feature loss on passing outputs.

### Phase 2 — Organic mesh support

**Deliver:** S5 QuadriFlow, guarded S6 voxel preprocessing, optional projection, richer material/attribute mapping, guided-mode entry point, silhouette QA.

**Exit test:** Known organic fixtures meet calibrated fidelity gates without hole loss or unauthorized attribute loss.

### Phase 3 — Guided production retopology

**Deliver:** Interactive protected-edge painting, priority heatmaps, manual loop guides, usable Blender Poly Build workflow, deformation-ready review gates, pose fixture checks.

**Exit test:** Tool flags and assists cases that need artist topology instead of falsely certifying them.

### Phase 4 — Region-specific advanced solver

**Deliver:** Single-shell patch partitioning, planar patch reconstruction, boundary-constrained resampling, stitch validation, performance tuning, and stable parallel batch process isolation.

**Exit test:** Mixed hard-surface assets can be region-processed with measured seam integrity. Feature gated until demonstrably reliable.

---

## 18. Validation fixture catalog

Build Blender `.blend` test fixtures using **only Blender geometry**. Every fixture should include a source object, declared intent, protected features, an acceptance manifest, and expected decision category.

| Fixture ID | Geometry | Expected behavior |
|---|---|---|
| T01 | High-density flat wall with window cutout | Remove planar redundancy; retain opening |
| T02 | Boolean-heavy vending-machine body with bevels | Preserve front silhouette, control panel borders, bevels |
| T03 | 4× subdivided cube with regular quad grid | Recognize Un-Subdivide eligibility |
| T04 | Dense smooth sculpted rock | Quad/decimation trials; hold silhouette |
| T05 | Open single-sided poster/leaf card | Never fill into volume automatically |
| T06 | Chain-link fence with many holes | Voxel strategy prohibited by default |
| T07 | Thin cable crossing a thicker body | Preserve cable or isolate component |
| T08 | Mirrored negative-scale pair | Consistent normals, world-space comparison |
| T09 | Shared mesh datablock on several objects | No source/instance mutation |
| T10 | Mixed materials and UV seams | Protect and verify attribute borders |
| T11 | Dense character elbow or flexible strap | Mark guided/deformation pathway |
| T12 | Intentional disconnected object shells | Do not forcibly weld components |
| T13 | Broken scan with non-manifold noise | Repair only with explicit permission |
| T14 | Efficient hand-modeled low-poly object | No-op must be permitted |
| T15 | Small mechanical hole on a large object | Do not lose small feature due to D-normalized tolerance |
| T16 | Concave large n-gon after dissolve | Reject/repair unsafe triangulation |
| T17 | Shape keys and nontrivial vertex weights | Refuse incompatible topology change by default |
| T18 | Batch of 100 heterogeneous props | Independent jobs, deterministic report summaries |

### Automated assertions

1. Original geometry fingerprints unchanged in all outcomes.
2. Every candidate result includes before/after **evaluated triangle** counts.
3. A candidate with a deleted locked opening never passes.
4. A candidate with lost required UVs never passes under strict preservation.
5. A mesh with no safe reduction can return `NO_IMPROVEMENT` rather than an arbitrary failure.
6. BMesh cleanup does not create unintentional component merges.
7. Candidate rankings are deterministic with fixed input, seed, and Blender build.
8. Headless and GUI analysis produce equivalent plans, excluding UI-only options.
9. Batch failures do not corrupt later assets.
10. Repeated candidate retries never modify source data.

### Quality benchmark methodology

Create a gold-standard set of artist-reviewed meshes and run **blind A/B reviews** for silhouettes, corner readability, shading, and editability. Track:

- % of candidates meeting required gates.
- Median triangle savings among passing rigid assets.
- False-pass rate (tool passes a visibly or structurally broken mesh).
- False-reject rate (tool rejects acceptable output).
- Artist repair minutes saved or added per asset.
- Runtime and memory by source triangle-count bin.

Initial rollout should prioritize **zero false passes on protected geometry** over maximum automated completion.

---


### 18.1 Additional regression fixtures derived from production practice

Extend the original T01–T18 suite with the following acceptance fixtures:

| ID | Production question | Mandatory observed result | Relevant source |
|---|---|---|---|
| T19 | Flat facade with **two** nested windows and inset signage | Both internal openings survive and remain separate from material border | [R3, R4] |
| T20 | Cylinder with open bore and a bolted side flange | Bore preserved; circumferential silhouette within view-dependent budget | [R3, R13] |
| T21 | Adjacent touching cables and a wall | No snap-bridging or component weld | [R5, R15] |
| T22 | Character elbow with dense auto quads | Static QA alone cannot earn deformation-ready status | [R1, R6] |
| T23 | Joint cage with approved flexion 0°, 45°, 100° | Pose test detects any new pinching / inversion | [R7] |
| T24 | UV seam across a corner with normal-map bake | Domain-aware UV transfer and fixed bake path; zero missing required seam | [R9, R11, R12] |
| T25 | Planar object with concave n-gon caused by dissolve | Stable triangulation; no triangle crossing outline | [R2, R3] |
| T26 | 95% quads but irregular organically retopologized | Reject false Un-Subdivide classification | [R4] |
| T27 | High-poly organic with fine sculpt pores | Plan marks high-frequency detail for potential bake; does not duplicate with needless triangles | [R6, R12] |
| T28 | Open fence with dense perforations | Automatically forbid voxel; holes retained | [R5] |
| T29 | Two identical sources with fixed QuadriFlow seed on pinned Blender build | Repeated behavior compared and recorded, not presumed bit-identical | [R5, R14] |
| T30 | Face-corner UV test: shared 3D vertex, different corner UVs | No averaged UV welding | [R9] |
| T31 | Source with baked custom normal appearance | Reject shading regression despite near-zero shape deviation | [R9, R11] |
| T32 | Extremely narrow trim attached to large facade | Absolute feature-width constraint overrides D-scaled threshold | [R18] |
| T33 | Large positive geometry change, sampled error low | Boundary/hole tests catch missing inward cavity | [R18] |
| T34 | Background mesh already optimal | Returns NO_OP without inventing savings | [R4] |

**Gold standard setup:** For every fixture save (`.blend`) source, one or more approved candidate models, feature annotations, key views, expected classification and reason codes. Re-run with a pinned Blender version as CI. Record cases where the tool refuses to modify: *false-pass rate is more dangerous than not automating an asset.*

### 18.2 Quantitative and qualitative benchmark protocol

Use a **paired baseline**: (A) plain Blender Decimate / QuadriFlow with similar target count, (B) TopoSmith's planned workflow. Judge only passing results, not all produced meshes. Independently compare render-turntable similarity, preserved feature count, triangle reduction, surface error, baking correctness, deformation validity (if relevant), total artist cleanup time and number of preview attempts.

**Suggested release targets (project hypotheses, to be tuned against fixtures):** 100% preservation of explicitly locked holes on the held-out hard-surface suite; 0 false `DEFORMATION_READY` classifications for automatic QuadriFlow; 0 unreported missing required UV layers; no source-datablock mutations; at least one case where conservative cleanup beats blind auto-remesh in artist evaluation. Never call these universal industry thresholds.

## 19. Known technical risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Entire mesh sent to QuadriFlow | Excessive density, lost details, poor corners | Classifier-first routing; compare against cleanup/planar candidates |
| Planar dissolve creates a complex n-gon | Bad triangulation or shading | Explicit evaluated triangle/triangulation QA and region rejection |
| Decimation appears to reduce Blender polygons but not GPU cost | Misleading results | Report evaluated triangles, UV/material splits, object/draw-call proxies separately |
| Voxel remesh closes openings or loses thin features | Silhouette/function failure | Strict repair opt-in; thin/open detection; hole-loop checks |
| UV seams/materials disappear | Texture breakage | Protected boundaries and mandatory data-layer validation |
| Closest-surface distance masks a missing cavity | False-positive quality pass | Boundary topology, silhouettes, and feature-specific tests |
| Symmetry assumption erases asymmetry | Visual damage | Require confidence and approval; compare both sides |
| Shape keys/rigging break | Broken animation | Refuse topology changes by default; future reviewed transfer/deformation pipeline |
| Complex patch stitching | Non-manifold seams/T-junctions | Defer until robust stitch proof; component-first routing |
| Version-specific operator signatures | Broken automation | Versioned adapters, reflection/capability checks, Blender CI matrix |
| Huge evaluated meshes exhaust memory | Failed batch | Vertex/triangle caps, chunked analysis where safe, per-process limits |
| Aggressive optimization erases intentionally small detail | Lost design | Protected feature width and absolute tolerance in addition to D |

---

## 20. Acceptance criteria / definition of done

A v1 release is acceptable when:

- [ ] It runs entirely inside a supported Blender installation using shipped Python and Blender-native geometry capabilities.
- [ ] It accepts existing mesh objects/collections and produces an inspectable plan **before** executing anything destructive.
- [ ] It distinguishes cleanup, planar reconstruction, unsubdivision, decimation, quad remesh, and guided retopo even if later methods remain gated.
- [ ] It never changes the source mesh or source `.blend` without an explicit user action.
- [ ] Every strategy works on copies; failed candidates can be discarded safely.
- [ ] It measures evaluated triangles, component connectivity, defects, and protected features.
- [ ] It validates source-to-candidate **and candidate-to-source** geometric deviation.
- [ ] It cannot pass a mesh that violates a mandatory edge/opening/material/UV constraint.
- [ ] It can say **No improvement**, **Over budget**, or **Manual review needed** without fabricating success.
- [ ] It supports Blender GUI preview and deterministic headless batch execution for supported strategies.
- [ ] It emits the strategy, reason, parameters, Blender version, source hash, QA values, and provenance in JSON.
- [ ] Its critical fixture tests pass across explicitly supported Blender versions.

### Recommended first demonstration

Take three Blender models: **(1)** a boolean-heavy vending machine, **(2)** a heavily subdivided interior wall with door opening, and **(3)** a sculpted trash bag.

The tool should: classify all three differently; preview an appropriate candidate for each; visibly show protected edges and QA results; leave source meshes untouched; and generate an honest machine-readable summary for accepted/rejected outcomes. Demonstrate that a simple global Decimate/QuadriFlow button does **not** give the same quality across the set.

---

> **v3.0 runtime release gate:** Geometry QA alone proves mesh correctness, not Godot speed. If `runtime_target="GODOT_4_7"` is selected, the tool must additionally emit the runtime handoff and a `PERFORMANCE_UNVERIFIED` status until a Godot benchmark validates it. New requirements and evidence appear in §§25–38.

## 21. API quick links (see annotated sources in §23)

These are implementation starting points. Blender behavior and operator signatures must be tested on the exact release selected by engineering.

1. **BMesh operators** — dissolution, degenerate cleanup, unsubdivision, triangulation, bridge/grid fill:  
   https://docs.blender.org/api/current/bmesh.ops.html
2. **Blender Python object operators** — native QuadriFlow and Voxel Remesh signatures:  
   https://docs.blender.org/api/current/bpy.ops.object.html
3. **Decimate modifier** — Collapse, Un-Subdivide, and Planar methods and tradeoffs:  
   https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/decimate.html
4. **Remesh modifier** — reconstruction approaches and voxel caveats:  
   https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/remesh.html
5. **Blender retopology guidance** — limits of automatic quad remeshing, particularly for deformation:  
   https://docs.blender.org/manual/en/5.1/modeling/meshes/retopology.html
6. **Poly Build tool** — artist-guided edge and face construction:  
   https://docs.blender.org/manual/en/5.2/modeling/meshes/tools/poly_build.html
7. **BVHTree API** — nearest-point/raycast surface comparison:  
   https://docs.blender.org/api/current/mathutils.bvhtree.html
8. **Mesh API** — evaluated triangulation, remesh settings, mesh attributes:  
   https://docs.blender.org/api/current/bpy.types.Mesh.html
9. **Object API** — evaluated `to_mesh()` ownership and cleanup:  
   https://docs.blender.org/api/current/bpy.types.Object.html
10. **Shrinkwrap Modifier API** — projection constraints and surface mapping:  
    https://docs.blender.org/api/current/bpy.types.ShrinkwrapModifier.html

---

## 22. Core engineering direction (expanded by §§23–24)

**Build the planner and validator first.** Native Blender already supplies several geometry operators. The engineering challenge is deciding when each is appropriate, preserving what matters, and preventing plausible-looking but invalid output from passing.

For the first usable version, focus on rigid hard-surface props and environment geometry: protected planar cleanup, grid recovery, controlled decimation, measured source fidelity, and trustworthy reports. Add native QuadriFlow and tightly gated voxel preprocessing next. Treat production-quality deformation loops, arbitrary single-shell region stitching, and reliable cross-topology UV preservation as subsequent, demonstrably harder work.

A successful tool should make an existing Blender mesh **simpler, safer, and more deliberate**—or tell the artist exactly why it cannot do so automatically.

---


## 23. Annotated reference library and implementation evidence map

**Read this before implementation.** Links below are concrete sources found and reviewed for this revision. Blender docs are **tool/API behavior**; Blender Studio is **production-art guidance**; research papers are **algorithmic foundations**; Polycount is **experienced practitioner discussion**, not a formal platform guarantee. Content behind a Blender Studio subscription may require access; publicly visible summaries still provide the specifically attributed high-level guidance.

### Official Blender behavior

**[R1] Blender Manual — Retopology / Remeshing**  
https://docs.blender.org/manual/en/5.1/modeling/meshes/retopology.html  
*Use:* Distinguishes automatic remeshing from manual deformation-ready retopology; describes Retopology overlay, Poly Build and snapping. **Design consequence:** manual/guided approval gate for deforming topology.

**[R2] Blender Python API — BMesh Operators**  
https://docs.blender.org/api/current/bmesh.ops.html  
*Use:* `dissolve_limit`, `dissolve_degenerate`, dissolve edges/faces and triangulation operations. **Design consequence:** guarded per-region edits, version-checked operator arguments and triangulation QA.

**[R3] Blender Manual — Mesh Clean Up / Limited Dissolve**  
https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html  
*Use:* Merge by Distance, degenerate cleanup, hole filling and planar limited dissolve. **Design consequence:** cleanup != deliberate remesh; do not apply fill holes to intentionally open assets.

**[R4] Blender Manual — Decimate Modifier**  
https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/decimate.html  
*Use:* Different Collapse, Un-Subdivide and Planar modes; Planar delimit options for UV/material/sharp boundaries. **Design consequence:** distinct strategies and preservation-first guardrails.

**[R5] Blender Manual — Remeshing / Remesh Modifier**  
https://docs.blender.org/manual/en/4.5/modeling/meshes/retopology.html  
https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/remesh.html  
*Use:* Auto-quad and voxel remeshing behavior and limitations. **Design consequence:** avoid global auto remesh on open thin surfaces; label the output accurately.

**[R8] Blender Manual — Poly Build**  
https://docs.blender.org/manual/en/4.5/modeling/meshes/tools/poly_build.html  
*Use:* Native retopology construction and editing. **Design consequence:** guided authoring stays Blender-only.

**[R9] Blender Manual — Data Transfer Modifier**  
https://docs.blender.org/manual/en/4.5/modeling/modifiers/modify/data_transfer.html  
*Use:* Source correspondence and mappings for vertex, edge, face and corner data. **Design consequence:** domain-specific transfer and seam QA; layer existence is not sufficient.

**[R10] Blender Manual — UV Operators / Seams and face shading**  
https://docs.blender.org/manual/en/4.5/modeling/meshes/editing/uv.html  
https://docs.blender.org/manual/en/5.0/modeling/modifiers/normals/smooth_by_angle.html  
*Use:* UV seam/unwrap tradeoffs, sharpness versus smooth shading. **Design consequence:** separate geometric feature protection from shading preservation.

**[R12] Blender Manual — Cycles Render Baking**  
https://docs.blender.org/manual/en/4.5/render/cycles/baking.html  
*Use:* Selected-to-active baking; cage/ray distance; UV padding/margins; tangent-space normal maps. **Design consequence:** topology changes may require an explicit, testable bake stage.

**[R13] Blender Python API — BVHTree**  
https://docs.blender.org/api/current/mathutils.bvhtree.html  
*Use:* Surface nearest-point and ray queries. **Design consequence:** bidirectional sampled distance plus feature-specific checks, not vertex-only comparisons.

**[R14] Blender Python API — Object operators, BMesh and Mesh**  
https://docs.blender.org/api/current/bpy.ops.object.html  
https://docs.blender.org/api/current/bmesh.html  
https://docs.blender.org/api/current/bpy.types.Mesh.html  
*Use:* Actual QuadriFlow operator parameters; mesh data access and evaluated triangulation. **Design consequence:** runtime capability detection, version-matrix tests, correct generated-mesh ownership.

**[R15] Blender Manual — Shrinkwrap Modifier**  
https://docs.blender.org/manual/en/4.5/modeling/modifiers/deform/shrinkwrap.html  
*Use:* Nearest surface vs projection and projection direction. **Design consequence:** projection needs component, direction and distance constraints for close parallel surfaces.

### Production practice from Blender Studio

**[R6] Blender Studio — Generic Retopology (Realistic Character Workflow)**  
https://studio.blender.org/training/realistic-human-research/retopology/  
*Use:* Recommend locking topology before downstream processes, starting from symmetry when appropriate, placing loops near clothing seams/landmarks, coordinating pivots. **Design consequence:** topology-intent plan and rig-relevance metadata are first-class requirements.

**[R7] Blender Studio — Stylized Character Workflow / Clean Retopology**  
https://studio.blender.org/training/stylized-character-workflow/  
https://studio.blender.org/training/stylized-character-workflow/chapter/5d384edea5b8f5c2c32c8507/  
*Use:* Studio training topics include loop flow, poles, facial articulation, crease management and joint loops. **Design consequence:** guided topology playbooks; do not equate statistical quad regularity with useful flow. Some detailed lesson videos are subscription content; the free course outline is the visible basis for that statement.

### Experienced game-art production discussion

**[R11] Polycount — EarthQuake, *Making sense of hard edges, UVs, normal maps and vertex counts* (2012)**  
https://polycount.com/discussion/107196/making-sense-of-hard-edges-uvs-normal-maps-and-vertex-counts/src  
*Use:* Practical interplay of hard edges, UV splits, normal-map baking and effective render vertices. **Design consequence:** strict data-layer / shading / bake verification and no false claim about final GPU vertex counts. This is knowledgeable industry community practice and context, **not** a Blender API specification or universal exporter rule.

### Geometry processing research

**[R16] Garland and Heckbert (1997), *Surface Simplification Using Quadric Error Metrics*, SIGGRAPH**  
https://publications.ri.cmu.edu/surface-simplification-using-quadric-error-metrics  
*Use:* Error-informed simplification by iterative vertex-pair contraction. **Design consequence:** optimize fidelity and shape error rather than face ratio alone. **Do not** claim identical implementation inside Blender Decimate without inspecting source.

**[R17] Huang et al. (2018), *QuadriFlow: A Scalable and Robust Method for Quadrangulation*, Computer Graphics Forum**  
https://stanford.edu/~jingweih/papers/quadriflow/  
https://doi.org/10.1111/cgf.13498  
*Use:* Field-aligned quadrangulation with fewer irregular vertices/singularities. **Design consequence:** QuadriFlow is a candidate quadrangulator—not an automatic semantic/rig-safe topology designer.

**[R18] Cignoni, Rocchini and Scopigno (1998), *Metro: Measuring Error on Simplified Surfaces*, Computer Graphics Forum**  
https://diglib.eg.org/items/e9ab8a1a-73dc-4b9f-b385-fddbca903089  
https://doi.org/10.1111/1467-8659.00236  
*Use:* Surface-sampling comparison and visualization of simplification error. **Design consequence:** bidirectional area-weighted sampling plus feature-aware checks; sampled maximum is not a proven global upper bound.

### Source integrity and revision policy

- **Verified fact**: Blender provides documented operation/behavior or a cited paper supports a general principle.
- **Best-practice inference**: Tool architecture draws a responsible recommendation from those facts (clearly labeled as design consequence).
- **Project hypothesis**: Any proposed tolerance (e.g., `0.15% of D`), face budget search, auto-classification confidence or pose count; it must be calibrated with real assets.
- Pin and record supported Blender versions. The `latest` and `current` documentation links can move and should be accompanied in CI by pinned runtime tests.
- The tool **must not require** external QuadriFlow executables, third-party retopology add-ons or non-Blender DCCs. All external links here are reference materials only; the implementation uses Blender-built-in functionality.
- Review and update this source matrix whenever upgrading Blender, changing the bake pipeline or adding a new asset family.

---

## 24. Developer handoff: what to build first, in exact order

**Sprint A — Trustworthy reading of Blender meshes:** owned evaluated snapshots; local/world transforms; shared datablock safety; topology graph; UV/material/normal/attribute inventory; component/boundary detection; deterministic JSON audit. Demonstrate T01, T05, T08, T09, T10, T30.

**Sprint B — Protection and classification:** hard-feature graph, planar segmentation, UV discontinuity detection, hole contour signatures, grid confidence, thin-shell refusal, artist marks. Demonstrate T01, T02, T15, T19, T26, T28.

**Sprint C — First real topology improvement:** conservative cleanup + protected limited dissolve + Un-Subdivide trials on copies. Triangulate candidates and run bidirectional distance, silhouette and locked contour QA. Demonstrate T01, T03, T16, T25, T34.

**Sprint D — Controlled alternatives:** Decimate Collapse vs QuadriFlow trials with explicit output labels; dependency-free preview ranks; no black-box success claims. Demonstrate T04, T14, T27, T29.

**Sprint E — Texture / deformation correctness:** Data Transfer adapter, UV/shading checks, optional Blender bake fixture, guided authoring overlays and pose-test harness. Demonstrate T11, T17, T22, T23, T24, T31.

**Release condition:** The tool must demonstrably avoid breaking features on a diverse, held-out collection of real objects; show its work in a plan and report; and distinguish a true topology reconstruction from a quick polygon reduction. A production-quality generalized single-shell stitcher is explicitly **not** a release prerequisite.


---

## 25. Godot 4.7 runtime optimization: purpose, scope and evidence

**This chapter is normative for the `GODOT_4_7` export profile.** It augments, not replaces, the retopology fundamentals and safety gates in §§1–24. Existing topology quality failures must **never** be waived to achieve apparent speed.

**Objective:** Output 3D assets from Blender that are suitable for a visually rich, stylized-realistic, navigable Godot 4.7 game level. The primary examples are repeated pieces of a late-1990s Pennsylvania city: storefront trim, brick details, light fixtures, parking stops, sidewalk slabs, fences, shelves, trash cans, railings, utility hardware, and interior dressing. The planner must also handle hero objects, destructible objects and animated assets without falsely treating everything as a MultiMesh candidate.

**What changes in v3:** A retopology result has two independent quality dimensions:

1. `GEOMETRY_QUALITY`: verified shape, surface integrity, UVs, silhouette, edge intent and visual requirements (§§4, 11, 11A).
2. `RUNTIME_SUITABILITY`: actual scene reuse, batching strategy, material surfaces, culling, LOD, lighting, collision obligations, memory proxies, and measured Godot results (this chapter).

The final release status is one of:

| State | Meaning | Release policy |
|---|---|---|
| `GEOMETRY_PASS_RUNTIME_UNTESTED` | Blender candidate passed; Godot behavior not measured | Allowed as a **candidate only** |
| `GEOMETRY_PASS_RUNTIME_PASS` | Both visual and in-engine regression gates met | Eligible for project release |
| `GEOMETRY_PASS_RUNTIME_NO_GAIN` | Correct mesh, no measurable runtime benefit | Preserve as an art candidate; don't advertise a speed win |
| `GEOMETRY_PASS_RUNTIME_REGRESSION` | Correct mesh, worse performance on target cases | Reject for optimization; compare alternate strategy |
| `NEEDS_ARTIST_REVIEW` | Quality/lighting/material outcome uncertain | No automated release |
| `INVALID_EXPORT_OR_FEATURE_LOSS` | Bad import, normals, pivots, surfaces, holes, collisions or semantics | Reject |

**Scope separation:** All source analysis, retopology and mesh-level preparation use **Blender-only** APIs. The Godot project is a *consumer and measurement harness*, not a second retopology DCC and not a required Blender add-on dependency. The JSON manifest describes how a level loader or Godot import script could use the assets. `MultiMesh` is a Godot object, not something exported as an ordinary Blender mesh.

### Evidence hierarchy

- **Confirmed 4.7 engine behavior**: official, version-pinned engine documentation `[G01]`–`[G13]`.
- **Established graphics production reasoning**: shader/material surface changes, UV seam splits, culling granularity, vertex vs fragment cost, shadow/depth passes.
- **Proposed project policy**: classification cutoffs, chunk dimensions, triangle/vertex budgets, maximum instance count per batch and acceptable measured deltas. These **must be profiled** for target hardware, cameras, renderer and content.

There is **no industry-wide 'X tris per asset' or 'Y instances per MultiMesh' guarantee.** [G01][G02][G03][G04]

## 26. Fundamentals: what really costs time in Godot

The asset planner must assess at least six distinct kinds of cost, not optimize one proxy indiscriminately.

| Cost center | Source in the asset/scene | What Blender can analyze/control | What requires Godot proof |
|---|---|---|---|
| **Submission / CPU** | Many draw submissions, nodes, object transforms, material state | Mesh reuse candidates; surface/material count; batch recipe | Render draw calls, main/render thread time, scene-tree counts |
| **Geometry / vertex** | Submitted indices/vertices, hard-normal and UV seam duplication, multiple passes | Triangulated mesh; unique corner attributes; normals/UV splitting proxy | Rendered primitives, vertex-bound behavior under target passes |
| **Pixels / overdraw** | Alpha cards, foliage, glass, large overlapping quads | Alpha surface classification, projected area estimates, card density | GPU time and angle-dependent cost |
| **Lighting / shadows** | Many shadow-casting meshes/lights, dynamic lighting or GI | Classify shadow-critical vs decorative; UV2 and lighting constraints | Shadow passes, light limits, lightmap workflow, actual shading |
| **Culling / LOD** | Huge object bounds, large MultiMesh spanning hidden areas | Spatial chunk recommendation, mesh bounding boxes, LOD profiles | Frustum/occlusion behavior, shared LOD for groups, HLOD transitions |
| **Memory / bandwidth** | Redundant vertex formats, textures, unique meshes and instance transforms | Geometry sizes, texture references, deduplication, estimated buffers | Import-compressed sizes, runtime VRAM, texture/video buffer monitor |

**Fundamental invariants:**

1. **Lower triangles ≠ fewer draw calls.** Each material/surface and pass may still require submission. Godot's `Mesh` resource separates geometry into surfaces with their own vertex/index arrays and materials. [G07]
2. **Fewer draws ≠ automatically lower frame time.** An enormous MultiMesh can submit more invisible geometry than independently culled objects. [G01][G02][G04]
3. **One MultiMesh ≠ one draw call in every situation.** Documentation describes a single-mesh instancing draw primitive, but a multi-surface mesh, material/pass variations, shadows and rendering backend affect actual frame calls. **Measure**; never encode `draw_calls = number_of_multimeshes` as fact. [G01][G07][G09]
4. **Blender polygon count is not runtime vertex count.** Triangulate evaluated geometry; account for per-face-corner UVs/normals/material boundaries; verify Godot imported arrays when available. [R09][R11][G07][G10]
5. **A hidden interior face is not guaranteed free.** It can still be submitted if its enclosing object is visible. Remove only after proving the face is permanently invisible and has no collisions, wall thickness, light occlusion, shadows, attachment or gameplay obligation.
6. **A normal map replaces shading detail, not geometry silhouettes.** Retain high-contrast silhouette elements and collision-relevant holes (§4A).
7. **Do not optimize the wrong renderer.** Forward+ has automatic instancing for identical `MeshInstance3D` mesh/material combinations, under documented material conditions; Mobile/Compatibility do not provide that same automatic mode. [G09]

### 26.1 Mandatory counters and interpretation

Collect the following from the Godot 4.7 test harness, where available:

- `Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME` — draw submissions for the rendered frame.
- `Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME` — vertices/indices **submitted across rendering passes**, not unique model vertices. Shadows and depth passes can increase the total.
- `Performance.RENDER_VIDEO_MEM_USED`, `RENDER_TEXTURE_MEM_USED`, `RENDER_BUFFER_MEM_USED` where exposed.
- `Performance.OBJECT_NODE_COUNT` and `OBJECT_RESOURCE_COUNT` — scene hierarchy/resource proxies, not automatically GPU bottlenecks.
- CPU-side frame duration and the visual profiler; GPU frame duration from a reliable target/backend profiling method. `TIME_FPS` alone is inadequate; it updates once per second.

Godot documents the monitor semantics and cautions that some are debug-only or update with delay. The benchmark must state if a metric is unavailable; **do not replace an unavailable GPU timing with a fabricated value.** [G08]

### 26.2 Better efficiency target: render budget at the camera, not just mesh at rest

For a repeated archetype `a` with `t_a` source triangles and `n_visible_batch` GPU-instanced transforms, a **planning proxy** is `t_a × n_visible_batch` triangles before passes and engine LOD. This is **not** a measured primitive count. If a 2,000-triangle bolt is repeated 1,000 times, instancing reduces draw overhead, **not** the need to process many instances of its geometry. Conversely, reducing one unique background statue from 4,000 to 3,500 triangles may have negligible runtime impact if CPU submission or fragment shading dominates.

Record `asset_triangles`, `estimated_render_vertices`, `instance_count`, `visible_at_camera`, `batch_aabb`, `mesh_surfaces`, `material_mode`, `alpha_mode`, `shadow_policy` and `lighting_policy` separately.

## 27. Runtime-intent classification before choosing topology

Add a required `RuntimeIntent` classifier **before candidate optimization**. It must use artist annotations whenever available; inference alone cannot establish gameplay semantics.

| Runtime class | Typical examples | Recommended presentation | Retopology bias | Forced exception |
|---|---|---|---|---|
| `HERO_INTERACTIVE` | Safe, cash register, vending machine, target door | Individual `MeshInstance3D` + independent interaction/collision | Fidelity, good pivots, controlled surfaces | Not wholesale MultiMesh |
| `STATIC_UNIQUE_OCCLUDER` | Unique room shell, large wall, structural facade | Individual/chunked `MeshInstance3D`; separate simple occluder | Broad planar cleanup, preserve openings | Don't batch whole building with interior contents |
| `STATIC_REPEATED_RIGID` | Parking meters, streetlights, trash cans, fence posts | Evaluate Forward+ automatic instancing **vs** local MultiMesh | Stable reusable archetype, few surfaces | Separate by sightline and light zone |
| `STATIC_REPEATED_TINY` | Nuts, trim brackets, electrical boxes, identical bulbs | MultiMesh/merged detail/texture alternative | Very low-cost source geometry | Delete subpixel detail after review |
| `STATIC_REPEATED_SURFACE` | Window-frame segments, bricks, sidewalk tiles | MultiMesh or modular fused mesh (benchmark) | Shared modular piece with canonical pivot | Decals/texture may be cheaper |
| `SHEET_ALPHA` | Leaves, weeds, posters, chain-link overlays | MultiMesh only with controlled fill-rate | Few cards, sensible cutout shapes | Many transparent overlapping cards can lose |
| `DYNAMIC_DESTRUCTIBLE` | Breakable bottles, destructible fixtures | Independent active object; optional batched dormant visuals | Distinct visual/collision representations | Preserve stable gameplay IDs, state transitions |
| `SKINNED_OR_MORPHING` | Characters, deformable cloth, facial props | Rigged renderer / custom technique | Deformation loops and weights | `MultiMesh` ignores blend shapes [G02] |
| `LIGHTMAP_UNIQUE_STATIC` | Walls, floors, primary room shells | Static `MeshInstance3D` for intended lightmapping path | UV2 suitability and reliable triangulation | Don't assume MultiMesh can substitute |
| `IMPOSTOR_OR_FAR_HLOD` | Distant building groups, hillsides | Manual visibility-range node or impostor | Large-scale silhouette; minimal surfaces | Must preserve skyline identity |

**Hard gates:** If `needs_individual_animation`, `unique_uv2_bake`, `interactive_physics`, `unique_material_state`, or `unique_light_behavior` is true, do not automatically convert to MultiMesh. Some of these may be solved later with a custom renderer/import workflow, but require an explicit tested override.

### 27.1 Planner decisions (not promises)

Return one of `KEEP_INDIVIDUAL`, `KEEP_SHARED_MESH_INSTANCES`, `MULTIMESH_SPATIALLY_CHUNKED`, `COMBINE_STATIC_MESH`, `HLOD_FAR_REPRESENTATION`, `BAKE_DETAIL_OR_DECAL`, `ARTIST_DECISION_REQUIRED`. Score the alternatives using measured baseline data and semantic hard gates.

A single repeated asset can have **different** chosen strategies at different level positions: a hero vending machine in the heist storefront may remain individual, while thirty identical background vending machines can share a cheaper mesh and local MultiMesh clusters if all material/lighting obligations match.

## 28. Detect reusable meshes and preserve instancing compatibility in Blender

Repeated assets only benefit from instancing if they actually refer to compatible base geometry and material setup. A naïve retopology pass that makes each copy a new individually modified mesh can destroy the opportunity to share one GPU mesh.

### 28.1 Archetype fingerprints

Create a **geometry identity hash** using, at minimum:

- Evaluated **local-space** position/index/triangulation (quantization only with an explicit tolerance and collision review).
- Per-face-corner UV0/UV1, normals or sharp/smooth partition, face material mapping and vertex-color requirements.
- Geometry intent flags and import material signature.
- Mesh scale conversion/orientation policy and origin/pivot contract.
- Source derivation: linked mesh datablock and modifier evaluation fingerprint.

Classify matches as:

- `EXACT_SHARE`: identical evaluated geometry and attribute contract — safe base mesh reuse candidate.
- `TRANSFORM_EQUIVALENT`: geometric transform can be moved from vertices to object transform while preserving shading, UV/material semantics and negative-scale/tangent behavior — must validate, not automatically claim exact.
- `ART_VARIANT_COMPATIBLE`: same geometry but instance data/tint can represent some appearance differences, under a **known compatible Godot material/shader**.
- `LOOKALIKE_ONLY`: same dimensions but distinct topology/UV/material; **not** safe to batch.

**Identity rule:** Normalize world transforms and preserve per-instance transforms. Retopologize the **canonical prototype once** (on a copy), then reuse that retopologized mesh for eligible instances. Keep unique decoration, damaged versions, or hero variants separate.

### 28.2 Pivot and transform policy

- Canonical pivot is authored explicitly: base center for lamps/posts, hinge for doors, bolt center for hardware, grid-aligned insertion corner for modular trim as appropriate.
- Keep dimension units in meters; assert intended scale and axis conversion on export (Godot Y-up). [G10]
- A common instancing mesh has its own local bounds. Placement transforms must not silently bake world translation into each prototype's vertices.
- Mirrors, negative determinants, non-uniform scales, UV-space variations and custom normals require import/test-specific approval; they are not free optimizations.
- Preserve stable placement IDs so scene generation, saving, interactions and destruction can refer to the same object after regeneration.

### 28.3 No unearned material merges

Do **not** blindly merge materials or atlas assets to reduce surfaces. That can trade draw cost for larger texture memory, worse streaming, UV resolution loss, extra shader work or broken baked details. Only propose merging materials that are semantically compatible and demonstrate a measurable scene win.

## 29. Spatial MultiMesh planning: the central new subsystem

Godot 4.7 draws many copies of a given mesh very efficiently, **but it culls a MultiMesh at the group level**. Godot's automatic mesh LOD also applies a **single LOD to the whole MultiMesh** based on the group AABB's closest point to the camera. Therefore, the planner must favor batches that are **visually and spatially coherent**, not globally maximal. [G01][G02][G03]

### 29.1 Required batch partition keys

The conservative default is one MultiMesh per:

`(archetype_id, effective_material_signature, render_layer, shadow_policy, lighting_policy, spatial_cluster_id, runtime_state_class)`

Additionally partition on `lod_group` or shader requirements when artist-authored manual HLOD/material changes require them. A MultiMesh resource points to one mesh; do not attempt to bundle unrelated meshes or several unique objects in one `MultiMesh.mesh` because they look similar.

### 29.2 Partition heuristics (engine-independent spatial planner)

1. Group **only** exact/approved compatible instances (see §28).
2. Start with semantic cells: **room, storefront facade, block side, street segment, courtyard, rooftop**, not an arbitrary world-wide grid.
3. Split groups separated by walls, floors, corners, meaningful occluders, significant camera-distance gradients or distinct indoor/outdoor lighting.
4. Compute the union of **transformed full per-instance mesh bounds**, not merely instance-origin points. Store group-local bounding box and bounds center.
5. For candidate chunks, simulate representative gameplay cameras and count instances in the group's AABB when only a few are independently visible; identify `CULLING_WASTE`.
6. Compare smaller vs larger chunks. Small chunks reduce unnecessary rendered instances but increase batches/draws; large chunks reduce draws but can damage culling and shared-LOD selection.
7. Split extremely elongated batches, even if all objects share a straight road, because nearest-AABB LOD selection can force unnecessarily detailed geometry onto distant instances.
8. Tag high-shadow-cost clusters (under many realtime lights) for separate benchmark and review.

**Initial exploratory cell sizes**, **not standards**: e.g. 8, 16, and 32 meter *maximum spatial spans* for exterior repeated props. For interiors, begin with room/floor compartments, not meters. Evaluate the candidate cells by **measured** total time for normal/occluded/shadow-heavy views; do not ship a hardcoded global `16m` setting as an assumed best practice.

### 29.3 Cost proxy for batch alternatives

A planning-only cost may be written as:

`proxy = A * estimated_draws + B * estimated_submitted_tris + C * culling_waste + D * lod_overdetail + E * instance_update_cost + F * memory_proxy`

`A..F` are **fitted or user-supplied priorities**, not universal coefficients. `estimated_draws` is a *surface/pass-aware heuristic*; `lod_overdetail` estimates the penalty when the nearest part of an AABB keeps far members at a higher LOD; `culling_waste` counts instances in a drawn group that would otherwise have been culled. Proxy ranking merely selects variants to test in Godot. A final runtime pass requires real results.

### 29.4 MultiMesh operational constraints

- `instance_count` sets allocation and clears/resizes buffers; set transform format, `use_colors` and `use_custom_data` **before** count. [G02]
- `visible_instance_count` changes how many of the stored ordered instances are submitted; it does **not** perform individual frustum culling. [G01][G02]
- `custom_aabb` can avoid runtime bounds recalculation, but incorrect bounds cause vanishing or wasted draws; validate after transforms change. [G02]
- `set_instance_color` tints per instance, provided the material supports vertex color use; custom per-instance data requires shader handling of `INSTANCE_CUSTOM`. [G02]
- `MultiMesh` has documented per-object light restrictions, and **blend shapes are ignored**. Separate lighting areas and protect morphing assets. [G02]
- MultiMesh is a **visual instancing feature**; physics bodies, pickup/interact logic, navigation and save-state identity are independent systems.

### 29.5 Spatial batching counterexamples (required unit tests)

| Scene | Bad batching | Expected recommendation |
|---|---|---|
| 200 curb bolts spread over 800m | One enormous MultiMesh on whole city | Reuse one prototype; many local chunks or simpler fused detail |
| 80 ceiling lights over ten rooms | One MultiMesh across all rooms | Room-wise batches or individual meshes if lighting semantics differ |
| 12 identical trash cans in one visible parking lot | 12 unique remeshes / nodes without baseline | Compare automatic Forward+ instancing vs one MultiMesh |
| 500 tree leaves with heavy alpha blending | Single batch assumed cheap | Profile overdraw; evaluate alpha-testing, reduced overlap, far LOD |
| Ten vending machines, one destructible | All ten tied to immutable gameplay states | Batch nine dormant visuals; independent interactive/destroyed one |
| Reused wall panels participating in lightmap bake | Global instancing without UV2 plan | Preserve static-bake path; reject assumption that instance batching preserves per-location baked result |

## 30. Geometry strategy modifications for runtime

### 30.1 High-priority geometry changes

**Class A — Planar hard surfaces:** Eliminate redundant coplanar cuts; simplify internal booleans where outline/hole boundaries survive; test stable triangulation. Avoid enormous complex n-gons with unpredictable import. **Don't** over-refine invisible back surfaces unless they matter for collision or lighting.

**Class B — Repeated curved details:** Curve segments should be driven by projected size and viewed silhouette. Favor a canonical mesh usable at varied rotations. For a cylindrical pole, spend rings along silhouette and at meaningful joint transitions, not hidden longitudinal topology.

**Class C — Alpha cards:** Analyze card triangle count **and** alpha fill area/overlap. A few large overlapping cards can be more expensive than extra opaque polygons; candidate comparisons must include alpha/shadow scenarios. [G09][G12]

**Class D — Hero props:** Preserve close-view readability, manipulable doors/drawers, material identity and bake-worthy shading. Their cost often comes from surfaces/shading rather than triangles; cap UV/material churn and prefer meaningful detail.

**Class E — Small environment repeats:** Aggressively test replacing micro-geometry with texture/normal/decals **only** when silhouette and lighting conditions permit. A single high-detail small prop multiplied a thousand times is a legitimate high-value retopology target.

### 30.2 The vertex duplication estimator

A rough `render_vertex_proxy` groups triangle *corners*, not just mesh vertices, by the attributes that force independent GPU vertices:

`(position/index, normal, uv0, uv1, color, tangent/handedness, required custom attributes, material surface)`.

Use **evaluated, triangulated** meshes. UVs/normals can differ at adjoining face corners; a single position vertex may become more than one runtime vertex. The proxy is best viewed as a **lower/upper estimate** until actual exported/interpreted vertex arrays are inspected. Do not output a single exact Godot vertex count based only on `len(mesh.vertices)`. [R09][R11][G07]

New Blender analysis outputs:

```text
triangles_by_material
triangle_count_evaluated
mesh_material_surface_count
corner_attribute_split_proxy
uv0_island_count / uv1_island_count (if available)
sharp_edge_count / material_border_count
alpha_blend_face_area_proxy
source_geometry_fingerprint
reuse_group_id / archetype_id
estimated_gpu_vertex_bytes (flagged estimate)
```

### 30.3 Keep physics and navigation separate from render topology

Rendering optimization cannot justify holes that break cover, collision surfaces or interaction. Keep or produce separate **simplified physics proxies** as a *future optional Blender stage*; do not assume a retopologized render mesh is a good collision mesh. A MultiMesh node does not automatically yield independent collision shapes for every instance. If the level loader needs colliders, the manifest must describe **which repeated positions** need them and what simplified shapes/physics policies are required. Do not instantiate thousands of collision nodes blindly; benchmark physics and navigation separately.

## 31. LOD and HLOD: use Godot's existing capabilities

Godot 4.7 automatically generates mesh LODs for imported 3D scenes using `meshoptimizer` (normally enabled for glTF and `.blend` imports), and can use them with `MeshInstance3D` and `MultiMeshInstance3D`. It supports explicit visibility ranges to implement artist-authored HLOD or switch a group of houses to one far representation. [G03][G05]

### 31.1 Three distinct concepts

- `LO0_SOURCE_OPTIMIZATION`: This Blender tool prepares a good source mesh. Godot can then generate its own lower-detail versions on scene import. **Not** the same thing as manually authoring LOD0/1/2 for runtime selection.
- `AUTO_MESH_LOD`: Godot import-time meshoptimizer simplification with screen-space selection. Confirm import option and results for each asset; Godot warns about artifacts in some assets. [G03][G11]
- `MANUAL_HLOD`: Artist-controlled distant proxy (one block facade for twenty buildings, small silhouette shell, impostor). Godot Visibility Range settings apply per `GeometryInstance3D` node. [G05]

### 31.2 Recommended policy

1. **Default**: optimize source mesh in Blender, export glTF, allow Godot's automatic mesh LOD generation and compare to disabled-LOD control.
2. **Manual HLOD**: for complex city blocks or repetitive facades whose combined far shape is materially cheaper than many individually drawn objects. Author a separate distant proxy **in Blender**, define Godot visibility-range handoff metadata.
3. **MultiMesh**: prevent a single group from spanning many depth ranges. All instances within a group share one selected LOD, so local chunking is essential. [G03]
4. **Hero/skinned/high-sharpness assets**: check LOD artifacts and selectively disable auto LOD where it breaks shading/deformation. [G03]
5. **Never author a second decimation chain solely because it sounds faster.** Manual LOD meshes add memory and maintenance; test when engine-generated ones demonstrably fall short.
6. Use screen-space coverage at multiple FOVs and at least two representative viewport resolutions; do not base transitions only on meters.

### 31.3 HLOD example for a street

| Distance role | Near player | Middle | Distant skyline |
|---|---|---|---|
| Building | Separate doorway, windows, roof and modular props | Shell with reduced details and some shared repeating materials | One grouped facade silhouette / baked far representation |
| Street furniture | Individual/interactable or local MultiMesh | Local MultiMesh chunks with engine LOD | HLOD aggregate or omit below silhouette threshold |
| Windows | Frames and local glass | Reduced frame profile | Wall texture + dark glass color blocks |
| Interior clutter | Separate accessible items | Cull by walls/rooms | Not rendered from exterior if invisible |

HLOD quality rule: avoid turning the skyline into a featureless wall, and do not bake signs/storefront landmarks away when they are a key recognition cue.

## 32. Materials, alpha, backfaces, lighting, occlusion and shadowing

### 32.1 Materials & surface economy

Godot keeps mesh data split into surfaces, each carrying arrays and material. The planner should report both `unique_material_resources` and **number of mesh material surfaces**. Related but distinct materials may be merged with a documented shader/atlas arrangement only after comparing UV costs, draw submissions, texture memory and visual quality. [G07]

- Prefer a small, reusable set of compatible opaque materials for repeated urban modules.
- Avoid creating a separate shader/material resource for every procedurally varied copy if per-instance tint/custom data can deliver the design. Confirm the material is compatible with Godot's documented per-instance features. [G02]
- Keep glass, emissive signs and alpha surface requirements separate where their pass/blend behavior differs. [G09]
- Optimize scene composition and card overlap before assuming alpha-heavy plants are cheap merely because they have few triangles. [G09][G12]

### 32.2 Backface culling and normals

Godot specifically documents that Blender's default material setting can export backface culling disabled, causing Godot to render backfaces; for ordinary single-sided solid meshes, enable Backface Culling on the Blender material before glTF export. Deliberate two-sided foliage/posters remain exceptions and must be labeled. [G10]

- No positive-width wall should disappear due to reversed winding or culled fronts.
- Validate projected shading and tangent-space normals **after** Godot import.
- For robust n-gon geometry, export a reproducible triangulated copy (e.g. non-destructive Triangulate modifier applied in export), keeping the source editable. Godot recommends triangulating before export for predictable results. [G13]

### 32.3 LightmapGI is not a free MultiMesh compatibility claim

Godot LightmapGI requires appropriate UV2 and baked static mesh setup. For reusable meshes, Godot documents scale-sensitive UV2 packing; unique baked placement may need unique lighting representation. The planner must preserve this obligation and avoid assuming one instanced UV2 layout produces correct baked lighting for all locations. [G06]

Use `lighting_policy` values: `STATIC_BAKED_UNIQUE`, `STATIC_REALTIME_LIT`, `DYNAMIC_LIT`, `UNLIT_DECOR`, `LIGHTMAP_REVIEW`. Default gameplay-important interior shells to individual static meshes until the actual project's bake/import path is tested. Evaluate local MultiMesh batches for repetitive decoration **only where their lighting mode is verified**.

### 32.4 Occluders and culling

Godot's occlusion bake currently considers `MeshInstance3D` geometry, **not** `MultiMeshInstance3D` as an input to occluder baking. MultiMeshes can still be **occludees**; if a batched structure must be an occluder, generate separate simple occluder representation/geometry. [G04]

Example: Instanced brick details on a building should not be tasked with occluding the interior. Keep the large wall/shell or a simplified `OccluderInstance3D` to block visibility; the tiny bricks are detail, not occlusion structure.

### 32.5 Shadow policy

Group repeated assets by whether they cast dynamic shadows and whether their shadows are meaningful to presentation. Separate `CAST_SHADOWS_REQUIRED`, `OPTIONAL`, and `NONE_APPROVED`. Never auto-disable hero, cover-critical, or strong mood-defining shadows as a mere triangle optimization. Test full frame time with shadows enabled and disabled to identify whether shadow rendering dominates.

## 33. Blender → Godot 4.7 handoff contract

The v2 TDD's strict Blender-only *retopology* constraint remains. v3 extends **output** to engine-consumable geometry and metadata; it does **not** require a Blender add-on to manipulate the Godot scene tree.

### 33.1 Export artifact layout

```text
exported_asset_pack/
  meshes/
    street_trashcan_A.glb
    sign_bracket_A.glb
    curb_post_A.glb
    vending_machine_hero.glb
    facade_block_far.glb
  manifests/
    retopology_quality.json
    archetype_registry.json
    multimesh_placement_plan.json
    import_policies.json
    runtime_benchmark_requirements.json
  reports/
    source_to_output_diff.json
    godot_import_smoke_test.json       # filled by downstream harness
    performance_ab_comparison.json      # filled by downstream harness
```

**Format:** Godot 4.7 documents glTF 2.0 `.glb`/`.gltf` as recommended, and `.blend` import as a Blender-to-glTF conversion behind the scenes. For deterministic handoff, prefer explicit exported `.glb` alongside original `.blend`, with textures/material paths checked. [G10]

### 33.2 New JSON runtime plan example

```json
{
  "schema_version": "3.0",
  "source_plan_id": "retopo_city_street_001",
  "runtime_target": {
    "engine": "Godot",
    "version_family": "4.7",
    "renderer": "Forward+",
    "target_fps": 60,
    "target_resolution": [1920, 1080],
    "device_class": "desktop_baseline",
    "measurement_status": "UNTESTED"
  },
  "archetypes": [
    {
      "archetype_id": "street_trashcan_A",
      "scene_uri": "res://assets/meshes/street_trashcan_A.glb",
      "mesh_node_path": "<resolved_during_godot_import_smoke_test>",
      "source_fingerprint": "sha256:<filled_at_build>",
      "geometry_qa_status": "PASS",
      "evaluated_triangles": 420,
      "surface_count": 1,
      "alpha_mode": "OPAQUE",
      "lighting_policy": "STATIC_REALTIME_LIT",
      "shadow_policy": "OPTIONAL",
      "instance_color_supported": true,
      "morph_targets": false
    }
  ],
  "batches": [
    {
      "batch_id": "parking_lot_east_trashcans",
      "archetype_id": "street_trashcan_A",
      "recommended_renderer": "MULTIMESH_SPATIALLY_CHUNKED",
      "world_cell_id": "parking_lot_east",
      "chunk_origin_m": [64.0, 0.0, 40.0],
      "spatial_extent_m": [14.0, 3.0, 10.0],
      "instance_ids": ["tc_001"],
      "instances": [
        {
          "id": "tc_001",
          "transform_world_column_major_4x4": [
            1,0,0,0, 0,1,0,0, 0,0,1,0, 65,0,41,1
          ],
          "color_rgba": [0.9, 0.92, 0.88, 1.0]
        }
      ],
      "bounds_mode": "UNION_TRANSFORMED_MESH_AABBS",
      "collision_policy": "EXTERNAL_PROXY_TABLE",
      "required_qa": ["godot_import", "camera_culling", "lod", "lighting", "frame_time"]
    }
  ]
}
```

The single instance illustrates schema structure; production exports must contain **one instance entry per ID**. The `scene_uri` loads an imported `PackedScene` in Godot, **not** a `Mesh` directly; the consumer resolves `mesh_node_path` in the imported scene and extracts its `Mesh` resource before setting `MultiMesh.mesh`. Coordinates, extents, color and triangle counts are **illustrative**, not measured. The engine loader must normalize coordinate conventions, convert 4×4 transforms to `Transform3D` correctly, and convert world transforms to **batch-local** transforms via `T_local = inverse(T_chunk_world) × T_instance_world`.

### 33.3 Explicit import policies

- Prefer `.glb` for deterministic transfer; test `.blend` direct import only as an optional iteration path.
- Preserve UV0 and normal/tangent data; Godot can generate tangents where absent, but final normal-map assets require import verification. [G11]
- Generate LODs on import by default for supported scene imports; disable selectively where verified breakage occurs. [G03][G11]
- Test shadow mesh import where suitable, recognizing this affects shadow vertex work, not the mesh's basic silhouette. [G11]
- Preserve per-archetype pivots and material slot names. Test backface culling on intended opaque assets. [G10]
- A raw glTF mesh export plus placement JSON does **not** automatically become a `MultiMeshInstance3D`. An imported `.glb` is a scene resource; the consumer resolves the intended `MeshInstance3D` within it to extract its `Mesh`. A downstream loader/importer then builds batches, or an explicitly supported GPU-instancing import route must be validated against the pinned engine build.

## 34. Godot-side consumption: implementation reference, not Blender retopology code

This minimal Godot 4.7 **GDScript example** illustrates the downstream contract. It is a *reference for the team implementing the level loader*, not a dependency injected into Blender.

```gdscript
# Godot 4.7 — attach to a MultiMeshInstance3D.
# Assumes prototype and already-converted, CHUNK-LOCAL transforms.
extends MultiMeshInstance3D

@export var prototype: Mesh
@export var placements: Array[Transform3D] = []
@export var colors: Array[Color] = []

func _ready() -> void:
    if prototype == null:
        push_error("A prototype Mesh is required")
        return
    if not colors.is_empty() and colors.size() != placements.size():
        push_error("Provide one color per transform, or no colors")
        return

    var batch := MultiMesh.new()
    batch.transform_format = MultiMesh.TRANSFORM_3D
    batch.use_colors = not colors.is_empty()
    batch.mesh = prototype
    batch.instance_count = placements.size()  # Must follow format/feature setup.

    for i in range(placements.size()):
        batch.set_instance_transform(i, placements[i])
        if batch.use_colors:
            batch.set_instance_color(i, colors[i])

    multimesh = batch
    # For shipped scenes, compute a correct CHUNK-LOCAL full-mesh AABB and
    # set batch.custom_aabb; validate against a debug visualization.
    # The per-instance collisions/interactions belong to separate systems.
```

**Reference-code limitations:** This code does not read the JSON schema, does not calculate spatial clusters, does not create colliders, does not set custom instance shader data, does not create HLOD and does not bake occluders. It is intentionally small. For very large dynamic batches, evaluate bulk buffer submission via the documented RenderingServer/MultiMesh path rather than per-instance updates each frame. [G01][G02]

## 35. Runtime verification: A/B benchmark laboratory

### 35.1 Four variants — never compare only 'before' and 'after'

For each test scene, create (when meaningful):

- `A_BASELINE_UNOPTIMIZED`: original distinct meshes/scene layout, same renderer/materials/cameras.
- `B_RETOPO_ONLY`: mesh candidates with same placement and node strategy.
- `C_REUSE_AUTO_INSTANCING`: shared prototypes with independent `MeshInstance3D` objects; particularly important for Forward+ opaque meshes. [G09]
- `D_MULTIMESH_CHUNKED`: optimized archetypes, spatial batches and visual-equivalent materials.
- Optional `E_HLOD_COMBINED`: manual far representation, only for levels that need it.

The harness must **hold visual output and gameplay obligations constant** to make performance attribution credible. New lighting/occluders/collision changes must be isolated and documented as additional experimental factors, not silently bundled into the retopology comparison.

### 35.2 Test cameras for a walkable heist level

At least:

1. **Street long view:** many storefronts/facades visible, distant repeated meshes, sunlight and shadows.
2. **Sidewalk near prop cluster:** a close view over trash cans, racks, signs, curb geometry; validates silhouette and near LOD.
3. **Interior cluttered room:** shelves, cash registers, small props; tests draw burden and occlusion behind walls.
4. **Hallway/doorway transition:** reveals whether cross-room MultiMesh groups defeat occlusion.
5. **Rooftop/elevated overlook:** exposes too-large city-block batches, shared LOD and excessive draw distance.
6. **Nighttime light-heavy case:** tests shadow/lighting penalties; do not benchmark only in cheap noon lighting.
7. **Four-player gameplay stress composition (if applicable):** gameplay effects, AI, networked state transitions; asset optimization must still be evaluated under credible gameplay load.

### 35.3 Measurement contract

- Pin exact Godot binary (`4.7.x`), renderer, graphics API, render scale, resolution, CPU, GPU, driver, graphics options and light/shadow/GI settings.
- Warm up shader/pipeline compilation and resource loading; separate cold-start stutter from steady-state performance.
- Repeat fixed camera paths/poses with the same camera matrices, content and placement seeds; control frame pacing and background workload where possible.
- Collect at least frame time P50/P95/P99 (CPU and GPU where genuinely available), draw calls, submitted primitives, nodes, memory, culling/LOD captures, rendering artifacts and screenshot diffs.
- Report **absolute milliseconds** along with relative percentage. E.g., for a frame at 16.67 ms (60 FPS budget), a saved 0.3 ms has different significance from 10% of a tiny individual draw function.
- Reject wins that come from missing props, invisible material backfaces, disabled collision, shadow differences, changed camera exposure/FOV, missing glass or deleted light sources.
- A benchmark failure may be caused by scene configuration rather than the retopology geometry; tag `CAUSE_UNCERTAIN` and inspect instead of discarding the entire asset.

### 35.4 Suggested acceptance policy (project hypothesis, not standard)

- **Geometry:** all existing strict topology/visual QA gates must pass.
- **Runtime:** no statistically credible increase in P95 frame time or visible artifact on **any critical tested gameplay camera**, unless an explicit project tradeoff is documented.
- **Benefit claim:** `RUNTIME_IMPROVED` only when a measured gain exceeds noise across reruns, not merely because triangle/draw counts drop. No mandatory universal percentage target.
- **Regression:** a repeatable GPU or CPU increase in important views is a blocker, even if total draw calls decrease.
- **MultiMesh batch validity:** culling tests show no false invisibility; split groups when camera/occlusion or shared-LOD cases perform worse than auto/shared instancing.
- **Lighting/physics:** required baked/dynamic lighting, collisions, interactions, nav, asset-state IDs and shadows remain correct.

### 35.5 Sample benchmark output

```json
{
  "schema_version": "3.0",
  "scene": "PA_Town_Block_Stress",
  "test_case": "hallway_transition",
  "engine_build": "4.7.x-pinned-at-run",
  "renderer": "Forward+",
  "resolution": [1920, 1080],
  "timing_ms": {
    "baseline_p50": null,
    "baseline_p95": null,
    "candidate_p50": null,
    "candidate_p95": null,
    "candidate_gpu_p95": null
  },
  "render_stats": {
    "baseline_draw_calls": null,
    "candidate_draw_calls": null,
    "baseline_submitted_primitives": null,
    "candidate_submitted_primitives": null,
    "video_memory_delta_bytes": null
  },
  "visual_test": "NOT_RUN",
  "lighting_test": "NOT_RUN",
  "culling_test": "NOT_RUN",
  "physics_test": "NOT_RUN",
  "status": "GEOMETRY_PASS_RUNTIME_UNTESTED"
}
```

Use `null` for absent observations. Do **not** publish fictional timings or imply the document has benchmarked the user's game.

## 36. Extended test fixtures, acceptance checks and implementation order

### 36.1 Required runtime fixtures

These supplement the earlier geometry fixtures (`T01–T34`). IDs and expected behavior are executable requirements.

| Test | Setup | Required observed decision |
|---|---|---|
| `G01` | 500 linked curb pieces at local scale | Exact archetype reuse; compare shared nodes vs MultiMesh |
| `G02` | Same pieces scattered behind 15 walls | Spatial chunking beats or matches global batching where culling matters |
| `G03` | Distant and close copies in one huge batch | Split by camera depth or meaningful cell; shared-LOD issue detected |
| `G04` | One mesh with four material surfaces | Report non-constant draw/pass cost; no single-call promise |
| `G05` | Hard UV seam and bevel-normal split | Runtime vertex proxy differs from Blender vertex count |
| `G06` | Opaque mesh exported with culling disabled | Import warning and optional safe material correction |
| `G07` | Thin paper double-sided / alpha foliage | Correct exceptions; no indiscriminate culling |
| `G08` | 200 roof/foliage alpha cards, many overlapping | GPU/fill-rate comparison required, not tris-only ranking |
| `G09` | 20 identical meshes using unique per-object materials | No unsafe automatic instancing; test shader/tint option separately |
| `G10` | One morph-target prop among static duplicates | Morphing object not automatically MultiMeshed |
| `G11` | Modular walls needing baked lighting UV2 | Bake contract preserved; cross-placement UV2 behavior reviewed |
| `G12` | Solid building shell with instanced facade detail | Separate occluder path; occlusion remains functional |
| `G13` | Hundreds of collidable props | Visual batching does not erase colliders or produce 100s of unprofiled bodies |
| `G14` | Breakable object promoted during interaction | Stable object ID and swap between static visual and active object |
| `G15` | Blender n-gon window frame exported to Godot | Stable triangulation, no shading/hole regression |
| `G16` | 100 lights across indoor and outdoor cells | Lighting limits assessed; no all-city shared batch |
| `G17` | Hero vending machine at interaction range | Keep readably modeled details, individual state and near silhouette |
| `G18` | Distant facade/block HLOD | Correct visibility transitions without missing skyline landmark |
| `G19` | Forward+ identical opaque objects | Automatic instancing included as competing baseline |
| `G20` | Mobile/Compatibility renderer | Re-run tests; no inference from Forward+ measurements |
| `G21` | Normal/shadow mesh/LOD import settings vary | Pin import settings and identify change source |
| `G22` | Repeated trash can with per-instance tint | Correct `use_colors` and material support validated |
| `G23` | Excessive fixed chunk AABB vs recomputed | No vanishing object; bounds cover full transformed meshes |
| `G24` | Dynamic placement updates every frame | Profile upload CPU and GPU bandwidth before allowing live massive MultiMesh |

### 36.2 Implementation roadmap — additions to §24

**Sprint F — Runtime proxy analyzer in Blender:** material surfaces/alpha/sharp-normal and UV splits; stable archetype identity; unit/pivot checks; rendering intent JSON. No Godot dependencies. Done when fixtures G04/G05/G06/G09/G15 pass inspection.

**Sprint G — MultiMesh spatial planner:** room/facade/block-side partitioner, archetype reuse, exact transformed bounds, camera cost proxy, chunk preview overlays, saved transform manifest. Done when G01/G02/G03/G12/G16/G23 pass planner tests.

**Sprint H — Export and downstream smoke test:** `.glb` and JSON export; Godot 4.7 consumer script or import hook; import normals/UVs/pivots/materials; instance color, culling, shadow and LOD QA. Done when G06/G10/G11/G15/G22 pass Godot fixtures.

**Sprint I — Benchmark harness and feedback:** automated fixed-camera A/B/C/D scene comparisons; serialized Godot counters, CPU/GPU timings where supported, screenshots, regression classification; feed evidence back into Blender plan scores without inventing performance labels. Done when G07/G08/G13/G14/G17/G18/G19/G20/G21/G24 are demonstrated, and every released fixture has runtime evidence.

### 36.3 Updated definition of done

- [ ] The Blender tool classifies runtime intent independent from geometry type.
- [ ] It can recognize exact repeated mesh archetypes without damaging canonical mesh sharing.
- [ ] It reports triangles **and** material surfaces **and** render-vertex proxies separately.
- [ ] It makes an explicit selection among individual meshes, automatic/shared instancing, chunked MultiMesh, merged static geometry, and HLOD.
- [ ] Its MultiMesh plans are partitioned by both semantic visibility spaces and actual spatial bounds.
- [ ] It flags MultiMesh group-culling and shared-LOD risks, not just draw-call savings.
- [ ] It protects baked lighting, occlusion, physics, gameplay identities and shadow obligations.
- [ ] It generates deterministic Blender-exportable glTF assets and machine-readable placement/import instructions.
- [ ] Its pinned Godot 4.7 harness can reproduce before/after visual/performance comparisons.
- [ ] No asset is described as **runtime optimized** solely from geometric analysis; engine-tested status is required.

---

## 37. Annotated, version-pinned Godot 4.7 references

These links were checked against the **`/en/4.7/`** documentation branch. They document Godot behavior, not measured results for a specific game or GPU. Some 4.7 pages carry an “not yet updated for 4.7” advisory; compatibility assumptions must be backed by the pinned test harness. Parenthetical section callouts above refer to these references.

**[G01] Optimization using MultiMeshes — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/performance/using_multimesh.html  
*Confirmed:* Hardware instancing; one group culled all-or-none, spatially split groups recommended, visible instance count, optional per-instance shader data. *Application:* §§26, 29, 34.

**[G02] `MultiMesh` class — Godot 4.7**  
https://docs.godotengine.org/en/4.7/classes/class_multimesh.html  
*Confirmed:* One mesh resource instanced repeatedly; no per-instance culling, relevant light restriction; blend shapes ignored; instance formats/color/custom data, custom AABB. *Application:* §§27–29, 34.

**[G03] Mesh level of detail (LOD) — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html  
*Confirmed:* Import-time `meshoptimizer` LOD, general default on imported scenes, screen-space selection, **one shared LOD across MultiMesh instances**. *Application:* §§29, 31.

**[G04] Occlusion culling — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/3d/occlusion_culling.html  
*Confirmed:* Occluder baking only takes `MeshInstance3D`, not `MultiMeshInstance3D`; any `GeometryInstance3D` may be occluded; conservative full-AABB visibility. *Application:* §§29, 32, 35.

**[G05] Visibility ranges (HLOD) — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/3d/visibility_ranges.html  
*Confirmed:* Manual node-level visibility ranges and distant representations, usable with `MultiMeshInstance3D`; manual HLOD and automatic LOD can coexist. *Application:* §31.

**[G06] Using Lightmap global illumination — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html  
*Confirmed:* UV2 requirement, static bake setup, instance scale caveats. *Application:* §§27, 32.

**[G07] `Mesh` resource — Godot 4.7**  
https://docs.godotengine.org/en/4.7/classes/class_mesh.html  
*Confirmed:* Render meshes comprise separately described surfaces with their own arrays/materials. *Application:* §§26, 30, 32.

**[G08] `Performance` monitors — Godot 4.7**  
https://docs.godotengine.org/en/4.7/classes/class_performance.html  
*Confirmed:* Draw-call and submitted-primitive monitor semantics, memory stats, monitor limitations. *Application:* §§26, 35.

**[G09] Optimizing 3D performance — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html  
*Confirmed:* Forward+ automatic instancing conditions, alternatives with MultiMesh, transparent object costs and culling. *Application:* §§26, 27, 32, 35.

**[G10] Available 3D formats — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html  
*Confirmed:* glTF recommended, Blender-to-glTF import path; Blender backface-culling default caveat. *Application:* §§28, 32–33.

**[G11] Import configuration — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html  
*Confirmed:* Generate LODs; Ensure Tangents/MikkTSpace; Shadow Meshes; post-import configuration. *Application:* §§31, 33, 35.

**[G12] GPU optimization — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html  
*Confirmed:* CPU, driver and GPU bottlenecks differ across hardware; vertex/pixel throughput and complexity demand empirical analysis. *Application:* §§26, 30, 32.

**[G13] Model export considerations — Godot 4.7**  
https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html  
*Confirmed:* coordinate-space conventions, triangulate before export for predictable results, apply transforms appropriately. *Application:* §§28, 32, 33.

---

## 38. Final engineering direction: optimize a scene, not just a mesh

Retopology is **one layer** of runtime optimization. The tool must output a *clean and reusable canonical mesh*, retain its artist-authoring semantics, and attach the necessary evidence and metadata for the level builder to decide **how many copies, where, with which material and lighting rules, and in which culling chunk**.

For the Godot 4.7 heist-game scenario, a meaningful result is:

> **“We reduced the repeated streetlight prototype's unnecessary geometry without changing its silhouette, reused the same imported mesh resource, split placements at room/street visibility boundaries, retained correct material/lighting/collision behavior, and measured a frame-time improvement on target camera paths.”**

Not:

> **“The mesh is 70% fewer polygons, so the game will run 70% faster.”**

That distinction is the definition of a production-grade, game-runtime-aware retopology planner.
