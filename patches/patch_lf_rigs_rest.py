"""Level Factory 0.208.0: every animated Lux rig at rest before the applied scene is packed (factory roadmap 247).

Anchored edit, asserted exactly once and the file's sha16 pinned, nothing written until it matched:
  assets/godot/run_lux_apply.gd   after the last frame awaited, before `PackedScene.pack`: every node in
                                  `lux_light_rig` that answers `rest()` (Lux 0.77.0) rested, and the count said
  tests/unit/test_lux_rigs_rest_before_pack.py   NEW (`lf_rigs_rest/test_lux_rigs_rest_before_pack.py.txt`)
CHANGELOG and VERSION from `lf_rigs_rest/CHANGELOG_0.208.0.md`; `--results-pending` leaves RESULT_ keys to `--fill`.
The GDScript is written with four spaces where the file has a tab; `_tabs` turns each leading group of four into one.

Read before it was written, in this session: `run_lux_apply.gd`'s frames (seven `await process_frame` before the
pack), its rain block and the pack and save after it, its `has_method` idiom for a Lux that may lack a method
(lines 103-111); Lux's three rigs' clocks and `rest()` (`patches/patch_lux_rig_rest.py`); and
`tests/unit/test_lux_preset_readback.py`, whose source-shape form the new test follows. Every file LF.

    python patches/patch_lf_rigs_rest.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_rigs_rest.py --fill
"""
import hashlib
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_rigs_rest"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.207.0", b"0.208.0"
CHANGELOG_HEAD = "## [0.207.0] - A package carries the buildings its scene stands, and no others\n"
DRIVER = "assets/godot/run_lux_apply.gd"
SHA = {DRIVER: "4b4e97d6a1576e2e"}
NEW = {"tests/unit/test_lux_rigs_rest_before_pack.py": "test_lux_rigs_rest_before_pack.py.txt"}


def _tabs(text):
    return re.sub(r"^((?:    )+)", lambda m: "\t" * (len(m.group(1)) // 4), text, flags=re.M)


OLD = '''        print("[lux] rain: %d drop(s); %s" % [rain_drops, rain_msg])
        await process_frame

    # Save the applied presentation scene.
    var applied := PackedScene.new()
'''
NEW_TEXT = '''        print("[lux] rain: %d drop(s); %s" % [rain_drops, rain_msg])
        await process_frame

    # EVERY ANIMATED RIG AT REST BEFORE THE SCENE IS PACKED (0.208.0, factory
    # roadmap 247). A failing or flickering fixture and a cycling stage light
    # animate from their own clocks on every frame this script awaits -- seven
    # before this point, each a wall-clock delta -- and pack() saves whatever
    # they had reached: across cold runs 9295 to 9300 eleven lights'
    # `light_energy` in this file differed in every pair. Lux 0.77.0's rigs
    # answer `rest()`, every lamp back at what its rebuild gave it and every
    # clock at zero; a Lux without it packs as before, and the count says 0.
    var rested := 0
    for rig_node in get_nodes_in_group(&"lux_light_rig"):
        if rig_node.has_method("rest"):
            rig_node.call("rest")
            rested += 1
    print("[lux] %d rig(s) at rest before the scene is packed" % rested)

    # Save the applied presentation scene.
    var applied := PackedScene.new()
'''


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
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.208.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.208.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.208.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.208.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    raw = (LF / DRIVER).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[DRIVER], (DRIVER, "is not the file this patch read", got)
    eol = _eol(raw, DRIVER)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    old, new = _tabs(OLD), _tabs(NEW_TEXT)
    assert text.count(old) == 1, (DRIVER, "anchor", text.count(old))
    assert not any(ln.startswith(" ") for ln in new.splitlines()), "a space indent left"
    text = text.replace(old, new)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        compile(data.decode("utf-8"), r, "exec")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    (LF / DRIVER).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.207.0 -> 0.208.0")


if __name__ == "__main__":
    main()
