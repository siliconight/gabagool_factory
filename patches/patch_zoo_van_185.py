"""Zoo 1.85.0: the getaway van's hero pass (roadmap 206). The walker,
2026-10-08: "this van is also going to be the foundation of a hero prop that
get's reused in multiple missions, so we can afford to really make it look
good". Tyres with a sidewall, a shoulder and a grooved tread at 28 segments,
steel wheels with hubs, lug nuts and caps, wipers hung from the header, West
Coast mirrors with glass, the crew's step, side markers, drip rails, the
tail's lamps, hinges and corner caps, a bumper step and mud flaps -- one van
a level, still five submissions.

Whole files from `zoo_van_185/`, each replacing the 1.84.0 file whose sha256
it asserts first: `core/van_forms.py`, `recipes/step_van.py`,
`genome/species/step_van.json`, `tests/test_step_van.py`. One anchored edit
(refuses on a miss): `tests/test_coincident_faces.py`, the census note.
CHANGELOG and VERSION from `zoo_van_185/CHANGELOG_1.85.0.md`.

    python patch_zoo_van_185.py
    ZOO_ROOT=<copy> python patch_zoo_van_185.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_van_185"

#: the 1.84.0 files (9cb7249) these replace, by sha256
WHOLE = {
    "zoo_keeper/core/van_forms.py": ("van_forms.py",
        "78a0b9d0bbab33a488ac30897cf0b8f8a02fb5a8cc7e8193dfa11679357aba4e"),
    "zoo_keeper/recipes/step_van.py": ("step_van.py",
        "467b120cd126b48d2b66b76d82a4ccb8280faa87d0cf3493c27f959bc5636dc7"),
    "zoo_keeper/genome/species/step_van.json": ("step_van.json",
        "a21b994c09a1c3d4d11e28cb44d570d8abfd9b06171cb55a6c069d7d1bda9661"),
    "tests/test_step_van.py": ("test_step_van.py",
        "374ed8cf115f472c61763aee1ddac78d950722b8c49704843b532e3f295a1dfb"),
}


def _edit(path, old, new):
    d = path.read_bytes()
    crlf = b"\r\n" in d
    s = d.decode("utf-8").replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, s.count(old), old[:60])
    s = s.replace(old, new)
    path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.84.0", v
    for rel, (_name, sha) in WHOLE.items():
        got = hashlib.sha256((ZOO / rel).read_bytes()).hexdigest()
        assert got == sha, (rel, "is not the 1.84.0 file", got)
    _edit(ZOO / "tests" / "test_coincident_faces.py",
          "#: own test sweeps its chassis at every centimetre of height.\n"
          "CENSUS_BUILDS = 363\n",
          "#: own test sweeps its chassis at every centimetre of height.\n"
          "#: 1.85.0: `step_van`'s hero pass -- tyres, steel wheels, wipers, mirrors,\n"
          "#: markers, caps, hinges, flaps -- the same three builds, same tool,\n"
          "#: Blender 5.1.1: \"3 builds, 0 with coincident pairs, 0 that did not\n"
          "#: build\" (13,572 / 13,792 / 14,012 tris), first build.\n"
          "CENSUS_BUILDS = 363\n")
    for rel, (name, _sha) in WHOLE.items():
        (ZOO / rel).write_bytes((SRC / name).read_bytes())
    entry = (SRC / "CHANGELOG_1.85.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.85.0]" not in d and d.startswith(b"## [1.84.0]")
    crlf = b"\r\n" in d
    cl.write_bytes((entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d)
    (ZOO / "VERSION").write_bytes(b"1.85.0")
    print("1.84.0 -> 1.85.0")


if __name__ == "__main__":
    main()
