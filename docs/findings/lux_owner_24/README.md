# Lux's runtime scaffolding and a Ctrl+S (roadmap 24)

**The question the item left open, 2026-08-01:** Lux gives runtime scaffolding an `owner` in the editor, and owner is
what a save keeps. What would close it is that rule, proven by loading a shipped `lux.applied.tscn` in the editor,
saving, and diffing.

## The instrument

`owner_probe.py` copies a package to a work folder, enables `owner_probe_plugin.gd` there as an editor plugin, and
runs Godot's editor headless. The plugin opens the scene, lets the @tool scripts run for 120 frames, records what
the editor holds, and saves. The driver then compares the saved scene's `[node ...]` headers with the shipped
scene's. A node path the save added is scaffolding the editor kept. The plugin's waits follow Level Factory's light
bake plugin. `--runtime <dir>` overlays a Lux checkout's runtime scripts on the package's copies, with Level
Factory's localize rewrite applied (`res://addons/lux/` ships as `res://runtime/lux/`), so a patched runtime is
measured on the same shipped scene.

## What it measured on Lux 0.77.0 (`owner_probe_9323.json`, cold run 9323's package)

    cycle 1   editor 123.0 s   nodes 964 -> 971   +7 -0
    cycle 2   editor  23.2 s   nodes 964 -> 971   +7 -0   (the same seven, rebuilt)

The seven, each owned to `edited_scene_root` under `if Engine.is_editor_hint()`:

    LuxRoot/LuxSun                                    DirectionalLight3D   lux_lighting.gd
    LuxRoot/LuxWorldEnvironment                       WorldEnvironment     lux_environment.gd
    LuxRoot/@CanvasLayer@N                            CanvasLayer          lux_post_fx.gd
      .../@BackBufferCopy@N, LuxPostRect,             the post stack       lux_post_fx.gd (two blocks)
      LuxCRTBackBuffer, LuxCRTRect

The layer is auto-named because the `LuxPostFX` module already holds the name it asks for. A second save keeps
seven, not fourteen: `_build_modules` clears its own scaffolding before it rebuilds, so a clean editor keeps the
scaffolding but does not multiply it. The item's four suns and three stacks still need something this did not do,
such as script reloads, and stay unisolated. The defect measured is the keeping itself. One Ctrl+S puts runtime
scaffolding into a shipped scene, and a consumer then carries it in version control.

The fixture spawner and the light loader own their nodes too. Those are what the apply step persists, and the
probe found nothing of theirs added.

## The rule, a call made 2026-10-19 and meant to be changed (Lux 0.78.0)

Runtime scaffolding is ownerless in the editor too. The editor still draws it, and no save keeps it. A LuxRoot that
wants it kept as its own nodes sets `persist_scaffolding_in_editor`, which defaults to off, and the four sites ask
it (`patches/patch_lux_scaffold_ownerless.py`). Lux's dock and editor plugin own none of these nodes and reference
none of them. The probes that name `LuxRoot/LuxSun` find it by path at runtime, which ownership does not change.

## What it measured on Lux 0.78.0

(`owner_probe_9323_lux0780.json`, the same package with the patched runtime overlaid, 14 scripts.)

    cycle 1   editor 119.2 s   nodes 964 -> 964   +0 -0
    cycle 2   editor  23.4 s   nodes 964 -> 964   +0 -0

The editor still held one WorldEnvironment, one DirectionalLight3D and one CanvasLayer. The scaffolding is
built and drawn, and no save keeps it. Every Lux self-test exits 0 on 0.78.0: 25 as before, plus
`scaffold_owner_selftest.gd`, which fails on 0.77.0 (`patches/lux_scaffold_ownerless/`). The next package
exported carries this runtime.

**What this does not settle:** the item's four suns. Nothing a reload in the editor makes is owned now, so
however many it builds, none reaches a saved scene.
