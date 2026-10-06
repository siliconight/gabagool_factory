"""Deli Counter 0.191.0, the tests for `patch_dc_circulation_parts.py`,
applied first so they are seen failing on 0.190.0.

    python patch_dc_circulation_parts_tests.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_circulation.py"

ANCHOR = '''def test_check_shell_reports_zero_props_rather_than_ok(monkeypatch):
    """A gate with no input is not a pass. `ok` may be True, but `props: 0`
    has to be visible so a caller can tell 'nothing to check' from 'checked
    and clean' -- the failure this whole finding is an instance of."""
    import zfight_gate
    monkeypatch.setattr(zfight_gate, "_node_world_boxes", lambda p: [])
    out = C.check_shell("ignored.glb", None,
                        {"surface_roles": {}, "stair_systems": [_stair()]})
    assert out["props"] == 0
'''

ADD = '''

# ---- the dressing arm boxes PARTS, not merged nodes (0.191.0) ---------------
#
# Zoo merges a building's covers per side per material (1.68.0). On cold run
# 9187's gs_empty_rowhome_l, 9 nodes carry 109 covers and each concrete
# node's box is the whole building, about 6.7 x 7.1 x 12 m. So every doorway
# lay inside a box and every building with covers failed the gate on every
# run from 9164 to 9187: 9, 48, 28 and 27 conflicts on the four measured
# (`docs/findings/presentation_gates/` at the factory root). Boxed by part
# (position-welded, index-connected components), the same four read 0, and
# a 1 m crate planted in a doorway is still caught.

def _write_glb(path, nodes):
    """A GLB with one mesh per node; each box written as a real export writes
    one: 24 vertices, four a face, because faces carry their own normals and
    UVs. ``nodes``: [(name, [(lo, hi), ...])] in GLB space."""
    import struct
    from pygltflib import (GLTF2, Accessor, Attributes, Buffer, BufferView,
                           Mesh, Node, Primitive, Scene)
    g = GLTF2()
    blob = bytearray()
    for name, boxes in nodes:
        pos, idx = [], []
        for lo, hi in boxes:
            c = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
                 for z in (lo[2], hi[2])]
            for face in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                         (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
                base = len(pos)
                pos += [c[k] for k in face]
                idx += [base, base + 1, base + 2, base, base + 2, base + 3]
        p_off = len(blob)
        blob += struct.pack("<%df" % (3 * len(pos)), *[v for q in pos for v in q])
        i_off = len(blob)
        blob += struct.pack("<%dI" % len(idx), *idx)
        g.bufferViews += [BufferView(buffer=0, byteOffset=p_off, byteLength=12 * len(pos)),
                          BufferView(buffer=0, byteOffset=i_off, byteLength=4 * len(idx))]
        g.accessors += [
            Accessor(bufferView=len(g.bufferViews) - 2, componentType=5126,
                     count=len(pos), type="VEC3",
                     min=[min(q[k] for q in pos) for k in range(3)],
                     max=[max(q[k] for q in pos) for k in range(3)]),
            Accessor(bufferView=len(g.bufferViews) - 1, componentType=5125,
                     count=len(idx), type="SCALAR")]
        g.meshes.append(Mesh(primitives=[Primitive(
            attributes=Attributes(POSITION=len(g.accessors) - 2),
            indices=len(g.accessors) - 1)]))
        g.nodes.append(Node(name=name, mesh=len(g.meshes) - 1))
    g.scenes = [Scene(nodes=list(range(len(g.nodes))))]
    g.scene = 0
    g.buffers = [Buffer(byteLength=len(blob))]
    g.set_binary_blob(bytes(blob))
    g.save_binary(str(path))
    return str(path)


def _door_godot():
    """The doorway volume `_doorway()` derives, in GLB space."""
    return C.to_godot_aabb(C.doorway_volume(_doorway()))


def _frame_strips(door):
    """Three thin strips hugging the aperture, as a cover frame is: two
    jambs and a head, 5 cm deep across the wall."""
    lo, hi = door
    zc = (lo[2] + hi[2]) / 2
    return [([lo[0] - 0.08, 0.0, zc - 0.025], [lo[0], 2.15, zc + 0.025]),
            ([hi[0], 0.0, zc - 0.025], [hi[0] + 0.08, 2.15, zc + 0.025]),
            ([lo[0] - 0.08, 2.1, zc - 0.025], [hi[0] + 0.08, 2.18, zc + 0.025])]


def test_a_merged_node_box_spans_its_parts(tmp_path):
    """The defect in one picture: a frame's strips and a base course 4 m away,
    merged into one node, box as one thing across the doorway."""
    door = _door_godot()
    far = ([door[1][0] + 4.0, 0.0, -0.5], [door[1][0] + 6.0, 0.3, 0.0])
    glb = _write_glb(tmp_path / "d.glb", [("CoverS_concrete", _frame_strips(door) + [far])])
    import zfight_gate
    nodes = zfight_gate._node_world_boxes(glb)
    vols = [("doorway:d0", C.doorway_volume(_doorway()))]
    assert len(nodes) == 1
    assert C.prop_conflicts(nodes, vols), "the merged box should cover the door"


def test_parts_are_welded_boxes_not_faces(tmp_path):
    """24 vertices a box, four a face: unwelded, each face is its own
    component and a zero-thickness plane that `_pen` can never flag."""
    glb = _write_glb(tmp_path / "d.glb", [("Cover", [([0, 0, 0], [1, 2, 3]),
                                                    ([5, 0, 0], [6, 1, 1])])])
    parts = C.dressing_part_boxes(glb)
    assert len(parts) == 2, parts
    sizes = sorted(tuple(round(b[1][k] - b[0][k], 6) for k in range(3)) for _n, b in parts)
    assert sizes == [(1.0, 1.0, 1.0), (1.0, 2.0, 3.0)]


def test_a_merged_frame_passes_the_doorway(tmp_path):
    door = _door_godot()
    far = ([door[1][0] + 4.0, 0.0, -0.5], [door[1][0] + 6.0, 0.3, 0.0])
    glb = _write_glb(tmp_path / "d.glb", [("CoverS_concrete", _frame_strips(door) + [far])])
    out = C.check_dressing(glb, {"slots": [_doorway()]}, {})
    assert out["ok"] is True, out
    assert out["nodes"] == 1 and out["props"] == 4


def test_a_crate_in_the_doorway_is_still_caught(tmp_path):
    """The positive control: the part boxes must still be able to fail."""
    door = _door_godot()
    c = [(door[0][k] + door[1][k]) / 2 for k in range(3)]
    crate = ([c[0] - 0.5, 0.0, c[2] - 0.5], [c[0] + 0.5, 1.0, c[2] + 0.5])
    glb = _write_glb(tmp_path / "d.glb",
                     [("CoverS_concrete", _frame_strips(door) + [crate])])
    out = C.check_dressing(glb, {"slots": [_doorway()]}, {})
    assert out["ok"] is False
    assert [x["volume"] for x in out["conflicts"]] == ["doorway:w_open0"]
    assert out["conflicts"][0]["penetration"] > 0.5


# ---- a stair's own guards stand at its hole's edge (0.191.0) ----------------
#
# `deli_counter.py` `_stair_guards` bakes `stairwell.stair_guards` as volumes
# named `stair_guard_{kind}_{k}`, and every volume is role `prop`. A back guard
# stands a storey above its flight's foot, inside the "full vertical column":
# office's `stair_guard_back_10`, 0.26 m into `office_stair_0`. It is excused
# from STAIR volumes and said to be; anywhere else it is a prop like any other.

def test_the_guard_prefix_is_the_builders():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    src = open(os.path.join(here, "deli_counter.py"), encoding="utf-8").read()
    body = src[src.index("def _stair_guards"):]
    assert 'name=f"stair_guard_{g[\\'kind\\']}_{k}"' in body
    assert C.GUARD_PREFIX == "stair_guard_"


def test_a_stairs_guard_is_excused_from_the_stair(monkeypatch):
    import zfight_gate
    monkeypatch.setattr(zfight_gate, "_node_world_boxes",
                        lambda p: [("stair_guard_back_3", ([5.0, 3.6, -5.5],
                                                           [6.0, 4.6, -4.5])),
                                   ("VAULT", ([5.0, 0.0, -5.5], [6.0, 3.0, -4.5]))])
    gp = {"surface_roles": {"stair_guard_back_3": "prop", "VAULT": "prop"},
          "stair_systems": [_stair()]}
    out = C.check_shell("ignored.glb", None, gp)
    assert [x["prop"] for x in out["conflicts"]] == ["VAULT"]
    assert [x["prop"] for x in out["excused"]] == ["stair_guard_back_3"]


def test_a_guard_in_a_doorway_is_not_excused(monkeypatch):
    import zfight_gate
    door = _door_godot()
    c = [(door[0][k] + door[1][k]) / 2 for k in range(3)]
    monkeypatch.setattr(zfight_gate, "_node_world_boxes",
                        lambda p: [("stair_guard_rail_1",
                                    ([c[0] - 0.4, 0.0, c[2] - 0.4],
                                     [c[0] + 0.4, 1.0, c[2] + 0.4]))])
    gp = {"surface_roles": {"stair_guard_rail_1": "prop"}}
    out = C.check_shell("ignored.glb", {"slots": [_doorway()]}, gp)
    assert out["ok"] is False and out["excused"] == []
'''


def main():
    data = TEST.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(ANCHOR), "test_circulation.py no longer ends where it did"
    assert "dressing_part_boxes" not in text
    TEST.write_bytes((text + ADD).encode("utf-8"))
    print("test_circulation.py: 7 tests for the circulation gate's parts and guards")


if __name__ == "__main__":
    main()
