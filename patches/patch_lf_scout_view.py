"""Level Factory 0.233.0 (the factory's roadmap 296): a level's `buildings.json` names each building's scout view,
Deli Counter 0.258.0's `drawings/scout.svg` -- res://, resolved by the closure verdict; null where a package has none.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `packages/exporting/buildings_index.py` and `tests/unit/test_buildings_index.py` (anchored hunks);
VERSION; the CHANGELOG entry, prepended. Generated from a proven clone (`patches/lf_scout_view/gen_lf_scout_view.py`),
dry-run on a fresh clone to the clone's every byte, a second run refused (`patches/lf_scout_view/dry_run_*.out.txt`).

    python patches/patch_lf_scout_view.py
    cd level_factory && python -m pytest -q
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'packages/exporting/buildings_index.py': 'd2b27bbfcbe52fee', 'tests/unit/test_buildings_index.py': 'e6224094163b4ba2'}
EDITS = {'packages/exporting/buildings_index.py': [('lines 10-11', '`site.tscn`, Godot metres, Y up. The game builds the screen; this is what it reads.\n\n', '`site.tscn`, Godot metres, Y up. The game builds the screen; this is what it reads.\n\nTHE SCOUT VIEW (0.233.0). The walker judged the axonometric too busy to scout from -- "simpler but carry all of the\nsignals needed" -- and Deli Counter 0.258.0 draws each building a second way, with only what a body finds its way\nby, as `drawings/scout.svg`. Each entry names it under `scout`; a package composed before 0.258.0 has none, and the\nentry says null there rather than guessing a path.\n\n'), ('lines 50-50', '                 "spec": None, "axonometric": None, "plans": []}\n', '                 "spec": None, "axonometric": None, "scout": None, "plans": []}\n'), ('lines 57-58', '                entry["axonometric"] = base + rec["axonometric"]\n            entry["plans"] = [{"storey": p["storey"], "file": base + p["file"]} for p in rec.get("plans") or []]\n', '                entry["axonometric"] = base + rec["axonometric"]\n            if rec.get("scout"):\n                entry["scout"] = base + rec["scout"]\n            entry["plans"] = [{"storey": p["storey"], "file": base + p["file"]} for p in rec.get("plans") or []]\n')], 'tests/unit/test_buildings_index.py': [('lines 45-49', '    for f in ("axonometric.svg", "floorB1.svg", "floor0.svg"):\n        (d / f).write_text("<svg/>", encoding="utf-8")\n    (d / "drawings.json").write_text(json.dumps({\n        "schema": "deli_counter.drawings.v1", "spec": "deli_a03", "axonometric": "axonometric.svg",\n        "plans": [{"storey": -1, "file": "floorB1.svg"}, {"storey": 0, "file": "floor0.svg"}]}), encoding="utf-8")\n', '    for f in ("axonometric.svg", "scout.svg", "floorB1.svg", "floor0.svg"):\n        (d / f).write_text("<svg/>", encoding="utf-8")\n    # deli_a03 composed by Deli Counter 0.258.0, with a scout view; office (below) by 0.257.0, without\n    (d / "drawings.json").write_text(json.dumps({\n        "schema": "deli_counter.drawings.v1", "spec": "deli_a03", "axonometric": "axonometric.svg",\n        "scout": "scout.svg",\n        "plans": [{"storey": -1, "file": "floorB1.svg"}, {"storey": 0, "file": "floor0.svg"}]}), encoding="utf-8")\n'), ('lines 102-102', '    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/floor0.svg" % BI.INDEX_NAME], issues\n', '    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/floor0.svg" % BI.INDEX_NAME], issues\n\n\ndef test_the_scout_view_is_named_where_a_package_carries_one(tmp_path):\n    """0.233.0, the factory\'s roadmap 296: a building whose package carries Deli Counter 0.258.0\'s scout view is named\n    with it, res://; one composed before has none and says null; a facade has none; and the closure verdict proves the\n    path -- take the file away and it names the index\'s reference to it."""\n    root = _package(tmp_path)\n    by_node = {e["node"]: e for e in BI.write(root)["buildings"]}\n    assert by_node["b0"]["scout"] == "res://lot/deli_a03/drawings/scout.svg"\n    assert by_node["b1"]["scout"] is None and by_node["b1"]["axonometric"] == "res://lot/office/drawings/axonometric.svg"\n    assert by_node["blocker_0"]["scout"] is None\n    assert not [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]\n    (root / "lot" / "deli_a03" / "drawings" / "scout.svg").unlink()\n    issues = [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]\n    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.svg" % BI.INDEX_NAME], issues\n')]}
NEW_FILES = {}
CHANGELOG = '## [0.233.0] - a level\'s index names each building\'s scout view\n\n**The factory\'s roadmap 296.** The walker judged the exploded axonometric too busy to scout from on two of three\nbuildings -- "simpler but carry all of the signals needed" -- and Deli Counter 0.258.0 draws each building a second\nway, with only what a body finds its way by, into its package as `drawings/scout.svg`, named in `drawings.json`.\n\n### Added\n- **`buildings.json` names it**: each entry carries `scout`, the drawing\'s `res://` path where its package has one,\n  null where it has none (a facade, or a package composed before Deli Counter 0.258.0 -- the entry says so rather\n  than guessing a path). The closure verdict resolves it as it does the other drawings.\n\n### Tests\n- `test_buildings_index.py`: a building composed with a scout view is named with it, one composed before has null, a\n  facade null, and the closure verdict names the index\'s reference when the file is taken away. On 0.232.1 it fails on\n  the new name (`KeyError: \'scout\'`).\n\n'
OLD_VERSION, NEW_VERSION = '0.232.1', '0.233.0'


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
