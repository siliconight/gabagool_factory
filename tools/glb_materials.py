"""Name the material on every mesh in a .glb, and say which ones have no texture.

WHAT THIS IS FOR. A mesh with no base-colour texture renders as flat white, and
that is indistinguishable at a glance from "a white panel is in the level".
This pipeline has now guessed at one such surface three times -- broken glass, a
degenerate plane, a stray sign -- and been wrong three times, because every
instrument it had reads GEOMETRY. `glb_nodes.py` answers "what shapes are in
here", `glb_uv_census.py` answers "can a texture be mapped onto them", and
nothing answered "is one actually assigned".

    python tools\\glb_materials.py <file-or-dir> [...] [--untextured-only]

WHAT IT MEASURES. The glTF JSON chunk only; no accessor data is decoded and no
image is opened. Per PRIMITIVE, because a primitive is what carries a material
reference and what Godot turns into one surface:

  material        the material's name, or <none> when the primitive has no
                  material index at all -- which is itself a defect: Godot
                  substitutes a default white.
  baseColorTex    whether pbrMetallicRoughness.baseColorTexture is present.
  baseColorFactor the flat RGBA multiplier. A primitive with no texture and a
                  factor of 1,1,1,1 is EXACTLY the white-panel case; the same
                  primitive with a dark factor is a deliberate flat material.

WHY BOTH COLUMNS. "No texture" alone is not a defect -- a flat-shaded trim
piece is legitimate. "No texture AND a white factor" is the thing that looks
like a bug in a screenshot, so it is reported as its own verdict rather than
left to the reader to combine.

WHAT A NONZERO EXIT MEANS. The file could not be read or is not a glTF binary.
An empty mesh list is reported as such, never as "nothing wrong".
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

_MAGIC = 0x46546C67          # 'glTF'
_CHUNK_JSON = 0x4E4F534A     # 'JSON'


def read_gltf_json(path: Path) -> dict:
    """The JSON chunk of a binary glTF, parsed. Raises ValueError if it is not
    one -- a .gltf text file is a different format and is not silently accepted,
    because accepting it would make an empty result look like a clean one."""
    raw = path.read_bytes()
    if len(raw) < 12:
        raise ValueError(f"{path.name}: too short to be a GLB")
    magic, version, total = struct.unpack_from("<III", raw, 0)
    if magic != _MAGIC:
        raise ValueError(f"{path.name}: not a binary glTF (bad magic)")
    if version != 2:
        raise ValueError(f"{path.name}: glTF version {version}, expected 2")
    off = 12
    while off + 8 <= len(raw):
        length, kind = struct.unpack_from("<II", raw, off)
        body = raw[off + 8: off + 8 + length]
        if kind == _CHUNK_JSON:
            return json.loads(body.decode("utf-8"))
        off += 8 + length + ((4 - length % 4) % 4 if length % 4 else 0)
    raise ValueError(f"{path.name}: no JSON chunk")


def _mesh_users(doc: dict) -> dict[int, list[str]]:
    """mesh index -> the node names that instance it, so output names the thing
    a human saw rather than an index."""
    users: dict[int, list[str]] = {}
    for node in doc.get("nodes", []):
        if "mesh" in node:
            users.setdefault(node["mesh"], []).append(node.get("name", "?"))
    return users


def rows(doc: dict) -> list[dict]:
    mats = doc.get("materials", [])
    users = _mesh_users(doc)
    out = []
    for mi, mesh in enumerate(doc.get("meshes", [])):
        owner = ", ".join(users.get(mi, [])) or mesh.get("name", f"mesh[{mi}]")
        for pi, prim in enumerate(mesh.get("primitives", [])):
            idx = prim.get("material")
            mat = mats[idx] if isinstance(idx, int) and idx < len(mats) else None
            pbr = (mat or {}).get("pbrMetallicRoughness", {})
            factor = pbr.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0])
            has_tex = "baseColorTexture" in pbr
            white = (not has_tex
                     and all(c >= 0.99 for c in factor[:3]))
            out.append({
                "node": owner,
                "primitive": pi,
                "material": (mat or {}).get("name", "<none>") if mat else "<none>",
                "has_base_color_texture": has_tex,
                "base_color_factor": [round(float(c), 3) for c in factor],
                "renders_flat_white": white,
            })
    return out


def _report(path: Path, data: list[dict], untextured_only: bool) -> int:
    shown = [r for r in data
             if not untextured_only or not r["has_base_color_texture"]]
    print(f"\n{path.name}: {len(data)} primitive(s)"
          + (f", {len(shown)} without a base-colour texture" if untextured_only
             else ""))
    if not data:
        print("  NO MESHES IN THIS FILE -- not the same as nothing wrong.")
        return 0
    if not shown:
        print("  every primitive carries a base-colour texture.")
        return 0
    print(f"  {'node':34s} {'material':26s} {'tex':4s} {'baseColorFactor'}")
    for r in shown:
        flag = " <- FLAT WHITE" if r["renders_flat_white"] else ""
        print(f"  {r['node'][:34]:34s} {r['material'][:26]:26s} "
              f"{'yes' if r['has_base_color_texture'] else 'NO':4s} "
              f"{r['base_color_factor']}{flag}")
    return sum(1 for r in shown if r["renders_flat_white"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("targets", nargs="+", help="a .glb file or a directory")
    ap.add_argument("--untextured-only", action="store_true",
                    help="list only primitives with no base-colour texture")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    files: list[Path] = []
    for t in a.targets:
        p = Path(t)
        files.extend(sorted(p.rglob("*.glb")) if p.is_dir() else [p])
    if not files:
        print("no .glb files in the given targets", file=sys.stderr)
        return 2

    blob, white_total, failed = {}, 0, 0
    for f in files:
        try:
            data = rows(read_gltf_json(f))
        except (OSError, ValueError, json.JSONDecodeError) as e:
            print(f"{f.name}: UNREADABLE -- {e}", file=sys.stderr)
            failed += 1
            continue
        blob[str(f)] = data
        if not a.json:
            white_total += _report(f, data, a.untextured_only)

    if a.json:
        print(json.dumps(blob, indent=2, sort_keys=True))
    else:
        print(f"\n{len(files) - failed} file(s) read, {failed} unreadable; "
              f"{white_total} primitive(s) render FLAT WHITE "
              f"(no texture, base colour 1,1,1).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
