"""Level Factory 0.179.1: the Godot cap follows the machine and the width the graders were proven
at, and the grounded table follows the two tools that moved (Deli Counter 0.209.1, Laser Tag 0.26.0).

See `lf_grader_cap/CHANGELOG_0.179.1.md`. Anchored edits, each asserted once, nothing written until
all of them matched:
  packages/jobs/scheduler.py     `GODOT_PROVEN_WIDTH` 3 and `godot_cap(cpu_count)`: half the
                                 logical CPUs, never below 2, never above the proven width;
                                 `DEFAULT_CONCURRENCY["godot_headless"]` reads it
  packages/tools/contracts.py    deli_counter 0.209.0 -> 0.209.1, laser_tag 0.25.0 -> 0.26.0, and
                                 a note above 0.179.0's
  tests/fixtures/repos/deli_counter/VERSION, tests/fixtures/repos/laser_tag/VERSION   the stubs
  tests/unit/test_godot_cap.py   NEW, from `lf_grader_cap/test_godot_cap.py.txt`
CHANGELOG and VERSION from `lf_grader_cap/CHANGELOG_0.179.1.md`.

    python patches/patch_lf_grader_cap.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_grader_cap.py --fill
    LF_ROOT=<copy> python patches/patch_lf_grader_cap.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_grader_cap"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_SMOKE": "result_smoke.txt",
           "RESULT_WIDTH": "result_width.txt"}
VERSION_WAS, VERSION = b"0.179.0", b"0.179.1"
CHANGELOG_HEAD = "## [0.179.0] - Roof props reach a level: a job of their own per enterable building\n"

SCHED = "packages/jobs/scheduler.py"
CONTRACTS = "packages/tools/contracts.py"
TEST = "tests/unit/test_godot_cap.py"
SHA = {SCHED: "051f613b7322540f", CONTRACTS: "ff438cab9d93f68f"}

S_IMP_OLD = "import datetime as _dt\nimport shutil as _shutil\n"
S_IMP_NEW = "import datetime as _dt\nimport os as _os\nimport shutil as _shutil\n"
S_CAP_OLD = ("# Default per-resource-class concurrency caps (TDD 19.2).\n"
             "DEFAULT_CONCURRENCY = {\n"
             "    \"python_cpu\": 4, \"blender\": 1, \"godot_headless\": 2,\n"
             "    \"godot_interactive\": 1, \"io_heavy\": 2, \"lightweight\": 8,\n"
             "}\n")
S_CAP_NEW = (
    "#: How wide the graders were PROVEN to run with every VERDICT unchanged\n"
    "#: (0.179.1, the walker's call 2026-10-11). Cold run 9246's graders rerun from\n"
    "#: copies of their staged projects: alone, or two at a time as before, every\n"
    "#: report identical to its job's in every field; three and six at a time,\n"
    "#: every grade, score, summary figure, finding, event count, time, source and\n"
    "#: collider identical in every trial, and one to three recorded event\n"
    "#: POSITIONS in some reports one rounding step (0.01 m) apart -- the same\n"
    "#: values each time, sitting on a rounding boundary, cause not established\n"
    "#: (async navigation iterations and the shared worker pool are the suspects).\n"
    "#: The walk tests stayed byte-identical at six. Raise this only on a\n"
    "#: measurement at the wider load (`docs/findings/grader_speed/` in the factory).\n"
    "GODOT_PROVEN_WIDTH = 3\n"
    "\n"
    "\n"
    "def godot_cap(cpu_count) -> int:\n"
    "    \"\"\"How many headless Godot jobs run at once: what the machine allows -- one\n"
    "    per physical core, read as half the logical CPUs (the stdlib reports only\n"
    "    those), never below the 2 every machine had -- and no wider than the load\n"
    "    the graders' verdicts were proven unchanged under (0.179.1).\n"
    "\n"
    "    MEASURED, NOT CHOSEN. The graders are this class -- each candidate's Laser\n"
    "    Tag evaluation and walk test -- and they were 88 % of cold run 9245's job\n"
    "    time, queued two at a time on 8 cores and 16 logical CPUs: its shell leg\n"
    "    spanned 15.7 minutes, and its longest single evaluation was 10.25 of them.\n"
    "    That job bounds the leg at any width, so three recovers nearly all of what\n"
    "    six would. A coarser simulation clock was measured too and REFUSED: Godot\n"
    "    scales the physics step with `time_scale`, and the reports changed.\n"
    "    \"\"\"\n"
    "    try:\n"
    "        cpus = int(cpu_count or 0)\n"
    "    except (TypeError, ValueError):\n"
    "        cpus = 0\n"
    "    return min(max(2, cpus // 2), max(2, GODOT_PROVEN_WIDTH))\n"
    "\n"
    "\n"
    "# Default per-resource-class concurrency caps (TDD 19.2). `godot_headless`\n"
    "# follows the machine and the proven width since 0.179.1 (`godot_cap`).\n"
    "DEFAULT_CONCURRENCY = {\n"
    "    \"python_cpu\": 4, \"blender\": 1, \"godot_headless\": godot_cap(_os.cpu_count()),\n"
    "    \"godot_interactive\": 1, \"io_heavy\": 2, \"lightweight\": 8,\n"
    "}\n")

ROWS = [
    ('    "deli_counter": {"version": "0.209.0", "source": "VERSION"},\n',
     '    "deli_counter": {"version": "0.209.1", "source": "VERSION"},\n'),
    ('    "laser_tag":    {"version": "0.25.0", "source": "VERSION",\n',
     '    "laser_tag":    {"version": "0.26.0", "source": "VERSION",\n'),
]
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.179.0), TWO ROWS, for the set after factory 1.38.0:\n"
NOTE = (
    "# RE-GROUNDED 2026-10-11 (0.179.1), TWO ROWS: deli_counter 0.209.0 -> 0.209.1\n"
    "# (a stair's circulation column ends at the top floor it serves) and laser_tag\n"
    "# 0.25.0 -> 0.26.0 (an enemy is built and steered as the contract's body).\n"
    "# Licensed by the real-tool smoke, which read exactly these two rows DRIFT\n"
    "# before and all green after.\n"
    "#\n"
)
STUBS = [
    ("tests/fixtures/repos/deli_counter/VERSION", b"Deli Counter 0.209.0\n", b"Deli Counter 0.209.1\n"),
    ("tests/fixtures/repos/laser_tag/VERSION", b"Laser Tag 0.25.0\n", b"Laser Tag 0.26.0\n"),
]


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.179.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.179.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.179.1.md")
    assert entry.startswith("## [0.179.1] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_godot_cap.py.txt")
    assert not (LF / TEST).exists(), "already applied"

    sp, s_eol, sched = _read(SCHED)
    assert "def godot_cap" not in sched, "already applied"
    sched = _once(sched, S_IMP_OLD, S_IMP_NEW, "the scheduler's imports")
    sched = _once(sched, S_CAP_OLD, S_CAP_NEW, "DEFAULT_CONCURRENCY")
    cp, c_eol, contracts = _read(CONTRACTS)
    assert "(0.179.1), TWO ROWS" not in contracts, "already applied"
    for old, new in ROWS:
        contracts = _once(contracts, old, new, old.strip())
    contracts = _once(contracts, NOTE_ANCHOR, NOTE + NOTE_ANCHOR, "0.179.0's note")
    stubs = []
    for rel, old, new in STUBS:
        got = (LF / rel).read_bytes()
        assert got.replace(b"\r\n", b"\n") == old, (rel, got)
        stubs.append((LF / rel, new))
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    _write(sp, s_eol, sched)
    _write(cp, c_eol, contracts)
    for p, new in stubs:
        p.write_bytes(new)
    _write(LF / TEST, b"\n", test_text)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.179.0 -> 0.179.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
