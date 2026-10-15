"""Level Factory 0.212.0: the light bake counts, and gives a second UV set to, only what it bakes (the factory's
roadmap 251, found writing cold run 9308's notes).

The export's log summed `add_primitive_uv2`'s counts over every scene of the package as "lightmapped": 9308's 225
was the presentation's 112, the content scene's same 112 again, and the backdrop's ground, which no bake draws.

  packages/exporting/light_bake.py                 `add_primitive_uv2(..., only=)`; `baked_scenes`; the export
                                                   passes `only=baked_scenes(export_dir)`
  tests/unit/test_bake_counts_what_it_bakes.py     new, from `lf_bake_counts/test_bake_counts_what_it_bakes.py.txt`

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and VERSION
from `lf_bake_counts/CHANGELOG_0.212.0.md`; `--results-pending` leaves RESULT_SUITE to `--fill`.

Read before it was written, in this session: `light_bake.py` lines 1-80 (the module docstring, imports,
`PRESENTATION`, `BAKE_SCENE`), 222-244 (`add_primitive_uv2`), 530-552 (the bake's opening, where the counts are
taken) and 600-629 (the log line and the failure path, which restores the presentation from bytes kept before any
UV2 is written); `tests/unit/test_light_bake.py`'s test of `add_primitive_uv2`, which calls it with no presentation
and expects every scene written -- the reason `only=None` keeps the old behaviour. `grep add_uv2` over Level
Factory, Lot, Lux and the factory's tools: only `light_bake.py` writes or reads it. Every file LF.

    python patches/patch_lf_bake_counts_what_it_bakes.py --results-pending
    (the suite in level_factory; COMMANDS.md trap 1: tally the progress characters)
    python patches/patch_lf_bake_counts_what_it_bakes.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_counts"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.211.1", b"0.212.0"
CHANGELOG_HEAD = "## [0.211.1] - the certified table re-grounded for factory 1.40.0"
SHA = {"packages/exporting/light_bake.py": "dfda58dfd8ad0728"}
NEW = {"tests/unit/test_bake_counts_what_it_bakes.py": "test_bake_counts_what_it_bakes.py.txt"}

OLD_DEF = (
    'def add_primitive_uv2(export_dir: Path) -> dict:\n'
    '    """`add_uv2 = true` on every inline primitive mesh in the package\'s\n'
    '    scenes. ``{scene: count}``."""\n'
    '    out = {}\n'
    '    pat = re.compile(r\'^\\[sub_resource type="(?:%s)" id="[^"]*"\\]$\' % "|".join(PRIMITIVES), re.M)\n'
    '    for scene in sorted(Path(export_dir).rglob("*.tscn")):\n'
    '        if ".godot" in scene.parts or scene.name == BAKE_SCENE:\n'
    '            continue\n')
NEW_DEF = (
    'def add_primitive_uv2(export_dir: Path, only=None) -> dict:\n'
    '    """`add_uv2 = true` on every inline primitive mesh in the package\'s\n'
    '    scenes. ``{scene: count}``.\n'
    '\n'
    '    ONLY WHAT THE BAKE DRAWS (0.212.0, the factory\'s roadmap 251). The\n'
    '    export passes `only=baked_scenes(export_dir)`. This wrote every scene,\n'
    '    and the log summed every count as "lightmapped": cold run 9308\'s 225 was\n'
    '    the presentation\'s 112, the content scene\'s same 112 again, and the\n'
    '    backdrop\'s ground, which no bake draws. `only=None` is every scene, as\n'
    '    before."""\n'
    '    out = {}\n'
    '    keep = None if only is None else set(only)\n'
    '    pat = re.compile(r\'^\\[sub_resource type="(?:%s)" id="[^"]*"\\]$\' % "|".join(PRIMITIVES), re.M)\n'
    '    for scene in sorted(Path(export_dir).rglob("*.tscn")):\n'
    '        if ".godot" in scene.parts or scene.name == BAKE_SCENE:\n'
    '            continue\n'
    '        if keep is not None and scene.relative_to(export_dir).as_posix() not in keep:\n'
    '            continue\n')

OLD_NEXT = 'def _cycling_rigs(blocks: list) -> set:\n'
NEW_NEXT = (
    '_PACKED = re.compile(r\'^\\[ext_resource type="PackedScene"[^\\]\\n]*\\bpath="res://([^"]+\\.tscn)"\', re.M)\n'
    '\n'
    '\n'
    'def baked_scenes(export_dir: Path) -> list:\n'
    '    """The scenes the bake draws, package-relative and sorted: the\n'
    '    presentation scene `bake.tscn` instances (`bake_scene_text`) and every\n'
    '    scene it instances, transitively. The content scene `site.tscn`, which\n'
    '    the presentation was applied from, and `site_backdrop.tscn`, which\n'
    '    `mission.tscn` loads at run time, are not among them (0.212.0)."""\n'
    '    export_dir = Path(export_dir)\n'
    '    seen, todo = set(), [PRESENTATION]\n'
    '    while todo:\n'
    '        rel = todo.pop()\n'
    '        p = export_dir / rel\n'
    '        if rel in seen or not p.is_file():\n'
    '            continue\n'
    '        seen.add(rel)\n'
    '        todo.extend(_PACKED.findall(p.read_text(encoding="utf-8")))\n'
    '    return sorted(seen)\n'
    '\n'
    '\n' + OLD_NEXT)

OLD_CALL = '        report["primitives"] = add_primitive_uv2(export_dir)\n'
NEW_CALL = '        report["primitives"] = add_primitive_uv2(export_dir, only=baked_scenes(export_dir))\n'

EDITS = {"packages/exporting/light_bake.py": [(OLD_DEF, NEW_DEF), (OLD_NEXT, NEW_NEXT), (OLD_CALL, NEW_CALL)]}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.212.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.212.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.212.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.212.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        p = LF / rel
        assert not p.exists(), (rel, "already exists")
        writes[p] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Level Factory 0.211.1 -> 0.212.0")


if __name__ == "__main__":
    main()
