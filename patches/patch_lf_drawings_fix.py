"""Level Factory 0.232.1 (the factory's roadmap 296): the Empties named, and the shell's drawings left out where
the shell is.

Read off cold run 9377's package: `empty_rows` reports each Empty's spec as `index` does, so an Empty's package
records why it has no drawing; and the composed root's `drawings/` -- the mission shell's, which a varied lot does not
stand -- stays out with the root's scene pair (`_root_left_out`).

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `packages/pipeline/building_library.py`, `packages/exporting/export.py` and
`tests/unit/test_compose_draws_its_buildings.py` (anchored hunks); VERSION; the CHANGELOG entry, prepended. Generated
from a proven clone (`patches/lf_drawings_fix/gen_lf_drawings_fix.py`), dry-run on a fresh clone to the clone's every
byte, a second run refused (`patches/lf_drawings_fix/dry_run_*.out.txt`).

    python patches/patch_lf_drawings_fix.py
    cd level_factory && python -m pytest -q
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'packages/pipeline/building_library.py': '8cf7fca9f9f4ce94', 'packages/exporting/export.py': 'fd82db8d5d4ebf5a', 'tests/unit/test_compose_draws_its_buildings.py': '4e97db9d9d8d45a4'}
EDITS = {'packages/pipeline/building_library.py': [('lines 940-940', '    id: ``{"id", "family", "glb", "gameplay", "slots"}``, ``family`` as\n', '    id: ``{"id", "family", "glb", "gameplay", "slots", "spec"}``, ``family`` as\n'), ('lines 948-949', '        aid = glb.stem\n        row = {"id": aid, "family": family, "glb": str(glb),\n', '        aid = glb.stem\n        spec = d.parent / "specs" / (aid + ".json")\n        row = {"id": aid, "family": family, "glb": str(glb),\n'), ('lines 951-951', '               "slots": str(d / f"{aid}.slots.json")}\n', '               "slots": str(d / f"{aid}.slots.json"),\n               # THE SPEC IT WAS BUILT FROM, as `index` reports it (0.232.1, the\n               # factory\'s roadmap 296): an Empty\'s rows come from here, not from\n               # `index`, so cold run 9377 composed all 26 with no spec and their\n               # packages carried no record of why they have no drawing.\n               "spec": str(spec) if spec.is_file() else ""}\n')], 'packages/exporting/export.py': [('lines 481-482', '_COMPOSED_ROOT_PAIR = frozenset({"site.tscn", "site_base.glb"})\n\n', '_COMPOSED_ROOT_PAIR = frozenset({"site.tscn", "site_base.glb"})\n\n#: THE COMPOSER\'S ROOT DRAWINGS (0.232.1, the factory\'s roadmap 296): Deli\n#: Counter 0.257.0 draws the composed root\'s building -- the mission\'s own\n#: shell -- into `drawings/` beside it. Where the root pair stays out (a varied\n#: lot, whose assembly stands the lot and not the shell), those drawings are of\n#: a building nothing stands, and they stay out with it. Cold run 9377\'s package\n#: carried the shell\'s nine files at its root beside an index of three buildings.\n_COMPOSED_ROOT_DRAWINGS = "drawings"\n\n\ndef _root_left_out(composed_root, keep_root) -> set:\n    """The composed root\'s own files a package leaves out (`_copy_tree`\'s\n    `skip_rel`): none where its scene ships (`keep_root`), else the root pair\n    and every file of the root\'s `drawings/` -- never a building\'s under\n    `lot/<id>/`."""\n    if keep_root:\n        return set()\n    d = Path(composed_root) / _COMPOSED_ROOT_DRAWINGS\n    drawn = ({p.relative_to(composed_root).as_posix() for p in d.rglob("*") if p.is_file()}\n             if d.is_dir() else set())\n    return set(_COMPOSED_ROOT_PAIR) | drawn\n\n'), ('lines 2172-2173', '                   skip_rel=(set() if (wanted or building_rel)\n                             else set(_COMPOSED_ROOT_PAIR)),\n', '                   skip_rel=_root_left_out(composed_root, wanted or building_rel),\n')], 'tests/unit/test_compose_draws_its_buildings.py': [('lines 98-98', '    assert d._drawing_kwargs(new, "") == ({}, "")\n', '    assert d._drawing_kwargs(new, "") == ({}, "")\n\n\ndef test_an_empty_row_names_its_spec_too(tmp_path):\n    """0.232.1: an Empty\'s row comes from `empty_rows`, not `index`, and cold run 9377 composed all 26 of its Empties\n    with no spec. A row names its spec where Deli Counter has one, and an empty string where it has none."""\n    build = tmp_path / "build"\n    build.mkdir()\n    for aid in ("gs_empty_rowhome_a", "gs_empty_rowhome_b"):\n        for suf in (".glb", ".gameplay.json", ".slots.json"):\n            (build / (aid + suf)).write_text("{}", encoding="utf-8")\n        (build / (aid + ".validation.json")).write_text(json.dumps({"facade": True}), encoding="utf-8")\n    _with_specs(build, ["gs_empty_rowhome_a"])\n    rows = {r["id"]: r for r in bl.empty_rows(build)}\n    assert rows["gs_empty_rowhome_a"]["spec"] == str(tmp_path / "specs" / "gs_empty_rowhome_a.json")\n    assert rows["gs_empty_rowhome_b"]["spec"] == ""\n\n\ndef test_the_composed_roots_drawings_stay_out_with_its_scene(tmp_path):\n    """0.232.1: cold run 9377\'s package carried the mission shell\'s drawings at its root, a building its varied lot\n    does not stand. Where the root\'s scene pair stays out, its `drawings/` does too; a lot building\'s drawings, and\n    every root file where the root ships, are left alone."""\n    from packages.exporting import export as ex\n    root = tmp_path / "presentation"\n    (root / "drawings").mkdir(parents=True)\n    (root / "lot" / "office" / "drawings").mkdir(parents=True)\n    for rel in ("site.tscn", "site_base.glb", "zoo_worldskin.gd", "drawings/axonometric.svg",\n                "drawings/axonometric.svg.import", "drawings/drawings.json", "lot/office/drawings/axonometric.svg"):\n        (root / rel).write_text("x", encoding="utf-8")\n    assert ex._root_left_out(root, False) == {"site.tscn", "site_base.glb", "drawings/axonometric.svg",\n                                              "drawings/axonometric.svg.import", "drawings/drawings.json"}\n    assert ex._root_left_out(root, True) == set()\n')]}
NEW_FILES = {}
CHANGELOG = '## [0.232.1] - the Empties named, and the shell\'s drawings left out where the shell is\n\n**The factory\'s roadmap 296, read off cold run 9377\'s package** (the factory\'s\n`patches/lf_drawings/package_check_9377.out.txt`): its three buildings drawn, ten drawings each named and present,\nevery `.import` the keep file, no texture made of any drawing, the closure verdict clean -- and two holes.\n\n### Fixed\n- **The Empties named their spec.** An Empty\'s row comes from `building_library.empty_rows`, not `index`, and carried\n  no `spec`, so 9377 composed all 26 with none: their packages held no record, and `buildings.json` gave each the\n  reason "its package carries no drawings" where the reason is that it is a facade. `empty_rows` reports the spec as\n  `index` does, never used to exclude.\n- **The mission shell\'s drawings stay out where the shell does.** Deli Counter draws the composed root\'s building --\n  the mission\'s own shell -- into `drawings/` beside it, and a varied lot does not stand that shell: 9377 shipped its\n  nine files at the package\'s root beside an index of three buildings. `_root_left_out` leaves the root\'s `drawings/`\n  out with its scene pair (`_COMPOSED_ROOT_PAIR`), and leaves every root file in where the root ships; a lot\n  building\'s `lot/<id>/drawings/` is never asked.\n\n### Tests\n- **test_compose_draws_its_buildings.py**, two more: an Empty\'s row names its spec where Deli Counter has one; the\n  composed root\'s drawings stay out with its scene. On 0.232.0 the first fails on behaviour (the row has no `spec`)\n  and the second on the new name (the factory\'s `patches/lf_drawings_fix/prove_tests_on_0232.out.txt`).\n\n'
OLD_VERSION, NEW_VERSION = '0.232.0', '0.232.1'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (LF / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: level_factory/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: level_factory/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: level_factory/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (LF / name).exists():
            raise SystemExit("REFUSED: level_factory/%s exists already; nothing written" % name)
    v = LF / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = LF / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("Level Factory %s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in level_factory/: the "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
