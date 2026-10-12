"""Do the compose job's building commands make the same package side by side as in turn?

Cold run 9251's compose job ran sixteen commands one after another: the mission shell's compose,
then one per building, each into its own folder under the lot's (Level Factory 0.186.0 runs the
buildings' side by side; the shell's stays first, since Deli Counter's `build_package` clears its
output folder, which holds theirs). This replays the job's own sixteen commands -- read from the
workspace index, every input read from the run's own job outputs -- into scratch folders three
ways, and compares the trees file by file:

  SEQ1, SEQ2   in turn, twice: the control (is the compose deterministic at all?)
  PAR          the shell's first and alone, then the buildings four at a time

and compares the first against the run's own compose output, to show the replay is the job.
A command that exits 3 failed Deli Counter's z-fight gate, which the compose job treats as advisory
(`exit_advisory`; the finding is PRESENTATION_ZFIGHT): each arm names the buildings that did. It
prints each arm's wall time and every file that differs. It measures and prints.

    python docs/findings/grader_speed/compose_replay_ab.py <workspace>
"""
import concurrent.futures as cf
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "compose_ab")
DRIVER = "run_presentation_compose.py"


def commands(ws):
    c = sqlite3.connect(os.path.join(ws, ".level_factory", "index.sqlite"))
    d = json.loads(c.execute("select payload from jobs where job_id like '%.presentation_compose'").fetchone()[0])
    flat, out = d["command"], []
    starts = [i for i in range(len(flat) - 1) if flat[i + 1].endswith(DRIVER)]
    for k, s in enumerate(starts):
        out.append(flat[s: starts[k + 1] if k + 1 < len(starts) else len(flat)])
    old_root = d["working_directory"]
    assert len(out) == 16 and all("--out" in a for a in out), (len(out), old_root)
    return out, old_root


def arm(name, cmds, old_root, width):
    root = os.path.join(X, name)
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    fixed = []
    for argv in cmds:
        a = list(argv)
        i = a.index("--out")
        assert a[i + 1].startswith(old_root), a[i + 1]
        a[i + 1] = root + a[i + 1][len(old_root):]
        fixed.append(a)
    env = dict(os.environ, DELI_OUT=root, LF_OUT=root)
    cwd = os.path.join(F, "deli_counter")

    def run(a):
        p = subprocess.run(a, cwd=cwd, env=env, capture_output=True, timeout=900)
        return p.returncode, os.path.basename(a[a.index("--out") + 1])

    t0 = time.time()
    codes = [run(fixed[0])]
    if width <= 1:
        codes += [run(a) for a in fixed[1:]]
    else:
        with cf.ThreadPoolExecutor(width) as ex:
            codes += list(ex.map(run, fixed[1:]))
    wall = time.time() - t0
    print("%-5s width %d: %.1f s; nonzero exits %s" % (
        name, width, wall, ["%s=%d" % (b, c) for c, b in codes if c] or "none"), flush=True)
    return root


def tree(root):
    out = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out


def differ(a, b, label):
    ta, tb = tree(a), tree(b)
    root_a, root_b = a.encode(), b.encode()
    norm = lambda data, root: data.replace(root.replace(b"\\", b"/"), b"<root>").replace(root, b"<root>")
    diff = [k for k in sorted(set(ta) & set(tb))
            if norm(open(ta[k], "rb").read(), root_a) != norm(open(tb[k], "rb").read(), root_b)]
    print("%s: %d and %d files; on one side only %d; different (each arm's own folder set aside) %d"
          % (label, len(ta), len(tb), len(set(ta) ^ set(tb)), len(diff)))
    for k in diff[:8]:
        print("    " + k)
    return diff


def main():
    ws = os.path.abspath(sys.argv[1])
    cmds, old_root = commands(ws)
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    s1 = arm("SEQ1", cmds, old_root, 1)
    s2 = arm("SEQ2", cmds, old_root, 1)
    p = arm("PAR", cmds, old_root, 4)
    differ(s1, s2, "control SEQ1 against SEQ2")
    differ(s1, p, "change  SEQ1 against PAR")
    differ(old_root, s1, "replay  the run's own out against SEQ1")
    shutil.rmtree(X, ignore_errors=True)


if __name__ == "__main__":
    main()
