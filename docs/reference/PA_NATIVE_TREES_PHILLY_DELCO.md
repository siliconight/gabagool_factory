---
title: Pennsylvania Native Trees — Philadelphia, Delaware County, and Regional Palettes
version: 1.0
date: 2026-10-10
primary_region: southeastern Pennsylvania
primary_counties: [Philadelphia, Delaware]
audience: [environment artists, level designers, procedural tool developers]
units: metric
companion: BLENDER_SCRIPTING_PA_TREES.md
---

# Pennsylvania native trees: a regional and visual guide

This guide explains which native trees to use for Pennsylvania environments, where they belong, and what makes them recognizable. Philadelphia and Delaware County—Delco—receive the most attention. Other county palettes provide a starting point for changing the landscape as a setting moves across the state.

The intended use is believable game environments and procedural asset creation. The botanical descriptions also work as an identification and reference-gathering guide. The companion [Blender scripting guide](BLENDER_SCRIPTING_PA_TREES.md) translates these features into geometry, materials, placement rules, and repeatable scripts.

## 1. How to interpret the information

Three different statements must stay separate:

| Statement | What it establishes |
|---|---|
| A species is native to Pennsylvania | It belongs naturally somewhere in the state. |
| A species is recorded in a county | A source documents its occurrence there; a planted specimen alone does not establish local nativity. |
| A species fits a particular site | Its soil, moisture, exposure, and disturbance requirements match that location. |

County borders do not create vegetation boundaries. A dry hillside and a wet floodplain in the same township can support very different trees.

**Evidence labels used here:**

- **Documented example:** a named source describes trees at a particular place. This is historical or published evidence, not a new field survey.
- **Habitat palette:** an editorial selection of native species suitable for depicting that environment. It is not a verified list of every species occurring in the county.
- **Localized addition:** appropriate for a specific habitat or confirmed reference site, rather than a default across the region.

The species profiles give **approximate working size ranges for ordinary mature assets**, not biological limits, champion-tree dimensions, or a formula relating height to age. Forest trees can be taller and narrower; open-grown trees can be shorter and wider. Diameter at breast height, abbreviated **DBH**, means trunk diameter measured about 1.37 m above ground. Crown spread means diameter, not radius.

Sources were checked on October 10, 2026. Older inventories remain valuable descriptions of habitat, but they should not be read as a census of trees still alive today.

## 2. What makes Philadelphia and Delco look like themselves

Start with a deciduous hardwood landscape. Use substantial oaks, tall tuliptrees, rounded maples, smooth gray beeches, and conspicuous pale sycamores beside water. Add smaller trees below them. Reserve conifer-heavy scenery for an appropriate site, planting history, or different part of Pennsylvania.

The same species should change form with its surroundings:

| Growing situation | Visible result |
|---|---|
| Closed woodland | Long relatively clear trunk; smaller high crown; dead or missing lower branches; crowns competing for openings. |
| Woodland edge | Foliage extends toward the open side; lower limbs survive there; the crown is uneven for a reason. |
| Open lawn or cemetery | Broad crown, larger low limbs, more visible root flare, often room for a distinctive silhouette. |
| Street or parking edge | Raised crown, pruning scars, constrained roots, occasional utility clearance, and a deliberately chosen planting position. |
| Creek bank | Flood-compatible species, sometimes exposed roots or leaning stems, and foliage exploiting the opening above water. |
| Abandoned field | Cohorts of younger trees, irregular recruitment patches, persistent gaps, and surviving older boundary trees. |

These are art-direction rules inferred from growth conditions. Do not give every tree every defect. A healthy park tree and a damaged stream-bank tree should tell different stories.

### Philadelphia: choose the part of the city first

| Environment | Habitat palette | Composition and form |
|---|---|---|
| Wissahickon/Fairmount-style wooded slopes | Tuliptree, white oak, northern red oak, American beech, red maple, sweet birch; dogwood and hornbeam below | Tall canopy, irregular gaps, exposed trunks, slopes, and a separate understory. Keep hemlock to a cool, locally supported pocket. |
| Drier upland woodland | White oak, black oak, chestnut oak, pignut hickory, sassafras | Coarser branching, more open crowns on poor sites, leaf litter, and shrubs where light reaches the ground. |
| Schuylkill/Delaware tributary floodplain | American sycamore, silver maple, boxelder, black willow, eastern cottonwood, American elm | Distinguish the wet bank from the higher terrace. Large spreading trees alternate with younger flood-disturbed patches. |
| Low Coastal Plain woodland | Red maple, sweetgum, pin oak, swamp white oak, blackgum | Flat or gently graded ground, wet depressions, and mixtures reflecting drainage. Willow oak and sweetbay are localized additions. |
| Rowhouse street, schoolyard, or planted park | Native candidates include red maple, northern red oak, swamp white oak, hackberry, and serviceberry | This is a planted palette. Select cultivar, planting age, available soil, and pruning history separately. Actual streets contain many introduced species. |
| Vacant parcel next to water or a wooded rail edge | Boxelder, cottonwood, black cherry, red maple, sassafras, with habitat restrictions | Uneven age structure and colonization from nearby seed sources. A native-only palette does not reproduce every real vacant lot. |

**Documented anchor:** Philadelphia's 2008 Natural Heritage Inventory describes tuliptree-dominated uplands and remnant Coastal Plain forest containing sweetgum and oaks. Use that as support for the broad contrast between upland woods and lowland forest, not as a species-by-species current inventory. [R1]

### Delaware County: a compact county with several different landscapes

| Environment | Habitat palette | Composition and form |
|---|---|---|
| Crum/Ridley/Darby creek valley woodland | Tuliptree, white oak, northern red oak, beech, red maple, hickories | High deciduous canopy with a mix of clear trunks and branching edge trees. Keep streamside species on the lower ground. |
| Stream bank and floodplain | Sycamore, silver maple, boxelder, black willow, green ash as a time-sensitive component | Pale sycamore limbs are a strong landmark. Add flood effects selectively; a creek valley is not uniformly swampy. |
| Western Delco uplands and older woodlots | White, red, black, and chestnut oaks; pignut hickory; blackgum; sassafras | Dry ridges should differ from richer lower slopes. Repeated species are appropriate; identical tree assets are conspicuous. |
| Chester/Tinicum/lower Darby lowlands | Red maple, sweetgum, pin oak, willow, cottonwood; swamp white oak on suitable ground | Separate wooded margins from open marsh. Open water and tidal marsh should remain open where the reference requires it. |
| Old farm edge, cemetery, large residential lot | White oak, black walnut, black cherry, red maple, eastern redcedar | Broad open-grown trees and remnants of old boundaries; young replacement trees can occupy gaps. |
| Serpentine habitat or a confirmed barrens reference | Pitch pine, eastern redcedar, sassafras, and locally documented scrub oaks | Sparse trees and open vegetation on unusual substrate. This is a special habitat, not the appearance of every neglected lot. |

**Documented Delco example:** Scott Arboretum's Crum Woods account records tuliptree, pignut and bitternut hickory, white ash, chestnut oak, sycamore, white pine, hemlock, blackgum, beech, red oak, and red/silver maples. Its separate woodland account also identifies white oak. These observations establish a useful local reference set; they do not imply equal abundance. [R3–R4]

The county inventory and watershed material provide the larger habitat context. [R2, R5] Hemlock is particularly worth treating as a local ravine component, rather than spreading it throughout Delco.

## 3. How to change the palette in other counties

These are **habitat-based regional starting palettes**, assembled from the cited forest-community descriptions and individual species ecology. They are not exhaustive county checklists. For a named real site, follow the verification procedure in section 9.

| County or county group | Landscape emphasis | Starting native palette and change from Philly/Delco |
|---|---|---|
| Chester | Piedmont woods, farms, stream valleys; local serpentine sites | Oaks, tuliptree, beech, red maple, hickories; walnut and cherry at field edges. Use the barrens palette only on appropriate substrate. |
| Montgomery | Piedmont woods, developed valleys, Schuylkill tributaries | Similar core to Delco. Increase floodplain species beside water; distinguish planted suburbia from remnant woods. |
| Bucks | Delaware lowlands, Piedmont and more rugged northern terrain | Sycamore/silver maple/river birch at suitable waterways; oaks, tuliptree, beech, maple on uplands; localized hemlock in cool terrain. |
| Lancaster | Farm landscape, wooded slopes, Susquehanna tributaries | White/red oaks, hickories, walnut, cherry, tuliptree; sycamore and silver maple along waterways. Mature boundary trees are useful landmarks. [R6] |
| York and southern Dauphin | Valleys, ridges, river corridors | Mixed oaks and hickories on uplands; maple/tuliptree on richer sites; sycamore, silver maple, and willow near water. |
| Berks, Lehigh, Northampton | Valley floors meeting wooded ridges | Make a visible transition from rich lower-slope hardwoods to chestnut/white/black oak on drier ridges. |
| Monroe and Pike | Cooler uplands, ravines, wetland complexes | Add hemlock, white pine, yellow birch, beech, and sugar maple. Keep oak woods on suitable dry slopes; avoid making all forest evergreen. [R8] |
| Centre | Ridge-and-valley relief and plateau margins | Oak ridges can sit near cool hemlock-hardwood ravines. Terrain and exposure should control the transition inside one level. |
| Tioga and Potter | Northern hardwood and hemlock landscapes | Give sugar maple, beech, yellow birch, black cherry, and hemlock greater emphasis than in a generic Delco level. [R8] |
| McKean and Warren | Northern hardwood and black-cherry country | Build taller forest-grown cherry assets; combine with maple, beech, birch, and locally appropriate hemlock. [R7–R8] |
| Forest and Clarion | Wooded plateau and river valleys | Hemlock and white pine can become major visual components. Cook Forest is a documented reference for exceptionally mature examples, not the default size of every stand. [R9] |
| Allegheny and Fayette | Rich woods, dissected hills, developed river valleys | Oak, beech, sugar maple, tuliptree, cherry, walnut; pawpaw on suitable rich sites. A western palette can justify additions absent from the core Delco kit. |
| Somerset | Higher, cooler terrain plus varied slopes | Increase northern-hardwood character on cool sites; retain oak communities where conditions fit. Do not substitute an alpine conifer forest. |
| Erie and Crawford | Northwestern hardwoods and glaciated wet ground | Beech/sugar maple on suitable uplands; wetland-specific trees in wet depressions. Bog conifers require a bog reference, not just a northern county. [R7] |

The principal statewide contrast is southern mixed-oak country versus northern hardwood/conifer mixtures, with riparian, Coastal Plain, and unusual geological habitats layered on top. DCNR and PNHP describe these communities more precisely than county boundaries do. [R7–R8, R10–R11]

## 4. Species profiles: the main asset library

**Reading the ranges:** `H` = total height in metres; `W` = crown spread in metres. They are practical mature-asset ranges assembled for visual production. Use photographs to select a particular specimen inside or outside them. The species links contain botanical descriptions and reference photographs; they do not establish occurrence in every county named above.

### Oaks

#### 01 — White oak · *Quercus alba* · `quercus_alba`

- **Site:** Well-drained woodland, slopes, large old lawns; avoid permanently wet ground. H 20–30; W 15–28 in open-grown examples.
- **Recognition:** Heavy spreading limbs and a broad, irregular crown. Pale gray bark breaks into plates. Leaves have rounded lobes without bristle tips; autumn often becomes muted red-brown.
- **Asset instruction:** Keep several large, readable limb arcs and gaps between them. A woodland version needs a higher crown. Use rounded-lobed leaves, not a generic maple atlas.
- **Reference:** [NC State: white oak](https://plants.ces.ncsu.edu/plants/quercus-alba/).

#### 02 — Northern red oak · *Quercus rubra* · `quercus_rubra`

- **Site:** Upland woods and reasonably moist, drained slopes. H 20–30; W 12–24.
- **Recognition:** Stout ascending limbs and a large crown. Mature bark can show long, lighter, relatively flat ridges. Leaves have pointed, bristle-tipped lobes and less extreme cutting than pin oak.
- **Asset instruction:** Preserve a stronger upward structure than an old open-grown white oak. Long bark ridges should follow the trunk and limbs. Autumn red is variable, not a mandatory saturated scarlet.
- **Reference:** [NC State: northern red oak](https://plants.ces.ncsu.edu/plants/quercus-rubra/).

#### 03 — Black oak · *Quercus velutina* · `quercus_velutina`

- **Site:** Dry to moderately moist upland woods, ridges, and slopes. H 15–25; W 10–20.
- **Recognition:** Dark, coarse mature bark; irregular crown; pointed-lobed leaves, often glossy above. Yellow inner bark is an identification feature, not an exposed surface color.
- **Asset instruction:** Make bark darker and more blocky than white oak. Avoid turning every black oak into a severely twisted dead tree. Place it with other upland hardwoods.
- **Reference:** [NC State: black oak](https://plants.ces.ncsu.edu/plants/quercus-velutina/).

#### 04 — Chestnut oak · *Quercus montana* · `quercus_montana`

- **Site:** Rocky, acidic, dry slopes and ridges. H 15–25; W 10–20.
- **Recognition:** Thick deeply ridged bark and leaves with rounded teeth around an elongated outline. The leaf does not have white oak's deep fingerlike lobes.
- **Asset instruction:** Use heavy bark relief and broad shallow leaf teeth. Poor rocky sites can justify a shorter, uneven crown. Older references may call this *Quercus prinus*; retain the current recipe ID above.
- **Reference:** [NC State: chestnut oak](https://plants.ces.ncsu.edu/plants/quercus-montana/).

#### 05 — Pin oak · *Quercus palustris* · `quercus_palustris`

- **Site:** Moist low ground and planted landscapes with suitable soil. H 18–25; W 9–16.
- **Recognition:** A relatively strong central trunk; lower branches often descend, middle branches extend outward, upper branches rise. Leaves have deep sinuses and narrow pointed lobes.
- **Asset instruction:** Drive branch elevation with height. This three-zone structure matters more than adding random crookedness. Do not prune away every low limb in the natural form.
- **Reference:** [NC State: pin oak](https://plants.ces.ncsu.edu/plants/quercus-palustris/).

#### 06 — Swamp white oak · *Quercus bicolor* · `quercus_bicolor`

- **Site:** Low woods and seasonally wet ground. H 15–24; W 15–24.
- **Recognition:** Broad crown, substantial limbs, shallow rounded leaf lobes or teeth, and pale leaf undersides. Branch bark can peel; mature trunk bark becomes furrowed.
- **Asset instruction:** Use a broad oak framework with leaves visibly different from white oak. A foliage material can reveal paler undersides during motion. Do not treat its name as permission to submerge every trunk.
- **Reference:** [NC State: swamp white oak](https://plants.ces.ncsu.edu/plants/quercus-bicolor/).

### Maples and large floodplain trees

#### 07 — Red maple · *Acer rubrum* · `acer_rubrum`

- **Site:** Broad habitat range, including moist woods and wet depressions. H 12–24; W 8–16.
- **Recognition:** Rounded to oval crown with ascending branches; opposite leaves and buds. Leaves usually have three to five main lobes with toothed margins. Autumn can be yellow, orange, red, or mixed.
- **Asset instruction:** Build a branching network beneath the canopy instead of a single green sphere. Pair leaf attachment on fine twigs, while allowing older branches to be missing. Red spring flowers are a separate seasonal detail.
- **Reference:** [NC State: red maple](https://plants.ces.ncsu.edu/plants/acer-rubrum/).

#### 08 — Silver maple · *Acer saccharinum* · `acer_saccharinum`

- **Site:** Floodplains, waterways, and older planted sites. H 18–30; W 15–25.
- **Recognition:** Large spreading, often divided crown; long limbs; deeply cut leaves with pale silvery undersides. Older bark becomes loose and shaggy.
- **Asset instruction:** Use a more open, sweeping silhouette than red maple. Let some tips descend. Show contrasting leaf backs without painting the whole canopy silver. Damage or cavities need a specimen-specific reason.
- **Reference:** [NC State: silver maple](https://plants.ces.ncsu.edu/plants/acer-saccharinum/).

#### 09 — Sugar maple · *Acer saccharum* · `acer_saccharum`

- **Site:** Richer well-drained woods and cooler sites; a stronger regional component farther north. H 20–30; W 12–22.
- **Recognition:** Dense rounded crown; opposite leaves with broad lobes and comparatively smooth margins between major points. Mature bark becomes furrowed and plate-like.
- **Asset instruction:** Differentiate the leaf outline from red maple. Use an oval crown with substantial interior shade and controlled gaps. Autumn can include yellow, orange, and red on different trees or crown areas.
- **Reference:** [NC State: sugar maple](https://plants.ces.ncsu.edu/plants/acer-saccharum/).

#### 10 — Boxelder · *Acer negundo* · `acer_negundo`

- **Site:** Floodplains, stream edges, and disturbed moist ground. H 8–18; W 8–16.
- **Recognition:** An irregular, often low-forking maple with compound leaves, commonly three to seven leaflets. It should not look like a conventional maple-leaf tree.
- **Asset instruction:** Allow several uneven stems and long outward limbs. Attach compound leaves in opposite pairs; keep leaflets connected to a rachis. Useful for scruffy creek margins, with condition varied by site.
- **Reference:** [NC State: boxelder](https://plants.ces.ncsu.edu/plants/acer-negundo/).

#### 11 — American sycamore · *Platanus occidentalis* · `platanus_occidentalis`

- **Site:** Streams, floodplains, and spacious planted grounds. H 22–35; W 15–28.
- **Recognition:** Massive pale upper trunk and limbs, with irregular cream, olive, tan, and gray bark patches. Large leaves have broad angular lobes. Spherical seed heads can persist into winter.
- **Asset instruction:** Branching and pale upper wood must read from a distance. Keep older lower bark rougher and darker. Avoid a white trunk covered in evenly distributed camouflage spots. Distinguish it from planted London plane.
- **Reference:** [NC State: American sycamore](https://plants.ces.ncsu.edu/plants/platanus-occidentalis/).

#### 12 — Eastern cottonwood · *Populus deltoides* · `populus_deltoides`

- **Site:** Sunny river margins, floodplain openings, and disturbed alluvium. H 20–35; W 12–25.
- **Recognition:** Tall substantial trunk, coarse mature bark, and an open broad crown. Triangular leaves create flickering movement; their flattened petioles matter to animation.
- **Asset instruction:** Use large-scale structure with relatively fine moving foliage. Include cohorts of younger stems where disturbance created an opening. This is not a weeping willow substitute.
- **Reference:** [NC State: eastern cottonwood](https://plants.ces.ncsu.edu/plants/populus-deltoides/); [USFS species review](https://research.fs.usda.gov/feis/species-reviews/popdel).

#### 13 — Black willow · *Salix nigra* · `salix_nigra`

- **Site:** Wet banks, low floodplain ground, and marsh margins. H 10–24; W 10–20.
- **Recognition:** Narrow leaves, dark fissured bark, crooked or multiple stems, and a loose irregular crown. Some branchlets droop, but the silhouette is not an ornamental weeping curtain.
- **Asset instruction:** Combine uneven trunks with fine flexible peripheral growth. Use narrow leaf units and a wet-site placement mask. Keep a planted weeping-willow asset in a separate category.
- **Reference:** [NC State: black willow](https://plants.ces.ncsu.edu/plants/salix-nigra/).

### Distinctive woodland canopy trees

#### 14 — Tuliptree / tulip poplar · *Liriodendron tulipifera* · `liriodendron_tulipifera`

- **Site:** Rich, moist, well-drained woods and lower slopes. H 25–40; W 10–20.
- **Recognition:** Exceptionally tall straight woodland trunk, high crown, and distinctive leaves with a notched or squared-off tip. Autumn is principally yellow.
- **Asset instruction:** Preserve the long clear stem and an upright crown. Do not turn it into a short mushroom-shaped oak. Flowers belong among foliage and are far less conspicuous in a mature canopy than decorative blossoms on a small tree.
- **Reference:** [NC State: tuliptree](https://plants.ces.ncsu.edu/plants/liriodendron-tulipifera/).

#### 15 — American beech · *Fagus grandifolia* · `fagus_grandifolia`

- **Site:** Moist well-drained woodland. H 18–30; W 12–24.
- **Recognition:** Smooth gray bark, a substantial branching structure, long narrow pointed buds, and simple toothed leaves. Young trees and some lower branches retain dry tan leaves in winter.
- **Asset instruction:** Keep bark low-relief; large deep oak fissures destroy the identity. Build long lateral limbs and fine twigs. Winter leaf retention should be patchy and concentrated on appropriate growth, not the whole mature canopy.
- **Reference:** [NC State: American beech](https://plants.ces.ncsu.edu/plants/fagus-grandifolia/).

#### 16 — Sweet / black birch · *Betula lenta* · `betula_lenta`

- **Site:** Wooded slopes, ravines, and well-drained moist ground. H 15–23; W 8–15.
- **Recognition:** Dark young bark with horizontal lenticels, becoming rougher with age. Fine branchwork, toothed oval leaves, and yellow autumn color.
- **Asset instruction:** Start dark, not white. Put horizontal marks on young wood and change the bark with age. It must not share an untouched paper-birch material.
- **Reference:** [NC State: sweet birch](https://plants.ces.ncsu.edu/plants/betula-lenta/).

#### 17 — River birch · *Betula nigra* · `betula_nigra`

- **Site:** Eastern Pennsylvania waterways and moist low ground; also planted extensively. H 12–24; W 8–18.
- **Recognition:** Curling tan, cinnamon, and cream bark on younger trunks; older bases become darker and coarse. Fine crown texture and toothed leaves.
- **Asset instruction:** Add a limited number of peeling bark strips close to the camera. Natural specimens may have one trunk; the familiar three-stem nursery form is a planting choice, not a species requirement.
- **Reference:** [NC State: river birch](https://plants.ces.ncsu.edu/plants/betula-nigra/).

#### 18 — Shagbark hickory · *Carya ovata* · `carya_ovata`

- **Site:** Deciduous woods on suitable drained soils. H 20–30; W 10–18.
- **Recognition:** Long loose bark strips peeling away from the trunk. Compound leaves usually have five substantial leaflets. Crown often relatively narrow and elevated in woods; autumn yellow.
- **Asset instruction:** Spend close-view geometry on a few convincing raised bark plates. Do not turn every branch into a shaggy cylinder. Foliage should read as compound sprays rather than oversized individual blades.
- **Reference:** [NC State: shagbark hickory](https://plants.ces.ncsu.edu/plants/carya-ovata/).

#### 19 — Pignut hickory · *Carya glabra* · `carya_glabra`

- **Site:** Upland woods, including drier slopes. H 18–30; W 8–18.
- **Recognition:** Tall trunk and relatively narrow crown; compound leaves often with five leaflets. Bark is ridged with age but lacks shagbark's long hanging strips.
- **Asset instruction:** Share the compound-leaf construction method with shagbark, but give it a different bark and crown recipe. It is particularly useful beside oaks in a Delco upland kit.
- **Reference:** [NC State: pignut hickory](https://plants.ces.ncsu.edu/plants/carya-glabra/).

#### 20 — Blackgum / black tupelo · *Nyssa sylvatica* · `nyssa_sylvatica`

- **Site:** Various acidic woodland conditions, from uplands to wet margins. H 12–24; W 8–15.
- **Recognition:** Irregular or pyramidal crown, often with outward-spreading branches; small glossy simple leaves. Older bark develops blocky relief. Autumn can turn strong red relatively early.
- **Asset instruction:** Keep the leaf outline unlobed. Break the crown into uneven horizontal or oblique masses. Its autumn color can provide a localized accent rather than coloring the whole forest red.
- **Reference:** [NC State: blackgum](https://plants.ces.ncsu.edu/plants/nyssa-sylvatica/).

#### 21 — Sweetgum · *Liquidambar styraciflua* · `liquidambar_styraciflua`

- **Site:** Especially relevant to southeastern lowland/Coastal Plain references; also planted elsewhere. H 18–30; W 10–18.
- **Recognition:** Upright trunk and a pyramidal-to-rounded crown. Alternate star-shaped leaves distinguish it from opposite-leaved maples. Spiky seed balls are distinctive litter and winter details.
- **Asset instruction:** Preserve a star outline, alternate attachment, and a comparatively upright young form. Autumn may mix purple, red, orange, and yellow. Do not use it as a generic native for every PA county.
- **Reference:** [NC State: sweetgum](https://plants.ces.ncsu.edu/plants/liquidambar-styraciflua/).

#### 22 — Black walnut · *Juglans nigra* · `juglans_nigra`

- **Site:** Rich woods, stream terraces, old farms, and field edges. H 18–30; W 12–24.
- **Recognition:** Open irregular crown, dark furrowed bark, long compound leaves with many leaflets, and round green-husked fruits. Leaf loss can expose the framework comparatively early.
- **Asset instruction:** Model one compound leaf as a connected assembly or an atlas unit. A string of unrelated oval leaves floating around a branch will read incorrectly. Ground fruit is an optional close-view detail.
- **Reference:** [NC State: black walnut](https://plants.ces.ncsu.edu/plants/juglans-nigra/).

#### 23 — Black cherry · *Prunus serotina* · `prunus_serotina`

- **Site:** Woodland, secondary growth, and edges; particularly important in northern Pennsylvania forests. H 15–30; W 8–18.
- **Recognition:** Small elongated serrated leaves; young bark with horizontal lenticels; mature bark with dark curled flakes. Forest-grown trees can be straight and tall; open-grown trees spread.
- **Asset instruction:** Build separate young and mature bark states. Avoid ornamental-cherry blossom clouds: flowering is in slender clusters. Use small leaf units rather than broad maple-like sheets.
- **Reference:** [NC State: black cherry](https://plants.ces.ncsu.edu/plants/prunus-serotina/).

#### 24 — White ash · *Fraxinus americana* · `fraxinus_americana`

- **Site:** Richer well-drained woods. H 18–30; W 10–20.
- **Recognition:** Upright branching, opposite compound leaves, and interlacing diamond-like bark ridges on mature trunks. Leaf undersides tend to be paler.
- **Asset instruction:** Preserve opposite fine-branch/leaf logic and connected compound leaves. Healthy, declining, and dead versions belong to different time/site recipes. Do not assume a modern ash mortality pattern in a 1990s scene.
- **Reference:** [NC State: white ash](https://plants.ces.ncsu.edu/plants/fraxinus-americana/).

#### 25 — Green ash · *Fraxinus pennsylvanica* · `fraxinus_pennsylvanica`

- **Site:** Low ground, floodplain woods, and historic plantings. H 15–24; W 10–18.
- **Recognition:** Opposite compound foliage and ridged bark; often a less massive form than an old white ash. Autumn is commonly yellow.
- **Asset instruction:** A shared ash framework is reasonable, but distinguish site, leaf treatment, and growth form. Contemporary abundance and condition need local evidence because emerald ash borer has changed the landscape.
- **Reference:** [NC State: green ash](https://plants.ces.ncsu.edu/plants/fraxinus-pennsylvanica/).

#### 26 — American elm · *Ulmus americana* · `ulmus_americana`

- **Site:** Rich low woods, floodplains, and historic planted landscapes. H 18–30; W 15–25.
- **Recognition:** Vase-like architecture: major limbs rise and then arch outward into fine drooping peripheral twigs. Leaves have toothed margins and unequal bases.
- **Asset instruction:** Construct the vase before adding foliage. Disease history affects which age classes and specimens are plausible. Keep a full old specimen for a supported reference or intentional exceptional tree.
- **Reference:** [NC State: American elm](https://plants.ces.ncsu.edu/plants/ulmus-americana/).

#### 27 — Common hackberry · *Celtis occidentalis* · `celtis_occidentalis`

- **Site:** Rich woods, banks, and suitable urban plantings. H 12–24; W 10–20.
- **Recognition:** Rough gray bark with corky ridges or warts; a rounded irregular crown; simple pointed leaves with unequal bases.
- **Asset instruction:** Keep bark relief localized and corky rather than deeply channelled like oak. Use a branching crown with fine twig texture. It is a useful planted native candidate where a fictional streetscape needs variety.
- **Reference:** [NC State: hackberry](https://plants.ces.ncsu.edu/plants/celtis-occidentalis/).

### Smaller woodland and edge trees

#### 28 — Flowering dogwood · *Cornus florida* · `cornus_florida`

- **Site:** Woodland understory and edges; planted yards. H 4–9; W 4–9.
- **Recognition:** Layered horizontal branches, opposite leaves with curved side veins, and small blocky bark. The conspicuous spring display consists of bracts surrounding small flowers.
- **Asset instruction:** Create shallow branch shelves with visible spaces between them. Keep blossoms seasonal and attach them to branch tips. A round canopy with white speckles misses the identity.
- **Reference:** [NC State: flowering dogwood](https://plants.ces.ncsu.edu/plants/cornus-florida/).

#### 29 — American hornbeam / musclewood · *Carpinus caroliniana* · `carpinus_caroliniana`

- **Site:** Shaded moist woods and stream margins. H 5–10; W 5–10.
- **Recognition:** Smooth gray trunk with muscle-like fluting; fine twigs and toothed leaves. Often an irregular small tree rather than a miniature canopy giant.
- **Asset instruction:** Put broad shallow lobes into the trunk cross-section. A bark texture alone cannot produce the fluted silhouette. Keep the tree below the main canopy.
- **Reference:** [NC State: hornbeam](https://plants.ces.ncsu.edu/plants/carpinus-caroliniana/).

#### 30 — Sassafras · *Sassafras albidum* · `sassafras_albidum`

- **Site:** Woodland edges, old fields, and suitable dry woods. H 6–15; W 4–10.
- **Recognition:** Irregular branching and several leaf shapes on one plant: unlobed, mitten-like, and three-lobed. Can form related groups through suckering.
- **Asset instruction:** Mix those leaf shapes within one asset. Use plausible small groups sharing a growth area; avoid uniform orchard spacing. Autumn supplies orange, yellow, and red variation.
- **Reference:** [NC State: sassafras](https://plants.ces.ncsu.edu/plants/sassafras-albidum/).

#### 31 — Downy serviceberry · *Amelanchier arborea* · `amelanchier_arborea`

- **Site:** Woodland edges, slopes, and suitable planted landscapes. H 4–10; W 3–7.
- **Recognition:** Light fine crown, smooth-to-finely ridged gray bark, toothed oval leaves, and early white flower clusters. May be single- or multi-stemmed.
- **Asset instruction:** Use fine twigs and restrained leaf mass. Spring flowers should not erase the entire branching structure. Other native serviceberries and nursery hybrids require separate identifications.
- **Reference:** [NC State: downy serviceberry](https://plants.ces.ncsu.edu/plants/amelanchier-arborea/).

#### 32 — Pawpaw · *Asimina triloba* · `asimina_triloba`

- **Site:** Rich moist woods and sheltered lower ground. H 3–9; W 3–6.
- **Recognition:** Large simple leaves, often visually drooping, on comparatively slender stems. Can form understory patches through suckering.
- **Asset instruction:** Use fewer, larger leaf units and patch-based placement. Maintain an understory scale. Do not scatter isolated tropical-looking trees throughout dry upland woodland.
- **Reference:** [NC State: pawpaw](https://plants.ces.ncsu.edu/plants/asimina-triloba/).

### Conifers

#### 33 — Eastern white pine · *Pinus strobus* · `pinus_strobus`

- **Site:** Appropriate woods and historic plantings; more prominent in some northern and local ravine landscapes. H 20–35; W 8–18.
- **Recognition:** Soft fine foliage from needles in bundles of five. Young trees have a leader and branch tiers; older crowns become irregular and wind-shaped.
- **Asset instruction:** Preserve tier history but remove perfect repetition. Model needle bundles or sprays as foliage units, not broad leaves. Do not make every mature specimen a symmetrical Christmas tree.
- **Reference:** [NC State: white pine](https://plants.ces.ncsu.edu/plants/pinus-strobus/).

#### 34 — Eastern hemlock · *Tsuga canadensis* · `tsuga_canadensis`

- **Site:** Cool ravines and sheltered moist woodland; locally important but not a blanket Delco dominant. H 18–30; W 8–15.
- **Recognition:** Short flat needles, layered sprays, drooping branch tips and leader, fine shaded foliage, and small hanging cones.
- **Asset instruction:** Use flattened branchlet fans and uneven descending tips. White-pine needle bundles are wrong. Density and condition should match the chosen place and time.
- **Reference:** [NC State: eastern hemlock](https://plants.ces.ncsu.edu/plants/tsuga-canadensis/).

#### 35 — Eastern redcedar · *Juniperus virginiana* · `juniperus_virginiana`

- **Site:** Sunny old fields, open rocky ground, edges, and suitable barrens. H 6–15; W 3–8.
- **Recognition:** Dense columnar-to-conical young form, fibrous reddish-brown bark, and small scale-like foliage; old trees can become irregular. Blue berry-like cones occur on female plants.
- **Asset instruction:** Make compact fine sprays rather than pine needle clusters. Vary the top and side outline while keeping the underlying compact habit. Dark winter foliage can include brownish or bronzy tones.
- **Reference:** [NC State: eastern redcedar](https://plants.ces.ncsu.edu/plants/juniperus-virginiana/).

## 5. Localized additions and regional substitutions

| Species | Where it adds value | Distinctive asset requirements |
|---|---|---|
| Yellow birch — *Betula alleghaniensis* | Cooler northern/highland woods and locally suitable cool sites | Golden-bronze curling bark, fine branches, yellow autumn leaves. Do not make it paper white. [Species reference](https://plants.ces.ncsu.edu/plants/betula-alleghaniensis/) |
| Pitch pine — *Pinus rigida* | Specific barrens or other suitable dry sites | Stiff needles in threes, coarse bark, irregular crown; occasional trunk sprouts where the reference supports them. [Species reference](https://plants.ces.ncsu.edu/plants/pinus-rigida/) |
| Willow oak — *Quercus phellos* | Southeastern Coastal Plain references; also planted beyond its natural local habitat | Narrow unlobed leaves on an oak framework. Keep cultivated occurrence separate from native-site evidence. [Species reference](https://plants.ces.ncsu.edu/plants/quercus-phellos/) |
| Sweetbay magnolia — *Magnolia virginiana* | Confirmed southeastern wetland/Coastal Plain reference | Small tree or multi-stem form, simple leaves with pale backs, restrained cream flowers. Northern specimens should not automatically receive a southern evergreen habit. [Species reference](https://plants.ces.ncsu.edu/plants/magnolia-virginiana/) |

Sweetbay and willow oak are included because the southeastern Coastal Plain is a real botanical distinction. They should not become high-weight defaults across Philadelphia and Delco. [R2, R7]

## 6. Native trees versus familiar planted or introduced trees

An accurate urban environment may contain non-native trees. Keep their status explicit instead of calling every familiar tree native.

| Familiar tree | Treatment in the asset library |
|---|---|
| Norway maple, tree-of-heaven, Callery pear | Separate introduced/invasive category; never use as evidence for a native woodland palette. |
| London plane | Planted hybrid category; visually related to American sycamore, but not the same species. |
| Ginkgo, Norway spruce, ornamental flowering cherries | Planted landscape assets, with historical and site context. |
| Black locust | Native to parts of western PA; widely established beyond that range. Do not label a Delco occurrence automatically locally native. |
| Honeylocust and Kentucky coffeetree | PNHP describes uncertain Pennsylvania nativity because cultivation obscures their history. Keep status unresolved rather than asserting confirmed local nativity. |
| Eastern redbud | Native within parts of the broader region, including southwestern PA contexts; a planted Philly example is not evidence for a local wild population. |

The complex-nativity distinctions above follow PNHP's March 2025 treatment. [R12] For other introduced species, use DCNR's identification resources and the local inventory's invasive-species discussion. [R1–R2, R13]

## 7. Season and historical date

Use season as a change to structure, leaf presence, fruit, and ground litter—not just hue.

| Season | Useful changes |
|---|---|
| Early spring | Open branch silhouettes; swelling buds; species-specific flowering; serviceberry and dogwood timing distinct from full summer foliage. |
| Late spring | Smaller, lighter new leaves mixed with fuller growth. Do not simultaneously maximize flowers, mature fruit, and autumn color. |
| Summer | Several restrained greens; leaf backs differ from fronts; canopy interiors darker because of lighting and occlusion. |
| Early autumn | Some species and individuals change ahead of others; maintain many green crowns. |
| Late autumn | Exposed branches, partial crowns, and species-specific litter. A uniformly orange forest loses local identity. |
| Winter | Most broadleaf trees bare; selected juvenile beech/oak leaves retained; seed heads or cones remain only where appropriate. |

These are regional production guidelines, not a fixed calendar. Weather, elevation, exposure, and species move the schedule.

### For a 1990s Pennsylvania setting

- **Ash:** Emerald ash borer was first detected in Pennsylvania in 2007. A 1990s environment should not inherit today's widespread EAB-driven dead-ash pattern. [R14]
- **American chestnut:** The major chestnut-blight transformation happened long before the 1990s. Do not reconstruct an intact pre-blight chestnut canopy by default. [R7]
- **Elm and hemlock:** Disease and pest histories already matter. Do not make every elm either ancient and perfect or dead; verify the local reference and era. Hemlock decline is also site- and time-dependent. [R15]
- **Planting history:** Current tree inventories and cultivars do not prove what stood on a street in 1994. Use period photography for a specific reconstruction.

## 8. Practical palettes for procedural levels

The following percentages are **authored art-direction weights**, not measured forest composition. They apply to mature canopy-tree selection within the named patch. Understory and regeneration are separate layers.

### A. Delco mixed upland woodland

| Canopy species | Selection weight |
|---|---:|
| Tuliptree | 25% |
| White oak | 20% |
| Northern red oak | 20% |
| American beech | 15% |
| Red maple | 10% |
| Pignut hickory | 10% |

Add small patches of hornbeam in moist shade, dogwood near suitable edges, and sassafras in lighter openings. A dry ridge subpatch should shift toward chestnut/black oak; a floodplain subpatch should use a different palette entirely.

### B. Southeastern creek floodplain

| Canopy species | Selection weight |
|---|---:|
| American sycamore | 35% |
| Silver maple | 25% |
| Red maple | 15% |
| Boxelder | 15% |
| Black willow | 10% |

Concentrate willow on wetter sunny margins. Put sycamore trunks on banks or floodplain surfaces supported by the reference; do not scatter large trees through open water. Cottonwood can substitute in an open, disturbed riverbank patch.

### C. Old field and residential woodland edge

| Tree species | Selection weight |
|---|---:|
| Black cherry | 30% |
| Sassafras | 25% |
| Eastern redcedar | 20% |
| Black walnut | 15% |
| Red maple | 10% |

Use a patchwork of ages. Preserve a few large pre-existing trees. Keep redcedar in sunny positions and adjust walnut placement to suitable soils. A heavily urbanized lot needs its own introduced-species layer if historical accuracy calls for one.

### Rules the placement system should enforce

1. Choose a habitat patch before selecting a species.
2. Filter by moisture, drainage, substrate, shade, and historical period.
3. Distinguish planted trees from natural recruitment.
4. Choose growth context: forest, edge, open, or managed.
5. Sample size and crown proportions together; a sapling is not just a scaled-down veteran.
6. Place understory separately from canopy. Vary density according to light and disturbance.
7. Give nearby trees a shared history where appropriate, without cloning their geometry.
8. Keep roots in terrain and foliage attached to branch systems.
9. Let absence matter: clearings, marshes, paths, lawns, and maintained utility areas should retain space.
10. Review the result from gameplay height, not only a bird's-eye view.

## 9. Verify a real county/site and gather useful references

For a faithful named location, record evidence separately from the asset recipe:

```json
{
  "species_id": "liriodendron_tulipifera",
  "county": "Delaware",
  "site": "Crum Woods",
  "state_native_status": "native",
  "county_occurrence": "documented_in_published_site_account",
  "local_population_origin": "woodland_context; not individually assessed",
  "source_url": "https://www.scottarboretum.org/ents-explore-the-crum-woods/",
  "evidence_type": "historical_site_observation",
  "current_field_verification": false,
  "asset_context": "forest_grown",
  "exact_specimen_dimensions": null
}
```

Use county Natural Heritage Inventories first, then a herbarium-backed flora or specimen record when precise distribution matters. Read collection habitat and cultivation notes. A dot on a county map can represent a historical record, a planted tree, or an uncertain identification; it is not an abundance estimate. PNHP's inventory index and Morris Arboretum's botanical collections are useful entry points. [R16–R17]

For each priority asset, gather:

- An entire **leaf-on tree** from enough distance to see the crown.
- A comparable **leaf-off tree**, which reveals the actual architecture.
- Trunk base/root flare, lower bark, upper bark, and a major fork.
- One twig showing leaf arrangement, not merely a detached leaf.
- Leaf front and back with scale; a full compound leaf where applicable.
- At least one forest-grown and one open-grown example.
- A local habitat photograph showing neighbours and ground conditions.

Keep reference photographs as references unless their individual licenses permit asset reuse. The pages linked here contain mixed image licenses; an educational website is not automatically a source of commercially reusable textures.

## 10. Minimum useful production set

For a first Philly/Delco library, build **12 recognizably different species** before producing hundreds of variants:

1. White oak.
2. Northern red oak.
3. Tuliptree.
4. Red maple.
5. American beech.
6. American sycamore.
7. Silver maple.
8. Black cherry.
9. Black walnut.
10. Flowering dogwood.
11. Sassafras.
12. Eastern redcedar.

Then add pin oak/sweetgum for lowland work, hickories for uplands, willow/boxelder for creek margins, and hemlock/white pine for supported sites. Create forest, edge, and open-grown forms where each is useful. That yields more recognizable variety than changing only scale and rotation.

## 11. Regional and historical references

Species-specific links appear with each profile. These references support regional context, locality examples, or historical distinctions.

- **R1 — Philadelphia County Natural Heritage Inventory (2008).** [PNHP PDF](https://www.naturalheritage.state.pa.us/CNAI_PDFs/Philadelphia_County_NHI_2008_WEB.pdf). Regional upland/Coastal Plain context; historical inventory.
- **R2 — Delaware County Natural Heritage Inventory (2011).** [County publication page](https://www.delcopa.gov/planning/pubs/NaturalHeritagelnventory); [PDF](https://www.delcopa.gov/sites/default/files/2024-12/Delaware_CNHI_Update_2011_WEB.pdf). Habitats, conservation areas, and site descriptions. Large PDF.
- **R3 — Scott Arboretum, ENTS Explore the Crum Woods (2009).** [Local observation account](https://www.scottarboretum.org/ents-explore-the-crum-woods/). Documents local tree examples; exceptional measured trees are not ordinary asset defaults.
- **R4 — Scott Arboretum, Epifagus virginiana.** [Crum Woods canopy context](https://www.scottarboretum.org/epifagus-virginiana/).
- **R5 — Delaware County watersheds.** [County overview](https://www.delcopa.gov/conservation-district-home/watershed). Distinguishes the county's stream corridors.
- **R6 — Lancaster County Planning Commission, Pennsylvania Native Trees and Shrubs (2011).** [County guide](https://lancastercountyplanning.org/DocumentCenter/View/156/Pennsylvania-Native-Trees-and-Shrubs). Contains a Lancaster occurrence indicator; consult current botanical sources for taxonomy and disputed nativity.
- **R7 — Pennsylvania DCNR, Forest Types.** [State forest-type overview](https://www.pa.gov/agencies/dcnr/conservation/forests-and-tree/forest-types). Macroregional patterns, Coastal Plain, barrens, and historical chestnut context.
- **R8 — PNHP, Hemlock (White Pine)–Northern Hardwood Forest.** [Community description](https://www.naturalheritage.state.pa.us/Community.aspx?id=16067). Northern/central mixed hardwood-conifer context.
- **R9 — DCNR, Cook Forest wildlife and forest description.** [Cook Forest](https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/find-a-park/cook-forest-state-park/wildlife-watching). Mature hemlock/white-pine reference.
- **R10 — PNHP, Tuliptree–Beech–Maple Forest.** [Community description](https://naturalheritage.dcnr.pa.gov/Community.aspx?=16065).
- **R11 — USGS National Vegetation Classification, American Beech–Sweet Birch–Tuliptree–Sugar Maple Forest.** [Community record](https://data.usgs.gov/usnvc-explorer/unitDetails/755371). Supports moist forest assemblage interpretation.
- **R12 — PNHP, Species with Complex Nativity Statuses (March 2025).** [Official treatment](https://naturalheritage.dcnr.pa.gov/docs/Species%20with%20complex%20nativity%20statuses_PA%20Vascular%20Plant%20List.pdf). Particularly relevant to locusts and Kentucky coffeetree.
- **R13 — DCNR, Forests and Trees.** [Identification-resource entry point](https://www.pa.gov/agencies/dcnr/conservation/forests-and-tree). Links the Common Trees of Pennsylvania field guide.
- **R14 — DCNR, Emerald Ash Borer.** [Pennsylvania detection history](https://www.pa.gov/agencies/dcnr/conservation/forests-and-tree/insects-and-diseases/emerald-ash-borer).
- **R15 — DCNR, Insects and Diseases.** [Forest-health overview](https://www.pa.gov/agencies/dcnr/conservation/forests-and-tree/insects-and-diseases); [hemlock woolly adelgid](https://www.pa.gov/agencies/dcnr/conservation/forests-and-tree/insects-and-diseases/hemlock-woolly-adelgid).
- **R16 — PNHP, County Natural Heritage Inventories.** [County index](https://www.naturalheritage.state.pa.us/inventories.aspx). Follow the relevant county and site rather than assuming uniform county vegetation.
- **R17 — Morris Arboretum & Gardens, Herbarium and Networks.** [Botanical research and flora resources](https://www.morrisarboretum.org/learn-discover/research-collections/herbarium-and-networks).

**Evidence boundary:** the habitat palettes, selection weights, production-size ranges, minimum asset set, and modeling priorities are editorial synthesis for environment production. They are not quoted ecological survey results or a certified county flora.
