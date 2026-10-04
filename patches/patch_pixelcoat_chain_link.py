"""Pixelcoat 0.56.0: chain link. A `diamond_mesh` generator and a
`chain_link` kind, alpha-cut, for Zoo's `chain_link_fence` -- the walker,
2026-10-04, choosing a fenced vacant lot for the far side of the through
road: "empty lot is a good start".

The gap protocol (`USING_THE_FACTORY.md`): a fence needs a see-through wire
fabric, Zoo's painted atlas is RGB with no alpha, and Pixelcoat already
writes cutout packs (road paint, foliage) that Zoo's textured path exports
as alphaMode MASK. So the owning tool grows the surface.

Anchored edits (every anchor once; refuses on a miss): `procedural_surface.py`
(`diamond_mesh`, exported), `material_grammar.py` (dispatch), both level
themes (`chain_link` -> `chain_link_galvanized`). The profile and tests copied
from `pixelcoat_chain_link/`. CHANGELOG and VERSION from
`pixelcoat_chain_link/CHANGELOG_0.56.0.md`.

    python patch_pixelcoat_chain_link.py
"""
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PC = HERE.parent / "pixelcoat"
SRC = HERE / "pixelcoat_chain_link"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


GEN = '''

def diamond_mesh(size, count: int, seed: int = 0, *, wire: float = 0.14,
                 weave: bool = False, label: str = "diamond_mesh") -> np.ndarray:
    """Chain-link fabric in ``[0, 1]``: two crossed families of diagonal
    wires, 1 on a wire and falling to 0 at a diamond's centre (0.56.0).

    ``count`` diamonds across the tile on each axis, so the wires run on the
    diagonals ``u + v`` and ``u - v`` at integer steps -- tileable for an
    integer ``count``. ``wire`` is a wire's width as a fraction of the
    diamond period; the field is 0.5 exactly at its edge, so a cutout at
    threshold 0.5 keeps the wires and nothing else. ``seed`` is unused: woven
    fabric is regular, and its irregularity is the wear's job.

    ``weave`` gives the SHADING instead of the shape: chain link is zig-zag
    strands, each hooked over its neighbour at one bend and under it at the
    next, not two families of straight wires laid across each other. At a
    crossing the family whose index parity says it is on top keeps its
    round highlight and the other darkens where it passes under; off the
    wire the field is 0. Used as an albedo band beside the cutout, at the
    same `count`, so the shading lands on the wires the cutout keeps.
    """
    h, w = _as_hw(size)
    n = max(1, int(count))
    u = ((np.arange(w, dtype=np.float64) + 0.5) / w * n)[None, :]
    v = ((np.arange(h, dtype=np.float64) + 0.5) / h * n)[:, None]
    a = u + v
    b = u - v
    da = np.abs(a - np.round(a))                # distance to the nearest wire, per family
    db = np.abs(b - np.round(b))
    d = np.minimum(da, db)
    half = max(1e-6, float(wire) / 2.0)
    if not weave:
        return np.clip(1.0 - 0.5 * d / half, 0.0, 1.0).astype(np.float32)
    on = d <= half
    # a round wire: brightest along its centre line
    ridge = np.clip(1.0 - d / half, 0.0, 1.0) ** 0.5
    # which family is on top at this crossing: alternate along each strand
    top_a = ((np.round(a) + np.round(b)).astype(np.int64) % 2) == 0
    near = (da <= half) & (db <= half)          # within a crossing
    mine_a = da <= db                           # the pixel belongs to family a
    under = near & (mine_a != top_a)
    shade = 0.45 + 0.55 * ridge
    shade = np.where(under, shade * 0.45, shade)
    return np.where(on, shade, 0.0).astype(np.float32)
'''


def main():
    v = (PC / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Pixelcoat 0.55.0", v
    ps = PC / "pixelcoat" / "core" / "procedural_surface.py"
    _edit(ps, [
        ('    "ribs",\n', '    "ribs",\n    "diamond_mesh",\n'),
        ('def wave(size, count: int, seed: int = 0, *, axis: str = "x", warp: float = 0.15,\n',
         GEN.lstrip("\n") + '\n\ndef wave(size, count: int, seed: int = 0, *, axis: str = "x", warp: float = 0.15,\n'),
    ])
    _edit(PC / "pixelcoat" / "core" / "material_grammar.py", [
        ('    if gen == "wave":\n',
         '    if gen == "diamond_mesh":\n'
         '        return ps.diamond_mesh(size, spec.get("count", 16), seed,\n'
         '                               wire=spec.get("wire", 0.14),\n'
         '                               weave=bool(spec.get("weave", False)), label=label)\n'
         '    if gen == "wave":\n'),
    ])
    for name in ("delco", "delco_1997"):
        p = PC / "profiles" / "themes" / f"{name}.json"
        assert "chain_link" not in json.loads(p.read_text(encoding="utf-8"))["materials"], name
        # inserted as text after `road_paint`, so nothing else in the file
        # is re-serialised
        _edit(p, [('    "road_paint": "road_paint_delco",\n',
                   '    "road_paint": "road_paint_delco",\n'
                   '    "chain_link": "chain_link_galvanized",\n')])
        json.loads(p.read_text(encoding="utf-8"))               # still JSON
    shutil.copyfile(SRC / "chain_link_galvanized.json", PC / "profiles" / "materials" / "chain_link_galvanized.json")
    shutil.copyfile(SRC / "test_chain_link.py", PC / "tests" / "test_chain_link.py")
    ch = PC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    anchor = "## [0.55.0]"
    assert s.count(anchor) == 1
    ch.write_text(s.replace(anchor, (SRC / "CHANGELOG_0.56.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + anchor), encoding="utf-8", newline="\n")
    (PC / "VERSION").write_text("Pixelcoat 0.56.0", encoding="utf-8", newline="\n")
    # the installed copy's fallback (test_version_is_single_sourced holds the two equal)
    _edit(PC / "pixelcoat" / "version.py", [('_FALLBACK = "0.55.0"\n', '_FALLBACK = "0.56.0"\n')])
    print("Pixelcoat 0.56.0 applied")


if __name__ == "__main__":
    main()
