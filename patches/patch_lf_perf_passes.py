"""Level Factory 0.141.0: the fixed-station harness measures every heading
twice and keeps the pass with the lower p95, so one hitch is not read as a
price. See `lf_perf_passes/CHANGELOG_0.141.0.md`.

Four price runs in a row on 2026-10-05 (cold runs 9155, 9156, 9158, 9159)
had a heading jump 1-4 ms in ONE of three runs with no draw changed --
camera_socket_6 at 270 twice, defender_spawn_21/22, camera_socket_0 -- and
each had to be argued away by hand. A hitch only ever ADDS time, so the
fastest of repeated measurements is the estimate.

Anchored edits (every anchor once; refuses on a miss):
  tools/perf_stations.gd       PASSES := 2; the station set measured PASSES
                               times back to back; each heading keeps its
                               lowest-p95 pass and records every pass and
                               the spread. The watchdog is NOT raised: one
                               run took 52 s start to report on 9159's
                               package, and the watchdog (600 s) must stay
                               under the runner's timeout (900 s) or a stall
                               is killed before it can write what it has
  tools/perf_stations_run.py   prints how many headings' passes disagree
Copies the test; CHANGELOG and VERSION.

    python patch_lf_perf_passes.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_perf_passes"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


WIN_OLD = '''const WINDOW := 60        ## frames measured per sample
'''
WIN_NEW = '''const WINDOW := 60        ## frames measured per sample
## EVERY HEADING, MORE THAN ONCE (0.141.0). The whole station set is measured
## this many times, back to back, and each heading keeps the pass with the
## LOWER p95 -- the figure a station is ranked and budgeted by. A hitch -- a
## stall in the OS, the driver, a late shader -- only ever adds time, so the
## minimum of repeated measurements is the estimate, and a pass apart in time
## is unlikely to hitch at the same heading. Four price runs on 2026-10-05
## each had a heading jump 1-4 ms in one of three runs with no draw changed,
## and every one had to be argued away by hand. One pass took 52 s start to
## report on cold run 9159's package, so two sit well inside WATCHDOG_SEC.
const PASSES := 2
'''

LOOP_OLD = '''	print("[perf] %d station(s) x %d heading(s), %d frames each after %d warmup"
		% [stations.size(), HEADINGS, WINDOW, WARMUP])
	for s in stations:
		var eye: Vector3 = (s["pos"] as Vector3) + Vector3.UP * EYE_H
		var per: Array = []
		# a derived station may carry the ONE heading that defines it
		var yaws: Array = [float(s["yaw"])] if s.has("yaw") else []
		if yaws.is_empty():
			for h in range(HEADINGS):
				yaws.append(360.0 * float(h) / float(HEADINGS))
		for yaw in yaws:
			per.append(await _sample(cam, eye, yaw))
		# THE WORST HEADING IS THE STATION.'''
LOOP_NEW = '''	print("[perf] %d station(s) x %d heading(s) x %d pass(es), %d frames each after %d warmup"
		% [stations.size(), HEADINGS, PASSES, WINDOW, WARMUP])
	_geometry["passes"] = PASSES
	# every station's headings, fixed once: a derived station may carry the
	# ONE heading that defines it
	var station_yaws: Array = []
	for s0 in stations:
		var yaws0: Array = [float(s0["yaw"])] if s0.has("yaw") else []
		if yaws0.is_empty():
			for h in range(HEADINGS):
				yaws0.append(360.0 * float(h) / float(HEADINGS))
		station_yaws.append(yaws0)
	# THE WHOLE SET, PASSES TIMES (0.141.0): samples[station][heading] is the
	# list of that heading's passes, a full pass apart in time
	var samples: Array = []
	for si in range(stations.size()):
		var lists: Array = []
		for _y in station_yaws[si]:
			lists.append([])
		samples.append(lists)
	for _pass in range(PASSES):
		for si in range(stations.size()):
			var sp: Dictionary = stations[si]
			var eye_p: Vector3 = (sp["pos"] as Vector3) + Vector3.UP * EYE_H
			var yaws_p: Array = station_yaws[si]
			for hi in range(yaws_p.size()):
				var smp: Dictionary = await _sample(cam, eye_p, float(yaws_p[hi]))
				(samples[si][hi] as Array).append(smp)
	for si in range(stations.size()):
		var s: Dictionary = stations[si]
		var eye: Vector3 = (s["pos"] as Vector3) + Vector3.UP * EYE_H
		var per: Array = []
		var yaws: Array = station_yaws[si]
		for hi in range(yaws.size()):
			# THE LOWER-p95 PASS IS THE HEADING, every field from that one
			# pass so its draws and frame times describe one measurement; the
			# others are kept beside it, with the spread, so a hitch shows
			var passes: Array = samples[si][hi]
			passes.sort_custom(func(a, b): return float(a["ms_p95"]) < float(b["ms_p95"]))
			var best: Dictionary = (passes[0] as Dictionary).duplicate()
			var kept: Array = []
			for p in passes:
				var pd: Dictionary = p
				kept.append({"ms_median": pd["ms_median"], "ms_p95": pd["ms_p95"],
					"draws": pd["draws"]})
			best["passes"] = kept
			var slowest: Dictionary = passes[passes.size() - 1]
			best["pass_spread_ms"] = float(slowest["ms_p95"]) - float(best["ms_p95"])
			per.append(best)
		# THE WORST HEADING IS THE STATION.'''

CONST_OLD = '''EXIT_CANNOT = 2
'''
CONST_NEW = '''EXIT_CANNOT = 2
#: A heading whose passes' p95 differ by more than this, ms, hitched in one
#: of them (0.141.0). Printed, never judged: the lower pass is already kept.
UNSTABLE_MS = 1.0
'''

RUN_OLD = '''    over = _table(rows, args.draws, args.ms)
'''
RUN_NEW = '''    over = _table(rows, args.draws, args.ms)

    # HOW MANY HEADINGS' PASSES DISAGREE (0.141.0). The probe measures every
    # heading more than once and keeps the pass with the lower p95; a heading
    # whose passes differ by more than UNSTABLE_MS hitched in one of them,
    # which the kept pass has already discounted. Said, so a reader can see
    # the minimum did work -- and whether a heading DREW differently between
    # passes, which would mean the passes did not see the same frame. A
    # report from before passes existed carries neither, and says so.
    heads = [h for r in rows for h in (r.get("headings") or [])
             if "pass_spread_ms" in h]
    print()
    if heads:
        spreads = [float(h["pass_spread_ms"]) for h in heads]
        redrawn = sum(1 for h in heads
                      if len({int(p["draws"]) for p in h.get("passes") or []}) > 1)
        print("  passes: %s per heading, the lower p95 kept; %d of %d heading(s) "
              "differed by more than %.1f ms p95 (largest %.2f ms); %d drew a "
              "different count"
              % ((doc.get("geometry") or {}).get("passes", "?"),
                 sum(1 for d in spreads if d > UNSTABLE_MS), len(heads),
                 UNSTABLE_MS, max(spreads), redrawn))
    else:
        print("  passes: one per heading (a report from before 0.141.0)")
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.140.0"
    _edit(LF / "tools" / "perf_stations.gd", [(WIN_OLD, WIN_NEW), (LOOP_OLD, LOOP_NEW)])
    _edit(LF / "tools" / "perf_stations_run.py", [(CONST_OLD, CONST_NEW), (RUN_OLD, RUN_NEW)])
    shutil.copyfile(SRC / "test_perf_passes.py", LF / "tests" / "unit" / "test_perf_passes.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.141.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.141.0", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.141.0")


if __name__ == "__main__":
    main()
