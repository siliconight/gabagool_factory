"""Deli Counter 0.266.0 on a CLONE (<repo>): an indoor litter bin is a wall piece (the walker's walk of cold run 9386,
finding 8: "garbage cans are usually up against walls inside buildings"). Anchored; refuses on a miss.

    python edit_dc_bins.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("level_design.py", [
    ('''    _piece("litter_bin", ((0.6, 0.6, 1.0), (0.5, 0.5, 0.85)), "cluster"),''',
     '''    # A LITTER BIN STANDS AGAINST A WALL (0.266.0). The walker, of deli_a03's
    # bin alone at an aisle's end: "garbage cans are usually up against walls
    # inside buildings". It was a cluster piece, and a piece is placed by its
    # own `where`, not by the list a recipe names it in: the corridor's and
    # the hallway's wall runs listed it and stood it on the floor grid, and
    # five recipes clustered it. A wall piece in every recipe now.
    _piece("litter_bin", ((0.6, 0.6, 1.0), (0.5, 0.5, 0.85)), "wall"),'''),
    ('''                   "wall": ("cabinet_panel", "shelf_run"),
                   "floor": (),
                   "clusters": ((("barrel_drum", "cartons", "litter_bin"),
                                 2, 3),)},''',
     '''                   "wall": ("cabinet_panel", "shelf_run", "litter_bin"),
                   "floor": (),
                   "clusters": ((("barrel_drum", "cartons"), 2, 3),)},'''),
    ('''                "wall": ("counter_kitchen", "shelf_run", "counter_kitchen"),
                "floor": ("table_work",),
                "clusters": ((("cartons", "litter_bin"), 2, 3),)},''',
     '''                "wall": ("counter_kitchen", "shelf_run", "counter_kitchen",
                         "litter_bin"),
                "floor": ("table_work",),
                "clusters": ((("cartons",), 2, 3),)},'''),
    ('''              "wall": ("chair_waiting", "chair_waiting", "sofa", "atm",
                       "vending", "payphone"),
              "floor": ("table_low",),
              "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1)),''',
     '''              "wall": ("chair_waiting", "chair_waiting", "sofa", "atm",
                       "vending", "payphone", "litter_bin"),
              "floor": ("table_low",),
              "clusters": ((("stanchion",), 3, 4),),'''),
    ('''             "wall": ("chair_waiting", "shelf_run", "chair_waiting",
                      "cabinet_file", "vending"),
             "floor": ("table_dining",),
             "clusters": ((("litter_bin",), 1, 1),),''',
     '''             "wall": ("chair_waiting", "shelf_run", "chair_waiting",
                      "cabinet_file", "vending", "litter_bin"),
             "floor": ("table_dining",),
             "clusters": (),'''),
    ('''                   "wall": ("shelf_run", "shelf_run", "cabinet_file",
                            "vending"),
                   "floor": (),
                   "rows": (), "rows_share": 0.25,
                   "clusters": ((("cartons",), 2, 3), (("litter_bin",), 1, 1)),''',
     '''                   "wall": ("shelf_run", "shelf_run", "cabinet_file",
                            "vending", "litter_bin"),
                   "floor": (),
                   "rows": (), "rows_share": 0.25,
                   "clusters": ((("cartons",), 2, 3),),'''),
])
edit("tests/test_furnish.py", [
    ('''    """2-4 pieces 0.3-0.8 m apart: every cluster piece but a lone litter bin
    has a neighbour within 0.8 m, edge to edge, and none stands taller than
    `_CLUSTER_MAX_H` in the middle of the floor."""''',
     '''    """2-4 pieces 0.3-0.8 m apart: every cluster piece has a neighbour within
    0.8 m, edge to edge, and none stands taller than `_CLUSTER_MAX_H` in the
    middle of the floor. (A lone litter bin was excused until 0.266.0, when
    the bin became a wall piece.)"""'''),
    ('''    for a in cl:
        if a["name"].startswith("litter_bin"):
            continue
        near = sorted''',
     '''    for a in cl:
        near = sorted'''),
])
print("level_design: litter_bin a wall piece, out of five recipes' clusters and into their wall runs")
