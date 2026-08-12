"""Do the modules in a wall run share a top and a bottom line?

    python module_extents.py <preview>/lot/<building>
    python module_extents.py <preview>/lot            # every building
    python module_extents.py --kit <built_dir> --slots <id>.slots.json
    python module_extents.py --sweep <preview>/lot --builds deli_counter/build
    python module_extents.py --selftest               # prove all three readers

Read-only. Parses the composed `site.tscn` and the `.glb` modules beside it.
No Blender, no Godot, no rebuild.

## What this exists to measure

Walked 2026-08-08. Three things looked wrong in the themed site: gaps under and
between walls, doorways whose surround does not line up with the wall either
side, and a block standing proud of a wall run with collision on it.

The first hypothesis was vertical placement -- modules sitting off the storey
grid. That was MEASURED AND REFUTED. Across all five buildings of `lot_demo_001`
there are exactly three off-band instances, all props, all in `bank_branch_a04`
(`column_w`, `column_e` at +0.15, `VAULT_DOOR` at -0.55), and the block that was
walked into is in none of those places. Origins are fine.

Which leaves the other half of the same question. A module's placement is its
TRANSFORM; what you see is its EXTENT. Two modules can share a storey band
exactly and still not share a top edge, if their meshes are different heights.
The `.tscn` carries the transform, so this reads it and the GLBs.

## The instance BASIS is half the placement, and this file used to drop it

Read `nums[10]` for the origin and stop, and every SCALED instance is reported
at its unscaled size. That is not hypothetical: it is what this file shipped
with on 2026-08-08, and it produced the finding "`wallEnd_rockay_*` is 1.000 m
tall in a 3.300 m band, centred, 1.15 m of void above and below" -- opened as
the week's top priority, against Zoo.

There is no void. `wallEnd` is the ONE species Deli Counter SCALES, and Zoo
says so in four places: `genome/species/wallEnd.json` ("ONE unit 1x1x1 solid
box that Deli Counter scales per wall remainder"), `core/kit.py` line 13 and
its `exact = typ != "wallEnd"`, and the comment in `recipes/_arch.py`. The
export naming agrees -- every other species bakes its width into its filename
(`wall_rockay_01_w200.glb`) and `wallEnd_rockay_01.glb` carries no width token
precisely because it has no width until it is placed. The `.tscn` duly carries
`Transform3D(1.8, 0,0,  0, 3.1, 0,  0,0, 0.3,  ...)`.

Measured over all nine buildings of `lot_demo_001`: `wallEnd` is the only
species with a non-unit basis anywhere, and every other species is exactly 1.0
on all three axes. The one species this file mis-measured is the only species
it COULD have mis-measured -- which is exactly why the number looked like a
defect in the kit rather than a defect in the ruler.

A tool that measures placement must read the whole transform. This one now
takes all eight corners of each module's local box through the instance matrix,
and prints the scale beside any instance that has one, so a scaled module can
never again read as a short one.

## What the corrected reading found, which is the opposite defect

Run over `lot_demo_001` with the basis applied, against the wall height each
building's `<id>.slots.json` actually asks for:

    building                slot h   wallEnd   wall built    error   per edge
    depot_a01                  5.2       5.2        3.300   -1.900   0.950 GAP
    rail_station_a02           4.7       4.7        3.300   -1.400   0.700 GAP
    supermarket_a01            4.2       4.2        3.300   -0.900   0.450 GAP
    bank_branch_a04            3.9       3.9        3.300   -0.600   0.300 GAP
    construction_site_a03      3.3       3.3        3.300   +0.000   flush
    funeral_home_a03           3.1       3.1        3.300   +0.200   0.100 OVERLAP
    pharmacy_a02               3.1       3.1        3.300   +0.200   0.100 OVERLAP

`wall`, `breach`, `doorway` and `window` are 3.300 m in EVERY building. The two
that look flush are the two whose storey happens to be 3.3. `wallEnd` matches
the requested height in all seven -- its height lives in the `.tscn` basis
written at assembly, while every other species bakes its height into the `.glb`
at build time, so the one module carrying its height in the scene is the one
that could not lose it. It looked broken here only because this file was not
reading the place it kept it.

`core/kit.py`'s `module_stem` states the premise that fails: "a wall varies on
one axis -- its width -- while its thickness and the storey height are fixed,
so `_w<cm>` is a complete key". The storey height runs 3.1 to 5.2 across this
library. `plan_kit`'s bucket key does include full dims and correctly separates
those modules, then hands them all one filename.

That collision is real but it is NOT what produced the 3.300, and neither was
staleness -- which was proposed here on 2026-08-09 and is retracted. The cause
was ONE KIT PER MISSION. `zoo_kit_build` was planned without an archetype, fed
the mission shell's `shell.slots.json`, and its output dir handed to every
building's compose; 3.300 is the mission shell's storey. Fixed the same day by
fanning the kit out per building (`packages/pipeline/planner.py`), and
confirmed on hardware: five buildings rebuilt, five buildings measuring exactly
what their slots ask -- bank at 3.9, and the 0.300 m gap under every wall in it
gone.

## `--kit`: does a built kit have the dimensions it was asked for?

Nothing in the pipeline checked this. The plate collision was found by hand
after it shipped, and so was the wall height -- the same question, asked of
geometry that already exists, that nobody was asking. `--kit` reads every
`.glb` in a built kit directory and compares it against the slots it was built
from:

    python module_extents.py --kit C:\\Temp\\depot_kit_probe \\
                             --slots deli_counter/build/depot_a01.slots.json

**It imports Zoo's real planner rather than restating it.** `plan_kit` decides
which modules a manifest needs, at what dims, and which are UNIT modules exempt
from the comparison. That is the naming law; it lives in
`zoo_keeper/core/kit.py`, and a second copy here would be a second thing to
keep in sync. `core/kit.py` has no module-level imports at all, so it loads by
path without pulling in `bpy` or the addon's `__init__`. Same move as
`library_themed_fit.py` importing the real themed-fitness rule.

**It compares by SPECIES, not by filename.** Reconstructing a stem needs the
theme and style the build used, and getting either wrong makes every module
miss -- which reads as "nothing to report" rather than as an error. The species
is the leading token of the filename and the `type` on a planned module, so the
two sides meet without this file ever constructing or parsing a stem.
`kit.py`'s docstring is explicit that neither Zoo nor Deli Counter parses these
names; a third party doing it would be the drift those two avoid.

A UNIT module is exempt, and that is not leniency: a `wallEnd` is *supposed* to
be a 1x1x1 box, so measuring one against its slot's 5.2 m would report the one
correct module in the kit as the broken one -- the mistake this file already
made once, from the other end.

## What a defect looks like here

For each storey band of each building, this prints the distinct (bottom, top)
pairs of every module placed on it. A band whose modules all agree is one pair.
A band with several pairs is a run that cannot line up, and the sizes of the
disagreement are the sizes of the seams you can see.

It reports. It does not decide what tolerance is acceptable -- that is a call
about the art, and nothing here has measured what a correct kit looks like.

## The readers, and why they are tested in-process

glTF stores each mesh's bounds as `min`/`max` on the POSITION accessor, so the
extent needs no mesh data -- but it does need the node transform above it, and
getting that wrong yields plausible numbers that are quietly wrong. `--selftest`
builds a GLB in memory with a known box at a known transform and asserts the
reader recovers it. A parser nobody has put wrong on purpose is a parser nobody
has tested.

There are TWO parsers here and only one of them was ever put wrong on purpose.
The `.tscn` instance transform was read by index, untested, and it is the one
that was wrong. `--selftest` now covers it too: a synthetic instance block with
a known non-unit scale and a known origin, asserted against the span it must
produce. That case fails on the version of this file that reads `nums[10]`
alone, which is the only property that makes it worth having.
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

# `res://` is OPTIONAL, and that is not defensive habit. The per-building
# packages are written PORTABLE (`lot.py --portable`, 2026-08-05) precisely so
# a stranger can drop one into their own project: their paths are
# scene-relative, `path="art/zoo/wall_rockay_01_w200.glb"`. A pattern that
# demands the prefix matches the composed site and silently matches NOTHING in
# the per-building scenes -- which is what this file shipped with, reporting
# "0 distinct modules" for all five buildings while looking like it ran.
# MTIME IS NOT A STALENESS SIGNAL HERE, and this file briefly claimed it was.
# On 2026-08-09 a module whose dims matched nothing planned was tagged "5 days
# older than the rest of this kit; probably left behind" -- and the tag was
# right about that one file by luck. The next run refuted the rule: Level
# Factory's cache is CONTENT-ADDRESSED, so a byte-identical module is never
# re-copied (`if not blob.exists()`), is hard-linked into the work dir, and
# `copy2` preserves its mtime the rest of the way. `wallEnd_rockay_01.glb` is a
# unit box whose content never changes, so it reads five days old while being
# current and correct. An age test would call it a leftover on every run.
#
# So this reports WHAT IT MEASURED -- these dimensions match no planned module
# -- and does not guess why. The cause is decidable where the evidence is: the
# kit index next to the modules, which `packages/validation/kit_dims.py` reads
# at the job that built them.


_IDS = re.compile(
    r'\[ext_resource[^\]]*?path="(?:res://)?([^"]+)"[^\]]*?id="([^"]+)"\]')


# ---------------------------------------------------------------- glTF reader
def _chunks(raw: bytes):
    """(json_dict, ...) from a binary glTF container."""
    if raw[:4] != b"glTF":
        raise ValueError("not a binary glTF")
    n = struct.unpack_from("<I", raw, 8)[0]
    off, js = 12, None
    while off + 8 <= min(n, len(raw)):
        clen, ctype = struct.unpack_from("<II", raw, off)
        body = raw[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(body.decode("utf-8"))
        off += 8 + clen + ((4 - clen % 4) % 4 if clen % 4 else 0)
    if js is None:
        raise ValueError("no JSON chunk")
    return js


def _mat(node) -> list[float]:
    """A node's local matrix, column-major, from `matrix` or from TRS."""
    if "matrix" in node:
        return list(node["matrix"])
    t = node.get("translation", [0.0, 0.0, 0.0])
    r = node.get("rotation", [0.0, 0.0, 0.0, 1.0])
    s = node.get("scale", [1.0, 1.0, 1.0])
    x, y, z, w = r
    rot = [
        1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w),
        2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w),
        2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y),
    ]
    m = [0.0] * 16
    for c in range(3):
        for row in range(3):
            m[c * 4 + row] = rot[c * 3 + row] * s[c]
    m[12], m[13], m[14], m[15] = t[0], t[1], t[2], 1.0
    return m


def _mul(a: list[float], b: list[float]) -> list[float]:
    """a * b, both column-major 4x4 (parent * child)."""
    out = [0.0] * 16
    for c in range(4):
        for r in range(4):
            out[c * 4 + r] = sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4))
    return out


def _apply(m: list[float], p) -> tuple[float, float, float]:
    x, y, z = p
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def glb_bounds(path_or_bytes):
    """``(min_xyz, max_xyz)`` in the file's own space, or ``None``.

    Walks the default scene applying node transforms, because a module whose
    mesh is authored at the origin and lifted by its node reads 0..3 m from the
    accessor alone and 1..4 m in the world -- and the whole question here is
    where the top edge lands.
    """
    raw = (path_or_bytes if isinstance(path_or_bytes, bytes)
           else Path(path_or_bytes).read_bytes())
    js = _chunks(raw)
    accs, meshes = js.get("accessors") or [], js.get("meshes") or []
    nodes = js.get("nodes") or []
    scenes = js.get("scenes") or [{}]
    roots = scenes[js.get("scene", 0)].get("nodes", list(range(len(nodes))))

    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    seen = False

    def visit(idx: int, parent: list[float]):
        nonlocal seen
        node = nodes[idx]
        world = _mul(parent, _mat(node))
        mi = node.get("mesh")
        if mi is not None and mi < len(meshes):
            for prim in meshes[mi].get("primitives") or []:
                a = (prim.get("attributes") or {}).get("POSITION")
                if a is None or a >= len(accs):
                    continue
                acc = accs[a]
                amin, amax = acc.get("min"), acc.get("max")
                if not (amin and amax and len(amin) >= 3):
                    continue
                seen = True
                for cx in (amin[0], amax[0]):
                    for cy in (amin[1], amax[1]):
                        for cz in (amin[2], amax[2]):
                            w = _apply(world, (cx, cy, cz))
                            for k in range(3):
                                lo[k] = min(lo[k], w[k])
                                hi[k] = max(hi[k], w[k])
        for c in node.get("children") or []:
            visit(c, world)

    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    for r in roots:
        visit(r, ident)
    return (tuple(lo), tuple(hi)) if seen else None


# ---------------------------------------------------------------- kit vs slots
def _find_kit_py(hint: str = None) -> Path:
    """Locate Zoo's `core/kit.py`, or ``None``.

    Checked in order: an explicit `--zoo <root>`, then upward from this file
    and from cwd. Returning None is not a failure mode the caller may ignore --
    without the real planner there is no comparison, only a guess at one.
    """
    names = ("zoo_keeper/core/kit.py", "zoo/zoo_keeper/core/kit.py")
    roots = []
    if hint:
        roots.append(Path(hint))
    here = Path(__file__).resolve()
    roots.extend([*here.parents, Path.cwd(), *Path.cwd().resolve().parents])
    for r in roots:
        for n in names:
            p = r / n
            if p.is_file():
                return p
    return None


def _load_kit(path: Path):
    """Import `core/kit.py` BY PATH, not as `zoo_keeper.core.kit`.

    The package `__init__` is a Blender add-on entry point and importing it
    would drag in `bpy`, which is absent outside Blender -- and this whole file
    exists to be runnable without it. `core/kit.py` declares no module-level
    imports, so loading the file alone is complete, not a workaround.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_zoo_kit_planner", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _built_kit(built: Path) -> dict:
    """{species: {stem: (w, d, h)}} for every readable .glb in a kit dir.

    A .glb IS Y-UP, and this cost a run to learn. Zoo authors in Blender's
    Z-up, so it is tempting to read a standing slab's height off z -- but the
    glTF spec is Y-up and Blender's exporter converts on the way out, so the
    file on disk has height in Y and thickness in Z. Reading z gave
    `wall WANTED h=[5.2] BUILT h=[0.3]` for a kit that was correct: a wall's
    height compared against its own thickness, which is precisely what the
    comment on `kit_check` warned about before this function did it.

    Deli Counter's `fit.dims` are [width, depth, height], so the mapping is
    (x, z, y) -- not a transpose anyone should have to re-derive at the call
    site, which is why it happens here once.
    """
    out, when = {}, {}
    for p in sorted(built.glob("*.glb")):
        try:
            b = glb_bounds(p)
        except (OSError, ValueError, struct.error):
            b = None
        if b is None:
            continue
        (lo, hi) = b
        # Leading token == the slot type. Types are single words (`wall`,
        # `wallEnd`, `doorway`, ...), so this splits where a stem never does.
        out.setdefault(p.stem.split("_")[0], {})[p.stem] = (
            round(hi[0] - lo[0], 4),      # w  <- x
            round(hi[2] - lo[2], 4),      # d  <- z
            round(hi[1] - lo[1], 4))      # h  <- y
        try:
            when[p.stem] = p.stat().st_mtime
        except OSError:
            pass
    return out, when


def _near(a, b, tol: float = 1e-3) -> bool:
    """Same (w, d, h) to the millimetre. Exported floats are not exact."""
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def kit_diff(built: Path, slots: Path, kit) -> dict:
    """Compare a built kit against its slots. Structured; prints nothing.

    Compares the whole (w, d, h), not just the height. The wall defect this was
    written for is a height, but the plate collision that preceded it was a
    DEPTH -- "the shorter room got a slab eight metres too deep" -- and a check
    that only ever looks at the axis of the last bug is a check that finds the
    last bug.

    Axis handling lives in `_built_kit`; read its docstring before changing
    anything here.
    """
    out = {"building_id": None, "planned": 0, "species": {}, "stale": {},
           "mismatch": 0, "missing": 0, "error": None}
    try:
        manifest = json.loads(slots.read_text(encoding="utf-8"))
        # theme/style only shape STEMS, and nothing here reads a stem -- the
        # comparison is per species. Defaults are correct precisely because
        # they cannot affect the answer.
        plan = kit.plan_kit(manifest)
    except (OSError, ValueError, AttributeError, KeyError) as exc:
        out["error"] = f"could not plan from {slots.name}: {exc}"
        return out

    want, unit = {}, set()
    for m in plan.get("modules", []):
        typ = m.get("type")
        if m.get("fit") == "unit":
            unit.add(typ)
            continue
        d = m.get("dims") or []
        if len(d) >= 3:
            want.setdefault(typ, set()).add(
                tuple(round(float(v), 4) for v in d[:3]))

    got, _when = _built_kit(built)
    out["building_id"] = plan.get("building_id")
    out["planned"] = plan.get("module_count") or 0
    out["built"] = sum(len(v) for v in got.values())
    if not got:
        out["error"] = (f"no readable .glb in {built} -- nothing was built, or "
                        f"the build wrote somewhere else. Not a clean kit.")
        return out

    for typ in sorted(set(want) | set(got) | unit):
        mine = got.get(typ, {})
        if typ in unit:
            off = {s: t for s, t in mine.items()
                   if not _near(t, (1.0, 1.0, 1.0))}
            state = "unit" if not off else "unit_bad"
        elif typ not in got:
            off, state = {}, "missing"
        elif typ not in want:
            off, state = dict(mine), "unplanned"
        else:
            off = {s: t for s, t in mine.items()
                   if not any(_near(t, w) for w in want[typ])}
            state = "ok" if not off else "mismatch"
        out["species"][typ] = {"state": state, "built": mine, "off": off,
                               "want": sorted(want.get(typ, ()))}
        out["missing"] += state == "missing"
        out["mismatch"] += state in ("mismatch", "unplanned", "unit_bad")
    return out


def _print_diff(r: dict) -> None:
    for typ, s in r["species"].items():
        st, mine, off, want = s["state"], s["built"], s["off"], s["want"]
        if st == "unit":
            print(f"    {typ:10} UNIT  x{len(mine):<3} "
                  f"ok (1x1x1, scaled at placement)")
        elif st == "unit_bad":
            print(f"    {typ:10} UNIT  x{len(mine):<3} EXPECTED 1x1x1")
        elif st == "missing":
            print(f"    {typ:10} planned x{len(want)} but NO .glb built")
        elif st == "unplanned":
            print(f"    {typ:10} built x{len(mine)} but the planner wants none")
        elif st == "ok":
            print(f"    {typ:10} x{len(mine):<3} ok   "
                  f"h={sorted({round(w[2], 3) for w in want})}")
        else:
            # NOT "built to the wrong size". What is measured is that no
            # planned module for this species has these dimensions, and a file
            # the plan never asked for reads identically. Measured 2026-08-09:
            # `prop_rockay_01_w160.glb` was reported here as a mismatch and was
            # in fact a five-day-old leftover in a package whose every other
            # module came from that day's build -- re-skinned and re-imported
            # by the packaging step as though it were current. Naming the fault
            # "wrong size" sent the reader to Zoo for a bug that is not there.
            print(f"    {typ:10} x{len(mine):<3} {len(off)} MATCHES NO "
                  f"PLANNED MODULE   planned (w,d,h): "
                  f"{want[:3]}{' ...' if len(want) > 3 else ''}")
        for stem, t in sorted(off.items()):
            print(f"        {stem:34} built w={t[0]:7.3f} d={t[1]:6.3f} "
                  f"h={t[2]:7.3f}")


def _need_kit(zoo_hint: str = None):
    """The planner, or None with the reason printed."""
    kit_py = _find_kit_py(zoo_hint)
    if kit_py is None:
        print("  cannot find Zoo's core/kit.py -- pass --zoo <zoo repo root>.")
        print("  Refusing to compare: the planner decides which modules are")
        print("  UNIT (exempt) and at what dims, and guessing that here is")
        print("  how the wallEnd finding happened.")
        return None, None
    return _load_kit(kit_py), kit_py


def kit_check(built: Path, slots: Path, zoo_hint: str = None) -> int:
    """One kit, verbosely. See `kit_diff`."""
    kit, kit_py = _need_kit(zoo_hint)
    if kit is None:
        return 2
    r = kit_diff(built, slots, kit)
    print(f"  planner: {kit_py}")
    if r["error"]:
        print(f"  {r['error']}")
        return 1
    print(f"  {r['building_id']}  {len(r['species'])} species built, "
          f"{r['planned']} planned")
    _print_diff(r)
    bad = r["mismatch"] + r["missing"]
    print(f"  {bad} species disagree with the slots they were built from"
          if bad else "  every species matches the slots it was built from")
    return 1 if bad else 0


def sweep(lot: Path, builds: Path, zoo_hint: str = None) -> int:
    """Every building in a lot, one line each, detail only where it is wrong.

    The point of a sweep is the SHAPE of the damage, not any one building.

    ABSENT IS NOT A DIAGNOSIS. An earlier version of this called a building
    with missing species STALE, which named a cause the measurement does not
    support: a preview package holds only the art its `.tscn` actually
    references, so a role the resolver never swapped in is absent for a reason
    that has nothing to do with age. Run across the lot, EVERY building was
    missing the same roles including the one that otherwise passes -- a uniform
    property of what a package contains, not eight independent staleness
    events. The verdict below says only what was seen: dims that disagree are
    WRONG, species with no file are ABSENT, and why is left to whoever looks.
    """
    kit, kit_py = _need_kit(zoo_hint)
    if kit is None:
        return 2
    dirs = sorted(p for p in lot.iterdir() if p.is_dir())
    if not dirs:
        print(f"  no building directories under {lot}")
        return 2
    print(f"  planner: {kit_py}")
    print(f"  {'building':24} {'glb':>5} {'planned':>8} {'absent':>7} "
          f"{'wrong':>6}  verdict")
    print("  " + "-" * 70)
    rows, unread = [], []
    for b in dirs:
        art, slots = b / "art" / "zoo", builds / f"{b.name}.slots.json"
        if not slots.is_file():
            unread.append(f"{b.name}: no {slots.name}")
            continue
        if not art.is_dir():
            unread.append(f"{b.name}: no art/zoo")
            continue
        r = kit_diff(art, slots, kit)
        rows.append((b.name, r))
        if r["error"]:
            print(f"  {b.name:24} {'-':>5} {'-':>8} {'-':>7} {'-':>6}  "
                  f"{r['error'].splitlines()[0][:40]}")
            continue
        # WRONG outranks ABSENT: a module built to the wrong size is a defect
        # in geometry that shipped, while an absent one may simply never have
        # been swapped in. Do not let the softer word hide the harder one.
        verdict = ("WRONG DIMS" if r["mismatch"] else
                   "absent only" if r["missing"] else "ok")
        print(f"  {b.name:24} {r['built']:>5} {r['planned']:>8} "
              f"{r['missing']:>7} {r['mismatch']:>6}  {verdict}")
    for name, r in rows:
        if r["error"] or not (r["mismatch"] + r["missing"]):
            continue
        print(f"\n  --- {name} ---")
        _print_diff(r)
    for u in unread:
        print(f"  skipped {u}")
    bad = sum(1 for _, r in rows if r["error"] or r["mismatch"] or r["missing"])
    print(f"\n  {bad} of {len(rows)} buildings disagree with their slots")
    return 1 if bad else 0


# ------------------------------------------------------------------- selftest
def _glb_bytes(minv, maxv, node: dict = None) -> bytes:
    """A minimal GLB whose single mesh has the given accessor bounds."""
    js = {
        "asset": {"version": "2.0"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [dict(node or {}, mesh=0)],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
        "accessors": [{"componentType": 5126, "count": 2, "type": "VEC3",
                       "min": list(minv), "max": list(maxv)}],
    }
    body = json.dumps(js).encode("utf-8")
    body += b" " * ((4 - len(body) % 4) % 4)
    return (b"glTF" + struct.pack("<II", 2, 12 + 8 + len(body))
            + struct.pack("<II", len(body), 0x4E4F534A) + body)


def _selftest_glb() -> int:
    """A GLB with a 2 x 3 x 0.3 box authored at the origin, on a node that
    lifts it 1.5 m and rotates it 90 degrees about Y. Correct reading: y spans
    1.5..4.5, and the rotation swaps x and z."""
    glb = _glb_bytes([-1.0, 0.0, -0.15], [1.0, 3.0, 0.15],
                     {"translation": [0.0, 1.5, 0.0],
                      "rotation": [0.0, 0.70710678, 0.0, 0.70710678]})
    got = glb_bounds(glb)
    if got is None:
        print("[selftest] FAIL: reader found no positions")
        return 1
    (lo, hi) = got
    checks = [("y_min", lo[1], 1.5), ("y_max", hi[1], 4.5),
              ("x_min", lo[0], -0.15), ("x_max", hi[0], 0.15),
              ("z_min", lo[2], -1.0), ("z_max", hi[2], 1.0)]
    bad = [(n, g, w) for n, g, w in checks if abs(g - w) > 1e-4]
    for n, g, w in checks:
        print(f"[selftest] {n:5} = {g:8.4f}  want {w:8.4f}  "
              f"{'ok' if abs(g - w) <= 1e-4 else 'FAIL'}")
    if bad:
        print("[selftest] the reader is wrong; do not trust its numbers")
        return 1
    print("[selftest] node transform and accessor bounds both handled")
    return 0


def _selftest_instance() -> int:
    """The case this file got wrong for real.

    A synthetic `.tscn` block instancing a UNIT box -- local y -0.5..0.5, the
    shape `wallEnd_rockay_01.glb` actually is -- under a `wallEnd`-style
    transform: scale (1.8, 3.3, 0.3), origin y 1.65.

    Correct reading: 1.65 +/- 3.3/2, i.e. 0.000 .. 3.300, height 3.300, flush
    with the 3.300 m wall beside it.

    Reading origin.y alone: 1.150 .. 2.150, height 1.000, "1.15 m of void above
    and below". That was the top item of the 2026-08-08 handoff and it was an
    artefact of this function not existing.
    """
    nums = [1.8, 0.0, 0.0,
            0.0, 3.3, 0.0,
            0.0, 0.0, 0.3,
            -8.1, 1.65, -10.0]
    m = _tscn_matrix(nums)
    local = ((-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))
    lo_y, hi_y = _world_y(m, local)
    sx, sy, sz = _scale_of(nums)
    checks = [("origin_y", m[13], 1.65), ("scale_x", sx, 1.8),
              ("scale_y", sy, 3.3), ("scale_z", sz, 0.3),
              ("bottom", lo_y, 0.0), ("top", hi_y, 3.3)]
    bad = [(n, g, w) for n, g, w in checks if abs(g - w) > 1e-4]
    for n, g, w in checks:
        print(f"[selftest] {n:8} = {g:8.4f}  want {w:8.4f}  "
              f"{'ok' if abs(g - w) <= 1e-4 else 'FAIL'}")
    if bad:
        print("[selftest] the instance transform is being read wrong; a scaled "
              "module will report at its unscaled size")
        return 1
    # The regression, stated as the number it produced, so the next reader of
    # a "short module" finding can tell in one line which bug they are looking
    # at. `oy + local` is exactly the arithmetic this file used to do.
    naive = (round(m[13] + local[0][1], 3), round(m[13] + local[1][1], 3))
    print(f"[selftest] basis applied: {lo_y:.3f}..{hi_y:.3f} "
          f"(origin-only would say {naive[0]:.3f}..{naive[1]:.3f})")
    return 0


def _kit_slab(w: float, d: float, h: float) -> bytes:
    """A .glb of a w x d x h slab, authored the way a real export IS: Y-UP.

    Written as (x=w, y=h, z=d) deliberately and not as a convenience. The first
    version of this fixture used Z-up because that is how Zoo authors, so it
    agreed with a `_built_kit` that read the wrong axis and the pair passed
    together. A fixture is a claim about the world; this one claims what a
    glTF file on disk actually looks like.
    """
    return _glb_bytes([-w / 2, -h / 2, -d / 2], [w / 2, h / 2, d / 2])


def _selftest_kit() -> int:
    """`--kit` against a synthetic building, built RIGHT and then built WRONG.

    Two slots: a 2.0 x 0.3 x 5.2 wall and a 5.2 m remainder.

    The correct kit must PASS. That assertion is the one that matters -- the
    mismatch case passed happily while `_built_kit` read a wall's thickness as
    its height, because a check that reads the wrong axis flags everything, and
    "it flagged the bad one" cannot tell you it would not also flag the good
    one. A verifier is only worth its clean report.

    Then the same wall rebuilt 3.3 m tall must be FLAGGED, and the `wallEnd`
    must NOT be -- it is supposed to be a unit box, and reporting the one
    correct module in the kit as broken is the 2026-08-08 finding arriving from
    the other side.

    Skipped, loudly, when Zoo is not beside this file: a check that quietly
    passes because it could not run is the failure this repo keeps finding.
    """
    import tempfile
    if _find_kit_py() is None:
        print("[selftest] kit: SKIPPED -- no Zoo checkout found next to this "
              "file; --kit is untested in this run")
        return 0
    manifest = {
        "building_id": "selftest_shell",
        "slots": [
            {"role": "wall", "size_mod": "full",
             "fit": {"dims": [2.0, 0.3, 5.2], "pivot": "center"}},
            {"role": "wall", "size_mod": "end",
             "fit": {"dims": [0.45, 0.3, 5.2], "pivot": "center"}},
            {"role": "prop", "fit": {"dims": [1.6, 0.5, 2.4]}},
        ],
    }
    bad = 0
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "slots.json").write_text(json.dumps(manifest), encoding="utf-8")
        wall = d / "wall_rockay_01_w200.glb"
        (d / "wallEnd_rockay_01.glb").write_bytes(_kit_slab(1.0, 1.0, 1.0))
        (d / "prop_rockay_01_w160.glb").write_bytes(_kit_slab(1.6, 0.5, 2.4))

        wall.write_bytes(_kit_slab(2.0, 0.3, 5.2))          # as asked for
        clean = kit_check(d, d / "slots.json")
        print(f"[selftest] kit: a kit built to its slots -> "
              f"{'clean' if clean == 0 else 'FALSE ALARM'}  "
              f"{'ok' if clean == 0 else 'FAIL'}")
        bad += clean != 0

        wall.write_bytes(_kit_slab(2.0, 0.3, 3.3))          # the defect
        short = kit_check(d, d / "slots.json")
        print(f"[selftest] kit: wall built 3.3 for a 5.2 slot -> "
              f"{'flagged' if short == 1 else 'NOT FLAGGED'}  "
              f"{'ok' if short == 1 else 'FAIL'}")
        bad += short != 1

        # A MODULE THE PLAN NEVER ASKED FOR IS STILL DETECTED. It is reported
        # as matching no planned module and nothing more: whether it was built
        # wrong or left behind is not decidable from a package, and this file
        # briefly guessed "left behind" from mtime. That guess is refuted --
        # the cache is content-addressed, so an unchanged module keeps its
        # original blob's timestamp and a correct `wallEnd` reads as ancient
        # forever. The cause is decidable at the kit, where the index is.
        wall.write_bytes(_kit_slab(2.0, 0.3, 5.2))          # correct again
        orphan = d / "prop_rockay_09_w160.glb"
        orphan.write_bytes(_kit_slab(1.6, 0.8, 0.75))
        r = kit_diff(d, d / "slots.json", _load_kit(_find_kit_py()))
        seen = (r["species"].get("prop") or {}).get("off") or {}
        ok = orphan.stem in seen and r["mismatch"] == 1
        print(f"[selftest] kit: a module the plan never asked for -> "
              f"{'reported' if ok else 'MISSED'}  {'ok' if ok else 'FAIL'}")
        bad += not ok
    if bad:
        print("[selftest] --kit is not trustworthy; a clean report from it "
              "means nothing in this run")
        return 1
    return 0


def _selftest() -> int:
    """All three readers, every run: the GLB, the `.tscn`, and the kit diff."""
    return _selftest_glb() or _selftest_instance() or _selftest_kit()


# ------------------------------------------------------------------- the scan
def _tscn_matrix(nums: list[float]) -> list[float]:
    """Column-major 4x4 from a `.tscn` Transform3D's twelve reals.

    Godot's resource writer emits the basis as its three COLUMN vectors
    (x_axis, y_axis, z_axis) and then the origin, which is why `nums[10]` is
    origin.y and why reading that one index looked like it worked. The other
    nine numbers are the half of the placement that scales and rotates the
    module, and dropping them is the bug this file is named after.
    """
    return [nums[0], nums[1], nums[2], 0.0,
            nums[3], nums[4], nums[5], 0.0,
            nums[6], nums[7], nums[8], 0.0,
            nums[9], nums[10], nums[11], 1.0]


def _scale_of(nums: list[float]) -> tuple[float, float, float]:
    """Per-axis scale = the length of each basis column."""
    return tuple(  # type: ignore[return-value]
        round(sum(nums[c * 3 + k] ** 2 for k in range(3)) ** 0.5, 4)
        for c in range(3))


def _instances(tscn: Path):
    """(node_name, module_stem, matrix, scale) for every instanced module."""
    text = tscn.read_text(encoding="utf-8")
    res = {m.group(2): m.group(1) for m in _IDS.finditer(text)}
    out = []
    for blk in re.split(r"\n(?=\[node )", text):
        nm = re.search(r'\[node name="([^"]+)"', blk)
        inst = re.search(r'instance=ExtResource\("([^"]+)"\)', blk)
        tm = re.search(r"transform = Transform3D\(([^)]*)\)", blk)
        if not (nm and inst and tm):
            continue
        nums = [float(v) for v in tm.group(1).split(",")]
        if len(nums) < 12:
            continue
        out.append((nm.group(1), res.get(inst.group(1), ""),
                    _tscn_matrix(nums), _scale_of(nums)))
    return out


def _world_y(m: list[float], local) -> tuple[float, float]:
    """(min_y, max_y) of a local AABB's eight corners under `m`.

    All eight, not the two that look like the top and the bottom: under a
    rotation the corner that ends up highest is not the one that started
    highest, and this file's whole subject is where the top edge lands.
    """
    (lo, hi) = local
    ys = [_apply(m, (cx, cy, cz))[1]
          for cx in (lo[0], hi[0])
          for cy in (lo[1], hi[1])
          for cz in (lo[2], hi[2])]
    return min(ys), max(ys)


def scan(building: Path) -> int:
    tscn = building / "site.tscn"
    if not tscn.is_file():
        print(f"  {building.name}: no site.tscn")
        return 0
    rows = _instances(tscn)
    if rows and not any(rel for _, rel, _, _ in rows):
        # Every instance resolved to an empty module path: the ext_resource
        # table did not parse. Say so instead of reporting a confident zero.
        print(f"  {building.name}: {len(rows)} instances but NO module paths "
              f"resolved -- the ext_resource pattern does not match this "
              f"file's format; refusing to report bands from nothing")
        return 1
    cache: dict[str, object] = {}
    bands: dict[float, dict[tuple, list[tuple[str, tuple]]]] = {}
    unread = []
    for name, rel, m, scale in rows:
        if not rel:
            continue
        p = building / rel
        if rel not in cache:
            try:
                cache[rel] = glb_bounds(p) if p.is_file() else None
            except (OSError, ValueError, struct.error):
                cache[rel] = None
        b = cache[rel]
        if b is None:
            unread.append(rel)
            continue
        # Absolute top and bottom: where this module's mesh actually lands,
        # under the FULL instance transform. The module's own box is what Zoo
        # authored; the basis is what Deli Counter did with it, and only the
        # two together are the thing you walk into.
        lo_y, hi_y = _world_y(m, b)
        bottom, top = round(lo_y, 3), round(hi_y, 3)
        band = round(m[13], 2)          # origin.y -- the storey it sits on
        bands.setdefault(band, {}).setdefault((bottom, top), []).append(
            (Path(rel).stem, scale))

    print(f"  {building.name}: {len(rows)} instances, "
          f"{len(cache)} distinct modules")
    for band in sorted(bands):
        pairs = bands[band]
        flag = "" if len(pairs) == 1 else f"   <-- {len(pairs)} DIFFERENT"
        print(f"    band y={band:<7} {len(pairs)} distinct (bottom, top){flag}")
        for (bot, top), users in sorted(pairs.items()):
            kinds = sorted({u.split("_rockay")[0] for u, _ in users})
            # Show the scale when there is one. A module reported at a height
            # its .glb does not have is not a mystery if the ruler says why.
            scaled = sorted({s for _, s in users if any(
                abs(v - 1.0) > 1e-6 for v in s)})
            note = ""
            if scaled:
                sy = sorted({s[1] for s in scaled})
                note = (f"   [scaled: sy={', '.join(f'{v:g}' for v in sy)}"
                        f"{'' if len(scaled) == 1 else f', {len(scaled)} bases'}]")
            print(f"        {bot:8.3f} .. {top:8.3f}  h={top - bot:6.3f}  "
                  f"x{len(users):<4} {', '.join(kinds)}{note}")
    if unread:
        print(f"    {len(set(unread))} module(s) could not be read: "
              + ", ".join(sorted(set(unread))[:4]))
    return 0


def _flag(argv: list[str], name: str) -> str:
    """`--name value`, or None. Errors are the caller's to report."""
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    if not argv:
        print(__doc__.splitlines()[2].strip())
        print(__doc__.splitlines()[4].strip())
        return 2

    lot = _flag(argv, "--sweep")
    if lot is not None:
        builds = _flag(argv, "--builds")
        if not builds:
            print("--sweep needs --builds <dir of <id>.slots.json> "
                  "(usually deli_counter/build).")
            return 2
        lot_p, b_p = Path(lot), Path(builds)
        for p in (lot_p, b_p):
            if not p.is_dir():
                print(f"not a directory: {p}")
                return 2
        if _selftest():
            return 1
        print()
        return sweep(lot_p, b_p, _flag(argv, "--zoo"))

    kit_dir = _flag(argv, "--kit")
    if kit_dir is not None:
        slots = _flag(argv, "--slots")
        if not slots:
            print("--kit needs --slots <id>.slots.json: without the manifest "
                  "there is nothing to compare the geometry against.")
            return 2
        built, sl = Path(kit_dir), Path(slots)
        if not built.is_dir():
            print(f"not a directory: {built}")
            return 2
        if not sl.is_file():
            print(f"not a file: {sl}")
            return 2
        if _selftest():
            return 1
        print()
        return kit_check(built, sl, _flag(argv, "--zoo"))

    root = Path(argv[0])
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2
    # The readers are proved before they are trusted, every run. It costs a
    # millisecond and it is the difference between a measurement and a number.
    if _selftest():
        return 1
    print()
    targets = ([root] if (root / "site.tscn").is_file()
               else sorted(p for p in root.iterdir() if p.is_dir()))
    for b in targets:
        scan(b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
