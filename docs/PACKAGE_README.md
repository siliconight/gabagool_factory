# lot_demo_001 — a drop-in Godot level package

A procedurally generated multi-building level, exported as a self-contained
Godot 4.7 package. Unzip it into a project and open one scene. There is
nothing to install, no plugin, no addon, no autoload, and no dependency on
the toolchain that produced it.

**Not AI-generated.** Every mesh, wall opening, stair, ladder, spawn and light
anchor here is produced by deterministic generators from a JSON spec and a
seed. Re-run the same seed, get the same building, byte for byte. No model
sampled this geometry and no model is needed to open it.

---

## Try it in about a minute

```
1. unzip
2. open lot_demo_001.portable-godot/project.godot in Godot 4.7
3. press F5   (mission.tscn is already the main scene)
```

Or, to drop it into a project you already have: copy the
`lot_demo_001.portable-godot/` folder anywhere under your `res://` tree and
open `mission.tscn`. Paths inside the package are relative to the package
root, so it does not care where you put it.

---

## What to look at

**The buildings are not the same building.** Five archetypes, each generated
independently — footprint, storey count, interior partitions, stair systems,
ladders, roof access. Walk inside one and then another.

**It is walkable, and that is checked, not hoped.** Every shell is baked with
a Godot navmesh at agent radius 0.40 and proven to have a path from the bottom
of each stair to the top before it is allowed to ship. A stair a bot cannot
climb is a build failure upstream, not a surprise you find here.

**Gameplay anchors are in the scene, not in a document.** Player and enemy
spawns, patrol points, objective and loot markers, and extraction anchors are
real nodes with real transforms. They are proposals for your runtime to use or
ignore — the package makes no claim about mission progression, AI, netcode, or
persistence.

**The lighting is a full pass, not a preview.** This export includes the art
layer: theming, material assignment, weathering, and a lighting pass baked
against the composed site.

---

## Files worth opening

| file | what it tells you |
|---|---|
| `mission.tscn` | the entry scene |
| `project.godot` | ready to open; `mission.tscn` is already the main scene |
| `gameplay_anchors.json` | every spawn, patrol point, objective, loot and extraction anchor |
| `navigation_hints.json` | what the nav bake found, per shell |
| `proposed_beat_graph.json` | suggested mission beats — proposals, not requirements |
| `runtime_ownership_requirements.json` | what your runtime owns: progression, AI, netcode, persistence |
| `export_closure_scan.json` | every `res://` reference, and whether it resolves *inside* this package |
| `portable_resource_manifest.json` | every resource shipped, with content hashes |
| `output_layers.json` | which layers this build contains (`graybox+art+gameplay`) |
| `LICENSES.json` / `LICENSES.md` | provenance and versions of every tool that touched it |
| `HANDOFF.md` | scope: what this package is and is not authoritative for |

---

## The portability claim, and how it was tested

The package ships with a verdict from a test that does not trust the export.

`portability-test` copies the package into a **clean, empty Godot project** —
no Level Factory, no addons, nothing else on disk — launches Godot headless,
and reports what the engine says:

```
engine_check             passed      godot_version             4.7
parser_error_count       0           shader_error_count        0
scene_instantiated       true        resource_count            35
missing_resource_count   0           external_reference_count  0
absolute_path_count      0           issues                    []
required_plugin_count    0           required_autoload_count   0
status                   PASS
```

The two that matter most for dropping this into a project you already have are
`absolute_path_count: 0` and `external_reference_count: 0` — nothing in here
points at a path on the machine that built it, and nothing reaches outside the
package.

Separately, an export-closure scan resolves every `res://` path in every scene
and refuses to produce a package if any of them points outside it. That gate is
enforcing, not advisory: a broken reference fails the export rather than
shipping a package that looks fine until something silently does not render.

Both of those exist because an earlier package passed a weaker check and was
98% empty. The scanner had been resolving `res://` paths by filename suffix,
which Godot has never done, and it certified a package where 132 references
dangled and 5 more resolved to the *wrong* mesh. Both the scanner and the
packaging step were fixed; the numbers above are from the fixed pipeline.

---

## What this package deliberately does not do

- It does not ship an addon, a plugin, or an autoload. If it needed one, it
  would not be portable, and the export refuses to include them.
- It does not contain the authoring tools, the specs, or the generators.
- It makes no claim about being fun, balanced, or network-correct. It claims to
  be structurally sound and to open in your project without ceremony.

---

## If something does not work

Send back `export_closure_scan.json` and the Godot output. The scan is the
first thing to read: it names every reference the package makes and where each
one resolves, which turns "it looks broken" into a specific file and line.
