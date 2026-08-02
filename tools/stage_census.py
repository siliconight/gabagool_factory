"""Count what each pipeline stage hands the next one, and refuse to compare runs.

WHAT THIS IS FOR. A scene loses content between stages silently. `lux_apply`
handed the exporter a site with both of its buildings missing -- 353 nodes in,
243 out, 25 module references in, 12 out -- and nothing anywhere reported a
number. Four instruments and 496 tests passed on the result, because every one
of them measured a property of the file it was given rather than the difference
between two files.

    python tools\\stage_census.py <workspace>\\.level_factory <mission-id>

WHAT IT MEASURES. For every `.tscn` a mission's jobs produced, and for the
export: node count, ext_resource count, the resource paths themselves, and
whether each referenced file and its `.import` sidecar exist. Then, between
consecutive stages, the resource paths that DISAPPEARED. A stage that drops a
reference is the event; the counts are how it is seen.

THE PROVENANCE GUARD, and it is the point of this file. Artifacts on disk are
only ever "the ones currently there". Comparing a compose output from one run
against a lux output from another says nothing at all, and saying it anyway cost
a full day: a stale `export_closure_scan.json` was read three times, a
`project.godot` the editor had rewritten was read as the pipeline's own output,
and a staging directory re-imported two days after its job was read as evidence
about that job. So this refuses by default. If the artifacts' mtimes span more
than `--max-span` seconds they are not one run, and the tool says so and exits
nonzero rather than printing a comparison somebody will quote.

`--allow-mixed` prints the comparison anyway, with every line marked. It exists
because sometimes you genuinely want to look at wreckage; it does not change the
exit code.

WHAT A NONZERO EXIT MEANS. Either the artifacts are not from one run, or they
could not be read. It never reports "nothing was lost" for a comparison it did
not make.
"""
import argparse
import os
import re
import sys
import time

NODE = re.compile(r'^\[node ', re.M)
EXT = re.compile(r'^\[ext_resource[^\]]*?\bpath="([^"]+)"', re.M)

#: Stages in the order the DAG runs them, so the report reads downstream and the
#: "lost between" lines name a direction. Jobs not listed still appear, ordered
#: by mtime after these -- a new job should show up without editing this list.
STAGE_ORDER = ("deli_generate", "lot_assemble", "laser_tag_evaluate",
               "pixelcoat_build", "zoo_kit_build", "patina_apply",
               "patina_dressing", "zoo_dressing_build", "zoo_fixtures_build",
               "presentation_compose", "lux_apply", "dispatch_handoff")


class Unreadable(Exception):
    """A file that could not be read. Not a finding about its contents."""


def scene_facts(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        raise Unreadable(f"{path}: {exc}")
    refs = EXT.findall(text)
    root = os.path.dirname(path)
    resources = []
    for r in refs:
        rel = r[6:] if r.startswith("res://") else r
        # res:// resolves against the PROJECT root, and a job's out/ is not
        # always it. Walk up until a project.godot appears; fall back to the
        # scene's own directory, and say which was used rather than implying
        # a resolution that did not happen.
        base = root
        probe = root
        rooted = False
        for _ in range(4):
            if os.path.exists(os.path.join(probe, "project.godot")):
                base = probe
                rooted = True
                break
            probe = os.path.dirname(probe)
        target = os.path.join(base, rel.replace("/", os.sep))
        resources.append({
            "ref": r,
            "rooted": rooted,
            "exists": os.path.exists(target),
            "import": os.path.exists(target + ".import"),
        })
    return {
        "path": path,
        "mtime": os.path.getmtime(path),
        "nodes": len(NODE.findall(text)),
        "ext_resources": len(refs),
        # Whether res:// could be resolved at all here. A job's out/ is not
        # always a Godot project, and without a project.godot every reference
        # reads as absent -- which is the tool not knowing where to look, NOT a
        # missing file. Saying which of the two produced a number is the whole
        # difference between a measurement and a scare.
        "rooted": all(x["rooted"] for x in resources) if resources else False,
        "resources": resources,
    }


def stage_rank(name):
    try:
        return STAGE_ORDER.index(name)
    except ValueError:
        return len(STAGE_ORDER)


def collect(lf_dir, mission_id):
    """Every .tscn this mission's jobs and export produced, in DAG order."""
    out = []
    jobs = os.path.join(lf_dir, "jobs")
    if os.path.isdir(jobs):
        for entry in sorted(os.listdir(jobs)):
            if not entry.startswith(mission_id + "."):
                continue
            stage = entry[len(mission_id) + 1:].split(".")[0]
            for dirpath, _dirs, files in os.walk(os.path.join(jobs, entry, "out")):
                for f in sorted(files):
                    if f.endswith(".tscn"):
                        out.append((stage, os.path.join(dirpath, f)))
    exports = os.path.join(lf_dir, "exports")
    if os.path.isdir(exports):
        for entry in sorted(os.listdir(exports)):
            if not entry.startswith(mission_id + "."):
                continue
            for dirpath, _dirs, files in os.walk(os.path.join(exports, entry)):
                for f in sorted(files):
                    if f.endswith(".tscn"):
                        out.append(("export", os.path.join(dirpath, f)))
    out.sort(key=lambda p: (stage_rank(p[0]), p[1]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lf_dir", help="the workspace's .level_factory directory")
    ap.add_argument("mission_id")
    ap.add_argument("--max-span", type=float, default=600.0,
                    help="seconds the artifacts' mtimes may span and still "
                         "count as one run (default 600)")
    ap.add_argument("--allow-mixed", action="store_true",
                    help="print the comparison even when the span is exceeded")
    args = ap.parse_args(argv)

    found = collect(args.lf_dir, args.mission_id)
    if not found:
        sys.stderr.write("no .tscn found for mission %r under %s\n"
                         % (args.mission_id, args.lf_dir))
        return 2

    rows = []
    failed = []
    for stage, path in found:
        try:
            f = scene_facts(path)
        except Unreadable as exc:
            failed.append(str(exc))
            continue
        f["stage"] = stage
        rows.append(f)

    if not rows:
        for msg in failed:
            sys.stderr.write(msg + "\n")
        return 2

    times = [r["mtime"] for r in rows]
    span = max(times) - min(times)
    one_run = span <= args.max_span

    width = max(len(r["stage"]) for r in rows)
    print("%-*s  %6s  %5s  %8s  %s"
          % (width, "stage", "nodes", "refs", "missing", "written"))
    for r in rows:
        if r["rooted"]:
            missing = "%d" % sum(1 for x in r["resources"]
                                 if not x["exists"] or not x["import"])
        else:
            missing = "n/a"
        age = "" if one_run else "  <-- %+.0fs" % (r["mtime"] - max(times))
        print("%-*s  %6d  %5d  %8s  %s%s"
              % (width, r["stage"], r["nodes"], r["ext_resources"], missing,
                 time.strftime("%Y-%m-%d %H:%M:%S",
                               time.localtime(r["mtime"])), age))
    if any(not r["rooted"] for r in rows if r["ext_resources"]):
        print()
        print("missing=n/a: this stage's output directory has no project.godot "
              "above it, so res:// cannot be resolved from here and the sidecar "
              "column would report every reference as absent.")

    if not one_run:
        print()
        print("REFUSED: these artifacts span %.0f s (%.1f days) and are not one "
              "run." % (span, span / 86400.0))
        print("A comparison across runs describes a scene nobody built. Re-run "
              "the mission with --force and measure that.")
        if not args.allow_mixed:
            return 1
        print("--allow-mixed: the comparison below is between different runs.")

    # One scene per stage for the diff. A stage can emit several -- compose
    # writes site.tscn AND site_main.tscn -- and diffing consecutive ROWS
    # compared those two against each other and reported it as a stage
    # transition: "-351 nodes, 25 references lost" between compose and itself,
    # with every later pair offset by one. The principal scene is the one with
    # the most nodes, which is the level; the others are entry stubs. Reported,
    # so a stage whose principal scene is not the one a reader expects is
    # visible rather than assumed.
    principal = {}
    for r in rows:
        best = principal.get(r["stage"])
        if best is None or r["nodes"] > best["nodes"]:
            principal[r["stage"]] = r
    chain = [principal[s] for s in
             sorted(principal, key=lambda s: (stage_rank(s), s))]
    print()
    for r in chain:
        sibs = sum(1 for x in rows if x["stage"] == r["stage"]) - 1
        if sibs:
            print("%s: comparing %s (%d nodes); %d other scene(s) in this "
                  "stage ignored" % (r["stage"], os.path.basename(r["path"]),
                                     r["nodes"], sibs))
    print()
    for prev, cur in zip(chain, chain[1:]):
        before = {x["ref"] for x in prev["resources"]}
        after = {x["ref"] for x in cur["resources"]}
        lost = sorted(before - after)
        gained = sorted(after - before)
        dn = prev["nodes"] - cur["nodes"]
        if not lost and not gained and dn == 0:
            continue
        print("%s -> %s: %+d nodes, %d reference(s) lost, %d gained"
              % (prev["stage"], cur["stage"], -dn, len(lost), len(gained)))
        for ref in lost:
            # Whether the LOST reference had a sidecar upstream, because that
            # correlation is the current lead and printing it is how it gets
            # confirmed or killed on a clean run rather than argued about.
            up = next((x for x in prev["resources"] if x["ref"] == ref), None)
            if up is None or not up["rooted"]:
                mark = ""
            elif up["import"]:
                mark = ""
            else:
                mark = "   (no .import upstream)"
            print("    lost   %s%s" % (ref, mark))
        for ref in gained:
            print("    gained %s" % ref)

    for msg in failed:
        sys.stderr.write("unreadable: " + msg + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
