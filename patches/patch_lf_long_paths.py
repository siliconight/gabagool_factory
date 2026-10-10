"""Level Factory 0.173.0: the doctor reads the long-paths flag and weighs the workspace's depth
(roadmap 227). See `lf_long_paths/CHANGELOG_0.173.0.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  packages/tools/doctor.py         WINDOWS_MAX_PATH, LEVEL_DEPTH, long_paths_enabled(),
                                   long_paths_check(); run_doctor takes workspace_root and its
                                   windows_long_paths row comes from them
  apps/cli/commands/__init__.py    setup weighs <factory>/levels, doctor its workspace
  packages/service/facade.py       the facade's doctor weighs its workspace
  new  tests/unit/test_doctor_long_paths.py
CHANGELOG and VERSION from `CHANGELOG_0.173.0.md`.

    python patch_lf_long_paths.py --results-pending   apply, the tests' and suite's results unfilled
    python patch_lf_long_paths.py --fill               fill both from result_tests.txt, result_suite.txt
    LF_ROOT=<copy> python patch_lf_long_paths.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_long_paths"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.172.1", b"0.173.0"
CHANGELOG_HEAD = "## [0.172.1] - Re-grounded to Lot 0.106.0\n"

DOCTOR = "packages/tools/doctor.py"
D_HELPERS_ANCHOR = "def run_doctor(\n"
D_HELPERS = '''#: Windows refuses a path longer than this unless `LongPathsEnabled` is 1 (0.173.0, roadmap 227).
WINDOWS_MAX_PATH = 260
#: How far below its workspace a level's files reach, in characters. MEASURED, not derived
#: (`docs/findings/long_paths/` at the factory root): restaurant_row_001 in cold runs 9222 and
#: 9223, Level Factory 0.172.0. The deepest was a Godot editor-state file in the lux_apply
#: staging copy, 217; the pipeline's own deepest output, a texture's provenance file, 193. The
#: names come from the library and from Godot's cache scheme, so a longer prop name or mission
#: id moves it.
LEVEL_DEPTH = 217
_LONG_PATHS_KEY = "SYSTEM\\\\CurrentControlSet\\\\Control\\\\FileSystem"


def long_paths_enabled() -> int | None:
    """`LongPathsEnabled` from the registry: 1, 0, or None where it cannot be read (no winreg
    off Windows, no key, no value)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _LONG_PATHS_KEY) as key:
            value, _kind = winreg.QueryValueEx(key, "LongPathsEnabled")
    except (ImportError, OSError):
        return None
    return 1 if value == 1 else 0


def long_paths_check(flag: int | None, workspace_root=None) -> tuple[str, str]:
    """The `windows_long_paths` row, (status, detail), from the flag and the workspace's path.

    Until 0.173.0 the row WARNed on every Windows machine without reading the flag, so it could
    not pass where long paths were on, and where they were off it could not say whether a
    workspace sat deep enough to matter. It WARNs, and does not FAIL, past the budget: what
    fails with the flag off has not been measured (this repo's machine has it on).
    """
    budget = WINDOWS_MAX_PATH - 1 - LEVEL_DEPTH
    if flag == 1:
        return PASS, f"LongPathsEnabled is 1: a path may run past {WINDOWS_MAX_PATH} characters"
    said = "LongPathsEnabled is 0" if flag == 0 else "LongPathsEnabled could not be read"
    if not workspace_root:
        return WARN, (f"{said}; a level writes files up to {LEVEL_DEPTH} characters below its "
                      f"workspace, so keep a workspace's path to {budget} characters or fewer")
    reach = len(str(workspace_root)) + 1 + LEVEL_DEPTH
    if reach <= WINDOWS_MAX_PATH:
        return PASS, (f"{said}, and a level's deepest file under {workspace_root} reaches "
                      f"{reach} of {WINDOWS_MAX_PATH} characters")
    return WARN, (f"{said}, and a level's deepest file under {workspace_root} would reach "
                  f"{reach} characters, past Windows' {WINDOWS_MAX_PATH}: unzip the factory into "
                  f"a shorter folder, for a workspace of at most {budget} characters such as "
                  f"C:\\\\gabagool\\\\levels, or have an administrator turn long paths on")


'''
D_SIG_OLD = "    workspace_writable: bool = True,\n) -> DoctorReport:\n"
D_SIG_NEW = ("    workspace_writable: bool = True,\n"
             "    workspace_root=None,\n"
             ") -> DoctorReport:\n")
D_ROW_OLD = (
    "    # Windows long-path awareness (informational off-Windows).\n"
    "    if sys.platform.startswith(\"win\"):  # pragma: no cover - platform specific\n"
    "        report.add(\"windows_long_paths\", WARN,\n"
    "                   \"verify LongPathsEnabled registry flag for deep asset paths\")\n"
)
D_ROW_NEW = (
    "    # Windows long paths (0.173.0, roadmap 227): the flag, weighed against how deep the\n"
    "    # workspace sits; `long_paths_check` says why the row used to be a constant WARN.\n"
    "    if sys.platform.startswith(\"win\"):\n"
    "        report.add(\"windows_long_paths\", *long_paths_check(long_paths_enabled(), workspace_root))\n"
)

CLI = "apps/cli/commands/__init__.py"
C_SETUP_OLD = "    report = run_doctor(found.tools_local, DEFAULT_TOOLS_LOCK, registry=AdapterRegistry())\n"
C_SETUP_NEW = (
    "    # the long-path row weighs the workspace START_HERE.md's first level makes (0.173.0)\n"
    "    report = run_doctor(found.tools_local, DEFAULT_TOOLS_LOCK, registry=AdapterRegistry(),\n"
    "                        workspace_root=root / \"levels\")\n"
)
C_DOCTOR_OLD = ("    report = run_doctor(ws.load_tools_local(), ws.load_tools_lock(),\n"
                "                        registry=AdapterRegistry())\n")
C_DOCTOR_NEW = ("    report = run_doctor(ws.load_tools_local(), ws.load_tools_lock(),\n"
                "                        registry=AdapterRegistry(), workspace_root=ws.root)\n")

FACADE = "packages/service/facade.py"
F_OLD = ("            registry=AdapterRegistry(),\n"
         "            workspace_writable=True,\n"
         "        )\n")
F_NEW = ("            registry=AdapterRegistry(),\n"
         "            workspace_writable=True,\n"
         "            workspace_root=self.ws.root,\n"
         "        )\n")

NEW_TEST = ("tests/unit/test_doctor_long_paths.py", "test_doctor_long_paths.py")


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LF / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    """The tests' and suite's results into LF's CHANGELOG and this patch's copy of the entry."""
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    writes = {}
    for path, rel in ((LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.173.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.173.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.173.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.173.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    text, eol = _text(DOCTOR)
    assert "long_paths_check" not in text, "already patched"
    text = _once(text, D_HELPERS_ANCHOR, D_HELPERS + D_HELPERS_ANCHOR, "run_doctor's def")
    text = _once(text, D_SIG_OLD, D_SIG_NEW, "run_doctor's signature")
    text = _once(text, D_ROW_OLD, D_ROW_NEW, "the long-paths row")
    writes[LF / DOCTOR] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(CLI)
    text = _once(text, C_SETUP_OLD, C_SETUP_NEW, "setup's doctor")
    text = _once(text, C_DOCTOR_OLD, C_DOCTOR_NEW, "doctor's doctor")
    writes[LF / CLI] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(FACADE)
    text = _once(text, F_OLD, F_NEW, "the facade's doctor")
    writes[LF / FACADE] = text.encode("utf-8").replace(b"\n", eol)
    rel, name = NEW_TEST
    assert not (LF / rel).exists(), (rel, "already exists")
    writes[LF / rel] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl_text, cl_eol = _text("CHANGELOG.md")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    (LF / "CHANGELOG.md").write_bytes(
        (entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.172.1 -> 0.173.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
