"""Level Factory 0.234.0 (the factory's roadmap 295): a level's `buildings.json` names each building's scout model,
Deli Counter 0.259.0's `drawings/scout.glb` -- res://, resolved by the closure verdict; null where a package has none.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `packages/exporting/buildings_index.py` and `tests/unit/test_buildings_index.py` (anchored hunks);
VERSION; the CHANGELOG entry, prepended. Generated from a proven clone (`patches/lf_scout_model/gen_lf_scout_model.py`),
dry-run on a fresh clone to the clone's every byte, a second run refused (`patches/lf_scout_model/dry_run_*.out.txt`).

    python patches/patch_lf_scout_model.py
    cd level_factory && python -m pytest -q
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'packages/exporting/buildings_index.py': 'f412cc57db717169', 'tests/unit/test_buildings_index.py': 'ad4ee4056da482ca'}
EDITS = {'packages/exporting/buildings_index.py': [('lines 15-16', 'entry says null there rather than guessing a path.\n\n', 'entry says null there rather than guessing a path.\n\nTHE SCOUT MODEL (0.234.0). The walker wants the scout view as something players turn all the way round -- "They\ncan scout out the buildings and rotate the schemas in a 360 degree way" (roadmap 295) -- and Deli Counter 0.259.0\nbuilds it, `drawings/scout.glb`, one mesh a storey, kept as the file it is so a game loads it with `GLTFDocument`\nwhen its screen opens. Each entry names it under `scout_model`, null where a package has none.\n\n'), ('lines 55-55', '                 "spec": None, "axonometric": None, "scout": None, "plans": []}\n', '                 "spec": None, "axonometric": None, "scout": None, "scout_model": None, "plans": []}\n'), ('lines 64-65', '                entry["scout"] = base + rec["scout"]\n            entry["plans"] = [{"storey": p["storey"], "file": base + p["file"]} for p in rec.get("plans") or []]\n', '                entry["scout"] = base + rec["scout"]\n            if rec.get("scout_model"):\n                entry["scout_model"] = base + rec["scout_model"]\n            entry["plans"] = [{"storey": p["storey"], "file": base + p["file"]} for p in rec.get("plans") or []]\n')], 'tests/unit/test_buildings_index.py': [('lines 46-47', '        (d / f).write_text("<svg/>", encoding="utf-8")\n    # deli_a03 composed by Deli Counter 0.258.0, with a scout view; office (below) by 0.257.0, without\n', '        (d / f).write_text("<svg/>", encoding="utf-8")\n    (d / "scout.glb").write_bytes(b"glTF")\n    # deli_a03 composed by Deli Counter 0.258.0, with a scout view; office (below) by 0.257.0, without\n'), ('lines 50-50', '        "scout": "scout.svg",\n', '        "scout": "scout.svg", "scout_model": "scout.glb",\n'), ('lines 119-119', '    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.svg" % BI.INDEX_NAME], issues\n', '    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.svg" % BI.INDEX_NAME], issues\n\n\ndef test_the_scout_model_is_named_where_a_package_carries_one(tmp_path):\n    """0.234.0, the factory\'s roadmap 295: a building whose package carries Deli Counter 0.259.0\'s scout model is named\n    with it, res://; one composed before has none and says null; a facade has none; and the closure verdict proves the\n    path -- take the model away and it names the index\'s reference to it."""\n    root = _package(tmp_path)\n    by_node = {e["node"]: e for e in BI.write(root)["buildings"]}\n    assert by_node["b0"]["scout_model"] == "res://lot/deli_a03/drawings/scout.glb"\n    assert by_node["b1"]["scout_model"] is None and by_node["blocker_0"]["scout_model"] is None\n    assert not [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]\n    (root / "lot" / "deli_a03" / "drawings" / "scout.glb").unlink()\n    issues = [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]\n    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.glb" % BI.INDEX_NAME], issues\n')]}
NEW_FILES = {}
CHANGELOG = '## [0.234.0] - a level\'s index names each building\'s scout model\n\n**The factory\'s roadmap 295.** The walker wants the scout view as something players turn all the way round -- "They\ncan scout out the buildings and rotate the schemas in a 360 degree way" -- and Deli Counter 0.259.0 builds it into\neach building\'s package as `drawings/scout.glb`: one mesh a storey, one material, kept as the file it is, so a game\nloads it with `GLTFDocument` when its screen opens.\n\n### Added\n- **`buildings.json` names it**: each entry carries `scout_model`, the model\'s `res://` path where its package has\n  one, null where it has none (a facade, or a package composed before Deli Counter 0.259.0). The closure verdict\n  resolves it as it does the drawings.\n\n### Tests\n- `test_buildings_index.py`: a building composed with a scout model is named with it, one composed before has null, a\n  facade null, and the closure verdict names the index\'s reference when the model is taken away. On 0.233.0 it fails\n  on the new name (`KeyError: \'scout_model\'`).\n\n'
OLD_VERSION, NEW_VERSION = '0.233.0', '0.234.0'


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
