"""Assemble a Godot project you can open and WALK the themed site in.

WHAT THIS IS FOR. The pipeline's outputs are not openable as they stand. Lot
writes the themed site with the composed building referenced by an ABSOLUTE
path -- `res://C:/Projects/.../presentation_compose/out/presentation/site.tscn`
-- which Godot cannot load, and the building's own `res://art/zoo/*.glb` refs
resolve against a project root that only exists inside the compose job. The
portable export is a different thing again: it ships a mission shell for a
consumer runtime, with the walk scene stripped by contract, so it has no player
in it.

So there was no way to stand in the themed level and look at it, which is the
one check no instrument in this repo replaces.

    python tools\\walk_themed.py <workspace>\\.level_factory <mission-id> [--out DIR]

Then open DIR in Godot and press F5. The main scene is Lot's walk scene: its
player, its ladders, its spawn.

WHAT IT ASSEMBLES, and why each piece is here:

  * the composed themed BUILDING as `building.tscn`, plus its siblings --
    `site_base.glb` and `art/` -- because the building names them at the
    project root and nothing else brings them;
  * the themed SITE, with that absolute reference rewritten to
    `res://building.tscn`;
  * Lot's walk scene as the entry, and `addons/lot` for the player and site
    scripts it names;
  * a `project.godot` whose main scene is the walk scene, so F5 works with no
    further clicking.

WHAT IT IS NOT. Not an export, not a deliverable, and deliberately not written
anywhere the pipeline reads. It is scratch you can throw away and rebuild from
one command, which is the only safe kind of copy: roadmap 33 is a day spent on
artifacts that outlived the run that made them.

WHAT A NONZERO EXIT MEANS. The project was not assembled. It never leaves a
half-built directory reporting success -- a project that opens to an empty
scene is worse than one that refused to be built.
"""
import argparse
import json
import os
import re
import hashlib
import shutil
import subprocess
import sys

_ABS_REF = re.compile(r'path="res://((?:[A-Za-z]:[\\/]|/)[^"]+)"')
#: The building reference in its OTHER form. Lot used to write the composed
#: building as an absolute `res://C:/...` path; it now writes the package
#: layout, `lot/shell/site.tscn`. `_ABS_REF` matches only the first, so on a
#: current site it substituted nothing, reported "0 absolute reference(s) made
#: local", and left a path to a directory this project does not have -- a walk
#: that assembled cleanly and could not load. Found 2026-08-29.
_PKG_REF = re.compile(r'path="(?:res://)?lot/shell/site\.tscn"')
#: Lot's scripts are named at the SCENE's directory (`path="lot_player.gd"`),
#: but the addon is copied to `addons/lot/`. Same failure, same walk.
_LOT_SCRIPT = re.compile(r'path="(?:res://)?(lot_[A-Za-z0-9_]+\.gd)"')
#: Every `path="..."` in a scene, for the closing check.
_ANY_REF = re.compile(r'path="([^"]+)"')


#: Written into every assembled walk project. WHY, and it cost a day to learn:
#: `shot_diff` guarded the PROJECT PATH, which is the harmless difference --
#: two directories are meant to differ in an A/B. The fatal difference is the
#: ART, and nothing recorded it. On 2026-08-29 a wear probe left `wear: 0.0`
#: baked into the workspace's job outputs; the genome file was reverted, three
#: later builds copied the stale art anyway, and two published comparisons
#: turned out to have moved two variables each. The guard fired on both and
#: said only "different projects", which is exactly the wrong half.
#:
#: So the subject is the ART CONTENT, hashed, plus the treatment flags that
#: change how it looks. Path is recorded and is NOT part of identity.
_SUBJECT_NAME = "walk_subject.json"
_SUBJECT_SCHEMA = "walk-subject/1"


def art_digest(out, sources):
    """(digest, file count) over the ART, and nothing that carries treatment.

    Hashes CONTENT, not mtimes or paths: a rebuild that produces identical art
    must compare equal, or every A/B needs a `--force` it should not need.
    `.import` sidecars and `.godot/` are excluded -- they are Godot's opinion
    about the art, regenerated per project, and including them would make two
    identical builds differ.

    THE ASSEMBLED WALK SCENE IS NOT ART, and the first version of this function
    said it was. `site_walk.tscn` is written HERE: Lot's sun and environment
    are taken out of it, a LuxRoot goes in, and `--triplanar` grafts another
    node. So two builds off ONE set of job outputs, differing only by a runtime
    flag, hashed differently -- and the guard refused the comparison it was
    built to permit, inside one run of using it. It failed safe, which is the
    only reason this was a nuisance rather than another silent confound.

    The fix is to hash the walk scene AS THE PIPELINE PRODUCED IT, from
    `sources`, so a real change upstream still moves the digest while anything
    grafted on the way in does not. `building.tscn` and `site.tscn` stay local:
    the first is copied verbatim and the second's rewrite is deterministic, so
    both are the art either way.
    """
    h = hashlib.sha256()
    n = 0
    for sub in ("art", "buildings"):
        base = os.path.join(out, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = sorted(d for d in dirs if d != ".godot")
            for f in sorted(files):
                if f.endswith((".import", ".uid")):
                    continue
                fp = os.path.join(dirpath, f)
                rel = os.path.relpath(fp, out).replace("\\", "/")
                h.update(rel.encode("utf-8"))
                with open(fp, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                n += 1
    for name in ("building.tscn", "site.tscn"):
        fp = os.path.join(out, name)
        if os.path.exists(fp):
            h.update(name.encode("utf-8"))
            with open(fp, "rb") as fh:
                h.update(fh.read())
            n += 1
    src_walk = sources.get("walk")
    if src_walk and os.path.exists(src_walk):
        h.update(b"source_walk")
        with open(src_walk, "rb") as fh:
            h.update(fh.read())
        n += 1
    return h.hexdigest(), n


def write_subject(out, args, building, site, walk, preset):
    """Stamp what this project IS, so a later comparison can check it."""
    srcs = {"building": building, "site": site, "walk": walk}
    digest, n = art_digest(out, srcs)
    doc = {
        "schema": _SUBJECT_SCHEMA,
        "mission_id": args.mission_id,
        "art_digest": digest,
        "art_files": n,
        "treatment": {
            "triplanar": bool(args.triplanar),
            # Recorded because it CHANGES THE PICTURE and the stamp exists to
            # stop two variables travelling as one. A --worldskin build and a
            # plain one differ in every wall, and without this line their
            # treatment blocks are identical and `shot_diff` would compare them
            # as the same experiment.
            "worldskin": bool(args.worldskin),
            "detached_textures": bool(args.detach_textures),
            "vertex_colors": args.vertex_colors or "",
            "fixture_lights": not args.no_fixture_lights,
            "walk_lighting_kept": bool(args.keep_walk_lighting),
            # Two builds that both keep Lot's lighting are NOT the same
            # experiment -- one has two suns and one has Lux driving the
            # level's own. Without this line their treatment blocks are
            # identical and `shot_diff` reports "treatment identical" over
            # the exact comparison item 92 exists to make.
            "sun_link": bool(args.sun_link) and bool(args.keep_walk_lighting),
            "lux_preset": preset or "",
        },
        "sources": srcs,
        "assembled_from": os.path.abspath(out),
    }
    with open(os.path.join(out, _SUBJECT_NAME), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    return doc


def unresolved_refs(out):
    """Every ext_resource path in `out`'s scenes that names no file.

    THE CHECK THIS TOOL PROMISED AND DID NOT HAVE. Its docstring says "a
    project that opens to an empty scene is worse than one that refused to be
    built", and then it built one: two reference forms changed underneath it
    and it reported success both times. Rewriting is a guess about formats;
    this is the question that does not care which format anything is in.
    """
    missing = []
    for name in sorted(os.listdir(out)):
        if not name.endswith(".tscn"):
            continue
        with open(os.path.join(out, name), encoding="utf-8") as fh:
            text = fh.read()
        for ref in _ANY_REF.findall(text):
            if "://" in ref and not ref.startswith("res://"):
                continue
            rel = ref[len("res://"):] if ref.startswith("res://") else ref
            if not os.path.exists(os.path.join(out, rel.replace("/", os.sep))):
                missing.append((name, ref))
    return missing


def vram_compressed(out):
    """`.import` sidecars that came out VRAM Compressed despite the default.

    Reads `compress/mode` back out of what Godot actually wrote rather than
    trusting that `[importer_defaults]` was honoured. 2 is VRAM Compressed --
    the value read off this project's own crashed run, not a guess.
    """
    hits = []
    for dirpath, dirs, files in os.walk(out):
        dirs[:] = [d for d in dirs if d != ".godot"]
        for f in files:
            if not f.endswith(".import"):
                continue
            p = os.path.join(dirpath, f)
            try:
                with open(p, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                continue
            if re.search(r"^compress/mode=2\s*$", text, re.M):
                hits.append(os.path.relpath(p, out))
    return sorted(hits)


_PROJECT = """; Scratch walk project, assembled by tools/walk_themed.py.
; Throw it away and rebuild it; nothing reads it back.
config_version=5

[application]
config/name="{name} (walk)"
run/main_scene="res://{entry}"
config/features=PackedStringArray("4.7")

[debug]
gdscript/warnings/inference_on_variant=1

; MUST match the shipped export's project.godot, which sets
; gl_compatibility. Without this Godot defaults to forward_plus, and the walk
; renders under a different renderer than the deliverable: different lighting,
; different materials, and any shot taken here is not comparable with one taken
; from the export. Found when shot_diff refused a pair whose renderer had
; silently changed from gl_compatibility to forward_plus between runs.
[rendering]
renderer/rendering_method="gl_compatibility"

; LIGHT LIMITS. The Compatibility renderer draws only the nearest N lights and
; silently drops the rest, so a level with 140 spawned fixtures has most of them
; switch off at a distance and pop back on as you walk in -- which reads as a
; draw-distance bug and is really a budget. Godot's defaults are 32 renderable
; and 8 per object; both are below what a fixture-lit level needs.
;
; These cost fill rate, so they are a preview setting, not a recommendation for
; the shipped project -- the export ships gl_compatibility too and has the same
; ceiling, which is a separate decision about how many fixtures a level should
; carry, not one this scratch project should make on anyone's behalf.
limits/opengl/max_renderable_lights=256
limits/opengl/max_lights_per_object=16

; Lux is an EDITOR plugin as well as a runtime script. Without this its @tool
; side never registers, so the editor viewport shows the level unlit and you
; have to tick a box in Project Settings before the thing you came to look at
; appears. A scratch project that needs a manual step before it is correct is
; a scratch project that will be looked at wrong.
[editor_plugins]
enabled=PackedStringArray("res://addons/lux/plugin.cfg")

; TEXTURE IMPORT DEFAULTS -- the reason a themed walk can be assembled at all.
;
; Godot's "Detect 3D" rewrites every texture a 3D material references: mipmaps
; on, and `compress/mode` bumped from Lossless to VRAM Compressed. In an editor
; session that is invisible housekeeping. In the `--headless --import` pass this
; tool runs it is fatal: the S3TC/BPTC compressor wants a rendering device, the
; headless display server does not provide one, and Godot dies with signal 11
; partway through. Measured 2026-08-29 on this project's own leavings: all 90
; `.png.import` files rewritten to `compress/mode=2` in one burst, then twelve
; `.godot/imported/*.s3tc.ctex*.tmp` files opened inside 40 ms and every one of
; them still ZERO BYTES when the process died. Twelve worker threads, no output,
; no partial texture -- it is not one bad PNG, it is the compressor.
;
; Disabling the detection keeps them Lossless, which for a walkthrough is not a
; downgrade: VRAM compression is the lossy step, so the preview is if anything
; closer to the source art than the export is.
;
; MIPMAPS MUST THEN BE ASKED FOR BY NAME. "Detect 3D" is what normally turns
; mipmaps ON as well as compression, so switching it off silently left
; `mipmaps/generate=false` on every texture. That cost nothing while every
; texture was EMBEDDED in a GLB -- the glTF importer sets its own up for 3D --
; and became visible the moment textures moved to loose files (roadmap 87):
; the same scene rendered with mean |delta| 3.32 and 54% of pixels moved,
; which is a larger change than the facade relief made. Not a missing texture,
; an un-mipmapped one, aliasing on every oblique surface. Generation is
; CPU-side, so unlike the compressor it is safe under --headless. It costs VRAM, which a scratch
; project can afford. `vram_compressed()` below re-reads the generated sidecars
; and refuses the project if this did not take -- the section name is Godot's,
; not ours, and a setting that silently stops working is how the preview would
; start crashing again with no message that says so.
[importer_defaults]
texture={{
"compress/mode": 0,
"detect_3d/compress_to": 0,
"mipmaps/generate": true
}}
{scene_defaults}"""

#: Written into `[importer_defaults]` only with --worldskin. `scene` is the
#: importer name Godot itself records in every `*.glb.import` -- read off
#: `wall_delco_01_w200.glb.import`, not guessed -- and `import_script/path` is
#: the hook it leaves empty there.
_SCENE_DEFAULTS = '''scene={
"import_script/path": "res://%s"
}
'''


class Failed(Exception):
    """Assembly could not complete. Never a partial success."""


def newest(root, name):
    """The newest file called `name` anywhere under `root`."""
    best = None
    for dirpath, _dirs, files in os.walk(root):
        if name in files:
            p = os.path.join(dirpath, name)
            if best is None or os.path.getmtime(p) > os.path.getmtime(best):
                best = p
    return best


def composed_site(compose_root):
    """The compose job's OWN site.tscn, never an archetype's copy of one.

    A varied lot publishes one scene per archetype under
    `presentation/lot/<id>/site.tscn`, and compose writes those AFTER the root:
    measured on cold_9001, root 10:06:31 against courthouse_a01 10:07:10. So
    `newest()` picks an archetype every time a lot is varied, and the walk
    project would be assembled around one building out of four -- with the
    site's own references to the other three pointing at nothing.

    The root is identified by STRUCTURE, not by clock: an archetype copy sits
    under a `lot/` parent and the root does not. Falling back to mtime among
    the remaining candidates keeps the single-shell behaviour identical.
    """
    best = None
    for dirpath, _dirs, files in os.walk(compose_root):
        if "site.tscn" not in files:
            continue
        if os.path.basename(os.path.dirname(dirpath)) == "lot":
            continue
        p = os.path.join(dirpath, "site.tscn")
        if best is None or os.path.getmtime(p) > os.path.getmtime(best):
            best = p
    return best


def copy_into(src_dir, dst_dir, skip_names=(), skip_dirs=(".godot", "addons")):
    """Copy a tree. `skip_names` applies at the SOURCE ROOT ONLY.

    It used to match a basename anywhere in the tree, which is the trap
    CLAUDE.md records against `_copy_tree`: "it matches basenames anywhere in
    the tree, so it also excluded all five `lot/<archetype>/site.tscn` and the
    export came back with every building unresolved". That was fixed in the
    export path and not here, and nothing noticed because until a VARIED LOT
    there was never a second `site.tscn` in the tree.

    Measured on cold_9001: the caller skips `site.tscn`, `project.godot` and
    `site_main.tscn` to keep the root's copies out, and so silently dropped
    `lot/{self_storage_a02,auto_shop_a01,museum_a02,courthouse_a01}/site.tscn`
    -- every building on the site. The assembler's own missing-reference check
    caught it and refused, which is the only reason this was a refusal rather
    than a walk through an empty world.

    Root-only is what the single caller meant; nothing asks for the old
    behaviour.
    """
    for dirpath, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(dirpath, src_dir)
        target = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        at_root = rel == "."
        os.makedirs(target, exist_ok=True)
        for f in files:
            if at_root and f in skip_names:
                continue
            shutil.copy2(os.path.join(dirpath, f), os.path.join(target, f))


#: Lux's NATIVE layout, not the export's.
#:
#: The export puts Lux at `runtime/lux/` and its localize step REWRITES the
#: `res://addons/lux/...` paths baked into the addon to match. Copying to
#: `runtime/lux` without that rewrite reproduces the layout and not the
#: relocation, and Godot then reports a wall of `Cannot open file
#: 'res://addons/lux/presets/*.tres'` plus a cascade ending in
#: `lux_root.gd:202 - Nonexistent function 'new'`. A scratch project has no
#: reason to relocate anything: left where the addon expects to be, every
#: internal path resolves with no rewriting at all.
_LUX_DEST = os.path.join("addons", "lux")

_LUX_NODE = """
[node name="LuxRoot" type="Node3D" parent="."]
script = ExtResource("lux_root")
"""

#: Written into the scratch project and attached to the walk scene. The walk
#: is assembled from themed_site_assemble's scene, NOT from lux.applied.tscn,
#: so it does not inherit run_lux_apply's fixture spawn -- measured on
#: category5_baie_dore_001: lux.quality.json said 152 fixture lights and
#: light_census on the preview said OmniLight3D 0.
_SPAWN_GD_NAME = "walk_fixtures.gd"
_SPAWN_GD = 'extends Node\n## Spawn Zoo\'s marked fixture lights in the scratch walk project.\n##\n## The shipped level gets these from `run_lux_apply.gd`, which calls\n## LuxFixtureSpawner and packs the result into lux.applied.tscn. The walk\n## project is assembled from themed_site_assemble\'s scene instead, with its\n## own grafted LuxRoot, so it does not inherit that spawn -- measured with\n## tools/light_census.py: lux.quality.json reported 152 fixture lights while\n## the preview ran OmniLight3D 0. A preview that is lit differently from the\n## level is worse than no preview, because it gets believed.\n\n\nfunc _ready() -> void:\n\tvar script_res: GDScript = load("res://addons/lux/runtime/lux_fixture_spawner.gd")\n\tif script_res == null:\n\t\tpush_warning("walk_fixtures: lux fixture spawner missing")\n\t\treturn\n\tvar root: Node = get_parent()\n\tif root == null:\n\t\treturn\n\t# WAIT A FRAME BEFORE SPAWNING. _ready runs while the parent is still\n\t# setting up its children, and Godot refuses add_child() on a node in that\n\t# state ("parent node is busy setting up children"). LuxFixtureSpawner does\n\t# not check the return, so it parents every rig into a container that never\n\t# entered the tree and reports "Spawned 152 fixture light(s)" -- measured:\n\t# containers=0 in the same breath as 152 successes.\n\tawait get_tree().process_frame\n\tvar res: Dictionary = script_res.spawn(root)\n\tprint("[walk_fixtures] %s" % String(res.get("msg", "")))\n\t# A spawn that reports 152 successes and leaves nothing in the tree is\n\t# either parenting somewhere that is not the running scene, or having its\n\t# container freed inside the same frame. Those need different fixes, and\n\t# one report at one instant cannot tell them apart -- so take the reading\n\t# twice, immediately and after the frame settles.\n\t_report("immediately", root)\n\tawait get_tree().process_frame\n\tawait get_tree().process_frame\n\t_report("two frames later", root)\n\n\nfunc _report(when: String, root: Node) -> void:\n\tvar kids: Array = []\n\tfor c in root.get_children():\n\t\tkids.append("%s(%s)" % [c.name, c.get_class()])\n\tvar omni: Array = root.find_children("*", "OmniLight3D", true, false)\n\tvar cons: Array = root.find_children("LuxFixtureLights", "", true, false)\n\tprint("[walk_fixtures] %s: root=%s(%s) in_tree=%s omni=%d containers=%d"\n\t\t% [when, root.name, root.get_class(), root.is_inside_tree(), omni.size(), cons.size()])\n\tprint("[walk_fixtures] %s: root children = %s" % [when, ", ".join(kids)])\n\tfor c in cons:\n\t\tprint("[walk_fixtures] %s: container %s rigs=%d"\n\t\t\t% [when, root.get_path_to(c), c.get_child_count()])\n\t\tif c.get_child_count() > 0:\n\t\t\tvar f: Node = c.get_child(0)\n\t\t\tvar fk: Array = []\n\t\t\tfor k in f.get_children():\n\t\t\t\tfk.append("%s(%s)" % [k.name, k.get_class()])\n\t\t\tprint("[walk_fixtures] %s: first rig %s(%s) kids = %s"\n\t\t\t\t% [when, f.name, f.get_class(), ", ".join(fk)])\n'

_SPAWN_NODE = """
[node name="WalkFixtures" type="Node" parent="."]
script = ExtResource("walk_fixtures")
"""

#: OPT-IN, and off by default, because it changes how every kit surface is
#: textured and the point of the walk project is to preview what SHIPS. Turned
#: on with --triplanar to A/B the module seam (roadmap 74, 80): Zoo projects
#: each module's texture from its own centre-pivot local box, so the pattern
#: restarts at every 2.00 m boundary, and glTF cannot carry a world-space
#: projection -- it has to be set on the material after import.
#: LEVEL FACTORY'S overlay, read from LF rather than copied into this file.
#: Two implementations of one overlay is how the walk and the export drift
#: apart; LF is the dominant export layer, so the preview shows what the export
#: shows. If LF moves it, this fails loudly at assembly rather than quietly
#: shipping a stale fork.
_OVERLAY_GD_NAME = "debug_overlay.gd"
_OVERLAY_SRC = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "level_factory", "assets", "godot",
    _OVERLAY_GD_NAME)

_OVERLAY_NODE = """
[node name="DebugOverlay" type="Node" parent="."]
script = ExtResource("debug_overlay")
"""

_WORLDSKIN_GD_NAME = "zoo_worldskin.gd"
_WORLDSKIN_GD = open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "zoo_worldskin.gd"),
    encoding="utf-8").read()

_TRIPLANAR_GD_NAME = "walk_triplanar.gd"
_TRIPLANAR_GD = 'extends Node\n## World-space triplanar UVs on the KIT materials, at runtime, in the scratch\n## walk project only.\n##\n## WHY THIS IS A RUNTIME SCRIPT AND NOT A PIPELINE CHANGE. Zoo bakes UVs into\n## the mesh (`cube_project_uv`, box projection from each module\'s own\n## centre-pivot local box) and glTF carries UV sets and nothing else -- there\n## is no way to express "project from world position" in a .glb. So this can\n## only be a material property set after import, and setting it here, in a\n## throwaway project, is how to SEE the difference before deciding whether the\n## export should carry it.\n##\n## WHAT IT IS TESTING. Every module\'s texture restarts at its own edges,\n## because every module projects from its own local box. Measured on the\n## elevation of `bank_block_001`: a hard vertical discontinuity in the stone at\n## every 2.00 m module boundary, the whole length of a 30 m facade. World\n## triplanar makes the projection a function of world position instead, so two\n## adjacent panels sample continuous texture and the seam has nothing to draw\n## it. It also stops a scaled module stretching its texture, which is the\n## stated reason Deli Counter confines its one-mesh-fits-any-width `wallEnd` to\n## filler (`_record_wall_slot`: "Full-width walls and openings stay exact-fit\n## (scale 1) so themed art is never stretched").\n##\n## SCOPED TO THE KIT ON PURPOSE. Walls, openings and their fillers -- anything\n## under a node Deli Counter named `ext_*` or `int_*`. Dressing and props are\n## left alone: world-space projection on a small movable object is wrong, and\n## the dressing path already varies between instances (measured with\n## `vertex_variation.py`: BETWEEN sd 0.02 on every cover family, against 0.00\n## for every kit module).\n\n## THE SCALE IS MEASURED OFF THE MESH, NOT GUESSED. The first version\n## multiplied `uv1_scale` by Zoo\'s `texel=1.2` on the assumption that the\n## material still carried Pixelcoat\'s tiling as a UV scale. It does not --\n## Godot\'s glTF importer bakes `KHR_texture_transform` into the mesh UVs -- so\n## the stone came out roughly twice its proper size and visibly soft, and the\n## elevation A/B could not see it because at that distance nothing is sharp.\n##\n## The density is recoverable from the mesh that already has it: walk the\n## surface\'s own vertices and UVs and take the median of |dUV| / |dPOSITION|\n## over its edges. That ratio IS the texels-per-metre the baked projection was\n## using, so re-applying it as `uv1_scale` reproduces the old density exactly\n## while the projection becomes world-space. Nothing to tune and nothing to\n## read off another file.\n##\n## Set `scale_override` above zero to force a value instead, for the case where\n## the derivation is wrong and someone needs to see it be wrong.\n@export var scale_override: float = 0.0\n\n\nfunc _ready() -> void:\n\t# One frame, for the same reason walk_fixtures waits: the parent is still\n\t# setting up children during _ready and instanced subtrees are not all\n\t# present yet.\n\tawait get_tree().process_frame\n\tvar root: Node = get_parent()\n\tif root == null:\n\t\tpush_warning("walk_triplanar: no parent to walk")\n\t\treturn\n\n\tvar seen: Dictionary = {}\n\tvar changed: int = 0\n\tvar skipped_non_kit: int = 0\n\tvar no_material: int = 0\n\tvar no_density: int = 0\n\tfor n in root.find_children("*", "MeshInstance3D", true, false):\n\t\tvar mi: MeshInstance3D = n\n\t\tif not _is_kit(mi):\n\t\t\tskipped_non_kit += 1\n\t\t\tcontinue\n\t\tvar mesh: Mesh = mi.mesh\n\t\tif mesh == null:\n\t\t\tcontinue\n\t\tfor i in range(mesh.get_surface_count()):\n\t\t\tvar mat: Material = mi.get_active_material(i)\n\t\t\tif mat == null:\n\t\t\t\tno_material += 1\n\t\t\t\tcontinue\n\t\t\tvar bm: BaseMaterial3D = mat as BaseMaterial3D\n\t\t\tif bm == null:\n\t\t\t\tcontinue\n\t\t\tvar key: int = bm.get_instance_id()\n\t\t\tif seen.has(key):\n\t\t\t\tcontinue\n\t\t\tseen[key] = true\n\t\t\tvar before: Vector3 = bm.uv1_scale\n\t\t\tvar density: float = scale_override\n\t\t\tvar how: String = "override"\n\t\t\tif density <= 0.0:\n\t\t\t\tdensity = _uv_density(mesh, i)\n\t\t\t\thow = "measured"\n\t\t\tif density <= 0.0:\n\t\t\t\tno_density += 1\n\t\t\t\tprint("[walk_triplanar] %s  NO UV DENSITY -- left alone"\n\t\t\t\t\t% bm.resource_name)\n\t\t\t\tcontinue\n\t\t\tbm.uv1_triplanar = true\n\t\t\tbm.uv1_world_triplanar = true\n\t\t\tbm.uv1_scale = Vector3(density, density, density)\n\t\t\tchanged += 1\n\t\t\tprint("[walk_triplanar] %s  uv1_scale %s -> %.4f (%s)"\n\t\t\t\t% [bm.resource_name, before, density, how])\n\n\t# Report the counts, not just a success. A run that changed zero materials\n\t# looks identical to one that was never added to the scene, and those need\n\t# different fixes.\n\tprint("[walk_triplanar] %d material(s) made world-triplanar, %d left alone for want of a UV density"\n\t\t% [changed, no_density])\n\tprint("[walk_triplanar] %d non-kit mesh(es) left alone, %d surface(s) with no material"\n\t\t% [skipped_non_kit, no_material])\n\n\n## Texels per metre, read off the surface\'s own vertices and UVs.\n##\n## Median rather than mean: a box carries a few degenerate edges (zero-length\n## UV steps across a seam, coincident verts after bevelling) and one of those\n## in a mean drags the whole material to the wrong scale. Sampling is capped --\n## a wall is 85 vertices but a plate can be thousands, and the ratio is the\n## same everywhere on a box-projected mesh, so more samples buy nothing.\nfunc _uv_density(mesh: Mesh, surface: int) -> float:\n\tvar arrays: Array = mesh.surface_get_arrays(surface)\n\tif arrays.size() <= Mesh.ARRAY_TEX_UV:\n\t\treturn 0.0\n\tvar verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]\n\tvar uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]\n\tif verts.size() < 2 or uvs.size() != verts.size():\n\t\treturn 0.0\n\tvar ratios: Array = []\n\tvar limit: int = mini(verts.size() - 1, 400)\n\tfor i in range(limit):\n\t\tvar dp: float = verts[i].distance_to(verts[i + 1])\n\t\tvar du: float = uvs[i].distance_to(uvs[i + 1])\n\t\tif dp > 0.001 and du > 0.00001:\n\t\t\tratios.append(du / dp)\n\tif ratios.is_empty():\n\t\treturn 0.0\n\tratios.sort()\n\treturn float(ratios[ratios.size() / 2])\n\n\n## True when any ancestor is a Deli Counter wall slot. The `ext_<storey>_<face>`\n## / `int_<storey>_<n>` naming is the same one `repetition_census.py` and\n## `look_shots.gd` already read, so the three tools agree on what a wall is.\nfunc _is_kit(n: Node) -> bool:\n\tvar cur: Node = n\n\twhile cur != null:\n\t\tvar nm: String = String(cur.name)\n\t\tif nm.begins_with("ext_") or nm.begins_with("int_"):\n\t\t\treturn true\n\t\tcur = cur.get_parent()\n\treturn false\n'

_TRIPLANAR_NODE = """
[node name="WalkTriplanar" type="Node" parent="."]
script = ExtResource("walk_triplanar")
"""

#: Roadmap 84's probe. `report` reads whether the engine consumes Zoo's
#: per-vertex wear and changes nothing; `force` also switches it on, which is
#: the EXPERIMENT and not the fix -- see the script's own header.
_VCOL_GD_NAME = "walk_vertexcolor.gd"
_VCOL_GD = 'extends Node\n## Does the ENGINE use Zoo\'s per-vertex wear? Read the flag; optionally set it.\n##\n## WHY THIS EXISTS. Roadmap 84. Zoo computes per-vertex wear, writes it into\n## COLOR_0, and it is unquestionably in the shipped GLB -- `vertex_variation.py`\n## measures 0.642 .. 0.982 across one wall panel, a fifth of the albedo. Then\n## deleting the entire layer and re-rendering through the same cameras moved\n## every shot by LESS than two independent launches of the same build. A\n## quarter of an albedo cannot change that much and move nothing, so the layer\n## is not arriving.\n##\n## `BaseMaterial3D` ignores COLOR_0 unless `vertex_color_use_as_albedo` is set,\n## and Godot\'s glTF importer decides that for itself. Nobody has ever read the\n## flag back. This reads it.\n##\n## TWO FACTS, NOT ONE, because they fail differently: whether the SURFACE\n## carries a colour array at all, and whether the MATERIAL is told to use it. A\n## surface with no COLOR_0 means the export dropped it (the 2026 dressing bug,\n## already fixed once); a surface with COLOR_0 and a material that ignores it\n## means the import dropped it, which is a different repair.\n##\n## `force_on` is the experiment, not the fix. Turning this on restores per-\n## module border shading to every wall in the library at full strength -- which\n## is item 81\'s defect arriving for the first time. Look at it before deciding\n## anything.\n@export var force_on: bool = false\n\n\nfunc _ready() -> void:\n\tawait get_tree().process_frame\n\tvar root: Node = get_parent()\n\tif root == null:\n\t\tpush_warning("walk_vertexcolor: no parent to walk")\n\t\treturn\n\n\tvar seen: Dictionary = {}\n\tvar flag_on: int = 0\n\tvar flag_off: int = 0\n\tvar surf_with_color: int = 0\n\tvar surf_no_color: int = 0\n\tvar changed: int = 0\n\n\tfor n in root.find_children("*", "MeshInstance3D", true, false):\n\t\tvar mi: MeshInstance3D = n\n\t\tif not _is_kit(mi):\n\t\t\tcontinue\n\t\tvar mesh: Mesh = mi.mesh\n\t\tif mesh == null:\n\t\t\tcontinue\n\t\tfor i in range(mesh.get_surface_count()):\n\t\t\tvar has_color: bool = false\n\t\t\tvar am: ArrayMesh = mesh as ArrayMesh\n\t\t\tif am != null:\n\t\t\t\tvar fmt: int = am.surface_get_format(i)\n\t\t\t\thas_color = (fmt & Mesh.ARRAY_FORMAT_COLOR) != 0\n\t\t\tif has_color:\n\t\t\t\tsurf_with_color += 1\n\t\t\telse:\n\t\t\t\tsurf_no_color += 1\n\n\t\t\tvar mat: Material = mi.get_active_material(i)\n\t\t\tif mat == null:\n\t\t\t\tcontinue\n\t\t\tvar bm: BaseMaterial3D = mat as BaseMaterial3D\n\t\t\tif bm == null:\n\t\t\t\tcontinue\n\t\t\tvar key: int = bm.get_instance_id()\n\t\t\tif seen.has(key):\n\t\t\t\tcontinue\n\t\t\tseen[key] = true\n\t\t\tif bm.vertex_color_use_as_albedo:\n\t\t\t\tflag_on += 1\n\t\t\telse:\n\t\t\t\tflag_off += 1\n\t\t\t\tif force_on:\n\t\t\t\t\tbm.vertex_color_use_as_albedo = true\n\t\t\t\t\tchanged += 1\n\n\tprint("[walk_vertexcolor] kit surfaces: %d carry COLOR_0, %d do not"\n\t\t% [surf_with_color, surf_no_color])\n\tprint("[walk_vertexcolor] kit materials: %d already use vertex colour as albedo, %d do not"\n\t\t% [flag_on, flag_off])\n\tprint("[walk_vertexcolor] force_on=%s, %d material(s) switched on"\n\t\t% [force_on, changed])\n\tif surf_with_color > 0 and flag_on == 0 and not force_on:\n\t\tprint("[walk_vertexcolor] VERDICT: the colours are on the meshes and no "\n\t\t\t+ "material reads them. Roadmap 84 confirmed.")\n\n\n## Same `ext_*` / `int_*` naming `repetition_census.py`, `look_shots.gd` and\n## `walk_triplanar.gd` already read, so four tools agree on what a wall is.\nfunc _is_kit(n: Node) -> bool:\n\tvar cur: Node = n\n\twhile cur != null:\n\t\tvar nm: String = String(cur.name)\n\t\tif nm.begins_with("ext_") or nm.begins_with("int_"):\n\t\t\treturn true\n\t\tcur = cur.get_parent()\n\treturn false\n'

_VCOL_NODE = """
[node name="WalkVertexColor" type="Node" parent="."]
script = ExtResource("walk_vertexcolor")
force_on = %s
"""

#: The preset line, when the mission's own lighting choice is known.
_LUX_PRESET_NODE = '''active_preset = ExtResource("lux_preset")
'''

_ACTIVE_PRESET = re.compile(r'active_preset\s*=\s*ExtResource\("([^"]+)"\)')

#: Lot's harness sun, as `write_walk_scene` emits it. Sun Link needs a node to
#: point AT, so the graft checks rather than assuming: a walk scene built with
#: the lighting dropped has none, and a NodePath to a node that is not there
#: resolves to null, which is silently the no-link behaviour again.
_SUN_NODE = re.compile(r'^\[node name="Sun" type="DirectionalLight3D"', re.M)


def applied_preset(applied_tscn):
    """The preset resource path ``lux_apply`` actually chose, or None.

    WHY THIS IS READ RATHER THAN DEFAULTED. ``graft_lux`` removes Lot's sun
    and environment and installs a bare LuxRoot, so before this the preview
    was lit by whatever the Lux script defaults to. Measured on
    ``category5_baie_dore_001``: ``lux.applied.tscn`` loads
    ``res://addons/lux/presets/blue_hour.tres`` and sets ``active_preset`` to
    it, and ``lux.quality.json`` says ``"preset": "Blue Hour"`` -- while the
    walk project's LuxRoot carried no ``active_preset`` line at all. Every
    walkthrough was therefore judging lighting the shipped level does not use,
    which is worse than walking unlit: unlit looks broken and gets fixed,
    wrong-but-plausible gets believed.
    """
    if not applied_tscn or not os.path.exists(applied_tscn):
        return None
    with open(applied_tscn, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = _ACTIVE_PRESET.search(text)
    if not m:
        return None
    ext = re.search(r'\[ext_resource[^\]]*path="([^"]+)"[^\]]*id="%s"\]'
                    % re.escape(m.group(1)), text)
    return ext.group(1) if ext else None


def graft_lux(tscn_text, drop_walk_lighting=True, preset=None,
              spawn_fixtures=True, triplanar=False, vertex_colors=None,
              overlay=False, sun_link=False):
    """Add a LuxRoot to a walk scene, and take Lot's own lighting out.

    WHY THE SECOND HALF. Lot's walk scene ships a `WorldEnvironment` and a
    `Sun`, and Lux supplies both itself -- the shipped `lux.applied.tscn` has
    a LuxRoot and no environment or light of its own. Leaving Lot's in place
    lights the level twice, and that is not hypothetical: `look_shots.py`
    already recorded the difference on this project.

        no Lux        mean 108.6   p95 254   near-clip 18.62%
        Lux, 2 suns   mean 151.7   p95 248   near-clip  3.17%
        Lux, 1 sun    mean 147.0   p95 222   near-clip  1.13%

    Two suns is measurably worse than one and was already known. Returns the
    rewritten text; raises nothing, because a walk scene without a
    WorldEnvironment to remove is fine.
    """
    out = tscn_text
    if drop_walk_lighting:
        for name in ("WorldEnvironment", "Sun"):
            start = out.find('[node name="%s"' % name)
            if start < 0:
                continue
            nxt = out.find("\n[node ", start + 1)
            out = out[:start] + (out[nxt + 1:] if nxt >= 0 else "")
    ext = ('[ext_resource type="Script" '
           'path="res://%s/runtime/lux_root.gd" id="lux_root"]\n'
           % _LUX_DEST.replace(os.sep, "/"))
    node = _LUX_NODE
    extra = 1
    if preset:
        ext += ('[ext_resource type="Resource" path="%s" id="lux_preset"]\n'
                % preset)
        node = node.rstrip("\n") + "\n" + _LUX_PRESET_NODE
        extra += 1
    # SUN LINK, and it has to happen HERE -- before the sibling node blocks
    # below, which are separate `[node]` entries rather than LuxRoot
    # properties. A property appended after them would land on WalkFixtures.
    #
    # THE `node_paths` HEADER IS THE WHOLE TRICK. Godot's scene loader builds
    # its set of node-path properties SOLELY from that field; a property
    # missing from it is assigned literally, so `sun_light = NodePath(...)`
    # becomes a NodePath written into a DirectionalLight3D-typed property,
    # GDScript rejects the type, and it is dropped SILENTLY -- no error, no
    # warning, `sun_light` null through `_ready`, and `ensure_sun()`
    # manufactures a LuxSun beside Lot's. `lux_inject.py` records measuring
    # exactly that on 4.7.stable: 2 directional lights without the field, 1
    # with it.
    if sun_link:
        if drop_walk_lighting:
            sys.stderr.write(
                "[walk_themed] --sun-link needs a sun to link to and the "
                "walk lighting is being dropped; not wiring it\n")
        elif not _SUN_NODE.search(out):
            sys.stderr.write(
                "[walk_themed] --sun-link asked for, but this walk scene has "
                "no `Sun` DirectionalLight3D to point at; not wiring it\n")
        else:
            node = node.replace(
                '[node name="LuxRoot" type="Node3D" parent="."]',
                '[node name="LuxRoot" type="Node3D" parent="."'
                ' node_paths=PackedStringArray("sun_light")]', 1)
            node = node.rstrip("\n") + '\nsun_light = NodePath("../Sun")\n'
    if spawn_fixtures:
        ext += ('[ext_resource type="Script" path="res://%s" '
                'id="walk_fixtures"]\n' % _SPAWN_GD_NAME)
        node = node.rstrip("\n") + "\n" + _SPAWN_NODE
        extra += 1
    if overlay:
        ext += ('[ext_resource type="Script" path="res://%s" '
                'id="debug_overlay"]\n' % _OVERLAY_GD_NAME)
        node = node.rstrip("\n") + "\n" + _OVERLAY_NODE
    if triplanar:
        ext += ('[ext_resource type="Script" path="res://%s" '
                'id="walk_triplanar"]\n' % _TRIPLANAR_GD_NAME)
        node = node.rstrip("\n") + "\n" + _TRIPLANAR_NODE
        extra += 1
    if vertex_colors:
        ext += ('[ext_resource type="Script" path="res://%s" '
                'id="walk_vertexcolor"]\n' % _VCOL_GD_NAME)
        force = "true" if vertex_colors == "force" else "false"
        node = node.rstrip("\n") + "\n" + (_VCOL_NODE % force)
        extra += 1
    marker = "\n\n[sub_resource"
    at = out.find(marker)
    if at < 0:
        at = out.find("\n\n[node ")
    out = out[:at] + "\n" + ext + out[at:] if at >= 0 else ext + out
    # load_steps is a preallocation hint; leaving it short makes Godot warn.
    m = re.search(r"load_steps=(\d+)", out)
    if m:
        out = out.replace("load_steps=%s" % m.group(1),
                          "load_steps=%d" % (int(m.group(1)) + extra), 1)
    return out.rstrip("\n") + "\n" + node


def clear_out(out):
    """Empty the scratch project, keeping Godot's `.godot` cache. Returns the
    paths that could not be removed.

    A plain `shutil.rmtree` dies with `WinError 32` and a traceback whose top
    frame is `shutil`, which names the mechanism and not the cause: Godot holds
    files under `.godot` for as long as the editor has the project open, and
    rebuilding a walk project you are currently walking is the normal thing to
    want to do. That cache is regenerated on import and is not part of what
    this assembles, so it is left alone; anything ELSE still locked is a real
    obstacle and is reported by name.
    """
    stuck = []
    for entry in os.listdir(out):
        if entry == ".godot":
            continue
        path = os.path.join(out, entry)
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError:
            stuck.append(path)
    return stuck


def default_out(mission_id):
    """`<factory-root>/_runs/walk_<mission>` -- the repo's scratch convention.

    `_runs/` is gitignored and already holds every throwaway project in this
    workspace (`lux_0801`, `themed_site_probe`, `portable_*_walk`). Deriving it
    from this file's own location rather than the cwd means the command works
    from any directory, and keeps assembled projects out of both the user's
    Projects folder and the mission workspace.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "_runs", "walk_%s" % mission_id)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--out", default=None,
                    help="where to assemble (default <factory>/_runs/"
                         "walk_<mission>; must be outside the workspace)")
    ap.add_argument("--lux-repo", default=None,
                    help="Lux checkout; its addons/lux becomes runtime/lux so "
                         "the walk is lit like the export (default: a sibling "
                         "'lux' next to this tools/ directory)")
    ap.add_argument("--sun-link", action="store_true",
                    help="with --keep-walk-lighting: point Lux at Lot's own "
                         "`Sun` so it DRIVES that light instead of adding a "
                         "second one. The composition half of roadmap item "
                         "92, and the row its table has never carried")
    ap.add_argument("--keep-walk-lighting", action="store_true",
                    help="keep Lot's WorldEnvironment and Sun alongside Lux "
                         "(two suns; measurably worse -- see graft_lux)")
    ap.add_argument("--lot-repo", default=None,
                    help="Lot checkout, for addons/lot (default: read "
                         "tools.local.json beside the workspace)")
    ap.add_argument("--godot", default=None,
                    help="Godot executable, to run an import pass at the end")
    ap.add_argument("--detach-textures", action="store_true",
                    help="lift the embedded images out of the assembled GLBs "
                         "into a shared art/tex/ folder and reference them "
                         "(roadmap 87). The art digest changes, because the "
                         "payload changes -- that is the point, and a later "
                         "shot_diff will correctly say the art moved")
    ap.add_argument("--worldskin", action="store_true",
                    help="bake world-space UVs onto kit modules AT IMPORT via "
                         "Godot's own `import_script/path` hook, which is what "
                         "a pipeline would do (roadmap 76/80/88). Unlike "
                         "--triplanar this needs no runtime script and "
                         "persists in the imported scene")
    ap.add_argument("--triplanar", action="store_true",
                    help="set world-space triplanar UVs on the KIT materials "
                         "at runtime. Off by default: it changes how every "
                         "wall is textured and the walk is meant to preview "
                         "what ships. Use it to A/B the module seam")
    ap.add_argument("--vertex-colors", choices=("report", "force"),
                    default=None,
                    help="roadmap 84. `report` reads back whether the engine "
                         "consumes Zoo's per-vertex wear and changes nothing. "
                         "`force` also switches it on -- that is the "
                         "experiment, not the fix: it restores per-module "
                         "border shading to every wall at full strength")
    ap.add_argument("--no-fixture-lights", action="store_true",
                    help="assemble WITHOUT spawning Zoo's fixture lights. The "
                         "B side of an A/B: emissive lenses glow under the "
                         "WorldEnvironment's glow pass whether or not any "
                         "light is cast, so the eye cannot separate a working "
                         "fixture from a decorative one. Two builds and a "
                         "pixel diff can.")
    args = ap.parse_args(argv)

    jobs = os.path.join(args.lf_dir, "jobs")
    themed = os.path.join(jobs, f"{args.mission_id}.themed_site_assemble")
    compose = os.path.join(jobs, f"{args.mission_id}.presentation_compose")
    if not os.path.isdir(themed):
        sys.stderr.write(
            f"no themed_site_assemble job for {args.mission_id}. Run the "
            f"mission with --art first.\n")
        return 2

    site = newest(themed, "site.tscn")
    walk = newest(themed, "site_walk.tscn")
    building = composed_site(compose)
    if not site or not walk:
        sys.stderr.write("themed site is missing site.tscn or site_walk.tscn; "
                         "the job did not produce a walkable site.\n")
        return 2
    if not building:
        sys.stderr.write("no composed building found; run presentation_compose.\n")
        return 2

    out = args.out or default_out(args.mission_id)
    # The promise in this module's docstring -- "deliberately not written
    # anywhere the pipeline reads" -- needs teeth, because the first default
    # broke it. It put the scratch project at `<lf_dir>/walk/<mission>`, INSIDE
    # the workspace, and the pipeline duly stamped provenance records onto it:
    # site.tscn.provenance.json, project.godot.provenance.json, even
    # site_main.tscn.provenance.json for a file that was never there. Scratch
    # inside the workspace also shows up in every instrument that scans it --
    # `orphan_artifacts.py` reported .themed.tscn / .fit.tscn / .m90.tscn /
    # .p90.tscn as produced-and-unread, and they were this directory.
    real_out = os.path.abspath(out)
    if os.path.abspath(args.lf_dir) + os.sep in real_out + os.sep:
        sys.stderr.write(
            "refusing to assemble inside the workspace (%s).\n"
            "This is throwaway scratch; the pipeline treats anything under\n"
            ".level_factory as job output and stamps provenance on it. Pass\n"
            "--out somewhere outside, e.g. _runs\\walk_<mission>.\n" % out)
        return 2
    lot_repo = args.lot_repo
    if not lot_repo:
        # tools.local.json lives at the WORKSPACE ROOT, beside
        # factory.project.json -- `Workspace.tools_local` is
        # `root / "tools.local.json"`. Both candidates here used to resolve to
        # `<ws>/.level_factory/tools.local.json`, which is not a path that has
        # ever existed, so auto-detection never worked and this tool only ever
        # ran when someone passed --lot-repo by hand. Found 2026-08-29.
        ws_root = os.path.dirname(os.path.abspath(args.lf_dir.rstrip("\\/")))
        local = os.path.join(ws_root, "tools.local.json")
        for cand in (local, os.path.join(args.lf_dir, "tools.local.json")):
            if os.path.exists(cand):
                try:
                    with open(cand, encoding="utf-8") as fh:
                        lot_repo = (json.load(fh).get("repositories") or {}
                                    ).get("lot")
                except (OSError, json.JSONDecodeError):
                    pass
                if lot_repo:
                    break
    lux_repo = args.lux_repo or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lux")
    lux_src = os.path.join(str(lux_repo), "addons", "lux")

    addons_src = os.path.join(str(lot_repo), "godot", "addons", "lot") \
        if lot_repo else None
    if not addons_src or not os.path.isdir(addons_src):
        sys.stderr.write(
            "cannot find Lot's addons/lot -- pass --lot-repo <lot checkout>. "
            "Without the player script the walk scene has nothing to walk "
            "with, and a project that opens to a frozen camera would look "
            "like a level defect.\n")
        return 2

    if os.path.isdir(out):
        stuck = clear_out(out)
        if stuck:
            sys.stderr.write(
                "cannot rebuild %s -- these are locked by another process:\n"
                % out)
            for f in stuck[:8]:
                sys.stderr.write("   " + f + "\n")
            sys.stderr.write(
                "Godot holds a project's files while it has it open. Close the "
                "editor\nand run this again, or pass --out somewhere else.\n")
            return 2
    os.makedirs(out, exist_ok=True)

    # 1 + 2. A VARIED LOT HAS NO SINGLE BUILDING, so the whole single-shell
    #    dance below does not apply to it. `themed_site_assemble` publishes a
    #    self-contained tree -- `site.tscn` naming `lot/<archetype>/site.tscn`,
    #    and each archetype dir carrying its own `art/` and `site_base.glb` --
    #    with no absolute reference anywhere in it. Measured on cold_9001: the
    #    themed root names exactly four paths, all of them `lot/<id>/site.tscn`.
    #
    #    So the rewrite had nothing to fire on, and this tool reported "a
    #    REWRITE that did not fire" -- correctly, and for a reason that was not
    #    a Lot spelling change. Roadmap 37 landed and the walk tool had never
    #    been taught what a site made of different buildings looks like.
    varied = os.path.isdir(os.path.join(os.path.dirname(site), "lot"))
    hits, pkg_hits = [], 0
    if varied:
        copy_into(os.path.dirname(site), out,
                  skip_names={"project.godot", "site.tscn", "site_walk.tscn"})
        shutil.copy2(site, os.path.join(out, "site.tscn"))
    else:
        # The composed building and everything it names at ITS project root.
        copy_into(os.path.dirname(building), out,
                  skip_names={"project.godot", "site.tscn", "site_main.tscn",
                              "HANDOFF.md", "compose.summary.json",
                              "portable_resource_manifest.json"})
        shutil.copy2(building, os.path.join(out, "building.tscn"))

        # The themed site, with the absolute reference made local. Lot writes
        # `res://<absolute path>` in non-portable mode; the file it names is
        # the building copied above, and nothing else in the scene is absolute.
        with open(site, encoding="utf-8") as fh:
            text = fh.read()
        hits = _ABS_REF.findall(text)
        text = _ABS_REF.sub('path="res://building.tscn"', text)
        text, pkg_hits = _PKG_REF.subn('path="res://building.tscn"', text)
        with open(os.path.join(out, "site.tscn"), "w", encoding="utf-8") as fh:
            fh.write(text)

    # 3. The walk scene, Lot's addon, and Lux -- because a walk lit by
    #    nothing is not a review of the level. The scratch project shipped
    #    with no Lux at all until now, so every walkthrough was judging
    #    untextured, unlit geometry against a level that ships lit.
    with open(walk, "r", encoding="utf-8") as fh:
        walk_text = fh.read()
    # Lot's scripts live under addons/lot here; the scene names them at its
    # own directory. Point them at where this project actually put them.
    walk_text, script_hits = _LOT_SCRIPT.subn(
        r'path="res://addons/lot/\1"', walk_text)
    # LF'S OVERLAY, COPIED NOT FORKED. Read at assembly so the preview cannot
    # drift from the export; if LF has moved it, say so rather than silently
    # assembling a walk with no coordinates in it -- which is the state that
    # made a whole afternoon of screenshots unlocatable.
    overlay_ok = os.path.isfile(_OVERLAY_SRC)
    if overlay_ok:
        with open(_OVERLAY_SRC, encoding="utf-8") as fh:
            overlay_text = fh.read()
        with open(os.path.join(out, _OVERLAY_GD_NAME), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(overlay_text)
    else:
        sys.stderr.write("walk_themed: no debug overlay -- %s is missing, so "
                         "this walk has no on-screen coordinates\n"
                         % _OVERLAY_SRC)

    lux_note = "no --lux-repo: walking WITHOUT Lux (not what ships)"
    preset = applied_preset(newest(os.path.join(
        jobs, f"{args.mission_id}.lux_apply"), "lux.applied.tscn"))
    if lux_src and os.path.isdir(lux_src):
        shutil.copytree(lux_src, os.path.join(out, _LUX_DEST))
        walk_text = graft_lux(walk_text,
                              drop_walk_lighting=not args.keep_walk_lighting,
                              preset=preset,
                              spawn_fixtures=not args.no_fixture_lights,
                              triplanar=args.triplanar,
                              vertex_colors=args.vertex_colors,
                              overlay=overlay_ok,
                              sun_link=args.sun_link)
        if not args.no_fixture_lights:
            with open(os.path.join(out, _SPAWN_GD_NAME), "w",
                      encoding="utf-8") as fh:
                fh.write(_SPAWN_GD)
        if args.triplanar:
            with open(os.path.join(out, _TRIPLANAR_GD_NAME), "w",
                      encoding="utf-8") as fh:
                fh.write(_TRIPLANAR_GD)
        if args.vertex_colors:
            with open(os.path.join(out, _VCOL_GD_NAME), "w",
                      encoding="utf-8") as fh:
                fh.write(_VCOL_GD)
        lux_note = os.path.abspath(lux_src) + (
            "" if args.keep_walk_lighting else "  (Lot's own sun/env removed)")
        if args.keep_walk_lighting:
            lux_note += "\n             sun      : " + (
                "SUN LINK -- Lux drives Lot's own sun, one directional light"
                if args.sun_link else
                "Lot's sun KEPT and Lux adds its own -- TWO suns; pass "
                "--sun-link to compose instead")
        if args.no_fixture_lights:
            lux_note += "\n             fixtures : NOT SPAWNED (--no-fixture-lights)"
        lux_note += "\n             preset   : " + (
            preset if preset else
            "NONE FOUND -- walking on Lux's DEFAULT, not this mission's "
            "choice; run lux_apply or the preview lights the wrong level")
    else:
        sys.stderr.write("[walk_themed] " + lux_note + "\n")
    with open(os.path.join(out, "site_walk.tscn"), "w", encoding="utf-8") as fh:
        fh.write(walk_text)
    for extra in ("site.site.gameplay.json", "site.site.lights.json"):
        src = os.path.join(os.path.dirname(walk), extra)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out, extra))
    os.makedirs(os.path.join(out, "addons"), exist_ok=True)
    shutil.copytree(addons_src, os.path.join(out, "addons", "lot"))

    with open(os.path.join(out, "project.godot"), "w", encoding="utf-8") as fh:
        scene_defaults = ""
        if args.worldskin:
            # WRITTEN BEFORE THE PROJECT THAT NAMES IT. Godot resolves
            # `import_script/path` while importing, and a default pointing at
            # a file that does not exist yet imports every GLB unchanged and
            # says nothing about why.
            with open(os.path.join(out, _WORLDSKIN_GD_NAME), "w",
                      encoding="utf-8", newline="\n") as wf:
                wf.write(_WORLDSKIN_GD)
            scene_defaults = _SCENE_DEFAULTS % _WORLDSKIN_GD_NAME
        fh.write(_PROJECT.format(name=args.mission_id, entry="site_walk.tscn",
                                 scene_defaults=scene_defaults))

    # 4. An import pass, if Godot is available. Reported, not swallowed: a
    #    silently failed import is how 13 modules lost their sidecars and
    #    nobody noticed for a week (roadmap 33).
    imported = None
    if args.godot:
        try:
            proc = subprocess.run(
                [args.godot, "--headless", "--path", out, "--import"],
                capture_output=True, timeout=600)
            imported = proc.returncode
            if imported != 0:
                sys.stderr.write(
                    "import pass exited %d; open the project once in the "
                    "editor before walking.\n" % imported)
        except (OSError, subprocess.SubprocessError) as exc:
            sys.stderr.write("import pass did not run: %s\n" % exc)

        # DID THE IMPORT DEFAULT ACTUALLY TAKE? If Godot ignored
        # `[importer_defaults]` the textures went to VRAM Compressed, the
        # headless compressor has no rendering device, and this run either
        # already died with signal 11 or will die the next time the sidecars
        # are honoured. Say which files, not "import failed" -- the crash
        # itself prints a 29-frame backtrace with no debug info and names
        # nothing.
        bad = vram_compressed(out)
        if bad:
            sys.stderr.write(
                "%d texture sidecar(s) came out VRAM Compressed despite\n"
                "[importer_defaults] texture/detect_3d/compress_to=0 in "
                "project.godot.\nThe headless import pass cannot compress "
                "those and will crash on them:\n" % len(bad))
            for f in bad[:8]:
                sys.stderr.write("   " + f + "\n")
            if len(bad) > 8:
                sys.stderr.write("   ... and %d more\n" % (len(bad) - 8))

    # REFUSE A PROJECT THAT CANNOT LOAD. Checked after the import pass so
    # the message is about references rather than about import artifacts.
    missing = unresolved_refs(out)
    if missing:
        sys.stderr.write(
            "assembled a project whose scenes name files it does not have:\n")
        for scene, ref in missing:
            sys.stderr.write("   %-16s -> %s\n" % (scene, ref))
        sys.stderr.write(
            "\nThis is a REWRITE that did not fire, not a missing input: Lot\n"
            "changes how it spells these and the substitutions above are a\n"
            "guess about the current spelling. Opening this would give an\n"
            "empty scene and look like a level defect. Nothing was left in\n"
            "%s.\n" % out)
        clear_out(out)
        return 2

    # BEFORE THE SUBJECT IS STAMPED, because detaching CHANGES THE ART on
    # disk and a digest taken beforehand would describe a payload that no
    # longer exists. The stamp has to describe what is actually in the folder,
    # which is the whole reason it was built (the stale-wear confound of
    # 2026-08-29).
    detached = None
    if args.detach_textures:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import detach_textures
        detached = detach_textures.detach_tree(os.path.join(out, "art"))
        detach_textures.report(detached)

    subject = write_subject(out, args, building, site, walk, preset)

    print("assembled: %s" % out)
    print("  building : %s" % building)
    print("  site     : %s  (%d absolute + %d package reference(s) made local)"
          % (site, len(hits), pkg_hits))
    print("  walk     : %s  (%d lot script ref(s) repointed at addons/lot)"
          % (walk, script_hits))
    if overlay_ok:
        print("  overlay  : %s  (LF's, F3 toggles; pos / building / surface)"
              % _OVERLAY_GD_NAME)
    if detached:
        print("  textures : %d payload(s) shared into art/%s/  "
              "(%d GLB(s) rewritten, %.2f -> %.2f MB)"
              % (detached["payloads"], detached["tex_dir"],
                 detached["rewritten"],
                 detached["glb_bytes_before"] / 1e6,
                 (detached["glb_bytes_after"] + detached["texture_bytes"])
                 / 1e6))
    print("  addons   : %s" % addons_src)
    print("  lux      : %s" % lux_note)
    if args.triplanar:
        print("  uv       : WORLD TRIPLANAR on kit materials (--triplanar) "
              "-- NOT what ships")
    if args.vertex_colors:
        print("  vcolour  : %s (--vertex-colors) -- roadmap 84 probe"
              % args.vertex_colors.upper())
    if imported is not None:
        print("  import   : exit %d" % imported)
    print("  subject  : art %s (%d files)  triplanar=%s fixtures=%s"
          % (subject["art_digest"][:12], subject["art_files"],
             subject["treatment"]["triplanar"],
             subject["treatment"]["fixture_lights"]))
    print()
    print("open it and press F5:")
    print("  godot --path \"%s\"" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Failed as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(2)
