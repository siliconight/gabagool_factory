r"""Roadmap items 43-45, and item 42's status caught up with reality.

    python patch_roadmap_43_45.py --check
    python patch_roadmap_43_45.py
    python patch_roadmap_43_45.py --selftest
    python patch_roadmap_43_45.py --revert

Run from the FACTORY ROOT. Then regenerate the derived table:

    python tools/roadmap_status.py --write

WHAT LANDS

    43  `run --target presentation` plans no art stages. Found today, by a
        test suite that had not been collectible for weeks.
    44  Semantic Proxy Replacement -- Zoo art variants standing in for
        graybox blocks, with the graybox collision still authoritative.
    45  Surface Dressing -- collisionless instanced detail geometry.

44 and 45 come from three documents the user wrote:
`Semantic_Proxy_Replacement_Art_Pass`, `City Collision ArtPass Substitutes`,
`Surface_Dressing_Level_Depth_Guide`. The items summarise the decisions and
name the questions those documents leave open; they are not a substitute for
promoting the specs into `docs/` when the work starts, the way
EXPORT_NAMING.md and FUNCTIONAL_LOCK.md were.

AND ITEM 42 IS UPDATED, BECAUSE ITS STATUS IS NOW FALSE

It reads `NARROWED 2026-08-14 -- scheme accepted and corrected; nothing
produces it yet`. Something produces it: 0.26.0 landed the build directory,
0.27.0 the archive name, the stable interior folder and `LF_MANIFEST.json`.
A real package was built and its manifest read. Leaving a status that says
nothing produces it is the exact failure this file's status convention
exists to prevent.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r4345"

OLD_42 = (
    "*STATUS: NARROWED 2026-08-14 -- scheme accepted and corrected; nothing "
    "produces it yet.")
NEW_42 = (
    "*STATUS: NARROWED 2026-08-14 -- stage 1 SHIPPED and proven on a real "
    "package: level_factory 0.26.0 (build dir), 0.27.0 (archive name, stable "
    "interior folder, LF_MANIFEST.json), factory-v1.19.0. "
    "`LF_lot_demo_001_s5219_20260814T211037Z_f1.18.0_portable-godot.zip`, 213 "
    "entries all under `LF_lot_demo_001/`, manifest read back and correct. "
    "REMAINING: the interior renames -- `lot/<building>/` -> "
    "`sites/<building>/` and dropping `assets/lot.glb` -- which move `res://` "
    "paths inside the package and want their own portability run. Original "
    "note follows.")

INSERT = '''*STATUS: OPEN 2026-08-14 -- found by `pytest level_factory/tests`, which had been aborting in collection since an unknown date; nine tests across tests/service and tests/integration fail and all nine trace to this*

**43. A whole CLI spelling stopped working and nothing noticed.**
`run --target presentation` plans no art stages. The run reports
`deli_generate ... cache`, `lot_assemble ... cache`, `Structural checks
passed`, exits 0, and stops. No `lux_apply`, no `dispatch_handoff`, no
presentation compose.

Nine tests say so, in nine different ways:

```
missing stage lux_apply                       test_presentation_export
no presentation previews for m1               test_advanced_review
m1.dispatch_handoff/out/mission.tscn missing  test_batch_production
presentation_status 'pending' != 'ready'      test_facade
job_console("m1.lux_apply") is None           test_facade
node_detail state 'PLANNED' != 'SUCCEEDED'    test_facade
```

`_resolve_layers` treats `--target` as the legacy path -- "explicit
`--art`/`--gameplay` win; otherwise fall back to the legacy `--target`
mapping." The first place to look is `packages/pipeline/planner.py`'s
`layers_for_target`: it either still knows the word `presentation` or it does
not, and it is one function.

**The interesting part is not the mapping.** It is that a documented CLI
spelling could stop planning anything at all, and the only things still
exercising it were tests that had not run since
`tests/test_presentation_fingerprint.py` began failing at import. Collection
aborts before any test in the directory executes, so one broken import took
`tests/integration` and `tests/service` dark together. level_factory 0.32.0
fixed the import; these nine are what was behind it.

Whether they are pre-existing or were exposed by 0.32.0's new `composer`
fingerprint key -- which turns former cache hits into real runs -- is
answered by reverting 0.32.0 and running the two directories again. Do that
before assuming either.

*STATUS: OPEN 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPass Substitutes`; nothing built. The gate it needs was built today and works*

**44. The green boxes could be cars, and the collision would not change.**
A graybox block is a semantic placeholder: it says what belongs here, not
what it looks like. Its transform already defines position, rotation, scale
and gameplay footprint. Replace the placeholder with an art asset, keep the
block's collision as the authority, and a validated level becomes a
believable one without reopening traversal.

```
Graybox Block -> Identify Object Type -> Select Art Asset
              -> Fit / Orient -> Retain Proxy Collision
              -> Add Non-Collision Detail
```

**The abstraction that makes a small library go far** is shape to category
to variants, not block to model:

```
BOX_MEDIUM_CITY     -> ATM / vending machine / utility cabinet / news rack
BOX_LARGE_CITY      -> dumpster / generator / HVAC / pallet stack
BOX_VEHICLE         -> sedan / taxi / police car / abandoned car
BOX_LONG_CITY       -> bench / planter / barrier / bike rack
CYLINDER_SMALL_CITY -> bollard / hydrant / parking meter / trash can
```

Roughly twenty "universal" proxies -- car, van, dumpster, ATM, vending
machine, utility cabinet, concrete planter, bench, mailbox, news box, trash
can, pallet stack, crate stack, construction barrier, shipping container,
HVAC unit, generator, vendor kiosk, bus shelter, trash pile -- cover most
city graybox. Zoo owns those families, their pivots, bounds, tags and
variation sets. Pixelcoat skins them, which is where the visual variety
multiplies again: one mesh family, several material treatments.

**Art is allowed to exceed the collision.** Mirrors, antennas, handles,
signs, cables, bumpers may protrude and carry no collision of their own.
That is the whole point -- dimensionality without changing navigation.

**Reversible, always.** A designer must be able to reveal the proxy. The
relationship between gameplay object and visual representation stays
explicit rather than being consumed by the substitution.

WHAT THIS NEEDS FIRST, AND IT IS NOT CODE

**Something must name the category, and today nothing does.** Lot's
`markers` carry a `type` (`attacker_spawn`, `cover`), and Deli's carry ids
like `COVER_LOW_AUTO_DESK_MANAGER_OFFICE_0` -- but a *prop block* with a
`BOX_MEDIUM_CITY` tag does not exist in either vocabulary. Deli Counter
emits the block; something has to say what it stands for. That is a contract
question between DC and Zoo and it comes before any substitution code.

**The gate this needs already exists, as of today.** The functional lock now
protects `openings`, `surfaces`, `ground` and the anchor registry, refuses to
be written empty, and reports drift on a real comparison -- level_factory
0.29.0 through 0.31.0, factory-v1.21.0. A proxy replacement that quietly
changed collision would move `collision_fingerprint`, and until this morning
that hash could not have noticed. Run the substitution after the functional
shell lock and the lock is the acceptance test.

**Rejection is a feature.** An asset that cannot fit the gameplay volume
within the allowed scale and yaw limits is refused, not squeezed. Item 41 is
the same boundary from the other side -- structural art routed through the
decoration path -- and both want `allowed_inward_intrusion_m` in the slot
manifest with something that reads it.

*STATUS: OPEN 2026-08-14 -- specified by `Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is the same boundary approached from the other side*

**45. Large playable surfaces are visually flat, and the fix is not more
grass.** Surface Dressing is collisionless instanced detail placed across
gameplay surfaces for relief, silhouette breakup, parallax and contact --
without adding gameplay relief. The problem it solves is that a clean
graybox reads as a diagram.

**The stack is layered responsibility, not one increasingly complicated
mesh:**

```
0  Gameplay geometry   floors, walls, stairs, cover      COLLISION AUTHORITY
1  Macro environment   buildings, cliffs, machinery      silhouette and space
2  Mid dressing        pipes, cables, crates, boards     "somebody authored this"
3  Surface dressing    grass, rubble, litter, roots      relief; collisionless
4  Surface detail      decals, cracks, grime             no geometry at all
5  Atmosphere          fog, dust, particles, shafts      depth through air
```

**Core rule: gameplay complexity and visual complexity scale
independently.** A level keeps simple collision and renders a dense
presentation layer.

WHERE IT LIVES IN THIS TOOLCHAIN

Post-lock, and every tool already has the right job for it. Deli Counter
exposes safe surfaces and semantic zones and is not modified by decorative
placement. Zoo owns the dressing asset families with `collision_policy:
none`. Pixelcoat breaks flatness in material before geometry is added --
texture noise and mesh noise must not compete at the same frequency. Patina
is the natural home for placement logic: clusters, seam dressing,
environmental cause, density, negative space. Lux makes relief produce
readable contact shadows without paying for shadow on every pebble. Dispatch
keeps it under a presentation branch that can be culled or disabled whole.
Level Factory gates it and can fail a build.

**The manifest is the deliverable, not the scene.** `surface_zone_id`,
`asset_set`, `placement_mode` (scatter / seam / cluster / anchor / spline /
authored), `density`, `scale_range`, `yaw_range`, `height_band`,
`collision_policy`, `shadow_policy`, `exclusion_tags`, `seed`,
`quality_tier`. Deterministic from a seed, or it is not reproducible and
does not belong in this pipeline.

**Placement rules that are art direction, not code**, and which the manifest
has to be able to express: cluster rather than scatter evenly, because
uniform spacing reads as procedural noise; anchor detail to causes -- growth
at cracks and moisture, rubble at damage, trash against walls and traffic
edges; dress intersections first, because wall-to-floor and prop-to-ground
seams are where modular construction shows; use two to four height bands
(2-10 cm micro, 10-30 cm cover, 30-70 cm medium, selective 70-150 cm).

**The test, and it is a good one:** hide the dressing layer and the level
should still play correctly. Show it and the same level should feel
materially richer. If a dressed level *plays* differently, the presentation
layer is too intrusive -- and Laser Tag is the instrument that says so,
against its own pre-art baseline.

DEFINITION OF DONE, AND ONE LINE OF IT IS NEWLY CHECKABLE

Collision unchanged from the locked version. Navigation regression passes.
Objective anchors, doors, interactables and cover language stay readable. No
decorative asset makes a believable but false traversal promise. No visible
uniform scatter from primary views. Density reducible or disableable without
affecting gameplay. Runtime budgets pass in Godot on worst-case views, not
empty scenes. The package remains deterministic from the manifest.

"Collision unchanged from the locked version" was not a checkable statement
before today. The functional lock hashed two Deli stair systems and would
have reported no drift no matter what a dressing pass did to the site. As of
level_factory 0.31.0 it protects 1,171 records including every collision node
name and every opening, so a dressing pass that touches collision now moves a
hash. This item and items 29 through 31 of that work were built in the wrong
order and it happened to work out.

'''


_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor.

    PIPELINE_ROADMAP.md is CRLF while every file under level_factory/ is LF,
    and `Path.read_text()` normalises newlines -- so a check written with
    read_text reports a CRLF file as LF and an LF-only patch then refuses a
    file it could have handled. That is how this patch was written the first
    time.
    """
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    out = body
    done = 0

    old42, new42 = _as(OLD_42, eol), _as(NEW_42, eol)
    if new42 in out:
        done += 1
    elif out.count(old42) == 1:
        out = out.replace(old42, new42, 1)
    else:
        print(f"REFUSING: item 42's status line occurs {out.count(old42)} "
              f"time(s), expected 1")
        return 1

    anchor = _as("\n### Not to be worked on\n", eol)
    if _as("**43. A whole CLI spelling stopped working", eol) in out:
        done += 1
    elif out.count(anchor) == 1:
        out = out.replace(
            anchor, _as("\n" + INSERT + "### Not to be worked on\n", eol), 1)
    else:
        print(f"REFUSING: the 'Not to be worked on' heading occurs "
              f"{out.count(anchor)} time(s), expected 1")
        return 1

    if done == 2:
        print(f"  already applied  {ROADMAP}")
        return 0

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import re
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    # DECODED FROM BYTES, not read_text: read_text normalises newlines, which
    # is what hid this file's CRLF from the first version of this patch.
    disk = (root / ROADMAP).read_bytes().decode("utf-8")
    check("the file's line endings are preserved",
          disk.count(_CRLF) > 0 or "\r" not in disk)
    md = disk.replace(_CRLF, "\n")
    flat = " ".join(md.split())

    # Structure: every new item has a STATUS line immediately above it.
    for n, title in ((43, "A whole CLI spelling"), (44, "The green boxes"),
                     (45, "Large playable surfaces")):
        check(f"item {n} is present", f"**{n}. {title}" in md)
        i = md.index(f"**{n}. {title}")
        before = md[:i].rstrip().splitlines()[-1]
        check(f"item {n} carries a STATUS line directly above it",
              before.startswith("*STATUS: ") and before.endswith("*"))

    check("the numbering is contiguous -- 42 then 43, 44, 45",
          [int(m) for m in re.findall(r"^\*\*(\d+)\. ", md, re.M)][-4:]
          == [42, 43, 44, 45])

    # 43: the finding, not a wish.
    check("43 names the failing spelling and the function to read",
          "run --target presentation" in flat
          and "layers_for_target" in md)
    check("43 says why nothing noticed",
          "one broken import took" in flat)
    check("43 refuses to assume the nine are pre-existing",
          "before assuming either" in flat)

    # 44: the decisions the source doc actually makes.
    check("44 carries the shape->category->variants abstraction",
          "BOX_VEHICLE" in md and "CYLINDER_SMALL_CITY" in md)
    check("44 keeps the graybox collision authoritative",
          "collision as the authority" in flat)
    check("44 allows art to exceed the collision",
          "may protrude and carry no collision" in flat)
    check("44 keeps it reversible",
          "reveal the proxy" in flat)
    check("44 names the missing contract before any code",
          "Something must name the category" in md
          and "does not exist in either vocabulary" in flat)
    check("44 names Pixelcoat as the multiplier",
          "Pixelcoat skins them" in flat)

    # 45: the layer stack and the boundary.
    check("45 carries the layer stack with authority at 0",
          "COLLISION AUTHORITY" in md and "Surface dressing" in md)
    check("45 makes the manifest the deliverable",
          "manifest is the deliverable, not the scene" in flat)
    check("45 names the placement rules as art direction",
          "uniform spacing reads as procedural noise" in flat
          and "dress intersections first" in flat.lower())
    check("45 carries the test",
          "hide the dressing layer" in flat
          and "should still play correctly" in flat)
    check("45 says which DoD line just became checkable",
          "was not a checkable statement" in flat and "1,171" in md)

    # 42's status was false and is not any more.
    # SCOPED TO ITEM 42'S OWN STATUS LINE. The first version searched the
    # whole file and failed on the DERIVED table at the top, which still
    # carries the old text until `roadmap_status.py --write` regenerates it.
    # A check that reads generated output as if it were source.
    i42 = md.index("**42. A level leaves the factory")
    status42 = md[:i42].rstrip().splitlines()[-1]
    check("42's own status no longer claims nothing produces it",
          "nothing produces it yet" not in status42)
    check("and the stale derived table is left for --write, not hand-edited",
          "nothing produces it yet" in md)
    check("42 names what shipped and what is left",
          "stage 1 SHIPPED" in md and "sites/<building>/" in md)

    # The derived table is regenerated separately; say so rather than fake it.
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  three items, each with a status and none of them a wish"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {ROADMAP}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {ROADMAP}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_roadmap_43_45.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
        print()
        print("  the table at the top is DERIVED -- it will not show 43-45")
        print("  until --write regenerates it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
