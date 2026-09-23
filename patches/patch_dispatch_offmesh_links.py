"""Carry a ladder's off-mesh nav link into the shipped package.

THE WALKER, 2026-09-23, asking whether the levels have navmesh off-mesh links
at all. They do -- `deli_counter.ladder._nav_link` emits one per ladder, with a
per-type traversal cost, direction, `required_capability: "climb"`, agent
types, lock state and a multiplayer reservation state -- and it reaches the
shell's `gameplay.json` and stops there.

MEASURED on `walk_export_club_block_009`, which HAS ladders (the first attempt
used a package with none and proved nothing, which is why this note names the
package):

    nav_link in the shell's gameplay.json      yes
    nav_link anywhere in the shipped package   0 files
    LADDER_ markers in the building scene      yes
    ladder entries in interactives.json (35)   0

So the climb marker ships and the link does not: a player can climb, and a
consumer who bakes a navmesh from this package -- which `navmesh:
bake_required` tells them to do -- has no edge to path along and will route
around the ladder or call the roof unreachable. Roadmap 172.

THE FRAME, stated because this is exactly where it would go wrong. A link's
`start_position` / `end_position` are in Deli Counter's Z-up frame, the same
frame as the nav hint NODES (measured: [8.0, -12.0, 0.0] to [8.0, -12.0, 6.6],
climbing in Z). They therefore get the same `blender_to_godot` conversion and
the same `source:` id namespacing the nodes already get -- not a different
treatment, because two spellings of one transform is how a frame bug starts.

SCHEMA v0.2 -> v0.3, because the payload gained a list and a reader that
believes it has seen every key of v0.2 would be wrong. `docs/FORMATS.md` and
the contract test move with it.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAVGRAPH = ROOT / "dispatch" / "dispatch" / "navgraph.py"
IMPORTER = ROOT / "dispatch" / "dispatch" / "importers" / "deli_counter.py"
TEST = ROOT / "dispatch" / "tests" / "test_contract_v03.py"

# ------------------------------------------------------------- navgraph.py
NG_A1 = '''@dataclass
class NavGraph:
    nodes: dict = field(default_factory=dict)   # id -> NavNode
    adj: dict = field(default_factory=dict)     # id -> set(id)
    bridges: list = field(default_factory=list)  # auto-added cross-source links
'''

NG_N1 = '''@dataclass
class NavGraph:
    nodes: dict = field(default_factory=dict)   # id -> NavNode
    adj: dict = field(default_factory=dict)     # id -> set(id)
    bridges: list = field(default_factory=list)  # auto-added cross-source links
    #: OFF-MESH links -- a ladder, and later a drop or a vault. NOT edges: an
    #: edge says two nav-hint nodes are connected by walkable floor, and a
    #: baked navmesh already knows that. This says a body can get from one
    #: point to another by a means the mesh cannot express, which is the whole
    #: reason the engines in this space have a separate concept for it.
    #:
    #: Deli Counter computes them (`ladder._nav_link`) with a per-type cost so
    #: a planner prefers a stair to a caged ladder, a `required_capability`, an
    #: access state, and a reservation state a multiplayer server needs. None
    #: of that is re-derivable from a marker position, which is why it is
    #: carried rather than left for the consumer.
    links: list = field(default_factory=list)
'''

NG_A2 = '''    def add_link(self, a: str, b: str) -> None:
        if a in self.nodes and b in self.nodes and a != b:
            self.adj[a].add(b)
            self.adj[b].add(a)
'''

NG_N2 = '''    def add_link(self, a: str, b: str) -> None:
        if a in self.nodes and b in self.nodes and a != b:
            self.adj[a].add(b)
            self.adj[b].add(a)

    def add_off_mesh_link(self, rec: dict, source: str, up_axis: str = "z") -> None:
        """Record one off-mesh link, in the nodes' frame and id space.

        The positions arrive in the producing tool's frame and are converted
        exactly as `load_nav_hints` converts a node's -- one transform, used
        twice, rather than two spellings of it. The id is namespaced with the
        source for the same reason node ids are: two tools may both ship a
        `ladder_0`.
        """
        def _pos(raw):
            return list(blender_to_godot(raw) if up_axis == "z"
                        else tuple(float(v) for v in raw))

        out = dict(rec)
        out["id"] = f"{source}:{rec.get('id', 'link')}"
        out["source"] = source
        if "start_position" in rec:
            out["start_position"] = _pos(rec["start_position"])
        if "end_position" in rec:
            out["end_position"] = _pos(rec["end_position"])
        self.links.append(out)
'''

NG_A3 = '''        return {
            "schema": "dispatch.navigation_hints.v0.2",
            "navmesh": "bake_required",
            "nodes": [
                {"id": n.id, "pos": list(n.pos), "source": n.source}
                for n in sorted(self.nodes.values(), key=lambda n: n.id)
            ],
            "edges": edges,
        }
'''

NG_N3 = '''        return {
            # v0.3 adds `links`. A reader that believed it had seen every key
            # of v0.2 would be wrong about this package, so the version moves.
            "schema": "dispatch.navigation_hints.v0.3",
            "navmesh": "bake_required",
            "nodes": [
                {"id": n.id, "pos": list(n.pos), "source": n.source}
                for n in sorted(self.nodes.values(), key=lambda n: n.id)
            ],
            "edges": edges,
            "links": sorted(self.links, key=lambda l: str(l.get("id", ""))),
        }
'''

NG_A4 = '''    merged = NavGraph()
    for g in graphs:
        for n in g.nodes.values():
            merged.add_node(n)
        for a in g.adj:
            for b in g.adj[a]:
                merged.add_link(a, b)
'''

NG_N4 = '''    merged = NavGraph()
    for g in graphs:
        for n in g.nodes.values():
            merged.add_node(n)
        for a in g.adj:
            for b in g.adj[a]:
                merged.add_link(a, b)
        # Off-mesh links survive the merge. They were namespaced by source on
        # the way in, so there is nothing to reconcile.
        merged.links.extend(g.links)
'''

# -------------------------------------------------- importers/deli_counter.py
IM_A = '''    imp.meta["interactives"] = list(gp.get("interactives", []) or [])
    nav = read_json_file(rt.files["shell.nav_hints.json"], "deli_counter")
    imp.nav = load_nav_hints(nav, "deli_counter", str(nav.get("up_axis", up)))
'''

IM_N = '''    imp.meta["interactives"] = list(gp.get("interactives", []) or [])
    nav = read_json_file(rt.files["shell.nav_hints.json"], "deli_counter")
    imp.nav = load_nav_hints(nav, "deli_counter", str(nav.get("up_axis", up)))
    # OFF-MESH LINKS, from the gameplay manifest rather than the nav hints:
    # Deli Counter computes one per ladder (`ladder._nav_link`) and files it on
    # the ladder, because that is where its cost, capability and access state
    # live. Without this the package ships a climb MARKER and no edge, so a
    # player can climb a ladder and an AI cannot path up it (roadmap 172).
    _up = str(nav.get("up_axis", up))
    for _lad in gp.get("ladders", []) or []:
        _link = _lad.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "deli_counter", _up)
'''

# ------------------------------------------------------------------- test
T_A = '''    assert d["schema"] == "dispatch.navigation_hints.v0.2"
'''

T_N = '''    assert d["schema"] == "dispatch.navigation_hints.v0.3"
'''


def _apply(path: Path, edits) -> None:
    data = path.read_bytes()
    if b"\r\n" in data:
        raise SystemExit(f"REFUSED: {path.name} expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(edits, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(
                f"REFUSED: {path.name} anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit(f"REFUSED: {path.name} would gain CRLF")
    path.write_bytes(out)
    print(f"{path.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


def main() -> None:
    _apply(NAVGRAPH, ((NG_A1, NG_N1), (NG_A2, NG_N2), (NG_A3, NG_N3),
                      (NG_A4, NG_N4)))
    _apply(IMPORTER, ((IM_A, IM_N),))
    _apply(TEST, ((T_A, T_N),))


if __name__ == "__main__":
    main()
