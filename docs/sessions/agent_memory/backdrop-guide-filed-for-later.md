---
name: backdrop-guide-filed-for-later
description: "Walker's Pennsylvania backdrop/skybox guide filed 2026-10-02 at docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md; queued for later, not started"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-02T23:00:46.638Z
---

On 2026-10-02 the walker attached `Pennsylvania_Backdrop_World_Art_Design_Guide.md`
"for later, how to make more Delco level appropriate backdrops to add to our
existing skyboxes or new ones". Kept verbatim at
`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`. Not started.

What it asks for: 18 location recipes (Delco rooftops, main-street strip, ridge
and water tower, SEPTA corridor, creek belt, Philly skyline/rowhouse sea/avenue/
riverfront/bridge, interchange, airport, Lancaster farm belt, Amish road, small
borough, quarry, warehouse belt, cemetery), three distance bands, one landmark
per view, a small motion budget, and a per-level deliverable record (recipe,
view direction, landmark, time/weather, motion, sound, coverage, perf method).
Section 8 is a CC0 photo-kitbash workflow: it needs photo downloads, which need
the walker's explicit yes each time ([[references-fill-blanks-not-override]]).

**Why:** the walker queued it explicitly; the "alive" queue (unsteady light,
moving parts, changing world) comes first ([[levels-feel-static-make-them-alive]]).

**How to apply:** when the walker picks it up, the sky today is owned by Lux's
`skymint` addon (`lux/addons/skymint/`, `lux/addons/lux/docs/skymint_integration.md`);
backdrop cards/meshes beyond the lot have no owner yet, so the gap protocol in
`USING_THE_FACTORY.md` decides where they grow. Price it in draw calls at fixed
stations like everything else; the guide's own motion cues (slow clouds, one
blinking tower light, a far train) overlap the "changing world" step.

2026-10-04: the walker sent technique references, read in `docs/reference/BACKDROP_TECHNIQUES.md`. Plan: three bands. Near (0-60 m) is Empties plus a fence. Mid (60-400 m) is low-poly silhouettes with a lit-window atlas, MultiMesh, depth fog. Far (400 m+) is a panorama pre-rendered from our own kit and baked into the sky (zero draws). ParallaxBackground is 2D-only and deprecated, not usable. A pre-rendered view needs a fixed camera; only the far band transfers.
