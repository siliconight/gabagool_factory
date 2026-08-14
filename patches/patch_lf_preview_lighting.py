r"""The walk preview's dev light rig stops flattening the level it is lighting.

    python patch_lf_preview_lighting.py --rig      # the numbers, no files touched
    python patch_lf_preview_lighting.py --check
    python patch_lf_preview_lighting.py
    python patch_lf_preview_lighting.py --verify <walk.tscn>
    python patch_lf_preview_lighting.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## A retraction first

I reported that the walk preview was unlit, on this evidence:

    grep -c "Light3D|WorldEnvironment|DirectionalLight" site.tscn  ->  0

`site.tscn` is the CONTENT scene. The rig is not in it and was never meant to
be -- `build_walk_preview` writes the rig into `walk.tscn`, the wrapper, and
says so in the comment right above the code that does it. I grepped the wrong
file and called it a finding. This is the same mistake shape as the eight
before it: **an artefact read as evidence about a process it is not part of.**

`lot_demo_001_walk/walk.tscn` on disk, 1,264 bytes, does have a rig:

    [node name="WorldEnvironment" type="WorldEnvironment" parent="PreviewLighting"]
    [node name="Sun" type="DirectionalLight3D" parent="PreviewLighting"]

So the preview is lit. The claim "no palette will fix flatness that's actually
missing light" was wrong on its premise, and `patch_lot_greybox_palette.py`'s
"What this does NOT fix" section is wrong with it.

## The real defect, which is worse than missing light

Here is the whole rig, as shipped:

    ambient_light_source = 2                          # COLOR
    ambient_light_color = Color(0.72, 0.73, 0.77, 1)
    ambient_light_energy = 1.4
    ...
    Sun: light_energy = 0.6
         shadow_enabled = false

**Ambient light is directionless.** It adds the same amount to a face pointing
up, a face pointing north and a face pointing into a corner. It cannot produce
form shading, because form shading IS the difference between faces at different
angles, and ambient has no angle.

The one light in the scene that can shade form runs at **0.6**, against
directionless fill at **1.4**, with **shadows off**. Better than 2:1 in favour
of the term that flattens everything. Under that rig a wall and the floor it
stands on, at the same albedo, render at very nearly the same pixel value --
which is the report, exactly: *"the flat gray makes it hard to see the geometry
and intentionality of the designs."*

And the code says why, in its own comment:

    #     preview adds a basic dev rig: sky + strong colour ambient (geometry is
    #     always visible, independent of renderer/sky quirks) + a sun for
    #     definition.

It was tuned so nothing could ever be too dark to see. It bought that guarantee
with form. Both were reasonable to want; only one of them was measured.

## The change

Four numbers and one matrix in the non-Lux branch of `build_walk_preview`.
No new nodes, no new resources, `load_steps` unchanged.

    ambient_light_energy   1.4  ->  0.30     fill, not the main light
    Sun light_energy       0.6  ->  1.70     the term that carries form
    shadow_enabled       false  ->  true     + PSSM4, 260 m, biases
    Sun transform          pitch only  ->  pitch + 40 deg yaw

Ratio goes from 0.43 : 1 (sun : ambient) to 5.67 : 1. A face square to the sun
reads about 2.0; a face turned away reads 0.30; the same albedo now spans most
of the visible range instead of a sliver of it.

The yaw is not decoration. The old sun was a pure pitch about X, so its
direction was (0, -0.91, -0.41) -- dead-on to two of the four perimeter walls
and exactly grazing the other two, which means `perim_E` and `perim_W` were
lit identically and read as one surface. Yawing 40 degrees gives
(-0.26, -0.91, -0.31): every one of the four cardinal walls now takes a
different amount, and so does every building face. The basis is orthonormal to
1e-6, checked by `--rig`.

Ambient does not go to zero. A surface facing directly away from the sun with
shadows on would otherwise be pure black, and an unreadable dark is no better
than an unreadable flat. 0.30 is a floor, which is what fill is for.

## What this does NOT fix, stated carefully this time

`lux_apply` output still never reaches the preview, and that is a real and
separate defect:

  * `walk_content_dir` returns `<mission>.themed_site_assemble/out` and never
    looks at `<mission>.lux_apply/out` at all.
  * `_find_level_scene` prefers a file named `site_lux.tscn`. `lux_apply`
    writes `lux.applied.tscn` (planner.py, `expected_outputs`). `grep -rn
    "site_lux"` over the whole tree returns exactly two lines, both inside
    `_find_level_scene` itself -- nothing writes that name, nothing else reads
    it. That preference branch has never fired.

Fixing it is not a rename: lux's `out/` holds the scene and its two sidecars
and nothing else, while the buildings it instances live in the input directory,
so something has to decide where the two get put together. That is a design
question and it gets its own patch rather than a guess bolted onto this one.

This rig is what you are actually looking at today, and it is the thing between
you and reading the geometry.
"""
from __future__ import annotations

import hashlib
import math
import re
import sys
from pathlib import Path

WP = Path("level_factory") / "packages" / "preview" / "walk_preview.py"
SIDECAR = ".pre_previewlight"

AMBIENT_ENERGY = 0.30
SUN_ENERGY = 1.70
SUN_YAW_DEG = 40.0
SUN_ELEVATION_DEG = 66.0


def _basis(yaw_deg: float, elev_deg: float):
    """The Sun's orthonormal basis. A DirectionalLight3D shines along -Z."""
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    ce, se = math.cos(math.radians(elev_deg)), math.sin(math.radians(elev_deg))
    cols = ((1.0, 0.0, 0.0), (0.0, ce, -se), (0.0, se, ce))
    return tuple((c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2])
                 for v in cols)


def _transform(yaw_deg: float, elev_deg: float) -> str:
    x, y, z = _basis(yaw_deg, elev_deg)
    nums = ", ".join(f"{v:.4f}" for v in x + y + z)
    return f"Transform3D({nums}, 0, 40, 0)"


def _rig(verbose: bool = True) -> int:
    x, y, z = _basis(SUN_YAW_DEG, SUN_ELEVATION_DEG)
    bad = 0

    def norm(v):
        return math.sqrt(sum(a * a for a in v))

    def dot(a, b):
        return sum(p * q for p, q in zip(a, b))

    for name, v in (("x", x), ("y", y), ("z", z)):
        if abs(norm(v) - 1.0) > 1e-6:
            bad = 1
            if verbose:
                print(f"    basis.{name} is not unit length: {norm(v):.8f}")
    for a, b, label in ((x, y, "x.y"), (y, z, "y.z"), (x, z, "x.z")):
        if abs(dot(a, b)) > 1e-6:
            bad = 1
            if verbose:
                print(f"    basis {label} not orthogonal: {dot(a, b):.8f}")

    direction = tuple(-v for v in z)
    if verbose:
        print("  sun")
        print(f"    energy           {SUN_ENERGY:.2f}")
        print(f"    shadows          on (PSSM 4 splits, 260 m)")
        print(f"    yaw / elevation  {SUN_YAW_DEG:.0f} deg / "
              f"{SUN_ELEVATION_DEG:.0f} deg")
        print(f"    direction        ({direction[0]:+.3f}, {direction[1]:+.3f},"
              f" {direction[2]:+.3f})")
        print(f"    basis            orthonormal to 1e-6"
              if not bad else "    basis            BAD")
        print()
        print("  ambient (directionless fill -- cannot shade form)")
        print(f"    energy           {AMBIENT_ENERGY:.2f}")
        print()
        print(f"  sun : ambient      {SUN_ENERGY / AMBIENT_ENERGY:.2f} : 1"
              f"      (was {0.6 / 1.4:.2f} : 1)")
        print()
        print("  what a face reads, same albedo, before and after")
        for label, ndotl in (("square to the sun", 1.0),
                             ("45 deg to the sun", 0.707),
                             ("turned away", 0.0)):
            was = 1.4 + 0.6 * ndotl
            now = AMBIENT_ENERGY + SUN_ENERGY * ndotl
            print(f"    {label:<20} was {was:.2f}   now {now:.2f}")
        spread_was = (1.4 + 0.6) - 1.4
        spread_now = (AMBIENT_ENERGY + SUN_ENERGY) - AMBIENT_ENERGY
        print(f"    spread across orientations   was {spread_was:.2f}"
              f"   now {spread_now:.2f}")
        print()
        print("  FAIL" if bad else "  rig holds")
    return bad


# --------------------------------------------------------------------------
# the edit
# --------------------------------------------------------------------------

RIG_OLD = """            'ambient_light_source = 2\\n'
            'ambient_light_color = Color(0.72, 0.73, 0.77, 1)\\n'
            'ambient_light_energy = 1.4\\n\\n'
            '[node name="Walk" type="Node3D"]\\n\\n'
            '[node name="PreviewLighting" type="Node3D" parent="."]\\n\\n'
            '[node name="WorldEnvironment" type="WorldEnvironment" parent="PreviewLighting"]\\n'
            'environment = SubResource("Env")\\n\\n'
            '[node name="Sun" type="DirectionalLight3D" parent="PreviewLighting"]\\n'
            'transform = Transform3D(1, 0, 0, 0, 0.4, -0.9, 0, 0.9, 0.4, 0, 15, 0)\\n'
            'light_energy = 0.6\\n'
            'shadow_enabled = false\\n\\n'"""

RIG_NEW = """            'ambient_light_source = 2\\n'
            'ambient_light_color = Color(0.72, 0.73, 0.77, 1)\\n'
            # FILL, not the main light. Ambient is directionless: it adds the
            # same amount to a face pointing up and a face pointing sideways,
            # so it cannot shade form -- form shading IS the difference
            # between orientations. At 1.4 against a 0.6 sun it was better
            # than 2:1 in favour of the term that flattens, and a wall read
            # the same value as the floor it stood on. It does not go to zero:
            # with shadows on, a face turned fully away would be black, and an
            # unreadable dark is no better than an unreadable flat.
            'ambient_light_energy = 0.3\\n\\n'
            '[node name="Walk" type="Node3D"]\\n\\n'
            '[node name="PreviewLighting" type="Node3D" parent="."]\\n\\n'
            '[node name="WorldEnvironment" type="WorldEnvironment" parent="PreviewLighting"]\\n'
            'environment = SubResource("Env")\\n\\n'
            '[node name="Sun" type="DirectionalLight3D" parent="PreviewLighting"]\\n'
            # Pitch AND yaw. The old basis was a pure rotation about X, so the
            # sun pointed at (0, -0.91, -0.41): square-on to perim_N and
            # perim_S and exactly grazing perim_E and perim_W, which left the
            # two pairs lit identically. 40 degrees of yaw gives
            # (-0.26, -0.91, -0.31) and every cardinal wall takes a different
            # amount. Orthonormal to 1e-6; `patch_lf_preview_lighting.py --rig`
            # recomputes and checks it.
            'transform = Transform3D(0.766, 0, -0.6428, -0.5872, 0.4067, -0.6998, 0.2614, 0.9135, 0.3116, 0, 40, 0)\\n'
            'light_energy = 1.7\\n'
            # Shadows are the other half of reading geometry: they say which
            # solid is in front of which, and where a solid meets the ground.
            # 260 m covers the long axis of a generated site (measured: the
            # lot_demo plate runs 309 m) without splitting the cascade so thin
            # it shimmers.
            'shadow_enabled = true\\n'
            'directional_shadow_mode = 2\\n'
            'directional_shadow_max_distance = 260.0\\n'
            'shadow_bias = 0.06\\n'
            'shadow_normal_bias = 2.0\\n\\n'"""


EDITS = {WP: ((RIG_OLD, RIG_NEW),)}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


# --------------------------------------------------------------------------
# --verify: read a built walk.tscn and report the rig it actually carries
# --------------------------------------------------------------------------

def _verify(scene: Path) -> int:
    text = scene.read_text(encoding="utf-8", errors="replace")

    def num(pattern, default=None):
        m = re.search(pattern, text, re.M)
        return float(m.group(1)) if m else default

    has_lux_root = "addons/lux" in text
    amb = num(r"^ambient_light_energy = ([\d.]+)")
    sun = num(r"^light_energy = ([\d.]+)")
    shadow = re.search(r"^shadow_enabled = (true|false)", text, re.M)
    lights = len(re.findall(r'type="(?:\w*Light3D|WorldEnvironment)"', text))

    print(f"  {scene}")
    print(f"    lighting owner   "
          + ("lux (content-owned)" if has_lux_root else "preview rig"))
    print(f"    light nodes      {lights}")
    if amb is None and sun is None:
        print("    no rig in this scene -- is this the CONTENT scene rather "
              "than walk.tscn? The rig lives in the wrapper.")
        return 1
    print(f"    ambient energy   {amb}")
    print(f"    sun energy       {sun}")
    print(f"    shadows          {shadow.group(1) if shadow else '(absent)'}")
    if amb and sun:
        print(f"    sun : ambient    {sun / amb:.2f} : 1")

    bad = 0
    if amb is not None and abs(amb - AMBIENT_ENERGY) > 1e-6:
        bad = 1
    if sun is not None and abs(sun - SUN_ENERGY) > 1e-6:
        bad = 1
    if shadow and shadow.group(1) != "true":
        bad = 1
    if bad:
        print("    STALE: this preview predates the patch -- rebuild it "
              "(`lf walk <mission>`) and verify again")
    else:
        print("    this preview carries the patched rig")
    return bad


def main(argv: list[str]) -> int:
    if "--rig" in argv:
        return _rig()

    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to a built walk.tscn")
        return _verify(Path(argv[i + 1]))

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding "
                             f"level_factory/)")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    if _rig(verbose=False):
        print("REFUSING: the sun basis is not orthonormal -- fix the numbers "
              "before writing them into a scene.")
        return 1

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  Rig:   python patch_lf_preview_lighting.py --rig")
        print("  Then:  the preview is written at `lf walk` time, so REBUILD "
              "it --")
        print("           python $LF walk lot_demo_001")
        print("         and verify what landed:")
        print("           python patch_lf_preview_lighting.py --verify \\")
        print("             lot-demo-ws\\.level_factory\\preview\\"
              "lot_demo_001_walk\\walk.tscn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
