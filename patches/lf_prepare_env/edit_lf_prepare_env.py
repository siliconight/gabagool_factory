"""Level Factory 0.244.0 on a clone: the panel prepares the tools' Python itself (the factory's roadmap 311, increment 2
of `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_prepare_env.py <clone>

Adds `prepare_environment` to packages/service/operations.py, a Prepare button to the dock, and tests. VERSION and
CHANGELOG are the generator's.
"""
import pathlib
import sys

C = pathlib.Path(sys.argv[1])


def edit(rel, edits):
    p = C / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:90])
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/service/operations.py", [
    ('''OPERATIONS = {
    "discover_installation": discover_installation,
    "configure_installation": configure_installation,
}
''', '''def _streaming_run(run_dir: Path, events):
    """A `subprocess.run` stand-in for `interpreter.make_venv` that streams a command's output.

    `make_venv` lets pip print to the terminal "because a download that only reports at the end reads as a hang";
    the panel has no terminal, so each line goes to the run's ``pip.log`` and to an event instead. A call that asks
    to capture its output (the `-m venv` step) runs as asked."""
    import subprocess

    def run(cmd, **kw):
        if kw.get("capture_output"):
            return subprocess.run(cmd, **kw)
        timeout = kw.get("timeout")
        log = run_dir / "pip.log"
        with open(log, "a", encoding="utf-8", newline="\\n") as out:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                    text=True, encoding="utf-8", errors="replace")
            for line in proc.stdout:
                out.write(line)
                text = line.strip()
                if text:
                    events.emit("install", "running", text[:300])
            code = proc.wait(timeout=timeout)
        return subprocess.CompletedProcess(cmd, code)
    return run


def prepare_environment(arguments: dict, events) -> dict:
    """Give the tools a Python of their own: what `factory setup --venv` does, from the panel.

    Makes ``<factory>/.venv`` from the interpreter running this worker -- under the launcher, Blender's own
    Python for somebody who installed nothing else -- installs `interpreter.PINNED` into it (pip fetches them: THE
    ONE STEP THAT NEEDS THE NETWORK, and the panel says so before the user presses it), and records it as
    ``python_executable`` in ``factory.local.json``, keeping the recorded Blender and Godot. pip's output streams as
    events and into ``pip.log`` in the run directory. Returns `discover_installation`'s answer afterwards, or
    refuses with `environment_failed` naming the step that failed. No arguments."""
    import sys

    _no_unknown(arguments, set())
    from packages.tools import discovery, interpreter
    root = discovery.factory_root()
    if root is None:
        raise RequestError("no_factory", "no %s at or above this Level Factory" % discovery.MANIFEST)
    run_dir = Path(events.path).parent
    pins = ", ".join("%s %s" % kv for kv in interpreter.PINNED.items())
    events.emit("venv", "running", "Making the factory's own Python environment from %s" % sys.executable)
    events.emit("install", "running", "Downloading and installing %s" % pins)
    py, err = interpreter.make_venv(root, sys.executable, run=_streaming_run(run_dir, events))
    if err:
        raise RequestError("environment_failed", err)
    try:
        local = discovery.read_local(root)
    except ValueError as exc:
        raise RequestError("installation_unreadable", str(exc)) from None
    keep = {k: v for k, v in local.items() if k in ("blender_executable", "godot_executable")}
    keep["python_executable"] = py
    discovery.write_local(root, keep)
    events.emit("record", "ok", "The tools now run under %s" % py)
    return _installation(root, "", "")


OPERATIONS = {
    "discover_installation": discover_installation,
    "configure_installation": configure_installation,
    "prepare_environment": prepare_environment,
}
'''),
    ('''    "tools_python": "Prepare the tools' Python environment (factory setup --venv); it downloads once.",
''', '''    "tools_python": "Press Prepare environment: it gives the tools a Python of their own (downloads once).",
'''),
])

edit("packages/service/worker.py", [
    ('''    def __init__(self, run_dir: Path, request_id: str, operation: str) -> None:
        self.path = run_dir / "events.jsonl"
''', '''    def __init__(self, run_dir: Path, request_id: str, operation: str) -> None:
        #: ``events.jsonl``; its folder is the run directory an operation may write its own logs into
        self.path = run_dir / "events.jsonl"
'''),
])

edit("apps/godot/addons/gabagool_factory/factory_dock.gd", [
    ('''var _check_button: Button
''', '''var _check_button: Button
var _prepare_button: Button
'''),
    ('''	_status = Label.new()
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_status)
''', '''	# shown only when the tools' Python is what blocks (increment 2): it downloads, so it is never pressed for you
	_prepare_button = Button.new()
	_prepare_button.text = "Prepare environment (downloads once)"
	_prepare_button.tooltip_text = "Gives the factory's tools a Python of their own, the same as `factory setup --venv`. " \\
		+ "It downloads Pillow, pygltflib and jsonschema once; after that the factory works offline."
	_prepare_button.visible = false
	_prepare_button.pressed.connect(prepare_environment)
	add_child(_prepare_button)

	_status = Label.new()
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_status)
'''),
    ('''func _run(operation: String, arguments: Dictionary, message: String) -> void:
	var why: String = client.start(operation, arguments)
	if why != "":
		_status.text = "Could not start: %s" % why
		return
	_check_button.disabled = true
	_status.text = message
''', '''## Give the tools a Python of their own (`prepare_environment`); downloads once.
func prepare_environment() -> void:
	_run("prepare_environment", {}, "Preparing the tools' Python. This downloads once and can take a few minutes...")


func _run(operation: String, arguments: Dictionary, message: String) -> void:
	var why: String = client.start(operation, arguments)
	if why != "":
		_status.text = "Could not start: %s" % why
		return
	_check_button.disabled = true
	_prepare_button.disabled = true
	_status.text = message
'''),
    ('''func _on_finished(result: Dictionary) -> void:
	_check_button.disabled = client.factory_root == ""
''', '''func _on_finished(result: Dictionary) -> void:
	_check_button.disabled = client.factory_root == ""
	_prepare_button.disabled = false
'''),
    ('''	var blocking: Array = data.get("blocking", [])
''', '''	var blocking: Array = data.get("blocking", [])
	_prepare_button.visible = blocking.has("tools_python")
'''),
])

edit("apps/godot/tests/test_factory_dock.gd", [
    ('''	_check(status.begins_with("Ready") or status.begins_with("Not ready"), "the status line says: %s" % status)
''', '''	_check(status.begins_with("Ready") or status.begins_with("Not ready"), "the status line says: %s" % status)
	# increment 2: Prepare environment shows only when the tools' Python is what blocks
	dock.show_installation({"checks": [], "ready": false, "blocking": ["tools_python"]})
	_check(dock._prepare_button.visible, "Prepare environment shows when the tools' Python blocks")
	dock.show_installation({"checks": [], "ready": true, "blocking": []})
	_check(not dock._prepare_button.visible, "and hides when nothing blocks")
'''),
])

test = C / "tests" / "service" / "test_prepare_environment.py"
assert not test.exists()
test.write_bytes('''"""The panel prepares the tools' Python itself (0.244.0, the factory's roadmap 311, increment 2).

Increment 1's dock named the blocker a new user meets first on this machine -- the launcher runs the factory on
Blender's own Python, which cannot import PIL, pygltflib or jsonschema -- and its fix was `factory setup --venv`, a
terminal step. `prepare_environment` is that step as a service operation. These tests drive it with a fake `run`
so nothing is downloaded; FAILS ON 0.243.0.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.service import operations  # noqa: E402
from packages.service.worker import EventSink, RequestError  # noqa: E402


def _factory(tmp_path, monkeypatch, made="ok"):
    from packages.tools import discovery, interpreter
    monkeypatch.setattr(discovery, "factory_root", lambda start=None: tmp_path)
    (tmp_path / discovery.LOCAL_FILE).write_text(json.dumps({
        "schema": discovery.LOCAL_SCHEMA, "blender_executable": "B", "godot_executable": "G",
        "python_executable": ""}), encoding="utf-8")
    calls = []

    def fake_make_venv(root, base, *, run=None, timeout=1800):
        calls.append((root, base))
        # what make_venv's pip step does with the run it is given: a command whose output streams
        run([sys.executable, "-c", "print('Collecting pillow'); print('Successfully installed pillow')"])
        if made != "ok":
            return "", made
        return str(tmp_path / ".venv" / "Scripts" / "python.exe"), ""
    monkeypatch.setattr(interpreter, "make_venv", fake_make_venv)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    return EventSink(run_dir, "r", "prepare_environment"), calls


def test_it_makes_the_environment_records_it_and_streams_pip(tmp_path, monkeypatch):
    from packages.tools import discovery
    sink, calls = _factory(tmp_path, monkeypatch)
    out = operations.prepare_environment({}, sink)
    assert calls == [(tmp_path, sys.executable)]
    rec = json.loads((tmp_path / discovery.LOCAL_FILE).read_text(encoding="utf-8"))
    assert rec["python_executable"].endswith("python.exe")
    assert (rec["blender_executable"], rec["godot_executable"]) == ("B", "G")       # kept
    events = [json.loads(x) for x in sink.path.read_text(encoding="utf-8").splitlines()]
    said = [e["message"] for e in events if e["stage"] == "install"]
    assert "Collecting pillow" in said and "Successfully installed pillow" in said
    assert "Successfully installed pillow" in (sink.path.parent / "pip.log").read_text(encoding="utf-8")
    assert "checks" in out


def test_a_failed_install_is_a_refusal_that_says_which_step(tmp_path, monkeypatch):
    from packages.tools import discovery
    sink, _calls = _factory(tmp_path, monkeypatch, made="pip install pillow==12.3.0 exited 1")
    with pytest.raises(RequestError) as e:
        operations.prepare_environment({}, sink)
    assert e.value.code == "environment_failed" and "pip install" in str(e.value)
    rec = json.loads((tmp_path / discovery.LOCAL_FILE).read_text(encoding="utf-8"))
    assert rec["python_executable"] == ""                                      # nothing recorded


def test_it_takes_no_arguments(tmp_path, monkeypatch):
    sink, _calls = _factory(tmp_path, monkeypatch)
    with pytest.raises(RequestError):
        operations.prepare_environment({"force": True}, sink)


def test_the_tools_python_fix_names_the_button():
    assert "Prepare environment" in operations.FIXES["tools_python"]
'''.encode("utf-8"))
print("wrote", test.name)
