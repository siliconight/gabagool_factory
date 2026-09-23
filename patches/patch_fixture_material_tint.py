"""Let the GLB import fixture express a material's TINT.

`zoo_worldskin._skin_ladders` picks a ladder's rail and rung by ranking the
metals a building owns by luminance, read off `albedo_color`. The fixture
hardcodes `baseColorFactor: [0.8, 0.8, 0.8, 1.0]` on every material, so every
metal in a fixture package has identical luminance and the pass would report
"only 1 tinted metal" -- the test could not tell a working pick from a broken
one.

Backwards compatible on purpose: a two-element `(name, textured)` entry keeps
the flat 0.8 grey, so every existing fixture in
`test_worldskin_stairs.py` / `test_worldskin_slabs.py` is untouched.

HOLD UNTIL THE COLD RUN ENDS.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "tests" / "unit" / "glb_import_fixture.py"

A1 = "    textured = any(t for _, t in materials)\n"
N1 = "    textured = any(m[1] for m in materials)\n"

A2 = """    mats: list = []
    for name, has_tex in materials:
        pbr: dict = {"baseColorFactor": [0.8, 0.8, 0.8, 1.0]}
        if has_tex:
            pbr["baseColorTexture"] = {"index": 0}
        mats.append({"name": name, "pbrMetallicRoughness": pbr})
"""

N2 = '''    mats: list = []
    for entry in materials:
        # A material is `(name, textured)` or `(name, textured, [r, g, b])`.
        # The third element is its `baseColorFactor` -- where Pixelcoat puts a
        # skin's tint, and what `zoo_worldskin._metal_palette` ranks a
        # ladder's rail and rung by. Two-element entries keep the flat 0.8
        # grey so every fixture written before this is unchanged.
        name, has_tex = entry[0], entry[1]
        rgb = list(entry[2]) if len(entry) > 2 else [0.8, 0.8, 0.8]
        pbr: dict = {"baseColorFactor": rgb + [1.0]}
        if has_tex:
            pbr["baseColorTexture"] = {"index": 0}
        mats.append({"name": name, "pbrMetallicRoughness": pbr})
'''

A3 = """    ``materials`` is ``[(material_name, textured)]``; a textured material gets
"""
N3 = """    ``materials`` is ``[(material_name, textured)]`` or
    ``[(material_name, textured, [r, g, b])]``; a textured material gets
"""

EDITS = ((A1, N1), (A2, N2), (A3, N3))


def _eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    bare = data.count(b"\n") - crlf
    if crlf and bare:
        raise SystemExit(f"REFUSED: mixed endings, {crlf} CRLF and {bare} LF")
    return "\r\n" if crlf else "\n"


def main() -> None:
    data = TARGET.read_bytes()
    eol = _eol(data)
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        o, n = old.replace("\n", eol), new.replace("\n", eol)
        hits = text.count(o)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(o, n)
    out = text.encode("utf-8")
    if _eol(out) != eol:
        raise SystemExit("REFUSED: would change the file's line endings")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes "
          f"(+{len(out) - before})")


if __name__ == "__main__":
    main()
