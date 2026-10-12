#!/bin/bash
# Which moved install test 8's seed_9205: Laser Tag 0.26.0's enemy body, or the speed cut (0.27.0's
# fixed clock and synchronous navigation)? Install tests 7 and 8 evaluated the same scene -- level.tscn,
# site.tscn, the two walk scripts and every building GLB byte for byte the same in the two staged
# projects; what differs is the Laser Tag addon, Lot 0.117.0's lot_navqa_setup.gd (only the walk
# test's site_navqa.tscn loads it), the drawn JSON's absolute paths and the import cache's .scn
# files -- and read: 0.25.0 on the waiting clock PASS_WITH_TUNING 82, player survival 75.66 s, 2
# player deaths; 0.27.0 on the fixed clock WARN 70, 7.0 s, 25 deaths. 0.27.0's own record held every
# grade and finding on fifteen candidates against 0.26.0's jobs, so the expectation is the body; this
# measures it. Arms, each the job's own command, on copies of test 8's staged project with only the
# addon's files swapped (the staged addon is the commit's files plus Godot's .uid files, checked):
#   w25_7  test 7's own staged project, 0.25.0, the waiting clock: must read test 7's job (control)
#   w25    0.25.0, the waiting clock, asynchronous navigation: = w25_7 if the import cache is moot
#   w26    0.26.0, the waiting clock, asynchronous navigation: 0.26.0 as a job ran it
#   f25    0.25.0, --fixed-fps 60, navigation synchronous by project settings
#   f26    0.26.0, --fixed-fps 60, navigation synchronous by project settings
#   f27    0.27.0 as shipped, --fixed-fps 60 (its own setters): must read test 8's job (control)
# The fixed arms run one at a time, the waiting ones no more than two at once (the 0.27.0 record:
# alone or two at a time land the same, three moved positions by 0.01 m). It measures and prints.
#
#     bash docs/findings/grader_speed/body_or_clock_ab.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
G="/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
JOB="restaurant_row_001.laser_tag_evaluate.candidate.seed_9205"
S7="/c/stranger_202_7/gabagool/levels/.level_factory"
S8="/c/stranger_202_8/gabagool/levels/.level_factory"
X="$F/_scratch/grader_speed/body_or_clock"
[ -d "$S7/staging/$JOB" ] && [ -d "$S8/staging/$JOB" ] || { echo "a staged project is missing"; exit 2; }
rm -rf "$X" && mkdir -p "$X"
for v in 25:d676dc6 26:6c74794 27:f5f47ad; do
  mkdir -p "$X/a${v%%:*}" && git -C "$F/lasertag" archive "${v##*:}" addons/laser_tag_tool | tar -x -C "$X/a${v%%:*}" || exit 3
done
stage() {   # stage <arm> <source project> <addon version or ""> <sync settings 0|1>
  cp -r "$2" "$X/p_$1"
  if [ -n "$3" ]; then
    local d="$X/p_$1/addons/laser_tag_tool"
    (cd "$d" && find . -type f ! -name "*.uid") | while read -r f; do
      [ -f "$X/a$3/addons/laser_tag_tool/$f" ] || rm -f "$d/$f" "$d/$f.uid"
    done
    cp -r "$X/a$3/addons/laser_tag_tool/." "$d/"
    local n; n=$(diff -rq "$X/a$3/addons/laser_tag_tool" "$d" | grep -vc '\.uid$')
    [ "$n" = 0 ] || { echo "$1: the addon is not 0.$3.0 ($n differences)"; exit 4; }
  fi
  [ "$4" = 1 ] && printf '\n[navigation]\n\nworld/map_use_async_iterations=false\nworld/region_use_async_iterations=false\n' >> "$X/p_$1/project.godot"
}
stage w25_7 "$S7/staging/$JOB" "" 0
stage w25 "$S8/staging/$JOB" 25 0
stage w26 "$S8/staging/$JOB" 26 0
stage f25 "$S8/staging/$JOB" 25 1
stage f26 "$S8/staging/$JOB" 26 1
stage f27 "$S8/staging/$JOB" "" 0
run_arm() {   # run_arm <arm> <extra engine args>
  local s; s=$(date +%s.%N)
  timeout 1800 "$G" --headless $2 --path "$(cygpath -w "$X/p_$1")" -s res://addons/laser_tag_tool/runners/run_map_eval.gd -- \
    --bake-nav --map res://level.tscn --scenario res://mission_scenario.tres --runs 25 --seed 9205 \
    --output "$(cygpath -w "$X/r_$1.json")" < /dev/null > "$X/run_$1.log" 2>&1
  echo "$1: exit $?, wall $(python -c "print(round($(date +%s.%N) - $s, 1))") s; $(grep -m1 '\[LT\] navigation' "$X/run_$1.log" | tr -d '\r' || echo 'no navigation line')"
}
run_arm f27 "--fixed-fps 60"
run_arm f26 "--fixed-fps 60"
run_arm f25 "--fixed-fps 60"
run_arm w25_7 "" & run_arm w26 "" & wait
run_arm w25 ""
python - "$(cygpath -w "$X")" "$(cygpath -w "$S7/jobs/$JOB")" "$(cygpath -w "$S8/jobs/$JOB")" <<'EOF'
import glob, json, os, sys
x, j7, j8 = sys.argv[1:4]
def load(p):
    return json.load(open(p, encoding="utf-8")) if p and os.path.isfile(p) else None
def job(d):
    found = sorted(glob.glob(os.path.join(d, "*", "out", "lasertag.report.json")))
    return load(found[-1]) if found else None
r = {"j7": job(j7), "j8": job(j8)}
for k in ("w25_7", "w25", "w26", "f25", "f26", "f27"):
    r[k] = load(os.path.join(x, "r_%s.json" % k))
S = ("avg_player_survival_seconds", "player_deaths", "avg_time_to_first_contact", "enemy_stuck_events",
     "player_stuck_events", "route_completion_rate")
for name, d in r.items():
    if d is None:
        print("%-6s NO REPORT" % name); continue
    s = d["summary"]
    print("%-6s %-16s %3s  survival %6s s  deaths %2s  contact %5s s  enemy stuck %3s  player stuck %2s  route %4s  events %4d" % (
        name, d["grade"], d["overall_score"], *(s[k] for k in S), len(d["events"])))
for a, b, what in (("w25_7", "j7", "control: the waiting clock reproduces test 7's job"),
                   ("f27", "j8", "control: the fixed clock reproduces test 8's job"),
                   ("w25", "w25_7", "the import cache (test 8's against test 7's)"),
                   ("f26", "f27", "0.27.0's setters against 0.26.0 with the settings"),
                   ("w26", "w25", "THE BODY on the waiting clock"),
                   ("f26", "f25", "the body on the fixed clock"),
                   ("f25", "w25", "THE SPEED CUT on 0.25.0's body"),
                   ("f26", "w26", "the speed cut on 0.26.0's body")):
    if r[a] is None or r[b] is None:
        print("%-5s vs %-5s %s: NO REPORT" % (a, b, what)); continue
    differ = [k for k in r[a] if k != "map" and r[a][k] != r[b].get(k)]
    n = sum(1 for p, q in zip(r[a]["events"], r[b]["events"]) if p != q) + abs(len(r[a]["events"]) - len(r[b]["events"]))
    print("%-5s vs %-5s %s: %s" % (a, b, what, "identical in every field" if not differ else
          "differ in %s (%d events), grade %s -> %s" % (differ, n, r[b]["grade"], r[a]["grade"])))
EOF
rm -rf "$X"/p_* "$X"/a2?
