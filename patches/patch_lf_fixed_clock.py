"""Level Factory 0.180.0: Laser Tag's evaluation runs on a clock that does not wait on real seconds,
and the grounded table follows the two tools that moved (Laser Tag 0.27.0, Zoo 1.102.0).

See `lf_fixed_clock/CHANGELOG_0.180.0.md`. Anchored edits, each asserted once, nothing written until
all of them matched:
  adapters/laser_tag/__init__.py   `LaserTagAdapter.fixed_fps` 60, and `plan_commands` passes
                                   `--fixed-fps 60` to the engine, before `--`
  packages/tools/contracts.py      laser_tag 0.26.0 -> 0.27.0, zoo 1.101.0 -> 1.102.0, and a note
                                   above 0.179.1's
  tests/fixtures/repos/laser_tag/VERSION, tests/fixtures/repos/zoo/VERSION   the stubs
  tests/unit/test_laser_tag_clock.py   NEW, from `lf_fixed_clock/test_laser_tag_clock.py.txt`
CHANGELOG and VERSION from `lf_fixed_clock/CHANGELOG_0.180.0.md`.

    python patches/patch_lf_fixed_clock.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_fixed_clock.py --fill
    LF_ROOT=<copy> python patches/patch_lf_fixed_clock.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_fixed_clock"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_SMOKE": "result_smoke.txt"}
VERSION_WAS, VERSION = b"0.179.1", b"0.180.0"
CHANGELOG_HEAD = ("## [0.179.1] - The Godot cap follows the machine and the width the graders were "
                  "proven at; the grounded table follows Deli Counter 0.209.1 and Laser Tag 0.26.0\n")

ADAPTER = "adapters/laser_tag/__init__.py"
CONTRACTS = "packages/tools/contracts.py"
TEST = "tests/unit/test_laser_tag_clock.py"
SHA = {ADAPTER: "18b02e33db2e09f4", CONTRACTS: "96d7d391f7ec0c49"}

A_ATTR_OLD = "    bake_wall_budget_seconds = 120.0\n"
A_ATTR_NEW = (
    "    bake_wall_budget_seconds = 120.0\n"
    "\n"
    "    #: THE CLOCK (0.180.0, factory roadmap 239). Godot paced every evaluation to\n"
    "    #: Laser Tag's 4x clock in REAL seconds: measured on cold runs 9245 and 9247,\n"
    "    #: each simulated 3.91 to 3.97 times its job's wall time, so most of a\n"
    "    #: ten-minute job waited. The engine's `--fixed-fps` makes each frame one\n"
    "    #: physics step computed as fast as the processor allows, the step itself\n"
    "    #: unchanged; 60 is the staged project's physics tick rate (staging leaves\n"
    "    #: Godot's default), so one frame is one step. With Laser Tag 0.27.0's\n"
    "    #: navigation updating on the evaluation's thread the report reads the same\n"
    "    #: in every field: cold run 9247's seed_9104 593 s -> 21 s, and fourteen\n"
    "    #: more candidates the same twice each (`docs/findings/grader_speed/` in the\n"
    "    #: factory). Laser Tag cannot see which clock it runs on (the engine leaves\n"
    "    #: `--fixed-fps` out of `OS.get_cmdline_args`), so this is the one place the\n"
    "    #: clock is chosen; 0 restores the synchronised clock. The budgets above\n"
    "    #: stay ceilings for the synchronised case.\n"
    "    fixed_fps = 60\n")
A_ARGS_OLD = ("        args = [\n"
              "            \"--headless\", \"--path\", str(project),\n")
A_ARGS_NEW = ("        # The clock is the ENGINE's, so it goes before `--` (`fixed_fps`).\n"
              "        clock = ([\"--fixed-fps\", str(int(self.fixed_fps))]\n"
              "                 if self.fixed_fps else [])\n"
              "        args = [\n"
              "            \"--headless\", *clock, \"--path\", str(project),\n")

ROWS = [
    ('    "laser_tag":    {"version": "0.26.0", "source": "VERSION",\n',
     '    "laser_tag":    {"version": "0.27.0", "source": "VERSION",\n'),
    ('    "zoo":          {"version": "1.101.0", "source": "VERSION",\n',
     '    "zoo":          {"version": "1.102.0", "source": "VERSION",\n'),
]
NOTE_ANCHOR = "# RE-GROUNDED 2026-10-11 (0.179.1), TWO ROWS: deli_counter 0.209.0 -> 0.209.1\n"
NOTE = (
    "# RE-GROUNDED 2026-10-11 (0.180.0), TWO ROWS: laser_tag 0.26.0 -> 0.27.0 (the\n"
    "# navigation map updates on the evaluation's thread, so `--fixed-fps` reads the\n"
    "# same report) and zoo 1.101.0 -> 1.102.0 (what a roof carries follows what the\n"
    "# building is). Licensed by the real-tool smoke, which read exactly these two\n"
    "# rows DRIFT before and all green after.\n"
    "#\n"
)
STUBS = [
    ("tests/fixtures/repos/laser_tag/VERSION", b"Laser Tag 0.26.0\n", b"Laser Tag 0.27.0\n"),
    ("tests/fixtures/repos/zoo/VERSION", b"1.101.0\n", b"1.102.0\n"),
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.180.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.180.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.180.0.md")
    assert entry.startswith("## [0.180.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_laser_tag_clock.py.txt")
    assert not (LF / TEST).exists(), "already applied"

    ap, a_eol, adapter = _read(ADAPTER)
    assert "fixed_fps" not in adapter, "already applied"
    adapter = _once(adapter, A_ATTR_OLD, A_ATTR_NEW, "the adapter's budgets")
    adapter = _once(adapter, A_ARGS_OLD, A_ARGS_NEW, "plan_commands' arguments")
    cp, c_eol, contracts = _read(CONTRACTS)
    for old, new in ROWS:
        contracts = _once(contracts, old, new, old.strip()[:30])
    contracts = _once(contracts, NOTE_ANCHOR, NOTE + NOTE_ANCHOR, "0.179.1's note")
    stubs = []
    for rel, old, new in STUBS:
        raw = (LF / rel).read_bytes()
        assert raw == old, (rel, raw)
        stubs.append((LF / rel, new))

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    _write(ap, a_eol, adapter)
    _write(cp, c_eol, contracts)
    for p, data in stubs:
        p.write_bytes(data)
    (LF / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.179.1 -> 0.180.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
