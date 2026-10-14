"""Patina 0.30.0 against 0.31.0 over every Deli Counter shell, with the dressing job's own command (roadmap 248).

    python docs/findings/patina_props/replay.py [--workers 6] [--only gs_midrise_a,gs_midrise_c] [--compare]

`--compare` reads the arms already under `_scratch/patina_replay/` and runs nothing.

Every Level Factory `patina_dressing` job runs one command -- read off all 31 of cold runs 9303's and 9285's job
logs, which differ only in the shell and the output path:

    python -m patina.cli <deli_counter/build/<id>.glb> --mode vertex-color --out <out> --theme default
        --dressing --anchors --gutters                  (cwd: the Patina repo)

This runs it on every `deli_counter/build/*.glb` with a `.slots.json` beside it, in three arms, each into its own
folder under `_scratch/patina_replay/`:

    a     Patina 0.30.0, `git archive 31d31e9` of the Patina repo unpacked beside the arms
    a2    the same 0.30.0 again: THE CONTROL. If any shell's outputs differ between a and a2, the replay cannot
          tell a change from noise, and it says so and stops reporting differences.
    b     the Patina working copy (0.31.0 once applied)

Then, per shell, which of the six outputs (`.patina.glb`, `.anchors.json`, `.dressing.json`, `.json`,
`.gameplay.json`, `.trim.png`) differ by bytes, a against b -- an output no arm wrote is no difference: Patina
writes `.gameplay.json` only for a shell that has one beside it. For a shell whose anchors moved, each kind's count
in each arm and the anchors' least and greatest x and y (Blender Z-up metres, the sidecar's own space). The shell's
prop slots whose plan box reaches past its other slots' are named, read off its slots.json, a slot turned 90 or 270
degrees with its width and depth swapped: a rough label, not a measure of what moved.

Prints what it measured and stops; writes the per-shell rows to `replay.out.json` beside itself.
"""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

F = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PATINA = F / "patina"
BUILD = F / "deli_counter" / "build"
SCR = F / "_scratch" / "patina_replay"
OLD = "31d31e9"                                   # Patina 0.30.0
OUTS = (".patina.glb", ".patina.anchors.json", ".patina.dressing.json", ".patina.json",
        ".patina.gameplay.json", ".patina.trim.png")


def _unpack_old():
    dest = SCR / "patina_0300"
    if (dest / "patina" / "cli.py").is_file():
        return dest
    blob = subprocess.run(["git", "-C", str(PATINA), "archive", OLD], capture_output=True, check=True).stdout
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
        tf.extractall(dest)
    assert (dest / "patina" / "cli.py").is_file(), "no patina/cli.py in the archive of " + OLD
    return dest


def _run(repo, glb, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (glb.stem + ".patina.glb")
    p = subprocess.run([sys.executable, "-m", "patina.cli", str(glb), "--mode", "vertex-color", "--out", str(out),
                        "--theme", "default", "--dressing", "--anchors", "--gutters"],
                       cwd=str(repo), capture_output=True, text=True)
    return p.returncode, (p.stderr or "")[-300:]


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.is_file() else None


def _anchor_summary(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    an = d.get("anchors")
    if not isinstance(an, dict):
        raise SystemExit("UNKNOWN SHAPE: %s has no anchors dict" % path)
    out = {}
    for kind, lst in an.items():
        if not lst:
            out[kind] = {"n": 0}
            continue
        xs = [a["pos"][0] for a in lst]
        ys = [a["pos"][1] for a in lst]
        out[kind] = {"n": len(lst), "x": [round(min(xs), 3), round(max(xs), 3)],
                     "y": [round(min(ys), 3), round(max(ys), 3)]}
    return out


def _box(s):
    w, dp = s["fit"]["dims"][0], s["fit"]["dims"][1]
    turned = round(float(s["transform"].get("rot_y", 0.0))) % 180 == 90       # degrees, as Deli Counter writes them
    half = (dp, w) if turned else (w, dp)
    t = s["transform"]["translation"]
    return [(t[i] - half[i] / 2.0, t[i] + half[i] / 2.0) for i in (0, 1)]


def _proud_props(slots_path):
    """Prop slots whose plan box reaches past every other slot's extent, from the slots.json alone."""
    d = json.loads(slots_path.read_text(encoding="utf-8"))
    rest = [_box(s) for s in d["slots"] if s.get("role") != "prop" and (s.get("fit") or {}).get("dims")]
    if not rest:
        return []
    lo = [min(b[i][0] for b in rest) for i in (0, 1)]
    hi = [max(b[i][1] for b in rest) for i in (0, 1)]
    out = []
    for s in d["slots"]:
        if s.get("role") != "prop" or not (s.get("fit") or {}).get("dims"):
            continue
        b = _box(s)
        if any(b[i][0] < lo[i] - 0.05 or b[i][1] > hi[i] + 0.05 for i in (0, 1)):
            out.append(s["slot_id"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default="")
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args()
    shells = sorted(p for p in BUILD.glob("*.glb") if (BUILD / (p.stem + ".slots.json")).is_file())
    if args.only:
        want = set(args.only.split(","))
        shells = [p for p in shells if p.stem in want]
    if not shells:
        raise SystemExit("UNKNOWN SHAPE: no shell with a slots.json in %s" % BUILD)
    old = _unpack_old()
    arms = {"a": old, "a2": old, "b": PATINA}
    jobs = [(arm, repo, glb) for glb in shells for arm, repo in arms.items()]
    if args.compare:
        results = []
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            results = list(ex.map(lambda j: (j[0], j[2].stem, _run(j[1], j[2], SCR / j[0])), jobs))
    failed = [(arm, name, rc, err) for arm, name, (rc, err) in results if rc != 0]
    for arm, name, rc, err in failed:
        print("RUN FAILED: %s %s exit %d: %s" % (arm, name, rc, err.strip().splitlines()[-1:] or ""))
    rows = []
    noisy = []
    for glb in shells:
        n = glb.stem
        dig = {arm: {o: _digest(SCR / arm / (n + o)) for o in OUTS} for arm in arms}
        absent = [o for o in OUTS if any(dig[arm][o] is None for arm in arms)]
        if ".patina.glb" in absent or [o for o in absent if not all(dig[arm][o] is None for arm in arms)]:
            rows.append({"shell": n, "error": "an output is missing in some arm: %s" % absent, "digests": dig})
            continue
        if dig["a"] != dig["a2"]:
            noisy.append(n)
        moved = [o for o in OUTS if dig["a"][o] != dig["b"][o]]
        row = {"shell": n, "moved": moved, "absent_in_all": absent,
               "proud_props": _proud_props(BUILD / (n + ".slots.json"))}
        if ".patina.anchors.json" in moved:
            row["anchors_a"] = _anchor_summary(SCR / "a" / (n + ".patina.anchors.json"))
            row["anchors_b"] = _anchor_summary(SCR / "b" / (n + ".patina.anchors.json"))
        rows.append(row)
    (HERE / "replay.out.json").write_text(json.dumps({"old": OLD, "shells": len(shells), "failed": len(failed),
                                                      "compare_only": args.compare, "noisy": noisy, "rows": rows},
                                                     indent=1), encoding="utf-8")
    print("shells %d, runs %d%s, failed %d" % (len(shells), len(jobs),
                                               " (compared only: the arms on disk)" if args.compare else "",
                                               len(failed)))
    if noisy:
        print("THE CONTROL MOVED: 0.30.0 twice differs on %d shell(s): %s -- no difference below is evidence"
              % (len(noisy), ", ".join(noisy)))
        return 1
    print("the control: 0.30.0 twice, every output of every shell byte-identical")
    errs = [r for r in rows if r.get("error")]
    same = [r for r in rows if not r.get("error") and not r["moved"]]
    diff = [r for r in rows if not r.get("error") and r["moved"]]
    print("0.30.0 against the working copy: %d shell(s) byte-identical in every output written, %d moved, %d errors"
          % (len(same), len(diff), len(errs)))
    for r in diff:
        print("  %-24s moved %s; props past the other slots: %s"
              % (r["shell"], ",".join(o.replace(".patina", "") for o in r["moved"]),
                 ",".join(r["proud_props"]) or "none"))
        for kind in sorted(set(r.get("anchors_a", {})) | set(r.get("anchors_b", {}))):
            a, b = r["anchors_a"].get(kind, {}), r["anchors_b"].get(kind, {})
            print("      %-12s n %3s -> %3s   y %s -> %s   x %s -> %s"
                  % (kind, a.get("n"), b.get("n"), a.get("y"), b.get("y"), a.get("x"), b.get("x")))
    unmoved_proud = [r["shell"] for r in same if r["proud_props"]]
    print("shells with a prop past their other slots whose outputs did NOT move: %d -- %s"
          % (len(unmoved_proud), ", ".join(unmoved_proud) or "none"))
    for r in errs:
        print("  ERROR %s: %s" % (r["shell"], r["error"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
