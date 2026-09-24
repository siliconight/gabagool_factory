"""The site graph includes the street, because the buildings do.

THE MEASUREMENT THAT FORCED THIS. `tools/level_recipe_census.py` scored every
candidate site spec on disk against the level recipe's `approaches` line:

    objective_approaches   0   38 specs
                           1   37 specs
                           2    4 specs
                           3+   0 specs

    sites carrying an isolated-building warning   65 of 79
    of those, naming two buildings                20

On cold run 9077's shipped package -- a run reported as a genuine zero -- the
adjacency reads `{b0: [b1], b1: [b0], b2: []}` and Lot prints "buildings with
no declared path-route from 'b0': b2".

THE GRAPH WAS WRONG ABOUT THE LEVEL, NOT THE OTHER WAY ROUND. `build_graph`
says so in its own docstring: "paths to raw points don't connect buildings and
are ignored here (they're still geometry in the scene)". Level Factory emits a
chain of building-to-building paths and DELIBERATELY drops any segment that
crosses a road -- cold run 9049, where a chain segment cut across a cross
street mid-block and read as a fake crosswalk. What it emits instead is a door
path from every building to the sidewalk, and the STREET carries the
connection. So a site of three buildings, one path edge and two roads is not a
site with one connection; every building on it can be walked to from every
other, down the street, and the graph modelled none of that.

An approach gate over that graph would have measured path authoring and failed
one hundred percent of levels ever generated. That is why the census ran first.

WHAT COUNTS AS MEETING A STREET: the declared door path, not proximity. Lot
already treats a path as the authored statement of where a building meets the
ground -- `kerb_crossings` drops a kerb where a path crosses one. So a raw-point
path with one end at a building and the other inside a road's band (carriageway
plus sidewalk) is that building's door onto that road, and two buildings with
doors onto the same road are connected. Proximity was the alternative and it is
worse: it needs a footprint the spec does not carry, and it would connect a
building that happens to sit near a road it has no way onto.

UNAMBIGUOUS OR NOT AT ALL. A path end is matched to a building only when the
nearest building centre is clearly nearest -- half the distance to the next one.
A tie means the spec does not say which building the door belongs to, and
guessing would put an edge somewhere nobody declared.

THE EDGES ARE A CLIQUE PER ROAD, and that is a model with a stated limit: it
says "these buildings share a street" and not "they are near each other along
it". For a row that is right -- the objective can be approached from either
direction. It does NOT distinguish a neighbour from a building 200 m down the
same road, and a later item that wants that will need distance along `t`.

STRICTLY MORE PERMISSIVE, checked before writing: `gate()` raises when
`_distinct_routes_to` is BELOW 2 and when no route exists at all, and
`isolated_buildings` is a warning about absence. Adding edges can only move a
site from failing to passing, never the reverse.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "lot" / "site_tactical.py"

OLD = '''def build_graph(site_spec):
    """Adjacency over building ids using declared building-to-building paths.
    Returns {bid: set(neighbour bids)}. Paths to raw points don't connect
    buildings and are ignored here (they're still geometry in the scene)."""
    ids = [b["id"] for b in site_spec.get("buildings", [])]
    adj = {bid: set() for bid in ids}
    for p in site_spec.get("paths", []):
        a, b = _path_endpoints(p)
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    return adj
'''

NEW = '''def _road_frame(road):
    """(unit along, unit perpendicular, length) for a road's centre line."""
    a, b = road.get("a"), road.get("b")
    dx, dy = float(b[0]) - float(a[0]), float(b[1]) - float(a[1])
    length = math.hypot(dx, dy) or 1e-9
    return (dx / length, dy / length), (-dy / length, dx / length), length


def _point_on_road(point, road):
    """Is `point` inside this road's band -- carriageway plus its sidewalks?

    The band, not the centre line: a door path stops ON the sidewalk (Level
    Factory ends one `SIDEWALK_WIDTH * SPUR_INTO_WALK` short of the walk's
    centre, deliberately, so Lot does not read it as a street crossing). A test
    against the centre line would therefore match no door path ever written.
    """
    (ux, uy), (px, py), length = _road_frame(road)
    a = road.get("a")
    vx, vy = float(point[0]) - float(a[0]), float(point[1]) - float(a[1])
    t = vx * ux + vy * uy
    off = vx * px + vy * py
    half = float(road.get("width", 9.0)) / 2.0 + float(road.get("sidewalk") or 0.0)
    return -1e-6 <= t <= length + 1e-6 and abs(off) <= half + 1e-6


def _building_at(point, centres):
    """The building this path end belongs to, or None when the spec is unclear.

    Nearest centre, and only when it is CLEARLY nearest -- within half the
    distance to the runner-up. A tie is a spec that does not say which building
    the door belongs to, and an edge nobody declared is worse than a missing
    one.
    """
    if not centres:
        return None
    ranked = sorted(((math.dist(point, c), bid) for bid, c in centres.items()))
    if len(ranked) == 1:
        return ranked[0][1]
    (d0, bid), (d1, _) = ranked[0], ranked[1]
    return bid if d0 * 2.0 <= d1 else None


def street_members(site_spec):
    """{road index: set of building ids with a declared door onto that road}.

    A building meets a road when one end of a raw-point path lands in that
    road's band and the other end identifies a building. That path is Lot's own
    notion of where a building meets the ground -- `kerb_crossings` drops a kerb
    where one crosses a kerb line -- so it is the authored answer rather than a
    guess from proximity.
    """
    roads = site_spec.get("roads") or []
    centres = {}
    for b in site_spec.get("buildings", []) or []:
        at = b.get("at")
        if isinstance(at, (list, tuple)) and len(at) >= 2:
            centres[b["id"]] = (float(at[0]), float(at[1]))
    out = {i: set() for i in range(len(roads))}
    for p in site_spec.get("paths", []) or []:
        a, b = p.get("a"), p.get("b")
        if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))):
            continue                      # a building-to-building path
        for end, other in ((a, b), (b, a)):
            for i, road in enumerate(roads):
                if not _point_on_road(end, road):
                    continue
                bid = _building_at(other, centres)
                if bid is not None:
                    out[i].add(bid)
    return out


def build_graph(site_spec):
    """Adjacency over building ids: declared paths AND the streets they meet.

    Returns {bid: set(neighbour bids)}.

    UNTIL 0.77.0 THIS WAS PATHS ONLY, and the docstring said so plainly --
    "paths to raw points don't connect buildings and are ignored here". The
    consequence was measured over every candidate spec on disk: 65 of 79 sites
    reported an isolated building, and the objective's approach count read 0 on
    38 of them and never exceeded 2. Level Factory emits a chain of
    building-to-building paths, drops any segment crossing a road (cold run
    9049), and gives every building a door path to the sidewalk instead -- so
    the street carried the connection and this function could not see it.

    Buildings with a declared door onto the same road are joined. That is a
    clique per road: it says they share a street, not that they are adjacent
    along it. A measure that needs "next door" will need distance along the
    road's own `t`, which `street_members` has and this does not use.
    """
    ids = [b["id"] for b in site_spec.get("buildings", [])]
    adj = {bid: set() for bid in ids}
    for p in site_spec.get("paths", []):
        a, b = _path_endpoints(p)
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    for members in street_members(site_spec).values():
        on_street = sorted(m for m in members if m in adj)
        for i, x in enumerate(on_street):
            for y in on_street[i + 1:]:
                adj[x].add(y)
                adj[y].add(x)
    return adj
'''


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    hits = text.count(OLD)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    out = text.replace(OLD, NEW).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
