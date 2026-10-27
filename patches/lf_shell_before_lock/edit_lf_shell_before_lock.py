"""Edit a Level Factory clone for 0.259.0: the panel's walk builds the chosen layout's shell before it locks it. Run
from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("packages/service/walking.py", [
('''    legs = [("import", ["-C", str(ws), "batch", "create", str(batch_path)]),
            ("brief", ["-C", str(ws), "approve", mission, "brief_approved", "--by", "panel", "--note", AUTOMATIC]),
            ("lock", ["-C", str(ws), "approve", mission, "functional_shell_locked", "--by", "panel",
                      "--note", AUTOMATIC]),''',
'''    # THE SHELL BEFORE THE LOCK (0.259.0). The lock records the chosen layout's shell AS IT STANDS -- its collision,
    # anchors and interactives -- and the art leg rebuilds that shell first wherever a tool changed it. Locked
    # before the rebuild, the lock held yesterday's shell and the export refused today's: walking seed 9205 after
    # Deli Counter 0.275.0-0.277.0 furnished its supermarket anew, "export blocked by functional regression:
    # collision_fingerprint changed after art pass", every time, until somebody re-locked by hand. `make` already
    # builds the shell before it locks; the panel's walk now does too.
    legs = [("import", ["-C", str(ws), "batch", "create", str(batch_path)]),
            ("brief", ["-C", str(ws), "approve", mission, "brief_approved", "--by", "panel", "--note", AUTOMATIC]),
            ("shell", ["-C", str(ws), "run", mission]),
            ("lock", ["-C", str(ws), "approve", mission, "functional_shell_locked", "--by", "panel",
                      "--note", AUTOMATIC]),'''),
('''    said = {"import": "Reading revision %d of the level" % doc["revision"], "brief": "Recording the brief",''',
'''    said = {"import": "Reading revision %d of the level" % doc["revision"], "brief": "Recording the brief",
            "shell": "Building the chosen layout's shell",'''),
])

edit("tests/service/test_walking.py", [
('''    assert [a[2] for a in calls] == ["approve", "approve", "run", "walk"]
    assert calls[0][3:5] == ["walker_001", "brief_approved"] and calls[1][4] == "functional_shell_locked"
    for gate in calls[:2]:
        assert gate[gate.index("--by") + 1] == "panel" and "not a review" in gate[gate.index("--note") + 1]
    assert calls[2][-2:] == ["--art", "--gameplay"] and "--play" not in calls[3]''',
'''    # 0.259.0: the shell is built before it is locked
    assert [a[2] for a in calls] == ["approve", "run", "approve", "run", "walk"]
    assert calls[0][3:5] == ["walker_001", "brief_approved"] and calls[2][4] == "functional_shell_locked"
    for gate in (calls[0], calls[2]):
        assert gate[gate.index("--by") + 1] == "panel" and "not a review" in gate[gate.index("--note") + 1]
    assert calls[1][2:] == ["run", "walker_001"]
    assert calls[3][-2:] == ["--art", "--gameplay"] and "--play" not in calls[4]'''),
('''    def leg(argv, log, *, cancel_file, on_poll=None):
        return 4 if argv[2:3] == ["run"] else _fake(calls)(argv, log, cancel_file=cancel_file)
    with pytest.raises(layouts.LayoutError) as e:
        walking.walk(got["path"], EventSink(run_dir, "r", "w"), run_dir, leg=leg)
    assert e.value.code == "leg_failed" and "art exited 4" in str(e.value)''',
'''    def leg(argv, log, *, cancel_file, on_poll=None):
        return 4 if argv[2:3] == ["run"] and "--art" in argv else _fake(calls)(argv, log, cancel_file=cancel_file)
    with pytest.raises(layouts.LayoutError) as e:
        walking.walk(got["path"], EventSink(run_dir, "r", "w"), run_dir, leg=leg)
    assert e.value.code == "leg_failed" and "art exited 4" in str(e.value)


def test_the_shell_is_built_before_it_is_locked(level):
    """0.259.0: the lock records the shell as it stands, so it must stand rebuilt -- locked first, a tool change that
    re-furnished a building made every walk's export refuse its own art pass ("collision_fingerprint changed after
    art pass"). A shell that fails stops the walk before anything is locked. FAILS ON 0.258.0."""
    got, run_dir, ws = level
    calls = []
    _workspace(level, calls)

    def leg(argv, log, *, cancel_file, on_poll=None):
        return 4 if argv[2:3] == ["run"] and "--art" not in argv else _fake(calls)(argv, log, cancel_file=cancel_file)
    with pytest.raises(layouts.LayoutError) as e:
        walking.walk(got["path"], EventSink(run_dir, "r", "w"), run_dir, leg=leg)
    assert e.value.code == "leg_failed" and "shell exited 4" in str(e.value)
    assert not [a for a in calls if "functional_shell_locked" in a]'''),
])

edit("tests/service/test_revise.py", [
('''    assert calls[0][2:4] == ["batch", "create"] and [a[2] for a in calls[1:]] == ["approve", "approve", "run", "walk"]''',
 '''    # 0.259.0: the shell is built before it is locked
    assert calls[0][2:4] == ["batch", "create"] and [a[2] for a in calls[1:]] == ["approve", "run", "approve", "run",
                                                                                 "walk"]'''),
])
