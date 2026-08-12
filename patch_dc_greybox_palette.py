r"""The greybox exports materials, so a surface can be told from another.

    python patch_dc_greybox_palette.py --check
    python patch_dc_greybox_palette.py
    python patch_dc_greybox_palette.py --verify <shell.glb>
    python patch_dc_greybox_palette.py --revert

Run from the FACTORY ROOT.

## The defect

Deli Counter assigns **no material to anything**. There is no `materials.new`,
no `data.materials.append`, no `diffuse_color` anywhere in the repo -- so the
shell exports with an empty glTF material list and Godot renders every surface
in one default. A stair, a wall, a doorway and the floor are the same flat grey
at every distance, and nothing about the geometry says which is which.

That is not a theming gap. The themed pass replaces these surfaces entirely
when it runs; this is about the shell people actually look at while the level
is being designed, walked and graded -- and about every surface the themed pass
never covers, which is all of them: `stair` and `ramp` have no Zoo slot species
at all.

The label already exists. `surface_roles[obj.name] = role` is written at export
for every visual mesh -- `wall` 113, `prop` 25, `window` 24, **`stair` 16**,
`doorway` 8, `floor` 2, `breach` 2, `ceiling` 1, `ramp` 1 on `cr_garage`. The
data to tell these apart has been in `gameplay.json` the whole time and nothing
consumed it for looking.

## The change

A palette keyed by that role, and two lines that paint each visual mesh as it
is labelled. Both call sites already write `surface_roles`; the material is
assigned beside it, so a surface can never carry a role without carrying the
material for it.

Materials are created once per role and shared, so the glTF gains **nine
material entries**, not one per mesh -- Godot loads nine and the shell stays
one draw call per role.

## Why these colours

This is the dev-texture convention, not art direction: **value separates
function, hue names it.** Floor mid, wall light, ceiling dark, so the three
surfaces you orient by are three different values before hue is considered.
Stairs and ramps amber; thresholds cyan; breaches red. The two readings that
matter most -- "I can climb this" and "I can get through here" -- are amber
against neutral and cyan against neutral, so neither depends on telling red
from green.

Roughness stays high everywhere so a light cannot blow a surface out and erase
the value that carries the reading. Metallic is zero: a specular highlight is
the enemy of a flat value read.

They are meant to be tuned. That is why they are one dict at the top of the
class with the reasoning attached, rather than numbers buried at the call site.

## What this is NOT

Not a theme, not pixelcoat, not final art. The next slice binds pixelcoat packs
to these same material names -- a stair pack with hard horizontal tread banding
is the one that earns its cost, because repeated horizontal edges are what make
something read as climbable at fifty metres. **That slice needs named material
slots to bind to, and until now there were none.** This creates them.

The perimeter box and ground plate are Lot's geometry, carry no roles, and are
not touched here. Same treatment, second patch.

## Cost

Every shell's `.glb` changes, so every fingerprint downstream of Deli Counter
moves and the art pass rebuilds once. Geometry is untouched -- collision,
slots, `surface_roles` and every manifest are byte-identical.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

TARGET = Path("deli_counter") / "deli_counter.py"
SIDECAR = ".pre_gbpalette"


PALETTE_OLD = '''    def _empty(self, name, location, collection, rot_z=0.0, size=0.4):'''

PALETTE_NEW = '''    #: Greybox READABILITY palette: (material name, base colour RGBA, roughness)
    #: per surface role.
    #:
    #: Until this existed the shell exported NO materials at all, so every
    #: surface arrived in Godot as one flat default and nothing could be told
    #: apart at any distance. This is the dev-texture convention rather than
    #: art direction: VALUE separates function, hue names it.
    #:
    #: Floor mid, wall light, ceiling dark -- the three surfaces a player
    #: orients by are three different values before hue is considered. Stairs
    #: and ramps amber, thresholds cyan, breaches red: the two readings that
    #: matter most, "I can climb this" and "I can get through here", are amber
    #: and cyan against neutral, so neither depends on telling red from green.
    #:
    #: Roughness stays high so a light cannot blow a surface out and erase the
    #: value that carries the reading; metallic is zero for the same reason.
    #:
    #: Tune them here. They are one dict with the reasoning attached rather
    #: than numbers at a call site, because somebody will want to.
    #: Every colour here is separated from the surface it is SEEN AGAINST by
    #: luminance, not only by hue. `--palette` checks those pairs and fails if
    #: one closes: the first draft had stairs at 0.564 against a 0.522 floor,
    #: a gap of 0.042, which is amber and grey reading as one surface in
    #: greyscale, in low light, or to a colourblind player -- on the single
    #: case this palette exists for.
    GREYBOX_PALETTE = {
        # seen against nothing -- these ARE the frame of reference
        "floor":   ("gb_floor",     (0.52, 0.52, 0.55, 1.0), 0.90),  # 0.522
        "ceiling": ("gb_ceiling",   (0.22, 0.22, 0.25, 1.0), 0.95),  # 0.222
        "wall":    ("gb_wall",      (0.72, 0.71, 0.68, 1.0), 0.88),  # 0.710
        # climbable: the brightest things on the site, seen against the FLOOR.
        # Stair and ramp are deliberately close to each other -- same
        # affordance, same family -- and far from what they stand on.
        "stair":   ("gb_stair",     (1.00, 0.78, 0.32, 1.0), 0.80),  # 0.794
        "ramp":    ("gb_ramp",      (0.95, 0.70, 0.25, 1.0), 0.80),  # 0.721
        # A ladder is the same affordance and the hardest to place: it is seen
        # against the WALL it is bolted to (0.710) and against the ROOF it
        # arrives at, not against the floor. It gets the brightest value on the
        # site because it is the smallest thing that has to be found.
        "ladder":  ("gb_ladder",    (1.00, 0.90, 0.55, 1.0), 0.78),  # 0.897
        # openings: seen against the WALL they are cut into, and DARK, because
        # a hole is darker than the thing it is a hole in.
        "doorway": ("gb_threshold", (0.05, 0.42, 0.50, 1.0), 0.75),  # 0.347
        "breach":  ("gb_breach",    (0.74, 0.24, 0.20, 1.0), 0.85),  # 0.343
        "window":  ("gb_window",    (0.42, 0.55, 0.62, 1.0), 0.35),  # 0.527
        # the deck you come out onto. Seen against the sky and against whatever
        # stands on it, NOT against the interior floor -- the two never share a
        # view, so they are allowed to sit near each other in value.
        "roof":    ("gb_roof",      (0.52, 0.56, 0.60, 1.0), 0.90),  # 0.555
        # cover: seen against the floor it stands on
        "prop":    ("gb_prop",      (0.28, 0.30, 0.26, 1.0), 0.92),  # 0.293
    }

    def _greybox_material(self, role):
        """The shared material for ``role``, made once. None for an unlisted role.

        Nodes rather than ``diffuse_color``: the glTF exporter reads the
        Principled BSDF and ignores the viewport colour entirely, so setting
        the latter alone would look correct in Blender and export nothing --
        which is the failure this patch exists to end, wearing a subtler hat.

        The BSDF is found BY TYPE, not by the name "Principled BSDF": that
        string is localised in some Blender builds, and a lookup that silently
        returns None would paint every surface the default white and report no
        error.
        """
        entry = self.GREYBOX_PALETTE.get(role)
        if entry is None:
            return None
        name, rgba, roughness = entry
        mat = bpy.data.materials.get(name)
        if mat is not None:
            return mat
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes
                     if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = rgba
            bsdf.inputs["Roughness"].default_value = roughness
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.0
        mat.diffuse_color = rgba          # viewport parity, exports nothing
        return mat

    def _paint(self, obj, role):
        """Give a visual mesh the material its role reads by.

        Assigned to the MESH, and skipped when the mesh already carries one.
        Modular segments share a mesh datablock across every instance -- the
        share key is role plus dims, so a shared mesh always has one role and
        painting it once is correct. Appending per object would add a duplicate
        slot to the same datablock on every reuse.
        """
        mat = self._greybox_material(role)
        data = getattr(obj, "data", None)
        if mat is None or data is None or not hasattr(data, "materials"):
            return
        if len(data.materials):
            return
        data.materials.append(mat)

    def _empty(self, name, location, collection, rot_z=0.0, size=0.4):'''


MODULE_OLD = '''                if role:
                    self.surface_roles[obj.name] = role'''

MODULE_NEW = '''                if role:
                    self.surface_roles[obj.name] = role
                    self._paint(obj, role)'''

SOLID_OLD = '''        if role is not None and collection is self.VISUAL:
            self.surface_roles[obj.name] = role'''

SOLID_NEW = '''        if role is not None and collection is self.VISUAL:
            self.surface_roles[obj.name] = role
            # Painted where it is labelled, so a surface cannot carry a role
            # without carrying the material that role reads by.
            self._paint(obj, role)'''


EDITS = ((PALETTE_OLD, PALETTE_NEW),
         (MODULE_OLD, MODULE_NEW),
         (SOLID_OLD, SOLID_NEW))

_CRLF = "\r\n"


def _find(body: str, anchor: str) -> tuple[str, int]:
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


# ------------------------------------------------------------------- verify
def _glb_json(path: Path) -> dict:
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise SystemExit(f"{path.name} is not a binary glTF")
    off = 12
    while off < len(data):
        length, kind = struct.unpack_from("<II", data, off)
        if kind == 0x4E4F534A:
            return json.loads(data[off + 8: off + 8 + length])
        off += 8 + length
    raise SystemExit(f"{path.name} has no JSON chunk")


def _verify(glb: Path) -> int:
    """What the exported shell actually carries. Reads only; pure stdlib."""
    doc = _glb_json(glb)
    mats = doc.get("materials") or []
    print(f"\n  {glb.name}")
    print(f"  materials  {len(mats)}")
    if not mats:
        print("  FAIL: no materials in the export. Every surface is one flat "
              "default, which is the state this patch exists to end.")
        return 1

    used = {}
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            idx = prim.get("material")
            if idx is not None:
                used[idx] = used.get(idx, 0) + 1

    for i, mat in enumerate(mats):
        pbr = mat.get("pbrMetallicRoughness") or {}
        colour = pbr.get("baseColorFactor")
        shown = ("(" + ", ".join(f"{c:.2f}" for c in colour[:3]) + ")"
                 if colour else "(none)")
        print(f"    {mat.get('name', '<unnamed>'):<14} base {shown:<22} "
              f"rough {pbr.get('roughnessFactor', '-')!s:<6} "
              f"used by {used.get(i, 0)} primitive(s)")

    # An unpainted COLLISION mesh is correct -- Godot never draws it, and the
    # palette is deliberately only applied to the VISUAL collection. An
    # unpainted VISUAL mesh is a role the palette does not cover, and lumping
    # the two into one count is how a missing role hides behind a big number.
    collision, visual = 0, []
    for mesh in doc.get("meshes") or []:
        name = mesh.get("name", "")
        for prim in mesh.get("primitives") or []:
            if prim.get("material") is not None:
                continue
            if name.endswith(("-colonly", "-convcolonly")) or "_col" in name:
                collision += 1
            else:
                visual.append(name or "<unnamed>")

    print(f"  unpainted: {collision} collision (correct), "
          f"{len(visual)} visual")
    bad = 0
    if visual:
        seen = {}
        for name in visual:
            seen[name] = seen.get(name, 0) + 1
        print("  FAIL: visual meshes with no material -- their role is missing "
              "from GREYBOX_PALETTE:")
        for name, count in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
            print(f"    {name}  x{count}")
        bad = 1
    if len({m.get("name") for m in mats}) < 2:
        print("  FAIL: one material. Nothing can be told from anything else.")
        bad = 1
    if not any(used.values()):
        print("  FAIL: materials exist but no primitive references one.")
        bad = 1
    if not bad:
        print("  every visual primitive carries the material its role reads by")
    return bad


#: Pairs that have to stay apart, and why. A surface is only legible against
#: what it is actually SEEN against: a stair against the floor it rises from, a
#: doorway against the wall it is cut into. Comparing everything to everything
#: would fail on pairs that never share a view.
_CRITICAL_PAIRS = (
    ("floor", "wall", "the two surfaces you orient by"),
    ("wall", "ceiling", "the two surfaces you orient by"),
    ("floor", "stair", "CLIMBABLE against what it rises from"),
    ("floor", "ramp", "climbable against what it rises from"),
    ("wall", "doorway", "an opening against the wall it is cut into"),
    ("wall", "breach", "an opening against the wall it is cut into"),
    ("floor", "prop", "cover against the floor it stands on"),
    ("roof", "prop", "cover against the deck it stands on"),
    ("roof", "stair", "the way up, against the deck it arrives at"),
    ("wall", "ladder", "a ladder against the wall it is bolted to"),
    ("floor", "ladder", "CLIMBABLE against what it rises from"),
    ("roof", "ladder", "the way up, against the deck it arrives at"),
)

#: Below this, two surfaces read as one in greyscale, in low light, or to a
#: colourblind player. 0.15 of relative luminance is about a value step a
#: person reliably sees on a matte surface at distance.
_MIN_VALUE_GAP = 0.15


def _luminance(rgba) -> float:
    return 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]


def _palette(path: Path) -> int:
    """Check the value separation the palette's own comment claims."""
    import re
    src = path.read_text(encoding="utf-8")
    match = re.search(r"GREYBOX_PALETTE = \{(.*?)\n    \}", src, re.S)
    if match is None:
        print("  no GREYBOX_PALETTE found -- apply the patch first")
        return 2
    rows = re.findall(
        r'"(\w+)":\s*\("(\w+)",\s*\(([0-9.]+), ([0-9.]+), ([0-9.]+)[^)]*\),'
        r'\s*([0-9.]+)', match.group(1))
    lum = {}
    print()
    for role, name, r, g, b, rough in rows:
        lum[role] = _luminance((float(r), float(g), float(b)))
        print(f"  {role:<9} {name:<13} luminance {lum[role]:.3f}   "
              f"rough {rough}")
    print()
    bad = 0
    for a, b, why in _CRITICAL_PAIRS:
        if a not in lum or b not in lum:
            continue
        gap = abs(lum[a] - lum[b])
        flag = "ok  " if gap >= _MIN_VALUE_GAP else "THIN"
        if gap < _MIN_VALUE_GAP:
            bad = 1
        print(f"  [{flag}] {a:>7} vs {b:<9} {gap:.3f}   {why}")
    print()
    if bad:
        print(f"  FAIL: a pair is under {_MIN_VALUE_GAP} of luminance. Hue is "
              f"doing work value should be doing,\n  and it stops doing it in "
              f"greyscale, in low light, and for a colourblind player.")
    else:
        print(f"  every pair that shares a view is separated by at least "
              f"{_MIN_VALUE_GAP} of luminance")
    return bad


def main(argv: list[str]) -> int:
    if "--palette" in argv:
        return _palette(Path.cwd() / TARGET)
    if "--verify" in argv:
        rest = [a for a in argv[argv.index("--verify") + 1:]
                if not a.startswith("--")]
        if not rest:
            print("--verify needs a path to a built shell .glb")
            return 2
        return _verify(Path(rest[0]))

    path = Path.cwd() / TARGET
    if not path.is_file():
        raise SystemExit(f"cannot find {TARGET} -- run from the factory root")
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    if "--revert" in argv:
        if not side.is_file():
            print(f"no sidecar at {side.name}")
            return 2
        path.write_bytes(side.read_bytes())
        print(f"  reverted   {path.name}")
        return 0

    done = sum(1 for _o, new in EDITS if _find(body, new)[1] == 1)
    if done == len(EDITS):
        print("  already applied")
        return 0
    if done:
        print(f"REFUSING: {done} of {len(EDITS)} edits already present")
        return 1

    out = body
    for old, new in EDITS:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: expected 1 occurrence, found {count}: "
                  f"{old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)
    data = out.encode("utf-8")

    if "--check" in argv:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})")
    print(f"  sha256       {hashlib.sha256(data).hexdigest()[:16]}")
    print()
    print("  Rebuild a shell, then:")
    print("    python patch_dc_greybox_palette.py --verify "
          "deli_counter\\build\\<id>.glb")
    print("  EXPECT nine materials, every visual primitive referencing one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
