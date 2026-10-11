"""Level Factory 0.178.1: a venv made from Blender's Python starts without an error (roadmap 202,
install test 4).

Anchored edits in `packages/tools/interpreter.py` (`import os`; `_BLENDER_SHIM` and
`blender_site_shim` before `make_venv`; `make_venv` writes the shim after the environment is made
and before pip runs, and its docstring says so) and three tests appended to
`tests/unit/test_setup_venv.py`; each file pinned by hash and each anchor asserted once, nothing
written on a miss; the file's own line endings kept. Applies on 0.178.0. CHANGELOG and VERSION from
`lf_venv_site_shim/CHANGELOG_0.178.1.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lf_venv_site_shim.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_venv_site_shim.py --fill
    LF_ROOT=<copy> python patches/patch_lf_venv_site_shim.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_venv_site_shim"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.178.0", b"0.178.1"
CHANGELOG_HEAD = "## [0.178.0] - The site spec tells Lot the package will bake its lights\n"
SHA = {"packages/tools/interpreter.py": "8ae31d198ba44e15",
       "tests/unit/test_setup_venv.py": "6b75840eecb8e5dd"}

IMP_OLD = "import json\nimport subprocess\nimport sys\n"
IMP_NEW = "import json\nimport os\nimport subprocess\nimport sys\n"

DEF_OLD = "def make_venv(root: Path, base: str, *, run=subprocess.run, timeout: int = 1800) -> tuple[str, str]:\n"
DEF_NEW = '''#: The environment's own `sitecustomize.py` when its base is Blender's bundled Python on Windows
#: (0.178.1); `blender_site_shim` says why. `{shared!r}` is the one substitution.
_BLENDER_SHIM = """\\
# Written by Level Factory's `setup --venv` (0.178.1). This environment's own sitecustomize,
# found before the one in Blender's site-packages, which this environment can see because it
# keeps its base's packages (`--system-site-packages`). Blender's finds its shared libraries
# three directories above `sys.executable` -- inside an environment, its Scripts folder -- so
# it named a directory that does not exist and printed "Error in sitecustomize" on every start.
# This one does what Blender's does, from the directory Blender's names for Blender's Python.
import os

SHARED = {shared!r}
if os.path.isdir(SHARED):
    os.add_dll_directory(SHARED)
    os.environ.setdefault("PXR_USD_WINDOWS_DLL_PATH", SHARED)
    os.environ["OIIO_LOAD_DLLS_FROM_PATH"] = "0"
    _mtlx = os.path.join(SHARED, "materialx", "libraries")
    for _var in ("MATERIALX_SEARCH_PATH", "PXR_MTLX_STDLIB_SEARCH_PATHS"):
        _was = os.environ.get(_var)
        os.environ[_var] = _mtlx if _was is None else _was + os.pathsep + _mtlx
"""


def blender_site_shim(venv: Path, base: str) -> Path | None:
    """Write the environment's own `sitecustomize.py` when `base` is Blender's bundled Python on
    Windows, and return its path; None, and nothing written, for any other base or platform.

    MEASURED, install test 4 (2026-10-11, `docs/findings/stranger_install/` in the factory): an
    environment made from Blender 5.1.1's Python by `setup --venv` printed
    `Error in sitecustomize; ... FileNotFoundError: ... '<folder above the factory>\\\\blender.shared'`
    on every start -- twelve times on the way to one first level, once on every tool the
    pipeline ran. Blender's own `sitecustomize.py` (its `lib/site-packages`) adds the DLL
    directory three folders above `sys.executable`, which in an environment is its `Scripts`
    folder, and `os.add_dll_directory` raises on a folder that is not there. Nothing failed;
    a stranger is told "Error" at every step, and an error nobody acts on is how a real one
    stops being read.

    Blender's base is recognised the way its own file finds its libraries -- `blender.shared`
    three folders above the interpreter (`C:\\\\blender\\\\5.1\\\\python\\\\bin\\\\python.exe` ->
    `C:\\\\blender\\\\blender.shared`) -- and the shim names that folder outright: an environment
    is tied to its base already (`pyvenv.cfg`'s `home`). Linux was read and not run: there
    Blender's file adds no DLL directory, only sets two environment variables, and raises
    nothing, so an environment there keeps Blender's file.
    """
    if not sys.platform.startswith("win"):
        return None
    shared = os.path.abspath(os.path.join(os.path.dirname(str(base)), "..", "..", "..",
                                          "blender.shared"))
    if not os.path.isdir(shared):
        return None
    site = Path(venv) / "Lib" / "site-packages"
    site.mkdir(parents=True, exist_ok=True)
    shim = site / "sitecustomize.py"
    shim.write_text(_BLENDER_SHIM.format(shared=shared), encoding="utf-8")
    return shim


def make_venv(root: Path, base: str, *, run=subprocess.run, timeout: int = 1800) -> tuple[str, str]:
'''

DOC_OLD = ("    as it runs, because a download that only reports at the end reads as a hang.\n"
           "    \"\"\"\n"
           "    venv = Path(root) / VENV\n")
DOC_NEW = ("    as it runs, because a download that only reports at the end reads as a hang.\n"
           "\n"
           "    From Blender's Python on Windows it writes the environment's own `sitecustomize.py`\n"
           "    (`blender_site_shim`, 0.178.1) before pip runs, so nothing the environment starts --\n"
           "    pip first -- prints Blender's \"Error in sitecustomize\".\n"
           "    \"\"\"\n"
           "    venv = Path(root) / VENV\n")

PY_OLD = ("    py = venv_python(venv)\n"
          "    if py is None:\n"
          "        return \"\", f\"{venv} has no interpreter after `-m venv`\"\n"
          "    pins = [f\"{dist}=={ver}\" for dist, ver in PINNED.items()]\n")
PY_NEW = ("    py = venv_python(venv)\n"
          "    if py is None:\n"
          "        return \"\", f\"{venv} has no interpreter after `-m venv`\"\n"
          "    blender_site_shim(venv, base)\n"
          "    pins = [f\"{dist}=={ver}\" for dist, ver in PINNED.items()]\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.178.1's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.178.1.md")
    assert entry.startswith("## [0.178.1] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"

    ip, i_eol, interp = _read("packages/tools/interpreter.py")
    assert "blender_site_shim" not in interp, "already applied"
    interp = _once(interp, IMP_OLD, IMP_NEW, "imports")
    interp = _once(interp, DEF_OLD, DEF_NEW, "make_venv def")
    interp = _once(interp, DOC_OLD, DOC_NEW, "make_venv doc")
    interp = _once(interp, PY_OLD, PY_NEW, "make_venv shim call")

    tp, t_eol, tests = _read("tests/unit/test_setup_venv.py")
    assert tests.endswith("\n")
    tests = tests.rstrip("\n") + "\n" + _src("test_blender_site_shim.py.txt")

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # Every pin and anchor matched: now write.
    ip.write_bytes(interp.replace("\n", i_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.0 -> 0.178.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
