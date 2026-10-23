"""Count library ladders by whether tools/walk_ladders.gd would size their climb
volume to the real climb. Mirrors walk_ladders.gd: volume height = rise to the
nearest HATCH marker within 1.0 m XZ (rise > 0.5), else 3.0; plus a 1.0 lip.
HATCH markers are emitted by deli_counter.py only for vertical_links kind
'hatch', at (v.x, v.y, v.story * H). Spec metres; z up."""
import glob, json, math, os, sys
specs = sorted(glob.glob(os.path.join(sys.argv[1], "*.json")))
rows = []; n_specs = 0; roof_specs = set()
for p in specs:
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception as e: print("SKIP", p, e); continue
    if not isinstance(d, dict) or "ladders" not in d: continue
    n_specs += 1
    H = float(d.get("story_height") or 3.0); N = int(d.get("n_stories") or 1)
    hatches = [v for v in (d.get("vertical_links") or []) if v.get("kind") == "hatch" and v.get("x") is not None]
    for ld in d.get("ladders") or []:
        f, t = int(ld.get("from_story", 0)), int(ld.get("to_story", 1))
        climb = (t - f) * H; base = f * H
        best = None
        for v in hatches:
            if math.hypot(v["x"] - ld["x"], v["y"] - ld["y"]) > 1.0: continue
            rise = (v.get("story") or 0) * H - base
            if rise > 0.5 and (best is None or rise < best): best = rise
        vol = best if best is not None else 3.0
        rows.append(dict(spec=os.path.basename(p), id=ld.get("id"), f=f, t=t, N=N, H=H,
                         roof=t >= N, climb=climb, vol_climb=vol, hatch=best is not None,
                         short=vol < climb - 1e-6))
        if t >= N: roof_specs.add(os.path.basename(p))
print("specs with a ladders key:", n_specs, " ladders:", len(rows))
roof = [r for r in rows if r["roof"]]
print("ladders reaching the roof (to_story >= n_stories):", len(roof), "in", len(roof_specs), "specs")
print("specs with to_story > n_stories:", len({r['spec'] for r in rows if r['t'] > r['N']}))
def tally(rs, label):
    print(label, "total", len(rs), "| volume shorter than climb:", sum(r["short"] for r in rs),
          "| with matching hatch marker:", sum(r["hatch"] for r in rs))
tally(roof, "ROOF")
tally([r for r in rows if not r["roof"]], "NON-ROOF")
from collections import Counter
print("roof ladders by (climb, vol_climb):", Counter((round(r['climb'],2), round(r['vol_climb'],2)) for r in roof).most_common())
print("all short ladders by (climb, vol_climb):", Counter((round(r['climb'],2), round(r['vol_climb'],2)) for r in rows if r['short']).most_common())
print("short roof specs:", sorted({r['spec'] for r in roof if r['short']})[:80])
