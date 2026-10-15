"""The comparison for `lt_share_ab.sh`: each arm's report against the two jobs' own.

For each seed, the jobs' reports (install test 8's, Laser Tag 0.27.0 on its scene; test 9's, 0.32.0 on its)
and the four arms' (`s<seed>_t<test>_v<version>`: test <test>'s staged scene, graded by Laser Tag 0.<version>.0).
Each arm is compared with each job in the grade, the score, every `summary` field both carry and the findings
list (severity, type, message); a report missing one of those refuses. Then a row of the numbers the
LT_MAP_* codes are read from. Measures only.

    python docs/findings/stranger_install/lt_share_ab.py [lt_ab<suffix>] [seed ...]      (default: lt_ab, 9205 9104)

The optional first argument names the arms' folder under `_scratch/install_202_9/`: `lt_ab.first` is the
first run, whose swapped arms had no import pass (`lt_share_ab.sh` says what that broke).
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
X = F / "_scratch" / "install_202_9" / (sys.argv.pop(1) if len(sys.argv) > 1 and sys.argv[1].startswith("lt_ab") else "lt_ab")
JOB = "C:/stranger_202_{t}/gabagool/levels/.level_factory/jobs/" \
      "restaurant_row_001.laser_tag_evaluate.candidate.seed_{s}/1/out/lasertag.report.json"
SHOW = ("route_completion_rate", "player_deaths", "player_stuck_events", "enemy_stuck_events",
        "enemy_blocked_events", "avg_time_to_first_contact", "avg_player_survival_seconds")


def load(path):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for key in ("grade", "overall_score", "summary", "findings"):
        if key not in d:
            raise SystemExit("%s: no `%s` (keys: %s)" % (path, key, sorted(d)))
    return d


def diff(a, b):
    """The fields that differ, over the grade, the score, the shared summary fields and the findings."""
    out = [k for k in ("grade", "overall_score") if a[k] != b[k]]
    shared = sorted(set(a["summary"]) & set(b["summary"]))
    out += ["summary." + k for k in shared if a["summary"][k] != b["summary"][k]]
    fa = [(f.get("severity"), f.get("type"), f.get("message")) for f in a["findings"]]
    fb = [(f.get("severity"), f.get("type"), f.get("message")) for f in b["findings"]]
    if fa != fb:
        out.append("findings")
    return out, len(shared)


def row(name, d):
    s = d["summary"]
    nums = "  ".join("%s %s" % (k.replace("avg_", "").replace("_events", "").replace("_rate", "")[:22],
                                s.get(k, "-")) for k in SHOW)
    warn = sorted("%s:%s" % (f.get("severity"), f.get("type")) for f in d["findings"] if f.get("severity") != "PASS")
    print("  %-16s %-17s %3s  %s" % (name, d["grade"], d["overall_score"], nums))
    print("  %-16s not PASS: %s" % ("", ", ".join(warn) or "none"))


def main():
    seeds = sys.argv[1:] or ["9205", "9104"]
    for s in seeds:
        jobs = {t: load(JOB.format(t=t, s=s)) for t in ("8", "9")}
        print("== seed_%s" % s)
        row("job, test 8", jobs["8"])
        row("job, test 9", jobs["9"])
        for t in ("8", "9"):
            for v in ("27", "32"):
                arm = "s%s_t%s_v%s" % (s, t, v)
                p = X / ("r_%s.json" % arm)
                if not p.is_file():
                    print("  %-16s NO REPORT (%s)" % (arm, p))
                    continue
                d = load(p)
                row(arm, d)
                for jt in ("8", "9"):
                    fields, n = diff(d, jobs[jt])
                    print("  %-16s vs test %s's job: %s" % (
                        "", jt, "the same in all %d summary fields, the grade, the score and the findings" % n
                        if not fields else "%d differ: %s" % (len(fields), ", ".join(fields)[:240])))
        print()


if __name__ == "__main__":
    main()
