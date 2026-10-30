"""Pixelcoat 0.65.0: a crown card's cutout is leaves, not discs.

`material_grammar.leaf_scatter` cuts the foliage pack's alpha from small rotated leaves in seeded sprays inside the
card's ellipse, each shading the albedo a little differently; `foliage_delco` asks for it with `cutout.leaves`.

Proven: tests/test_leaf_scatter.py fails on 0.64.0 (fails_on_old.out.txt); the clone's suite, 682 passed, 1 skipped
(suite_clone.out.txt), the Controlled Contrast baseline held; the slice rebuilt and priced (the factory's
docs/findings/slice_look/, slice 13b).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'pixelcoat'
PINS = {'CHANGELOG.md': '9f57fc271b89e7c9', 'VERSION': '1d2ae80d79699ddb', 'pixelcoat/core/material_grammar.py': '9c07c96412034b90', 'pixelcoat/version.py': '11aecf38bc3f5b02', 'profiles/materials/foliage_delco.json': '4fa5f10a8af176af'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.65.0] - a crown card\'s cutout is leaves, not discs\n\nThe factory\'s roadmap 324; the walker, 2026-10-30, of the vertical slice: "try the card-based trees". The foliage pack\na tree\'s crown cards wear cut its alpha from a Worley field at 7 cells a tile -- a dozen plate-sized discs on a 4 m\ncard -- so a card crown read as green circles, the reason Zoo\'s card crown was judged not ready on cold run 9032.\n`material_grammar.leaf_scatter` cuts it instead from leaves: `sprays` seeded spray centres inside the card\'s ellipse,\n`per` leaves round each at a radius drawn from the spray\'s own, each a rotated ellipse `length` px long and `width` of\nthat wide pointing out from its spray with a seeded wobble, wrapped at the tile\'s edges; each leaf multiplies the\nalbedo by its own shade in [1 - `shade`, 1 + `shade`], so neighbouring leaves differ. A grammar asks for it with\n`cutout.leaves`; `foliage_delco` does (16 sprays, 260 leaves each, 13 px, at 512 px, shade 0.10 -- the slice was\njudged at 0.20, and halving it keeps the pack inside the Controlled Contrast baseline, `tests/test_art_standard.py`,\nwhich 0.20 broke: value range 0.196 -> 0.247). Zoo (>= 1.151.0) frames one\ntile a card. On the slice (the factory\'s `docs/findings/slice_look/`, slice 13b) the street trees read as trees.\nTests: tests/test_leaf_scatter.py.\n\n')], 'VERSION': [('lines 1-1', 'Pixelcoat 0.64.0', 'Pixelcoat 0.65.0')], 'pixelcoat/core/material_grammar.py': [('lines 371-372', '\ndef synthesize(grammar: MaterialGrammar, size=512, seed: int = DEFAULT_SEED) -> dict:\n', '\n\ndef leaf_scatter(shape, spec: dict, seed: int, ellipse=None):\n    """``(keep, shade)`` for a crown card\'s cutout made of LEAVES (0.65.0, the factory\'s roadmap 324).\n\n    The walker, 2026-10-30, of the vertical slice\'s street trees: "try the card-based trees". The foliage pack\'s\n    cutout was a Worley field at 7 cells a tile -- a dozen discs the size of a dinner plate on a 4 m card -- so a\n    card crown read as green circles, the reason it was judged not ready on cold run 9032. A real crown seen from the\n    street is many small leaves, gathered in sprays along the twigs, with sky between the sprays.\n\n    So: `sprays` spray centres, seeded, inside the card\'s ellipse (the same ellipse the Worley cutout is clipped to,\n    centred on the tile\'s corner and wrapped, so a card\'s UVs running -0.5 to 0.5 tiles frame it); round each, `per`\n    leaves at a radius drawn from the spray\'s own, each a rotated ellipse `length` px long and `width` of that wide,\n    pointing out from the spray\'s centre with a seeded wobble. ``keep`` is the union of the leaves; ``shade`` a\n    per-leaf brightness in [1 - `shade`, 1 + `shade`] that multiplies the albedo, so neighbouring leaves differ and\n    the crown has a texture, not just a silhouette. Leaves wrap at the tile\'s edges. Deterministic for a seed."""\n    h, w = shape\n    rng = np.random.default_rng(seed)\n    sprays = int(spec.get("sprays", 14))\n    per = int(spec.get("per", 110))\n    length = float(spec.get("length", 12.0))\n    width = float(spec.get("width", 0.42)) * length\n    spread = float(spec.get("spread", 0.11)) * min(h, w)\n    vary = float(spec.get("shade", 0.18))\n    rx = float((ellipse or {}).get("rx", 0.46)) * w\n    ry = float((ellipse or {}).get("ry", 0.46)) * h\n    keep = np.zeros((h, w), dtype=bool)\n    shade = np.ones((h, w), dtype=np.float32)\n    r = int(np.ceil(length / 2.0)) + 1\n    oy, ox = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32)\n    for _s in range(sprays):\n        # a spray\'s centre inside the ellipse about the tile\'s corner, (0, 0) wrapped\n        while True:\n            u, v = rng.uniform(-1.0, 1.0, 2)\n            if u * u + v * v <= 0.72:\n                break\n        cy, cx = v * (ry - spread), u * (rx - spread)\n        for _l in range(per):\n            ang = rng.uniform(0.0, 2.0 * np.pi)\n            dist = abs(rng.normal(0.0, spread * 0.55))\n            py, px = cy + np.sin(ang) * dist, cx + np.cos(ang) * dist\n            if (px / rx) ** 2 + (py / ry) ** 2 > 1.0:\n                continue\n            theta = ang + rng.normal(0.0, 0.6)\n            ct, st = np.cos(theta), np.sin(theta)\n            a = (ox * ct + oy * st) / (length / 2.0)\n            b = (-ox * st + oy * ct) / (width / 2.0)\n            leaf = a * a + b * b <= 1.0\n            yy = (np.round(py).astype(int) + oy.astype(int)) % h\n            xx = (np.round(px).astype(int) + ox.astype(int)) % w\n            k = 1.0 + rng.uniform(-vary, vary)\n            keep[yy[leaf], xx[leaf]] = True\n            shade[yy[leaf], xx[leaf]] = k\n    return keep, shade\n\n\ndef synthesize(grammar: MaterialGrammar, size=512, seed: int = DEFAULT_SEED) -> dict:\n'), ('lines 646-646', '    if grammar.cutout:\n', '    if grammar.cutout and grammar.cutout.get("leaves"):\n        # LEAVES, NOT BLOBS (0.65.0): see `leaf_scatter`\n        co = grammar.cutout\n        keep, shade = leaf_scatter((h, w), co["leaves"], ps.stream_seed(seed, "leaves"),\n                                   co.get("ellipse"))\n        albedo = np.clip(albedo * shade[..., None], 0.0, 1.0)\n        if grammar.posterize:\n            albedo = ps.posterize(albedo, grammar.posterize)\n        out["albedo"] = _to_u8(np.concatenate([albedo, keep.astype(np.float32)[..., None]], axis=-1))\n    elif grammar.cutout:\n')], 'pixelcoat/version.py': [('lines 33-33', '_FALLBACK = "0.64.0"\n', '_FALLBACK = "0.65.0"\n')], 'profiles/materials/foliage_delco.json': [('lines 54-55', '      "ry": 0.44\n    }\n', '      "ry": 0.44\n    },\n    "leaves": {\n      "sprays": 16,\n      "per": 260,\n      "length": 13.0,\n      "width": 0.42,\n      "spread": 0.12,\n      "shade": 0.1\n    }\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_leaf_scatter.py': '"""A crown card\'s cutout made of leaves, not discs (0.65.0, the factory\'s roadmap 324).\n\nThe walker, 2026-10-30, of the vertical slice\'s street trees: "try the card-based trees". The foliage pack\'s cutout was\na Worley field at 7 cells a tile -- a dozen plate-sized discs on a 4 m card -- so a card crown read as green circles.\n`cutout.leaves` scatters small leaves in sprays inside the card\'s ellipse.\n"""\nimport json\nimport pathlib\n\nimport numpy as np\n\nfrom pixelcoat.core import material_grammar as G\n\nROOT = pathlib.Path(__file__).resolve().parents[1]\n\n\ndef _keep(seed=7):\n    return G.leaf_scatter((256, 256), {"sprays": 10, "per": 120, "length": 7.0}, seed, {"rx": 0.46, "ry": 0.44})\n\n\ndef test_the_foliage_profile_asks_for_leaves():\n    """FAILS ON 0.64.0: the profile\'s cutout was the Worley discs."""\n    d = json.loads((ROOT / "profiles" / "materials" / "foliage_delco.json").read_text(encoding="utf-8"))\n    assert d["cutout"].get("leaves"), d["cutout"]\n    assert d["transparency"]["alpha_mode"] == "scissor"\n\n\ndef _pieces(keep):\n    """Connected pieces of a mask, 4-neighbour, wrapped as the tile is -- a flood fill, no SciPy."""\n    h, w = keep.shape\n    seen = np.zeros_like(keep)\n    n = 0\n    for y, x in zip(*np.nonzero(keep)):\n        if seen[y, x]:\n            continue\n        n += 1\n        stack = [(y, x)]\n        seen[y, x] = True\n        while stack:\n            cy, cx = stack.pop()\n            for ny, nx in (((cy + 1) % h, cx), ((cy - 1) % h, cx), (cy, (cx + 1) % w), (cy, (cx - 1) % w)):\n                if keep[ny, nx] and not seen[ny, nx]:\n                    seen[ny, nx] = True\n                    stack.append((ny, nx))\n    return n\n\n\ndef test_many_small_leaves_not_a_few_discs():\n    """Connected pieces of the cutout: a leaf scatter\'s sprays break into many; seven Worley cells make about a\n    dozen."""\n    keep, _shade = _keep()\n    n = _pieces(keep)\n    assert n >= 30, n\n    assert 0.05 < keep.mean() < 0.6, keep.mean()\n\n\ndef test_the_leaves_stay_inside_the_cards_ellipse_and_differ_in_shade():\n    keep, shade = _keep()\n    h, w = keep.shape\n    fy, fx = np.meshgrid((np.arange(h) + 0.5) / h, (np.arange(w) + 0.5) / w, indexing="ij")\n    dx, dy = np.minimum(fx, 1.0 - fx), np.minimum(fy, 1.0 - fy)\n    outside = (dx / 0.46) ** 2 + (dy / 0.44) ** 2 > 1.35       # a leaf may reach a little past its centre\'s ellipse\n    assert not keep[outside].any()\n    assert len(np.unique(np.round(shade[keep], 3))) > 20\n\n\ndef test_deterministic_for_a_seed():\n    a, sa = _keep(3)\n    b, sb = _keep(3)\n    c, _sc = _keep(4)\n    assert (a == b).all() and (sa == sb).all() and not (a == c).all()\n'}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
