"""Do the dome glass's normals point out of the bowl? Reads a fixtures GLB's M_Dome_Lens primitives.

    python docs/cold_runs/cold_9239/dome_normals_probe.py <fixtures.glb> [material]

For each primitive of the material: the share of its vertices whose normal points away from the
primitive's own centroid (outward) and the mean normal's z. A bowl hanging below a ceiling, faces
out, reads outward near 1.0 and a mean z below 0. It prints what it measured and stops.
"""
import struct
import sys

from pygltflib import GLTF2


def _read(g, blob, acc_i):
    acc = g.accessors[acc_i]
    bv = g.bufferViews[acc.bufferView]
    start = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    n = acc.count
    stride = bv.byteStride or 12
    out = []
    for k in range(n):
        out.append(struct.unpack_from("<3f", blob, start + k * stride))
    return out


def main(path, material="M_Dome_Lens"):
    g = GLTF2().load(path)
    blob = g.binary_blob()
    mats = [m.name for m in g.materials]
    found = 0
    for mi, mesh in enumerate(g.meshes):
        for p in mesh.primitives:
            if p.material is None or mats[p.material] != material:
                continue
            pos = _read(g, blob, p.attributes.POSITION)
            nrm = _read(g, blob, p.attributes.NORMAL)
            cx = sum(v[0] for v in pos) / len(pos)
            cy = sum(v[1] for v in pos) / len(pos)
            cz = sum(v[2] for v in pos) / len(pos)
            outward = sum(1 for v, n in zip(pos, nrm)
                          if (v[0] - cx) * n[0] + (v[1] - cy) * n[1] + (v[2] - cz) * n[2] > 0)
            mean_z = sum(n[1] for n in nrm) / len(nrm)      # glTF is Y-up
            print("mesh %d (%s): %d verts, outward %.3f, mean normal y (up) %+.3f"
                  % (mi, mesh.name, len(pos), outward / len(pos), mean_z))
            found += 1
    print("primitives of %s: %d" % (material, found))


if __name__ == "__main__":
    main(*sys.argv[1:])
