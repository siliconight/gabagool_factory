"""Where does an export's time go, outside the light bake's editor?

Re-exports a workspace's mission in-process -- its own package held aside and put back, as the
other re-export probes do -- with two things watched: every process the export starts (Godot,
Blender, anything through `subprocess.Popen`, which `subprocess.run` uses too), its start since the
export began, how long it ran and a short form of its command; and every line the export prints,
stamped with the seconds since it began. Between two processes the time is the export's own
Python. Prints the timeline, then the processes grouped by kind with their totals, then the
Python time between them. It measures and prints; it names no cause.

    python docs/findings/grader_speed/export_timeline_probe.py <workspace> <mission> [--profile]

`--profile` runs the export under cProfile as well and prints the export's own functions by
cumulative and by own time (slower: the timeline is then not a timing to quote).
"""
import builtins
import os
import runpy
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "export_timeline")
PROFILE = "--profile" in sys.argv
T0 = [0.0]
EVENTS = []      # (start since T0, seconds, kind, short command, return code)
LINES = []       # (seconds since T0, the line)


def short(cmd):
    """The kind of a process and a short form of its command."""
    parts = [str(c) for c in (cmd if isinstance(cmd, (list, tuple)) else [cmd])]
    exe = os.path.basename(parts[0]).lower() if parts else "?"
    keep = []
    for i, p in enumerate(parts[1:], 1):
        if p.startswith("--") and p not in ("--path", "--resolution"):
            keep.append(p)
        elif parts[i - 1] in ("-s", "--script", "--python") and p:
            keep.append(os.path.basename(p))
    kind = "godot" if "godot" in exe else ("blender" if "blender" in exe else exe)
    if kind == "godot":
        if "--editor" in keep:
            kind = "godot --editor"
        elif "--import" in keep:
            kind = "godot --import"
        else:
            kind = "godot --script"
    return kind, " ".join([exe] + keep)[:150]


class TimedPopen(subprocess.Popen):
    def __init__(self, args, *a, **kw):
        self._lf_t0 = time.time()
        self._lf_args = args
        self._lf_done = False
        super().__init__(args, *a, **kw)

    def _lf_note(self):
        if not self._lf_done and self.returncode is not None:
            self._lf_done = True
            kind, cmd = short(self._lf_args)
            EVENTS.append((self._lf_t0 - T0[0], time.time() - self._lf_t0, kind, cmd, self.returncode))

    def wait(self, *a, **kw):
        r = super().wait(*a, **kw)
        self._lf_note()
        return r

    def poll(self):
        r = super().poll()
        self._lf_note()
        return r


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    subprocess.Popen = TimedPopen
    real_print = builtins.print

    def stamped(*a, **kw):
        if kw.get("file") in (None, sys.stdout):
            LINES.append((time.time() - T0[0], " ".join(str(x) for x in a)))
        return real_print(*a, **kw)
    os.makedirs(X, exist_ok=True)
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    try:
        sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
        builtins.print = stamped
        prof = None
        if PROFILE:
            import cProfile
            prof = cProfile.Profile()
            prof.enable()
        T0[0] = time.time()
        try:
            runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
        except SystemExit as exc:
            LINES.append((time.time() - T0[0], "export exit %s" % exc.code))
        total = time.time() - T0[0]
        if prof is not None:
            prof.disable()
    finally:
        builtins.print = real_print
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                p = os.path.join(exports, n)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        real_print("[tl] the run's package restored", flush=True)
    real_print("[tl] the export %.1f s; %d process(es); %d line(s) printed" % (total, len(EVENTS), len(LINES)))
    timeline = [(t, "proc", "%-15s %6.1f s  %s (exit %s)" % (k, d, c, rc)) for t, d, k, c, rc in EVENTS]
    timeline += [(t, "line", s[:150]) for t, s in LINES if s.strip()]
    for t, what, s in sorted(timeline):
        real_print("[tl] %7.1f  %s  %s" % (t, "P" if what == "proc" else " ", s))
    kinds = {}
    for t, d, k, c, rc in EVENTS:
        n, s = kinds.get(k, (0, 0.0))
        kinds[k] = (n + 1, s + d)
    for k, (n, s) in sorted(kinds.items(), key=lambda kv: -kv[1][1]):
        real_print("[tl] by kind: %-15s %3d process(es) %7.1f s" % (k, n, s))
    # the export's own time: the wall less the union of the processes' spans
    spans = sorted((t, t + d) for t, d, _k, _c, _rc in EVENTS)
    covered, end = 0.0, 0.0
    for a, b in spans:
        if b <= end:
            continue
        covered += b - max(a, end)
        end = b
    real_print("[tl] processes running %.1f s of the %.1f; the export's own Python %.1f s"
               % (covered, total, total - covered))
    gaps = []
    end = 0.0
    for a, b in spans:
        if a > end:
            gaps.append((a - end, end, a))
        end = max(end, b)
    if total > end:
        gaps.append((total - end, end, total))
    for g, a, b in sorted(gaps, reverse=True)[:10]:
        real_print("[tl] no process from %7.1f to %7.1f: %5.1f s" % (a, b, g))
    if PROFILE:
        # the export's own functions by their own time and by what they and their callees took,
        # less the time spent waiting on a process (Popen.wait / poll / communicate)
        import pstats
        st = pstats.Stats(prof)
        rows = []
        for (path, line, fn), (cc, nc, tt, ct, callers) in st.stats.items():
            if "level_factory" in path.replace("\\", "/"):
                rel = path.replace("\\", "/").split("level_factory/", 1)[-1]
                rows.append((ct, tt, nc, "%s:%d %s" % (rel, line, fn)))
        real_print("[tl] profile, the export's functions by cumulative time (cumulative includes the "
                   "processes they waited on):")
        for ct, tt, nc, name in sorted(rows, reverse=True)[:40]:
            real_print("[tl]   cum %7.1f s  own %6.1f s  calls %6d  %s" % (ct, tt, nc, name))
        real_print("[tl] profile, by own time:")
        for ct, tt, nc, name in sorted(rows, key=lambda r: -r[1])[:15]:
            real_print("[tl]   own %6.1f s  cum %7.1f s  calls %6d  %s" % (tt, ct, nc, name))


if __name__ == "__main__":
    main()
