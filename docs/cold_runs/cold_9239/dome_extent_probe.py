"""Where a dome's glass sits against its canopy, in the fixtures GLB's own frame, and which way a
troffer's diffuser faces (the control for which axis is up).

    python docs/cold_runs/cold_9239/dome_extent_probe.py <fixtures.glb>

Prints, for the first dome's canopy and glass meshes, the world-y extent of their vertices
(node transforms applied), and the mean normal y of the first troffer diffuser. It prints what it
measured and stops.
"""
import struct
import sys

import numpy as np
from pygltflib import GLTF2


def _vec3(g, blob, acc_i):
    acc = g.accessors[acc_i]
    bv = g.bufferViews[acc.bufferView]
    start = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    stride = bv.byteStride or 12
    return np.array([struct.unpack_from("<3f", blob, start + k * stride) for k in range(acc.count)])


def _node_matrix(node):
    if node.matrix:
        return np.array(node.matrix, dtype=float).reshape(4, 4).T
    t = np.eye(4)
    if node.translation:
        t[:3, 3] = node.translation
    r = np.eye(4)
    if node.rotation:
        x, y, z, w = node.rotation
        r[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    s = np.eye(4)
    if node.scale:
        s[0, 0], s[1, 1], s[2, 2] = node.scale
    return t @ r @ s


def main(path):
    g = GLTF2().load(path)
    blob = g.binary_blob()
    parent = {}
    for i, n in enumerate(g.nodes):
        for c in n.children or []:
            parent[c] = i

    def world(i):
        m = _node_matrix(g.nodes[i])
        while i in parent:
            i = parent[i]
            m = _node_matrix(g.nodes[i]) @ m
        return m

    def extent(name_prefix):
        for i, n in enumerate(g.nodes):
            if n.mesh is not None and n.name.startswith(name_prefix):
                m = world(i)
                for p in g.meshes[n.mesh].primitives:
                    pos = _vec3(g, blob, p.attributes.POSITION)
                    pw = (m @ np.c_[pos, np.ones(len(pos))].T).T[:, :3]
                    nrm = _vec3(g, blob, p.attributes.NORMAL)
                    nw = (m[:3, :3] @ nrm.T).T
                    return n.name, pw[:, 1].min(), pw[:, 1].max(), nw[:, 1].mean()
        return None

    for pre in ("Dome_Canopy", "Dome_Glass", "Dome_Finial", "FluorescentFixture_Diffuser"):
        got = extent(pre)
        if got:
            print("%-28s y %.3f .. %.3f, mean normal y %+.3f" % got)
        else:
            print("%-28s not found" % pre)


if __name__ == "__main__":
    main(sys.argv[1])
