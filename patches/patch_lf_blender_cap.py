"""Level Factory 0.185.0: Blender jobs run three at a time where the machine allows, the width cold
run 9251 measured (factory roadmap 239, the art leg).

Anchored edits in `packages/jobs/scheduler.py`, each asserted once, nothing written until all of
them matched: `BLENDER_PROVEN_WIDTH` 3 and `blender_cap(cpu_count)` before the caps, and
`DEFAULT_CONCURRENCY["blender"]` reads it; a new `tests/unit/test_blender_cap.py` from
`lf_blender_cap/`. CHANGELOG and VERSION from `lf_blender_cap/CHANGELOG_0.185.0.md`;
`--results-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_blender_cap.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_blender_cap.py --fill
    LF_ROOT=<copy> python patches/patch_lf_blender_cap.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_blender_cap"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.184.0", b"0.185.0"
CHANGELOG_HEAD = ("## [0.184.0] - The scheduler's caps can be overridden for one invocation, so a "
                  "wider width is measured before it becomes a default\n")
SCHED = "packages/jobs/scheduler.py"
TEST = "tests/unit/test_blender_cap.py"
GODOT_TEST = "tests/unit/test_godot_cap.py"
ENV_TEST = "tests/unit/test_concurrency_override.py"
SHA = {SCHED: "a54c8f750842df0d", GODOT_TEST: "c84c13865926e385", ENV_TEST: "d5f006b56e6126a0"}

# Two tests pinned `blender` at 1, the default this release moves; each now says why.
G_OLD = ("def test_the_other_classes_did_not_move():\n"
         "    caps = scheduler.DEFAULT_CONCURRENCY\n"
         "    assert (caps[\"python_cpu\"], caps[\"blender\"], caps[\"godot_interactive\"],\n"
         "            caps[\"io_heavy\"], caps[\"lightweight\"]) == (4, 1, 1, 2, 8)\n")
G_NEW = ("def test_the_other_classes_did_not_move():\n"
         "    # `blender` moved in 0.185.0, to its own measured cap (test_blender_cap.py)\n"
         "    caps = scheduler.DEFAULT_CONCURRENCY\n"
         "    assert (caps[\"python_cpu\"], caps[\"godot_interactive\"],\n"
         "            caps[\"io_heavy\"], caps[\"lightweight\"]) == (4, 1, 2, 8)\n")
V_OLD = ("    monkeypatch.setenv(S.CONCURRENCY_ENV, \"blender=3\")\n"
         "    sch = _scheduler()\n"
         "    assert sch.concurrency[\"blender\"] == 3\n"
         "    assert sch.concurrency[\"python_cpu\"] == S.DEFAULT_CONCURRENCY[\"python_cpu\"]\n"
         "    assert \"blender 1 -> 3\" in capsys.readouterr().out\n")
V_NEW = ("    # a width the default is not, whatever the machine makes the default (0.185.0)\n"
         "    was = S.DEFAULT_CONCURRENCY[\"blender\"]\n"
         "    monkeypatch.setenv(S.CONCURRENCY_ENV, \"blender=%d\" % (was + 1))\n"
         "    sch = _scheduler()\n"
         "    assert sch.concurrency[\"blender\"] == was + 1\n"
         "    assert sch.concurrency[\"python_cpu\"] == S.DEFAULT_CONCURRENCY[\"python_cpu\"]\n"
         "    assert \"blender %d -> %d\" % (was, was + 1) in capsys.readouterr().out\n")

C_OLD = ("# Default per-resource-class concurrency caps (TDD 19.2). `godot_headless`\n"
         "# follows the machine and the proven width since 0.179.1 (`godot_cap`).\n"
         "DEFAULT_CONCURRENCY = {\n"
         "    \"python_cpu\": 4, \"blender\": 1, \"godot_headless\": godot_cap(_os.cpu_count()),\n")
C_NEW = ("#: How wide Blender jobs were PROVEN to run with nothing in their outputs\n"
         "#: changing that two runs one at a time do not already change (0.185.0).\n"
         "#: Cold run 9251 ran with `LF_CONCURRENCY=blender=3` on 9245's lot and seeds:\n"
         "#: its Blender window 45.7 s where 9250's one-at-a-time took 114.0, the art\n"
         "#: leg's jobs 177.1 s against 251.7, the drive 10.8 minutes against 12.1 -- and\n"
         "#: every model the Blender jobs built byte-identical to 9250's or different in\n"
         "#: a file that also differs between two runs at one (9248, 9249, 9250): the\n"
         "#: order of a mesh's triangles, a merged mesh's vertex order, the weighted\n"
         "#: normals of two trash-bag props drifting 1e-4 to 3e-4, Deli Counter's shell\n"
         "#: manifest (the factory's `docs/findings/grader_speed/blender_width_compare.py`).\n"
         "#: Raise it only on a measurement at the wider load.\n"
         "BLENDER_PROVEN_WIDTH = 3\n"
         "\n"
         "\n"
         "def blender_cap(cpu_count) -> int:\n"
         "    \"\"\"How many Blender jobs run at once: half the logical CPUs, never below\n"
         "    the 1 TDD 19.2 set, and no wider than `BLENDER_PROVEN_WIDTH` (0.185.0).\"\"\"\n"
         "    try:\n"
         "        cpus = int(cpu_count or 0)\n"
         "    except (TypeError, ValueError):\n"
         "        cpus = 0\n"
         "    return min(max(1, cpus // 2), max(1, BLENDER_PROVEN_WIDTH))\n"
         "\n"
         "\n"
         "# Default per-resource-class concurrency caps (TDD 19.2). `godot_headless`\n"
         "# follows the machine and the proven width since 0.179.1 (`godot_cap`), and\n"
         "# `blender` since 0.185.0 (`blender_cap`).\n"
         "DEFAULT_CONCURRENCY = {\n"
         "    \"python_cpu\": 4, \"blender\": blender_cap(_os.cpu_count()),\n"
         "    \"godot_headless\": godot_cap(_os.cpu_count()),\n")


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.185.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.185.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.185.0.md")
    assert entry.startswith("## [0.185.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_blender_cap.py.txt")
    assert not (LF / TEST).exists(), "already applied"
    sp, s_eol, sched = _read(SCHED)
    assert "BLENDER_PROVEN_WIDTH" not in sched, "already applied"
    sched = _once(sched, C_OLD, C_NEW, "the default caps")
    gp, g_eol, gtest = _read(GODOT_TEST)
    gtest = _once(gtest, G_OLD, G_NEW, "test_godot_cap's other classes")
    vp, v_eol, vtest = _read(ENV_TEST)
    vtest = _once(vtest, V_OLD, V_NEW, "test_concurrency_override's message")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(sp, s_eol, sched)
    _write(gp, g_eol, gtest)
    _write(vp, v_eol, vtest)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.184.0 -> 0.185.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
