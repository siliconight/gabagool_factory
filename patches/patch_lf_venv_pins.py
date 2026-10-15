"""Level Factory 0.214.0: what the three pins bring is held too (the factory's roadmap 256, found by install
test 9).

  packages/tools/interpreter.py      `CONSTRAINED`, `CONSTRAINTS`, `write_constraints`; `make_venv` writes the
                                     file and passes `-c`
  apps/cli/commands/__init__.py      `setup --venv`'s line says what is held
  tests/unit/test_setup_venv.py      the first test restated for the `-c`; two new tests appended

Every file's sha16 pinned and every anchor asserted once, nothing written until all matched. CHANGELOG and
VERSION from `lf_venv_pins/CHANGELOG_0.214.0.md`; `--results-pending` leaves RESULT_SUITE to `--fill`.

Read before it was written, in this session: interpreter.py 53-58 (`PINNED`, `VENV`) and 128-157 (`make_venv`
whole); commands/__init__.py 200-240 (`cmd_setup`, the `--venv` branch); test_setup_venv.py whole (its `_Fake`
records each argv; the first test reads the pip call's argv by position); install test 9's setup log, the
"Successfully installed" line the nine versions come from. Every file LF.

    python patches/patch_lf_venv_pins.py --results-pending
    (the suite in level_factory; COMMANDS.md trap 1: tally the progress characters)
    python patches/patch_lf_venv_pins.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_venv_pins"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.213.0", b"0.214.0"
CHANGELOG_HEAD = "## [0.213.0] - The output layers, shown: the light apart from the art"
SHA = {"packages/tools/interpreter.py": "dc348b041d90cdc9",
       "apps/cli/commands/__init__.py": "674e1f3fca61c588",
       "tests/unit/test_setup_venv.py": "0dc3645f34a6febe"}

INTERP_PINNED_OLD = 'PINNED = {"pillow": "12.3.0", "pygltflib": "1.16.5", "jsonschema": "4.26.0"}\nVENV = ".venv"\n'
INTERP_PINNED_NEW = INTERP_PINNED_OLD + '''#: What the three bring, held at the versions install test 9 ran (0.214.0, the factory's
#: roadmap 256). pip resolved these afresh at every `setup --venv`, and two installs two days
#: apart took wrapt 2.5.0 and 2.5.1 from one package. Written to the environment's
#: `constraints.txt` and passed with `-c`: a constraint fixes a version without asking for
#: the package, so what the base already carries (attrs, packaging and typing-extensions,
#: from Blender's own Python) stays the base's.
CONSTRAINED = {"dataclasses-json": "0.6.7", "deprecated": "3.0.0",
               "jsonschema-specifications": "2025.9.1", "marshmallow": "3.26.2",
               "mypy-extensions": "1.1.0", "referencing": "0.37.0", "rpds-py": "2026.9.1",
               "typing-inspect": "0.9.0", "wrapt": "2.5.1"}
CONSTRAINTS = "constraints.txt"
'''

INTERP_DEF_OLD = 'def make_venv(root: Path, base: str, *, run=subprocess.run, timeout: int = 1800) -> tuple[str, str]:\n'
INTERP_DEF_NEW = '''def write_constraints(venv: Path) -> Path:
    """`<venv>/constraints.txt`: every distribution `setup --venv` may install, one `==`
    line each -- `PINNED` and `CONSTRAINED`, sorted (0.214.0). Returns its path."""
    path = Path(venv) / CONSTRAINTS
    lines = [f"{d}=={v}" for d, v in sorted({**PINNED, **CONSTRAINED}.items())]
    path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    return path


''' + INTERP_DEF_OLD

INTERP_DOC_OLD = '    """Make `<root>/.venv` from `base` and install `PINNED` into it. ``(its python, "")``, or\n'
INTERP_DOC_NEW = ('    """Make `<root>/.venv` from `base` and install `PINNED` into it, what they bring held at\n'
                  '    `CONSTRAINED` by a constraints file (0.214.0). ``(its python, "")``, or\n')

INTERP_PIP_OLD = ('    pins = [f"{dist}=={ver}" for dist, ver in PINNED.items()]\n'
                  '    got = run([str(py), "-m", "pip", "install", "--disable-pip-version-check", *pins],\n')
INTERP_PIP_NEW = ('    pins = [f"{dist}=={ver}" for dist, ver in PINNED.items()]\n'
                  '    constraints = write_constraints(venv)\n'
                  '    got = run([str(py), "-m", "pip", "install", "--disable-pip-version-check",\n'
                  '               "-c", str(constraints), *pins],\n')

CMD_OLD = ('        pins = ", ".join(f"{d} {v}" for d, v in interpreter.PINNED.items())\n'
           '        print(f"making {root / interpreter.VENV} from {sys.executable}, with {pins}")\n')
CMD_NEW = ('        pins = ", ".join(f"{d} {v}" for d, v in interpreter.PINNED.items())\n'
           '        print(f"making {root / interpreter.VENV} from {sys.executable}, with {pins}, and the "\n'
           '              f"{len(interpreter.CONSTRAINED)} packages they bring held at their versions "\n'
           '              f"({interpreter.CONSTRAINTS})")\n')

TEST_FIRST_OLD = '    assert sorted(fake.calls[1][5:]) == sorted(f"{d}=={v}" for d, v in interpreter.PINNED.items())\n'
TEST_FIRST_NEW = ('    assert fake.calls[1][5:7] == ["-c", str(tmp_path / ".venv" / interpreter.CONSTRAINTS)]\n'
                  '    assert sorted(fake.calls[1][7:]) == sorted(f"{d}=={v}" for d, v in interpreter.PINNED.items())\n')

TEST_END_OLD = '        "moot -- re-read Blender\'s file before keeping it", control.stderr)\n'
TEST_END_NEW = TEST_END_OLD + '''

# --------------------------------------------------------------------------- #
# 0.214.0: what the three pins bring is held too (the factory's roadmap 256)
# --------------------------------------------------------------------------- #

def test_the_constraints_file_holds_every_distribution_setup_may_install(tmp_path):
    fake = _Fake()
    interpreter.make_venv(tmp_path, "/base/python", run=fake)
    path = tmp_path / ".venv" / interpreter.CONSTRAINTS
    lines = path.read_text(encoding="utf-8").split()
    held = {**interpreter.PINNED, **interpreter.CONSTRAINED}
    # sorted by NAME, as the writer sorts: as strings, "jsonschema-specifications==..." would
    # sort before "jsonschema==..." ("-" is below "="), two spellings of one order
    assert lines == [f"{d}=={v}" for d, v in sorted(held.items())]
    assert len(lines) == 12 and not set(interpreter.PINNED) & set(interpreter.CONSTRAINED)
    # written before pip runs, which is still the second thing run, and pip is told where it is
    assert fake.calls[1][1:4] == ["-m", "pip", "install"] and fake.calls[1][5:7] == ["-c", str(path)]


def test_what_the_pins_bring_is_the_set_install_test_9_installed():
    brought = {"dataclasses-json", "deprecated", "jsonschema-specifications", "marshmallow",
               "mypy-extensions", "referencing", "rpds-py", "typing-inspect", "wrapt"}
    assert set(interpreter.CONSTRAINED) == brought
'''

EDITS = {
    "packages/tools/interpreter.py": [(INTERP_PINNED_OLD, INTERP_PINNED_NEW), (INTERP_DEF_OLD, INTERP_DEF_NEW),
                                      (INTERP_DOC_OLD, INTERP_DOC_NEW), (INTERP_PIP_OLD, INTERP_PIP_NEW)],
    "apps/cli/commands/__init__.py": [(CMD_OLD, CMD_NEW)],
    "tests/unit/test_setup_venv.py": [(TEST_FIRST_OLD, TEST_FIRST_NEW), (TEST_END_OLD, TEST_END_NEW)],
}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.214.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.214.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (LF / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.214.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.214.0] - "), entry[:40]
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
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Level Factory 0.213.0 -> 0.214.0")


if __name__ == "__main__":
    main()
