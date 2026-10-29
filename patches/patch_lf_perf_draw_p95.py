"""Level Factory 0.269.0: a heading's draws are what the scene holds, not its stray frame.

`perf_stations.gd`'s `_sample` reports each window's p95 of draws, primitives and objects instead of the maximum,
and keeps the maximum as `draws_max` in the heading and in each pass's record. Two runs over one package had read
616 and 703 at one heading: the scene there alternates 540 and 616 and now and then submits one frame higher (the
factory's docs/findings/price_draw_flicker/).

Proven: tests/unit/test_perf_draw_p95.py fails on 0.268.0 (fails_on_old.out.txt); the clone's suite, exit 0, 2,775
passed, 18 skipped, 1 xfailed (suite_clone.out.txt); three runs of the patched harness over one package agree at
all 53 headings and equal the earlier report (p95_run{1,2,3}.json in the finding).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': '638a446ddc4c23ec', 'VERSION': 'f067ad79375be5ff', 'tools/perf_stations.gd': '1331ee8dea2ce53b'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.268.0] - a gas station and a bank on one avenue\n', "## [0.269.0] - a heading's draws are what the scene holds, not its stray frame\n\nTwo harness runs over one package disagreed on draws: slice 9's controls read 616 and 703 at one heading, a floor\nof 87 where every earlier slice price had read about 0 (the factory's `docs/findings/price_draw_flicker/`). Recorded\nframe by frame inside `perf_stations.gd`, the scene at that heading alternates 540 and 616 every frame and now and\nthen submits ONE frame higher -- 703 at frame 51 of a 60-frame window, 987 and 1008 at frames 4 and 3 of another\nheading's -- and the window's maximum, which was the heading's count, took whichever stray frame it held. All 34\nheadings whose two passes disagreed on draws across the slice's prices were at the two stations those spikes were\nrecorded at. `_sample` now reports each window's p95 of draws, primitives and objects -- the count the scene holds,\nas `ms_p95` is the frame time it holds -- and keeps the maximum as `draws_max`, in each pass's record too, so a\nspike still shows. Over the traced run's 53 headings the p95 agreed between the two passes at every heading and\nequalled the earlier report at every heading. Three hypotheses on the way are retracted and kept in the finding: a\nturn read before it reached the renderer (a diff that paired headings by list position; the report sorts them by\np95), Lux's failing streetlights cutting out (refuted with every rig rested), and the scene's first 1.5 s drawing\n158 more (real, but the harness already measures 7.5 s and more after the scene is added, and a 3.5 s settle\nchanged nothing). Why the scene spikes is not established. Tests: tests/unit/test_perf_draw_p95.py.\n\n## [0.268.0] - a gas station and a bank on one avenue\n")], 'VERSION': [('lines 1-1', '0.268.0', '0.269.0')], 'tools/perf_stations.gd': [('lines 336-338', '\tvar draws := 0\n\tvar prims := 0\n\tvar objs := 0\n', "\t# THE COUNTS ARE EACH WINDOW'S p95, NOT ITS MAXIMUM (0.269.0). Two runs over\n\t# one package read 616 and 703 draws at one heading; recorded frame by\n\t# frame (the factory's docs/findings/price_draw_flicker/), the scene there\n\t# alternates 540 and 616 every frame and now and then submits ONE frame\n\t# higher -- 703 at frame 51 of a window, 987 and 1008 at frames 4 and 3 of\n\t# another heading's -- and the maximum took whichever stray frame a window\n\t# happened to hold. The 34 headings whose passes disagreed on draws across\n\t# the slice's prices were all at the two stations those spikes were\n\t# recorded at; why the scene spikes there is not established. The p95 is the count\n\t# the scene holds, as `ms_p95` is the frame time it holds; one stray frame\n\t# in WINDOW cannot move it, and the maximum is kept beside it as\n\t# `draws_max` so a spike still shows.\n\tvar draw_frames: Array = []\n\tvar prim_frames: Array = []\n\tvar obj_frames: Array = []\n"), ('lines 345-345', '\t\tdraws = maxi(draws, int(Performance.get_monitor(\n', '\t\tdraw_frames.append(int(Performance.get_monitor(\n'), ('lines 347-347', '\t\tprims = maxi(prims, int(Performance.get_monitor(\n', '\t\tprim_frames.append(int(Performance.get_monitor(\n'), ('lines 349-349', '\t\tobjs = maxi(objs, int(Performance.get_monitor(\n', '\t\tobj_frames.append(int(Performance.get_monitor(\n'), ('lines 362-363', '\tms.sort()\n\treturn {\n', '\tms.sort()\n\tdraw_frames.sort()\n\tprim_frames.sort()\n\tobj_frames.sort()\n\tvar draws: int = int(_pct(draw_frames, 0.95))\n\tvar prims: int = int(_pct(prim_frames, 0.95))\n\tvar objs: int = int(_pct(obj_frames, 0.95))\n\treturn {\n'), ('lines 370-371', '\t\t"draws": draws, "primitives": prims, "objects": objs,\n\t}\n', '\t\t"draws": draws, "primitives": prims, "objects": objs,\n\t\t"draws_max": int(draw_frames[draw_frames.size() - 1]),\n\t}\n'), ('lines 717-717', '\t\t\t\t\t"draws": pd["draws"]})\n', '\t\t\t\t\t"draws": pd["draws"], "draws_max": pd["draws_max"]})\n')]}
WHOLE = {}
NEW_FILES = {'tests/unit/test_perf_draw_p95.py': '"""A heading\'s draws are its window\'s p95, not its maximum; the maximum is kept beside it (0.269.0).\n\nTwo harness runs over one package read 616 and 703 draws at one heading. Recorded frame by frame (the factory\'s\ndocs/findings/price_draw_flicker/, `trace_run1.json`), the scene there alternates 540 and 616 every frame and now and\nthen submits ONE frame higher -- 703 at frame 51 of a window, 987 and 1008 at frames 4 and 3 of another heading\'s --\nand the window\'s maximum took whichever stray frame it held. Over that run\'s 53 headings, the p95 of each window\nagreed between the two passes at every heading and equalled the earlier report at every heading.\n\nThe probe runs only inside Godot, so its half is read as source, as `test_perf_passes.py` reads it.\n"""\nimport re\nimport sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[2]))\n\nfrom tests.unit.test_perf_stations_run import RUNNER  # noqa: E402\n\nPROBE = RUNNER.with_name("perf_stations.gd")\n\n\ndef _sample_src():\n    s = PROBE.read_text(encoding="utf-8")\n    start = s.index("func _sample(")\n    return s[start:s.index("\\nfunc ", start + 1)]\n\n\ndef test_the_counts_are_not_a_running_maximum():\n    """FAILS ON 0.268.0: `draws = maxi(draws, ...)` -- one stray frame in the window became the heading\'s count."""\n    s = _sample_src()\n    assert not re.search(r"\\bdraws = maxi\\(", s)\n    assert not re.search(r"\\bprims = maxi\\(", s) and not re.search(r"\\bobjs = maxi\\(", s)\n\n\ndef test_the_counts_are_each_windows_p95_and_the_maximum_is_kept():\n    s = _sample_src()\n    assert "var draws: int = int(_pct(draw_frames, 0.95))" in s\n    assert "var prims: int = int(_pct(prim_frames, 0.95))" in s\n    assert "var objs: int = int(_pct(obj_frames, 0.95))" in s\n    # sorted before the percentile is read, as `ms` is\n    assert s.index("draw_frames.sort()") < s.index("int(_pct(draw_frames, 0.95))")\n    assert \'"draws_max": int(draw_frames[draw_frames.size() - 1])\' in s\n    # and every pass\'s record carries it, so a spike still shows in the report\n    assert \'"draws": pd["draws"], "draws_max": pd["draws_max"]\' in PROBE.read_text(encoding="utf-8")\n\n\ndef test_one_stray_frame_cannot_move_the_count():\n    """The window is long enough that its p95 index sits below the top three frames."""\n    src = PROBE.read_text(encoding="utf-8")\n    window = int(re.search(r"^const WINDOW := (\\d+)", src, re.M).group(1))\n    assert int(float(window - 1) * 0.95) <= window - 2\n'}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
