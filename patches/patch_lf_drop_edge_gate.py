"""Level Factory 0.216.0: the gate over undeclared drops (factory roadmap 173, the last step).

What it changes (anchored; refuses on a miss; CRLF-safe):
  * assets/godot/walkable_edge.gd -- Level Factory's own copy of the factory's tools/walkable_edge.gd, byte for
    byte (sha256 pinned below), so a consumer with only this repo has the measurement.
  * packages/exporting/drop_edges.py -- the verdict (new).
  * packages/exporting/export.py -- ExportDropEdgesError, ExportProfile.require_declared_drops, step 4.88.
  * tests/unit/test_drop_edges.py, VERSION 0.216.0, CHANGELOG.

    python patches/patch_lf_drop_edge_gate.py --tests   # the test file only (prove it fails first)
    python patches/patch_lf_drop_edge_gate.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
TOOL = ROOT / "tools" / "walkable_edge.gd"
TOOL_SHA256 = "878f755daa9521ae3069c0fb49b8d5d88662abff3263cdcde2504998d2e674f9"


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


MODULE = '''"""Can a body walk off an edge the level did not declare? The gate over UNDECLARED DROPS (factory roadmap 173).

WHAT THIS EXISTS FOR. Every other gate in this exporter measures traversal correctness or resource closure --
can a body get from A to B, does every `res://` reference resolve. None asked whether a body can FALL somewhere
nobody meant. On cold run 9072's package the instrument found, from physics, a stairwell the walker had found
first, and its first run on a current package found the office's stair pit: a landing open 6.67 m over the well,
a flight's inner side open over the flight beside it, 12 edges no gate had ever seen (the factory's
`docs/findings/drop_edges_173/`; Deli Counter 0.225.0 fixed them at the source). THE RULE this gate enforces is
the item's: every drop a body can reach is either GUARDED, or DECLARED, or a defect.

THE MEASUREMENT is `assets/godot/walkable_edge.gd`, which owns it (this module owns the verdict): over a grid of
cells it finds every surface a body stands on with the body's own capsule, floods what the body can REACH from
the package's `player_start` across steps, falls and the package's off-mesh links (its ladders), and reports
every edge where a reached cell's neighbour is further down than a body steps with nothing above step-over
height between them and nothing in the body's way -- an UNGUARDED drop. Nine repairs on cold run 9317's package
went into that instrument before its residue was the level's and not its own; they are written beside it.

THE DECLARED SET is read off the PACKAGE, so the gate's list and the AI's list are one list:
  * a drop link: `navigation_hints.json` `links[]` with `required_capability` "drop" (Deli Counter 0.226.0 files
    one on every `floor_hole` / `hatch` vertical link, Lot 0.125.0 moves it into site space, Dispatch 0.5.3
    carries it) -- an edge at its storey within HOLE_MARGIN of its `hole` rect is declared;
  * a ladder's shaft: a link with `required_capability` "climb" -- an edge within LADDER_R of the ladder's
    column, at any height from its foot to its head, is the hatch or hole the ladder passes through: its head's,
    and every floor's between (`_in_shaft`);
  * a flight's own open side: an edge whose cell stands on a stair collider (`GreyboxBase/stair<n>...`), which
    the agent contract calls ordinary architecture and Deli Counter guards at its own thresholds;
  * a thing's top: an edge whose cell stands on anything that is not a floor, a roof, a tread or the ground (a
    desk, a car, a parapet, the perimeter fence) is not a floor a body walks, and is reported, not refused;
  * outdoors: an edge with nothing overhead (the plate's rim, a roof, a dock) is somebody's decision -- reported,
    not refused. In the instrument's own comment, a body that walks off an edge INSIDE a building has found a
    defect.

WHAT IT REFUSES: an unguarded drop, indoors, from a reached cell on a floor-like surface, that nothing above
declares. Measured through this module, in the engine, on cold run 9318's package (Deli Counter 0.225.0, which
predates the drop links; the factory's `docs/findings/drop_edges_173/gate_probe_9318.out.txt` and
`gate_reclass_9318.out.txt`): 54 unguarded edges, 46 indoors -- 10 a flight's own side, 3 a rail's top, 13 a
ladder's shaft, and 20 at deli_a01's floor hole, which that package does not declare, so the gate refuses it.
The same report with the link Deli Counter 0.226.0 records and Lot 0.125.0 places for that hole passes: its
rect lies within 0.16 m of all 20 rows. A package that trips it is fixed by DECLARING the drop in its spec (a
`floor_hole` link) or GUARDING it (a rail), never by editing the package -- the fix lands in Deli Counter, which
is where roadmap 173's first two findings landed.

THE RECORDS: `drop_edges.json` is the instrument's report (every row, with what each stands on and drops to, and
the owner table), `drop_edges_scan.json` is this module's verdict. Both land ABOVE the closure verdict, inside
the package the verdict describes and the manifest that lists it, like `greybox_skin_scan.json`.

THE COST: the instrument walks the rectangle the package's nav nodes and links span plus `EXTENT_MARGIN_M`
(`extent_from_hints`), not the backdrop, with the rectangle's corner snapped to the cell lattice by the
instrument. On cold run 9318's package: 1,521 x 1,521 cells and 150 s over everything; bounded by its `Site`
node's subtree STILL 1,521 a side (the site's ground carries the backdrop's); bounded by its nav nodes 341 x 126
cells and 7 s, with the same rows as the unbounded run. An unsnapped corner put every cell a centimetre off the
unbounded lattice and the flood lost a stair's one-cell turn landing -- the fragility the nav gate's grid sweep
exists for, measured and recorded beside the instrument. In an export the import cache is warm; on a bare
package `measure` imports first, and that is most of its 104 s on the same package.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from packages.exporting.greybox_skin import _engine_tail

_LF_ROOT = Path(__file__).resolve().parents[2]
EDGE_SCRIPT = _LF_ROOT / "assets" / "godot" / "walkable_edge.gd"
#: The instrument's report, as it writes it.
REPORT_NAME = "drop_edges.json"
#: This module's verdict, beside it.
SCAN_NAME = "drop_edges_scan.json"
SCHEMA = "lf.walkable_edge.v1"
SCAN_SCHEMA = "drop_edges_scan/1"
#: The grid's margin beyond the rectangle the package's nav nodes and links span, metres: a body wanders past
#: the last nav node to a wall, a fence, a kerb. Measured on cold run 9318's package: the site node's own subtree
#: reached as far as the backdrop (its ground carries the backdrop's), so a node name bounded nothing; the nav
#: nodes do, and every package has them (Dispatch's `navigation_hints.json`).
EXTENT_MARGIN_M = 12.0
#: The instrument's grid, metres. Half a body's width: an edge is found within one cell of where it is.
CELL_M = 0.5
#: An edge this close to a storey's level is at that storey (a ramp head, a plate, a slab's own thickness).
LEVEL_TOL = 0.35
#: An edge this far outside a declared hole's rect is the hole's own rim (one cell plus a tread).
HOLE_MARGIN = 0.6
#: A ladder's hole is 1.5 m square: its rim plus a cell.
LADDER_R = 1.6


class DropCensusError(RuntimeError):
    """The census could not be taken. Not the same as a package with no undeclared drop."""


class UndeclaredDropError(RuntimeError):
    """A body can walk off an edge, indoors, that nothing guards and nothing declares."""


class NoSeedError(DropCensusError):
    """The package says nowhere a body starts, so the flood has no seed and the census is NOT TAKEN -- which
    the export says out loud and records, rather than refusing a package it could not measure. A
    single-building shell exported on its own (the exporter's own tests) has no `player_start`; a site
    mission always has one (Lot's getaway van)."""


def _floor_like(tail: str) -> bool:
    """A surface a body WALKS on, by what owns its collider in this toolchain's packages: Deli Counter's floor
    and basement slabs (`GreyboxBase/slab_col_<n>`), a roof (`roof_footprint/Roof`, an Empty's
    `KitCollision/Roof`), a stair's ramps, landings and discharges (`GreyboxBase/stair<n>...`, never a
    `stair_guard`), a ladder's plane, and Lot's own surfaces, which are the site node's direct children
    (`Site/Ground`, `Site/road_1`, `Site/sidewalk_1L_2`, `Site/frontage_0L_1`, `Site/kerbcut_0L_1`, `Site/path_1`,
    `Site/yard_1`) -- except `Site/perim_*`, the fence. Everything else is a thing's top."""
    if tail.startswith("Site/perim_"):
        return False
    return (tail.startswith("Site/") or re.match(r"GreyboxBase/slab_col_-?\\d+$", tail) is not None
            or tail.endswith("/Roof") or re.match(r"GreyboxBase/stair\\d", tail) is not None
            or re.match(r"GreyboxBase/ladder\\d+_plane$", tail) is not None)


def _tail(owners: list, i) -> str:
    return "none" if i is None or int(i) < 0 else "/".join(str(owners[int(i)]).split("/")[-2:])


def seed_from_anchors(export_dir) -> list:
    """Where the body starts: the package's `player_start` anchor, `transform.pos`, Godot metres."""
    path = Path(export_dir) / "gameplay_anchors.json"
    if not path.is_file():
        raise DropCensusError("no gameplay_anchors.json in the package: nothing says where a body starts")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DropCensusError(f"gameplay_anchors.json unreadable: {exc}") from exc
    starts = [a for a in (data.get("anchors") or []) if a.get("anchor_type") == "player_start"]
    if not starts:
        raise NoSeedError("gameplay_anchors.json carries no player_start anchor: nothing says where a body starts")
    pos = ((starts[0].get("transform") or {}).get("pos"))
    if not (isinstance(pos, list) and len(pos) == 3):
        raise DropCensusError("the player_start anchor carries no transform.pos: %r" % (starts[0],))
    return [float(v) for v in pos]


def extent_from_hints(export_dir, margin: float = EXTENT_MARGIN_M):
    """The rectangle the package's nav nodes and off-mesh links span, plus `margin`, as "x0,z0,x1,z1" in Godot
    metres (x and z: the ground plane) -- or "" when the package carries no nav hints, which leaves the
    instrument to walk everything it draws and says so in its report."""
    path = Path(export_dir) / "navigation_hints.json"
    if not path.is_file():
        return ""
    hints = json.loads(path.read_text(encoding="utf-8"))
    pts = []
    for n in hints.get("nodes") or []:
        p = n.get("pos")
        if isinstance(p, list) and len(p) == 3:
            pts.append((float(p[0]), float(p[2])))
    for link in hints.get("links") or []:
        for key in ("start_position", "end_position"):
            p = link.get(key)
            if isinstance(p, list) and len(p) == 3:
                pts.append((float(p[0]), float(p[2])))
    if not pts:
        return ""
    xs = [p[0] for p in pts]
    zs = [p[1] for p in pts]
    return "%.2f,%.2f,%.2f,%.2f" % (min(xs) - margin, min(zs) - margin, max(xs) + margin, max(zs) + margin)


def not_taken(reason: str) -> dict:
    """The scan a package carries when the census could not be seeded: it says so, and certifies nothing."""
    return {"schema": SCAN_SCHEMA, "not_taken": reason, "counts": None, "undeclared": [], "outdoors": []}


def measure(export_dir, godot_executable, *, script: Path = EDGE_SCRIPT, cell: float = CELL_M,
            timeout: int = 900) -> dict:
    """Run the instrument in the engine and return its report.

    The report is the evidence, not the exit code: one that does not parse, or whose schema and keys are not
    the instrument's, RAISES rather than reading as a package with no edges (the factory's CLAUDE.md, a checker
    written against a guessed schema). Leaves the package as it found it: the exporter keeps the bake's import
    cache until the censuses have run, so in an export this imports nothing; on a bare package it imports and
    then removes what it made, because the closure verdict scans every file.
    """
    from packages.exporting import occluders

    export_dir = Path(export_dir)
    report_path = export_dir / REPORT_NAME
    if not godot_executable:
        raise DropCensusError("no Godot executable: the drop-edge census cannot be taken")
    if not Path(script).is_file():
        raise DropCensusError(f"instrument missing: {script}")
    seed = seed_from_anchors(export_dir)
    links = export_dir / "navigation_hints.json"
    had_cache = (export_dir / ".godot").exists()
    occluders.ensure_imported(export_dir, godot_executable)
    bundled = export_dir / Path(script).name
    bundled.write_bytes(Path(script).read_bytes())
    proc = None
    try:
        args = [str(godot_executable), "--headless", "--path", str(export_dir),
                "--script", f"res://{Path(script).name}", "--",
                f"res://{REPORT_NAME}", str(cell), "%s,%s,%s" % tuple(seed),
                f"res://{links.name}" if links.is_file() else "", extent_from_hints(export_dir)]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        raise DropCensusError(f"the instrument did not run: {exc}") from exc
    finally:
        bundled.unlink(missing_ok=True)
        if not had_cache:
            occluders.drop_cache(export_dir)
    if not report_path.is_file():
        raise DropCensusError("the instrument wrote no report (godot exit %s)%s"
                              % (getattr(proc, "returncode", "?"), _engine_tail(proc)))
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DropCensusError(f"report unreadable: {exc}") from exc
    if not isinstance(report, dict) or report.get("schema") != SCHEMA:
        raise DropCensusError(f"report schema is {report.get('schema')!r}, not {SCHEMA!r}")
    for key in ("edges", "owners", "reachable_cells", "seed", "standable_cells", "unguarded"):
        if key not in report:
            raise DropCensusError(f"report carries no {key!r}")
    if report.get("error") or not report.get("ok", False):
        raise DropCensusError(f"the instrument failed: {report.get('error') or 'ok is false'}")
    return report


def _declared_from_links(export_dir) -> tuple:
    """(drop rects, ladders) from the package's links: rects as (x0, z0, x1, z1, level) in Godot metres
    (a `hole` rides verbatim in the site's Blender frame: Godot x = x, z = -y), ladders as their two ends,
    ((x, y, z), (x, y, z)), Godot metres."""
    path = Path(export_dir) / "navigation_hints.json"
    rects, ladders = [], []
    if not path.is_file():
        return rects, ladders
    hints = json.loads(path.read_text(encoding="utf-8"))
    for link in hints.get("links") or []:
        cap = link.get("required_capability")
        if cap == "drop" and link.get("hole") and link.get("start_position"):
            (hx0, hy0), (hx1, hy1) = link["hole"]
            rects.append((min(hx0, hx1), -max(hy0, hy1), max(hx0, hx1), -min(hy0, hy1),
                          float(link["start_position"][1])))
        elif cap == "climb":
            a, b = link.get("start_position"), link.get("end_position")
            if all(isinstance(p, list) and len(p) == 3 for p in (a, b)):
                ladders.append((tuple(float(v) for v in a), tuple(float(v) for v in b)))
    return rects, ladders


def _in_shaft(x, y, z, ladder) -> bool:
    """Whether (x, y, z) is at a ladder's shaft: at a height from its foot to its head (LEVEL_TOL either way),
    within LADDER_R of where the ladder is at that height -- a vertical ladder's column, a raked one's line.

    NOT ITS ENDS ONLY. The first draft of this rule claimed an edge within LADDER_R of either END at that end's
    height, and refused cold run 9318's package on 7 rows: the deli's ladder runs from the ground floor to the
    roof THROUGH the first floor, whose slab is cut for it, and the cut is no end of the link."""
    (x0, y0, z0), (x1, y1, z1) = ladder
    lo, hi = min(y0, y1), max(y0, y1)
    if y < lo - LEVEL_TOL or y > hi + LEVEL_TOL:
        return False
    t = 0.0 if hi - lo < 1e-6 else min(1.0, max(0.0, (y - y0) / (y1 - y0)))
    px, pz = x0 + t * (x1 - x0), z0 + t * (z1 - z0)
    return ((x - px) ** 2 + (z - pz) ** 2) ** 0.5 <= LADDER_R


def _dist_outside_rect(x, z, rect) -> float:
    """How far (x, z) lies outside the rect (0 inside)."""
    x0, z0, x1, z1 = rect[:4]
    dx = max(x0 - x, 0.0, x - x1)
    dz = max(z0 - z, 0.0, z - z1)
    return (dx * dx + dz * dz) ** 0.5


def classify(report: dict, export_dir) -> dict:
    """Every row put in the first class that claims it; the verdict is the `undeclared` count."""
    owners = report.get("owners") or []
    rects, ladders = _declared_from_links(export_dir)
    counts = {k: 0 for k in ("top", "outdoors", "stair_side", "declared_drop", "ladder_hole", "undeclared")}
    undeclared, outdoors = [], []
    for e in report.get("edges") or []:
        x, y, z = float(e["x"]), float(e["y"]), float(e["z"])
        on = _tail(owners, e.get("on"))
        if not _floor_like(on):
            cls = "top"
        elif not e.get("indoors", False):
            cls = "outdoors"
        elif re.match(r"GreyboxBase/stair\\d", on):
            cls = "stair_side"
        elif any(abs(y - r[4]) <= LEVEL_TOL and _dist_outside_rect(x, z, r) <= HOLE_MARGIN for r in rects):
            cls = "declared_drop"
        elif any(_in_shaft(x, y, z, lad) for lad in ladders):
            cls = "ladder_hole"
        else:
            cls = "undeclared"
        counts[cls] += 1
        row = {"x": x, "y": y, "z": z, "drop_m": float(e.get("drop_m", 0)), "on": on,
               "to": _tail(owners, e.get("to"))}
        if cls == "undeclared":
            undeclared.append(row)
        elif cls == "outdoors":
            outdoors.append(row)
    undeclared.sort(key=lambda r: -r["drop_m"])
    outdoors.sort(key=lambda r: -r["drop_m"])
    return {
        "schema": SCAN_SCHEMA,
        "seed": report.get("seed"),
        "standable_cells": report.get("standable_cells"),
        "reachable_cells": report.get("reachable_cells"),
        "links": {"drop": len(rects), "climb": len(ladders),
                  "used": report.get("links_used"), "unresolved": report.get("links_unresolved")},
        "drop_edges": report.get("drop_edges"), "guarded": report.get("guarded"),
        "unguarded": report.get("unguarded"), "counts": counts,
        "undeclared": undeclared[:200], "outdoors": outdoors[:50],
        "cell_m": report.get("cell_m"), "extent": report.get("extent"),
    }


def write_scan(export_dir, scan: dict) -> Path:
    path = Path(export_dir) / SCAN_NAME
    path.write_text(json.dumps(scan, indent=2, sort_keys=True), encoding="utf-8")
    return path


def summary(scan: dict) -> str:
    """One line for the export log. Says which question it answered."""
    if scan.get("counts") is None:
        return "NOT TAKEN -- %s; nothing is certified about this package's drops" % scan.get("not_taken", "?")
    c = scan["counts"]
    return ("%s reached of %s standable cells, %s unguarded drop edge(s): %d a flight's own side, %d at a "
            "declared drop, %d at a ladder's shaft, %d a thing's top, %d outdoors (reported), %d UNDECLARED "
            "indoors -- the class this gate refuses on"
            % (scan.get("reachable_cells"), scan.get("standable_cells"), scan.get("unguarded"),
               c["stair_side"], c["declared_drop"], c["ladder_hole"], c["top"], c["outdoors"], c["undeclared"]))


def assert_declared(export_dir, scan: dict) -> dict:
    """Raise `UndeclaredDropError` when a body can walk off an undeclared edge indoors. A scan not taken
    refuses nothing: it certified nothing, and said so."""
    if scan.get("counts") is None:
        return scan
    bad = int(scan["counts"].get("undeclared", 0))
    if not bad:
        return scan
    lines = [
        "UNDECLARED_DROP_INDOORS: %d unguarded edge(s) a body reaches, indoors, on a floor, that nothing "
        "declares" % bad,
        "  a body walks off each into a fall deeper than it steps; a rail guards it, a floor_hole / hatch "
        "vertical link in the building's spec declares it, and either fix lands in Deli Counter, not here",
    ]
    for r in scan["undeclared"][:8]:
        lines.append("    (%.2f, %.2f, %.2f) drop %.2f m  on %s  to %s"
                     % (r["x"], r["y"], r["z"], r["drop_m"], r["on"], r["to"]))
    lines.append("  full report: %s and %s" % (Path(export_dir) / SCAN_NAME, Path(export_dir) / REPORT_NAME))
    raise UndeclaredDropError("\\n".join(lines))
'''

TEST = '''"""The gate over undeclared drops: the verdict half, on synthetic instrument reports (0.216.0, factory roadmap 173).

The measurement half is `assets/godot/walkable_edge.gd`, proven on cold runs 9317-9318's packages in the
factory's `docs/findings/drop_edges_173/`; these pin what this module does with a report.

Run: python -m pytest -q tests/unit/test_drop_edges.py
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.exporting import drop_edges as D  # noqa: E402

OWNERS = [
    "/root/Mission/Bake/Site/b0/GreyboxBase/slab_col_1",        # 0 a floor
    "/root/Mission/Bake/Site/b0/GreyboxBase/stair1ramp_0",       # 1 a flight
    "/root/Mission/Bake/Site/b0/cartons_r1/CartonStack",         # 2 a thing
    "/root/Mission/Bake/Site/perim_N",                           # 3 the fence
    "/root/Mission/Bake/Site/road_0",                            # 4 the ground
    "/root/Mission/Bake/Site/b0/GreyboxBase/slab_col_0",         # 5 the floor below
]


def _row(x, y, z, drop, indoors, on, to=5):
    return {"x": x, "y": y, "z": z, "drop_m": drop, "indoors": indoors, "on": on, "to": to}


def _report(rows):
    return {"schema": D.SCHEMA, "ok": True, "error": "", "owners": OWNERS, "edges": rows,
            "standable_cells": 1000, "reachable_cells": 900, "drop_edges": len(rows), "guarded": 0,
            "unguarded": len(rows), "links_used": 1, "links_unresolved": 0, "cell_m": 0.5,
            "seed": {"x": 0.0, "y": 0.0, "z": 0.0}}


def _hints(tmp_path, links):
    (tmp_path / "navigation_hints.json").write_text(json.dumps({"links": links}), encoding="utf-8")


#: deli_a01's floor hole as the package carries it: a drop link at storey 1 (3.3 m) whose hole is the cut's
#: rect in the site's frame (Blender XY: Godot x = x, z = -y).
DROP_LINK = {"id": "lot:deli_a01_floor_hole_1_8_-4_navlink", "required_capability": "drop",
             "start_position": [-43.0, 3.3, 1.49], "end_position": [-43.0, 0.0, 1.49], "bidirectional": False,
             "hole": [[-43.75, -2.24], [-42.25, -0.74]]}
#: a ladder from the ground floor to the roof
CLIMB_LINK = {"id": "lot:night_deli_ladder_0_navlink", "required_capability": "climb",
              "start_position": [-43.0, 0.0, 9.49], "end_position": [-43.0, 6.6, 9.49], "bidirectional": True}


def test_floor_like_is_by_owner_not_height():
    assert D._floor_like("GreyboxBase/slab_col_-1") and D._floor_like("GreyboxBase/stair0ramp_1")
    assert D._floor_like("roof_footprint/Roof") and D._floor_like("Site/road_0") and D._floor_like("Site/kerbcut_0L_1")
    assert not D._floor_like("Site/perim_N") and not D._floor_like("cover_3/SimpleCar")
    assert not D._floor_like("GreyboxBase/stair_guard_rail_1_col") and not D._floor_like("GreyboxBase/desk_r1_col")


def test_every_class_claims_its_row(tmp_path):
    _hints(tmp_path, [DROP_LINK, CLIMB_LINK])
    rows = [
        _row(-43.0, 3.3, 1.0, 3.3, True, 0),        # at the declared hole's rim, its storey
        _row(-43.0, 0.0, 9.0, 3.3, True, 0),        # at the ladder's foot, where its hole is
        _row(-60.0, 1.1, -12.5, 1.1, True, 1),      # a flight's own open side
        _row(-54.5, 1.5, -6.0, 1.5, True, 2),       # standing on a carton stack
        _row(10.0, 0.0, 10.0, 999.0, False, 4),     # the plate's rim, under the sky
        _row(-55.0, 3.3, 3.0, 3.3, True, 0),        # a floor, indoors, nothing declares it
    ]
    scan = D.classify(_report(rows), tmp_path)
    assert scan["counts"] == {"declared_drop": 1, "ladder_hole": 1, "stair_side": 1, "top": 1, "outdoors": 1,
                              "undeclared": 1}, scan["counts"]
    assert scan["links"] == {"drop": 1, "climb": 1, "used": 1, "unresolved": 0}
    assert scan["undeclared"][0]["on"] == "GreyboxBase/slab_col_1"
    assert scan["schema"] == D.SCAN_SCHEMA


def test_a_ladder_claims_its_shaft_at_every_floor_it_passes(tmp_path):
    # cold run 9318's deli ladder: ground floor to roof, through the first floor's slab at 3.3 m; its 7 rows there
    # are no END of the link, and a rule that asked for the ends refused them
    _hints(tmp_path, [CLIMB_LINK])
    through = _row(-43.0, 3.3, 8.25, 3.3, True, 0)       # 1.24 m from the column, the floor between its ends
    above = _row(-43.0, 9.9, 8.25, 3.3, True, 0)         # over the ladder's head: not its shaft
    beside = _row(-40.0, 3.3, 9.49, 3.3, True, 0)        # 3 m from the column
    scan = D.classify(_report([through, above, beside]), tmp_path)
    assert scan["counts"]["ladder_hole"] == 1 and scan["counts"]["undeclared"] == 2, scan["counts"]
    assert {(r["y"], r["x"]) for r in scan["undeclared"]} == {(9.9, -43.0), (3.3, -40.0)}


def test_a_declared_hole_claims_its_rim_but_not_another_storey(tmp_path):
    _hints(tmp_path, [DROP_LINK])
    near = _row(-42.0, 3.3, 1.0, 3.3, True, 0)       # 0.25 m outside the rect's edge, same storey
    other = _row(-43.0, 0.0, 1.0, 3.3, True, 5)      # under the hole, the storey below
    scan = D.classify(_report([near, other]), tmp_path)
    assert scan["counts"]["declared_drop"] == 1 and scan["counts"]["undeclared"] == 1


def test_the_verdict_refuses_only_undeclared_indoors(tmp_path):
    _hints(tmp_path, [DROP_LINK, CLIMB_LINK])
    clean = D.classify(_report([_row(-43.0, 3.3, 1.0, 3.3, True, 0), _row(10.0, 0.0, 10.0, 999.0, False, 4)]), tmp_path)
    assert D.assert_declared(tmp_path, clean) is clean
    bad = D.classify(_report([_row(-55.0, 3.3, 3.0, 3.3, True, 0)]), tmp_path)
    with pytest.raises(D.UndeclaredDropError) as err:
        D.assert_declared(tmp_path, bad)
    assert "UNDECLARED_DROP_INDOORS: 1" in str(err.value) and "slab_col_1" in str(err.value)


def test_a_package_without_links_declares_nothing(tmp_path):
    scan = D.classify(_report([_row(-43.0, 3.3, 1.0, 3.3, True, 0)]), tmp_path)
    assert scan["counts"]["undeclared"] == 1 and scan["links"]["drop"] == 0


def test_the_seed_is_the_player_start(tmp_path):
    (tmp_path / "gameplay_anchors.json").write_text(json.dumps({"anchors": [
        {"anchor_type": "extraction", "transform": {"pos": [1, 2, 3]}},
        {"anchor_type": "player_start", "transform": {"pos": [44.85, 0.0, 15.465]}}]}), encoding="utf-8")
    assert D.seed_from_anchors(tmp_path) == [44.85, 0.0, 15.465]
    (tmp_path / "gameplay_anchors.json").write_text(json.dumps({"anchors": []}), encoding="utf-8")
    with pytest.raises(D.NoSeedError):                     # a DropCensusError, but one the export does not refuse on
        D.seed_from_anchors(tmp_path)
    assert issubclass(D.NoSeedError, D.DropCensusError)


def test_a_census_not_taken_certifies_nothing_and_refuses_nothing(tmp_path):
    scan = D.not_taken("gameplay_anchors.json carries no player_start anchor")
    assert scan["counts"] is None and scan["schema"] == D.SCAN_SCHEMA
    assert "NOT TAKEN" in D.summary(scan)
    assert D.assert_declared(tmp_path, scan) is scan


def test_the_extent_is_the_nav_nodes_plus_a_margin(tmp_path):
    (tmp_path / "navigation_hints.json").write_text(json.dumps({
        "nodes": [{"id": "a", "pos": [-70.0, 0.0, -20.0]}, {"id": "b", "pos": [60.0, 3.3, 30.0]}],
        "links": [CLIMB_LINK]}), encoding="utf-8")
    assert D.extent_from_hints(tmp_path, margin=10.0) == "-80.00,-30.00,70.00,40.00"
    (tmp_path / "navigation_hints.json").write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
    assert D.extent_from_hints(tmp_path) == ""                 # nothing to bound by: the instrument walks it all


def test_summary_names_the_refused_class(tmp_path):
    _hints(tmp_path, [])
    scan = D.classify(_report([_row(-55.0, 3.3, 3.0, 3.3, True, 0)]), tmp_path)
    assert "1 UNDECLARED indoors" in D.summary(scan)


def test_the_scan_lands_in_the_package(tmp_path):
    _hints(tmp_path, [])
    scan = D.classify(_report([]), tmp_path)
    path = D.write_scan(tmp_path, scan)
    assert path.name == D.SCAN_NAME and json.loads(path.read_text(encoding="utf-8"))["schema"] == D.SCAN_SCHEMA


def test_the_instrument_ships_with_level_factory():
    assert D.EDGE_SCRIPT.is_file(), D.EDGE_SCRIPT
    text = D.EDGE_SCRIPT.read_text(encoding="utf-8")
    assert "extends SceneTree" in text and "lf.walkable_edge.v1" in text
'''

EXPORT_GATE = '''    # 4.88 CAN A BODY WALK OFF AN EDGE THE LEVEL DID NOT DECLARE? (0.216.0,
    # factory roadmap 173.) See `packages.exporting.drop_edges`, which owns the
    # verdict, and `assets/godot/walkable_edge.gd`, which owns the measurement.
    #
    # IN THE ENGINE, because the question is where a BODY stands and falls:
    # the body's own capsule over every surface, a flood from the package's
    # player_start across steps, falls and its ladders, and every reached edge
    # with a fall beyond a step and nothing in the way. The declared set is
    # the package's own: its drop links, its ladders' shafts, a flight's own
    # open side. Refuses on an UNDECLARED drop INDOORS; a roof's rim, a dock
    # and a thing's top are reported.
    #
    # ABOVE THE CLOSURE VERDICT, like the greybox census: `drop_edges.json`
    # and `drop_edges_scan.json` are inside the package the verdict describes
    # and inside the manifest that lists it. NOT in `_WRITTEN_AFTER_VERDICT`.
    #
    # ENFORCED ONLY WITH A GODOT TO RUN IT, and OPTED OUT by the profile
    # (`require_declared_drops`): a build with no engine cannot take the
    # census, and a census not taken must say so rather than read as clean.
    # A package with no `player_start` (a single shell exported on its own,
    # as this exporter's tests do) seeds no flood: the census is NOT TAKEN,
    # the scan says so, and the export goes on -- not refused over a thing
    # it could not measure, not certified either.
    from packages.exporting import drop_edges
    if godot_executable:
        try:
            de_report = drop_edges.measure(export_dir, godot_executable)
            de_scan = drop_edges.classify(de_report, export_dir)
            drop_edges.write_scan(export_dir, de_scan)
            print("[export] drop edges: " + drop_edges.summary(de_scan))
            if profile.require_declared_drops:
                drop_edges.assert_declared(export_dir, de_scan)
            else:
                print("[export] drop edges: the profile does not require "
                      "declared drops, so the count above is reported, not "
                      "refused on")
        except drop_edges.NoSeedError as exc:
            de_scan = drop_edges.not_taken(str(exc))
            drop_edges.write_scan(export_dir, de_scan)
            print("[export] drop edges: " + drop_edges.summary(de_scan))
        except drop_edges.DropCensusError as exc:
            raise ExportDropEdgesError(
                "the drop-edge census failed and this build had a Godot to "
                "run it with: %s\\n  a package that cannot be measured must "
                "not be shipped claiming it was" % exc) from exc
        except drop_edges.UndeclaredDropError as exc:
            raise ExportDropEdgesError(str(exc)) from exc
    else:
        print("[export] drop edges: no Godot in this build, so the census "
              "was not taken and nothing is certified about it")
'''

CACHE_ANCHOR = "    # THE CACHE GOES HERE, AFTER THE CENSUS (0.181.0, factory roadmap 239), and\n"

ERROR_OLD = "class ExportWarmupError(RuntimeError):\n"
ERROR_NEW = '''class ExportDropEdgesError(RuntimeError):
    """A body can walk off an edge, indoors, that nothing guards and nothing
    declares -- or the census that asks could not be taken.

    Factory roadmap 173: every drop a body reaches is either GUARDED, or
    DECLARED, or a defect. The first two findings that were not the
    instrument's own were an office stair's landing open 6.67 m over its well
    and a flight's inner side open over the flight beside it, 12 edges no gate
    had seen; Deli Counter 0.225.0 fixed them at the source. See
    `packages.exporting.drop_edges` for what is refused and what is reported,
    and `assets/godot/walkable_edge.gd` for the measurement."""


class ExportWarmupError(RuntimeError):
'''

PROFILE_OLD = "    require_resource_closure: bool = True\n"
PROFILE_NEW = '''    require_resource_closure: bool = True
    #: Refuse a package in which a body can walk off an undeclared edge
    #: indoors (0.216.0, factory roadmap 173; `packages/exporting/drop_edges`).
    #: On by default for the same reason the closure verdict is: a warning
    #: nobody reads is how a package ships with a fall in it. Off, the census
    #: still runs and its count is in the export log and `drop_edges_scan.json`.
    require_declared_drops: bool = True
'''

CHANGELOG = '''## [0.216.0] - the gate over undeclared drops: a body walks off an edge only where the level says it may

**Factory roadmap 173's last step.** Every other gate in this exporter measures traversal correctness or
resource closure; none asked whether a body can FALL somewhere nobody meant. On cold run 9072's package the
instrument found, from physics, a stairwell the walker had found first; run on cold run 9317's package it
found the office's stair pit -- a landing open 6.67 m over its well, a flight's inner side open over the flight
beside it, 12 edges no gate had seen -- and Deli Counter 0.225.0 fixed them at the source. Then the declared set
was made to ship in the package (Deli Counter 0.226.0, Lot 0.125.0, Dispatch 0.5.3: a one-way off-mesh link on
every `floor_hole` / `hatch` vertical link, with the cut's rect). This is the gate that reads it.

### Added
- **`assets/godot/walkable_edge.gd`**, the measurement, Level Factory's own copy of the factory's
  `tools/walkable_edge.gd` (sha256 878f755daa9521ae3069c0fb49b8d5d88662abff3263cdcde2504998d2e674f9): the body's own capsule over every surface on a grid, lifted on slopes,
  with surfaces steeper than `floor_max_angle` skipped and occupied ones kept as walls; a flood from the seed
  across steps, falls and the package's ladders; every reached edge whose neighbour drops further than a step
  with nothing above step-over height between and nothing in the body's way, with what each stands on and drops
  to. Nine repairs on one package before its residue was the level's and not its own (the factory's
  `docs/findings/drop_edges_173/`). Bounded to the rectangle the package's nav nodes and links span plus 12 m,
  its corner snapped to the cell lattice: on cold run 9318's package 341 x 126 cells and 7 s against 1,521 a
  side and 150 s unbounded, with the same rows. The `Site` node's subtree reached as far as the backdrop, and an
  unsnapped corner lost a stair's one-cell turn landing; both are measured in the factory's finding.
- **`packages/exporting/drop_edges.py`**, the verdict: seeds from the package's `player_start`, links from its
  `navigation_hints.json`, classes every unguarded edge -- a thing's top, outdoors, a flight's own side, a
  declared drop's rim, a ladder's shaft at any floor it passes -- and REFUSES on an undeclared drop indoors.
  `drop_edges.json` (the instrument's report) and `drop_edges_scan.json` (the verdict) land in the package
  above the closure verdict. A package with no `player_start` seeds no flood: the census is NOT TAKEN, the scan
  says so, and the export goes on (this suite's own shell exports have none).
- `ExportProfile.require_declared_drops` (default True; off, the census runs and reports); `ExportDropEdgesError`;
  step 4.88 of `export_mission`, after the greybox census and before the cache goes.
- `tests/unit/test_drop_edges.py` (12): a floor is known by its owner, not its height, every class claims its
  row, a ladder claims its shaft at every floor it
  passes, a hole claims its rim and not the storey below, the verdict refuses only undeclared indoors, a package
  without links declares nothing, the seed is the player_start, a census not taken certifies and refuses
  nothing, the extent is the nav nodes plus a margin, the instrument ships.

### Measured
Through this module, in the engine, on cold run 9318's package (Deli Counter 0.225.0, which predates the drop
links): 54 unguarded edges, 46 indoors -- 10 a flight's own side, 3 a rail's top, 13 a ladder's shaft, and 20 at
deli_a01's floor hole, REFUSED, because that package does not declare the hole. The same report with the link
Deli Counter 0.226.0 records and Lot 0.125.0 places passes with 0 undeclared. The first draft asked for a
ladder's ENDS only and also refused 7 rows where the deli's roof ladder passes through the first floor; the
shaft rule claims them. The first export through the gate is the factory's cold run 9320.

'''


def write_tests():
    (LF / "tests" / "unit" / "test_drop_edges.py").write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_drop_edges.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = TOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TOOL_SHA256, "tools/walkable_edge.gd is not the instrument this patch pins"
    (LF / "assets" / "godot" / "walkable_edge.gd").write_bytes(raw)
    (LF / "packages" / "exporting" / "drop_edges.py").write_text(MODULE, encoding="utf-8", newline="\n")
    ex = LF / "packages" / "exporting" / "export.py"
    _apply(ex, ERROR_OLD, ERROR_NEW)
    _apply(ex, PROFILE_OLD, PROFILE_NEW)
    _apply(ex, CACHE_ANCHOR, EXPORT_GATE + "\n" + CACHE_ANCHOR)
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.215.1", v.read_text(encoding="utf-8")
    v.write_text("0.216.0", encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    text = rawc.decode("utf-8")
    assert text.startswith("## [0.215.1]"), text[:40]
    cl.write_bytes((CHANGELOG.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Level Factory 0.216.0 applied: the instrument, the verdict module, the export step, the profile flag, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
