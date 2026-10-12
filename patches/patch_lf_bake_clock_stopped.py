"""Level Factory 0.192.0: the light bake's editor stops its clock and looks for the scene at once;
the localizer skips class names a script does not contain (factory roadmap 239).

Anchored edits, each asserted once, nothing written until all of them matched:
  assets/godot/light_bake_plugin.gd   the header gains the 0.192.0 paragraph (`plugin_header`);
                                      `OPEN_FLOOR_FRAMES` beside `OPEN_LIMIT_MS`; `_enter_tree`
                                      stops the engine's clock; phase 1 looks for the opened
                                      scene from `OPEN_FLOOR_FRAMES` where it waited 240 frames
  packages/exporting/localize.py      `_rewrite_text`'s class-name scan skips a name its text does
                                      not contain (`localize_old` -> `localize_new`)
  tests/unit/test_bake_clock_stopped.py    NEW
  tests/unit/test_localize_class_scan.py   NEW
CHANGELOG and VERSION from `lf_bake_clock_stopped/CHANGELOG_0.192.0.md`; `--results-pending`
leaves the RESULT_ keys to `--fill`.

Read before it was written: docs/findings/grader_speed/bake_phases_probe.py and its runs with
--open-floor and --freeze-time (bake_phases_probe.openfloor.out.txt, .freeze.out.txt), their
lightmaps compared by lightmap_compare.py --layout; export_timeline_probe.py with --profile; the
localizer benchmarked on cold run 9257's package.

    python patches/patch_lf_bake_clock_stopped.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_bake_clock_stopped.py --fill
    LF_ROOT=<copy> python patches/patch_lf_bake_clock_stopped.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_clock_stopped"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.191.0", b"0.192.0"
CHANGELOG_HEAD = "## [0.191.0] - The light bake's editor is given the scene groups it would read first\n"
PLUGIN = "assets/godot/light_bake_plugin.gd"
LOCALIZE = "packages/exporting/localize.py"
TESTS = {"tests/unit/test_bake_clock_stopped.py": "test_bake_clock_stopped.py.txt",
         "tests/unit/test_localize_class_scan.py": "test_localize_class_scan.py.txt"}
SHA = {PLUGIN: "01e7e6b24abb602b", LOCALIZE: "8e5e353a2946d274"}

HEADER_END = '## it. The bake\'s own wait (BAKE_LIMIT_MS) was always a clock.\n'
CONST_OLD = "const OPEN_LIMIT_MS := 300000\n"
CONST_NEW = ("const OPEN_LIMIT_MS := 300000\n"
             "## The frames before the opened scene is first looked for (0.192.0). It was\n"
             "## 240, and the scene was open at that first look in every bake.\n"
             "const OPEN_FLOOR_FRAMES := 1\n")
ENTER_OLD = ("\tOS.low_processor_usage_mode = false\n"
             "\tset_process(true)\n")
ENTER_NEW = ("\tOS.low_processor_usage_mode = false\n"
             "\t# Every clock a script keeps from its frames stops here, before the scene\n"
             "\t# opens: the failing fixtures' lenses bake at one level whenever Bake is\n"
             "\t# pressed (0.192.0, the header says why).\n"
             "\tEngine.time_scale = 0.0\n"
             "\tset_process(true)\n")
FLOOR_OLD = ("\t\t1:\n"
             "\t\t\tif _frames < 240:\n"
             "\t\t\t\treturn\n")
FLOOR_NEW = ("\t\t1:\n"
             "\t\t\tif _frames < OPEN_FLOOR_FRAMES:\n"
             "\t\t\t\treturn\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.192.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.192.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.192.0.md")
    assert entry.startswith("## [0.192.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in TESTS:
        assert not (LF / rel).exists(), ("already applied", rel)
    pp, p_eol, plugin = _read(PLUGIN)
    assert "OPEN_FLOOR_FRAMES" not in plugin and "time_scale" not in plugin, "already applied"
    plugin = _once(plugin, HEADER_END, HEADER_END + _src("plugin_header.txt"), "the header's last paragraph")
    plugin = _once(plugin, CONST_OLD, CONST_NEW, "OPEN_LIMIT_MS")
    plugin = _once(plugin, ENTER_OLD, ENTER_NEW, "_enter_tree")
    plugin = _once(plugin, FLOOR_OLD, FLOOR_NEW, "the open's floor")
    assert "_frames < 240" not in plugin
    lp, l_eol, loc = _read(LOCALIZE)
    loc = _once(loc, _src("localize_old.py.txt"), _src("localize_new.py.txt"), "the class-name scan")
    tests = {rel: _src(name) for rel, name in TESTS.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(pp, p_eol, plugin)
    _write(lp, l_eol, loc)
    for rel, text in tests.items():
        (LF / rel).write_bytes(text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.191.0 -> 0.192.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
