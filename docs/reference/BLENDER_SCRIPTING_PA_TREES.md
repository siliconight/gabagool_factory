---
title: Building Recognizable Pennsylvania Trees with Blender Scripting
version: 1.0
date: 2026-10-10
target_api: Blender 4.5 LTS baseline; verify against the installed Blender build
audience: [Blender technical artists, procedural asset developers, environment artists]
units: metres
companion: PA_NATIVE_TREES_PHILLY_DELCO.md
validation: Python geometry checks passed; Blender runtime and engine import not executed
---

# Building recognizable Pennsylvania trees with Blender scripting

Blender can generate the trees in the companion [Pennsylvania tree guide](PA_NATIVE_TREES_PHILLY_DELCO.md), but the generator needs to describe **how each species grows**. Changing the leaf texture on one generic tree is not enough.

The production goal is a tree that reads correctly at three distances: its crown and major limbs from far away; branching, bark, and foliage grouping at normal gameplay distance; and leaf structure, junctions, and root flare close up. A low-poly tree can succeed at all three if detail is allocated deliberately.

This guide contains a production design, numeric starting recipes, a runnable architecture-study script, and verification criteria. It does not assume a particular tree add-on. The example uses Blender's mesh API and standard Python. Geometry Nodes are an optional assembly stage.

## 1. Define the result before choosing an algorithm

A tree asset should have six independent descriptions:

| Description | Examples | What it controls |
|---|---|---|
| Species | White oak, sycamore, tuliptree | Bark family, leaf shape, branching tendencies, seasonal behaviour. |
| Growth context | Forest, edge, open lawn, managed street | Crown height/width, missing branches, direction of growth, pruning. |
| Development | Sapling, young, mature, veteran | Trunk proportions, bark age, branch hierarchy, crown complexity. |
| Condition/history | Healthy, storm break, old pruning, flood exposure | A few causal modifications with consistent consequences. |
| Season | Early spring, summer, autumn, winter | Leaf presence, color, flowers, fruit, retained dead leaves. |
| Delivery role | Hero tree, normal gameplay tree, distant stand | Mesh detail, material count, collision, LOD, and foliage representation. |

For example, `white_oak + open_grown + mature` should produce broad heavy limbs. `white_oak + forest_grown + mature` should have a longer clear trunk and a narrower elevated crown. Both remain white oaks.

### Observable acceptance targets

1. In a black silhouette, an elm reads as a vase, a dogwood as layered shelves, and a tuliptree as a tall upright tree.
2. With leaves hidden, the main branches support the intended crown.
3. With flat gray materials, scale, root flare, taper, and branch junctions remain believable.
4. With leaves visible, foliage follows small branches and leaves intentional gaps.
5. With textures visible, bark scale and leaf identity reinforce the form.
6. In the target game camera, important cues survive the first two LOD transitions.

These are proposed production acceptance criteria. They are not botanical identification tests or measured performance guarantees.

## 2. Use a skeleton, then surfaces, then foliage

Represent the tree as a graph before creating Blender objects. Each branch needs an ID, parent ID, attachment position, sequence of centreline points, radius samples, and growth order. Leaves and foliage sprays attach to explicit sockets on fine branches.

```json
{
  "branch_id": "trunk/03/02",
  "parent_id": "trunk/03",
  "parent_attachment_u": 0.73,
  "order": 2,
  "points_m": [[0.0, 0.0, 8.0], [0.4, 0.1, 8.4], [0.9, 0.2, 8.6]],
  "radii_m": [0.045, 0.022, 0.008],
  "alive": true,
  "leaf_bearing": true
}
```

Here `parent_attachment_u` is normalized distance along the parent branch, not a vertex index. Preserve it when resampling so a topology change does not detach the child.

### Why this separation matters

- A leafless version can reuse the skeleton.
- Bark UVs can follow branch length and circumference.
- LOD can remove fine branches without changing the silhouette-defining limbs.
- Wind can follow parent-child relationships.
- Broken branches can remove their descendants and leave a coherent scar.
- Growth context can modify architecture before geometry is built.
- The same hierarchy can produce a detailed baking source and a lighter game mesh.

Do not create thousands of independent Blender objects for individual leaves during final assembly. Collect mesh arrays or use instances, then choose an explicit export representation. The API provides `Mesh.from_pydata()` for constructing geometry from vertices, edges, and faces. Validate the generated arrays rather than assuming the API makes malformed geometry valid. [B1]

## 3. Choose a branch-generation method

| Method | Good use | Limitations to address |
|---|---|---|
| Authored recursive rules | Species with readable scaffold structure; quick controlled variants | Repeated angles can become mechanical; unconstrained recursion produces bushes or fractals. |
| Space colonization | Crowns shaped around light opportunities, neighbouring crowns, or a target volume | Needs a species scaffold, radius rules, and constraints; by itself it does not know oak versus tuliptree. |
| Authored main limbs plus procedural twigs | Hero trees and strong regional silhouettes | Requires initial art direction but gives reliable landmarks. |
| L-systems | Explicit repeated botanical rules and educational growth experiments | A concise grammar is not automatically a convincing mature tree. |
| Existing tree generator | Rapid experiments or a source for baking | Verify license, version, export behaviour, and actual species controls before integrating. |

**Recommended production approach:** author or generate a small number of major limbs using a species recipe, then grow secondary branches toward a constrained crown volume, then create leaf-bearing twigs and sockets. This combines recognizable structure with controlled variation.

Runions, Lane, and Prusinkiewicz describe a space-colonization method using attractor points to grow branching structures in three dimensions. Their work is a useful algorithmic foundation; the species recipes and pipeline in this guide are an original application of those ideas. [B2]

### Space-colonization implementation outline

1. Sample attractors inside several overlapping crown lobes, not a single perfectly smooth sphere.
2. Subtract no-growth volumes for buildings and explicitly preserved gaps.
3. For each attractor, find an eligible branch node inside an influence radius.
4. Average the directions from each node to its assigned attractors.
5. Combine that direction with continuation, upward growth, and species-specific lateral bias.
6. Add a segment of controlled length.
7. Remove attractors reached within a kill distance.
8. Stop when attractors are consumed, no growth occurs, or a fixed iteration limit is reached.
9. Prune redundant fine branches and calculate radii from their descendants.
10. Produce foliage sockets on surviving fine growth.

Use a spatial hash or k-d tree for neighbour queries when counts become large. If no node is close enough to any attractor, extend an appropriate leader toward the nearest crown region or report an invalid setup; do not loop indefinitely. Influence and kill distances are lengths in metres and must scale with the chosen tree.

## 4. Production recipe contract

This JSON is a suggested contract for the full generator. The starter script later in this document deliberately implements only a smaller `PRESETS` dictionary. Adding fields to this JSON will not add those features to the starter automatically.

```json
{
  "schema_version": 1,
  "recipe_version": "quercus_alba_open_mature_001",
  "species_id": "quercus_alba",
  "context": "open_grown",
  "development": "mature",
  "seed": 42017,
  "units": "metres",
  "dimensions": {
    "height_m": 23.0,
    "crown_spread_m": [22.0, 19.0],
    "dbh_m": 0.95,
    "crown_start_height_m": 5.5
  },
  "architecture": {
    "family": "broad_spreading",
    "major_scaffold_count": 7,
    "major_angle_from_vertical_deg": [45.0, 78.0],
    "branch_orders": 4,
    "azimuth_jitter_deg": 16.0,
    "upward_tip_bias": 0.25,
    "crown_lobes": 7,
    "crown_gap_target": 0.15
  },
  "foliage": {
    "arrangement": "alternate",
    "unit": "simple_leaf",
    "blade_length_m": [0.10, 0.20],
    "shape_family": "rounded_lobed_oak",
    "leaf_bearing_orders": [3, 4],
    "atlas_id": "quercus_alba_summer_v01"
  },
  "bark": {
    "family": "pale_gray_plates",
    "reference_tile_width_m": 0.60,
    "reference_tile_height_m": 1.20,
    "geometry_detail": "root_flare_and_major_plates_only"
  },
  "history": {
    "pruning_cuts": [],
    "broken_branch_ids": [],
    "dominant_light_direction_xy": [1.0, 0.0],
    "edge_response_strength": 0.12
  },
  "season": {
    "name": "summer",
    "leaf_presence": 1.0,
    "senescence": 0.0
  },
  "delivery": {
    "role": "gameplay",
    "lod_triangle_targets": [18000, 7500, 2500],
    "material_target": 2,
    "collision": "trunk_and_selected_major_limbs"
  }
}
```

All numeric architecture and budget settings are **authored starting values**. Calibrate them against local reference photographs and the target renderer. They are not measured species constants.

Define `crown_gap_target` operationally: for example, fraction of background pixels inside an artist-marked crown outline in a fixed orthographic view. Without a measurement method, a "15% gap" control is ambiguous.

### Keep randomness stable

Derive a random stream from `asset_seed + stable_branch_id + operation_name`. Do not use one global random stream for the whole forest, and do not use Python's process-randomized `hash()` as a persistent seed. Changing leaf density should not regenerate the main trunk or move unrelated trees.

Record the generator version alongside the seed. A seed alone cannot reproduce an asset after the algorithm changes.

## 5. Species architecture recipes

The companion guide supplies habitat and botanical context. The following values are **artist-authored starting ranges for mature forms**, not survey data. `C/H` is crown-start height divided by total height; `W/H` is crown diameter divided by height. Angles are measured away from vertical: 0° points up, 90° is horizontal, above 90° points down.

| Species/form | C/H | W/H | Architecture controls that matter |
|---|---:|---:|---|
| White oak, open | 0.18–0.35 | 0.80–1.20 | 5–9 substantial scaffold systems; long sideways arcs; tips can turn upward; varied crown lobes. |
| Northern red oak | 0.28–0.50 | 0.60–0.90 | 5–9 ascending scaffold systems; more vertical continuity than an old spreading white oak. |
| Black oak | 0.30–0.55 | 0.55–0.85 | Uneven broad crown; strong coarse limbs; site-driven rather than universal distortion. |
| Chestnut oak, dry slope | 0.25–0.50 | 0.55–0.95 | Uneven limb reach and restrained height; bark relief is a major cue. |
| Pin oak | 0.15–0.35 | 0.40–0.70 | Lower limbs 95–115°; middle 65–90°; upper 25–55°; strong leader. |
| Swamp white oak | 0.20–0.40 | 0.70–1.05 | Broad heavy oak framework; comparatively shallow-lobed foliage. |
| Red maple | 0.30–0.50 | 0.55–0.85 | Rounded/oval crown; ascending limbs; opposite fine-growth attachment. |
| Silver maple | 0.20–0.40 | 0.70–1.10 | Long spreading limbs; uneven major forks; outward and downward terminal growth. |
| Sugar maple | 0.30–0.50 | 0.60–0.90 | Dense oval crown divided into branch-supported lobes; restrained gaps. |
| Tuliptree, forest | 0.55–0.75 | 0.30–0.55 | Persistent tall leader; high crown; small lower limbs lost with competition. |
| American sycamore | 0.25–0.50 | 0.65–1.00 | Few large readable divisions; broad irregular crown; exposed pale upper wood. |
| American beech | 0.25–0.50 | 0.65–1.00 | Long lateral branches and fine twigs; low crown when space allows; smooth trunk. |
| Hickories, forest | 0.50–0.70 | 0.35–0.60 | Clear upright stem, elevated crown, compound foliage sprays. |
| Black walnut | 0.30–0.55 | 0.65–1.00 | Coarse open branching; long compound-leaf units; visible internal structure. |
| Black cherry, forest | 0.50–0.70 | 0.35–0.60 | Tall relatively straight stem; small leaf units and fine perimeter. |
| American elm | 0.25–0.45 | 0.75–1.15 | Major limbs ascend before arching out; fine downward tips complete the vase. |
| Dogwood | 0.15–0.35 | 0.80–1.30 | Flattened foliage shelves; short vertical separation; visible negative space. |
| White pine | 0.20–0.60 | 0.35–0.65 | Leader and whorl history; broken tier repetition; high irregular mature crown. |
| Hemlock | 0.10–0.45 | 0.35–0.65 | Lateral fans, drooping ends and leader; fine flat needle sprays. |
| Redcedar | 0.05–0.25 | 0.30–0.60 | Compact scale-foliage sprays; tapering crown with limited local irregularity. |

Forest and open-grown ranges overlap deliberately. Context modifies a species; it does not turn every forest tree into the same narrow pole.

### Remaining species: the specific change your script needs

| Species | Required distinction |
|---|---|
| Boxelder | Low irregular branching; opposite **compound** leaves. |
| Cottonwood | Tall coarse framework, triangular leaf outlines, independent petiole-driven flicker. |
| Black willow | Uneven stems; many fine peripheral twigs; narrow leaf blades; moderate droop. |
| Sweet birch | Fine crown, dark age-dependent bark, horizontal lenticels on younger wood. |
| River birch | Separate single-stem and planted multi-stem recipes; selected peeling-bark geometry. |
| Blackgum | Irregular spreading branch masses; small unlobed glossy leaves; blockier older bark. |
| Sweetgum | Strong young leader; star-shaped **alternate** leaves; optional hanging seed balls. |
| White/green ash | Opposite fine growth; compound leaves; condition chosen from time/site evidence. |
| Hackberry | Localized corky bark relief; fine irregular perimeter. |
| Hornbeam | Fluted trunk cross-section and smooth surface, rather than merely a normal map. |
| Sassafras | A mixture of unlobed, mitten, and three-lobed leaf units on the same asset. |
| Serviceberry | Fine small crown; restrained spring flowers; optional multiple stems. |
| Pawpaw | Large simple leaves on small stems; understory patch placement. |
| Yellow birch | Golden/copper peeling bark; cooler-site recipe. |
| Pitch pine | Stiffer needle sprays in bundles of three; coarser irregular architecture. |
| Willow oak | Oak architecture carrying narrow unlobed leaves. |
| Sweetbay | Small-tree/multiple-stem option, pale leaf backs, northern seasonal behaviour. |

Do not force conifers through the broadleaf leaf-placement routine. Share utilities—paths, tubes, random streams, UVs—but retain different foliage modules.

## 6. Branch geometry that survives close inspection

### Taper and attachment

Sample branch radius along its path. A useful artistic starting model is:

```text
radius(t) = tip_radius + (base_radius - tip_radius) * (1 - t)^taper_exponent
```

Here `t` runs from 0 at the attachment to 1 at the tip. Start with an exponent around 0.7–1.5 and compare references. This is a modeling control, not a universal growth law.

At a fork, a useful initial thickness constraint is:

```text
sum(child_radius^p) <= parent_radius^p
```

Using `p` near 2 gives an area-based starting point. Botanical branching is more complex; use the relation to catch implausibly thick child branches, not to claim exact biology. Calibrate swelling at a real fork separately.

**Important:** A graph connection does not guarantee a good mesh junction. Intersecting tubes are acceptable for a distant prototype, but visible hero forks need a branch collar and a continuous transition.

### Tube construction

1. Resample each centreline according to curvature and screen importance.
2. Estimate a tangent at each sample.
3. Transport a local cross-section frame along the curve; avoid arbitrary independent rotations.
4. Generate a ring of vertices using the sampled radius.
5. Join adjacent rings with consistent winding.
6. Preserve the principal silhouette when reducing radial sides.
7. Store distance along the branch and branch ID before combining meshes.

An abrupt frame flip twists UVs and produces visible seams. Parallel transport, or a carefully projected previous frame, is more stable than selecting a new global "up" axis at every sample.

### Initial cross-section budgets

| Part | Normal gameplay asset | Close hero asset |
|---|---:|---:|
| Main trunk | 8–12 radial sides | 12–20, concentrated where visible |
| Major limbs | 6–10 | 8–14 |
| Secondary limbs | 4–7 | 6–10 |
| Fine twigs | Geometry only where visible | 3–5, or bake into foliage units |

These are suggested starting budgets. A trunk viewed at arm's length or against a bright sky may need more silhouette detail. A dense distant stand may need substantially less.

### Root flare and bark age

Build a root collar that widens into the ground and a few uneven buttress directions. Flatten or hide roots below terrain rather than exposing a decorative radial star. Avoid roots floating above slopes.

Young upper branches and old lower trunk usually need different surface treatments. Sycamore should grade from coarse lower bark toward pale patchy upper wood; beech should remain comparatively smooth; shagbark's conspicuous plates belong mainly on sufficiently mature wood.

## 7. Leaves, sprays, and crown volume

There are three distinct modeling units:

| Unit | Appropriate use |
|---|---|
| Individual leaf blade | Close view, reference assembly, or baking source. |
| Compound leaf or needle spray | Botanically connected group: walnut rachis with leaflets, pine needle bundle, hemlock fan. |
| Foliage cluster/card | Game representation of several leaves and twigs; scale must match what the image represents. |

Do not size a card containing twelve leaves as though it were one 12 cm leaf. Record both the botanical unit and the cluster's physical bounds.

### Build individual broad leaves

1. Define a 2D outline in leaf-local coordinates with the petiole at the origin.
2. Distinguish rounded oak lobes, pointed oak lobes, maple lobes, and tuliptree's notched tip.
3. Triangulate concave outlines correctly; a naive fan can fill the gaps between lobes.
4. Add a shallow central fold, slight longitudinal curvature, and restrained edge variation.
5. Create a separate back-surface treatment or a shader that handles the back face deliberately.
6. Keep the leaf's dimensions in metres. Small species should not receive huge foliage blades simply to fill the crown.

For compound leaves, create a rachis and place leaflets along it. A compound leaf is one botanical leaf; opposite versus alternate describes how those entire leaves attach to the twig.

### Useful physical scale checks

The following are approximate **reference-check ranges**, not exact limits: maple blades often occupy roughly 0.06–0.15 m; large oak/tuliptree blades roughly 0.10–0.20 m; sycamore blades can be broader, around 0.12–0.25 m. A walnut compound leaf is much longer than one walnut leaflet. Check the species photographs before fixing an atlas scale.

### Attach foliage to growth

Generate sockets on distal portions of living fine branches. Each socket should provide position, twig tangent, branch ID, attachment arrangement, and a stable random key. Generate a petiole or include one in the foliage unit so the attachment is visible when close enough.

For opposite leaves, use paired sockets at nodes with a rotated orientation at successive nodes. For alternate leaves, use alternating or species-appropriate arrangements. This does **not** require every surviving large branch to appear in perfect pairs; age and branch loss break that pattern.

Populate several branch-supported crown lobes. Keep gaps between major systems and some exposed internal wood. A crown should have a volume of foliage, not just an outer shell of flat green polygons.

### Conifer modules

- **White pine:** Create fine sprays using bundles of five long slender needles in the close representation. Replace them with textured sprays at gameplay distance.
- **Hemlock:** Create flattened branchlet fans with short needles and hanging tips. The fan orientation is part of the silhouette.
- **Redcedar:** Use compact branching sprays of scale foliage, with juvenile pricklier growth only when relevant.
- **Pitch pine:** Use stiffer, coarser three-needle bundles and a different architecture from white pine.

Individual needles are useful for baking and selected close shots. Modeling every needle on every distant tree is usually the wrong allocation of work.

## 8. Bark and foliage materials

Start with two materials per delivered tree where practical: bark and foliage. This is an authored production target; combining materials does not automatically remove alpha overdraw or shadow cost.

### Species-specific bark generation

| Bark family | Procedural construction | Geometry needed close up |
|---|---|---|
| Beech | Low-frequency gray variation, subtle small marks, low bump amplitude | Broad trunk form and scars; keep deep fissures out. |
| White/red oak | Longitudinal ridges plus irregular plate boundaries; change scale with branch size | A few silhouette-affecting ridges on major visible wood. |
| Chestnut oak | Larger deeper longitudinal relief, broken into irregular ridges | Stronger silhouette where the trunk is close. |
| Sycamore | Large irregular peeling regions, masked by height and bark age; cream/gray/olive/tan palette | Major patch edges only when close enough to matter. |
| Shagbark hickory | Long irregular vertical strips over a furrowed base | Sparse lifted strips with actual thickness and uneven curl. |
| River birch | Age-dependent pale/tan/cinnamon regions over darker lower bark | Selected thin curls; avoid covering the trunk in identical ribbons. |
| Black cherry | Horizontal marks on young growth; small dark flaky plates on mature trunk | A few edge flakes near the viewer. |
| Hornbeam | Smooth gray material | Actual longitudinal trunk fluting. |
| Hackberry | Corky localized lumps and interrupted ridges | Local relief where visible in silhouette. |
| Redcedar | Fine fibrous longitudinal structure and warm muted bark | A few irregular peeling fibres at close range. |

Use directional coordinates. Stretching isotropic noise is not enough to produce a convincing branch-aware bark pattern. Bake approved procedural materials to engine-ready textures; Blender shader graphs are not automatically portable to glTF or Godot. [B5]

### Bark UV scale

Use the branch's accumulated centreline length for the vertical coordinate and circumference for the horizontal coordinate:

```text
V = distance_along_branch_m / texture_tile_height_m
U = distance_around_ring_m / texture_tile_width_m
```

Preserve a consistent physical texture scale across trunk and limbs. Check the seam, branch junctions, and shrinking circumference at tips. A 10 cm twig must not display the same enormous cracks as a metre-wide trunk.

### Foliage texture rules

- Build atlases from owned or appropriately licensed material, or render original modeled leaf assemblies.
- Include front/back differences, a connected twig or rachis where relevant, and a few distinct silhouettes.
- Use edge padding/dilation around opaque pixels to reduce mip fringes.
- Keep broad values and subtle variation visible after mipmapping; tiny veins are a close-detail feature.
- Bake lighting-independent base color. Strong photographed sunlight and shadows will conflict with game lighting.
- Generate normals and roughness deliberately. Leaves should not look like uniformly glossy plastic.
- Introduce color variation per branch or crown region, with a small leaf-level remainder. Uncorrelated neon leaf colors look synthetic.

Foliage transparency is renderer-dependent. Prefer a tested cutout/alpha-scissor approach when it suits the target art direction; compare alpha-hash and coverage options in the actual renderer. Ordinary blended transparency can create sorting and overdraw problems. Godot's material documentation describes the supported modes and their tradeoffs. [B6]

Leaf translucency is transmitted/backscattered light, not self-illumination. Avoid using constant emission to brighten leaves in every lighting condition.

## 9. Geometry Nodes assembly option

Let Python own the reproducible recipe and branch graph. Use Geometry Nodes for fast foliage assembly when iteration benefits from a visible graph.

1. Python creates the woody mesh and a point mesh containing foliage sockets.
2. Store attributes such as `branch_id`, `leaf_variant`, `leaf_scale`, and the orientation data your node group expects.
3. Read the socket geometry with Object Info.
4. Read a collection of leaf/spray variants with Collection Info, configured so variants remain separate instances.
5. Use Instance on Points with selection, orientation, scale, and variant index driven by socket data.
6. Join the foliage instances with the wood for preview, or retain two outputs for material/export control.
7. Realize Instances only where the downstream operation or chosen export path requires actual mesh geometry.
8. Inspect the evaluated result and export a deliberate baked mesh or supported instancing representation.

Instances reference shared geometry; realizing makes geometry available for operations that need it and may substantially increase data size. It is not a promise that every instance becomes an independent object. [B3–B4]

Use named node sockets where possible, inspect their types, and fail clearly when required sockets are missing. Geometry Nodes interfaces evolve across versions; record the Blender version used for each generated release.

## 10. Starter script: three inspectable architecture studies

The following script creates side-by-side white-oak, tuliptree, and sycamore studies. It demonstrates deterministic branch streams, tapered tube geometry, different nominal proportions, attached simple leaves, and concave leaf triangulation.

**What it produces:** a diagnostic scaffold with deliberately sparse, physically scaled foliage. Hide the leaf objects to inspect the branching. It creates a new collection and leaves existing scene objects intact. Running it again creates another collection.

**What still needs production work:** reference-matched crown density, rounded refinement of simplified leaf outlines, bark UVs/textures, species-specific bark, continuous branch collars, exact DBH/height calibration, conifers, seasonal variants, LODs, collision, wind, and export. Tube junctions overlap rather than forming a welded organic surface. Nominal dimensions in `PRESETS` are controls, not exact measured output dimensions.

The study intentionally uses the same plain bark material so structure can be reviewed first. Its light leaf coverage should not be mistaken for a finished summer canopy. Add a denser twig stage or build/bake connected foliage clusters before evaluating a final leaf-on tree.

### Run it

1. In Blender, open the Scripting workspace and create a text block.
2. Paste the complete code block below and choose **Run Script**.
3. Find `PA_Tree_Architecture_Study` in the Outliner.
4. Select its objects and use **Frame Selected**.
5. Inspect from front, side, top, and a low camera angle. Switch to Material Preview if needed.
6. Change one preset or seed at a time while comparing screenshots.

Alternatively, save the block as `pa_tree_demo.py` and run:

```bash
blender --background --python pa_tree_demo.py
```

The background command creates the scene in memory but does not save a `.blend` file. Add a deliberate save step only after choosing a destination. For checks without Blender:

```bash
python pa_tree_demo.py --check
```

```python
"""PA tree architecture study. Blender 4.5+ target; no add-ons required.
Outside Blender: python pa_tree_demo.py --check
In Blender: Text Editor > Run Script, or blender --background --python pa_tree_demo.py
Creates a NEW collection; does not clear the scene or write files.
"""
import hashlib
import math
import random
import sys

PRESETS = {
    "quercus_alba": dict(h=20.0, w=20.0, dbh=0.85, clear=0.28,
                         leaders=7, rise=0.18, leaf=0.17, shape="oak"),
    "liriodendron_tulipifera": dict(h=28.0, w=14.0, dbh=0.70, clear=0.58,
                                  leaders=10, rise=0.25, leaf=0.18, shape="tulip"),
    "platanus_occidentalis": dict(h=24.0, w=22.0, dbh=1.00, clear=0.32,
                                leaders=7, rise=0.16, leaf=0.23, shape="sycamore"),
}

# Original simplified outlines, counter-clockwise, in a unit leaf coordinate system.
# Base at (0, 0), tip toward +Y. These are teaching shapes, not scanned specimens.
OUTLINES = {
    "oak": [(0,0),(.10,.10),(.22,.15),(.24,.24),(.11,.30),
            (.29,.37),(.30,.48),(.12,.53),(.27,.61),(.25,.72),
            (.10,.76),(.14,.87),(0,1),(-.14,.87),(-.10,.76),
            (-.25,.72),(-.27,.61),(-.12,.53),(-.30,.48),(-.29,.37),
            (-.11,.30),(-.24,.24),(-.22,.15),(-.10,.10)],
    "tulip": [(0,0),(.16,.12),(.38,.23),(.24,.44),(.42,.76),
              (.35,1),(0,.84),(-.35,1),(-.42,.76),(-.24,.44),
              (-.38,.23),(-.16,.12)],
    "sycamore": [(0,0),(.12,.20),(.42,.25),(.28,.43),(.50,.59),
                 (.20,.62),(0,1),(-.20,.62),(-.50,.59),(-.28,.43),
                 (-.42,.25),(-.12,.20)],
}

def rng_for(seed, key):
    digest = hashlib.blake2b(f"{seed}:{key}".encode(), digest_size=8).digest()
    return random.Random(int.from_bytes(digest, "little"))

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def length(a): return math.sqrt(dot(a,a))
def unit(a):
    n = length(a)
    if n < 1e-10: raise ValueError("Zero-length direction")
    return mul(a,1/n)
def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def mix(a,b,t): return add(mul(a,1-t),mul(b,t))
def basis(t):
    ref = (0,0,1) if abs(t[2]) < .9 else (1,0,0)
    u = unit(cross(ref,t))
    return u, cross(t,u)

def turn(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def triangulate(poly):
    """Ear clipping handles the concave lobes that a naive centre fan cannot."""
    ids = list(range(len(poly)))
    area = sum(poly[i][0]*poly[(i+1)%len(poly)][1]-
               poly[(i+1)%len(poly)][0]*poly[i][1] for i in ids)
    if area < 0: ids.reverse()
    faces = []
    while len(ids) > 3:
        for j in range(len(ids)):
            a,b,c = ids[j-1],ids[j],ids[(j+1)%len(ids)]
            if turn(poly[a],poly[b],poly[c]) <= 1e-10: continue
            inside = any(
                turn(poly[a],poly[b],poly[k]) >= -1e-10 and
                turn(poly[b],poly[c],poly[k]) >= -1e-10 and
                turn(poly[c],poly[a],poly[k]) >= -1e-10
                for k in ids if k not in (a,b,c))
            if inside: continue
            faces.append((a,b,c)); ids.pop(j); break
        else: raise ValueError("Leaf outline is degenerate or self-intersecting")
    faces.append(tuple(ids))
    return faces

class MeshData:
    def __init__(self): self.vertices,self.faces = [],[]
    def append(self,vertices,faces):
        n = len(self.vertices)
        self.vertices.extend(vertices)
        self.faces.extend(tuple(n+i for i in face) for face in faces)

def tube(mesh,path,radii,sides=7):
    vertices,faces = [],[]
    tangent = unit(sub(path[1],path[0]))
    previous_u,_ = basis(tangent)
    for j,p in enumerate(path):
        tangent = unit(sub(path[min(j+1,len(path)-1)],path[max(0,j-1)]))
        projected = sub(previous_u,mul(tangent,dot(previous_u,tangent)))
        u = unit(projected) if length(projected)>1e-8 else basis(tangent)[0]
        v = cross(tangent,u)
        previous_u = u
        for k in range(sides):
            angle = math.tau*k/sides
            offset = add(mul(u,math.cos(angle)),mul(v,math.sin(angle)))
            vertices.append(add(p,mul(offset,radii[j])))
        if j:
            for k in range(sides):
                a=(j-1)*sides+k; b=(j-1)*sides+(k+1)%sides
                c=j*sides+(k+1)%sides; d=j*sides+k
                faces.extend([(a,b,c),(a,c,d)])
    for k in range(1,sides-1): faces.append((0,k+1,k))
    n=(len(path)-1)*sides
    for k in range(1,sides-1): faces.append((n,n+k,n+k+1))
    mesh.append(vertices,faces)

def curved_path(start,end,bend,steps=7):
    return [add(mix(start,end,i/steps),mul(bend,math.sin(math.pi*i/steps)))
            for i in range(steps+1)]

def leaf(mesh,base,direction,size,shape,roll):
    t=unit(direction); u,v=basis(t)
    side=add(mul(u,math.cos(roll)),mul(v,math.sin(roll)))
    normal=cross(side,t)
    vertices=[]
    for x,y in OUTLINES[shape]:
        p=add(base,add(mul(side,x*size),mul(t,y*size)))
        # A shallow longitudinal cup, not a rigid flat cutout.
        p=add(p,mul(normal,.07*size*math.sin(math.pi*y)))
        vertices.append(p)
    mesh.append(vertices,triangulate(OUTLINES[shape]))

def build(species,seed=42):
    p=PRESETS[species]; h=p["h"]; radius=p["w"]*.5
    wood,leaves=MeshData(),MeshData()
    trunk=[(.18*math.sin(i*.3),.12*math.sin(i*.5),h*i/24) for i in range(25)]
    trunk_r=[max(.018,p["dbh"]*.5*(1-i/24)**.8)*(1.30 if i==0 else 1)
             for i in range(25)]
    tube(wood,trunk,trunk_r,10)
    for a in range(p["leaders"]):
        r=rng_for(seed,f"scaffold/{a}")
        fraction=p["clear"]+(0.92-p["clear"])*(a+.5)/p["leaders"]
        index=min(23,max(1,round(fraction*24)))
        start=trunk[index]
        az=a*2.3999632297+r.uniform(-.26,.26)
        radial=(math.cos(az),math.sin(az),0)
        crown_t=(start[2]/h-p["clear"])/(1-p["clear"])
        reach=radius*max(.18,math.sin(math.pi*max(.10,min(.94,crown_t))))
        end=add(start,mul(radial,reach*r.uniform(.8,1.05)))
        end=(end[0],end[1],min(h*.98,start[2]+h*p["rise"]*r.uniform(.65,1)))
        path=curved_path(start,end,mul(radial,-reach*.13))
        base_r=trunk_r[index]*.42
        tube(wood,path,[max(.01,base_r*(1-i/7)**.85) for i in range(8)],8)
        for b in range(5):
            q=rng_for(seed,f"scaffold/{a}/secondary/{b}")
            s=path[3+b%4]
            direction=unit((radial[0]+q.uniform(-.9,.9),
                            radial[1]+q.uniform(-.9,.9),q.uniform(.2,.9)))
            e=add(s,mul(direction,reach*q.uniform(.22,.40)))
            secondary=curved_path(s,e,(0,0,reach*.06),5)
            sr=max(.007,base_r*(1-(3+b%4)/7)**.85*.40)
            tube(wood,secondary,[max(.004,sr*(1-i/5)) for i in range(6)],5)
            for c in range(4):
                q=rng_for(seed,f"scaffold/{a}/secondary/{b}/twig/{c}")
                s=secondary[2+c%3]
                d=unit(add(direction,(q.uniform(-.8,.8),q.uniform(-.8,.8),.25)))
                e=add(s,mul(d,q.uniform(.45,.9)))
                twig=curved_path(s,e,(0,0,.08),5)
                tube(wood,twig,[.004*(1-i/6) for i in range(6)],4)
                u,v=basis(d)
                for j in range(1,6):
                    angle=j*2.3999632297+q.uniform(-.2,.2)
                    side=add(mul(u,math.cos(angle)),mul(v,math.sin(angle)))
                    leaf_dir=unit(add(mul(d,.35),side))
                    leaf(leaves,twig[j],leaf_dir,p["leaf"]*q.uniform(.85,1.15),
                         p["shape"],q.uniform(-.8,.8))
    return wood,leaves

def validate(mesh):
    assert mesh.vertices and mesh.faces
    assert all(math.isfinite(v) for p in mesh.vertices for v in p)
    for face in mesh.faces:
        assert len(face)==3 and len(set(face))==3
        assert all(0<=i<len(mesh.vertices) for i in face)
        a,b,c=(mesh.vertices[i] for i in face)
        assert length(cross(sub(b,a),sub(c,a)))>1e-12

def check():
    for name in PRESETS:
        first=build(name,42); second=build(name,42); other=build(name,43)
        for m in first: validate(m)
        assert all(a.vertices==b.vertices and a.faces==b.faces for a,b in zip(first,second))
        assert first[0].vertices != other[0].vertices
        for shape in OUTLINES:
            assert len(triangulate(OUTLINES[shape]))==len(OUTLINES[shape])-2
        print(name,{"wood_triangles":len(first[0].faces),
                    "leaf_triangles":len(first[1].faces)})
    print("PASS: finite coordinates, valid triangles, repeatable seeds, distinct variants")

def emit_blender():
    import bpy
    collection=bpy.data.collections.new("PA_Tree_Architecture_Study")
    bpy.context.scene.collection.children.link(collection)
    def material(name,color):
        m=bpy.data.materials.new(name); m.use_nodes=True
        bsdf=m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value=(*color,1)
        bsdf.inputs["Roughness"].default_value=.78
        m.diffuse_color=(*color,1)
        m.use_backface_culling=False
        return m
    bark=material("PA_Study_Bark",(.16,.12,.08))
    foliage=material("PA_Study_Leaf",(.06,.20,.035))
    for index,species in enumerate(PRESETS):
        for label,data,mat in zip(("Wood","Leaves"),build(species), (bark,foliage)):
            validate(data)
            mesh=bpy.data.meshes.new(f"{species}_{label}")
            mesh.from_pydata(data.vertices,[],data.faces); mesh.update()
            obj=bpy.data.objects.new(mesh.name,mesh); collection.objects.link(obj)
            obj.location.x=index*34
            obj.data.materials.append(mat)
            obj["species_id"]=species; obj["seed"]=42
            obj["recipe_version"]="architecture_study_1"
            for polygon in mesh.polygons: polygon.use_smooth=(label=="Wood")
    print("Created architecture studies. Select collection objects and Frame Selected.")

if __name__=="__main__":
    check() if "--check" in sys.argv else emit_blender()
```

### Validation performed for this document

The embedded script was executed in ordinary Python with `--check`. The generated mesh data passed finite-coordinate, triangle-index, nondegenerate-triangle, deterministic-seed, and changed-seed checks for all three presets.

| Preset | Wood triangles | Leaf triangles | Total |
|---|---:|---:|---:|
| White oak | 9,484 | 15,400 | 24,884 |
| Tuliptree | 13,336 | 10,000 | 23,336 |
| Sycamore | 9,484 | 7,000 | 16,484 |

These are **generated triangle counts**, not measured render performance. The Blender-only scene creation path was not executed because Blender is unavailable in the authoring environment. No Blender render or Godot import has been certified by these checks. The self-check also does not prove collision-free branches, manifold junctions, accurate botanical form, or export correctness.

## 11. Turn the study into a production tree

### Step 1 — Approve a leaf-off silhouette

Pick one local reference specimen and one growth context. Match total height, crown spread, crown-start height, major fork positions, and the direction of the largest limbs. Use a 1.8 m reference human or another known scale object. Keep the camera and lighting fixed during comparisons.

For an open-grown white oak, suppress a visually excessive central spike and develop several heavy scaffold systems. For a tuliptree, preserve the tall leader and high crown. For a sycamore, reduce visual competition from tiny branches so the large divisions remain readable.

### Step 2 — Refine attachments and root flare

Use a connected mesh construction or a high-resolution union followed by controlled retopology for hero forks. Voxel-remeshing the entire tree can erase small limbs and inflate polygons; limit it to the junction work that needs it. Preserve branch IDs or transfer them back to the rebuilt mesh if wind and UV tools depend on them.

### Step 3 — Build one excellent foliage unit

Create a twig with a botanically sensible set of leaves. Render and inspect it from front, back, side, and below. For a gameplay asset, bake a small collection of these into cards or use a compact mesh spray. Give each unit a clear attachment root and local forward axis.

### Step 4 — Fill the crown through branch systems

Increase fine growth and foliage units within each major crown lobe. Keep some interior wood visible and retain the gaps approved in silhouette review. Density is a per-branch and per-lobe control. Do not solve every thin-looking area by globally enlarging leaves.

### Step 5 — Add species materials

Match lower trunk, upper trunk, and younger branch references. Use physical texture scale. The sycamore's upper wood should become a visual identifier; the beech's trunk should remain smooth; the oak's crown should not depend on bark alone to be identifiable.

### Step 6 — Make correlated variants

Create 3–6 useful structural variants before adding dozens of random seeds. Include forest/edge/open forms where needed. Reuse textures, but move forks, crown lobes, and missing branches coherently. Avoid mirroring recognizably directional damage or identical pruning scars everywhere.

### Step 7 — Bake and export

Keep the source graph and detailed foliage source editable. Export a delivery copy with approved materials and topology. Store the recipe and generator version alongside it.

## 12. LOD and performance for game use

These are **initial content budgets**, to be replaced by measurements in the actual target game:

| Role | Approximate total triangles per tree | Texture strategy | Main priority |
|---|---:|---|---|
| Close hero | 20k–60k | Shared species atlas plus selected close bark detail | Silhouette, forks, trunk scale, close foliage. |
| Normal gameplay | 6k–20k | Shared bark/foliage atlases | Readable crown, controlled overdraw, stable shadows. |
| Mid-distance | 1k–6k | Reduced clusters and shared textures | Preserve species silhouette and major gaps. |
| Far stand | A few hundred to roughly 1.5k, or impostor | Coarse mesh or directional impostor | Stable outline, color mass, transition quality. |

Triangle count is only one cost. Transparent pixels, shadow passes, material changes, texture memory, instancing, and visible tree count can dominate. Test a representative stand from the worst plausible camera, not a single isolated tree.

### LOD must remove the right detail

- Keep a sycamore's pale major branches.
- Keep an elm's arching vase.
- Keep a dogwood's shelves and their gaps.
- Keep a pine's branch-tier character and irregular top.
- Remove invisible twigs, merge small foliage units, and simplify interior geometry first.
- Do not apply decimation blindly to leaf cards: it can break silhouettes, UV borders, and foliage coverage.
- Adjust coverage after each reduction; fewer polygons should not unexpectedly halve the apparent leaf mass.

Use screen-space importance rather than one fixed distance for every tree. Validate transitions at the game's actual field of view, resolution, exposure, and temporal antialiasing settings.

### Wind and collision

Author wind data that distinguishes trunk stiffness, branch sway, and leaf flutter. Nearby leaves on one branch should share some motion. A single sine offset based only on world position can make the entire tree resemble rubber.

If exporting wind weights through vertex colors or custom attributes, define the channel contract and verify the engine importer preserves it. Do not assume Blender attributes or custom shader logic automatically survive glTF. Turn off unintended vertex-color tinting when those channels contain data.

Use simple trunk and selected major-limb collision for most trees. Individual leaves rarely need collision. Collision and visual geometry should be separate delivery decisions.

## 13. Export and Godot handoff

Blender's glTF exporter translates supported data into glTF; it does not carry arbitrary Blender material logic into the engine. Bake procedural appearance to supported textures and material settings. [B5]

For your Godot workflow, treat the installed engine's importer and renderer as the final authority. This guide does not assume that every feature in the latest documentation behaves identically in a specific Godot 4.7 build.

### Delivery checklist

1. Use metres consistently and apply intended object transforms on the delivery copy.
2. Place the tree origin at ground contact; check actual bounding dimensions.
3. Preserve the approved root flare at terrain intersection.
4. Export evaluated mesh geometry where the chosen path requires it.
5. Confirm two-sided foliage/back-face treatment and alpha cutoff after import.
6. Verify texture color space and normal-map direction.
7. Confirm materials, LOD configuration, collision, and shadow behaviour in-engine.
8. Check wind-channel preservation and animation bounds if wind is used.
9. Test noon, overcast, low sun, night, and bright backlighting.
10. Open a fresh project/import to ensure the result does not depend on unsaved Blender state.

### Batch-generation manifest

```json
{
  "asset_id": "pa_quercus_alba_open_mature_s42017",
  "species_id": "quercus_alba",
  "recipe_version": "quercus_alba_open_mature_001",
  "generator_version": "tree_factory_001",
  "blender_version": "record_actual_build_here",
  "seed": 42017,
  "growth_context": "open_grown",
  "season": "summer",
  "measured_bounds_m": null,
  "measured_triangles_by_lod": null,
  "material_count": null,
  "export_format": "glb",
  "checks": {
    "geometry_arrays": "pending",
    "blender_render": "pending",
    "engine_import": "pending",
    "species_review": "pending",
    "performance_scene": "pending"
  }
}
```

Fill measured fields from the exported asset rather than copying target budgets. A filename containing `native` is not proof of local nativity; store locality evidence in the placement/species database from the companion guide.

## 14. Put the right trees into the level

Build a placement graph or masks for water, drainage, slope, soil/substrate, existing canopy, land use, and maintained clearances. Filter species before applying random weights.

For a Delco creek scene, a useful sequence is:

1. Establish the stream, floodplain, higher terrace, and dry slope.
2. Put wet-compatible candidates near the bank and use a different pool higher up.
3. Place a few large landmark trees from site logic.
4. Add secondary canopy trees with variable spacing and coherent local groups.
5. Grow crowns toward available space; avoid identical circular personal-space gaps around every trunk.
6. Populate understory where shade/moisture allow it.
7. Add younger recruitment, occasional deadwood, and appropriate litter.
8. Apply path, fence, building, and maintenance constraints.
9. Review visibility and gameplay routes, then make explicit authored adjustments.

A useful conceptual selection model is:

```text
candidate_weight = regional_weight
                 * habitat_suitability
                 * light_suitability
                 * historical_presence_factor
                 * land_use_factor
```

Use hard exclusions for impossible combinations. A multiplication of soft weights must not occasionally put a mature upland oak in open water. These factors are authored scores unless calibrated to an ecological model.

Natural woodland spacing should respond to age, gaps, and competition. Planted streets can have deliberate rows, shared nursery cohorts, and pruning patterns. Randomizing those rows into a forest would erase the human planting history.

## 15. Review sheet and failure diagnosis

| Check | Pass evidence | Common failure and correction |
|---|---|---|
| Species silhouette | Distinct identity in flat black | Same sphere for every species: change scaffold and crown architecture first. |
| Botanical leaf unit | Correct outline, arrangement, and connected parts | Walnut leaflets float independently: build the rachis and attachment. |
| Scale | Measured height, width, DBH, leaf size | Giant leaves compensate for missing twigs: fix foliage hierarchy. |
| Crown structure | Foliage follows branches and preserves gaps | Uniform clumps hide weak skeleton: review without foliage. |
| Junctions | Major forks have convincing continuity | Tubes intersect like plumbing: add collars or rebuild visible junctions. |
| Bark | Direction and physical scale fit species/age | Same stretched noise on all trunks: use bark-specific structure and UV scale. |
| Ground contact | Root flare enters terrain | Cylinder stuck into ground or floating roots: fit collar to terrain. |
| Variation | Different histories and coherent forms | Random rotation only: vary forks, lobes, age, and context. |
| Season | Leaves, fruit, flowers, and litter agree | Summer crown plus unrelated spring bloom: use one seasonal state. |
| LOD | Identity and canopy coverage survive | Transition becomes bald or changes species: protect major masses. |
| Lighting | Materials hold up in several conditions | Leaf emission or baked sun shadows: correct the material model. |
| Placement | Species matches habitat and land use | Every native species everywhere: filter by site before sampling. |

For each priority tree, save front/side/top silhouettes, a leaf-off view, a trunk close-up, a foliage close-up, and an in-engine gameplay view. Human species review remains necessary; a geometry validator cannot tell whether an oak looks like an oak.

## 16. Suggested implementation order

1. **Skeleton milestone:** three distinct leaf-off trees—white oak, tuliptree, sycamore—with measured bounds and stable seeds.
2. **Species milestone:** correct leaf units, bark treatments, and crown coverage for those three.
3. **Delivery milestone:** baked materials, LODs, collision, and verified target-engine import.
4. **Variation milestone:** forest/edge/open forms and a small set of strong structural variants.
5. **Expansion milestone:** maple and beech; then dogwood, walnut, cherry; then separate conifer modules.
6. **Regional milestone:** habitat-driven Delco/Philly placement using the companion guide's palette and evidence fields.

The first milestone should produce clearly different architecture. If it does not, adding more species names or random seeds will multiply the same mistake.

## 17. References and verification boundaries

- **B1 — Blender Python API: Mesh.** [Mesh data and `from_pydata`](https://docs.blender.org/api/current/bpy.types.Mesh.html?highlight=transform). API foundation for direct mesh construction. The starter's generation logic is original example code.
- **B2 — Runions, Lane & Prusinkiewicz (2007), Modeling Trees with a Space Colonization Algorithm.** [Authors' paper page](https://algorithmicbotany.org/papers/colonization.egwnp2007.html). Research foundation for attractor-based growth.
- **B3 — Blender 4.5 LTS Manual: Instances.** [Instance concepts](https://docs.blender.org/manual/en/4.5/modeling/geometry_nodes/instances.html); [Instance on Points](https://docs.blender.org/manual/en/4.5/modeling/geometry_nodes/instances/instance_on_points.html).
- **B4 — Blender Manual: Realize Instances.** [Node reference](https://docs.blender.org/manual/en/4.5/modeling/geometry_nodes/instances/realize_instances.html). Consult the installed-version manual if sockets differ.
- **B5 — Blender glTF documentation and official exporter.** [glTF manual](https://docs.blender.org/manual/en/4.2/addons/import_export/scene_gltf2.html); [Khronos exporter repository](https://github.com/KhronosGroup/glTF-Blender-IO). The cited 4.2 page supports the material/export concepts; check options against the installed build.
- **B6 — Godot: StandardMaterial3D and ORMMaterial3D.** [Official material documentation](https://docs.godotengine.org/en/stable/tutorials/3d/standard_material_3d.html). Transparency and material behaviour are renderer/version dependent.
- **Botanical references:** the species-linked university extension pages and regional sources in [the companion tree guide](PA_NATIVE_TREES_PHILLY_DELCO.md). Use these to judge the species traits; the numeric generator ranges are artistic starting points.

**Validated:** embedded Python syntax and generated mesh-array checks for the three example presets. **Not validated here:** execution inside Blender, rendered appearance, botanical fidelity of finished assets, GLB export/import, or runtime performance. Complete the review milestones in the actual production environment before treating generated trees as approved assets.
