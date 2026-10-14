"""Run a Zoo job's build N times under `stage_digest.py`, each in its own Blender process, and say at which step the
runs first disagree (roadmap 247).

    python docs/findings/roofprops_bytes/stage_runs.py <job dir> [--runs N] [--match PREFIX] [--zoo <zoo root>]

`<job dir>` is a cold-run job's attempt folder (`.../jobs/<job>/1`): its `job.log`'s first line is the command, run
again with `--out` moved to `_scratch/rp247_stage/<i>`. Collects every `STAGE` line and prints, per part and step in
build order, how many distinct digests the runs gave for each field (`stage_digest._fields` names them) and which runs gave
which, as one digit a run. Prints what it measured; it names
no cause.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "rp247_stage")
PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage_digest.py")
FIELDS = ("ov", "of", "fi", "fr", "v", "f", "c", "u", "n")


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    job = os.path.abspath(sys.argv[1])
    runs = int(arg("--runs", "4"))
    env = dict(os.environ, STAGE_MATCH=arg("--match", "SatelliteDish"))
    if "--zoo" in sys.argv:
        env["ZOO_ROOT"] = os.path.abspath(arg("--zoo", ""))
    first = open(os.path.join(job, "job.log"), encoding="utf-8", errors="replace").readline()
    assert first.startswith("$ "), first[:80]
    cmd = shlex.split(first[2:].strip(), posix=False)
    assert cmd.count("--python") == 1 and "--out" in cmd, cmd[:8]
    cmd[cmd.index("--python") + 1] = PROBE
    table, order = {}, []
    for i in range(runs):
        out = os.path.join(X, str(i))
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        c = list(cmd)
        c[c.index("--out") + 1] = out
        r = subprocess.run(c, capture_output=True, text=True, timeout=900, env=env)
        lines = [ln.split() for ln in r.stdout.splitlines() if ln.startswith("STAGE ")]
        ends = [ln for ln in r.stdout.splitlines() if ln.startswith("STAGE_EXIT")]
        print("run %d: exit %d, %d stage lines, %s" % (i, r.returncode, len(lines), ends[-1] if ends else "no exit line"))
        if not lines:
            print(r.stdout[-1500:], r.stderr[-1500:])
            raise SystemExit("run %d printed no STAGE line" % i)
        for ln in lines:
            # STAGE <part> <step> ov=.. of=.. fi=.. fr=.. v=.. f=.. c=.. u=.. n=.. nv=.. nf=..
            key = (ln[1], ln[2])
            if key not in table:
                table[key] = []
                order.append(key)
            got = dict(tok.split("=", 1) for tok in ln[3:])
            assert all(f in got for f in FIELDS), ("an unrecognised STAGE line", ln[:6])
            table[key].append(got)
    for key in order:
        rows = table[key]
        if len(rows) != runs:
            print("%-34s %-22s seen in %d of %d runs" % (key[0], key[1], len(rows), runs))
            continue
        varied = []
        for f in FIELDS:
            vals = [r[f] for r in rows]
            if len(set(vals)) > 1:
                varied.append("%s %d (%s)" % (f, len(set(vals)), "".join(str(sorted(set(vals)).index(v)) for v in vals)))
        print("%-34s %-22s %s" % (key[0], key[1], "; ".join(varied) if varied else "the same in every run"))


if __name__ == "__main__":
    main()
