"""Deli Counter 0.262.0: every library stair is solid underneath unless named -- the walker, of deli_a03's up-stair:
"this stair has unexpected space below it" (the factory's `docs/findings/walk_2026-10-23_deli/`, finding 4). The
library's one open underside was a 0.124.1 hand patch that outlived its reason when 0.189.0 widened the door beside it.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `specs/deli_a03.json` and `test_stair_back.py` (anchored hunks); the new `test_library_undersides.py`;
VERSION; the CHANGELOG entry, prepended. Generated from a proven clone (`patches/dc_solid_undersides/gen_dc_solid_undersides.py`),
dry-run on a fresh clone to the clone's every byte, a second run refused (`patches/dc_solid_undersides/dry_run_*.out.txt`).

    python patches/patch_dc_solid_undersides.py
    cd deli_counter && python build.py --all && python nav_gate.py --all && python -m pytest -q && python check.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "deli_counter"
PINS = {'specs/deli_a03.json': '73c555d39e8f459d', 'test_stair_back.py': 'f9656f639bbfd5e2'}
EDITS = {'specs/deli_a03.json': [('lines 409-409', '   "open_under": true,\n', ''), ('lines 411-411', '    "open_under_why": "Nav gate 2026-09-13: with the underside solid, objective_A upstairs is unreachable; the only route to this flight\'s foot passes under its high end, because deli_stair_down\'s slab hole leaves 0.4 m beside it. Reachable with the underside open.",\n', '    "underside_why": "Deli Counter 0.262.0: solid, the library default. 0.124.1 opened it (nav gate 2026-09-13: with the underside solid objective_A upstairs was unreachable, the only route to this flight\'s foot passing under its high end, deli_stair_down\'s slab hole leaving 0.4 m beside it). 0.189.0 widened office_stair_door to 2.4 m and the door now opens onto the strip beside this flight, so the opening outlived its reason: built solid, both stairs traverse and objective_A is reached at 8 of 8 voxel-grid origins. The walker, walking cold run 9383: \\"this stair has unexpected space below it\\".",\n')], 'test_stair_back.py': [('lines 177-177', '    assert n == 131, n\n', "    # 132 since 0.262.0: deli_a03's deli_stair_up, open underneath by hand since 0.124.1, is solid\n    assert n == 132, n\n")]}
REPLACED = {}
NEW_FILES = {'test_library_undersides.py': '"""Every library stair is solid underneath unless it is named here (0.262.0).\n\nThe walker, walking cold run 9383, of deli_a03\'s up-stair: "this stair has unexpected space below it". Solid has been\nthe default since the walker asked for it (2026-09-13, `test_stair_underside.py`); that stair was the library\'s one\nexception, opened by hand in 0.124.1 because its foot could only be reached from under its high end, and it outlived\nits reason when 0.189.0 widened the door beside it. Nothing noticed, because nothing asked. Now an open underside in\nthe library is a decision written down below with its reason -- a sightline, say -- or it is a failure, and the nav\ngate proves a solid flight\'s foot reachable the way it proves every flight (`nav_gate.py`).\n\nTHE TEST THAT MATTERS IS `test_every_library_stair_is_solid_unless_named`.\n"""\nimport glob\nimport os\nimport sys\n\nimport pytest\n\nHERE = os.path.dirname(os.path.abspath(__file__))\nif HERE not in sys.path:\n    sys.path.insert(0, HERE)\n\nimport spec_loader  # noqa: E402\nimport stairwell  # noqa: E402\n\n#: (spec file, stair id) -> why its underside is open. Empty: no library stair is open underneath.\nOPEN_UNDERSIDES = {}\n\n\ndef _library():\n    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):\n        spec = spec_loader.load_spec(p)\n        for st in getattr(spec, "stairs", []) or []:\n            yield os.path.basename(p), spec, st\n\n\n@pytest.fixture(autouse=True)\ndef _no_env(monkeypatch):\n    monkeypatch.delenv("DC_STAIR_UNDERSIDES", raising=False)\n\n\ndef test_every_library_stair_is_solid_unless_named():\n    opened = sorted((name, st.id) for name, spec, st in _library()\n                    if stairwell.stair_underside(spec, st) == "open" and (name, st.id) not in OPEN_UNDERSIDES)\n    assert not opened, "open underneath and not named in OPEN_UNDERSIDES: %s" % opened\n\n\ndef test_every_named_opening_is_still_open_and_says_why():\n    """A name here that no longer builds open is a reason nobody is reading."""\n    built = {(name, st.id): stairwell.stair_underside(spec, st) for name, spec, st in _library()}\n    for key, why in OPEN_UNDERSIDES.items():\n        assert built.get(key) == "open", key\n        assert why.strip(), key\n'}
CHANGELOG = '## [0.262.0] - every library stair is solid underneath unless named\n\n**The walker\'s walk of cold run 9383** (the factory\'s `docs/findings/walk_2026-10-23_deli/`, finding 4), of deli_a03\'s\nup-stair: "this stair has unexpected space below it". Solid has been the default since 2026-09-13; that flight was the\nlibrary\'s one exception, opened by hand in 0.124.1 because its foot could only be reached from under its high end, the\nbasement flight\'s slab hole leaving 0.4 m beside it. 0.189.0 widened the door beside it to 2.4 m, and the door has\nopened onto the strip beside the flight ever since -- the opening outlived its reason and nothing asked.\n\n### Changed\n- **deli_a03\'s `deli_stair_up` is solid underneath**: `open_under` removed; its `open_under_why` becomes\n  `underside_why`, keeping the history. Built solid, the nav gate traverses both stairs and reaches objective_A\n  upstairs and the patrol point at 8 of 8 voxel-grid origins (the factory\'s\n  `patches/dc_solid_undersides/navgate_deli_a03.out.txt`). The flight takes the side and back guards every solid\n  one-run flight takes, and its slot is closed by its back.\n\n### Tests\n- `test_library_undersides.py` (new): THE TEST THAT MATTERS -- every library stair builds solid underneath unless it is\n  named in `OPEN_UNDERSIDES` with its reason (empty); a name there that no longer builds open fails too. On 0.261.0 it\n  fails naming `(\'deli_a03.json\', \'deli_stair_up\')`.\n- `test_stair_back.py`: the library\'s solid one-run flights are 132, not 131 -- deli_a03\'s joins them; the slots left\n  open are still `credit_union_a02`\'s one, closed by its partition.\n\n'
OLD_VERSION, NEW_VERSION = 'Deli Counter 0.261.0', 'Deli Counter 0.262.0'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: deli_counter/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: deli_counter/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: deli_counter/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    # a refurnished spec is carried whole, the file it replaces pinned like any other
    for name, text in REPLACED.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: deli_counter/%s exists already; nothing written" % name)
    v = REPO / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.split()[-1].encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("%s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in deli_counter/: build.py --all, "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
