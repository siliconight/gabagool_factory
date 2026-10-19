"""Gather the walker's asset flags from walk copies into one ledger per asset (factory roadmap 253).

    python tools/asset_flags.py                        # every _runs/walk_export_*/ that holds flags
    python tools/asset_flags.py <walk copy> ...        # these copies only
    python tools/asset_flags.py --out <dir>            # where the ledger goes (default docs/findings/asset_flags_253/)
    python tools/asset_flags.py --selftest             # prove it on a throwaway tree

The walker, 2026-10-14: "I want a way to flag assets that look good and assets that need more polish/love". In a
walk copy, G marks what the crosshair rests on as looking good and P as needing love (`tools/walk_asset_flags.gd`,
debug builds only); each press appends one record to the copy's `asset_flags.jsonl` and saves a small frame under
its `asset_flags/`. This gathers them:

  ledger.json   every flag, grouped by asset -- a module or species by its file, else the node the pick named --
                with its counts, levels, buildings and frames
  LEDGER.md     the same, ranked: what needs love first, by how many times it was flagged, then what looks good
  frames/       each flag's frame, copied here so the ledger outlives the walk copy (`factory_retire.py` takes a
                walk export untouched for thirty days)

A record whose shape this does not know is COUNTED AND NAMED, not skipped in silence: a ledger that quietly
drops a fifth of its rows reads as complete and is not.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "docs", "findings", "asset_flags_253")
SCHEMA = "walk_asset_flag/1"
VERDICTS = ("needs_love", "good")
_KEYS = ("verdict", "asset", "asset_file", "building", "level", "node", "how", "time_utc")


def _copies(args):
    if args:
        return [os.path.abspath(a) for a in args]
    return sorted(d for d in glob.glob(os.path.join(ROOT, "_runs", "walk_export_*"))
                  if os.path.isfile(os.path.join(d, "asset_flags.jsonl")))


def read_flags(copy_dir):
    """``(records, refused)``: the copy's flag records, each carrying ``copy`` and ``frame_src``, and the lines
    this could not read as one, as ``(line number, reason)``."""
    path = os.path.join(copy_dir, "asset_flags.jsonl")
    records, refused = [], []
    if not os.path.isfile(path):
        return records, refused
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError as exc:
                refused.append((n, "not JSON: %s" % exc))
                continue
            if not isinstance(rec, dict) or rec.get("schema") != SCHEMA:
                refused.append((n, "schema %r, not %r" % (rec.get("schema") if isinstance(rec, dict) else None, SCHEMA)))
                continue
            missing = [k for k in _KEYS if k not in rec]
            if missing or rec["verdict"] not in VERDICTS:
                refused.append((n, "missing %s" % missing if missing else "verdict %r" % rec["verdict"]))
                continue
            rec = dict(rec)
            rec["copy"] = os.path.basename(copy_dir)
            frame = str(rec.get("frame") or "")
            rec["frame_src"] = (os.path.join(copy_dir, frame.replace("res://", "").replace("/", os.sep))
                                if frame.startswith("res://") else "")
            records.append(rec)
    return records, refused


def key_of(rec):
    """What a flag is ABOUT: the asset's file when the pick resolved one, else the node it named."""
    return rec.get("asset_file") or rec.get("node") or "(nothing under the crosshair)"


def ledger(records):
    """``{key: entry}``, one entry per asset, its flags newest last."""
    out = {}
    for rec in sorted(records, key=lambda r: r.get("time_utc", "")):
        k = key_of(rec)
        e = out.setdefault(k, {"asset": rec.get("asset") or "", "asset_file": rec.get("asset_file") or "",
                               "needs_love": 0, "good": 0, "buildings": [], "levels": [], "flags": []})
        e[rec["verdict"]] += 1
        for field, src in (("buildings", "building"), ("levels", "level")):
            v = rec.get(src) or ""
            if v and v not in e[field]:
                e[field].append(v)
        e["flags"].append({k2: rec.get(k2) for k2 in ("verdict", "time_utc", "level", "building", "node", "how",
                                                       "camera", "point", "copy", "frame")})
    return out


def ranked(entries):
    """Needs love first, by how often; then looks good, by how often; then by name."""
    return sorted(entries.items(), key=lambda kv: (-kv[1]["needs_love"], -kv[1]["good"], kv[0]))


def write(entries, out_dir, records, refused_by_copy):
    os.makedirs(out_dir, exist_ok=True)
    frames = os.path.join(out_dir, "frames")
    copied = 0
    for rec in records:
        src = rec.get("frame_src") or ""
        if src and os.path.isfile(src):
            os.makedirs(frames, exist_ok=True)
            dst = os.path.join(frames, "%s__%s" % (rec["copy"], os.path.basename(src)))
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied += 1
    with open(os.path.join(out_dir, "ledger.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"schema": "asset_flag_ledger/1", "assets": entries,
                   "refused": {c: r for c, r in refused_by_copy.items() if r}}, fh, indent=1, sort_keys=True)
    lines = ["# Asset flags: the ledger", "",
             "Generated by `tools/asset_flags.py` from the walk copies' `asset_flags.jsonl` (G = looks good, "
             "P = needs love, `tools/walk_asset_flags.gd`). Do not edit by hand; run it again.", ""]
    for verdict, title in (("needs_love", "Needs love"), ("good", "Looks good")):
        rows = [(k, e) for k, e in ranked(entries) if e[verdict]]
        lines += ["## %s" % title, ""]
        if not rows:
            lines += ["Nothing flagged.", ""]
            continue
        for k, e in rows:
            name = e["asset"] or k
            lines.append("- **%s** -- %d flag(s); %s; %s" % (
                name, e[verdict], ", ".join(e["buildings"]) or "no building",
                ", ".join(e["levels"]) or "no level"))
        lines.append("")
    refused = sum(len(r) for r in refused_by_copy.values())
    if refused:
        lines += ["## Not read", ""]
        for c, rows in refused_by_copy.items():
            for n, why in rows:
                lines.append("- %s line %d: %s" % (c, n, why))
        lines.append("")
    with open(os.path.join(out_dir, "LEDGER.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    return copied


def main(argv):
    if "--selftest" in argv:
        return selftest()
    out = DEFAULT_OUT
    if "--out" in argv:
        i = argv.index("--out")
        out = os.path.abspath(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    copies = _copies([a for a in argv if not a.startswith("--")])
    records, refused_by_copy = [], {}
    for c in copies:
        recs, refused = read_flags(c)
        records += recs
        refused_by_copy[os.path.basename(c)] = refused
    entries = ledger(records)
    copied = write(entries, out, records, refused_by_copy)
    need = sum(1 for e in entries.values() if e["needs_love"])
    good = sum(1 for e in entries.values() if e["good"])
    refused = sum(len(r) for r in refused_by_copy.values())
    print("%d flag(s) from %d walk cop(ies): %d asset(s) need love, %d look good; %d frame(s) copied; "
          "%d line(s) not read -> %s" % (len(records), len(copies), need, good, copied, refused, out))
    return 1 if refused else 0


def selftest():
    import tempfile
    base = tempfile.mkdtemp(prefix="asset_flags_")
    try:
        copy = os.path.join(base, "walk_export_x")
        os.makedirs(os.path.join(copy, "asset_flags"))
        open(os.path.join(copy, "asset_flags", "f1.png"), "wb").write(b"png")

        def rec(verdict, asset, t, frame=""):
            return json.dumps({"schema": SCHEMA, "verdict": verdict, "asset": asset,
                               "asset_file": "res://lot/deli_a01/art/zoo/%s.glb" % asset if asset else "",
                               "building": "deli_a01", "level": "urban_row_001", "node": "/root/x/%s" % asset,
                               "how": "render", "time_utc": t, "frame": frame})
        with open(os.path.join(copy, "asset_flags.jsonl"), "w", encoding="utf-8") as fh:
            fh.write(rec("needs_love", "wall_a", "2026-10-19T10:00:01", "res://asset_flags/f1.png") + "\n")
            fh.write(rec("needs_love", "wall_a", "2026-10-19T10:00:02") + "\n")
            fh.write(rec("good", "bench_b", "2026-10-19T10:00:03") + "\n")
            fh.write(rec("good", "wall_a", "2026-10-19T10:00:04") + "\n")
            fh.write('{"schema": "something_else/9"}\n')
            fh.write("not json\n")
        out = os.path.join(base, "ledger")
        code = main([copy, "--out", out])
        assert code == 1, "two unreadable lines must fail the run, not vanish"
        led = json.load(open(os.path.join(out, "ledger.json"), encoding="utf-8"))
        wall = led["assets"]["res://lot/deli_a01/art/zoo/wall_a.glb"]
        assert (wall["needs_love"], wall["good"]) == (2, 1), wall
        assert led["assets"]["res://lot/deli_a01/art/zoo/bench_b.glb"]["good"] == 1
        assert len(led["refused"]["walk_export_x"]) == 2, led["refused"]
        md = open(os.path.join(out, "LEDGER.md"), encoding="utf-8").read()
        assert md.index("**wall_a** -- 2 flag(s)") < md.index("## Looks good"), md
        assert os.path.isfile(os.path.join(out, "frames", "walk_export_x__f1.png"))
        assert "## Not read" in md and "line 6" in md
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
