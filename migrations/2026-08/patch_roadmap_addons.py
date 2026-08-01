"""Items 19, 20 and 21: the Godot halves, the Patina/Lux boundary, the drift.

Three findings from one evening of reading, all of the same family: the parts
were built before the picture arrived, and nothing has gone back to reconcile
them. None is a defect anybody introduced. All three are load-bearing on the
standalone contract every README in this repo opens with.

19 is the general shape and the one worth keeping: four Godot addons exist
because each tool needed one before Level Factory could say who owns what.
20 is the specific case, and the one with code behind it rather than inference.
21 is measured by `verify-contracts` and is a number, not an argument.

Anchored on `### Not to be worked on`, which has been verified unique twice this
session and which the previous roadmap patch inserted ahead of rather than
touching. The assert refuses on a miss, as usual.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
RM = ROOT / "PIPELINE_ROADMAP.md"

ANCHOR = "### Not to be worked on\n"

NEW = '''**19. Every tool grew a Godot half before there was a DAG to say who owns
what.** The general form of items 20 and 21, and the one to keep if only one
survives.

There are at least four editor/runtime addons across the toolchain:

    addons/patina/              PS1 shader, per-surface apply, dock
    addons/zoo_importer/        family/habitat manifests, ATT_ socket Snap
    addons/pixelcoat_importer/  fixes texture import settings, writes .tres
    deli_counter's plugin dock  "Set up & Play"

plus `addons/lux/`, which is a rendering framework rather than an importer.
Every one of them was the right call when it was written: the tool needed
something in-engine and nothing else existed to provide it. They accumulated the
same way the version drift in item 21 did — not through carelessness, but
because the picture arrived after the parts.

**The problem is that each one is a thing that does not survive a bare folder
drop**, which is precisely what the shared header of every README in this repo
forbids: "the deliverable is a level shell that must work standalone in somebody
else's Godot project with none of these tools present." An addon is not present.

The honest default, now that a DAG exists to enforce it: **one addon ships, and
it is Lux**, because lighting and display genuinely are runtime and cannot be
baked into a mesh. Everything else either bakes into the .glb and the texture
set, or it is authoring convenience that does not belong in a pack at all. Zoo's
Snap workflow and its exhibit manifests are the clear second case — they help
somebody build a level and cost a recipient nothing when absent.

**THE LIGHTING CHAIN IS THE EXAMPLE OF THIS ALREADY DONE RIGHT, and it is worth
copying rather than re-deriving.** Deli Counter decides WHERE lights belong and
emits `<building>.lights.json`. Lot merges every building's manifest with its own
exterior streetlight anchors into one site manifest. Then ONE contract feeds TWO
consumers with no second source of truth: **Zoo bakes the visible fixture — the
housing, the collision, the emissive face — anchored at exactly the point the
light emits from, and Lux spawns the `Light3D` rig at that same anchor.** Zoo's
half ships inside the .glb and survives a bare drop; Lux's half is the one addon.
Nobody has to reconcile a lamp with its light because neither of them decided
where it goes.

So Zoo's fixture work is NOT authoring convenience and does not belong in the
same bucket as its importer dock. The dock, the Snap workflow and the exhibit
manifests are the convenience half; the baked kit, dressing and fixture geometry
are deliverable and must ship.

**AND THIS MAKES THE DROPPED LIGHTS FILE WORSE THAN IT LOOKED.** The cold run
found that Lot wrote `coldrun_pawn_job.site.lights.json` with 7 anchors and
`lot/package.py` did not put it in the pack — its manifest lists ten files and
lighting is not one of them. Under this chain that is not a missing sidecar. It
means **the pack ships the lamp housings and not the lights**: Zoo's fixtures are
baked into the geometry and visible, and the anchors Lux needs to put a
`Light3D` at each one are absent. A recipient gets a level full of light
fittings that do not emit. Fixing that is one line in the packer and it should
not wait for anything else in this item.

Unresolved under this rule: Patina's decal pass instantiates `Decal` nodes from
`decals.instances[]`, and no shader change bakes that. Either the stamps composite
into the texture set offline, or decals remain a runtime dependency whoever owns
them. That is the single hardest case and it should be decided on its own.

**20. Patina's Godot half is a renderer from before Lux was one.** The specific
case, with code behind it rather than inference.

Patina's `ps1.gdshader` implements what its own header calls "the four signature
PS1 tells". Lux carries all four as named uniforms in
`lux_stylized_standard.gdshader` and `lux_ordered_dither.gdshader`:

    vertex snapping     vertex_snap_enabled, vertex_snap_resolution
    affine mapping      affine_amount               (9 references)
    ordered dither      lux_ordered_dither.gdshader (13 references)
    colour depth        quantize / levels           (8 references)

Lux adds banded diffuse, palette pull, rim, specular, wetness, mach-band
emphasis, and `grime` / `grime_color` on top. Patina's file is 2,688 bytes and
exists twice — `addon/patina/ps1.gdshader` and `shaders/ps1.gdshader`, identical
length. Lux's two are 7,799 and 4,437, at a version `verify-contracts` calls
certified. Patina's carries "FIRST-RUN-IN-ENGINE ... has not been walked in the
editor yet."

**THE REASON TO ACT IS NOT DUPLICATION. It is that Patina's shader is the one
component making vertex colour ambiguous.** In code:

    patina/ps1.gdshader   render_mode vertex_lighting, ambient_light_disabled,
                          shadows_disabled
                          vec3 col = COLOR.rgb;   // vertex colour = the lighting

    lux_stylized_standard render_mode diffuse_burley, specular_schlick_ggx
                          uniform bool use_vertex_color = true;   // -> albedo
                          plus a real light() function

Zoo bakes wear into COLOR_0 and its README says to enable "Vertex Color > Use as
Albedo to multiply the baked grime into the base color". Patina's OWN offline
pass bakes banding, mottle and per-slot variation into the same channel
expecting the same thing. Patina's shader is the only place in the toolchain
that reads it as illumination instead. Retire it and the channel means one thing
everywhere.

**THE MIGRATION IS ALREADY HALF-WRITTEN, in a flag.** Patina's `--depth` presets
are the seam: `lux` "bakes only what Lux can't derive — Lux owns runtime light,
so it owns shadow colour and distance fog", against `delco`, "standalone (no
Lux) — owns the whole look". That is Patina ceding ground one concern at a time
as Lux matured. Finishing it means making `lux` the only mode and retiring
`delco` as a compatibility path for a world that no longer exists.

    retires   ps1.gdshader (both copies), patina_apply.gd, patina_dock.gd,
              plugin.gd, plugin.cfg, the --depth delco/exterior presets
    stays     the entire offline bake: vertex nuance, banding, mottle,
              per-slot variation, auto-UV, anchors, dressing. Densify stays
              too -- Lux's affine has the same limitation, since Godot still
              exposes no `noperspective` qualifier.
    connects  a PS1 preset .tres beside Lux's five, and shell.patina.json
              feeding Lux uniforms instead of driving a private shader.

**THE OPEN QUESTION, not to be folded in as settled.** Pixelcoat's stated
purpose is "repeating materials, trim sheets" for 3D surfaces. Patina also emits
structured and posterized texture sets. If Pixelcoat owns the skin, Patina's
texture output should narrow to wear LAYERS -- grime masks, edge dirt, streaks
that multiply over a Pixelcoat pack rather than replacing it. That would make
the boundary legible: Pixelcoat is what a surface is made of, Zoo is the
geometry wearing it, Patina is what makes it look used, Lux is how it is lit.
But Patina posterizes textures while Lux quantizes the frame, and those may
compose into the intended look or fight and band on already-flat surfaces.
Read Patina's texture modes against Pixelcoat's before deciding. Only the shader
half of this item is established.

**21. Four of eight tools have drifted from what Level Factory certified.**
Measured, not argued: `python -m level_factory -C rockay-ws verify-contracts`

    DRIFT   deli_counter   installed 0.88.0  vs certified 0.75.0
    DRIFT   lot            installed 0.32.0  vs certified 0.18.3
    DRIFT   pixelcoat      installed 0.11.0  vs certified  0.9.0
    DRIFT   zoo            installed 0.32.0  vs certified 0.30.2
    OK      dispatch, laser_tag, lux, patina

**The four that drifted are exactly the four that produce geometry and art.**
The four that match are consumers and services. Lot is fourteen minor versions
past its certification, and the Level Factory adapter still declares
`output_contract_version = "lot.site.0.18"` to match — so anything run through
the DAG today is validated against a Lot predating the kerb-cut work, the step
gates, and the flat-surface change. The art stages are the ones nobody has run
recently, and they are the ones furthest out of date; those two facts are the
same fact.

Note that item 20 would re-certify two tools that currently read OK. That is not
an argument against it, but it does mean the drift should be closed first, so
the re-certification has a clean baseline rather than absorbing four unrelated
version jumps at the same time.

'''


def main() -> int:
    if not RM.exists():
        raise SystemExit(f"missing {RM}. Nothing written.")
    src = RM.read_text(encoding="utf-8")
    before = len(src)
    if "**19. Every tool grew a Godot half" in src:
        print("PIPELINE_ROADMAP.md: items 19, 20 and 21 already present")
        return 0
    if "**18. Every gate measures whether a level WORKS" not in src:
        raise SystemExit("PIPELINE_ROADMAP.md has no item 18 -- run "
                         "patch_roadmap_goal.py first, or this is not the file "
                         "this patch was written against. NOTHING WRITTEN.")
    n = src.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"the `Not to be worked on` heading appears {n} "
                         f"time(s), expected exactly 1. NOTHING WRITTEN.")
    backup = RM.with_suffix(".md.pre_addons")
    if not backup.exists():
        shutil.copy2(RM, backup)
    RM.write_text(src.replace(ANCHOR, NEW + ANCHOR), encoding="utf-8")
    print("  PIPELINE_ROADMAP.md: items 19, 20 and 21 added ahead of "
          "`Not to be worked on`")
    print(f"  {before} -> {len(RM.read_text(encoding='utf-8'))} characters; "
          f"previous file kept at {backup.name}")
    print("\n  Nothing executable changed. 19 is the pattern, 20 is the case "
          "with code\n  behind it, 21 is a number from verify-contracts. The "
          "texture overlap in 20\n  is flagged as open rather than folded in as "
          "fact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
