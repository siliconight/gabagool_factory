"""Level Factory 0.255.0 on a clone: what setup downloads is said before it downloads, licences included, and every
pin is held to the licence recorded for it (the walker's call 2026-10-26, the factory's docs/THIRD_PARTY.md).
Anchored; refuses on a miss.

    python edit_lf_licences.py <clone>

Copies tests/unit/test_setup_licences.py and apps/godot/tests/test_dock_downloads.gd (+ .uid) from `src/`;
`interpreter` records LICENSES, says the downloads, and `make_venv` refuses an environment whose packages are not the
recorded versions and licences; `setup --venv`, `prepare_environment` and the dock say the downloads first.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
NEW = sorted(str(p.relative_to(HERE / "src")).replace("\\", "/") for p in (HERE / "src").rglob("*") if p.is_file())
for rel in NEW:
    dst = C / rel
    assert not dst.exists(), rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/tools/interpreter.py", [
    ('''CONSTRAINTS = "constraints.txt"
''', '''CONSTRAINTS = "constraints.txt"
#: Each package setup downloads, with the licence its own metadata declares -- ``License-Expression``, else its
#: licence classifier (`_ASK_LICENCES` reads them the same way). Measured 2026-10-26 in the factory's ``.venv`` and
#: listed for users in the factory's docs/THIRD_PARTY.md (0.255.0). The factory redistributes none of them: pip
#: fetches each from PyPI on the user's machine. `make_venv` refuses an environment whose packages are not these
#: versions under these licences, so moving a pin to a release that changed its licence fails instead of shipping.
LICENSES = {"pillow": "MIT-CMU", "pygltflib": "MIT", "jsonschema": "MIT", "dataclasses-json": "MIT",
            "deprecated": "MIT", "jsonschema-specifications": "MIT", "marshmallow": "MIT",
            "mypy-extensions": "MIT", "referencing": "MIT", "rpds-py": "MIT", "typing-inspect": "MIT",
            "wrapt": "BSD-2-Clause"}
#: Run BY the environment's interpreter: each named distribution's installed version and declared licence, as one
#: line of JSON -- ``{name: [version, licence]}``, ``[null, null]`` for one not installed.
_ASK_LICENCES = (
    "import importlib.metadata as md, json, sys\\n"
    "CLASSIFIED = {'MIT License': 'MIT', 'BSD License': 'BSD', 'Apache Software License': 'Apache-2.0'}\\n"
    "out = {}\\n"
    "for name in sys.argv[1:]:\\n"
    "    try:\\n"
    "        m = md.distribution(name).metadata\\n"
    "    except md.PackageNotFoundError:\\n"
    "        out[name] = [None, None]\\n"
    "        continue\\n"
    "    lic = m.get('License-Expression')\\n"
    "    if not lic:\\n"
    "        cls = [c.split(' :: ')[-1] for c in m.get_all('Classifier') or [] if c.startswith('License ::')]\\n"
    "        lic = CLASSIFIED.get(cls[0], cls[0]) if cls else (m.get('License') or '').strip().split('\\\\n')[0]\\n"
    "    out[name] = [m.get('Version'), lic or None]\\n"
    "print(json.dumps(out))\\n"
)


def downloads() -> list[dict]:
    """What setup downloads: ``[{"name", "version", "licence"}]``, the pins first, then what they bring."""
    held = {**PINNED, **CONSTRAINED}
    return [{"name": n, "version": held[n], "licence": LICENSES[n]} for n in [*PINNED, *CONSTRAINED]]


def downloads_said() -> str:
    """One sentence a user reads before setup downloads anything."""
    rows = downloads()
    return ("Downloads %d packages from PyPI, once, each under its own licence (%s): %s. Listed in the factory's "
            "docs/THIRD_PARTY.md." % (len(rows), ", ".join(sorted({r["licence"] for r in rows})),
                                      ", ".join("%s %s (%s)" % (r["name"], r["version"], r["licence"]) for r in rows)))


def licence_problems(py: str, *, run=subprocess.run, timeout: int = 120) -> list[str]:
    """Each way the packages installed for ``py`` differ from `PINNED`/`CONSTRAINED` and `LICENSES`; empty when
    they match. An answer this cannot read is a problem, never a pass."""
    held = {**PINNED, **CONSTRAINED}
    got = run([py, "-c", _ASK_LICENCES, *LICENSES], capture_output=True, text=True, timeout=timeout,
              stdin=subprocess.DEVNULL)
    lines = [ln for ln in (getattr(got, "stdout", "") or "").splitlines() if ln.strip()]
    try:
        found = json.loads(lines[-1])
        assert isinstance(found, dict)
    except (IndexError, ValueError, AssertionError):
        return ["%s did not say which packages it has (exit %s)" % (py, getattr(got, "returncode", "?"))]
    problems = []
    for name, licence in LICENSES.items():
        version, declared = (found.get(name) or [None, None])[:2]
        if version is None:
            problems.append("%s is not installed" % name)
        elif version != held[name]:
            problems.append("%s is %s, not the pinned %s" % (name, version, held[name]))
        elif declared != licence:
            problems.append("%s %s declares licence %r, not the recorded %r" % (name, version, declared, licence))
    return problems
'''),
    ('''def make_venv(root: Path, base: str, *, run=subprocess.run, timeout: int = 1800) -> tuple[str, str]:''',
     '''def make_venv(root: Path, base: str, *, run=subprocess.run, timeout: int = 1800,
              verify: bool = True) -> tuple[str, str]:'''),
    ('''    if got.returncode != 0:
        return "", f"pip install {' '.join(pins)} exited {got.returncode} (its output is above)"
    return str(py), ""
''', '''    if got.returncode != 0:
        return "", f"pip install {' '.join(pins)} exited {got.returncode} (its output is above)"
    # 0.255.0: what pip installed is what was recorded -- versions and licences -- or the environment is refused
    problems = licence_problems(str(py), run=run) if verify else []
    if problems:
        return "", "the installed packages are not what the factory recorded: " + "; ".join(problems)
    return str(py), ""
'''),
])

edit("apps/cli/commands/__init__.py", [
    ('''              f"({interpreter.CONSTRAINTS})")
        py, err = interpreter.make_venv(root, sys.executable)
''', '''              f"({interpreter.CONSTRAINTS})")
        print(interpreter.downloads_said())
        py, err = interpreter.make_venv(root, sys.executable)
'''),
])

edit("packages/service/operations.py", [
    ('''    events.emit("install", "running", "Downloading and installing %s" % pins)
''', '''    events.emit("install", "running", interpreter.downloads_said())
'''),
    ('''    pins = ", ".join("%s %s" % kv for kv in interpreter.PINNED.items())
    events.emit("venv", "running",''', '''    events.emit("venv", "running",'''),
    ('''    return {"factory_root": str(root), "ready": not blocking, "blocking": blocking, "worst": report.worst,
            "executables": paths, "checks": rows}
''', '''    from packages.tools import interpreter
    return {"factory_root": str(root), "ready": not blocking, "blocking": blocking, "worst": report.worst,
            "executables": paths, "checks": rows,
            # what Prepare environment would download, said before anybody presses it (0.255.0)
            "downloads": interpreter.downloads(), "downloads_said": interpreter.downloads_said()}
'''),
])

edit("apps/godot/addons/gabagool_factory/factory_dock.gd", [
    ('''var _prepare_button: Button
''', '''var _prepare_button: Button
var _downloads: Label
'''),
    ('''	_prepare_button.tooltip_text = "Gives the factory's tools a Python of their own, the same as `factory setup --venv`. " \\
		+ "It downloads Pillow, pygltflib and jsonschema once; after that the factory works offline."
	_prepare_button.visible = false
	_prepare_button.pressed.connect(prepare_environment)
	_setup.add_child(_prepare_button)
''', '''	_prepare_button.tooltip_text = "Gives the factory's tools a Python of their own, the same as `factory setup --venv`. " \\
		+ "It downloads once; after that the factory works offline."
	_prepare_button.visible = false
	_prepare_button.pressed.connect(prepare_environment)
	_setup.add_child(_prepare_button)
	# what it downloads and under which licences, read before it is pressed (0.255.0)
	_downloads = Label.new()
	_downloads.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_downloads.visible = false
	_setup.add_child(_downloads)
'''),
    ('''	_prepare_button.visible = blocking.has("tools_python")
''', '''	_prepare_button.visible = blocking.has("tools_python")
	_downloads.text = str(data.get("downloads_said", ""))
	_downloads.visible = _prepare_button.visible and _downloads.text != ""
'''),
])

edit("tests/unit/test_setup_venv.py", [
    ('''        return SimpleNamespace(returncode=self.pip_exit, stdout="", stderr="")
''', '''        if argv[1:2] == ["-c"]:              # 0.255.0: the licence question, answered as recorded
            held = {**interpreter.PINNED, **interpreter.CONSTRAINED}
            return SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(
                {n: [held[n], lic] for n, lic in interpreter.LICENSES.items()}))
        return SimpleNamespace(returncode=self.pip_exit, stdout="", stderr="")
'''),
    ('''        return SimpleNamespace(returncode=0)        # no network here: pip is not run
    py, err = interpreter.make_venv(tmp_path, sys.executable, run=run)
''', '''        return SimpleNamespace(returncode=0)        # no network here: pip is not run
    py, err = interpreter.make_venv(tmp_path, sys.executable, run=run, verify=False)   # nothing installed to check
'''),
    ('''        return SimpleNamespace(returncode=0)         # no network here: pip is not run
    py, err = interpreter.make_venv(tmp_path, str(base), run=run)
''', '''        return SimpleNamespace(returncode=0)         # no network here: pip is not run
    py, err = interpreter.make_venv(tmp_path, str(base), run=run, verify=False)   # nothing installed to check
'''),
])
