"""Zoo 1.58.0: the dumpster. The walker, 2026-10-03, with two photographs:
"we should have some trash dumpsters next to buildings (sides or back where
its not in the way of where customers would naturally walk into the
building)". A new species, `dumpster`: a front-load container in one
painted atlas and one draw, four invented Delco haulers.

New files copied from `zoo_dumpster/`: `core/dumpster_forms.py`,
`recipes/dumpster.py`, `genome/species/dumpster.json`,
`tests/test_dumpster.py`. Anchored edits (every anchor once; refuses on a
miss): `core/card_art.py` (the painter's dispatch), `tests/test_genome.py`
(the hand-authored species set), `tests/test_material_options_closed.py`
(painted steel). CHANGELOG and VERSION from `zoo_dumpster/CHANGELOG_1.58.0.md`.

    python patch_zoo_dumpster.py
    ZOO_ROOT=<copy> python patch_zoo_dumpster.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_dumpster"


def _edit(path, old, new):
    d = path.read_bytes()
    crlf = b"\r\n" in d
    s = d.decode("utf-8").replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, old[:60])
    s = s.replace(old, new)
    path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.57.1", v
    zk = ZOO / "zoo_keeper"
    assert not (zk / "core" / "dumpster_forms.py").exists(), "already applied"
    for name, dst in (("dumpster_forms.py", zk / "core" / "dumpster_forms.py"),
                      ("dumpster.py", zk / "recipes" / "dumpster.py"),
                      ("dumpster.json", zk / "genome" / "species" / "dumpster.json"),
                      ("test_dumpster.py", ZOO / "tests" / "test_dumpster.py")):
        dst.write_bytes((SRC / name).read_bytes())
    _edit(zk / "core" / "card_art.py",
          '    # THE PUMP (1.36.0): its panels, price wheels and header are\n',
          '    # THE DUMPSTER (1.58.0): its plate, sticker, lids and trim are\n'
          '    # `dumpster_forms`\' tiles\n'
          '    if kind.startswith("dumpster_"):\n'
          '        from . import dumpster_forms as DF\n'
          '        return DF.paint(spec)\n'
          '    # THE PUMP (1.36.0): its panels, price wheels and header are\n')
    _edit(ZOO / "tests" / "test_genome.py",
          '                "price_pylon"}\n',
          '                "price_pylon",\n'
          '                # the front-load dumpster (1.58.0)\n'
          '                "dumpster"}\n')
    _edit(ZOO / "tests" / "test_material_options_closed.py",
          '           "cash_register")\n',
          '           "cash_register",\n'
          '           # a dumpster is painted plate, its fleet colour in the\n'
          '           # painted atlas; its lids are plastic in the same image\n'
          '           # (1.58.0)\n'
          '           "dumpster")\n')
    # the two audits that count species by a literal on purpose
    _edit(ZOO / "tests" / "test_coincident_faces.py",
          'CENSUS_BUILDS = 351\n',
          '#: 1.58.0: `dumpster`, three builds more, same tool, Blender 5.1.1: "3\n'
          '#: builds, 0 with coincident pairs, 0 that did not build", 92 tris at\n'
          '#: each corner. Its test runs `coincident_pairs` over 27 sizes x 4\n'
          '#: haulers.\n'
          'CENSUS_BUILDS = 354\n')
    _edit(ZOO / "tests" / "test_theme_style_resolution.py",
          '    assert len(_genomes()) == 91 + len(_minted), len(_genomes())\n',
          '    # 1.58.0: 92, + dumpster, with its own `delco` row.\n'
          '    assert len(_genomes()) == 92 + len(_minted), len(_genomes())\n')
    entry = (SRC / "CHANGELOG_1.58.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.58.0]" not in d and d.startswith(b"## [1.57.1]")
    crlf = b"\r\n" in d
    cl.write_bytes((entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d)
    (ZOO / "VERSION").write_bytes(b"1.58.0")
    print("1.57.1 -> 1.58.0")


if __name__ == "__main__":
    main()
